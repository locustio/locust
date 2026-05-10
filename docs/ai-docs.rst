.. _ai-docs:

==============================
AI-optimized documentation
==============================

Locust provides machine-readable documentation optimized for use with LLMs and AI coding assistants,
following the `llms.txt standard <https://llmstxt.org/>`_.

Available files
===============

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - File
     - Description
     - Use case
   * - `llms.txt <llms.txt>`_
     - Lightweight index with links to all documentation pages and short descriptions
     - Quick reference, tool discovery
   * - `llms-full.txt <llms-full.txt>`_
     - Complete documentation content in a single Markdown file (~200KB)
     - Full context for AI assistants

How to use
==========

**With AI coding assistants:**

Many AI tools can ingest ``llms.txt`` or ``llms-full.txt`` directly. For example, you can point your
assistant to ``https://docs.locust.io/en/stable/llms-full.txt`` to give it full context about Locust.

**With CLI tools:**

.. code-block:: console

    $ curl -s https://docs.locust.io/en/stable/llms-full.txt | your-llm-tool

**As a CLAUDE.md reference:**

.. code-block:: markdown

    # Locust Documentation
    See https://docs.locust.io/en/stable/llms-full.txt for full API and usage docs.

How it works
============

These files are **auto-generated** from the same RST source files that produce this HTML documentation.
They are built during every documentation build using a Sphinx extension, so they are always up to date
and never out of sync with the rest of the docs.

Excluded content: changelog, FAQ, and further reading pages are not included to keep the files focused
on actionable documentation.
