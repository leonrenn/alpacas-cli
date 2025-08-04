"""Configuration file for the Sphinx documentation builder."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "alpacas-cli")))

extensions = ["sphinx.ext.autodoc"]
html_theme = "sphinx_rtd_theme"
