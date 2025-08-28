"""
Module d'interface utilisateur pour l'application SEO Schema Analyzer
"""

# Imports pour faciliter l'accès
from .search_section import search_section
from .results_section import results_section
from .my_page_section import my_page_section
from .generator_section import generator_section
from .test_section import test_section
from .sidebar import render_sidebar

__all__ = [
    'search_section',
    'results_section',
    'my_page_section',
    'generator_section',
    'test_section',
    'render_sidebar'
]