"""
Générateur de données de test pour tous les types de schemas
"""

import streamlit as st
from datetime import datetime, timedelta


class TestDataGenerator:
    """Classe pour générer des données de test pour tous les types de schemas"""

    @staticmethod
    def get_test_data_for_schema(schema_type: str) -> dict:
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
    def _get_organization_test_data() -> dict:
        return {
            'company_name': 'Agence WebTech Solutions',
            'description': 'Agence spécialisée dans le développement web et le marketing digital. Nous accompagnons les entreprises dans leur transformation numérique.',
            'website': 'https://webtech-solutions.com',
            'logo': 'https://webtech-solutions.com/logo.png',
            'telephone': '+33 1 23 45 67 89',
            'email': 'contact@webtech-solutions.com',
            'same_as_urls': 'https://www.linkedin.com/company/webtech-solutions\nhttps://twitter.com/webtechsolutions',
            'founding_date': '2018-03-15',
            'number_of_employees': 25,
            'duns_number': '123456789',
            'vat_id': 'FR12345678901'
        }

    @staticmethod
    def _get_local_business_test_data() -> dict:
        base_data = TestDataGenerator._get_organization_test_data()
        base_data.update({
            'street_address': '123 Avenue des Champs-Élysées',
            'city': 'Paris',
            'postal_code': '75008',
            'country': 'FR',
            'latitude': '48.8738',
            'longitude': '2.2950',
            'price_range': '€€',
            'opening_hours': 'Mo-Fr 09:00-18:00',
            'payment_methods': ['Cash', 'Credit Card', 'Debit Card', 'PayPal'],
            'currencies_accepted': ['EUR', 'USD']
        })
        return base_data

    @staticmethod
    def _get_restaurant_test_data() -> dict:
        base_data = TestDataGenerator._get_local_business_test_data()
        base_data.update({
            'company_name': 'Restaurant Le Petit Gourmet',
            'description': 'Restaurant gastronomique français proposant une cuisine traditionnelle avec des produits frais et de saison.',
            'serves_cuisine': ['French', 'European'],
            'menu_url': 'https://lepetitgourmet.com/menu',
            'accepts_reservations': True,
            'has_delivery': True
        })
        return base_data

    @staticmethod
    def _get_store_test_data() -> dict:
        base_data = TestDataGenerator._get_local_business_test_data()
        base_data.update({
            'company_name': 'Boutique Mode & Style',
            'description': 'Boutique de mode proposant des vêtements tendance pour hommes et femmes.',
            'department': 'Fashion',
            'brand': ['Zara', 'H&M', 'Mango']
        })
        return base_data

    @staticmethod
    def _get_product_test_data() -> dict:
        return {
            'product_name': 'MacBook Pro 16 pouces',
            'product_description': 'Ordinateur portable professionnel Apple avec processeur M3 Pro, 18 Go de RAM et 512 Go de stockage SSD.',
            'brand': 'Apple',
            'sku': 'MBP16-M3-512',
            'gtin': '194252056813',
            'mpn': 'MK1E3FN/A',
            'product_category': 'Electronics > Computers > Laptops',
            'product_availability': 'https://schema.org/InStock',
            'product_condition': 'https://schema.org/NewCondition',
            'product_price': '2899',
            'product_currency': 'EUR',
            'price_valid_until': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'product_images': 'https://example.com/macbook-pro-16.jpg\nhttps://example.com/macbook-pro-16-2.jpg'
        }

    @staticmethod
    def _get_article_test_data() -> dict:
        return {
            'article_headline': 'Comment optimiser le SEO de votre site web en 2024',
            'article_description': 'Guide complet pour améliorer le référencement naturel de votre site web avec les dernières bonnes pratiques SEO.',
            'author_name': 'Sophie Martin',
            'publisher_name': 'Blog WebTech',
            'date_published': '2024-01-15',
            'date_modified': '2024-01-20',
            'article_image': 'https://example.com/seo-guide-2024.jpg',
            'word_count': 2500,
            'article_section': 'SEO',
            'keywords': 'SEO, référencement, optimisation, Google'
        }

    @staticmethod
    def _get_news_article_test_data() -> dict:
        base_data = TestDataGenerator._get_article_test_data()
        base_data.update({
            'article_headline': 'Google met à jour son algorithme de recherche',
            'article_description': 'Le géant américain annonce une nouvelle mise à jour majeure de son algorithme qui impactera les résultats de recherche.',
            'article_section': 'Technologie',
            'dateline': 'Mountain View, Californie'
        })
        return base_data

    @staticmethod
    def _get_blog_posting_test_data() -> dict:
        base_data = TestDataGenerator._get_article_test_data()
        base_data.update({
            'article_headline': '10 astuces pour améliorer la vitesse de votre site web',
            'article_description': 'Découvrez nos conseils d\'expert pour optimiser les performances et la vitesse de chargement de votre site internet.',
            'blog_name': 'Blog WebTech Solutions'
        })
        return base_data

    @staticmethod
    def _get_review_test_data() -> dict:
        return {
            'review_type': 'Service',
            'itemreviewed_name': 'Service de développement web',
            'review_rating': '5',
            'review_author': 'Marc Dubois',
            'review_date': '2024-01-10',
            'review_text': 'Excellent service ! L\'équipe a été très professionnelle et a livré un site web parfaitement adapté à nos besoins. Je recommande vivement.',
            'review_summary': 'Service exceptionnel',
            'would_recommend': True,
            'review_tags': 'professionnel, qualité, recommandé',
            'review_images': 'https://example.com/review-image.jpg'
        }

    @staticmethod
    def _get_aggregate_rating_test_data() -> dict:
        return {
            'target_type': 'Service',
            'target_name': 'Service de développement web',
            'rating_value': '4.8',
            'best_rating': '5',
            'worst_rating': '1',
            'review_count': '127'
        }

    @staticmethod
    def _get_recipe_test_data() -> dict:
        return {
            'recipe_name': 'Tarte aux pommes traditionnelle',
            'recipe_description': 'Une délicieuse tarte aux pommes faite maison avec une pâte brisée croustillante et des pommes fondantes.',
            'recipe_author': 'Chef Marie Dupont',
            'recipe_cuisine': 'Française',
            'recipe_category': 'Dessert',
            'prep_time': 'PT30M',
            'cook_time': 'PT45M',
            'total_time': 'PT75M',
            'recipe_yield': '8',
            'recipe_ingredients': 'Pâte brisée\n6 pommes\n100g de sucre\n50g de beurre\n1 œuf\nCannelle',
            'recipe_instructions': '1. Préchauffer le four à 180°C\n2. Étaler la pâte dans un moule\n3. Éplucher et couper les pommes\n4. Disposer les pommes sur la pâte\n5. Saupoudrer de sucre et cannelle\n6. Cuire 45 minutes',
            'recipe_nutrition': '{"calories": "280", "fat": "12g", "carbs": "45g", "protein": "4g"}',
            'recipe_keywords': 'tarte, pommes, dessert, français'
        }

    @staticmethod
    def _get_video_object_test_data() -> dict:
        return {
            'video_name': 'Tutoriel : Comment créer un site web professionnel',
            'video_description': 'Apprenez à créer un site web professionnel étape par étape avec ce tutoriel complet.',
            'video_duration': 'PT15M30S',
            'video_upload_date': '2024-01-15',
            'video_thumbnail_url': 'https://example.com/video-thumbnail.jpg',
            'content_url': 'https://example.com/video.mp4',
            'embed_url': 'https://example.com/embed/video123',
            'publisher_name': 'WebTech Academy'
        }

    @staticmethod
    def _get_event_test_data() -> dict:
        return {
            'event_name': 'Conférence Web Marketing 2024',
            'event_description': 'Conférence dédiée aux dernières tendances du marketing digital et du e-commerce.',
            'event_start_date': '2024-03-15',
            'event_start_time': '09:00',
            'event_end_date': '2024-03-15',
            'event_end_time': '17:00',
            'event_mode': 'OfflineEventAttendanceMode',
            'event_status': 'https://schema.org/EventScheduled',
            'venue_name': 'Palais des Congrès',
            'venue_address': '2 Place de la Porte Maillot, 75017 Paris',
            'organizer_name': 'WebTech Events',
            'organizer_url': 'https://webtech-events.com',
            'ticket_price': '150',
            'ticket_currency': 'EUR',
            'ticket_url': 'https://webtech-events.com/billets'
        }

    @staticmethod
    def _get_course_test_data() -> dict:
        return {
            'course_name': 'Formation SEO Avancé',
            'course_description': 'Formation complète pour maîtriser les techniques avancées de référencement naturel.',
            'provider_name': 'WebTech Academy',
            'course_mode': 'online',
            'course_duration': 'P30D',
            'course_price': '499',
            'course_currency': 'EUR',
            'course_level': 'Advanced',
            'course_prerequisites': 'Connaissances de base en SEO',
            'course_outcomes': 'Maîtrise des techniques SEO avancées\nOptimisation technique\nStratégie de contenu'
        }

    @staticmethod
    def _get_website_test_data() -> dict:
        return {
            'site_name': 'WebTech Solutions',
            'alternate_name': 'WTS',
            'site_description': 'Agence web spécialisée dans le développement et le marketing digital',
            'potential_action': True,
            'search_target': 'https://webtech-solutions.com/search?q={search_term_string}',
            'search_term': 'search_term_string'
        }

    @staticmethod
    def _get_breadcrumb_test_data() -> dict:
        return {
            'breadcrumbs': 'Accueil > Services > Développement Web > E-commerce'
        }

    @staticmethod
    def _get_faq_test_data() -> dict:
        return {
            'faq_items': 'Combien coûte un site web ?\nLe prix varie selon la complexité et les fonctionnalités souhaitées. Contactez-nous pour un devis personnalisé.\n\nCombien de temps faut-il pour créer un site ?\nEn moyenne, il faut 4 à 8 semaines selon la complexité du projet.\n\nProposez-vous la maintenance ?\nOui, nous proposons des contrats de maintenance mensuels pour assurer la sécurité et les mises à jour.'
        }

    @staticmethod
    def _get_person_test_data() -> dict:
        return {
            'person_name': 'Sophie Martin',
            'person_job_title': 'Directrice Marketing Digital',
            'person_description': 'Expert en marketing digital avec plus de 10 ans d\'expérience dans le secteur.',
            'person_email': 'sophie.martin@webtech-solutions.com',
            'person_telephone': '+33 1 23 45 67 90',
            'person_same_as': 'https://www.linkedin.com/in/sophie-martin-marketing\nhttps://twitter.com/sophiemartin',
            'person_image': 'https://example.com/sophie-martin.jpg',
            'person_birth_date': '1985-06-15',
            'person_nationality': 'FR'
        }

    @staticmethod
    def _get_job_posting_test_data() -> dict:
        return {
            'job_title': 'Développeur Full Stack Senior',
            'job_description': 'Nous recherchons un développeur full stack expérimenté pour rejoindre notre équipe dynamique.',
            'employment_type': 'FULL_TIME',
            'job_location_type': 'Hybrid',
            'job_city': 'Paris',
            'job_country': 'FR',
            'salary_min': '45000',
            'salary_max': '65000',
            'salary_currency': 'EUR',
            'date_posted': datetime.now().strftime('%Y-%m-%d'),
            'valid_through': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'required_skills': 'JavaScript, React, Node.js, Python, PostgreSQL',
            'preferred_qualifications': 'Bac+5 en informatique\n3+ ans d\'expérience\nMaîtrise de l\'anglais',
            'work_hours': '35'
        }

    @staticmethod
    def _get_service_test_data() -> dict:
        return {
            'service_name': 'Développement d\'applications web',
            'service_description': 'Conception et développement d\'applications web sur mesure pour entreprises.',
            'service_type': 'Web Development',
            'area_served': 'France, Europe',
            'service_duration': '2 à 6 mois selon complexité',
            'delivery_method': ['En ligne', 'Sur site', 'Hybride'],
            'certifications': 'Google Partner\nCertifié Symfony\nCertifié AWS',
            'guarantees': 'Garantie 12 mois\nSupport technique inclus',
            'process_steps': '1. Analyse des besoins\n2. Conception UX/UI\n3. Développement\n4. Tests et validation\n5. Déploiement\n6. Formation\n7. Support',
            'offers_catalog': [
                {
                    'name': 'Site vitrine',
                    'price': 'À partir de 2500€',
                    'description': 'Site web professionnel avec CMS'
                },
                {
                    'name': 'E-commerce',
                    'price': 'À partir de 8000€',
                    'description': 'Boutique en ligne complète'
                }
            ]
        }

    @staticmethod
    def _get_software_application_test_data() -> dict:
        return {
            'app_name': 'TaskManager Pro',
            'app_category': 'ProductivityApplication',
            'app_subcategory': 'Task Management',
            'operating_systems': ['Windows', 'macOS', 'Web'],
            'software_version': '2.1.0',
            'pricing_model': 'Freemium',
            'features': 'Gestion de tâches\nCollaboration équipe\nTableaux Kanban\nRapports avancés',
            'screenshots': 'https://example.com/taskmanager-screenshot1.jpg\nhttps://example.com/taskmanager-screenshot2.jpg',
            'documentation_url': 'https://taskmanager-pro.com/docs',
            'support_url': 'https://taskmanager-pro.com/support',
            'privacy_policy_url': 'https://taskmanager-pro.com/privacy',
            'terms_url': 'https://taskmanager-pro.com/terms',
            'permissions': 'Accès réseau\nStockage local\nNotifications'
        }

    @staticmethod
    def _get_howto_test_data() -> dict:
        return {
            'howto_name': 'Comment optimiser la vitesse de votre site web',
            'total_time': 'PT2H',
            'estimated_cost': {
                'value': '0',
                'currency': 'EUR'
            },
            'tools': 'Google PageSpeed Insights\nGTmetrix\nCompresseur d\'images\nÉditeur de code',
            'supplies': 'Accès FTP au site\nSauvegarde du site\nCompte Google Analytics',
            'steps': '1. Analyser les performances actuelles\n2. Optimiser les images\n3. Minifier CSS et JavaScript\n4. Configurer la mise en cache\n5. Optimiser la base de données\n6. Tester les améliorations'
        }

    @staticmethod
    def apply_test_data_to_session_state(selected_schemas: list):
        """Applique les données de test à la session state pour les schémas sélectionnés"""

        # Données de base communes
        base_test_data = TestDataGenerator._get_organization_test_data()

        # Parcourir chaque schéma sélectionné et ajouter ses données de test
        for schema_type in selected_schemas:
            schema_test_data = TestDataGenerator.get_test_data_for_schema(schema_type)

            # Mettre à jour la session state avec les données de test
            for key, value in schema_test_data.items():
                # Utiliser les clés originales directement sans préfixe
                st.session_state[key] = value

        # S'assurer que les données de base sont aussi dans la session state
        for key, value in base_test_data.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def populate_form_fields_with_test_data(selected_schemas: list):
        """
        Remplit les champs de formulaire avec des données de test.
        Cette méthode s'assure que les widget keys correspondent aux données de test.
        """

        # Nettoyer d'abord les données de test existantes
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith('test_')]
        for key in keys_to_remove:
            del st.session_state[key]

        # Appliquer les nouvelles données de test
        TestDataGenerator.apply_test_data_to_session_state(selected_schemas)

        return len(selected_schemas)