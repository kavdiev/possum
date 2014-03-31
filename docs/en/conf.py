# -*- coding: utf-8 -*-
from datetime import datetime
import os
import sys

# if needed, create possum/settings.py
POSSUM = os.path.join("..", "..")
CONF = os.path.join("..", "..", "possum", "settings.py")
CONF_TEMPLATE = os.path.join("..", "possum", "settings_production.py")
if not os.path.isfile(CONF):
    import shutil
    shutil.copyfile(CONF_TEMPLATE, CONF)

sys.path.append(POSSUM)
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest',
              'sphinx.ext.inheritance_diagram', 'sphinx.ext.todo',
              'sphinx.ext.coverage']

templates_path = [os.path.join('..', '_templates')]
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'
project = u'Possum'
copyright = u'2008-%d, Bonnegent Sébastien' % datetime.now().year

version = '0.5.0'
#release = "%s.1" % version
#release =  "%s-rc1" % version
release = version

language = 'en'
today_fmt = '%B %d, %Y'
exclude_trees = ['_build']

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None
default_role = 'obj'

pygments_style = 'sphinx'
html_theme = 'default'
html_theme_options = {}
html_title = "%s %s" % (project, release)
html_logo = os.path.join("..", "images", "bandeau-192.png")
html_favicon = os.path.join("..", "_static", "favicon.ico")
html_static_path = [os.path.join('..', '_static')]

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}
html_sidebars = {
    '**': ['globaltoc.html', 'searchbox.html', 'ohloh.html'],
}
#    '**': ['globaltoc.html', 'localtoc.html', 'searchbox.html'],
#    'using/windows': ['windowssidebar.html', 'searchbox.html'],

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_use_modindex = True
html_use_modindex = False

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True
html_show_sourcelink = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Possumdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
# latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
# latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'Possum.tex', u'Possum Documentation',
   u'Bonnegent Sébastien', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# Additional stuff for the LaTeX preamble.
# latex_preamble = ''

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_use_modindex = True
