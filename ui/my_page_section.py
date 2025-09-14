"""
Module pour la section d'analyse de sa propre page
Version corrigée avec gestion complète de la traduction et méthodes compatibles
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

        # Analyser la page
        with st.spinner(get_text('loading', st.session_state.language)):
            try:
                # Vérifier le cache
                cached_data = get_cached_schema_analysis(my_url)
                if cached_data:
                    st.session_state.my_page_schemas = cached_data
                else:
                    # Scraper les schemas
                    scraper = SchemaScraper()
                    schemas_data = scraper.scrape_schemas(my_url)

                    # Analyser les schemas
                    analyzer = SchemaAnalyzer()
                    analyzed_schemas = analyzer.analyze_schemas(schemas_data['schemas'])

                    # Combiner les données
                    result = {
                        **schemas_data,
                        'analysis': analyzed_schemas
                    }

                    # Mettre en cache et sauvegarder
                    set_cached_schema_analysis(my_url, result)
                    st.session_state.my_page_schemas = result

                st.success(get_text('success_analysis', st.session_state.language))

            except Exception as e:
                st.error(f"{get_text('error_general', st.session_state.language)}: {str(e)}")
                return

    # Afficher les résultats s'ils existent
    if st.session_state.my_page_schemas:
        _display_my_page_results()


def _display_my_page_results():
    """Affiche les résultats d'analyse de ma page"""
    schemas_data = st.session_state.my_page_schemas

    # Tabs pour organiser l'affichage
    tab1, tab2 = st.tabs([
        f"📊 {get_text('current_schemas', st.session_state.language)}",
        f"💡 {get_text('recommended_schemas', st.session_state.language)}"
    ])

    with tab1:
        _display_current_schemas(schemas_data)

    with tab2:
        _display_recommendations(schemas_data)


def _display_current_schemas(schemas_data):
    """Affiche les schemas actuels de la page"""
    if not schemas_data.get('schemas'):
        st.info(get_text('no_schemas_found', st.session_state.language))
        return

    # Métriques générales
    st.subheader(f"📈 {get_text('analysis_summary', st.session_state.language)}")

    schema_types = schemas_data.get('schema_types', [])
    unique_schemas = len(set(schema_types))
    total_schemas = len(schema_types)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label=get_text('total_schemas_found', st.session_state.language),
            value=total_schemas
        )

    with col2:
        st.metric(
            label=get_text('unique_schema_types', st.session_state.language),
            value=unique_schemas
        )

    with col3:
        page_score = min(100, (unique_schemas / 5) * 100)  # Score sur 5 schemas principaux
        st.metric(
            label=get_text('optimization_score', st.session_state.language),
            value=f"{page_score:.0f}%"
        )

    # Liste des schemas trouvés
    st.subheader(f"📋 {get_text('schemas_found_on_page', st.session_state.language)}")

    for i, (schema_type, schema_data) in enumerate(schemas_data['schemas'].items()):
        with st.expander(f"{get_schema_icon(schema_type)} {schema_type}", expanded=False):
            # Informations de base du schema
            col1, col2 = st.columns(2)

            with col1:
                if isinstance(schema_data, dict):
                    name = schema_data.get('name', get_text('no_name_specified', st.session_state.language))
                    st.write(f"**{get_text('name_label', st.session_state.language)}** {name}")

                    if 'description' in schema_data:
                        desc = schema_data['description'][:150] + "..." if len(
                            str(schema_data['description'])) > 150 else schema_data['description']
                        st.write(f"**{get_text('description_label', st.session_state.language)}** {desc}")

            with col2:
                if isinstance(schema_data, dict):
                    filled_fields = sum(1 for v in schema_data.values() if v not in [None, "", []])
                    total_fields = len(schema_data)
                    completion = (filled_fields / total_fields * 100) if total_fields > 0 else 0

                    st.metric(
                        label=get_text('completion', st.session_state.language),
                        value=f"{completion:.0f}%"
                    )
                    st.write(f"{filled_fields}/{total_fields} {get_text('fields_filled', st.session_state.language)}")

            # Bouton pour voir le JSON complet
            if st.button(f"{get_text('view_json', st.session_state.language)}", key=f"view_json_{i}"):
                st.json(schema_data)

    # Option pour voir le JSON brut
    with st.expander(f"🔍 {get_text('view_raw_data', st.session_state.language)}"):
        st.json(schemas_data.get('schemas', {}))


def _display_recommendations(schemas_data):
    """Affiche les recommandations de schemas"""
    # Vérifier si on a des données SERP pour la comparaison
    serp_analysis = get_serp_analysis_data()

    if not serp_analysis:
        st.info(get_text('search_first', st.session_state.language))
        return

    # Afficher la comparaison avec le top 10
    _display_comparison(serp_analysis)

    # Afficher les recommandations
    _display_schema_recommendations(serp_analysis, schemas_data)


def _display_comparison(serp_analysis):
    """Affiche la comparaison avec le top 10"""
    schemas_data = st.session_state.my_page_schemas

    st.subheader(f"🆚 {get_text('comparison_with_top10', st.session_state.language)}")

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
            label=get_text('my_schemas', st.session_state.language),
            value=my_page_unique_schemas
        )

    with col2:
        st.metric(
            label=get_text('top10_schemas', st.session_state.language),
            value=top10_unique_schemas
        )

    with col3:
        st.metric(
            label=get_text('coverage', st.session_state.language),
            value=f"{coverage_rate:.0f}%"
        )

    with col4:
        competitive_missing = len(comparison.get('missing_competitive', []))
        if competitive_missing == 0:
            st.metric(get_text('competitive_schemas', st.session_state.language),
                      f"✅ {get_text('complete', st.session_state.language)}",
                      delta=get_text('excellent', st.session_state.language))
        else:
            st.metric(get_text('missing_schemas', st.session_state.language), competitive_missing,
                      delta=f"-{competitive_missing}")

    # Tableau de comparaison détaillée
    st.subheader(f"📊 {get_text('detailed_schema_analysis', st.session_state.language)}")

    comparison_data = []

    # Tous les schemas uniques du top 10
    all_top10_schemas = set(serp_analysis.get('schema_coverage', {}).keys())
    my_schemas = set(comparison['current_schemas'])

    for schema_type in all_top10_schemas:
        schema_info = serp_analysis['schema_coverage'][schema_type]

        # Déterminer le statut
        if schema_type in my_schemas:
            status = f"✅ {get_text('present', st.session_state.language)}"
            action = ""
        else:
            status = f"❌ {get_text('missing', st.session_state.language)}"
            action = get_text('recommended_to_add', st.session_state.language)

        comparison_data.append({
            get_text('schema_type', st.session_state.language): f"{get_schema_icon(schema_type)} {schema_type}",
            get_text('top10_usage', st.session_state.language): f"{schema_info.get('percentage', 0):.0f}%",
            get_text('pages_using_it', st.session_state.language): f"{schema_info.get('count', 0)}/10",
            get_text('status', st.session_state.language): status,
            get_text('action', st.session_state.language): action
        })

    # Afficher le tableau
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def _display_schema_recommendations(serp_analysis, schemas_data):
    """Affiche les recommandations de schemas spécifiques"""
    st.subheader(f"💡 {get_text('schema_recommendations', st.session_state.language)}")
    st.caption(get_text('competitor_analysis', st.session_state.language))

    # Initialiser le sélectionneur de schemas s'il n'existe pas
    if 'selected_schemas' not in st.session_state:
        st.session_state.selected_schemas = []

    analyzer = SchemaAnalyzer()
    comparison = analyzer.compare_with_page(
        serp_analysis,
        set(schemas_data.get('schema_types', []))
    )

    # Générer les recommandations manuellement (puisque get_recommendations n'existe pas)
    recommendations = _generate_recommendations(serp_analysis, comparison)

    if not recommendations:
        st.success(get_text('already_optimized', st.session_state.language))
        return

    # Grouper par priorité
    high_priority = [r for r in recommendations if r['priority'] == 'high']
    medium_priority = [r for r in recommendations if r['priority'] == 'medium']
    low_priority = [r for r in recommendations if r['priority'] == 'low']

    # Afficher les recommandations par priorité
    for priority_group, priority_name, priority_color in [
        (high_priority, get_text('high_priority', st.session_state.language), "🔴"),
        (medium_priority, get_text('medium_priority', st.session_state.language), "🟡"),
        (low_priority, get_text('low_priority', st.session_state.language), "🟢")
    ]:
        if not priority_group:
            continue

        st.subheader(f"{priority_color} {priority_name}")

        for rec in priority_group:
            schema_type = rec['schema']

            with st.expander(f"{get_schema_icon(schema_type)} {schema_type}", expanded=priority_group == high_priority):
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Raison de la recommandation
                    reason_text = _get_reason_text(rec['reason'], rec['details'])
                    st.write(f"**{get_text('recommendation_reason', st.session_state.language)}:** {reason_text}")

                    # Détails du top 10
                    if 'coverage' in rec['details']:
                        coverage = rec['details']['coverage']
                        st.write(f"**{get_text('top10_usage', st.session_state.language)}:** {coverage:.0f}%")

                    # Description du schema
                    schema_desc = _get_schema_description(schema_type)
                    if schema_desc:
                        st.write(f"**{get_text('description', st.session_state.language)}:** {schema_desc}")

                with col2:
                    # Bouton pour ajouter à la sélection
                    if schema_type not in st.session_state.selected_schemas:
                        if st.button(
                                get_text('add_to_selection', st.session_state.language),
                                key=f"add_{schema_type}"
                        ):
                            st.session_state.selected_schemas.append(schema_type)
                            st.rerun()
                    else:
                        st.success(f"✅ {get_text('selected', st.session_state.language)}")
                        if st.button(
                                get_text('remove', st.session_state.language),
                                key=f"remove_{schema_type}"
                        ):
                            st.session_state.selected_schemas.remove(schema_type)
                            st.rerun()

    # Section des schemas sélectionnés
    if st.session_state.selected_schemas:
        st.subheader(f"📝 {get_text('selected_schemas', st.session_state.language)}")

        # Afficher les schemas sélectionnés
        selected_text = ", ".join([f"{get_schema_icon(s)} {s}" for s in st.session_state.selected_schemas])
        st.write(selected_text)

        st.success(
            f"🎉 {len(st.session_state.selected_schemas)} {get_text('schemas_ready_to_generate', st.session_state.language)}")
        st.info(get_text('click_generator_tab', st.session_state.language))

        # Bouton pour aller au générateur
        if st.button(
                f"🛠️ {get_text('generate_selected', st.session_state.language)}",
                type="primary",
                use_container_width=True
        ):
            # Afficher confirmation TRADUITE
            st.success(
                f"✅ {len(st.session_state.selected_schemas)} {get_text('schemas_ready_generator', st.session_state.language)}")
            st.balloons()
            st.info(f"👆 {get_text('click_generator_continue', st.session_state.language)}")


def _generate_recommendations(serp_analysis, comparison):
    """Génère les recommandations basées sur l'analyse SERP et la comparaison"""
    recommendations = []

    # Schemas manquants avec haute priorité (plus de 50% d'utilisation)
    for schema in comparison.get('missing_competitive', []):
        if schema not in [r['schema'] for r in recommendations]:
            coverage = serp_analysis['schema_coverage'].get(schema, {})
            percentage = coverage.get('percentage', 0)

            if percentage >= 50:
                priority = 'high'
                reason = 'high_competition'
            elif percentage >= 20:
                priority = 'medium'
                reason = 'common_practice'
            else:
                priority = 'low'
                reason = 'common_practice'

            recommendations.append({
                'schema': schema,
                'priority': priority,
                'reason': reason,
                'details': {
                    'coverage': percentage
                }
            })

    # Schemas manquants communs
    for schema in comparison.get('missing_common', []):
        if schema not in [r['schema'] for r in recommendations]:
            coverage = serp_analysis['schema_coverage'].get(schema, {})
            recommendations.append({
                'schema': schema,
                'priority': 'medium',
                'reason': 'common_practice',
                'details': {
                    'coverage': coverage.get('percentage', 0)
                }
            })

    # Trier par priorité
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

    return recommendations[:10]  # Limiter à 10 recommandations


def _get_reason_text(reason, details):
    """Retourne le texte explicatif d'une recommandation"""
    reason_texts = {
        'high_competition': get_text('reason_high_competition', st.session_state.language),
        'common_practice': get_text('reason_common_practice', st.session_state.language),
        'page_type_suggestion': get_text('reason_page_type', st.session_state.language),
        'seo_boost': get_text('reason_seo_boost', st.session_state.language)
    }

    return reason_texts.get(reason, get_text('reason_general', st.session_state.language))


def _get_schema_description(schema_type):
    """Retourne la description d'un type de schema"""
    descriptions = {
        'Organization': get_text('schema_desc_organization', st.session_state.language),
        'LocalBusiness': get_text('schema_desc_localbusiness', st.session_state.language),
        'Product': get_text('schema_desc_product', st.session_state.language),
        'Article': get_text('schema_desc_article', st.session_state.language),
        'WebSite': get_text('schema_desc_website', st.session_state.language),
        'BreadcrumbList': get_text('schema_desc_breadcrumb', st.session_state.language),
        'FAQPage': get_text('schema_desc_faq', st.session_state.language),
        'Review': get_text('schema_desc_review', st.session_state.language),
        'AggregateRating': get_text('schema_desc_aggregaterating', st.session_state.language),
        'Event': get_text('schema_desc_event', st.session_state.language),
        'JobPosting': get_text('schema_desc_jobposting', st.session_state.language),
        'Service': get_text('schema_desc_service', st.session_state.language)
    }

    return descriptions.get(schema_type, "")