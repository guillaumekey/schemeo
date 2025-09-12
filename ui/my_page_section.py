"""
Module pour la section d'analyse de sa propre page
Version corrigée avec gestion de la nouvelle structure de données
"""
import streamlit as st
import pandas as pd
import json
from translations import get_text
from scrapers.schema_scraper import SchemaScraper
from analyzers.schema_analyzer import SchemaAnalyzer
from utils.helpers import is_valid_url, normalize_url, get_schema_icon
from utils.cache import get_cached_schema_analysis, set_cached_schema_analysis


def ensure_data_compatibility():
    """Assure la compatibilité entre les différentes structures de données"""
    # Si on a schema_results mais pas serp_results, faire la copie
    if ('schema_results' in st.session_state and
            st.session_state.schema_results and
            'serp_results' not in st.session_state):
        st.session_state.serp_results = st.session_state.schema_results

    # Si on a serp_results mais pas schema_results, faire la copie inverse
    elif ('serp_results' in st.session_state and
          st.session_state.serp_results and
          'schema_results' not in st.session_state):
        st.session_state.schema_results = st.session_state.serp_results


def get_serp_analysis_data():
    """
    Récupère les données d'analyse SERP pour la comparaison
    Gère les différentes structures possibles
    """
    ensure_data_compatibility()

    # Essayer la nouvelle structure
    if 'serp_results' in st.session_state and st.session_state.serp_results:
        return st.session_state.serp_results.get('analysis', {})

    # Essayer l'ancienne structure
    if 'schema_results' in st.session_state and st.session_state.schema_results:
        return st.session_state.schema_results.get('analysis', {})

    return None


def my_page_section():
    """Section pour analyser sa propre page - Version corrigée"""

    # S'assurer de la compatibilité des données
    ensure_data_compatibility()

    my_url = st.text_input(
        get_text('my_url', st.session_state.language),
        placeholder=get_text('my_url_placeholder', st.session_state.language)
    )

    if st.button(get_text('analyze_my_page', st.session_state.language)):
        if not is_valid_url(my_url):
            st.error(get_text('error_url', st.session_state.language))
            return

        # Vérifier le cache
        cached_analysis = get_cached_schema_analysis(my_url)
        if cached_analysis:
            st.info("📦 Analyse récupérée du cache")
            st.session_state.my_page_schemas = cached_analysis
        else:
            with st.spinner(get_text('analyzing', st.session_state.language)):
                try:
                    scraper = SchemaScraper()
                    schemas = scraper.extract_schemas(normalize_url(my_url))

                    # S'assurer que schemas est un dictionnaire
                    if schemas is None:
                        schemas = {}

                    # Obtenir les types de schemas
                    schema_types = scraper.get_schema_types(schemas)

                    # S'assurer que schema_types est un ensemble/liste
                    if schema_types is None:
                        schema_types = set()

                    # Convertir en liste de manière sûre
                    schema_types_list = []
                    if schema_types:
                        try:
                            schema_types_list = list(schema_types)
                        except Exception as e:
                            st.error(f"Erreur conversion liste: {e}")
                            schema_types_list = []

                    st.session_state.my_page_schemas = {
                        'url': my_url,
                        'schemas': schemas,
                        'schema_types': schema_types_list
                    }

                    # Mettre en cache
                    set_cached_schema_analysis(my_url, st.session_state.my_page_schemas)

                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.my_page_schemas = {
                        'url': my_url,
                        'schemas': {},
                        'schema_types': []
                    }

        st.success(get_text('success_analysis', st.session_state.language))

    if st.session_state.my_page_schemas:
        _display_current_schemas()

        # Comparaison avec le top 10 si disponible
        serp_analysis = get_serp_analysis_data()
        if serp_analysis:
            _display_comparison(serp_analysis)
        else:
            st.info(
                "💡 Effectuez d'abord une recherche Google dans l'onglet 'Recherche Google' pour comparer avec le top 10")


def _display_current_schemas():
    """Affiche les schemas actuels de la page"""
    schemas_data = st.session_state.my_page_schemas

    st.subheader(f"📋 {get_text('current_schemas', st.session_state.language)}")

    schema_types = schemas_data.get('schema_types', [])

    if schema_types:
        # Afficher tous les schemas trouvés avec possibilité de cliquer
        for schema_type in sorted(schema_types):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"• {get_schema_icon(schema_type)} {schema_type}")

            with col2:
                if st.button("👁️", key=f"view_{schema_type}_my_page", help=f"Voir le code {schema_type}"):
                    st.session_state[f"show_{schema_type}_code"] = not st.session_state.get(
                        f"show_{schema_type}_code", False)

            # Afficher le code si demandé
            if st.session_state.get(f"show_{schema_type}_code", False):
                # Récupérer les schemas de ce type
                scraper = SchemaScraper()
                matching_schemas = scraper.get_schemas_by_type(schemas_data.get('schemas', {}), schema_type)

                if matching_schemas:
                    for i, schema in enumerate(matching_schemas):
                        if len(matching_schemas) > 1:
                            st.caption(f"Instance {i + 1} de {schema_type}")
                        st.code(json.dumps(schema, indent=2, ensure_ascii=False), language='json')
                else:
                    st.warning(f"Aucun code trouvé pour {schema_type}")

        # Afficher le compte total
        st.info(f"Total : {len(schema_types)} schemas trouvés")

        # Option pour voir le JSON brut
        with st.expander("🔍 Voir les données brutes"):
            st.json(schemas_data.get('schemas', {}))
    else:
        st.write(get_text('no_schemas_found', st.session_state.language))


def _display_comparison(serp_analysis):
    """Affiche la comparaison avec le top 10 - VERSION SIMPLIFIÉE"""
    schemas_data = st.session_state.my_page_schemas

    st.subheader(f"🆚 Comparaison avec le Top 10 Google")

    analyzer = SchemaAnalyzer()
    comparison = analyzer.compare_with_page(
        serp_analysis,
        set(schemas_data.get('schema_types', []))
    )

    # Calculer les métriques
    my_page_unique_schemas = len(set(schemas_data.get('schema_types', [])))
    top10_unique_schemas = len(serp_analysis.get('schema_coverage', {}))

    # Taux de couverture
    if top10_unique_schemas > 0:
        coverage_rate = (len(set(comparison['current_schemas']) & set(
            serp_analysis.get('schema_coverage', {}).keys())) / top10_unique_schemas) * 100
    else:
        coverage_rate = 0

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Mes schemas",
            value=my_page_unique_schemas
        )

    with col2:
        st.metric(
            label="Top 10 schemas",
            value=top10_unique_schemas
        )

    with col3:
        st.metric(
            label="Couverture",
            value=f"{coverage_rate:.0f}%"
        )

    with col4:
        competitive_missing = len(comparison.get('missing_competitive', []))
        if competitive_missing == 0:
            st.metric("Schemas compétitifs", "✅ Complet", delta="Excellent")
        else:
            st.metric("Manquants", competitive_missing, delta=f"-{competitive_missing}")

    # TABLEAU DE COMPARAISON DÉTAILLÉ - PLACÉ DIRECTEMENT ICI
    st.subheader("📊 Analyse détaillée des schemas")

    comparison_data = []

    # Tous les schemas uniques du top 10
    all_top10_schemas = set(serp_analysis.get('schema_coverage', {}).keys())
    my_schemas = set(comparison['current_schemas'])

    for schema_type in all_top10_schemas:
        schema_data = serp_analysis['schema_coverage'][schema_type]

        # Déterminer la priorité
        competitive_schemas = serp_analysis.get('competitive_schemas', [])
        if schema_type in competitive_schemas:
            priority = 'Haute'
        elif schema_data.get('percentage', 0) >= 50:
            priority = 'Moyenne'
        else:
            priority = 'Faible'

        comparison_data.append({
            'Schema': f"{get_schema_icon(schema_type)} {schema_type}",
            'Ma page': '✅' if schema_type in my_schemas else '❌',
            'Usage Top 10': f"{schema_data.get('percentage', 0)}%",
            'Sites': schema_data.get('count', 0),
            'Priorité': priority
        })

    # Ajouter mes schemas uniques
    for schema_type in my_schemas:
        if schema_type not in all_top10_schemas:
            comparison_data.append({
                'Schema': f"{get_schema_icon(schema_type)} {schema_type}",
                'Ma page': '✅',
                'Usage Top 10': '0%',
                'Sites': 0,
                'Priorité': 'Unique'
            })

    # Créer et afficher le DataFrame
    df_comparison = pd.DataFrame(comparison_data)

    # Trier par priorité et usage
    priority_order = {'Haute': 4, 'Moyenne': 3, 'Faible': 2, 'Unique': 1}
    df_comparison['_priority_order'] = df_comparison['Priorité'].map(priority_order)
    df_comparison = df_comparison.sort_values(['_priority_order', 'Sites'], ascending=[False, False])

    # Supprimer la colonne de tri temporaire
    df_comparison = df_comparison.drop('_priority_order', axis=1)

    # Afficher le tableau
    st.dataframe(
        df_comparison,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Schema": st.column_config.TextColumn("Schema", width="medium"),
            "Ma page": st.column_config.TextColumn("Ma page", width="small"),
            "Usage Top 10": st.column_config.TextColumn("Usage Top 10", width="small"),
            "Sites": st.column_config.NumberColumn("Sites", width="small"),
            "Priorité": st.column_config.TextColumn("Priorité", width="small")
        }
    )