"""
Module pour la section des résultats d'analyse
Version corrigée avec gestion de la nouvelle structure de données - VERSION COMPLÈTE TRADUITE
"""
import streamlit as st
import pandas as pd
import json
import hashlib
from config import Config
from translations import get_text, format_text
from utils.helpers import (
    get_domain_from_url, get_schema_icon,
    generate_schema_report, create_download_button
)


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


def get_analysis_data():
    """
    Fonction universelle pour récupérer les données d'analyse
    Gère automatiquement les différentes structures
    """
    ensure_data_compatibility()

    # Essayer la nouvelle structure
    if 'serp_results' in st.session_state and st.session_state.serp_results:
        data = st.session_state.serp_results
        return {
            'urls_analyzed': data.get('urls_analyzed', []),
            'analysis': data.get('analysis', {}),
            'schema_frequency': data.get('schema_frequency', {}),
            'schema_by_position': data.get('schema_by_position', {}),
            'search_params': data.get('search_params', {}),
            'full_data': data  # Garder les données complètes
        }

    # Essayer l'ancienne structure
    if 'schema_results' in st.session_state and st.session_state.schema_results:
        data = st.session_state.schema_results
        return {
            'urls_analyzed': data.get('urls_analyzed', []),
            'analysis': data.get('analysis', {}),
            'schema_frequency': data.get('schema_frequency', {}),
            'schema_by_position': data.get('schema_by_position', {}),
            'search_params': data.get('search_params', {}),
            'full_data': data
        }

    return None


def results_section():
    """Section des résultats d'analyse - Version corrigée"""

    # Utiliser la fonction universelle pour récupérer les données
    data = get_analysis_data()

    if not data:
        st.info(get_text('no_schemas_found', st.session_state.language))
        return

    analysis = data.get('analysis', {})
    urls_analyzed = data.get('urls_analyzed', [])

    # Métriques principales
    st.subheader(f"📊 {get_text('main_metrics', st.session_state.language)}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=get_text('urls_analyzed', st.session_state.language),
            value=len(urls_analyzed)
        )

    with col2:
        st.metric(
            label=get_text('schema_types', st.session_state.language),
            value=len(analysis.get('schema_coverage', {}))
        )

    with col3:
        competitive_count = len(analysis.get('competitive_schemas', []))
        st.metric(
            label=get_text('competitive_schemas', st.session_state.language),
            value=competitive_count
        )

    with col4:
        if len(urls_analyzed) > 0:
            total_schemas = sum(d.get('count', 0) for d in analysis.get('schema_coverage', {}).values())
            avg_schemas = total_schemas / len(urls_analyzed)
        else:
            avg_schemas = 0

        st.metric(
            label=get_text('avg_schemas_per_page', st.session_state.language),
            value=f"{avg_schemas:.1f}"
        )

    # Distribution des schemas
    st.subheader(f"📊 {get_text('schema_distribution', st.session_state.language)}")

    if analysis.get('schema_coverage'):
        # Créer un DataFrame pour l'affichage
        coverage_data = []
        for schema_type, schema_data in analysis['schema_coverage'].items():
            coverage_data.append({
                'Schema': f"{get_schema_icon(schema_type)} {schema_type}",
                get_text('websites', st.session_state.language): schema_data.get('count', 0),
                get_text('coverage', st.session_state.language): f"{schema_data.get('percentage', 0)}%",
                get_text('positions', st.session_state.language): analysis.get('position_analysis', {}).get(schema_type,
                                                                                                            {}).get(
                    'positions', [])
            })

        df = pd.DataFrame(coverage_data)
        df = df.sort_values(get_text('websites', st.session_state.language), ascending=False)

        # Afficher le tableau
        st.dataframe(
            df[['Schema', get_text('websites', st.session_state.language),
                get_text('coverage', st.session_state.language)]],
            use_container_width=True,
            hide_index=True
        )

        # Graphique de distribution
        if st.checkbox(get_text('show_chart', st.session_state.language)):
            chart_data = pd.DataFrame({
                'Schema': [d['Schema'] for d in coverage_data],
                get_text('websites', st.session_state.language): [d[get_text('websites', st.session_state.language)] for
                                                                  d in coverage_data]
            })
            st.bar_chart(chart_data.set_index('Schema'))

    # NOUVELLE SECTION : Analyse détaillée par concurrent
    st.divider()
    st.subheader(f"🔍 {get_text('detailed_competitor_analysis', st.session_state.language)}")

    _display_competitor_analysis(data)

    # Télécharger le rapport
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"💾 {get_text('download_report', st.session_state.language)}"):
            report = generate_schema_report(analysis, st.session_state.language)
            create_download_button(
                data=report,
                filename=f"schema_analysis_{data.get('search_params', {}).get('keyword', 'analysis')}.json",
                label=get_text('download_report', st.session_state.language),
                file_type="json"
            )

    with col2:
        if st.button(f"📋 {get_text('download_report_markdown', st.session_state.language)}"):
            report = generate_schema_report(analysis, st.session_state.language)
            create_download_button(
                data=report,
                filename=f"schema_analysis_{data.get('search_params', {}).get('keyword', 'analysis')}.md",
                label=get_text('download_report_markdown', st.session_state.language),
                file_type="text"
            )


def _display_competitor_analysis(data):
    """Affiche l'analyse détaillée par concurrent avec le code des schemas"""
    urls_analyzed = data.get('urls_analyzed', [])

    if not urls_analyzed:
        st.warning(get_text('no_analysis_data_available', st.session_state.language))
        return

    # Options d'affichage
    st.subheader(f"⚙️ {get_text('display_options', st.session_state.language)}")
    col1, col2 = st.columns(2)

    with col1:
        show_all_details = st.checkbox(f"🔍 {get_text('show_all_details', st.session_state.language)}", value=False)

    with col2:
        filter_options = [get_text('all', st.session_state.language)] + list(
            data.get('analysis', {}).get('schema_coverage', {}).keys())
        filter_schema = st.selectbox(
            f"🎯 {get_text('filter_by_schema', st.session_state.language)}",
            options=filter_options,
            index=0
        )

    st.write("")

    # Afficher chaque concurrent
    for url_data in urls_analyzed:
        position = url_data.get('position', 0)
        url = url_data.get('url', '')
        domain = get_domain_from_url(url)
        schema_types = url_data.get('schema_types', [])
        schemas = url_data.get('schemas', {})

        # Filtrage par schema si nécessaire
        if filter_schema != get_text('all', st.session_state.language):
            if filter_schema not in schema_types:
                continue

        # En-tête du concurrent
        with st.container():
            col1, col2, col3 = st.columns([0.5, 3, 1])

            with col1:
                st.metric(get_text('position', st.session_state.language), position)

            with col2:
                st.write(f"**{domain}**")
                st.caption(url)

            with col3:
                if schema_types:
                    st.metric(get_text('schemas', st.session_state.language), len(schema_types))
                else:
                    st.write(f"❌ {get_text('no_schemas', st.session_state.language)}")

        if schema_types:
            # Affichage compact par défaut
            if not show_all_details:
                # Liste des schemas avec icones
                schema_list = []
                for schema_type in sorted(schema_types):
                    icon = get_schema_icon(schema_type)
                    schema_list.append(f"{icon} {schema_type}")

                st.write(
                    f"📋 **{get_text('schemas_detected', st.session_state.language)} :** " + " • ".join(schema_list))

                # Bouton pour voir les détails
                if st.button(f"👁️ {get_text('view_schema_code', st.session_state.language)}",
                             key=f"view_schemas_{position}"):
                    st.session_state[f"show_schemas_{position}"] = not st.session_state.get(
                        f"show_schemas_{position}", False)

            # Affichage détaillé des schemas
            if show_all_details or st.session_state.get(f"show_schemas_{position}", False):
                _display_schemas_for_competitor(schemas, schema_types, position, filter_schema)

        st.divider()


def _display_schemas_for_competitor(schemas, schema_types, position, filter_schema):
    """Affiche les schemas détaillés pour un concurrent - VERSION CORRIGÉE"""

    for schema_type in sorted(schema_types):
        if filter_schema != get_text('all', st.session_state.language) and schema_type != filter_schema:
            continue

        # Récupérer les schemas de ce type
        matching_schemas = _get_schemas_by_type(schemas, schema_type)

        if matching_schemas:
            instance_text = get_text('instance', st.session_state.language) if len(matching_schemas) == 1 else get_text(
                'instances', st.session_state.language)
            with st.expander(
                    f"{get_schema_icon(schema_type)} **{schema_type}** ({len(matching_schemas)} {instance_text})",
                    expanded=False):

                if len(matching_schemas) > 1:
                    # Plusieurs instances - créer des sous-onglets
                    sub_tabs = st.tabs([f"{get_text('instance', st.session_state.language)} {i + 1}" for i in
                                        range(len(matching_schemas))])
                    for i, (sub_tab, schema) in enumerate(zip(sub_tabs, matching_schemas)):
                        with sub_tab:
                            # CORRECTION : Ajouter l'index du schema pour garantir l'unicité
                            _display_single_schema_with_analysis(
                                schema, schema_type, position, len(matching_schemas), schema_index=i
                            )
                else:
                    # Une seule instance
                    _display_single_schema_with_analysis(
                        matching_schemas[0], schema_type, position, 1, schema_index=0
                    )


def _get_schemas_by_type(schemas, schema_type):
    """Récupère les schemas d'un type donné"""
    matching_schemas = []

    # Parcourir tous les schemas
    for key, schema_list in schemas.items():
        if isinstance(schema_list, list):
            for schema in schema_list:
                if isinstance(schema, dict):
                    # Vérifier le @type
                    schema_types = schema.get('@type', [])
                    if isinstance(schema_types, str):
                        schema_types = [schema_types]

                    # Normaliser les types
                    normalized_types = []
                    for st_type in schema_types:
                        if isinstance(st_type, str):
                            # Extraire le nom du type (dernière partie après /)
                            type_name = st_type.split('/')[-1] if '/' in st_type else st_type
                            normalized_types.append(type_name)

                    if schema_type in normalized_types:
                        matching_schemas.append(schema)

    return matching_schemas


def _display_single_schema_with_analysis(schema, schema_type, position, instance_num, schema_index=0):
    """Affiche un schema individuel avec analyse - VERSION CORRIGÉE pour clés uniques"""

    # CORRECTION : Ajouter un identifiant unique basé sur le contenu du schema
    schema_id = schema.get('@id', '')
    schema_name = schema.get('name', '')
    schema_url = schema.get('url', '')

    # Créer un hash unique basé sur le contenu pour éviter les doublons
    content_hash = hashlib.md5(json.dumps(schema, sort_keys=True).encode()).hexdigest()[:8]

    # Créer une clé vraiment unique
    base_key = f"{schema_type}_{position}_{instance_num}_{schema_index}_{content_hash}"

    # Initialiser les états si ils n'existent pas
    analyze_key = f"show_analysis_{base_key}"
    tips_key = f"show_tips_{base_key}"

    if analyze_key not in st.session_state:
        st.session_state[analyze_key] = False
    if tips_key not in st.session_state:
        st.session_state[tips_key] = False

    # Informations de base
    col1, col2 = st.columns([2, 1])

    with col1:
        # Extraire les informations clés du schema
        key_info = {}
        if 'name' in schema:
            key_info[get_text('name', st.session_state.language)] = schema['name']
        if '@id' in schema:
            key_info[get_text('id', st.session_state.language)] = schema['@id']
        if 'url' in schema:
            key_info['URL'] = schema['url']
        if 'description' in schema:
            description = str(schema['description'])
            key_info[get_text('description_label', st.session_state.language)] = description[:100] + "..." if len(
                description) > 100 else description

        if key_info:
            st.write(f"**ℹ️ {get_text('key_information', st.session_state.language)} :**")
            for key, value in key_info.items():
                st.write(f"• **{key}** : {value}")

    with col2:
        # Statistiques du schema
        total_fields = len(schema.keys())
        filled_fields = sum(1 for v in schema.values() if v not in [None, '', [], {}])
        completion = (filled_fields / total_fields * 100) if total_fields > 0 else 0

        st.metric(get_text('completion', st.session_state.language), f"{completion:.0f}%")
        st.caption(
            format_text('fields_filled_count', st.session_state.language, filled=filled_fields, total=total_fields))

    # Boutons d'action avec clés garanties uniques
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"📋 {get_text('copy_code', st.session_state.language)}", key=f"copy_{base_key}"):
            # Code à copier (format prêt pour l'intégration)
            clean_code = {
                "@context": "https://schema.org",
                **schema
            }
            st.code(json.dumps(clean_code, indent=2, ensure_ascii=False), language='json')
            st.success(get_text('copy_ready_code', st.session_state.language))

    with col2:
        analyze_label = f"🔍 {get_text('hide_analysis', st.session_state.language)}" if st.session_state[
            analyze_key] else f"🔍 {get_text('show_analysis', st.session_state.language)}"
        if st.button(analyze_label, key=f"toggle_analysis_{base_key}"):
            st.session_state[analyze_key] = not st.session_state[analyze_key]
            st.rerun()

    with col3:
        tips_label = f"💡 {get_text('hide_tips', st.session_state.language)}" if st.session_state[
            tips_key] else f"💡 {get_text('show_tips', st.session_state.language)}"
        if st.button(tips_label, key=f"toggle_tips_{base_key}"):
            st.session_state[tips_key] = not st.session_state[tips_key]
            st.rerun()

    # Affichage conditionnel des analyses
    if st.session_state[analyze_key]:
        st.write(f"**🔍 {get_text('analysis_schema', st.session_state.language)} :**")
        _analyze_schema_completeness(schema, schema_type)

    if st.session_state[tips_key]:
        st.write(f"**💡 {get_text('optimization_tips', st.session_state.language)} :**")
        _provide_schema_optimization_tips(schema, schema_type)

    # Code JSON complet
    st.write(f"**📝 {get_text('complete_json_ld', st.session_state.language)} :**")
    st.code(json.dumps(schema, indent=2, ensure_ascii=False), language='json')


def _display_detailed_schemas_for_url(url_data, filter_schema=None):
    """Affiche le code détaillé des schemas pour une URL"""
    if filter_schema is None:
        filter_schema = get_text('all', st.session_state.language)

    schemas_data = url_data.get('schemas', {})
    position = url_data.get('position', 0)

    if not schemas_data:
        st.warning(get_text('no_schema_data_available', st.session_state.language))
        return

    # Onglets pour différents types de données structurées
    available_types = []
    if schemas_data.get('json-ld'):
        available_types.append("JSON-LD")
    if schemas_data.get('microdata'):
        available_types.append("Microdata")
    if schemas_data.get('rdfa'):
        available_types.append("RDFa")
    if schemas_data.get('opengraph'):
        available_types.append("OpenGraph")

    if not available_types:
        st.warning(get_text('no_schema_found_data', st.session_state.language))
        return

    # Créer les onglets pour les différents formats
    if len(available_types) > 1:
        tabs = st.tabs(available_types)
    else:
        tabs = [st.container()]

    for i, data_type in enumerate(available_types):
        with tabs[i] if len(available_types) > 1 else tabs[0]:

            if data_type == "JSON-LD":
                _display_json_ld_schemas(schemas_data.get('json-ld', []), filter_schema, position)

            elif data_type == "Microdata":
                _display_microdata_schemas(schemas_data.get('microdata', []), filter_schema, position)

            elif data_type == "RDFa":
                _display_rdfa_schemas(schemas_data.get('rdfa', []), filter_schema, position)

            elif data_type == "OpenGraph":
                _display_opengraph_data(schemas_data.get('opengraph', []), position)


def _display_json_ld_schemas(json_ld_data, filter_schema, position=0):
    """Affiche les schemas JSON-LD avec le code complet - VERSION CORRIGÉE"""
    if not json_ld_data:
        st.info(get_text('no_json_ld_found', st.session_state.language))
        return

    # Regrouper les schemas par type avec index pour éviter les doublons
    schemas_by_type = {}
    for i, schema in enumerate(json_ld_data):
        if '@type' in schema:
            schema_type = schema['@type']

            # Gérer le cas où @type est une liste
            if isinstance(schema_type, list):
                # Prendre le premier type ou chercher un type standard
                for t in schema_type:
                    # Normaliser le type
                    type_name = t.split('/')[-1] if '/' in t else t
                    if hasattr(Config, 'STANDARD_SCHEMA_TYPES') and type_name in Config.STANDARD_SCHEMA_TYPES:
                        schema_type = type_name
                        break
                else:
                    # Si aucun type standard trouvé, prendre le premier
                    schema_type = schema_type[0].split('/')[-1] if '/' in schema_type[0] else schema_type[0]
            else:
                # Normaliser le type simple
                schema_type = schema_type.split('/')[-1] if '/' in schema_type else schema_type

            # Appliquer le filtre
            if filter_schema == get_text('all', st.session_state.language) or schema_type == filter_schema:
                if schema_type not in schemas_by_type:
                    schemas_by_type[schema_type] = []
                # CORRECTION : Stocker le schema avec son index original pour l'unicité
                schemas_by_type[schema_type].append((schema, i))

    if not schemas_by_type:
        message = get_text('no_json_ld_found', st.session_state.language)
        if filter_schema != get_text('all', st.session_state.language):
            message += f" {get_text('for_type', st.session_state.language)} {filter_schema}"
        st.info(message)
        return

    # Afficher chaque type de schema
    for schema_type, schema_list in sorted(schemas_by_type.items()):

        # En-tête du type de schema
        instance_text = get_text('instance', st.session_state.language) if len(schema_list) == 1 else get_text(
            'instances', st.session_state.language)
        with st.expander(
                f"{get_schema_icon(schema_type)} **{schema_type}** ({len(schema_list)} {instance_text})",
                expanded=True):

            # Si plusieurs instances, créer des sous-onglets
            if len(schema_list) > 1:
                sub_tabs = st.tabs(
                    [f"{get_text('instance', st.session_state.language)} {i + 1}" for i in range(len(schema_list))])
                for tab_index, (sub_tab, (schema, original_index)) in enumerate(zip(sub_tabs, schema_list)):
                    with sub_tab:
                        # CORRECTION : Utiliser l'index original + l'index du tab pour l'unicité
                        _display_single_schema_with_analysis(
                            schema, schema_type, position, tab_index + 1, schema_index=original_index
                        )
            else:
                # Une seule instance
                schema, original_index = schema_list[0]
                _display_single_schema_with_analysis(
                    schema, schema_type, position, 1, schema_index=original_index
                )


# CORRECTION ALTERNATIVE : Utiliser un compteur global pour garantir l'unicité absolue
_widget_counter = 0


def get_unique_key(prefix="widget"):
    """Génère une clé garantie unique"""
    global _widget_counter
    _widget_counter += 1
    return f"{prefix}_{_widget_counter}"


def _display_single_schema_with_analysis_v2(schema, schema_type, position, instance_num):
    """Version alternative avec compteur global pour garantir l'unicité absolue"""

    # Utiliser le compteur global pour garantir l'unicité
    unique_id = get_unique_key(f"{schema_type}_{position}")

    # Initialiser les états
    analyze_key = f"show_analysis_{unique_id}"
    tips_key = f"show_tips_{unique_id}"

    if analyze_key not in st.session_state:
        st.session_state[analyze_key] = False
    if tips_key not in st.session_state:
        st.session_state[tips_key] = False

    # Informations de base (même code que précédemment)
    col1, col2 = st.columns([2, 1])

    with col1:
        # Extraire les informations clés du schema
        key_info = {}
        if 'name' in schema:
            key_info[get_text('name', st.session_state.language)] = schema['name']
        if '@id' in schema:
            key_info[get_text('id', st.session_state.language)] = schema['@id']
        if 'url' in schema:
            key_info['URL'] = schema['url']
        if 'description' in schema:
            description = str(schema['description'])
            key_info[get_text('description_label', st.session_state.language)] = description[:100] + "..." if len(
                description) > 100 else description

        if key_info:
            st.write(f"**ℹ️ {get_text('key_information', st.session_state.language)} :**")
            for key, value in key_info.items():
                st.write(f"• **{key}** : {value}")

    with col2:
        # Statistiques du schema
        total_fields = len(schema.keys())
        filled_fields = sum(1 for v in schema.values() if v not in [None, '', [], {}])
        completion = (filled_fields / total_fields * 100) if total_fields > 0 else 0

        st.metric(get_text('completion', st.session_state.language), f"{completion:.0f}%")
        st.caption(
            format_text('fields_filled_count', st.session_state.language, filled=filled_fields, total=total_fields))

    # Boutons d'action avec clés uniques garanties
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"📋 {get_text('copy_code', st.session_state.language)}", key=get_unique_key("copy")):
            clean_code = {"@context": "https://schema.org", **schema}
            st.code(json.dumps(clean_code, indent=2, ensure_ascii=False), language='json')
            st.success(get_text('copy_ready_code', st.session_state.language))

    with col2:
        analyze_label = f"🔍 {get_text('hide_analysis', st.session_state.language)}" if st.session_state[
            analyze_key] else f"🔍 {get_text('show_analysis', st.session_state.language)}"
        if st.button(analyze_label, key=get_unique_key("analyze")):
            st.session_state[analyze_key] = not st.session_state[analyze_key]
            st.rerun()

    with col3:
        tips_label = f"💡 {get_text('hide_tips', st.session_state.language)}" if st.session_state[
            tips_key] else f"💡 {get_text('show_tips', st.session_state.language)}"
        if st.button(tips_label, key=get_unique_key("tips")):
            st.session_state[tips_key] = not st.session_state[tips_key]
            st.rerun()

    # Affichage conditionnel
    if st.session_state[analyze_key]:
        st.write(f"**🔍 {get_text('analysis_schema', st.session_state.language)} :**")
        _analyze_schema_completeness(schema, schema_type)

    if st.session_state[tips_key]:
        st.write(f"**💡 {get_text('optimization_tips', st.session_state.language)} :**")
        _provide_schema_optimization_tips(schema, schema_type)

    # Code JSON complet
    st.write(f"**📝 {get_text('complete_json_ld', st.session_state.language)} :**")
    st.code(json.dumps(schema, indent=2, ensure_ascii=False), language='json')


def _display_microdata_schemas(microdata, filter_schema, position=0):
    """Affiche les schemas Microdata"""
    if not microdata:
        st.info(get_text('no_microdata_found', st.session_state.language))
        return

    for i, schema in enumerate(microdata):
        if 'type' in schema:
            type_url = schema['type']
            if isinstance(type_url, str) and 'schema.org' in type_url:
                type_name = type_url.split('/')[-1]
                if type_name in Config.STANDARD_SCHEMA_TYPES:
                    if filter_schema == get_text('all', st.session_state.language) or type_name == filter_schema:
                        with st.expander(f"{get_schema_icon(type_name)} **{type_name}** (Microdata)", expanded=False):
                            st.code(json.dumps(schema, indent=2, ensure_ascii=False), language='json')


def _display_rdfa_schemas(rdfa_data, filter_schema, position=0):
    """Affiche les schemas RDFa"""
    if not rdfa_data:
        st.info(get_text('no_rdfa_found', st.session_state.language))
        return

    st.code(json.dumps(rdfa_data, indent=2, ensure_ascii=False), language='json')


def _display_opengraph_data(opengraph_data, position=0):
    """Affiche les données OpenGraph"""
    if not opengraph_data:
        st.info(get_text('no_opengraph_found', st.session_state.language))
        return

    st.code(json.dumps(opengraph_data, indent=2, ensure_ascii=False), language='json')


def _analyze_schema_completeness(schema, schema_type):
    """Analyse la complétude d'un schema"""

    # Champs recommandés par type de schema
    recommended_fields = {
        'Organization': ['name', 'url', 'logo', 'address', 'contactPoint', 'sameAs'],
        'LocalBusiness': ['name', 'address', 'telephone', 'openingHours', 'geo', 'priceRange'],
        'Product': ['name', 'image', 'description', 'offers', 'brand', 'aggregateRating'],
        'Article': ['headline', 'author', 'datePublished', 'image', 'publisher'],
        'Person': ['name', 'jobTitle', 'worksFor', 'url', 'sameAs'],
        'Event': ['name', 'startDate', 'location', 'description', 'offers'],
        'Recipe': ['name', 'image', 'description', 'recipeIngredient', 'recipeInstructions', 'nutrition'],
        'WebPage': ['name', 'url', 'description', 'breadcrumb', 'mainEntity'],
        'WebSite': ['name', 'url', 'potentialAction', 'publisher'],
        'ImageObject': ['name', 'url', 'width', 'height', 'encodingFormat'],
        'BreadcrumbList': ['itemListElement'],
        'NewsArticle': ['headline', 'author', 'datePublished', 'image', 'publisher', 'articleSection'],
        'BlogPosting': ['headline', 'author', 'datePublished', 'image', 'publisher'],
    }

    if schema_type in recommended_fields:
        present_fields = []
        missing_fields = []

        for field in recommended_fields[schema_type]:
            if field in schema and schema[field] not in [None, '', [], {}]:
                present_fields.append(field)
            else:
                missing_fields.append(field)

        col1, col2 = st.columns(2)

        with col1:
            if present_fields:
                st.success(f"**✅ {get_text('present_fields', st.session_state.language)} :**")
                for field in present_fields:
                    st.write(f"• {field}")

        with col2:
            if missing_fields:
                st.warning(f"**⚠️ {get_text('missing_fields', st.session_state.language)} :**")
                for field in missing_fields:
                    st.write(f"• {field}")

        # Score global
        score = (len(present_fields) / len(recommended_fields[schema_type]) * 100) if recommended_fields[
            schema_type] else 0

        if score >= 80:
            st.success(format_text('excellent_schema_score', st.session_state.language, score=int(score)))
        elif score >= 60:
            st.warning(format_text('good_schema_score', st.session_state.language, score=int(score)))
        else:
            st.error(format_text('incomplete_schema_score', st.session_state.language, score=int(score)))
    else:
        st.info(get_text('no_specific_analysis', st.session_state.language))


def _provide_schema_optimization_tips(schema, schema_type):
    """Fournit des conseils d'optimisation pour un schema"""

    tips = {
        'Organization': [
            get_text('org_tip_logo_hires', st.session_state.language),
            get_text('org_tip_social_networks', st.session_state.language),
            get_text('org_tip_address_gps', st.session_state.language),
            get_text('org_tip_contact_details', st.session_state.language)
        ],
        'LocalBusiness': [
            get_text('local_tip_opening_hours', st.session_state.language),
            get_text('local_tip_quality_photos', st.session_state.language),
            get_text('local_tip_price_range', st.session_state.language),
            get_text('local_tip_business_type', st.session_state.language)
        ],
        'Product': [
            get_text('product_tip_hires_images', st.session_state.language),
            get_text('product_tip_aggregate_rating', st.session_state.language),
            get_text('product_tip_brand_model', st.session_state.language),
            get_text('product_tip_availability_price', st.session_state.language)
        ],
        'Article': [
            get_text('article_tip_large_image', st.session_state.language),
            get_text('article_tip_author_info', st.session_state.language),
            get_text('article_tip_publish_dates', st.session_state.language),
            get_text('article_tip_reading_time', st.session_state.language)
        ],
        'WebPage': [
            get_text('webpage_tip_meta_description', st.session_state.language),
            get_text('webpage_tip_breadcrumbs', st.session_state.language),
            get_text('webpage_tip_main_entity', st.session_state.language),
            get_text('webpage_tip_canonical_urls', st.session_state.language)
        ],
        'WebSite': [
            get_text('website_tip_internal_search', st.session_state.language),
            get_text('website_tip_social_links', st.session_state.language),
            get_text('website_tip_organization_owner', st.session_state.language),
            get_text('website_tip_site_description', st.session_state.language)
        ],
        'ImageObject': [
            get_text('image_tip_exact_dimensions', st.session_state.language),
            get_text('image_tip_encoding_format', st.session_state.language),
            get_text('image_tip_alt_description', st.session_state.language),
            get_text('image_tip_absolute_urls', st.session_state.language)
        ],
        'BreadcrumbList': [
            get_text('breadcrumb_tip_hierarchy', st.session_state.language),
            get_text('breadcrumb_tip_absolute_urls', st.session_state.language),
            get_text('breadcrumb_tip_current_page', st.session_state.language),
            get_text('breadcrumb_tip_logical_order', st.session_state.language)
        ]
    }

    if schema_type in tips:
        for tip in tips[schema_type]:
            st.write(f"💡 {tip}")
    else:
        st.write(f"💡 {get_text('tip_required_fields', st.session_state.language)}")
        st.write(f"💡 {get_text('tip_specific_data', st.session_state.language)}")
        st.write(f"💡 {get_text('tip_content_consistency', st.session_state.language)}")
        st.write(f"💡 {get_text('tip_google_test', st.session_state.language)}")

    # Conseils généraux
    st.write(f"**📌 {get_text('general_tips', st.session_state.language)} :**")
    st.write(f"• {get_text('tip_update_regularly', st.session_state.language)}")
    st.write(f"• {get_text('tip_avoid_duplicates', st.session_state.language)}")
    st.write(f"• {get_text('tip_use_absolute_urls', st.session_state.language)}")
    st.write(f"• {get_text('tip_test_google_tools', st.session_state.language)}")