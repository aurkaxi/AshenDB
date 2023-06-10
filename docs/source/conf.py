import pathlib
import os
import sys

sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "AshenDB"
copyright = "2023, Abdullah Al Muaz (@aurkaxi)"
author = "Abdullah Al Muaz (@aurkaxi)"
release = "0.0.6"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.napoleon",
]
autodoc_typehints = "both"
autodoc_member_order = "bysource"

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["css/overwrite.css"]
html_logo = "AshenDB_Logo.png"
html_theme_options = {
    "sidebar_hide_name": True,
    "announcement": "<em>Important</em>: This is a pre-release version of AshenDB. It is not recommended for production use.",
    # Defining Dracula theme colors
    "dark_css_variables": {
        # Base Colors
        "color-foreground-primary": "#d9dad8",
        "color-foreground-secondary": "#75a9a4",
        "color-foreground-muted": "#6d7c99",
        "color-background-border": "#333437",
        "color-background-primary": "#0d0e10",
        "color-background-secondary": "#333437",
        "color-background-hover": "#405256",
        "color-background-hover--transparent": "#40525600",
        "color-background-border": "#6d7c99",
        "color-background-item": "#333437",
        # Announcements
        "color-announcement-background": "#a55d80",
        "color-announcement-text": "#d9dad8",
        # Brand Colors
        "color-brand-primary": "#75a9a4",
        "color-brand-content": "#88c0d0",
        # Highlighted Text (search)
        "color-highlight-background": "#6d7c99",
        # GUI Labels
        "color-guilabel-background": "#6d7c9900",
        "color-guilabel-border": "#33343780",
        # API documentation
        "color-api-keyword": "#75a9a4",
        "color-highlight-on-target": "#405256",
        "color-api-background": "#1d232c",
        # Admonitions
        "color-admonition-background": "#6d7c99",
        # Cards
        "color-card-border": "#333437",
        "color-card-background": "#6d7c99",
        "color-card-marginal-background": "#405256",
    },
    "light_css_variables": {
        "font-stack": "FiraCode Nerd Font",
        "font-stack--monospace": "FiraCode Nerd Font",
    },
}
pygments_dark_style = "dracula"
