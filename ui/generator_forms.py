"""
Formulaires pour la collecte des données du générateur de schemas
"""
import streamlit as st
from datetime import datetime
from ui.country_selector import render_country_selector


def render_business_info_form(company_name, legal_name, logo_url):
    """Formulaire pour les informations d'entreprise"""
    additional_data = {}

    with st.expander("🏢 Informations d'entreprise", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            additional_data['legal_name'] = legal_name
            additional_data['logo'] = logo_url
            additional_data['taxID'] = st.text_input("Numéro fiscal/SIRET")
            additional_data['vatID'] = st.text_input("Numéro TVA")

        with col2:
            additional_data['naics'] = st.text_input(
                "Code NAICS",
                help="Classification industrielle nord-américaine"
            )
            additional_data['employee_count'] = st.number_input(
                "Nombre d'employés",
                min_value=0,
                value=0
            )

        with col3:
            founding_date = st.date_input("Date de création")
            if founding_date:
                additional_data['foundingDate'] = founding_date.isoformat()

            additional_data['slogan'] = st.text_input("Slogan")

    return additional_data


def render_address_form():
    """Formulaire pour l'adresse"""
    additional_data = {}

    with st.expander("📍 Adresse et localisation"):
        col1, col2 = st.columns(2)

        with col1:
            street = st.text_input("Adresse")
            city = st.text_input("Ville")
            postal_code = st.text_input("Code postal")

        with col2:
            region = st.text_input("Région/État")
            country = render_country_selector()

        additional_data['address'] = {
            'streetAddress': street,
            'addressLocality': city,
            'addressRegion': region,
            'postalCode': postal_code,
            'addressCountry': country
        }

    return additional_data


def render_contact_form():
    """Formulaire pour les informations de contact"""
    additional_data = {}

    with st.expander("☎️ Informations de contact"):
        col1, col2 = st.columns(2)

        with col1:
            telephone = st.text_input(
                "Téléphone principal",
                placeholder="+33 1 23 45 67 89"
            )
            email = st.text_input("Email principal")

        with col2:
            fax = st.text_input("Fax (optionnel)")

        additional_data['telephone'] = telephone
        additional_data['email'] = email
        if fax:
            additional_data['faxNumber'] = fax

        # Points de contact multiples
        st.subheader("Points de contact")
        num_contacts = st.number_input(
            "Nombre de points de contact",
            min_value=0,
            max_value=5,
            value=1
        )

        contact_points = []
        for i in range(num_contacts):
            st.write(f"**Contact {i + 1}**")
            col1, col2, col3 = st.columns(3)

            with col1:
                contact_type = st.selectbox(
                    "Type",
                    ["customer service", "technical support", "sales", "billing"],
                    key=f"contact_type_{i}"
                )

            with col2:
                contact_phone = st.text_input(
                    "Téléphone",
                    key=f"contact_phone_{i}"
                )

            with col3:
                contact_email = st.text_input(
                    "Email",
                    key=f"contact_email_{i}"
                )

            contact_languages = st.multiselect(
                "Langues disponibles",
                ["French", "English", "Spanish", "German", "Italian"],
                key=f"contact_lang_{i}"
            )

            if contact_phone or contact_email:
                contact_points.append({
                    'type': contact_type,
                    'telephone': contact_phone,
                    'email': contact_email,
                    'languages': contact_languages,
                    'area_served': additional_data.get('address', {}).get('addressCountry', '')
                })

        if contact_points:
            additional_data['contact_points'] = contact_points

    return additional_data


def render_local_business_form():
    """Formulaire pour LocalBusiness"""
    additional_data = {}

    with st.expander("🏪 Informations commerce local"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📍 Géolocalisation")
            lat = st.text_input(
                "Latitude",
                help="Ex: 48.8566"
            )
            lng = st.text_input(
                "Longitude",
                help="Ex: 2.3522"
            )

            if lat and lng:
                additional_data['geo'] = {'lat': lat, 'lng': lng}

        with col2:
            st.subheader("💳 Commerce")
            additional_data['price_range'] = st.selectbox(
                "Gamme de prix",
                ["€", "€€", "€€€", "€€€€"]
            )

            payment_methods = st.multiselect(
                "Moyens de paiement acceptés",
                ["Cash", "Credit Card", "Debit Card", "Mobile Payment",
                 "Bank Transfer", "Check", "PayPal", "Apple Pay", "Google Pay"]
            )
            if payment_methods:
                additional_data['payment_accepted'] = ", ".join(payment_methods)

            currencies = st.multiselect(
                "Devises acceptées",
                ["EUR", "USD", "GBP", "CHF", "CAD"]
            )
            if currencies:
                additional_data['currencies_accepted'] = ", ".join(currencies)

        # Horaires d'ouverture
        st.subheader("🕐 Horaires d'ouverture")
        opening_hours_type = st.radio(
            "Format des horaires",
            ["Simple", "Détaillé"],
            horizontal=True
        )

        if opening_hours_type == "Simple":
            opening_hours_simple = st.text_input(
                "Horaires",
                placeholder="Mo-Fr 09:00-18:00, Sa 10:00-16:00"
            )
            if opening_hours_simple:
                additional_data['openingHours'] = opening_hours_simple
        else:
            # Horaires détaillés
            opening_hours = []
            days_groups = [
                ("Lundi-Vendredi", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
                ("Samedi", ["Saturday"]),
                ("Dimanche", ["Sunday"])
            ]

            for group_name, days in days_groups:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    if st.checkbox(f"Ouvert {group_name}", key=f"open_{group_name}"):
                        with col2:
                            opens = st.time_input(
                                "Ouverture",
                                key=f"opens_{group_name}"
                            )
                        with col3:
                            closes = st.time_input(
                                "Fermeture",
                                key=f"closes_{group_name}"
                            )

                        opening_hours.append({
                            'days': days,
                            'opens': opens.strftime("%H:%M"),
                            'closes': closes.strftime("%H:%M")
                        })

            if opening_hours:
                additional_data['opening_hours'] = opening_hours

    return additional_data


def render_restaurant_form():
    """Formulaire pour Restaurant"""
    additional_data = {}

    with st.expander("🍽️ Informations restaurant"):
        cuisines = st.multiselect(
            "Types de cuisine",
            ["Française", "Italienne", "Japonaise", "Chinoise", "Indienne",
             "Mexicaine", "Méditerranéenne", "Végétarienne", "Vegane",
             "Gastronomique", "Traditionnelle", "Moderne", "Fusion"]
        )
        if cuisines:
            additional_data['cuisines'] = cuisines

        col1, col2 = st.columns(2)
        with col1:
            menu_url = st.text_input("URL du menu")
            if menu_url:
                additional_data['menu_url'] = menu_url

        with col2:
            accepts_reservations = st.checkbox("Accepte les réservations")
            additional_data['accepts_reservations'] = accepts_reservations

    return additional_data


def render_product_form(company_name, generator):
    """Formulaire pour Product"""
    additional_data = {}

    with st.expander("📦 Informations produit"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Identification")
            additional_data['product_name'] = st.text_input("Nom du produit")
            additional_data['sku'] = st.text_input("SKU/Référence")
            additional_data['gtin13'] = st.text_input("Code-barres EAN-13")
            additional_data['mpn'] = st.text_input("Référence fabricant")
            additional_data['brand_name'] = st.text_input(
                "Marque",
                value=company_name
            )

        with col2:
            st.subheader("Prix et disponibilité")
            additional_data['price'] = st.text_input("Prix")
            additional_data['currency'] = st.selectbox(
                "Devise",
                ["EUR", "USD", "GBP", "CHF", "CAD"]
            )
            additional_data['availability'] = st.selectbox(
                "Disponibilité",
                options=list(generator.enumerations['availability']),
                format_func=lambda x: x.split('/')[-1]
            )

            price_valid = st.date_input("Prix valide jusqu'au")
            if price_valid:
                additional_data['price_valid_until'] = price_valid.isoformat()

        st.subheader("Caractéristiques")
        col1, col2, col3 = st.columns(3)

        with col1:
            additional_data['color'] = st.text_input("Couleur")
            additional_data['size'] = st.text_input("Taille")

        with col2:
            additional_data['material'] = st.text_input("Matériaux")
            additional_data['weight_value'] = st.text_input("Poids")

        with col3:
            if additional_data.get('weight_value'):
                additional_data['weight_unit'] = st.selectbox(
                    "Unité",
                    ["GRM", "KGM", "LBR", "ONZ"]
                )

        # Images produit
        st.subheader("Images")
        num_images = st.number_input(
            "Nombre d'images",
            min_value=1,
            max_value=10,
            value=3
        )

        images = []
        for i in range(num_images):
            img_url = st.text_input(
                f"URL image {i + 1}",
                key=f"product_img_{i}"
            )
            if img_url:
                images.append(img_url)

        if images:
            additional_data['images'] = images

    return additional_data


def render_article_form(logo_url):
    """Formulaire pour Article/News"""
    additional_data = {}

    with st.expander("📄 Informations article"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['headline'] = st.text_input(
                "Titre de l'article",
                help="Maximum 110 caractères recommandé"
            )
            additional_data['article_section'] = st.text_input(
                "Section",
                placeholder="Technologie, Santé, Sport..."
            )
            additional_data['author_name'] = st.text_input("Nom de l'auteur")

        with col2:
            additional_data['author_url'] = st.text_input("URL profil auteur")
            additional_data['publisher_logo'] = st.text_input(
                "Logo éditeur",
                value=logo_url
            )
            additional_data['keywords'] = st.text_input(
                "Mots-clés",
                placeholder="Séparez par des virgules"
            )

        # Corps de l'article
        additional_data['article_body'] = st.text_area(
            "Corps de l'article (optionnel)",
            height=200,
            help="Le contenu complet de l'article"
        )

        # Images multiples formats
        st.subheader("Images (formats multiples)")
        st.caption("Google recommande 3 formats: 16:9, 4:3, 1:1")

        col1, col2, col3 = st.columns(3)
        images = []

        with col1:
            img_16_9 = st.text_input("Image 16:9", key="img_16_9")
            if img_16_9:
                images.append(img_16_9)

        with col2:
            img_4_3 = st.text_input("Image 4:3", key="img_4_3")
            if img_4_3:
                images.append(img_4_3)

        with col3:
            img_1_1 = st.text_input("Image 1:1", key="img_1_1")
            if img_1_1:
                images.append(img_1_1)

        if images:
            additional_data['images'] = images

    return additional_data


def render_faq_form():
    """Formulaire pour FAQPage"""
    additional_data = {}

    with st.expander("❓ Questions/Réponses FAQ"):
        num_questions = st.number_input(
            "Nombre de questions",
            min_value=1,
            max_value=20,
            value=3
        )

        questions = []
        for i in range(num_questions):
            st.write(f"**Question {i + 1}**")
            q = st.text_input(
                "Question",
                key=f"faq_q_{i}"
            )
            a = st.text_area(
                "Réponse",
                key=f"faq_a_{i}",
                height=100
            )

            if q and a:
                questions.append({'question': q, 'answer': a})

        if questions:
            additional_data['questions'] = questions

    return additional_data


def render_event_form(company_name, website, generator):
    """Formulaire pour Event"""
    additional_data = {}

    with st.expander("📅 Informations événement"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Dates et horaires")
            start_date = st.date_input("Date de début")
            start_time = st.time_input("Heure de début")

            end_date = st.date_input("Date de fin")
            end_time = st.time_input("Heure de fin")

            if start_date and start_time:
                additional_data['start_date'] = f"{start_date.isoformat()}T{start_time.strftime('%H:%M:%S')}+01:00"

            if end_date and end_time:
                additional_data['end_date'] = f"{end_date.isoformat()}T{end_time.strftime('%H:%M:%S')}+01:00"

        with col2:
            st.subheader("Mode de participation")
            attendance_mode = st.selectbox(
                "Type d'événement",
                options=list(generator.enumerations['eventAttendanceMode']),
                format_func=lambda x: {
                    'https://schema.org/OfflineEventAttendanceMode': '🏢 En présentiel',
                    'https://schema.org/OnlineEventAttendanceMode': '💻 En ligne',
                    'https://schema.org/MixedEventAttendanceMode': '🔄 Hybride'
                }[x]
            )
            additional_data['attendance_mode'] = attendance_mode

            event_status = st.selectbox(
                "Statut",
                options=list(generator.enumerations['eventStatus']),
                format_func=lambda x: x.split('/')[-1]
            )
            additional_data['event_status'] = event_status

        # Lieu physique
        if attendance_mode in ['https://schema.org/OfflineEventAttendanceMode',
                               'https://schema.org/MixedEventAttendanceMode']:
            st.subheader("📍 Lieu physique")
            additional_data['location_name'] = st.text_input("Nom du lieu")

        # Lieu virtuel
        if attendance_mode in ['https://schema.org/OnlineEventAttendanceMode',
                               'https://schema.org/MixedEventAttendanceMode']:
            st.subheader("💻 Accès en ligne")
            additional_data['virtual_location_url'] = st.text_input(
                "URL de l'événement en ligne"
            )

        # Organisateur et intervenants
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Organisateur")
            additional_data['organizer_name'] = st.text_input(
                "Nom de l'organisateur",
                value=company_name
            )
            additional_data['organizer_url'] = st.text_input(
                "Site de l'organisateur",
                value=website
            )

        with col2:
            st.subheader("Billetterie")
            additional_data['ticket_price'] = st.text_input("Prix du billet")
            additional_data['ticket_url'] = st.text_input("URL billetterie")
            ticket_currency = st.selectbox(
                "Devise",
                ["EUR", "USD", "GBP", "CHF", "CAD"],
                key="event_currency"
            )
            if additional_data.get('ticket_price'):
                additional_data['ticket_currency'] = ticket_currency

    return additional_data


def render_howto_form():
    """Formulaire pour HowTo"""
    additional_data = {}

    with st.expander("🔧 Guide pratique HowTo"):
        col1, col2 = st.columns(2)

        with col1:
            howto_name = st.text_input("Titre du guide")
            total_time = st.text_input(
                "Temps total",
                placeholder="PT45M (45 minutes)",
                help="Format ISO 8601: PT30M, PT1H30M..."
            )

            if howto_name:
                additional_data['howto_name'] = howto_name
            if total_time:
                additional_data['total_time'] = total_time

        with col2:
            estimated_cost = st.text_input("Coût estimé")
            cost_currency = st.selectbox(
                "Devise",
                ["EUR", "USD", "GBP"],
                key="howto_currency"
            )

            if estimated_cost:
                additional_data['estimated_cost'] = {
                    'value': estimated_cost,
                    'currency': cost_currency
                }

        # Outils et matériel
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔨 Outils nécessaires")
            tools = st.text_area(
                "Un outil par ligne",
                height=100
            )
            if tools:
                additional_data['tools'] = tools.strip().split('\n')

        with col2:
            st.subheader("📦 Matériel nécessaire")
            supplies = st.text_area(
                "Un matériel par ligne",
                height=100
            )
            if supplies:
                additional_data['supplies'] = supplies.strip().split('\n')

        # Étapes
        st.subheader("📋 Étapes")
        num_steps = st.number_input(
            "Nombre d'étapes",
            min_value=2,
            max_value=20,
            value=3
        )

        steps = []
        for i in range(num_steps):
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    step_name = st.text_input(
                        f"Étape {i + 1} - Titre",
                        key=f"step_name_{i}"
                    )
                    step_text = st.text_area(
                        f"Instructions",
                        key=f"step_text_{i}",
                        height=80
                    )

                with col2:
                    step_image = st.text_input(
                        "Image (optionnel)",
                        key=f"step_img_{i}"
                    )

                if step_name and step_text:
                    step_data = {
                        'name': step_name,
                        'text': step_text,
                        'position': i + 1
                    }
                    if step_image:
                        step_data['image'] = step_image
                    steps.append(step_data)

        if steps:
            additional_data['steps'] = steps

    return additional_data


def render_person_form(company_name):
    """Formulaire pour Person"""
    additional_data = {}

    with st.expander("👤 Informations personne"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['given_name'] = st.text_input("Prénom")
            additional_data['family_name'] = st.text_input("Nom")
            additional_data['job_title'] = st.text_input("Fonction")
            additional_data['email'] = st.text_input("Email", key="person_email")

        with col2:
            additional_data['telephone'] = st.text_input("Téléphone", key="person_phone")
            additional_data['image'] = st.text_input("Photo de profil")
            additional_data['works_for'] = st.text_input(
                "Entreprise",
                value=company_name
            )

    return additional_data


def render_breadcrumb_form(website):
    """Formulaire pour BreadcrumbList"""
    additional_data = {}

    with st.expander("🍞 Fil d'Ariane"):
        st.caption("Définissez le chemin de navigation de votre page")

        num_crumbs = st.number_input(
            "Nombre de niveaux",
            min_value=2,
            max_value=5,
            value=3
        )

        breadcrumbs = []
        for i in range(num_crumbs):
            col1, col2 = st.columns(2)

            with col1:
                crumb_name = st.text_input(
                    f"Niveau {i + 1} - Nom",
                    placeholder="Accueil" if i == 0 else "",
                    key=f"crumb_name_{i}"
                )

            with col2:
                crumb_url = st.text_input(
                    f"URL",
                    placeholder=website if i == 0 else "",
                    key=f"crumb_url_{i}"
                )

            if crumb_name and crumb_url:
                breadcrumbs.append({
                    'name': crumb_name,
                    'url': crumb_url
                })

        if breadcrumbs:
            additional_data['breadcrumbs'] = breadcrumbs

    return additional_data


def render_job_posting_form(generator):
    """Formulaire pour JobPosting"""
    additional_data = {}

    with st.expander("💼 Offre d'emploi"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['job_title'] = st.text_input("Intitulé du poste")
            additional_data['job_description'] = st.text_area(
                "Description du poste",
                height=150
            )

            employment_types = st.multiselect(
                "Type d'emploi",
                options=list(generator.enumerations['employmentType']),
                format_func=lambda x: {
                    'FULL_TIME': 'Temps plein',
                    'PART_TIME': 'Temps partiel',
                    'CONTRACTOR': 'Freelance',
                    'TEMPORARY': 'Temporaire',
                    'INTERN': 'Stage',
                    'VOLUNTEER': 'Bénévolat',
                    'PER_DIEM': 'Vacation',
                    'OTHER': 'Autre'
                }.get(x, x)
            )
            additional_data['employment_types'] = employment_types

        with col2:
            date_posted = st.date_input("Date de publication", key="job_date")
            if date_posted:
                additional_data['date_posted'] = date_posted.isoformat()

            valid_through = st.date_input("Valide jusqu'au", key="job_valid")
            if valid_through:
                additional_data['valid_through'] = valid_through.isoformat()

            # Salaire
            salary_min = st.text_input("Salaire minimum")
            salary_max = st.text_input("Salaire maximum")
            if salary_min or salary_max:
                salary_currency = st.selectbox(
                    "Devise",
                    ["EUR", "USD", "GBP"],
                    key="job_currency"
                )
                additional_data['salary'] = {
                    'min': salary_min,
                    'max': salary_max,
                    'currency': salary_currency
                }

    return additional_data

def render_service_form(company_name):
    """Formulaire pour Service - SANS reviews intégrées"""
    additional_data = {}

    with st.expander("🔧 Informations du service"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['service_name'] = st.text_input(
                "Nom du service",
                help="Nom spécifique du service offert"
            )

            additional_data['service_type'] = st.text_input(
                "Type de service",
                placeholder="Consulting, Marketing Digital, Développement Web...",
                help="Catégorie ou type de service"
            )

            additional_data['service_description'] = st.text_area(
                "Description détaillée du service",
                height=100,
                help="Description complète de ce que comprend le service"
            )

        with col2:
            # Zone de service
            area_served = st.multiselect(
                "Zones desservies",
                ["Local", "Régional", "National", "International", "Europe", "Monde"],
                help="Zones géographiques où le service est disponible"
            )
            if area_served:
                additional_data['area_served'] = area_served

            # Tarification
            additional_data['price_range'] = st.selectbox(
                "Gamme de prix",
                ["€", "€€", "€€€", "€€€€", "Sur devis"],
                help="Indication de la gamme tarifaire"
            )

            # Disponibilité
            availability = st.selectbox(
                "Disponibilité",
                ["Immédiate", "Sous 24h", "Sous 48h", "Sur rendez-vous", "Selon planning"],
                help="Délai de disponibilité du service"
            )
            if availability:
                additional_data['availability'] = availability

        # Catalogue de services (offres multiples)
        st.subheader("📋 Catalogue de services")
        num_offers = st.number_input(
            "Nombre de services/offres dans le catalogue",
            min_value=0,
            max_value=10,
            value=0,
            help="Si vous proposez plusieurs variantes ou options de service"
        )

        offers = []
        for i in range(num_offers):
            with st.container():
                st.write(f"**Service {i + 1}**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    offer_name = st.text_input(
                        "Nom de l'offre",
                        key=f"offer_name_{i}"
                    )

                with col2:
                    offer_price = st.text_input(
                        "Prix",
                        placeholder="1000€, À partir de 500€...",
                        key=f"offer_price_{i}"
                    )

                with col3:
                    offer_description = st.text_input(
                        "Description courte",
                        key=f"offer_desc_{i}"
                    )

                if offer_name:
                    offers.append({
                        'name': offer_name,
                        'price': offer_price,
                        'description': offer_description
                    })

        if offers:
            additional_data['offers_catalog'] = offers

        # Caractéristiques du service
        st.subheader("✨ Caractéristiques")
        col1, col2 = st.columns(2)

        with col1:
            # Durée du service
            service_duration = st.text_input(
                "Durée typique",
                placeholder="1 heure, 3 mois, Projet de 6 mois...",
                help="Durée moyenne du service"
            )
            if service_duration:
                additional_data['service_duration'] = service_duration

            # Méthode de livraison
            delivery_method = st.multiselect(
                "Méthode de livraison",
                ["En ligne", "Sur site", "Hybride", "À distance", "En présentiel"],
                help="Comment le service est-il délivré"
            )
            if delivery_method:
                additional_data['delivery_method'] = delivery_method

        with col2:
            # Certifications/Accréditations
            certifications = st.text_area(
                "Certifications/Accréditations",
                placeholder="ISO 9001, Google Partner, HubSpot Certified...",
                help="Une certification par ligne",
                height=80
            )
            if certifications:
                additional_data['certifications'] = certifications.strip().split('\n')

            # Garanties
            guarantees = st.text_input(
                "Garanties offertes",
                placeholder="Satisfaction garantie, Support 24/7...",
                help="Garanties ou engagements liés au service"
            )
            if guarantees:
                additional_data['guarantees'] = guarantees

        # Processus du service
        st.subheader("📊 Processus du service")
        process_steps = st.text_area(
            "Étapes du processus",
            placeholder="1. Consultation initiale\n2. Analyse des besoins\n3. Proposition\n4. Mise en œuvre\n5. Suivi",
            help="Décrivez les étapes principales du service",
            height=100
        )
        if process_steps:
            additional_data['process_steps'] = process_steps.strip().split('\n')

        # SUPPRIMÉ : Toute la partie "Témoignages/Reviews"
        # Message informatif à la place
        st.info("💡 Pour ajouter des avis clients, sélectionnez 'Review' et/ou 'AggregateRating' dans la liste des schémas à générer.")

    return additional_data


def render_software_application_form(company_name, website):
    """Formulaire pour SoftwareApplication"""
    additional_data = {}

    with st.expander("💻 Informations de l'application"):
        col1, col2 = st.columns(2)

        with col1:
            additional_data['app_name'] = st.text_input(
                "Nom de l'application",
                help="Nom officiel de votre logiciel/application"
            )

            additional_data['app_category'] = st.selectbox(
                "Catégorie d'application",
                ["BusinessApplication", "DesignApplication", "DeveloperApplication",
                 "EducationalApplication", "EntertainmentApplication", "FinanceApplication",
                 "GameApplication", "HealthApplication", "LifestyleApplication",
                 "MedicalApplication", "MusicApplication", "NewsApplication",
                 "PhotoApplication", "ProductivityApplication", "SecurityApplication",
                 "ShoppingApplication", "SocialNetworkingApplication", "SportsApplication",
                 "TravelApplication", "UtilitiesApplication", "VideoApplication", "WeatherApplication"],
                help="Catégorie principale de l'application"
            )

            additional_data['app_subcategory'] = st.text_input(
                "Sous-catégorie",
                placeholder="CRM, Project Management, Analytics...",
                help="Sous-catégorie plus spécifique"
            )

        with col2:
            additional_data['operating_systems'] = st.multiselect(
                "Systèmes d'exploitation",
                ["Windows", "macOS", "Linux", "iOS", "Android", "Web", "Cross-platform"],
                help="Systèmes supportés"
            )

            additional_data['software_version'] = st.text_input(
                "Version actuelle",
                placeholder="2.5.1",
                help="Numéro de version actuel"
            )

            additional_data['file_size'] = st.text_input(
                "Taille du fichier",
                placeholder="50 MB",
                help="Taille du téléchargement"
            )

        # URLs de téléchargement
        st.subheader("⬇️ Téléchargement et installation")
        col1, col2 = st.columns(2)

        with col1:
            additional_data['download_url'] = st.text_input(
                "URL de téléchargement",
                placeholder=f"{website}/download",
                help="Lien direct de téléchargement"
            )

            additional_data['install_url'] = st.text_input(
                "URL d'installation",
                placeholder=f"{website}/install",
                help="Page d'instructions d'installation"
            )

        with col2:
            additional_data['software_requirements'] = st.text_area(
                "Configuration requise",
                placeholder="• RAM: 4GB minimum\n• Espace disque: 500MB\n• Internet requis",
                height=80,
                help="Configuration système requise"
            )

        # Tarification
        st.subheader("💰 Modèle de tarification")
        pricing_model = st.selectbox(
            "Modèle de prix",
            ["Gratuit", "Freemium", "Essai gratuit", "Achat unique", "Abonnement", "Par utilisateur", "Sur devis"]
        )

        if pricing_model != "Gratuit":
            col1, col2 = st.columns(2)

            with col1:
                additional_data['price'] = st.text_input(
                    "Prix",
                    placeholder="29.99€, À partir de 10€/mois..."
                )

            with col2:
                additional_data['price_currency'] = st.selectbox(
                    "Devise",
                    ["EUR", "USD", "GBP"]
                )
        else:
            additional_data['price'] = "0"
            additional_data['price_currency'] = "EUR"

        additional_data['pricing_model'] = pricing_model

        # Fonctionnalités
        st.subheader("⚡ Fonctionnalités principales")
        features = st.text_area(
            "Liste des fonctionnalités",
            placeholder="• Gestion de projets\n• Collaboration en temps réel\n• Rapports automatisés\n• Intégrations API",
            height=100,
            help="Une fonctionnalité par ligne"
        )
        if features:
            additional_data['features'] = features.strip().split('\n')

        # Screenshots
        st.subheader("📸 Captures d'écran")
        num_screenshots = st.number_input(
            "Nombre de captures d'écran",
            min_value=0,
            max_value=10,
            value=3
        )

        screenshots = []
        for i in range(num_screenshots):
            screenshot_url = st.text_input(
                f"URL capture d'écran {i + 1}",
                key=f"screenshot_{i}",
                placeholder=f"{website}/screenshots/screen{i + 1}.png"
            )
            if screenshot_url:
                screenshots.append(screenshot_url)

        if screenshots:
            additional_data['screenshots'] = screenshots

        # Support et documentation
        st.subheader("📚 Support et documentation")
        col1, col2 = st.columns(2)

        with col1:
            additional_data['documentation_url'] = st.text_input(
                "URL documentation",
                placeholder=f"{website}/docs"
            )

            additional_data['support_url'] = st.text_input(
                "URL support",
                placeholder=f"{website}/support"
            )

        with col2:
            additional_data['privacy_policy_url'] = st.text_input(
                "Politique de confidentialité",
                placeholder=f"{website}/privacy"
            )

            additional_data['terms_url'] = st.text_input(
                "Conditions d'utilisation",
                placeholder=f"{website}/terms"
            )

        # Permissions requises (pour apps mobiles)
        if any(os in additional_data.get('operating_systems', []) for os in ['iOS', 'Android']):
            st.subheader("🔒 Permissions requises")
            permissions = st.multiselect(
                "Permissions de l'application",
                ["Caméra", "Microphone", "Localisation", "Contacts", "Calendrier",
                 "Photos", "Notifications", "Stockage", "Réseau", "Bluetooth"],
                help="Permissions requises pour le fonctionnement"
            )
            if permissions:
                additional_data['permissions'] = permissions

    return additional_data


def render_review_form():
    """Formulaire pour Review"""
    additional_data = {}

    with st.expander("⭐ Informations de l'avis"):
        # Type d'élément évalué
        review_type = st.selectbox(
            "Type d'élément évalué",
            ["Product", "Service", "LocalBusiness", "Restaurant", "Event", "Book", "Movie", "Course", "Other"],
            help="Quel type d'élément est évalué dans cet avis"
        )
        additional_data['review_type'] = review_type

        col1, col2 = st.columns(2)

        with col1:
            # Élément évalué
            additional_data['item_name'] = st.text_input(
                "Nom de l'élément évalué",
                help="Nom du produit, service, entreprise, etc."
            )

            additional_data['item_url'] = st.text_input(
                "URL de l'élément (optionnel)",
                placeholder="https://example.com/product",
                help="Lien vers l'élément évalué"
            )

            # Auteur de l'avis
            st.subheader("👤 Auteur de l'avis")
            author_type = st.radio(
                "Type d'auteur",
                ["Person", "Organization"],
                horizontal=True
            )
            additional_data['author_type'] = author_type

            additional_data['author_name'] = st.text_input(
                "Nom de l'auteur",
                help="Nom de la personne ou organisation qui a écrit l'avis"
            )

            if author_type == "Person":
                additional_data['author_url'] = st.text_input(
                    "Profil de l'auteur (optionnel)",
                    placeholder="https://example.com/profile/john-doe"
                )

        with col2:
            # Note et évaluation
            st.subheader("📊 Évaluation")

            rating_scale = st.selectbox(
                "Échelle de notation",
                ["1-5", "1-10", "1-100"],
                help="Échelle utilisée pour la notation"
            )

            if rating_scale == "1-5":
                best_rating = 5
                worst_rating = 1
                max_val = 5
            elif rating_scale == "1-10":
                best_rating = 10
                worst_rating = 1
                max_val = 10
            else:  # 1-100
                best_rating = 100
                worst_rating = 1
                max_val = 100

            additional_data['rating_value'] = st.slider(
                "Note attribuée",
                min_value=worst_rating,
                max_value=best_rating,
                value=int(best_rating * 0.8),
                help="Note donnée dans l'avis"
            )

            additional_data['best_rating'] = best_rating
            additional_data['worst_rating'] = worst_rating

            # Date de l'avis
            review_date = st.date_input(
                "Date de l'avis",
                help="Date de publication de l'avis"
            )
            if review_date:
                additional_data['date_published'] = review_date.isoformat()

        # Corps de l'avis
        st.subheader("📝 Contenu de l'avis")

        additional_data['review_headline'] = st.text_input(
            "Titre de l'avis (optionnel)",
            placeholder="Excellent produit, je recommande !",
            help="Titre court résumant l'avis"
        )

        additional_data['review_body'] = st.text_area(
            "Texte de l'avis",
            height=150,
            placeholder="Description détaillée de l'expérience avec le produit/service...",
            help="Contenu complet de l'avis"
        )

        # Aspects évalués (optionnel)
        include_aspects = st.checkbox("Inclure des aspects spécifiques évalués")
        if include_aspects:
            st.subheader("🎯 Aspects évalués")
            num_aspects = st.number_input(
                "Nombre d'aspects",
                min_value=1,
                max_value=5,
                value=2
            )

            aspects = []
            for i in range(num_aspects):
                col1, col2, col3 = st.columns(3)

                with col1:
                    aspect_name = st.text_input(
                        f"Aspect {i + 1}",
                        placeholder="Qualité",
                        key=f"aspect_name_{i}"
                    )

                with col2:
                    aspect_rating = st.slider(
                        f"Note",
                        min_value=worst_rating,
                        max_value=best_rating,
                        value=int(best_rating * 0.8),
                        key=f"aspect_rating_{i}"
                    )

                with col3:
                    aspect_comment = st.text_input(
                        f"Commentaire",
                        placeholder="Très bonne qualité",
                        key=f"aspect_comment_{i}"
                    )

                if aspect_name:
                    aspects.append({
                        'name': aspect_name,
                        'rating': aspect_rating,
                        'comment': aspect_comment
                    })

            if aspects:
                additional_data['review_aspects'] = aspects

        # Recommandation
        col1, col2 = st.columns(2)

        with col1:
            would_recommend = st.selectbox(
                "Recommanderiez-vous ?",
                ["", "Oui", "Non", "Peut-être"],
                help="L'auteur recommande-t-il cet élément ?"
            )
            if would_recommend:
                additional_data['would_recommend'] = would_recommend

        with col2:
            # Tags/Catégories
            review_tags = st.text_input(
                "Tags/Catégories (optionnel)",
                placeholder="excellent, rapport qualité-prix, recommandé",
                help="Mots-clés séparés par des virgules"
            )
            if review_tags:
                additional_data['review_tags'] = review_tags.split(',')

        # Images de l'avis (optionnel)
        include_images = st.checkbox("Inclure des images dans l'avis")
        if include_images:
            num_images = st.number_input(
                "Nombre d'images",
                min_value=1,
                max_value=5,
                value=1
            )

            images = []
            for i in range(num_images):
                img_url = st.text_input(
                    f"URL image {i + 1}",
                    key=f"review_img_{i}",
                    placeholder="https://example.com/review-photo.jpg"
                )
                if img_url:
                    images.append(img_url)

            if images:
                additional_data['review_images'] = images

    return additional_data


def render_aggregate_rating_form():
    """Formulaire pour AggregateRating"""
    additional_data = {}

    with st.expander("📊 Évaluation globale (AggregateRating)"):
        st.info("L'AggregateRating représente la moyenne de plusieurs avis pour un même élément")

        col1, col2 = st.columns(2)

        with col1:
            # Élément évalué
            st.subheader("🎯 Élément évalué")

            rating_target_type = st.selectbox(
                "Type d'élément",
                ["Product", "Service", "LocalBusiness", "Restaurant", "Event",
                 "Book", "Movie", "Course", "Recipe", "SoftwareApplication", "Other"],
                help="Type d'élément qui reçoit cette note globale"
            )
            additional_data['target_type'] = rating_target_type

            additional_data['target_name'] = st.text_input(
                "Nom de l'élément",
                help="Nom du produit, service, etc. qui est évalué"
            )

            additional_data['target_url'] = st.text_input(
                "URL de l'élément (optionnel)",
                placeholder="https://example.com/product"
            )

        with col2:
            # Statistiques de notation
            st.subheader("📈 Statistiques")

            # Échelle de notation
            rating_scale = st.selectbox(
                "Échelle de notation",
                ["1-5 étoiles", "1-10 points", "1-100 pourcent", "Personnalisée"],
                help="Système de notation utilisé"
            )

            if rating_scale == "1-5 étoiles":
                best = 5
                worst = 1
            elif rating_scale == "1-10 points":
                best = 10
                worst = 1
            elif rating_scale == "1-100 pourcent":
                best = 100
                worst = 0
            else:  # Personnalisée
                col_a, col_b = st.columns(2)
                with col_a:
                    worst = st.number_input(
                        "Note minimale",
                        value=1,
                        min_value=0
                    )
                with col_b:
                    best = st.number_input(
                        "Note maximale",
                        value=5,
                        min_value=worst + 1
                    )

            additional_data['best_rating'] = best
            additional_data['worst_rating'] = worst

            # Note moyenne
            additional_data['rating_value'] = st.number_input(
                "Note moyenne",
                min_value=float(worst),
                max_value=float(best),
                value=float(worst + (best - worst) * 0.8),
                step=0.1,
                format="%.1f",
                help="Moyenne des notes reçues"
            )

            # Nombre d'avis
            additional_data['review_count'] = st.number_input(
                "Nombre d'avis",
                min_value=1,
                value=10,
                help="Nombre total d'avis utilisés pour calculer la moyenne"
            )

            # Nombre de notations (optionnel, peut différer du nombre d'avis)
            include_rating_count = st.checkbox("Spécifier le nombre de notations séparément")
            if include_rating_count:
                additional_data['rating_count'] = st.number_input(
                    "Nombre de notations",
                    min_value=1,
                    value=additional_data['review_count'],
                    help="Nombre total de personnes ayant noté (peut différer du nombre d'avis écrits)"
                )

        # Distribution des notes (optionnel mais recommandé)
        include_distribution = st.checkbox("Inclure la distribution des notes")
        if include_distribution:
            st.subheader("📊 Distribution des notes")
            st.caption("Répartition des notes par niveau (améliore l'affichage dans Google)")

            distribution = {}
            total_ratings = 0

            if rating_scale == "1-5 étoiles":
                cols = st.columns(5)
                for i, col in enumerate(cols, 1):
                    with col:
                        count = st.number_input(
                            f"{i} ⭐",
                            min_value=0,
                            value=0,
                            key=f"dist_{i}"
                        )
                        if count > 0:
                            distribution[str(i)] = count
                            total_ratings += count
            else:
                # Pour autres échelles, diviser en 5 groupes
                ranges = []
                step = (best - worst) / 5
                for i in range(5):
                    range_min = worst + (i * step)
                    range_max = worst + ((i + 1) * step)
                    ranges.append((range_min, range_max))

                cols = st.columns(5)
                for i, (col, (r_min, r_max)) in enumerate(zip(cols, ranges)):
                    with col:
                        label = f"{r_min:.0f}-{r_max:.0f}"
                        count = st.number_input(
                            label,
                            min_value=0,
                            value=0,
                            key=f"dist_range_{i}"
                        )
                        if count > 0:
                            distribution[label] = count
                            total_ratings += count

            if distribution:
                additional_data['rating_distribution'] = distribution

                # Vérifier la cohérence
                if total_ratings != additional_data.get('rating_count', additional_data['review_count']):
                    st.warning(
                        f"⚠️ La somme de la distribution ({total_ratings}) ne correspond pas au nombre total de notations ({additional_data.get('rating_count', additional_data['review_count'])})")

        # Informations supplémentaires
        st.subheader("ℹ️ Informations supplémentaires")

        col1, col2 = st.columns(2)

        with col1:
            # Source des avis
            review_source = st.text_input(
                "Source des avis (optionnel)",
                placeholder="Google Reviews, Trustpilot, etc.",
                help="Plateforme ou source des avis"
            )
            if review_source:
                additional_data['review_source'] = review_source

            # URL de la page d'avis
            reviews_url = st.text_input(
                "URL de la page d'avis (optionnel)",
                placeholder="https://example.com/reviews",
                help="Lien vers la page contenant tous les avis"
            )
            if reviews_url:
                additional_data['reviews_url'] = reviews_url

        with col2:
            # Date de mise à jour
            last_updated = st.date_input(
                "Dernière mise à jour",
                help="Date de la dernière mise à jour de la note globale"
            )
            if last_updated:
                additional_data['last_updated'] = last_updated.isoformat()

            # Période couverte
            include_period = st.checkbox("Spécifier la période des avis")
            if include_period:
                col_a, col_b = st.columns(2)
                with col_a:
                    period_start = st.date_input(
                        "Du",
                        key="period_start"
                    )
                with col_b:
                    period_end = st.date_input(
                        "Au",
                        key="period_end"
                    )

                if period_start and period_end:
                    additional_data['review_period'] = {
                        'start': period_start.isoformat(),
                        'end': period_end.isoformat()
                    }

    return additional_data

def render_social_networks_form():
    """Formulaire pour les réseaux sociaux"""
    with st.expander("🌐 Réseaux sociaux"):
        st.caption("Ajoutez vos profils sociaux pour améliorer votre Knowledge Graph")

        social_profiles = []
        social_networks = [
            ("Facebook", "https://facebook.com/"),
            ("LinkedIn", "https://linkedin.com/company/"),
            ("Twitter/X", "https://twitter.com/"),
            ("Instagram", "https://instagram.com/"),
            ("YouTube", "https://youtube.com/@"),
            ("TikTok", "https://tiktok.com/@"),
            ("Pinterest", "https://pinterest.com/")
        ]

        cols = st.columns(2)
        for i, (network, base_url) in enumerate(social_networks):
            with cols[i % 2]:
                profile = st.text_input(
                    network,
                    placeholder=f"{base_url}...",
                    key=f"social_{network}"
                )
                if profile:
                    social_profiles.append(profile)

        return social_profiles