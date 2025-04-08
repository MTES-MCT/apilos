# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "APiLos"
copyright = "2025, Sylvain Delabye, Nicolas Oudard"
author = "Sylvain Delabye, Nicolas Oudard"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


# Add MyST Parser extension
extensions = ["sphinxcontrib.mermaid", "myst_parser"]

# Configure source suffix to recognize Markdown files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Enable MyST options for diagrams and other rich features
myst_enable_extensions = [
    "colon_fence",  # Supports ::: fenced blocks
]

myst_fence_as_directive = ["mermaid"]

master_doc = "README"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "fr"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
