# -*- coding: utf-8 -*-
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import os

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

# autoclass options
#autoclass_content = "both"

# Add any paths that contain templates here, relative to this directory.
#templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'Locust'
#copyright = ''

# Intersphinx config
intersphinx_mapping = {
    'requests': ('http://requests.readthedocs.org/en/latest/', None),
}

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
from locust import __version__

# The full version, including alpha/beta/rc tags.
release = __version__

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

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
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# HTML theme
#html_theme = "haiku"

#html_theme = "default"
#html_theme_options = {
#    "rightsidebar": "true",
#    "codebgcolor": "#fafcfa",
#    "bodyfont": "Arial",
#}

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'trac'
