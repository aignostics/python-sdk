"""Sphinx configuration."""

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add _ext directory to sys.path for custom extensions
sys.path.insert(0, str(Path(__file__).parent / "_ext"))

extensions = [
    "fix_tables",  # Custom extension to fix table structures for LaTeX
    "sphinx_toolbox.collapse",  # https://sphinx-toolbox.readthedocs.io/
    "sphinx_toolbox.sidebar_links",
    "sphinx_toolbox.github",
    "sphinx_toolbox.source",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # https://sphinxcontrib-napoleon.readthedocs.io/en/latest/
    "sphinxcontrib.autodoc_pydantic",  # https://autodoc-pydantic.readthedocs.io/en/stable/users/examples.html
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    "sphinx.ext.extlinks",  # https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
    "sphinx.ext.imgconverter",
    "sphinx_inline_tabs",
    "sphinxcontrib.mermaid",  # https://github.com/mgaitan/sphinxcontrib-mermaid
    "sphinxext.opengraph",
    "swagger_plugin_for_sphinx",  # https://github.com/SAP/swagger-plugin-for-sphinx?tab=readme-ov-file
    "sphinx_selective_exclude.eager_only",  # https://github.com/pfalcon/sphinx_selective_exclude?tab=readme-ov-file
    "sphinx_selective_exclude.search_auto_exclude",
    "sphinx_selective_exclude.modindex_exclude",
    "myst_parser",
]

project = "aignostics"
author = "Helmut Hoffer von Ankershoffen"
copyright = f" (c) 2025-{datetime.now(UTC).year} Aignostics GmbH, Author: {author}"  # noqa: A001
version = "0.2.232"
release = version
github_username = "aignostics"
github_repository = "python-sdk"

language = "en"

ogp_site_name = "Aignostics Python SDK"
ogp_image = "https://aignostics.readthedocs.io/en/latest/_static/logo.png"
ogp_custom_meta_tags = ('<meta name="twitter:card" content="Aignostics Python SDK" />',)
ogp_enable_meta_description = True
ogp_description_length = 300

show_warning_types = True
suppress_warnings = [
    "ref.ref",
    "docutils",
    "myst.xref_missing",
    "myst.domains",
    "myst.xref_ambiguous",
    "myst.header",
]
autodoc_pydantic_model_show_json = False

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc configuration to prevent duplicate object descriptions
# Only document members whose __module__ matches the documented module
autodoc_default_options = {
    "imported-members": False,
}

linkcheck_retries = 2
linkcheck_timeout = 1
linkcheck_workers = 10
linkcheck_ignore = [
    r"http://127\.0\.0\.1",
    r"http://localhost",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"
html_static_path = ["_static"]
html_logo = "../../logo.png"
html_theme_options = {
    "announcement": (
        '<a target="_blank" href="https://github.com/aignostics/python-sdk">GitHub</a> - '
        '<a target="_blank" href="https://pypi.org/project/aignostics">PyPI</a> - '
        '<a target="_blank" href="https://hub.docker.com/r/helmuthva/aignostics-python-sdk/tags">Docker</a> - '
        '<a target="_blank" href="https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk">SonarQube</a> - '
        '<a target="_blank" href="https://app.codecov.io/gh/aignostics/python-sdk">Codecov</a>'
    ),
}


myst_fence_as_directive = ["mermaid"]
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
# Configure table handling for LaTeX
myst_gfm_only = False  # Use full MyST syntax, not just GFM
mermaid_params = ["-p", str(Path(__file__).parent / "puppeteer-config.json")]

# Suppress errors and continue build even with issues
keep_going = True

# Tell latexmk to be more forgiving about undefined references
latex_engine = "lualatex"  # https://github.com/readthedocs/readthedocs.org/issues/8382
latex_use_xindy = True

# If true, show page references after internal links.
latex_show_pagerefs = True

# If true, show URL addresses after external links.
latex_show_urls = "footnote"

# If false, no module index is generated.
latex_domain_indices = True

latex_table_style = ["booktabs", "colorrows"]

# See https://www.sphinx-doc.org/en/master/latex.html
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "a4paper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
    # https://github.com/sphinx-doc/sphinx/issues/12332.
    "preamble": r"""
% Suppress underfull/overfull box warnings
\vbadness=10000
\hbadness=10000
\vfuzz=\maxdimen
\hfuzz=\maxdimen
\emergencystretch=\maxdimen
\tolerance=10000

% Suppress LaTeX warnings about undefined references
\makeatletter
\def\@latex@warning#1{}
\def\@latex@warning@no@line#1{}
\def\G@refundefinedtrue{}
\makeatother

\directlua {
  luaotfload.add_fallback("emoji",
  {
     "[TwemojiMozilla.ttf]:mode=harf;",
     "[DejaVuSans.ttf]:mode=harf;",
  }
  )
}
\setmainfont{LatinModernRoman}[RawFeature={fallback=emoji},SmallCapsFont={* Caps}]
\setsansfont{LatinModernSans}[RawFeature={fallback=emoji}]
\setmonofont{DejaVuSansMono}[RawFeature={fallback=emoji},Scale=0.8]
    """,
    "makeindex": r"\usepackage[columns=1]{idxlayout}\makeindex",
}

slug = re.sub(r"\W+", "-", project.lower())

latex_documents = [
    ("index", f"{slug}.tex", rf"{project} Documentation", author, "manual", False),
]

latex_logo = "../../logo.png"
