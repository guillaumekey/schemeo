"""
Section de recherche avec mécanisme de retry et diagnostic avancé
Version corrigée et compatible
"""
import streamlit as st
from translations import get_text
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
                st.info(
                    "ℹ️ **Système de retry automatique activé** : En cas d'erreur 503, le système réessaiera automatiquement.")
            with col2:
                if st.button("🔍 Diagnostic", help="Vérifier le statut de l'API"):
                    run_diagnostic()

    # Configuration de la recherche
    st.subheader("🔍 Configuration de la recherche")

    col1, col2 = st.columns(2)

    with col1:
        keyword = st.text_input(
            get_text('keyword', st.session_state.language),
            placeholder=get_text('keyword_placeholder', st.session_state.language),
            help="Entrez le mot-clé principal pour analyser la concurrence"
        )

    with col2:
        search_language = st.selectbox(
            get_text('search_language', st.session_state.language),
            options=['fr', 'en', 'es', 'de', 'it'],
            format_func=lambda x: {
                'fr': '🇫🇷 Français',
                'en': '🇬🇧 English',
                'es': '🇪🇸 Español',
                'de': '🇩🇪 Deutsch',
                'it': '🇮🇹 Italiano'
            }[x],
            help="Langue des résultats de recherche Google"
        )

    # Localisation simplifiée pour éviter les problèmes
    st.subheader("🌍 Localisation")

    # Options pré-testées et fonctionnelles
    reliable_locations = get_reliable_locations()

    location_display = st.selectbox(
        "Choisir une localisation :",
        options=list(reliable_locations.keys()),
        index=0,
        help="Localisations testées et fiables avec ValueSERP"
    )

    location = reliable_locations[location_display]

    # Paramètres avancés (optionnel)
    with st.expander("⚙️ Paramètres avancés", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            retry_enabled = st.checkbox(
                "🔄 Retry automatique en cas d'erreur 503",
                value=True,
                help="Réessaie automatiquement en cas de surcharge du serveur"
            )

            if retry_enabled:
                max_retries = st.slider("Nombre max de tentatives", 1, 5, 3)
            else:
                max_retries = 1

        with col2:
            show_debug = st.checkbox("🔧 Mode debug", value=False)

        if show_debug:
            st.code(f"""
Paramètres de recherche :
• Mot-clé : {keyword or '[non défini]'}
• Localisation : {location}
• Langue : {search_language}
• Retry activé : {retry_enabled}
• Max tentatives : {max_retries}
            """)

    # Bouton principal d'analyse
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        analyze_button = st.button(
            "🚀 " + get_text('analyze_button', st.session_state.language),
            type="primary",
            use_container_width=True,
            help="Lance l'analyse avec retry automatique en cas de problème"
        )

    if analyze_button:
        # Validations
        if not st.session_state.api_key:
            st.error("🔑 " + get_text('error_api_key', st.session_state.language))
            st.info("💡 Configurez votre clé API ValueSERP dans la barre latérale")
            return

        if not keyword or len(keyword.strip()) < 2:
            st.error("📝 " + get_text('error_keyword', st.session_state.language))
            return

        keyword = keyword.strip()

        # Vérifier le cache en premier
        cached_results = get_cached_serp_results(keyword, location, search_language)
        if cached_results:
            st.success("📦 Résultats récupérés du cache - pas de requête API nécessaire")
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
        st.info("🔍 Démarrage de l'analyse avec retry automatique...")

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Initialiser l'API avec retry
        api = ValueSERPAPIWithRetry(st.session_state.api_key)
        api.max_retries = max_retries - 1  # -1 car on compte la première tentative

        # Étape 1: Recherche SERP avec retry
        status_text.text("📡 Recherche des résultats Google (avec retry automatique)...")
        progress_bar.progress(20)

        search_result = api.search_google_with_retry(
            keyword,
            location=location,
            language=search_language
        )

        if not search_result:
            st.error("❌ Aucune réponse de l'API après tous les retries")
            return

        # Vérifier s'il y a une erreur
        if 'error' in search_result:
            status_code = search_result.get('status_code', 'N/A')
            error_msg = search_result['error']

            st.error(f"❌ Erreur {status_code}: {error_msg}")

            # Afficher les suggestions si disponibles
            if 'suggestions' in search_result:
                st.info("💡 **Solutions suggérées:**")
                for suggestion in search_result['suggestions']:
                    st.write(f"• {suggestion}")

            # Suggestions spécifiques selon l'erreur
            if status_code == 503:
                st.warning("⚠️ **Service temporairement surchargé**")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Réessayer maintenant"):
                        st.rerun()
                with col2:
                    if st.button("📊 Vérifier le statut ValueSERP"):
                        st.link_button("🌐 Page de statut ValueSERP", "https://valueserp.statuspage.io/")

            return

        # Vérifier les résultats organiques
        results = search_result.get('organic_results', [])
        if not results:
            st.warning("⚠️ Aucun résultat organique trouvé pour ce mot-clé")
            return

        progress_bar.progress(40)
        status_text.text(f"✅ {len(results)} résultats récupérés - Analyse des schemas...")

        # Étape 2: Analyse des schemas
        schema_scraper = SchemaScraper()
        scraper_results = schema_scraper.analyze_serp_results(results)

        progress_bar.progress(70)
        status_text.text("📊 Traitement et analyse des données...")

        # Étape 3: Analyse des données
        analyzer = SchemaAnalyzer()
        analysis = analyzer.analyze_serp_schemas(scraper_results)

        progress_bar.progress(90)
        status_text.text("✅ Finalisation...")

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

        st.success("🎉 Analyse terminée avec succès !")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("URLs analysées", len(scraper_results.get('urls_analyzed', [])))
        with col2:
            st.metric("Types de schemas", len(analysis.get('schema_coverage', {})))
        with col3:
            st.metric("Total schemas", total_schemas)

        st.info("👉 Consultez l'onglet **'Résultats de l'analyse'** pour voir les détails")

        # Masquer l'alerte de statut après succès
        st.session_state.show_valueserp_status = False

    except Exception as e:
        st.error(f"❌ Erreur inattendue: {str(e)}")
        if show_debug:
            st.exception(e)


def run_diagnostic():
    """Lance un diagnostic complet de ValueSERP"""
    if not st.session_state.api_key:
        st.error("🔑 Clé API manquante pour le diagnostic")
        return

    with st.spinner("🔍 Diagnostic en cours..."):
        diagnosis = diagnose_valueserp_issues(st.session_state.api_key)

    st.subheader("📋 Rapport de diagnostic ValueSERP")

    # Statut global
    status = diagnosis['service_status']['status']
    if status == 'operational':
        st.success(f"✅ {diagnosis['service_status']['message']}")
        # Masquer l'alerte si tout va bien
        st.session_state.show_valueserp_status = False
    elif status == 'degraded':
        st.warning(f"⚠️ {diagnosis['service_status']['message']}")
        if 'details' in diagnosis['service_status']:
            st.write(f"**Détails:** {diagnosis['service_status']['details']}")
    else:
        st.error(f"❌ {diagnosis['service_status']['message']}")
        if 'details' in diagnosis['service_status']:
            st.write(f"**Détails:** {diagnosis['service_status']['details']}")

    # Recommandations
    if diagnosis['recommendations']:
        st.subheader("💡 Recommandations")
        for rec in diagnosis['recommendations']:
            st.write(f"• {rec}")

    # Informations techniques
    with st.expander("🔧 Informations techniques", expanded=False):
        st.json(diagnosis)

    # Liens utiles
    st.subheader("🔗 Liens utiles")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📊 Statut ValueSERP", "https://valueserp.statuspage.io/")
    with col2:
        st.link_button("📧 Support ValueSERP", "https://www.valueserp.com/contact")