"""
Module pour la section de recherche Google
"""
import streamlit as st
from translations import get_text
from api.valueserp import ValueSERPAPI
from scrapers.schema_scraper import SchemaScraper
from analyzers.schema_analyzer import SchemaAnalyzer
from utils.cache import get_cached_serp_results, set_cached_serp_results


def search_section():
    """Section de recherche Google"""
    col1, col2, col3 = st.columns(3)

    with col1:
        keyword = st.text_input(
            get_text('keyword', st.session_state.language),
            placeholder=get_text('keyword_placeholder', st.session_state.language)
        )

    with col2:
        location = st.text_input(
            get_text('search_location', st.session_state.language),
            value="France"
        )

    with col3:
        search_language = st.selectbox(
            get_text('search_language', st.session_state.language),
            options=['fr', 'en', 'es', 'de', 'it'],
            format_func=lambda x: {
                'fr': '🇫🇷 Français',
                'en': '🇬🇧 English',
                'es': '🇪🇸 Español',
                'de': '🇩🇪 Deutsch',
                'it': '🇮🇹 Italiano'
            }[x]
        )

    if st.button(get_text('analyze_button', st.session_state.language), type="primary"):
        if not st.session_state.api_key:
            st.error(get_text('error_api_key', st.session_state.language))
            return

        if not keyword:
            st.error(get_text('error_keyword', st.session_state.language))
            return

        # Vérifier le cache
        cached_results = get_cached_serp_results(keyword, location, search_language)
        if cached_results:
            st.info("📦 Résultats récupérés du cache")
            st.session_state.serp_results = cached_results
            st.session_state.schema_analysis = cached_results.get('analysis')
        else:
            # Effectuer la recherche
            with st.spinner(get_text('analyzing', st.session_state.language)):
                api = ValueSERPAPI(st.session_state.api_key)
                results = api.get_search_results(keyword, location=location, language=search_language)

                if results:
                    # Analyser les schemas
                    scraper = SchemaScraper()
                    urls = [r['link'] for r in results if 'link' in r]

                    analysis_results = scraper.analyze_multiple_urls(urls[:10])

                    # Analyser avec SchemaAnalyzer
                    analyzer = SchemaAnalyzer()
                    analysis = analyzer.analyze_serp_schemas(analysis_results)

                    # Stocker les résultats
                    st.session_state.serp_results = {
                        'keyword': keyword,
                        'results': results,
                        'schema_results': analysis_results,
                        'analysis': analysis
                    }

                    # Mettre en cache
                    set_cached_serp_results(keyword, location, search_language, st.session_state.serp_results)

                    st.success(get_text('success_analysis', st.session_state.language))
                else:
                    st.error("Erreur lors de la recherche. Vérifiez votre clé API.")