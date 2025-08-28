"""
Module pour la section d'analyse de sa propre page
"""
import streamlit as st
import pandas as pd
import json
from translations import get_text
from scrapers.schema_scraper import SchemaScraper
from analyzers.schema_analyzer import SchemaAnalyzer
from utils.helpers import is_valid_url, normalize_url, get_schema_icon
from utils.cache import get_cached_schema_analysis, set_cached_schema_analysis


def my_page_section():
    """Section pour analyser sa propre page"""
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
        if st.session_state.serp_results and st.session_state.serp_results.get('analysis'):
            _display_comparison()
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


def _display_comparison():
    """Affiche la comparaison avec le top 10"""
    schemas_data = st.session_state.my_page_schemas

    st.subheader(f"🔍 Comparaison avec le Top 10 Google")

    analyzer = SchemaAnalyzer()
    comparison = analyzer.compare_with_page(
        st.session_state.serp_results['analysis'],
        set(schemas_data.get('schema_types', []))
    )

    # Calculer les métriques améliorées
    my_page_unique_schemas = len(set(schemas_data.get('schema_types', [])))
    top10_unique_schemas = len(st.session_state.serp_results['analysis']['schema_coverage'])

    # Taux de couverture : schemas de ma page présents dans le top 10 / total schemas du top 10
    if top10_unique_schemas > 0:
        coverage_rate = (len(set(comparison['current_schemas']) & set(
            st.session_state.serp_results['analysis']['schema_coverage'].keys())) / top10_unique_schemas) * 100
    else:
        coverage_rate = 0

    # Métriques de comparaison améliorées
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Mes schemas uniques",
            value=my_page_unique_schemas,
            help="Nombre de types de schemas différents sur votre page"
        )

    with col2:
        st.metric(
            label="Schemas du Top 10",
            value=top10_unique_schemas,
            help="Nombre de types de schemas différents trouvés dans le top 10"
        )

    with col3:
        st.metric(
            label="Taux de couverture",
            value=f"{coverage_rate:.0f}%",
            delta=f"{my_page_unique_schemas}/{top10_unique_schemas}",
            help="Pourcentage des schemas du top 10 que vous avez"
        )

    # Analyse détaillée de la comparaison
    _display_comparison_table(comparison)

    # Recommandations - Seulement haute et moyenne priorité
    _display_filtered_recommendations(comparison, analyzer)


def _display_comparison_table(comparison):
    """Affiche le tableau de comparaison"""
    st.subheader(f"📊 Analyse de la comparaison")

    # Créer un tableau de comparaison
    comparison_data = []
    all_schemas = set()

    # Récupérer tous les schemas du top 10
    for schema_type, data in st.session_state.serp_results['analysis']['schema_coverage'].items():
        all_schemas.add(schema_type)
        comparison_data.append({
            'Schema': f"{get_schema_icon(schema_type)} {schema_type}",
            'Top 10': f"{data['count']}/10 ({data['percentage']}%)",
            'Votre page': '✅ Oui' if schema_type in comparison['current_schemas'] else '❌ Non',
            'Priorité': '🔴 Haute' if schema_type in comparison['missing_competitive'] else
            '🟡 Moyenne' if data['percentage'] > 30 else '🟢 Basse'
        })

    # Ajouter vos schemas uniques
    for schema_type in comparison['unique_schemas']:
        if schema_type not in all_schemas:
            comparison_data.append({
                'Schema': f"{get_schema_icon(schema_type)} {schema_type}",
                'Top 10': '0/10 (0%)',
                'Votre page': '✅ Oui',
                'Priorité': '🔵 Unique'
            })

    # Trier par priorité
    priority_order = {'🔴 Haute': 0, '🟡 Moyenne': 1, '🟢 Basse': 2, '🔵 Unique': 3}
    comparison_data.sort(key=lambda x: priority_order.get(x['Priorité'], 4))

    # Afficher le tableau
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)


def _display_filtered_recommendations(comparison, analyzer):
    """Affiche uniquement les recommandations de priorité haute et moyenne"""
    st.subheader(f"💡 {get_text('recommended_schemas', st.session_state.language)}")

    # Créer des recommandations basées directement sur l'analyse
    recommendations = []

    # Récupérer tous les schemas manquants avec leur priorité
    for schema_type, data in st.session_state.serp_results['analysis']['schema_coverage'].items():
        if schema_type not in comparison['current_schemas']:
            # Déterminer la priorité
            if schema_type in comparison['missing_competitive']:
                priority = 'high'
            elif data['percentage'] >= 30:  # Changé de > à >= pour inclure 30%
                priority = 'medium'
            else:
                priority = 'low'

            # Ajouter uniquement haute et moyenne priorité
            if priority in ['high', 'medium']:
                position_data = st.session_state.serp_results['analysis']['position_analysis'].get(schema_type, {})
                recommendations.append({
                    'schema': schema_type,
                    'priority': priority,
                    'details': {
                        'avg_position': position_data.get('average_position', 'N/A'),
                        'top_3_count': position_data.get('in_top_3', 0),
                        'coverage': data['percentage']
                    }
                })

    # Trier par priorité
    recommendations.sort(key=lambda x: 0 if x['priority'] == 'high' else 1)

    if recommendations:
        # Séparer par priorité
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']

        # Variable pour tracker si on a affiché des recommandations
        has_recommendations = False

        # Afficher les recommandations haute priorité
        if high_priority:
            has_recommendations = True
            st.write("**🔴 Priorité haute** (Schemas présents dans le top 3)")
            for rec in high_priority:
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Utiliser SchemaAnalyzer pour les insights
                    analyzer = SchemaAnalyzer()
                    insights = analyzer.get_schema_insights(rec['schema'])
                    st.write(f"{get_schema_icon(rec['schema'])} **{rec['schema']}**")
                    st.caption(f"Position moyenne: {rec['details'].get('avg_position', 'N/A')} | "
                               f"Présent dans le top 3: {rec['details'].get('top_3_count', 0)} fois")

                    # Afficher les bénéfices
                    if insights.get('benefits'):
                        with st.expander(f"Bénéfices de {rec['schema']}"):
                            for benefit in insights['benefits']:
                                st.write(f"• {benefit}")

                with col2:
                    if st.button(f"➕ Ajouter", key=f"add_high_{rec['schema']}"):
                        if rec['schema'] not in st.session_state.get('selected_schemas', []):
                            if 'selected_schemas' not in st.session_state:
                                st.session_state.selected_schemas = []
                            st.session_state.selected_schemas.append(rec['schema'])
                            st.success(f"{rec['schema']} ajouté!")
                            st.rerun()

        # Afficher les recommandations priorité moyenne
        if medium_priority:
            has_recommendations = True
            if high_priority:  # Ajouter un espace si on a déjà affiché haute priorité
                st.write("")
            st.write("**🟡 Priorité moyenne** (Pratique courante ≥30%)")
            for rec in medium_priority:
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Utiliser SchemaAnalyzer pour les insights
                    analyzer = SchemaAnalyzer()
                    insights = analyzer.get_schema_insights(rec['schema'])
                    st.write(f"{get_schema_icon(rec['schema'])} **{rec['schema']}**")
                    st.caption(f"Présent sur {rec['details'].get('coverage', 0)}% des sites")

                    # Afficher les bénéfices
                    if insights.get('benefits'):
                        with st.expander(f"Bénéfices de {rec['schema']}"):
                            for benefit in insights['benefits']:
                                st.write(f"• {benefit}")

                with col2:
                    if st.button(f"➕ Ajouter", key=f"add_med_{rec['schema']}"):
                        if rec['schema'] not in st.session_state.get('selected_schemas', []):
                            if 'selected_schemas' not in st.session_state:
                                st.session_state.selected_schemas = []
                            st.session_state.selected_schemas.append(rec['schema'])
                            st.success(f"{rec['schema']} ajouté!")
                            st.rerun()

        if not has_recommendations:
            st.info(
                "✅ Votre page est déjà bien optimisée ! Vous avez tous les schemas importants (haute et moyenne priorité).")
    else:
        st.info("✅ Votre page est déjà parfaitement optimisée ! Vous avez tous les schemas importants.")

    # Bouton pour aller au générateur avec les schemas sélectionnés
    if st.session_state.get('selected_schemas'):
        st.write("---")

        # Afficher les schemas sélectionnés
        with st.expander(f"📋 Schemas sélectionnés ({len(st.session_state.selected_schemas)})", expanded=False):
            for schema in st.session_state.selected_schemas:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {get_schema_icon(schema)} {schema}")
                with col2:
                    if st.button("❌", key=f"remove_{schema}", help=f"Retirer {schema}"):
                        st.session_state.selected_schemas.remove(schema)
                        st.rerun()

        # Bouton principal pour générer
        if st.button("🛠️ Générer les schemas sélectionnés", type="primary", use_container_width=True,
                     key="generate_selected_btn"):
            st.session_state.active_tab = 3
            st.success(f"✅ {len(st.session_state.selected_schemas)} schemas prêts à générer !")
            st.info("👉 Cliquez sur l'onglet **'🛠️ Générateur de schemas'** ci-dessus pour continuer.")
            # Note: Le rerun() ne fonctionne pas bien avec les tabs de Streamlit
            # L'utilisateur doit cliquer manuellement sur l'onglet