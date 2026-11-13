# Sphinx configuration for the OperaSim-AGX hackathon manual.
project = "OperaSim-AGX ハッカソン セットアップガイド"
copyright = "2026, OperaSim-AGX contributors"
author = "OperaSim-AGX contributors"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx_rtd_theme"]

exclude_patterns = ["_build", "*.md"]

source_suffix = ".rst"
master_doc = "index"

language = "ja"

html_theme = "sphinx_rtd_theme"
html_title = "OperaSim-AGX ハッカソン セットアップガイド"
