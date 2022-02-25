#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import os
import subprocess

from locust.argument_parser import get_empty_argument_parser, setup_parser_arguments


# Run command `locust --help` and store output in cli-help-output.txt which is included in the docs
def save_locust_help_output():
    cli_help_output_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cli-help-output.txt")
    print(f"Running `locust --help` command and storing output in {cli_help_output_file}")
    help_output = subprocess.check_output(["locust", "--help"]).decode("utf-8")
    with open(cli_help_output_file, "w") as f:
        f.write(help_output)


save_locust_help_output()

# Generate RST table with help/descriptions for all available environment variables


def save_locust_env_variables():
    env_options_output_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config-options.rst")
    print(f"Generating RST table for Locust environment variables and storing in {env_options_output_file}")
    parser = get_empty_argument_parser()
    setup_parser_arguments(parser)
    table_data = []
    for action in parser._actions:
        if action.env_var:
            table_data.append(
                (
                    ", ".join([f"``{c}``" for c in action.option_strings]),
                    f"``{action.env_var}``",
                    ", ".join([f"``{c}``" for c in parser.get_possible_config_keys(action) if not c.startswith("--")]),
                    action.help,
                )
            )
    colsizes = [max(len(r[i]) for r in table_data) for i in range(len(table_data[0]))]
    formatter = " ".join("{:<%d}" % c for c in colsizes)
    rows = [formatter.format(*row) for row in table_data]
    edge = formatter.format(*["=" * c for c in colsizes])
    divider = formatter.format(*["-" * c for c in colsizes])
    headline = formatter.format(*["Command line", "Environment", "Config file", "Description"])
    output = "\n".join(
        [
            edge,
            headline,
            divider,
            "\n".join(rows),
            edge,
        ]
    )
    with open(env_options_output_file, "w") as f:
        f.write(output)


save_locust_env_variables()


# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
from locust import __version__

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx-prompt",
    "sphinx_substitution_extensions",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_search.extension",
]

# autoclass options
# autoclass_content = "both"

autodoc_typehints = "none"  # I would have liked to use 'description' but unfortunately it too is very verbose

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General substitutions.
project = "Locust"
# copyright = ''

# Intersphinx config
intersphinx_mapping = {
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}


# The full version, including alpha/beta/rc tags.
release = __version__

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = "%B %d, %Y"

# List of documents that shouldn't be included in the build.
# unused_docs = []

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# Sphinx will recurse into subversion configuration folders and try to read
# any document file within. These should be ignored.
# Note: exclude_dirnames is new in Sphinx 0.5
exclude_dirnames = []

# Options for HTML output
# -----------------------

html_show_sourcelink = False
html_file_suffix = ".html"


# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# Custom CSS overrides
html_static_path = ["_static"]
html_context = {
    "css_files": ["_static/theme-overrides.css", "_static/css/rtd_sphinx_search.min.css"],
}


# HTML theme
# html_theme = "haiku"

# html_theme = "default"
# html_theme_options = {
#    "rightsidebar": "true",
#    "codebgcolor": "#fafcfa",
#    "bodyfont": "Arial",
# }

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = 'trac'

rst_prolog = f"""
.. |version| replace:: {__version__}
"""
