"""
Section de génération de schemas avec fonctionnalité de test intégrée
Version corrigée sans erreurs de syntaxe
"""

import json
import streamlit as st
from datetime import datetime, timedelta
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


class TestDataGenerator:
    """Classe pour générer des données de test pour tous les types de schemas"""

    @staticmethod
    def get_test_data_for_schema(schema_type):
        """Retourne des données de test pour un type de schema donné"""

        test_data_map = {
            'Organization': TestDataGenerator._get_organization_test_data(),
            'LocalBusiness': TestDataGenerator._get_local_business_test_data(),
            'Restaurant': TestDataGenerator._get_restaurant_test_data(),
            'Store': TestDataGenerator._get_store_test_data(),
            'Product': TestDataGenerator._get_product_test_data(),
            'Article': TestDataGenerator._get_article_test_data(),
            'NewsArticle': TestDataGenerator._get_news_article_test_data(),
            'BlogPosting': TestDataGenerator._get_blog_posting_test_data(),
            'Review': TestDataGenerator._get_review_test_data(),
            'AggregateRating': TestDataGenerator._get_aggregate_rating_test_data(),
            'Recipe': TestDataGenerator._get_recipe_test_data(),
            'VideoObject': TestDataGenerator._get_video_object_test_data(),
            'Event': TestDataGenerator._get_event_test_data(),
            'Course': TestDataGenerator._get_course_test_data(),
            'WebSite': TestDataGenerator._get_website_test_data(),
            'BreadcrumbList': TestDataGenerator._get_breadcrumb_test_data(),
            'FAQPage': TestDataGenerator._get_faq_test_data(),
            'Person': TestDataGenerator._get_person_test_data(),
            'JobPosting': TestDataGenerator._get_job_posting_test_data(),
            'Service': TestDataGenerator._get_service_test_data(),
            'SoftwareApplication': TestDataGenerator._get_software_application_test_data(),
            'HowTo': TestDataGenerator._get_howto_test_data()
        }

        return test_data_map.get(schema_type, {})

    @staticmethod
    def _get_organization_test_data():
        return {
            # Informations de base
            'company_name': 'Agence WebTech Solutions',
            'description': 'Agence spécialisée dans le développement web et le marketing digital. Nous accompagnons les entreprises dans leur transformation numérique.',
            'website': 'https://webtech-solutions.com',
            'logo': 'https://webtech-solutions.com/logo.png',

            # Informations business
            'taxID': '12345678901234',
            'vatID': 'FR12345678901',
            'naics': '541511',
            'employee_count': 25,
            'slogan': 'Votre partenaire digital de confiance',

            # Contact principal
            'telephone': '+33 1 23 45 67 89',
            'email': 'contact@webtech-solutions.com',
            'fax': '+33 1 23 45 67 90',

            # Adresse
            'street_address': '123 Avenue des Champs-Élysées',
            'city': 'Paris',
            'postal_code': '75008',
            'region': 'Île-de-France',
            'country': 'FR',

            # Réseaux sociaux
            'facebook': 'https://facebook.com/webtechsolutions',
            'linkedin': 'https://linkedin.com/company/webtech-solutions',
            'twitter': 'https://twitter.com/webtechsolutions',
            'instagram': 'https://instagram.com/webtechsolutions',
            'youtube': 'https://youtube.com/webtechsolutions',
            'tiktok': 'https://tiktok.com/@webtechsolutions',
            'pinterest': 'https://pinterest.com/webtechsolutions'
        }

    @staticmethod
    def _get_local_business_test_data():
        base_data = TestDataGenerator._get_organization_test_data()
        base_data.update({
            # Informations LocalBusiness spécifiques
            'price_range': '€€',
            'opening_hours': 'Mo-Fr 09:00-18:00',
            'payment_accepted': 'Cash, Credit Card, Debit Card, PayPal',
            'currencies_accepted': 'EUR, USD',
            'latitude': '48.8738',
            'longitude': '2.2950'
        })
        return base_data

    @staticmethod
    def _get_restaurant_test_data():
        base_data = TestDataGenerator._get_local_business_test_data()
        base_data.update({
            'company_name': 'Restaurant Le Petit Gourmet',
            'description': 'Restaurant gastronomique français proposant une cuisine traditionnelle.',
            'cuisines': ['Française', 'Européenne'],
            'menu_url': 'https://lepetitgourmet.com/menu',
            'accepts_reservations': True
        })
        return base_data

    @staticmethod
    def _get_store_test_data():
        base_data = TestDataGenerator._get_local_business_test_data()
        base_data.update({
            'company_name': 'Boutique Mode & Style',
            'description': 'Boutique de mode proposant des vêtements tendance.',
        })
        return base_data

    @staticmethod
    def _get_product_test_data():
        return {
            'product_name': 'MacBook Pro 16 pouces',
            'product_description': 'Ordinateur portable professionnel Apple avec processeur M3 Pro, 18 Go de RAM et 512 Go de stockage SSD.',
            'brand_name': 'Apple',
            'sku': 'MBP16-M3-512',
            'gtin13': '194252056813',
            'mpn': 'MK1E3FN/A',
            'price': '2899',
            'currency': 'EUR',
            'availability': 'https://schema.org/InStock',
            'price_valid_until': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'color': 'Gris sidéral',
            'size': '16 pouces',
            'material': 'Aluminium',
            'weight_value': '2.1',
            'weight_unit': 'KGM',
            # Images produit
            'product_img_0': 'https://example.com/macbook-pro-16.jpg',
            'product_img_1': 'https://example.com/macbook-pro-16-2.jpg',
            'product_img_2': 'https://example.com/macbook-pro-16-3.jpg'
        }

    @staticmethod
    def _get_article_test_data():
        return {
            'headline': 'Comment optimiser le SEO de votre site web en 2024',
            'article_description': 'Guide complet pour améliorer le référencement naturel de votre site web avec les dernières bonnes pratiques SEO.',
            'author_name': 'Sophie Martin',
            'author_url': 'https://webtech-solutions.com/author/sophie-martin',
            'publisher_name': 'Blog WebTech',
            'publisher_logo': 'https://webtech-solutions.com/logo.png',
            'article_section': 'SEO',
            'keywords': 'SEO, référencement, optimisation, Google',
            'article_body': 'Dans cet article complet, nous explorerons les meilleures pratiques SEO pour 2024, en couvrant l\'optimisation technique, le contenu de qualité, et les stratégies de netlinking...',
            # Images multiples formats
            'img_16_9': 'https://example.com/seo-guide-2024-16x9.jpg',
            'img_4_3': 'https://example.com/seo-guide-2024-4x3.jpg',
            'img_1_1': 'https://example.com/seo-guide-2024-1x1.jpg'
        }

    @staticmethod
    def _get_news_article_test_data():
        base_data = TestDataGenerator._get_article_test_data()
        base_data.update({
            'headline': 'Google met à jour son algorithme de recherche',
            'article_section': 'Technologie'
        })
        return base_data

    @staticmethod
    def _get_blog_posting_test_data():
        base_data = TestDataGenerator._get_article_test_data()
        base_data.update({
            'headline': '10 astuces pour améliorer la vitesse de votre site web'
        })
        return base_data

    @staticmethod
    def _get_review_test_data():
        return {
            'review_type': 'Service',
            'itemreviewed_name': 'Service de développement web',
            'review_rating': '5',
            'review_author': 'Marc Dubois',
            'review_text': 'Excellent service ! Je recommande vivement.',
            'review_summary': 'Service exceptionnel',
            'would_recommend': True
        }

    @staticmethod
    def _get_aggregate_rating_test_data():
        return {
            'target_type': 'Service',
            'target_name': 'Service de développement web',
            'rating_value': '4.8',
            'best_rating': '5',
            'worst_rating': '1',
            'review_count': '127'
        }

    @staticmethod
    def _get_recipe_test_data():
        return {
            'recipe_name': 'Tarte aux pommes traditionnelle',
            'recipe_description': 'Une délicieuse tarte aux pommes faite maison.',
            'prep_time': 'PT30M',
            'cook_time': 'PT45M',
            'recipe_yield': '8',
            'recipe_category': 'Dessert',
            'recipe_cuisine': 'Française',
            'recipe_ingredients': 'Pâte brisée\n6 pommes\n100g de sucre\n50g de beurre\n1 œuf\nCannelle',
            'recipe_instructions': '1. Préchauffer le four à 180°C\n2. Étaler la pâte dans un moule\n3. Éplucher et couper les pommes\n4. Disposer les pommes sur la pâte\n5. Saupoudrer de sucre et cannelle\n6. Cuire 45 minutes'
        }

    @staticmethod
    def _get_video_object_test_data():
        return {
            'video_name': 'Tutoriel : Comment créer un site web professionnel',
            'video_description': 'Apprenez à créer un site web professionnel étape par étape.',
            'video_duration': 'PT15M30S',
            'video_thumbnail_url': 'https://example.com/video-thumbnail.jpg',
            'content_url': 'https://example.com/video.mp4',
            'embed_url': 'https://example.com/embed/video123'
        }

    @staticmethod
    def _get_event_test_data():
        return {
            'event_name': 'Conférence Web Marketing 2024',
            'event_description': 'Conférence dédiée aux dernières tendances du marketing digital.',
            'venue_name': 'Palais des Congrès',
            'venue_address': '2 Place de la Porte Maillot, 75017 Paris',
            'organizer_name': 'WebTech Events',
            'ticket_price': '150',
            'ticket_currency': 'EUR'
        }

    @staticmethod
    def _get_course_test_data():
        return {
            'course_name': 'Formation SEO Avancé',
            'course_description': 'Formation complète pour maîtriser les techniques avancées de référencement.',
            'provider_name': 'WebTech Academy'
        }

    @staticmethod
    def _get_website_test_data():
        return {
            'site_name': 'WebTech Solutions',
            'alternate_name': 'WTS',
            'site_description': 'Agence web spécialisée dans le développement et le marketing digital',
            'potential_action': True,
            'search_target': 'https://webtech-solutions.com/search?q={search_term_string}',
            'search_term': 'search_term_string'
        }

    @staticmethod
    def _get_breadcrumb_test_data():
        return {
            # Breadcrumb avec format individuel
            'crumb_name_0': 'Accueil',
            'crumb_url_0': 'https://webtech-solutions.com',
            'crumb_name_1': 'Services',
            'crumb_url_1': 'https://webtech-solutions.com/services',
            'crumb_name_2': 'Développement Web',
            'crumb_url_2': 'https://webtech-solutions.com/services/developpement-web',
            'crumb_name_3': 'E-commerce',
            'crumb_url_3': 'https://webtech-solutions.com/services/developpement-web/e-commerce'
        }

    @staticmethod
    def _get_faq_test_data():
        return {
            # Questions FAQ avec format correct
            'question_0': 'Combien coûte un site web ?',
            'answer_0': 'Le prix varie selon la complexité et les fonctionnalités souhaitées. Pour un site vitrine, comptez entre 2000€ et 5000€. Pour un e-commerce, entre 5000€ et 15000€. Contactez-nous pour un devis personnalisé.',

            'question_1': 'Combien de temps faut-il pour créer un site web ?',
            'answer_1': 'En moyenne, il faut 4 à 8 semaines selon la complexité du projet. Un site vitrine prend 3-4 semaines, tandis qu\'un e-commerce peut nécessiter 6-10 semaines.',

            'question_2': 'Proposez-vous la maintenance ?',
            'answer_2': 'Oui, nous proposons des contrats de maintenance mensuels pour assurer la sécurité, les mises à jour et les sauvegardes de votre site web.',

            'question_3': 'Travaillez-vous avec des CMS spécifiques ?',
            'answer_3': 'Nous travaillons principalement avec WordPress, Shopify pour l\'e-commerce, et développons aussi des solutions sur mesure selon vos besoins.'
        }

    @staticmethod
    def _get_person_test_data():
        return {
            'given_name': 'Sophie',
            'family_name': 'Martin',
            'job_title': 'Directrice Marketing Digital',
            'person_description': 'Expert en marketing digital avec plus de 10 ans d\'expérience.',
            'works_for': 'Agence WebTech Solutions'
        }

    @staticmethod
    def _get_job_posting_test_data():
        return {
            'job_title': 'Développeur Full Stack Senior',
            'job_description': 'Nous recherchons un développeur full stack expérimenté.',
            'employment_type': 'FULL_TIME',
            'job_city': 'Paris',
            'job_country': 'FR',
            'salary_min': '45000',
            'salary_max': '65000',
            'salary_currency': 'EUR'
        }

    @staticmethod
    def _get_service_test_data():
        return {
            'service_name': 'Développement d\'applications web',
            'service_description': 'Conception et développement d\'applications web sur mesure.',
            'service_type': 'Web Development',
            'area_served': ['France', 'Europe'],
            'price_range': '€€€'
        }

    @staticmethod
    def _get_software_application_test_data():
        return {
            'app_name': 'TaskManager Pro',
            'app_category': 'ProductivityApplication',
            'app_subcategory': 'Task Management',
            'operating_systems': ['Windows', 'macOS', 'Web'],
            'software_version': '2.1.0',
            'pricing_model': 'Freemium'
        }

    @staticmethod
    def _get_howto_test_data():
        return {
            'howto_name': 'Comment optimiser la vitesse de votre site web',
            'total_time': 'PT2H',
            'estimated_cost': '0',
            'tools': 'Google PageSpeed Insights\nGTmetrix\nCompresseur d\'images\nÉditeur de code',
            'supplies': 'Accès FTP au site\nSauvegarde du site\nCompte Google Analytics',
            # Étapes individuelles
            'step_name_0': 'Analyser les performances actuelles',
            'step_text_0': 'Utilisez Google PageSpeed Insights pour analyser votre site et identifier les problèmes de performance.',
            'step_img_0': 'https://example.com/step1-pagespeed.jpg',

            'step_name_1': 'Optimiser les images',
            'step_text_1': 'Compressez toutes les images de votre site et convertissez-les au format WebP pour réduire leur taille.',
            'step_img_1': 'https://example.com/step2-images.jpg',

            'step_name_2': 'Minifier CSS et JavaScript',
            'step_text_2': 'Supprimez les espaces et commentaires inutiles de vos fichiers CSS et JS pour réduire leur taille.',
            'step_img_2': 'https://example.com/step3-minify.jpg'
        }

    @staticmethod
    def apply_test_data_to_session_state(selected_schemas):
        """Applique les données de test à la session state pour les schémas sélectionnés"""

        # Données de base communes
        base_test_data = TestDataGenerator._get_organization_test_data()

        # Parcourir chaque schéma sélectionné et ajouter ses données de test
        for schema_type in selected_schemas:
            schema_test_data = TestDataGenerator.get_test_data_for_schema(schema_type)

            # Mettre à jour la session state avec les données de test
            for key, value in schema_test_data.items():
                st.session_state[key] = value

        # S'assurer que les données de base sont aussi dans la session state
        for key, value in base_test_data.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def populate_form_fields_with_test_data(selected_schemas):
        """Remplit les champs de formulaire avec des données de test"""
        TestDataGenerator.apply_test_data_to_session_state(selected_schemas)
        return len(selected_schemas)


def render_optimization_analysis(selected_schemas, enable_deduplication):
    """Affiche l'analyse d'optimisation pour les schemas sélectionnés"""
    if not enable_deduplication or len(selected_schemas) < 2:
        return

    st.info("🔄 **Analyse d'optimisation activée**")

    # Analyser les optimisations possibles
    optimizations = []

    # Vérifier si Review/AggregateRating peuvent être intégrés
    if 'Review' in selected_schemas and any(
            s in selected_schemas for s in ['Organization', 'LocalBusiness', 'Service']):
        optimizations.append("✅ Review sera intégré dans Organization/LocalBusiness/Service")

    if 'AggregateRating' in selected_schemas and any(
            s in selected_schemas for s in ['Organization', 'LocalBusiness', 'Service']):
        optimizations.append("✅ AggregateRating sera intégré dans Organization/LocalBusiness/Service")

    # Vérifier les structures @graph
    if len(selected_schemas) > 3:
        optimizations.append("🔗 Structure @graph optimisée sera utilisée pour lier les schemas")

    if optimizations:
        st.success("**Optimisations détectées :**")
        for opt in optimizations:
            st.write(f"- {opt}")


def render_recipe_form():
    """Formulaire pour Recipe"""
    additional_data = {}

    with st.expander("🍳 Informations recette"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['recipe_name'] = st.text_input(
                "Nom de la recette",
                value=st.session_state.get('recipe_name', '')
            )
            additional_data['recipe_description'] = st.text_area(
                "Description",
                value=st.session_state.get('recipe_description', ''),
                height=100
            )
            additional_data['prep_time'] = st.text_input(
                "Temps de préparation",
                value=st.session_state.get('prep_time', ''),
                placeholder="PT30M"
            )
            additional_data['cook_time'] = st.text_input(
                "Temps de cuisson",
                value=st.session_state.get('cook_time', ''),
                placeholder="PT45M"
            )

        with col2:
            additional_data['recipe_yield'] = st.text_input(
                "Portions",
                value=st.session_state.get('recipe_yield', '')
            )
            additional_data['recipe_category'] = st.text_input(
                "Catégorie",
                value=st.session_state.get('recipe_category', ''),
                placeholder="Dessert, Plat principal..."
            )
            additional_data['recipe_cuisine'] = st.text_input(
                "Cuisine",
                value=st.session_state.get('recipe_cuisine', ''),
                placeholder="Française, Italienne..."
            )

        # Ingrédients
        additional_data['recipe_ingredients'] = st.text_area(
            "Ingrédients (un par ligne)",
            value=st.session_state.get('recipe_ingredients', ''),
            height=100
        )

        # Instructions
        additional_data['recipe_instructions'] = st.text_area(
            "Instructions (une par ligne)",
            value=st.session_state.get('recipe_instructions', ''),
            height=150
        )

    return additional_data


def render_video_object_form():
    """Formulaire pour VideoObject"""
    additional_data = {}

    with st.expander("🎥 Informations vidéo"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['video_name'] = st.text_input(
                "Nom de la vidéo",
                value=st.session_state.get('video_name', '')
            )
            additional_data['video_description'] = st.text_area(
                "Description",
                value=st.session_state.get('video_description', ''),
                height=100
            )
            additional_data['video_duration'] = st.text_input(
                "Durée",
                value=st.session_state.get('video_duration', ''),
                placeholder="PT15M30S"
            )

        with col2:
            additional_data['video_thumbnail_url'] = st.text_input(
                "URL miniature",
                value=st.session_state.get('video_thumbnail_url', '')
            )
            additional_data['content_url'] = st.text_input(
                "URL vidéo",
                value=st.session_state.get('content_url', '')
            )
            additional_data['embed_url'] = st.text_input(
                "URL d'intégration",
                value=st.session_state.get('embed_url', '')
            )

    return additional_data


def render_website_form(company_name, website):
    """Formulaire pour WebSite"""
    additional_data = {}

    with st.expander("🌐 Informations du site web"):
        additional_data['site_name'] = st.text_input(
            "Nom du site",
            value=st.session_state.get('site_name', company_name)
        )
        additional_data['alternate_name'] = st.text_input(
            "Nom alternatif",
            value=st.session_state.get('alternate_name', '')
        )
        additional_data['site_description'] = st.text_area(
            "Description du site",
            value=st.session_state.get('site_description', ''),
            height=100
        )

        # Fonction de recherche
        additional_data['potential_action'] = st.checkbox(
            "Inclure la fonction de recherche",
            value=st.session_state.get('potential_action', False)
        )

        if additional_data.get('potential_action'):
            additional_data['search_target'] = st.text_input(
                "URL de recherche",
                value=st.session_state.get('search_target', f"{website}/search?q={{search_term_string}}")
            )
            additional_data['search_term'] = st.text_input(
                "Paramètre de recherche",
                value=st.session_state.get('search_term', 'search_term_string')
            )

    return additional_data


def generate_simple_wordpress_code(schemas):
    """Génère un code WordPress simple"""
    code = """<?php
// Ajouter ce code dans votre functions.php

function add_custom_schemas() {
    if (is_singular()) {
        ?>
        <script type="application/ld+json">
"""

    for schema in schemas:
        code += json.dumps(schema, indent=2, ensure_ascii=False)
        code += "\n"

    code += """        </script>
        <?php
    }
}
add_action('wp_head', 'add_custom_schemas');
?>"""

    return code


def generate_simple_implementation_doc(selected_schemas, generated_schemas):
    """Génère une documentation d'implémentation simple"""
    doc = f"""# Documentation des Schemas Générés

## Schemas sélectionnés
{', '.join(selected_schemas)}

## Nombre de schemas générés
{len(generated_schemas)}

## Instructions d'intégration

### HTML
1. Copiez le code HTML généré
2. Collez-le dans la section <head> de votre page
3. Testez avec Google Rich Results Test

### WordPress
1. Ajoutez le code PHP dans functions.php
2. Ou utilisez un plugin SEO (Yoast, RankMath)

### Validation
- Google Rich Results Test: https://search.google.com/test/rich-results
- Schema.org Validator: https://validator.schema.org/

## Schemas générés le
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return doc


def generator_section():
    """Section principale du générateur de schemas avec gestion des doublons et test"""

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
        render_optimization_analysis(selected_schemas, enable_deduplication)

    # ===== NOUVELLE FONCTIONNALITÉ : BOUTON DE TEST =====
    if selected_schemas:
        st.divider()
        st.subheader("🧪 Mode Test & Debug")

        col_test1, col_test2 = st.columns(2)

        with col_test1:
            if st.button(
                    "🎯 Remplir avec données de test",
                    type="secondary",
                    help="Remplit automatiquement tous les formulaires avec des données génériques pour tester la génération",
                    use_container_width=True
            ):
                # Appliquer les données de test
                num_schemas = TestDataGenerator.populate_form_fields_with_test_data(selected_schemas)
                st.success(f"✅ Données de test appliquées pour {num_schemas} schemas sélectionnés !")
                st.info("💡 Vous pouvez maintenant cliquer sur 'Générer les schemas' pour tester.")
                st.rerun()

        with col_test2:
            if st.button(
                    "🗑️ Nettoyer les données de test",
                    help="Efface toutes les données de test des formulaires",
                    use_container_width=True
            ):
                # Nettoyer les données de test
                keys_to_remove = [key for key in st.session_state.keys()
                                  if any(test_key in key for test_key in [
                        'company_name', 'description', 'website', 'logo',
                        'product_name', 'headline', 'service_name',
                        'event_name', 'recipe_name', 'given_name'
                    ])]
                for key in keys_to_remove:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("🗑️ Données de test nettoyées !")
                st.rerun()

    # ===== FIN NOUVELLE FONCTIONNALITÉ =====

    if not selected_schemas:
        st.warning(get_text('select_at_least_one', st.session_state.language))
        return

    # Afficher les détails des schemas sélectionnés
    if selected_schemas:
        with st.expander(f"📊 Schemas sélectionnés ({len(selected_schemas)})", expanded=False):
            for schema in selected_schemas:
                st.write(f"✅ {schema}")

    # Configuration du client
    st.divider()
    st.subheader("🏢 Informations de base")

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            get_text('company_name', st.session_state.language),
            value=st.session_state.get('company_name', ''),
            key="company_name"
        )
        website = st.text_input(
            "Site web",
            placeholder="https://example.com",
            value=st.session_state.get('website', ''),
            key="website"
        )

    with col2:
        description = st.text_area(
            "Description de l'entreprise",
            value=st.session_state.get('description', ''),
            height=100,
            key="description"
        )
        logo_url = st.text_input(
            "URL du logo",
            value=st.session_state.get('logo', ''),
            key="logo"
        )

    client_info = {
        'name': company_name,
        'website': website,
        'description': description,
        'logo': logo_url
    }

    # Informations supplémentaires pour certains schemas
    legal_name = st.text_input(
        get_text('legal_name', st.session_state.language),
        value=company_name,
        help=get_text('full_legal_name_help', st.session_state.language)
    )

    # Formulaires spécifiques selon les schemas sélectionnés
    st.divider()
    st.subheader("📝 Détails des schemas")

    additional_data = {}

    # Détermine quels formulaires afficher pour Review et AggregateRating
    show_review_form = True
    show_aggregate_form = True

    if enable_deduplication:
        # Ne pas afficher les formulaires séparés si les schemas peuvent être intégrés
        has_reviewable = any(s in selected_schemas for s in ['Organization', 'LocalBusiness', 'Service', 'Product'])
        if 'Review' in selected_schemas and has_reviewable:
            show_review_form = False
        if 'AggregateRating' in selected_schemas and has_reviewable:
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
        product_data = render_product_form(company_name, base_generator)
        additional_data.update(product_data)

    # Article, NewsArticle, BlogPosting
    if any(schema in selected_schemas for schema in ['Article', 'NewsArticle', 'BlogPosting']):
        article_data = render_article_form(selected_schemas)
        additional_data.update(article_data)

    # Recipe
    if 'Recipe' in selected_schemas:
        recipe_data = render_recipe_form()
        additional_data.update(recipe_data)

    # VideoObject
    if 'VideoObject' in selected_schemas:
        video_data = render_video_object_form()
        additional_data.update(video_data)

    # Event
    if 'Event' in selected_schemas:
        event_data = render_event_form(company_name, website)
        additional_data.update(event_data)

    # Course
    if 'Course' in selected_schemas:
        course_data = render_event_form(company_name, website)  # Réutilise le même formulaire
        additional_data.update(course_data)

    # WebSite
    if 'WebSite' in selected_schemas:
        website_data = render_website_form(company_name, website)
        additional_data.update(website_data)

    # FAQPage
    if 'FAQPage' in selected_schemas:
        faq_data = render_faq_form()
        additional_data.update(faq_data)

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

        # Appeler render_service_form normalement
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

        # Toujours afficher le formulaire
        aggregate_data = render_aggregate_rating_form()
        additional_data.update(aggregate_data)

    # Bouton de génération
    st.divider()

    if st.button("🚀 Générer les schemas", type="primary", use_container_width=True):
        if not company_name.strip():
            st.error("⚠️ Le nom de l'entreprise est requis")
            return

        with st.spinner("Génération des schemas en cours..."):
            try:
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
                        st.write(f"{j + 1}. **{schema_type}** {f'(ID: {schema_id})' if schema_id else ''}")

                # Afficher chaque schema de la structure
                if show_preview or show_code:
                    for j, schema in enumerate(schema_data['@graph']):
                        schema_type = schema.get('@type', 'Unknown')
                        if isinstance(schema_type, list):
                            schema_type = ' + '.join(schema_type)

                        with st.expander(f"{schema_type} (Structure #{j + 1})", expanded=False):
                            if show_preview:
                                # Affichage simplifié du schema
                                st.json(schema, expanded=False)

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
                        # Affichage simplifié du schema
                        st.json(schema_data, expanded=False)

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
        # WordPress/CMS - Code simplifié
        wp_code = generate_simple_wordpress_code(st.session_state.generated_schemas)
        st.download_button(
            label="🔌 Code WordPress",
            data=wp_code,
            file_name="schemas-wordpress.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col4:
        # Documentation simplifiée
        doc = generate_simple_implementation_doc(selected_schemas, st.session_state.generated_schemas)
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

            1. **Créez une balise** HTML personnalisée
            2. **Collez** le code HTML généré
            3. **Configurez** le déclencheur (All Pages ou spécifique)
            4. **Testez** en mode prévisualisation
            5. **Publiez** votre conteneur

            **Type de balise :** HTML personnalisé  
            **Déclenchement :** All Pages (ou conditions spécifiques)
            """)

        with tab4:
            st.markdown("""
            ### Validation et test

            **Outils recommandés :**
            - [Google Rich Results Test](https://search.google.com/test/rich-results)
            - [Schema.org Validator](https://validator.schema.org/)
            - [JSON-LD Playground](https://json-ld.org/playground/)

            **Étapes de validation :**
            1. Copiez l'URL de votre page ou le code JSON-LD
            2. Testez avec Google Rich Results Test
            3. Corrigez les erreurs éventuelles
            4. Vérifiez l'éligibilité aux résultats enrichis
            """)