"""
Module pour la section des résultats d'analyse
"""
import streamlit as st
import pandas as pd
import json
from config import Config
from translations import get_text
from utils.helpers import (
    get_domain_from_url, get_schema_icon,
    generate_schema_report, create_download_button
)


def results_section():
    """Section des résultats d'analyse"""
    if not st.session_state.serp_results:
        st.info(get_text('no_schemas_found', st.session_state.language))
        return

    results = st.session_state.serp_results
    analysis = results.get('analysis', {})

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="URLs analysées",
            value=analysis.get('total_urls', 0)
        )

    with col2:
        st.metric(
            label="Types de schemas",
            value=len(analysis.get('schema_coverage', {}))
        )

    with col3:
        competitive_count = len(analysis.get('competitive_schemas', []))
        st.metric(
            label="Schemas compétitifs",
            value=competitive_count
        )

    with col4:
        avg_schemas = sum(d['count'] for d in analysis.get('schema_coverage', {}).values()) / analysis.get('total_urls', 1)
        st.metric(
            label="Schemas/page (moy.)",
            value=f"{avg_schemas:.1f}"
        )

    # Distribution des schemas
    st.subheader(f"📊 {get_text('schema_distribution', st.session_state.language)}")

    if analysis.get('schema_coverage'):
        # Créer un DataFrame pour l'affichage
        coverage_data = []
        for schema_type, data in analysis['schema_coverage'].items():
            coverage_data.append({
                'Schema': f"{get_schema_icon(schema_type)} {schema_type}",
                'Sites': data['count'],
                'Couverture': f"{data['percentage']}%",
                'Positions': analysis['position_analysis'].get(schema_type, {}).get('positions', [])
            })

        df = pd.DataFrame(coverage_data)
        df = df.sort_values('Sites', ascending=False)

        # Afficher le tableau
        st.dataframe(
            df[['Schema', 'Sites', 'Couverture']],
            use_container_width=True,
            hide_index=True
        )

        # Graphique de distribution
        if st.checkbox("Afficher le graphique"):
            chart_data = pd.DataFrame({
                'Schema': [d['Schema'] for d in coverage_data],
                'Sites': [d['Sites'] for d in coverage_data]
            })
            st.bar_chart(chart_data.set_index('Schema'))

    # Résultats détaillés
    with st.expander(f"🔍 {get_text('detailed_results', st.session_state.language)}"):
        schema_results = results.get('schema_results', {})

        for url_data in schema_results.get('urls_analyzed', []):
            st.write(f"**Position {url_data['position']}**: {get_domain_from_url(url_data['url'])}")

            if url_data['schema_types']:
                # Afficher les types de schemas
                schema_list = ", ".join([f"{get_schema_icon(s)} {s}" for s in url_data['schema_types']])
                st.write(f"Schemas: {schema_list}")

                # Bouton pour voir les détails
                if st.button(f"👁️ Voir les schemas", key=f"view_schemas_{url_data['position']}"):
                    # Stocker dans session state pour afficher en dehors de l'expander
                    st.session_state[f"show_schemas_{url_data['position']}"] = True
            else:
                st.write("Aucun schema trouvé")

            st.divider()

    # Afficher les schemas détaillés (code existant)
    _display_detailed_schemas(results)

    # Télécharger le rapport
    if st.button("📥 Télécharger le rapport"):
        report = generate_schema_report(analysis, st.session_state.language)
        create_download_button(
            data=report,
            filename=f"schema_analysis_{results['keyword']}.md",
            label="Télécharger le rapport (Markdown)",
            file_type="text"
        )


def _display_detailed_schemas(results):
    """Affiche les schemas détaillés pour chaque URL"""
    if 'schema_results' in results:
        schema_results = results.get('schema_results', {})
        for url_data in schema_results.get('urls_analyzed', []):
            if st.session_state.get(f"show_schemas_{url_data['position']}", False):
                st.write(f"### 📋 Schemas pour {get_domain_from_url(url_data['url'])} (Position {url_data['position']})")

                # Bouton pour fermer
                if st.button(f"❌ Fermer", key=f"close_schemas_{url_data['position']}"):
                    st.session_state[f"show_schemas_{url_data['position']}"] = False
                    st.rerun()

                schemas_data = url_data.get('schemas', {})

                # JSON-LD
                if schemas_data.get('json-ld'):
                    st.write("**📋 Schemas JSON-LD:**")

                    # Regrouper les schemas par type pour éviter les doublons visuels
                    schemas_by_type = {}
                    for i, schema in enumerate(schemas_data['json-ld']):
                        if '@type' in schema:
                            schema_type = schema['@type']
                            # Gérer le cas où @type est une liste
                            if isinstance(schema_type, list):
                                for t in schema_type:
                                    if t in Config.STANDARD_SCHEMA_TYPES:
                                        schema_type = t
                                        break

                            # Ne garder que les types standards
                            if isinstance(schema_type, str) and schema_type in Config.STANDARD_SCHEMA_TYPES:
                                if schema_type not in schemas_by_type:
                                    schemas_by_type[schema_type] = []
                                schemas_by_type[schema_type].append(schema)

                    # Afficher les schemas groupés par type
                    for schema_type, schemas_list in sorted(schemas_by_type.items()):
                        st.write(f"**{get_schema_icon(schema_type)} {schema_type}** ({len(schemas_list)} instance{'s' if len(schemas_list) > 1 else ''})")

                        # Si un seul schema de ce type, l'afficher directement
                        if len(schemas_list) == 1:
                            st.code(json.dumps(schemas_list[0], indent=2, ensure_ascii=False), language='json')
                        else:
                            # Si plusieurs, créer des tabs
                            tabs = st.tabs([f"Instance {i + 1}" for i in range(len(schemas_list))])
                            for i, (tab, schema) in enumerate(zip(tabs, schemas_list)):
                                with tab:
                                    # Afficher un résumé si possible
                                    if 'name' in schema:
                                        st.caption(f"Nom: {schema['name']}")
                                    if '@id' in schema:
                                        st.caption(f"ID: {schema['@id']}")
                                    st.code(json.dumps(schema, indent=2, ensure_ascii=False), language='json')

                # Microdata
                if schemas_data.get('microdata'):
                    st.write("**🏷️ Schemas Microdata:**")
                    for schema in schemas_data['microdata']:
                        if 'type' in schema:
                            type_url = schema['type']
                            if isinstance(type_url, str) and 'schema.org' in type_url:
                                type_name = type_url.split('/')[-1]
                                if type_name in Config.STANDARD_SCHEMA_TYPES:
                                    st.write(f"**{get_schema_icon(type_name)} {type_name}**")
                                    st.code(json.dumps(schema, indent=2, ensure_ascii=False), language='json')

                st.divider()