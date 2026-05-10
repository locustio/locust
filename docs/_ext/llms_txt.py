"""Sphinx extension that generates llms.txt and llms-full.txt for AI consumption.

Generates an index file (llms.txt) and a full concatenated markdown file (llms-full.txt)
from the existing RST documentation during the HTML build, following the llmstxt.org
standard.

This extension uses ``sphinx_markdown_builder.translator.MarkdownTranslator``
(MIT License, Copyright (c) 2023-2026 Liran Funaro) via a minimal builder proxy
to render doctrees as Markdown. See THIRD-PARTY-NOTICES.md at the repository root.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import TYPE_CHECKING

from docutils import nodes
from sphinx.util import logging

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://docs.locust.io/en/stable/"
DEFAULT_EXCLUDE = ["changelog", "faq", "further-reading", "ai-docs"]
DEFAULT_DESCRIPTION = "Developer-friendly load testing framework. Write scalable load tests in plain Python."


class _MarkdownConfig:
    """Config proxy with default values for sphinx-markdown-builder's translator."""

    markdown_http_base = ""
    markdown_uri_doc_suffix = ".html"
    markdown_anchor_sections = False
    markdown_anchor_signatures = False
    markdown_docinfo = False
    markdown_bullet = "*"
    markdown_flavor = ""


class _MarkdownBuilderProxy:
    """Minimal proxy providing the attributes MarkdownTranslator needs from a builder."""

    def __init__(self, current_doc_name: str = ""):
        self.config = _MarkdownConfig()
        self.current_doc_name = current_doc_name

    def get_target_uri(self, docname: str, typ: str = None) -> str:
        return f"{docname}.html"


def _doctree_to_markdown(doctree: nodes.document, docname: str) -> str:
    """Convert a Sphinx doctree to Markdown using sphinx-markdown-builder's translator."""
    from sphinx_markdown_builder.translator import MarkdownTranslator

    tree = deepcopy(doctree)
    # deepcopy loses the reporter; restore it from the original
    tree.reporter = doctree.reporter
    proxy = _MarkdownBuilderProxy(current_doc_name=docname)
    visitor = MarkdownTranslator(tree, proxy)
    tree.walkabout(visitor)
    return visitor.astext()


def _get_first_paragraph(doctree: nodes.document) -> str:
    """Extract the first paragraph text from a doctree for use as a description."""
    for node in doctree.traverse(nodes.paragraph):
        return node.astext().replace("\n", " ").strip()
    return ""


def _walk_toctree(env, docname: str, exclude: list[str]) -> list[str]:
    """Recursively walk toctree includes and return ordered docnames, excluding specified ones."""
    result = []
    includes = env.toctree_includes.get(docname, [])
    for child in includes:
        if child in exclude:
            continue
        result.append(child)
        result.extend(_walk_toctree(env, child, exclude))
    return result


def _get_section_groups(env, master_doc: str, exclude: list[str]) -> list[tuple[str, list[str]]]:
    """Parse the master document's toctree to get section groups.

    Returns a list of (section_title, [docnames]) pairs based on the master doc structure.
    Only processes direct child sections of the root, not the root section itself.
    """
    doctree = env.get_doctree(master_doc)
    groups = []

    # Find the root section
    root_sections = list(doctree.traverse(nodes.section, descend=True, siblings=False))
    if not root_sections:
        return groups

    root_section = root_sections[0]

    # Process only direct child sections of the root
    for child in root_section.children:
        if not isinstance(child, nodes.section):
            continue

        title_node = child.next_node(nodes.title)
        if title_node is None:
            continue
        section_title = title_node.astext()

        # Only get toctrees that are direct children of this section (not nested)
        toctree_nodes = []
        for node in child.children:
            if node.tagname == "toctree":
                toctree_nodes.append(node)
            elif isinstance(node, nodes.compound):
                for subnode in node.children:
                    if subnode.tagname == "toctree":
                        toctree_nodes.append(subnode)

        if not toctree_nodes:
            continue

        docnames = []
        for toctree_node in toctree_nodes:
            for entry in toctree_node.get("entries", []):
                _, docname = entry
                if docname and docname not in exclude:
                    docnames.append(docname)

        if docnames:
            groups.append((section_title, docnames))

    return groups


def _generate_llms_txt(app: Sphinx, section_groups: list[tuple[str, list[str]]]) -> str:
    """Generate the llms.txt index content."""
    base_url = app.config.llms_txt_base_url.rstrip("/") + "/"
    description = app.config.llms_txt_description
    project = app.config.project

    lines = [f"# {project}\n"]
    lines.append(f"> {description}\n")

    for section_title, docnames in section_groups:
        lines.append(f"\n## {section_title}\n")
        for docname in docnames:
            title_node = app.env.titles.get(docname)
            title = title_node.astext() if title_node else docname
            url = f"{base_url}{docname}.html"

            doctree = app.env.get_doctree(docname)
            desc = _get_first_paragraph(doctree)
            if desc:
                lines.append(f"- [{title}]({url}): {desc}")
            else:
                lines.append(f"- [{title}]({url})")

    return "\n".join(lines) + "\n"


def _generate_llms_full_txt(app: Sphinx, section_groups: list[tuple[str, list[str]]]) -> str:
    """Generate the llms-full.txt full content."""
    project = app.config.project
    description = app.config.llms_txt_description

    parts = [f"# {project}\n\n> {description}\n"]

    for section_title, docnames in section_groups:
        for docname in docnames:
            doctree = app.env.get_doctree(docname)
            try:
                md_content = _doctree_to_markdown(doctree, docname)
                parts.append(f"\n---\n\n{md_content}")
            except Exception as e:
                logger.warning("llms_txt: failed to convert %s to markdown: %s", docname, e)
                text = doctree.astext()
                title_node = app.env.titles.get(docname)
                title = title_node.astext() if title_node else docname
                parts.append(f"\n---\n\n# {title}\n\n{text}")

    return "\n".join(parts) + "\n"


def on_build_finished(app: Sphinx, exception: Exception | None) -> None:
    """Event handler called when the build finishes."""
    if exception:
        return

    if app.builder.name != "html":
        return

    exclude = app.config.llms_txt_exclude
    master_doc = app.config.master_doc

    section_groups = _get_section_groups(app.env, master_doc, exclude)
    if not section_groups:
        logger.warning("llms_txt: no toctree sections found, skipping generation")
        return

    llms_txt = _generate_llms_txt(app, section_groups)
    llms_full_txt = _generate_llms_full_txt(app, section_groups)

    outdir = app.outdir
    llms_txt_path = os.path.join(outdir, "llms.txt")
    llms_full_txt_path = os.path.join(outdir, "llms-full.txt")

    with open(llms_txt_path, "w", encoding="utf-8") as f:
        f.write(llms_txt)
    logger.info("llms_txt: wrote %s", llms_txt_path)

    with open(llms_full_txt_path, "w", encoding="utf-8") as f:
        f.write(llms_full_txt)
    logger.info("llms_txt: wrote %s", llms_full_txt_path)


def setup(app: Sphinx) -> dict:
    app.add_config_value("llms_txt_base_url", DEFAULT_BASE_URL, "html")
    app.add_config_value("llms_txt_exclude", DEFAULT_EXCLUDE, "html")
    app.add_config_value("llms_txt_description", DEFAULT_DESCRIPTION, "html")
    app.connect("build-finished", on_build_finished)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
