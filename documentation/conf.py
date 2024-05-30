project = "roastery"
release = "202405"

author = "Laurens Duijvesteijn"
copyright = "Laurens Duijvesteijn, 2024"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]
html_theme = "furo"
html_title = "<code>roastery</code>"

autodoc_default_options = {
  "undoc-members": True,
  "member-order": "bysource",
}
autodoc_typehints = "both"

autodoc_type_aliases = {
    "CleanFn": "roastery.importer.CleanFn",
    "ExtractFn": "roastery.importer.ExtractFn",
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'fava': ("https://beancount.github.io/fava/", None),
}

nitpicky = True
nitpick_ignore = [
  ("py:class", r"any"),
  ("py:class", r"roastery.importer.CleanFn"),
  ("py:class", r"roastery.importer.ExtractFn"),
]
nitpick_ignore_regex = [
  ("py:class", r"beancount.*"),
]

exclude_patterns = [
  r"getting-started/finance.*"
]

todo_include_todos = True
