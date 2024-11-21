# Configuration file for Sphinx documentation

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'E-Commerce Microservices Platform'
copyright = '2024'
author = 'Your Name'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx_rtd_theme'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Theme configuration
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/14/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
}