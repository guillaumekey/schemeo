"""
Module d'utilitaires et fonctions helpers
"""
from .helpers import (
    is_valid_url,
    normalize_url,
    format_json_for_display,
    create_download_button,
    display_schema_summary,
    get_domain_from_url,
    clean_text,
    merge_schemas,
    calculate_serp_score,
    generate_schema_report,
    estimate_implementation_time,
    create_progress_bar,
    format_schema_for_copy,
    get_schema_icon
)

from .cache import (
    CacheManager,
    cache_manager,
    cached,
    get_cached_serp_results,
    set_cached_serp_results,
    get_cached_schema_analysis,
    set_cached_schema_analysis
)

__all__ = [
    # Helpers
    'is_valid_url',
    'normalize_url',
    'format_json_for_display',
    'create_download_button',
    'display_schema_summary',
    'get_domain_from_url',
    'clean_text',
    'merge_schemas',
    'calculate_serp_score',
    'generate_schema_report',
    'estimate_implementation_time',
    'create_progress_bar',
    'format_schema_for_copy',
    'get_schema_icon',
    # Cache
    'CacheManager',
    'cache_manager',
    'cached',
    'get_cached_serp_results',
    'set_cached_serp_results',
    'get_cached_schema_analysis',
    'set_cached_schema_analysis'
]