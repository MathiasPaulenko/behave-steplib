"""Sphinx configuration for behave-steplib documentation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("..").resolve()))

project = "behave-steplib"
author = "Mathias Paulenko"
copyright = "2025, Mathias Paulenko"
try:
    from steplib._version import __version__ as release
except ImportError:  # pragma: no cover
    release = "0.0.0+unknown"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_autodoc_typehints",
]

templates_path: list[str] = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "behave-steplib documentation"
html_baseurl = "https://mathiaspaulenko.github.io/behave-steplib/"
html_static_path: list[str] = []

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "undoc-members": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
