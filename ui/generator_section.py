"""
Module pour la section de génération de schemas - Version optimisée sans doublons
"""
import streamlit as st
import json
from typing import List, Dict  # AJOUT DE L'IMPORT MANQUANT
from translations import get_text
from generators.schema_generator import SchemaGenerator
from generators.schema_deduplication_manager import SchemaDeduplicationManager, SchemaGeneratorOptimized
from ui.generator_forms import (
    render_business_info_form,
    render_address_form,
    render_contact_form,
    render_local_business_form,
    render_restaurant_form,
    render_product_form,
    render_article_form,
    render_faq_form,
    render_event_form,
    render_howto_form,
    render_person_form,
    render_breadcrumb_form,
    render_job_posting_form,
    render_social_networks_form,
    render_service_form,
    render_software_application_form,
    render_review_form,
    render_aggregate_rating_form
)
from ui.generator_utils import (
    display_schema_preview,
    generate_wordpress_code,
    generate_implementation_doc
)


def _ensure_reviewable_item_exists(self, schemas: List[Dict],
                                   client_info: Dict,
                                   additional_data: Dict) -> List[Dict]:
    """
    S'assure qu'un élément reviewable existe pour chaque Review
    """
    has_review = any(s.get('@type') == 'Review' for s in schemas)

    if has_review:
        # Chercher si on a un Service, Product, etc.
        reviewable_types = ['Service', 'Product', 'LocalBusiness', 'Restaurant', 'Organization']
        has_reviewable = any(
            s.get('@type') in reviewable_types or
            (isinstance(s.get('@type'), list) and any(t in reviewable_types for t in s['@type']))
            for s in schemas
        )

        if not has_reviewable:
            # Créer un Service automatiquement
            service_schema = {
                "@context": "https://schema.org",
                "@type": "Service",
                "name": additional_data.get('itemreviewed_name',
                                            additional_data.get('service_name',
                                                                'Agence marketing digital')),
                "description": additional_data.get('service_description',
                                                   client_info.get('description', '')),
                "provider": {
                    "@id": f"{client_info.get('website', '')}#organization"
                },
                "serviceType": additional_data.get('service_type', 'Marketing Agency'),
                "@id": f"{client_info.get('website', '')}#service"
            }
            schemas.append(service_schema)

    return schemas

def generator_section():
    """Section principale du générateur de schemas avec gestion des doublons"""

    # Initialiser les générateurs
    base_generator = SchemaGenerator()
    optimized_generator = SchemaGeneratorOptimized(base_generator)

    # Récupérer les schemas sélectionnés depuis my_page_section si disponibles
    if 'selected_schemas' in st.session_state and st.session_state.selected_schemas:
        pre_selected = st.session_state.selected_schemas
    else:
        pre_selected = []

    # Catégoriser les schemas
    business_schemas = ['Organization', 'LocalBusiness', 'Restaurant', 'Store']
    content_schemas = ['Article', 'NewsArticle', 'BlogPosting', 'Product',
                       'Review', 'AggregateRating', 'Recipe', 'VideoObject']
    navigation_schemas = ['WebSite', 'BreadcrumbList', 'FAQPage']
    event_schemas = ['Event', 'Course']
    person_schemas = ['Person', 'JobPosting']
    howto_schemas = ['HowTo']
    other_schemas = ['Service', 'SoftwareApplication']

    # Sélection des schemas à générer
    st.subheader(f"📋 {get_text('select_schemas', st.session_state.language)}")

    # Option pour activer la déduplication intelligente
    col_opt1, col_opt2 = st.columns(2)

    with col_opt1:
        include_optional = st.checkbox(
            get_text('include_optional_fields', st.session_state.language),
            value=True
        )

    with col_opt2:
        enable_deduplication = st.checkbox(
            "🔄 Optimisation automatique des schemas",
            value=True,
            help="Évite les doublons et intègre intelligemment les schemas liés (Review dans Service, AggregateRating dans Organization, etc.)"
        )

    selected_schemas = []

    # Afficher par catégories
    col1, col2 = st.columns(2)

    with col1:
        # Business Schemas
        with st.expander(get_text('business_schemas', st.session_state.language), expanded=True):
            for schema in business_schemas:
                if st.checkbox(schema, value=(schema in pre_selected), key=f"gen_{schema}"):
                    selected_schemas.append(schema)

        # Content Schemas avec indication de l'intégration possible
        with st.expander(get_text('content_schemas', st.session_state.language)):
            for schema in content_schemas:
                # Ajouter une indication si ce schema peut être intégré
                help_text = None
                if schema == 'Review' and enable_deduplication:
                    help_text = "Sera intégré dans Organization/Service si sélectionnés"
                elif schema == 'AggregateRating' and enable_deduplication:
                    help_text = "Sera intégré dans Organization/Service si sélectionnés"

                if st.checkbox(schema, value=(schema in pre_selected), key=f"gen_{schema}", help=help_text):
                    selected_schemas.append(schema)

    with col2:
        # Event & Navigation Schemas
        with st.expander(get_text('event_navigation_schemas', st.session_state.language)):
            for schema in navigation_schemas + event_schemas + person_schemas + howto_schemas:
                if st.checkbox(schema, value=(schema in pre_selected), key=f"gen_{schema}"):
                    selected_schemas.append(schema)

        # Other Schemas
        with st.expander(get_text('other_schemas', st.session_state.language)):
            for schema in other_schemas:
                if st.checkbox(schema, value=(schema in pre_selected), key=f"gen_{schema}"):
                    selected_schemas.append(schema)

    # Afficher l'analyse d'optimisation si activée
    if selected_schemas and enable_deduplication:
        dedup_manager = SchemaDeduplicationManager()
        optimization_result = dedup_manager.optimize_schema_selection(selected_schemas)

        if optimization_result['warnings']:
            with st.expander("🔍 Analyse d'optimisation", expanded=False):
                st.info("Voici comment vos schemas seront optimisés :")
                for warning in optimization_result['warnings']:
                    st.write(warning)

                # Afficher la structure finale prévue
                st.write("\n**Structure finale prévue :**")

                # Schemas principaux
                if optimization_result['primary_schemas']:
                    st.write("**Schemas principaux :**")
                    for schema in optimization_result['primary_schemas']:
                        if isinstance(schema, tuple):
                            st.write(f"  • {' + '.join(schema)} (fusionnés)")
                        else:
                            st.write(f"  • {schema}")
                            # Afficher les schemas intégrés
                            if schema in optimization_result['embedded_schemas']:
                                for embedded in optimization_result['embedded_schemas'][schema]:
                                    st.write(f"    ↳ {embedded} (intégré)")

                # Schemas liés
                if optimization_result['linked_schemas']:
                    st.write("**Schemas liés séparément :**")
                    for schema in optimization_result['linked_schemas']:
                        st.write(f"  • {schema}")

    if not selected_schemas:
        st.info("👆 Sélectionnez au moins un schema à générer")
        return

    st.divider()

    # Informations de base du client
    st.subheader(f"🏢 {get_text('client_info', st.session_state.language)}")

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            get_text('company_name', st.session_state.language),
            help=get_text('commercial_name_help', st.session_state.language)
        )
        legal_name = st.text_input(
            get_text('legal_name', st.session_state.language),
            value=company_name,
            help=get_text('full_legal_name_help', st.session_state.language)
        )

    with col2:
        website = st.text_input(
            get_text('website', st.session_state.language),
            placeholder="https://example.com",
            help=get_text('complete_url_help', st.session_state.language)
        )
        logo_url = st.text_input(
            get_text('logo_url', st.session_state.language),
            placeholder="https://example.com/logo.png",
            help=get_text('logo_help', st.session_state.language)
        )

    # Description
    description = st.text_area(
        get_text('description', st.session_state.language),
        help=get_text('detailed_description_help', st.session_state.language)
    )

    # Collecter les informations client
    client_info = {
        'company_name': company_name,
        'legal_name': legal_name,
        'website': website,
        'logo': logo_url,
        'description': description
    }

    # Données additionnelles selon les schemas sélectionnés
    additional_data = {}

    # Déterminer quels formulaires afficher selon l'optimisation
    show_review_form = True
    show_aggregate_form = True

    if enable_deduplication and selected_schemas:
        dedup_manager = SchemaDeduplicationManager()
        optimization = dedup_manager.optimize_schema_selection(selected_schemas)

        # Vérifier si Review sera intégré
        for embedded_list in optimization['embedded_schemas'].values():
            if 'Review' in embedded_list:
                show_review_form = False
            if 'AggregateRating' in embedded_list:
                show_aggregate_form = False

    # Business Info
    if any(schema in selected_schemas for schema in ['Organization', 'LocalBusiness', 'Restaurant', 'Store']):
        business_data = render_business_info_form(company_name, legal_name, logo_url)
        additional_data.update(business_data)

    # Address
    if any(schema in selected_schemas for schema in ['LocalBusiness', 'Restaurant', 'Store', 'Event']):
        address_data = render_address_form()
        additional_data.update(address_data)

    # Contact
    if any(schema in selected_schemas for schema in ['Organization', 'LocalBusiness', 'Restaurant', 'Store']):
        contact_data = render_contact_form()
        additional_data.update(contact_data)

    # Social Networks
    if any(schema in selected_schemas for schema in ['Organization', 'LocalBusiness', 'Person']):
        social_profiles = render_social_networks_form()
        if social_profiles:
            additional_data['social_media'] = social_profiles

    # LocalBusiness specifics
    if 'LocalBusiness' in selected_schemas:
        local_data = render_local_business_form()
        additional_data.update(local_data)

    # Restaurant specifics
    if 'Restaurant' in selected_schemas:
        restaurant_data = render_restaurant_form()
        additional_data.update(restaurant_data)

    # Product
    if 'Product' in selected_schemas:
        product_data = render_product_form()
        additional_data.update(product_data)

    # Article
    if any(schema in selected_schemas for schema in ['Article', 'NewsArticle', 'BlogPosting']):
        article_data = render_article_form()
        additional_data.update(article_data)

    # FAQ
    if 'FAQPage' in selected_schemas:
        faq_data = render_faq_form()
        additional_data.update(faq_data)

    # Event
    if 'Event' in selected_schemas:
        event_data = render_event_form()
        additional_data.update(event_data)

    # HowTo
    if 'HowTo' in selected_schemas:
        howto_data = render_howto_form()
        additional_data.update(howto_data)

    # Person
    if 'Person' in selected_schemas:
        person_data = render_person_form(company_name)
        additional_data.update(person_data)

    # BreadcrumbList
    if 'BreadcrumbList' in selected_schemas:
        breadcrumb_data = render_breadcrumb_form(website)
        additional_data.update(breadcrumb_data)

    # JobPosting
    if 'JobPosting' in selected_schemas:
        temp_generator = SchemaGenerator()
        job_data = render_job_posting_form(temp_generator)
        additional_data.update(job_data)

    # Service
    if 'Service' in selected_schemas:
        # Vérifier si Organization/LocalBusiness est aussi sélectionné
        has_org_or_local = ('Organization' in selected_schemas or 'LocalBusiness' in selected_schemas)

        # Si Organization/LocalBusiness est présent ET que l'optimisation est activée
        if has_org_or_local and enable_deduplication:
            st.info("ℹ️ Les avis et évaluations du Service seront centralisés dans Organization/LocalBusiness")

        # Appeler render_service_form normalement (sans paramètre inexistant)
        service_data = render_service_form(company_name)
        additional_data.update(service_data)

    # SoftwareApplication
    if 'SoftwareApplication' in selected_schemas:
        software_data = render_software_application_form(company_name, website)
        additional_data.update(software_data)

    # Review - toujours afficher le formulaire mais avec indication
    if 'Review' in selected_schemas:
        if not show_review_form and enable_deduplication:
            st.info(
                "📝 Les données Review seront intégrées automatiquement dans le schema parent (Organization/Service)")
        elif not enable_deduplication:
            st.info(
                "💡 Le schema Review peut être intégré automatiquement dans Organization/Service. Activez l'optimisation pour éviter les doublons.")

        # Toujours afficher le formulaire pour collecter les données
        review_data = render_review_form()
        additional_data.update(review_data)

    # AggregateRating - toujours afficher le formulaire mais avec indication
    if 'AggregateRating' in selected_schemas:
        if not show_aggregate_form and enable_deduplication:
            st.info(
                "⭐ Les données AggregateRating seront intégrées automatiquement dans le schema parent (Organization/Service)")
        elif not enable_deduplication:
            st.info(
                "💡 Le schema AggregateRating peut être intégré automatiquement dans Organization/Service. Activez l'optimisation pour éviter les doublons.")

        # Toujours afficher le formulaire pour collecter les données
        aggregate_data = render_aggregate_rating_form()
        additional_data.update(aggregate_data)

    st.divider()

    # Bouton de génération
    if st.button(
            f"🚀 {get_text('generate_schemas', st.session_state.language)}",
            type="primary",
            use_container_width=True
    ):
        with st.spinner(get_text('generating_schemas', st.session_state.language)):
            try:
                # Debug optionnel - ACTIVÉ pour diagnostic
                with st.expander("🔍 Debug - Données envoyées au générateur", expanded=True):
                    st.write("**Client Info:**")
                    st.json(client_info)
                    st.write("**Additional Data AVANT nettoyage:**")
                    st.json(additional_data)

                    # NETTOYER les données Service si nécessaire
                    if enable_deduplication and 'Service' in selected_schemas:
                        has_org_or_local = ('Organization' in selected_schemas or 'LocalBusiness' in selected_schemas)
                        if has_org_or_local:
                            st.warning("🧹 Nettoyage des données Service pour éviter la duplication")

                            # Supprimer les données de témoignages du Service
                            keys_to_remove = []
                            for key in additional_data.keys():
                                if 'testimonial' in key or 'service_review' in key or 'service_rating' in key:
                                    keys_to_remove.append(key)

                            for key in keys_to_remove:
                                del additional_data[key]
                                st.write(f"  ❌ Supprimé: {key}")

                    st.write("**Additional Data APRÈS nettoyage:**")
                    st.json(additional_data)

                    # Vérifier spécifiquement les données AggregateRating
                    if 'AggregateRating' in selected_schemas:
                        st.write("**🔍 Données AggregateRating détectées:**")
                        aggregate_keys = ['rating_value', 'review_count', 'target_name', 'target_type']
                        for key in aggregate_keys:
                            if key in additional_data:
                                st.write(f"  • {key}: {additional_data[key]}")

                        # Vérifier si les données sont présentes
                        if not any(key in additional_data for key in aggregate_keys):
                            st.warning("⚠️ Aucune donnée AggregateRating trouvée dans additional_data !")

                # S'assurer que les données essentielles sont présentes
                if 'logo' not in additional_data and logo_url:
                    additional_data['logo'] = logo_url

                # Générer avec ou sans optimisation
                if enable_deduplication:
                    # Utiliser le générateur optimisé qui fait TOUT
                    generated, optimization_messages = optimized_generator.generate_optimized_schemas(
                        selected_schemas,
                        client_info,
                        additional_data,
                        include_optional
                    )

                    # Afficher les messages d'optimisation
                    if optimization_messages:
                        with st.expander("✅ Optimisations appliquées", expanded=True):
                            for msg in optimization_messages:
                                st.write(msg)
                else:
                    # Utiliser le générateur standard
                    generated = base_generator.generate_multiple_schemas(
                        selected_schemas,
                        client_info,
                        additional_data,
                        include_optional
                    )

                st.session_state.generated_schemas = generated

                # Message de succès
                if enable_deduplication:
                    # Compter le nombre réel de schemas
                    schema_count = 0
                    for item in generated:
                        if '@graph' in item:
                            schema_count += len(item['@graph'])
                        else:
                            schema_count += 1

                    st.success(
                        f"✨ Schemas générés et optimisés ! "
                        f"({schema_count} schemas dans {len(generated)} structure{'s' if len(generated) > 1 else ''})"
                    )
                else:
                    st.success(
                        get_text('schemas_generated_success', st.session_state.language).format(
                            count=len(generated)
                        )
                    )

                # Nettoyer les schemas sélectionnés depuis my_page
                if 'selected_schemas' in st.session_state:
                    del st.session_state.selected_schemas

            except Exception as e:
                st.error(f"Erreur lors de la génération : {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    # Afficher les schemas générés
    if st.session_state.generated_schemas:
        st.divider()
        st.subheader(f"✨ {get_text('generated_schemas', st.session_state.language)}")

        # Options d'affichage
        col1, col2, col3 = st.columns(3)

        with col1:
            show_preview = st.checkbox(
                get_text('visual_preview', st.session_state.language),
                value=True
            )

        with col2:
            show_code = st.checkbox(
                get_text('show_code', st.session_state.language),
                value=False
            )

        with col3:
            minify = st.checkbox(
                get_text('minify_code', st.session_state.language),
                value=False
            )

        # Afficher chaque schema avec indication de la structure
        for i, schema_data in enumerate(st.session_state.generated_schemas):
            # Si c'est un @graph, traiter chaque schema individuellement
            if '@graph' in schema_data:
                st.write(f"**📊 Structure @graph optimisée - {len(schema_data['@graph'])} schemas liés**")

                # Afficher un résumé de la structure
                with st.expander("🔗 Vue d'ensemble de la structure", expanded=False):
                    st.write("Cette structure @graph contient les schemas suivants, liés entre eux :")
                    for j, schema in enumerate(schema_data['@graph']):
                        schema_type = schema.get('@type', 'Unknown')
                        if isinstance(schema_type, list):
                            schema_type = ' + '.join(schema_type)
                        schema_id = schema.get('@id', '')
                        st.write(f"{j + 1}. **{schema_type}** - `{schema_id}`")

                        # Afficher les liens
                        if 'provider' in schema and isinstance(schema['provider'], dict):
                            st.write(f"   ↳ Fournisseur : {schema['provider'].get('@id', '')}")
                        if 'itemReviewed' in schema and isinstance(schema['itemReviewed'], dict):
                            st.write(f"   ↳ Élément évalué : {schema['itemReviewed'].get('@id', '')}")
                        if 'aggregateRating' in schema:
                            st.write(f"   ↳ Note moyenne intégrée")
                        if 'review' in schema:
                            review_count = len(schema['review']) if isinstance(schema['review'], list) else 1
                            st.write(f"   ↳ {review_count} avis intégré{'s' if review_count > 1 else ''}")

                # Afficher chaque schema du graph
                for j, schema in enumerate(schema_data['@graph']):
                    schema_type = schema.get('@type', 'Unknown')
                    if isinstance(schema_type, list):
                        schema_type = ' + '.join(schema_type)

                    with st.expander(f"{schema_type} #{j + 1}", expanded=(j == 0)):
                        if show_preview:
                            display_schema_preview(schema)

                        if show_code:
                            if minify:
                                code = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
                            else:
                                code = json.dumps(schema, indent=2, ensure_ascii=False)
                            st.code(code, language='json')
            else:
                # Schema individuel
                schema_type = schema_data.get('@type', 'Unknown')
                if isinstance(schema_type, list):
                    schema_type = ' + '.join(schema_type)

                with st.expander(f"{schema_type} #{i + 1}", expanded=(i == 0)):
                    if show_preview:
                        display_schema_preview(schema_data)

                    if show_code:
                        if minify:
                            code = json.dumps(schema_data, ensure_ascii=False, separators=(',', ':'))
                        else:
                            code = json.dumps(schema_data, indent=2, ensure_ascii=False)
                        st.code(code, language='json')

        # Options d'export et d'intégration
        render_export_options(base_generator, selected_schemas)


def render_export_options(generator, selected_schemas):
    """Affiche les options d'export et d'intégration"""
    st.divider()
    st.subheader("📥 Export et intégration")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # JSON unique ou multiple
        if len(st.session_state.generated_schemas) == 1:
            download_data = st.session_state.generated_schemas[0]
            filename = "schema.json"
        else:
            download_data = st.session_state.generated_schemas
            filename = "schemas.json"

        st.download_button(
            label="📄 Télécharger JSON",
            data=json.dumps(download_data, indent=2, ensure_ascii=False),
            file_name=filename,
            mime="application/json",
            use_container_width=True
        )

    with col2:
        # HTML avec script tags
        html_code = generator.format_for_insertion(st.session_state.generated_schemas)
        st.download_button(
            label="🌐 Télécharger HTML",
            data=html_code,
            file_name="schemas.html",
            mime="text/html",
            use_container_width=True
        )

    with col3:
        # WordPress/CMS
        wp_code = generate_wordpress_code(st.session_state.generated_schemas)
        st.download_button(
            label="📝 Code WordPress",
            data=wp_code,
            file_name="schemas-wordpress.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col4:
        # Documentation
        doc = generate_implementation_doc(
            selected_schemas,
            st.session_state.generated_schemas
        )
        st.download_button(
            label="📚 Documentation",
            data=doc,
            file_name="schemas-documentation.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Instructions d'intégration
    with st.expander("📖 Instructions d'intégration"):
        tab1, tab2, tab3, tab4 = st.tabs(["HTML", "WordPress", "Tag Manager", "Validation"])

        with tab1:
            st.markdown("""
            ### Intégration HTML

            1. **Copiez** le code HTML généré
            2. **Collez-le** dans la section `<head>` ou `<body>` de votre page
            3. **Assurez-vous** qu'il n'y a pas de conflits avec d'autres scripts JSON-LD
            4. **Testez** avec l'outil de test des résultats enrichis de Google

            ```html
            <!-- Exemple de placement -->
            <head>
                <!-- Autres balises meta -->

                <!-- Vos schemas JSON-LD -->
                <script type="application/ld+json">
                { ... }
                </script>
            </head>
            ```
            """)

        with tab2:
            st.markdown("""
            ### Intégration WordPress

            **Option 1 : Functions.php**
            1. Accédez à `Apparence > Éditeur de thème`
            2. Ouvrez `functions.php`
            3. Collez le code PHP fourni
            4. Enregistrez les modifications

            **Option 2 : Plugin personnalisé**
            1. Créez un nouveau plugin
            2. Ajoutez le code dans le fichier principal
            3. Activez le plugin

            **Option 3 : Plugin SEO**
            - Yoast SEO
            - RankMath
            - All in One SEO
            """)

        with tab3:
            st.markdown("""
            ### Google Tag Manager

            1. **Créez une nouvelle balise**
               - Type : HTML personnalisé
               - Déclencheur : Toutes les pages (ou pages spécifiques)

            2. **Collez le code JSON-LD**
               ```html
               <script type="application/ld+json">
               { ... }
               </script>
               ```

            3. **Testez en mode aperçu**
            4. **Publiez le conteneur**
            """)

        with tab4:
            st.markdown("""
            ### Validation et test

            **Outils de validation recommandés :**

            1. **[Google Rich Results Test](https://search.google.com/test/rich-results)**
               - Test officiel de Google
               - Montre l'aperçu dans les SERP

            2. **[Schema.org Validator](https://validator.schema.org/)**
               - Validation complète
               - Détection d'erreurs

            3. **[Google Search Console](https://search.google.com/search-console)**
               - Monitoring en temps réel
               - Rapports d'erreurs

            **Points à vérifier :**
            - ✅ Syntaxe JSON valide
            - ✅ Propriétés requises présentes
            - ✅ Format des dates (ISO 8601)
            - ✅ URLs absolues
            - ✅ Pas de doublons
            """)

    # Conseils d'optimisation
    with st.expander("💡 Conseils d'optimisation"):
        st.markdown("""
        ### Bonnes pratiques pour les schemas

        **1. Évitez les doublons**
        - Un seul schema par type par page
        - Utilisez @graph pour lier plusieurs schemas

        **2. Complétez les champs importants**
        - Plus d'informations = meilleure visibilité
        - Privilégiez les champs reconnus par Google

        **3. Maintenez à jour**
        - Prix, disponibilité, horaires
        - Avis et notations
        - Événements et dates

        **4. Cohérence des données**
        - Les informations doivent correspondre au contenu visible
        - Utilisez les mêmes données partout

        **5. Images optimisées**
        - Haute résolution (min 1200x1200 pour les produits)
        - Format JPG ou PNG
        - URLs absolues et accessibles
        """)