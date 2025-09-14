"""
Section de recherche avec mécanisme de retry et diagnostic avancé
Version corrigée et compatible - Entièrement traduite
"""
import streamlit as st
from translations import get_text, format_text
from api.valueserp import ValueSERPAPIWithRetry, diagnose_valueserp_issues
from scrapers.schema_scraper import SchemaScraper
from analyzers.schema_analyzer import SchemaAnalyzer
from utils.cache import get_cached_serp_results, set_cached_serp_results
from utils.valueserp_locations import get_reliable_locations
import time


def search_section():
    """Section de recherche Google avec retry automatique"""

    # Alerte de statut ValueSERP en haut
    if st.session_state.get('show_valueserp_status', True):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.info(f"ℹ️ {get_text('valueserp_status_info', st.session_state.language)}")
            with col2:
                if st.button(
                        f"🔍 {get_text('diagnostic', st.session_state.language)}",
                        help=get_text('check_api_status', st.session_state.language)
                ):
                    run_diagnostic()

    # Configuration de la recherche
    st.subheader(f"🔍 {get_text('search_configuration', st.session_state.language)}")

    col1, col2 = st.columns(2)

    with col1:
        keyword = st.text_input(
            get_text('keyword', st.session_state.language),
            placeholder=get_text('keyword_placeholder', st.session_state.language),
            help=get_text('keyword_help', st.session_state.language)
        )

    with col2:
        # Format function dynamique pour les langues de recherche
        def get_search_language_display(lang_code):
            lang_names = {
                'fr': {
                    'fr': '🇫🇷 Français',
                    'en': '🇬🇧 Anglais',
                    'es': '🇪🇸 Espagnol',
                    'de': '🇩🇪 Allemand',
                    'it': '🇮🇹 Italien'
                },
                'en': {
                    'fr': '🇫🇷 French',
                    'en': '🇬🇧 English',
                    'es': '🇪🇸 Spanish',
                    'de': '🇩🇪 German',
                    'it': '🇮🇹 Italian'
                },
                'es': {
                    'fr': '🇫🇷 Francés',
                    'en': '🇬🇧 Inglés',
                    'es': '🇪🇸 Español',
                    'de': '🇩🇪 Alemán',
                    'it': '🇮🇹 Italiano'
                }
            }
            current_lang = st.session_state.get('language', 'fr')
            return lang_names.get(current_lang, lang_names['fr']).get(lang_code, lang_code)

        search_language = st.selectbox(
            get_text('search_language', st.session_state.language),
            options=['fr', 'en', 'es', 'de', 'it'],
            format_func=get_search_language_display,
            help=get_text('search_language_help', st.session_state.language)
        )

    # Localisation simplifiée pour éviter les problèmes
    st.subheader(f"🌐 {get_text('localization', st.session_state.language)}")

    # Options pré-testées et fonctionnelles
    reliable_locations = get_reliable_locations()

    location_display = st.selectbox(
        get_text('choose_location', st.session_state.language),
        options=list(reliable_locations.keys()),
        index=0,
        help=get_text('tested_reliable_locations', st.session_state.language)
    )

    location = reliable_locations[location_display]

    # Paramètres avancés (optionnel)
    with st.expander(f"⚙️ {get_text('advanced_settings', st.session_state.language)}", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            retry_enabled = st.checkbox(
                f"🔄 {get_text('auto_retry_503', st.session_state.language)}",
                value=True,
                help=get_text('retry_help', st.session_state.language)
            )

            if retry_enabled:
                max_retries = st.slider(
                    get_text('max_retries', st.session_state.language),
                    1, 5, 3
                )
            else:
                max_retries = 1

        with col2:
            show_debug = st.checkbox(
                f"🔧 {get_text('debug_mode', st.session_state.language)}",
                value=False
            )

        if show_debug:
            debug_params = f"""
{get_text('search_params', st.session_state.language)} :
• {get_text('keyword', st.session_state.language)} : {keyword or get_text('keyword_undefined', st.session_state.language)}
• {get_text('localization', st.session_state.language)} : {location}
• {get_text('search_language', st.session_state.language)} : {search_language}
• {get_text('auto_retry_503', st.session_state.language)} : {retry_enabled}
• {get_text('max_retries', st.session_state.language)} : {max_retries}
            """
            st.code(debug_params)

    # Bouton principal d'analyse
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        analyze_button = st.button(
            f"🚀 {get_text('analyze_button', st.session_state.language)}",
            type="primary",
            use_container_width=True,
            help=get_text('launch_analysis', st.session_state.language)
        )

    if analyze_button:
        # Validations
        if not st.session_state.api_key:
            st.error(f"🔑 {get_text('error_api_key', st.session_state.language)}")
            st.info(f"💡 {get_text('configure_api_key', st.session_state.language)}")
            return

        if not keyword or len(keyword.strip()) < 2:
            st.error(f"🔍 {get_text('error_keyword', st.session_state.language)}")
            return

        keyword = keyword.strip()

        # Vérifier le cache en premier
        cached_results = get_cached_serp_results(keyword, location, search_language)
        if cached_results:
            st.success(f"📦 {get_text('no_api_needed', st.session_state.language)}")
            st.session_state.serp_results = cached_results
            st.session_state.schema_analysis = cached_results.get('analysis')
            st.rerun()
            return

        # Effectuer la recherche avec retry
        perform_search_with_retry(keyword, location, location_display, search_language, max_retries, show_debug)


def perform_search_with_retry(keyword, location, location_display, search_language, max_retries, show_debug):
    """Effectue la recherche avec mécanisme de retry"""

    # Container pour les messages de statut
    status_container = st.container()
    progress_container = st.container()

    with status_container:
        st.info(f"🔍 {get_text('starting_analysis', st.session_state.language)}")

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Initialiser l'API avec retry
        api = ValueSERPAPIWithRetry(st.session_state.api_key)
        api.max_retries = max_retries - 1  # -1 car on compte la première tentative

        # Étape 1: Recherche SERP avec retry
        status_text.text(f"📡 {get_text('searching_google_results', st.session_state.language)}")
        progress_bar.progress(20)

        search_result = api.search_google_with_retry(
            keyword,
            location=location,
            language=search_language
        )

        if not search_result:
            st.error(f"❌ {get_text('no_api_response', st.session_state.language)}")
            return

        # Vérifier s'il y a une erreur
        if 'error' in search_result:
            status_code = search_result.get('status_code', 'N/A')
            error_msg = search_result['error']

            st.error(f"❌ {get_text('api_error', st.session_state.language)} {status_code}: {error_msg}")

            # Afficher les suggestions si disponibles
            if 'suggestions' in search_result:
                st.info(f"💡 {get_text('suggested_solutions', st.session_state.language)}")
                for suggestion in search_result['suggestions']:
                    st.write(f"• {suggestion}")

            # Suggestions spécifiques selon l'erreur
            if status_code == 503:
                st.warning(f"⚠️ {get_text('service_overloaded', st.session_state.language)}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🔄 {get_text('retry_now', st.session_state.language)}"):
                        st.rerun()
                with col2:
                    if st.button(f"📊 {get_text('check_valueserp_status', st.session_state.language)}"):
                        st.link_button(f"🌐 {get_text('valueserp_status_page', st.session_state.language)}",
                                       "https://valueserp.statuspage.io/")

            return

        # Vérifier les résultats organiques
        results = search_result.get('organic_results', [])
        if not results:
            st.warning(f"⚠️ {get_text('no_organic_results', st.session_state.language)}")
            return

        progress_bar.progress(40)
        status_text.text(format_text('results_retrieved_analyzing', st.session_state.language, count=len(results)))

        # Étape 2: Analyse des schemas
        schema_scraper = SchemaScraper()
        scraper_results = schema_scraper.analyze_serp_results(results)

        progress_bar.progress(70)
        status_text.text(f"📊 {get_text('processing_analyzing_data', st.session_state.language)}")

        # Étape 3: Analyse des données
        analyzer = SchemaAnalyzer()
        analysis = analyzer.analyze_serp_schemas(scraper_results)

        progress_bar.progress(90)
        status_text.text(f"✅ {get_text('finalizing', st.session_state.language)}")

        # Combiner les résultats
        final_results = {
            **scraper_results,
            'analysis': analysis,
            'search_params': {
                'keyword': keyword,
                'location': location,
                'location_display': location_display,
                'language': search_language
            }
        }

        # Sauvegarder
        st.session_state.serp_results = final_results
        st.session_state.schema_analysis = analysis
        set_cached_serp_results(keyword, location, search_language, final_results)

        progress_bar.progress(100)

        # Résumé de succès
        total_schemas = sum(analysis.get('schema_coverage', {}).get(schema, {}).get('count', 0)
                            for schema in analysis.get('schema_coverage', {}))

        status_container.empty()
        progress_container.empty()

        st.success(f"🎉 {get_text('analysis_complete', st.session_state.language)}")

        # Métriques finales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(get_text('urls_analyzed', st.session_state.language),
                      len(scraper_results.get('urls_analyzed', [])))
        with col2:
            st.metric(get_text('schema_types', st.session_state.language), len(analysis.get('schema_coverage', {})))
        with col3:
            st.metric(get_text('total_schemas', st.session_state.language), total_schemas)

        st.info(f"👉 {get_text('check_results_tab', st.session_state.language)}")

        # Masquer l'alerte de statut après succès
        st.session_state.show_valueserp_status = False

    except Exception as e:
        st.error(f"❌ {get_text('unexpected_error', st.session_state.language)}: {str(e)}")
        if show_debug:
            st.exception(e)


def run_diagnostic():
    """Lance un diagnostic complet de ValueSERP"""
    if not st.session_state.api_key:
        st.error(f"🔑 {get_text('missing_api_key_diagnostic', st.session_state.language)}")
        return

    with st.spinner(f"🔍 {get_text('diagnostic_running', st.session_state.language)}"):
        diagnosis = diagnose_valueserp_issues(st.session_state.api_key)

    st.subheader(f"📋 {get_text('valueserp_diagnostic_report', st.session_state.language)}")

    # Statut global
    status = diagnosis['service_status']['status']
    if status == 'operational':
        st.success(f"✅ {diagnosis['service_status']['message']}")
        # Masquer l'alerte si tout va bien
        st.session_state.show_valueserp_status = False
    elif status == 'degraded':
        st.warning(f"⚠️ {diagnosis['service_status']['message']}")
        if 'details' in diagnosis['service_status']:
            st.write(f"**{get_text('details', st.session_state.language)}:** {diagnosis['service_status']['details']}")
    else:
        st.error(f"❌ {diagnosis['service_status']['message']}")
        if 'details' in diagnosis['service_status']:
            st.write(f"**{get_text('details', st.session_state.language)}:** {diagnosis['service_status']['details']}")

    # Recommandations
    if diagnosis['recommendations']:
        st.subheader(f"💡 {get_text('recommendations', st.session_state.language)}")
        for rec in diagnosis['recommendations']:
            st.write(f"• {rec}")

    # Informations techniques
    with st.expander(f"🔧 {get_text('technical_info', st.session_state.language)}", expanded=False):
        st.json(diagnosis)

    # Liens utiles
    st.subheader(f"🔗 {get_text('useful_links', st.session_state.language)}")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button(f"📊 {get_text('valueserp_status_page', st.session_state.language)}",
                       "https://valueserp.statuspage.io/")
    with col2:
        st.link_button(f"🔧 {get_text('valueserp_support', st.session_state.language)}",
                       "https://www.valueserp.com/contact")