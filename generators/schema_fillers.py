"""
Classes spécialisées pour remplir chaque type de schema
Version corrigée avec détection intelligente des types pour Review et AggregateRating
"""
from typing import Dict, Optional, List
from datetime import datetime


class SchemaFillerBase:
    """Classe de base pour les fillers de schemas"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        """Méthode de base pour remplir un schema"""
        # Remplir les champs communs
        if 'name' in schema and schema['name'] == "":
            schema['name'] = client_info.get('company_name', '')
        if 'url' in schema and schema['url'] == "":
            schema['url'] = client_info.get('website', '')
        if 'description' in schema and schema['description'] == "":
            schema['description'] = client_info.get('description', '')


class OrganizationFiller(SchemaFillerBase):
    """Filler pour les schemas Organization"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Logo
        if 'logo' in additional_data and additional_data['logo']:
            if isinstance(schema.get('logo'), dict):
                schema['logo']['url'] = additional_data['logo']
                # S'assurer que les dimensions sont présentes
                if 'width' not in schema['logo']:
                    schema['logo']['width'] = 300
                if 'height' not in schema['logo']:
                    schema['logo']['height'] = 300
            else:
                schema['logo'] = {
                    "@type": "ImageObject",
                    "url": additional_data['logo'],
                    "width": 300,
                    "height": 300
                }

        # Adresse complète
        if 'address' in additional_data and isinstance(additional_data['address'], dict):
            if isinstance(schema.get('address'), dict):
                for key, value in additional_data['address'].items():
                    if key in schema['address'] and value:
                        schema['address'][key] = value

        # Points de contact
        if 'contact_points' in additional_data and additional_data['contact_points']:
            schema['contactPoint'] = []
            for contact in additional_data['contact_points']:
                contact_point = {
                    "@type": "ContactPoint",
                    "contactType": contact.get('type', 'customer service')
                }

                # Ajouter uniquement les champs non vides
                if contact.get('telephone'):
                    contact_point['telephone'] = contact['telephone']
                if contact.get('email'):
                    contact_point['email'] = contact['email']
                if contact.get('area_served'):
                    contact_point['areaServed'] = contact['area_served']
                if contact.get('languages'):
                    contact_point['availableLanguage'] = contact['languages']

                schema['contactPoint'].append(contact_point)

        # Identifiants d'entreprise - remplir seulement si non vides
        for field in ['legalName', 'taxID', 'vatID', 'naics', 'duns']:
            if field in additional_data and additional_data[field]:
                schema[field] = additional_data[field]

        # Réseaux sociaux
        if 'social_media' in additional_data and additional_data['social_media']:
            schema['sameAs'] = additional_data['social_media']

        # Nombre d'employés
        if 'employee_count' in additional_data and additional_data['employee_count'] > 0:
            if isinstance(schema.get('numberOfEmployees'), dict):
                schema['numberOfEmployees']['value'] = str(additional_data['employee_count'])
            else:
                schema['numberOfEmployees'] = {
                    "@type": "QuantitativeValue",
                    "value": str(additional_data['employee_count'])
                }

        # Date de fondation
        if 'foundingDate' in additional_data and additional_data['foundingDate']:
            schema['foundingDate'] = additional_data['foundingDate']

        # Slogan
        if 'slogan' in additional_data and additional_data['slogan']:
            schema['slogan'] = additional_data['slogan']

        # Téléphone et email directs (en plus des points de contact)
        if 'telephone' in additional_data and additional_data['telephone']:
            schema['telephone'] = additional_data['telephone']
        if 'email' in additional_data and additional_data['email']:
            schema['email'] = additional_data['email']
        if 'faxNumber' in additional_data and additional_data['faxNumber']:
            schema['faxNumber'] = additional_data['faxNumber']


class LocalBusinessFiller(OrganizationFiller):
    """Filler pour les schemas LocalBusiness"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        # Appeler d'abord le filler Organization
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Coordonnées géographiques
        if 'geo' in additional_data and 'geo' in schema and isinstance(schema['geo'], dict):
            if 'lat' in additional_data['geo'] and additional_data['geo']['lat']:
                schema['geo']['latitude'] = str(additional_data['geo']['lat'])
            if 'lng' in additional_data['geo'] and additional_data['geo']['lng']:
                schema['geo']['longitude'] = str(additional_data['geo']['lng'])

        # Horaires détaillés
        if 'opening_hours' in additional_data and additional_data['opening_hours']:
            schema['openingHoursSpecification'] = []
            for hours in additional_data['opening_hours']:
                spec = {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": hours.get('days', []),
                    "opens": hours.get('opens', ''),
                    "closes": hours.get('closes', '')
                }
                if 'validFrom' in hours and hours['validFrom']:
                    spec['validFrom'] = hours['validFrom']
                if 'validThrough' in hours and hours['validThrough']:
                    spec['validThrough'] = hours['validThrough']
                schema['openingHoursSpecification'].append(spec)

        # Commerce
        if 'price_range' in additional_data and additional_data['price_range']:
            schema['priceRange'] = additional_data['price_range']
        if 'payment_accepted' in additional_data and additional_data['payment_accepted']:
            schema['paymentAccepted'] = additional_data['payment_accepted']
        if 'currencies_accepted' in additional_data and additional_data['currencies_accepted']:
            schema['currenciesAccepted'] = additional_data['currencies_accepted']

        # S'assurer que telephone et email sont présents
        if 'telephone' in additional_data and additional_data['telephone']:
            schema['telephone'] = additional_data['telephone']
        if 'email' in additional_data and additional_data['email']:
            schema['email'] = additional_data['email']


class RestaurantFiller(LocalBusinessFiller):
    """Filler pour les schemas Restaurant"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Spécifique restaurant
        if 'cuisines' in additional_data and additional_data['cuisines']:
            schema['servesCuisine'] = additional_data['cuisines']
        if 'menu_url' in additional_data and additional_data['menu_url']:
            schema['hasMenu'] = additional_data['menu_url']
        if 'accepts_reservations' in additional_data:
            schema['acceptsReservations'] = additional_data['accepts_reservations']


class ProductFiller(SchemaFillerBase):
    """Filler pour les schemas Product"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Identification produit
        for field in ['sku', 'gtin', 'gtin13', 'mpn', 'product_name']:
            if field in additional_data and additional_data[field]:
                target_field = 'name' if field == 'product_name' else field
                schema[target_field] = additional_data[field]

        # Marque
        if 'brand' in schema and isinstance(schema['brand'], dict):
            schema['brand']['name'] = client_info.get('company_name', '')
            if 'brand_name' in additional_data and additional_data['brand_name']:
                schema['brand']['name'] = additional_data['brand_name']

        # Caractéristiques physiques
        for field in ['size', 'color', 'material']:
            if field in additional_data and additional_data[field]:
                schema[field] = additional_data[field]

        # Dimensions avec unités
        for dim in ['weight', 'width', 'height', 'depth']:
            if f"{dim}_value" in additional_data and additional_data[f"{dim}_value"]:
                if dim in schema and isinstance(schema[dim], dict):
                    schema[dim]['value'] = additional_data[f"{dim}_value"]
                    schema[dim]['unitCode'] = additional_data.get(f"{dim}_unit", "CMT")

        # Offres
        if 'offers' in schema and isinstance(schema['offers'], dict):
            if 'price' in additional_data and additional_data['price']:
                schema['offers']['price'] = additional_data['price']
            if 'currency' in additional_data and additional_data['currency']:
                schema['offers']['priceCurrency'] = additional_data['currency']
            if 'availability' in additional_data and additional_data['availability']:
                schema['offers']['availability'] = additional_data['availability']
            if 'price_valid_until' in additional_data and additional_data['price_valid_until']:
                schema['offers']['priceValidUntil'] = additional_data['price_valid_until']

            # Vendeur
            if 'seller' in schema['offers'] and isinstance(schema['offers']['seller'], dict):
                schema['offers']['seller']['name'] = client_info.get('company_name', '')

        # Images multiples
        if 'images' in additional_data and additional_data['images']:
            schema['image'] = additional_data['images']


class ArticleFiller(SchemaFillerBase):
    """Filler pour les schemas Article et ses variantes"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        # Dates
        schema['datePublished'] = datetime.now().isoformat()
        schema['dateModified'] = datetime.now().isoformat()

        # Publisher
        if 'publisher' in schema and isinstance(schema['publisher'], dict):
            schema['publisher']['name'] = client_info.get('company_name', '')

        if not additional_data:
            return

        # Headline et description
        if 'headline' in additional_data and additional_data['headline']:
            schema['headline'] = additional_data['headline']

        # Auteur
        if 'author_name' in additional_data and additional_data['author_name']:
            if 'author' in schema:
                if isinstance(schema['author'], dict):
                    schema['author']['name'] = additional_data['author_name']
                    if 'author_url' in additional_data and additional_data['author_url']:
                        schema['author']['url'] = additional_data['author_url']
                else:
                    schema['author'] = {
                        "@type": "Person",
                        "name": additional_data['author_name']
                    }
                    if 'author_url' in additional_data and additional_data['author_url']:
                        schema['author']['url'] = additional_data['author_url']

        # Publisher logo
        if 'publisher_logo' in additional_data and additional_data['publisher_logo']:
            if 'publisher' in schema and isinstance(schema['publisher'], dict):
                if 'logo' in schema['publisher']:
                    if isinstance(schema['publisher']['logo'], dict):
                        schema['publisher']['logo']['url'] = additional_data['publisher_logo']
                    else:
                        schema['publisher']['logo'] = {
                            "@type": "ImageObject",
                            "url": additional_data['publisher_logo']
                        }

        # Contenu
        if 'article_body' in additional_data and additional_data['article_body']:
            schema['articleBody'] = additional_data['article_body']
            # Calculer le nombre de mots
            schema['wordCount'] = len(additional_data['article_body'].split())

        if 'article_section' in additional_data and additional_data['article_section']:
            schema['articleSection'] = additional_data['article_section']

        if 'keywords' in additional_data and additional_data['keywords']:
            schema['keywords'] = additional_data['keywords']

        # Images multiples formats
        if 'images' in additional_data and additional_data['images']:
            schema['image'] = additional_data['images']


class EventFiller(SchemaFillerBase):
    """Filler pour les schemas Event"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Dates
        if 'start_date' in additional_data and additional_data['start_date']:
            schema['startDate'] = additional_data['start_date']
        if 'end_date' in additional_data and additional_data['end_date']:
            schema['endDate'] = additional_data['end_date']

        # Mode de participation
        if 'attendance_mode' in additional_data and additional_data['attendance_mode']:
            schema['eventAttendanceMode'] = additional_data['attendance_mode']

        # Statut
        if 'event_status' in additional_data and additional_data['event_status']:
            schema['eventStatus'] = additional_data['event_status']

        # Lieu
        if 'location_name' in additional_data and additional_data['location_name']:
            if 'location' in schema and isinstance(schema['location'], dict):
                schema['location']['name'] = additional_data['location_name']
            elif 'location' in schema and isinstance(schema['location'], list) and len(schema['location']) > 0:
                if isinstance(schema['location'][0], dict):
                    schema['location'][0]['name'] = additional_data['location_name']

        # Lieu virtuel pour événements en ligne
        if schema.get('eventAttendanceMode') in ['https://schema.org/OnlineEventAttendanceMode',
                                                 'https://schema.org/MixedEventAttendanceMode']:
            if 'virtual_location_url' in additional_data and additional_data['virtual_location_url']:
                if schema['eventAttendanceMode'] == 'https://schema.org/OnlineEventAttendanceMode':
                    schema['location'] = {
                        "@type": "VirtualLocation",
                        "url": additional_data['virtual_location_url']
                    }
                else:  # Mixed mode
                    if not isinstance(schema.get('location'), list):
                        schema['location'] = [schema.get('location', {
                            "@type": "Place",
                            "name": "",
                            "address": {
                                "@type": "PostalAddress",
                                "streetAddress": "",
                                "addressLocality": "",
                                "addressRegion": "",
                                "postalCode": "",
                                "addressCountry": ""
                            }
                        })]
                    schema['location'].append({
                        "@type": "VirtualLocation",
                        "url": additional_data['virtual_location_url']
                    })

        # Organisateur
        if 'organizer' in schema and isinstance(schema['organizer'], dict):
            if 'organizer_name' in additional_data and additional_data['organizer_name']:
                schema['organizer']['name'] = additional_data['organizer_name']
            if 'organizer_url' in additional_data and additional_data['organizer_url']:
                schema['organizer']['url'] = additional_data['organizer_url']

        # Billetterie
        if 'offers' in schema and isinstance(schema['offers'], dict):
            if 'ticket_price' in additional_data and additional_data['ticket_price']:
                schema['offers']['price'] = additional_data['ticket_price']
            if 'ticket_url' in additional_data and additional_data['ticket_url']:
                schema['offers']['url'] = additional_data['ticket_url']
            if 'ticket_currency' in additional_data and additional_data.get('ticket_price'):
                schema['offers']['priceCurrency'] = additional_data.get('ticket_currency', 'EUR')


class FAQPageFiller(SchemaFillerBase):
    """Filler pour les schemas FAQPage"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        if additional_data and 'questions' in additional_data and additional_data['questions']:
            schema['mainEntity'] = []
            for q in additional_data['questions']:
                if q.get('question') and q.get('answer'):
                    schema['mainEntity'].append({
                        "@type": "Question",
                        "name": q['question'],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": q['answer']
                        }
                    })


class BreadcrumbListFiller(SchemaFillerBase):
    """Filler pour les schemas BreadcrumbList"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        if additional_data and 'breadcrumbs' in additional_data and additional_data['breadcrumbs']:
            schema['itemListElement'] = []
            for i, crumb in enumerate(additional_data['breadcrumbs'], 1):
                if crumb.get('name') and crumb.get('url'):
                    schema['itemListElement'].append({
                        "@type": "ListItem",
                        "position": i,
                        "name": crumb['name'],
                        "item": crumb['url']
                    })


class WebSiteFiller(SchemaFillerBase):
    """Filler pour les schemas WebSite"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        base_url = client_info.get('website', '').rstrip('/')

        # Corriger l'URL du SearchAction et ajouter la référence au publisher
        if 'potentialAction' in schema and isinstance(schema['potentialAction'], dict):
            if 'target' in schema['potentialAction'] and isinstance(schema['potentialAction']['target'], dict):
                schema['potentialAction']['target']['urlTemplate'] = f"{base_url}/search?q={{search_term_string}}"

        # Ajouter la référence au publisher
        if base_url:
            schema['publisher'] = {
                "@id": f"{base_url}#organization"
            }
            schema['@id'] = f"{base_url}#website"

        if additional_data and 'search_url_template' in additional_data and additional_data['search_url_template']:
            if 'potentialAction' in schema and isinstance(schema['potentialAction'], dict):
                if 'target' in schema['potentialAction'] and isinstance(schema['potentialAction']['target'], dict):
                    schema['potentialAction']['target']['urlTemplate'] = additional_data['search_url_template']


class HowToFiller(SchemaFillerBase):
    """Filler pour les schemas HowTo"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        if 'howto_name' in additional_data and additional_data['howto_name']:
            schema['name'] = additional_data['howto_name']

        if 'total_time' in additional_data and additional_data['total_time']:
            schema['totalTime'] = additional_data['total_time']

        if 'estimated_cost' in additional_data and isinstance(additional_data['estimated_cost'], dict):
            if additional_data['estimated_cost'].get('value'):
                schema['estimatedCost'] = {
                    "@type": "MonetaryAmount",
                    "currency": additional_data['estimated_cost'].get('currency', 'EUR'),
                    "value": additional_data['estimated_cost']['value']
                }

        if 'tools' in additional_data and additional_data['tools']:
            schema['tool'] = [{"@type": "HowToTool", "name": tool} for tool in additional_data['tools']]

        if 'supplies' in additional_data and additional_data['supplies']:
            schema['supply'] = [{"@type": "HowToSupply", "name": supply} for supply in additional_data['supplies']]

        if 'steps' in additional_data and additional_data['steps']:
            schema['step'] = []
            for step_data in additional_data['steps']:
                step = {
                    "@type": "HowToStep",
                    "position": step_data.get('position', 1),
                    "name": step_data.get('name', ''),
                    "text": step_data.get('text', '')
                }
                if 'image' in step_data and step_data['image']:
                    step['image'] = step_data['image']
                schema['step'].append(step)


class PersonFiller(SchemaFillerBase):
    """Filler pour les schemas Person"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        # IMPORTANT: Ne PAS appeler super().fill() pour Person
        # car on ne veut pas que le nom de la personne soit remplacé par celui de l'entreprise

        if not additional_data:
            return

        # Construire le nom complet de la PERSONNE
        full_name_parts = []

        if 'given_name' in additional_data and additional_data['given_name']:
            schema['givenName'] = additional_data['given_name']
            full_name_parts.append(additional_data['given_name'])

        if 'family_name' in additional_data and additional_data['family_name']:
            schema['familyName'] = additional_data['family_name']
            full_name_parts.append(additional_data['family_name'])

        # Définir le nom complet
        if full_name_parts:
            schema['name'] = ' '.join(full_name_parts)
        elif 'person_name' in additional_data and additional_data['person_name']:
            schema['name'] = additional_data['person_name']
        # Si aucun nom fourni, laisser vide plutôt que d'utiliser le nom de l'entreprise

        # Informations professionnelles
        if 'job_title' in additional_data and additional_data['job_title']:
            schema['jobTitle'] = additional_data['job_title']

        if 'works_for' in additional_data and additional_data['works_for']:
            if 'worksFor' in schema and isinstance(schema['worksFor'], dict):
                schema['worksFor']['name'] = additional_data['works_for']
            else:
                schema['worksFor'] = {
                    "@type": "Organization",
                    "name": additional_data['works_for']
                }

        # Contact
        if 'email' in additional_data and additional_data['email']:
            schema['email'] = additional_data['email']

        if 'telephone' in additional_data and additional_data['telephone']:
            schema['telephone'] = additional_data['telephone']

        if 'image' in additional_data and additional_data['image']:
            schema['image'] = additional_data['image']

        # URL personnelle (pas celle de l'entreprise)
        if 'person_url' in additional_data and additional_data['person_url']:
            schema['url'] = additional_data['person_url']
        elif 'url' in schema:
            # Si pas d'URL personnelle fournie, supprimer l'URL
            del schema['url']

        # Réseaux sociaux de la personne
        if 'social_media' in additional_data and additional_data['social_media']:
            schema['sameAs'] = additional_data['social_media']

        # Adresse (optionnelle pour une personne)
        if 'person_address' in additional_data and additional_data['person_address']:
            schema['address'] = additional_data['person_address']
        elif 'address' in schema:
            # Si pas d'adresse personnelle, supprimer
            del schema['address']

        # Description personnelle
        if 'person_description' in additional_data and additional_data['person_description']:
            schema['description'] = additional_data['person_description']
        elif 'description' in schema:
            # Supprimer la description de l'entreprise si pas de description personnelle
            del schema['description']

class JobPostingFiller(SchemaFillerBase):
    """Filler pour les schemas JobPosting"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        if 'job_title' in additional_data and additional_data['job_title']:
            schema['title'] = additional_data['job_title']

        if 'job_description' in additional_data and additional_data['job_description']:
            schema['description'] = additional_data['job_description']

        if 'date_posted' in additional_data and additional_data['date_posted']:
            schema['datePosted'] = additional_data['date_posted']

        if 'valid_through' in additional_data and additional_data['valid_through']:
            schema['validThrough'] = additional_data['valid_through']

        if 'employment_types' in additional_data and additional_data['employment_types']:
            schema['employmentType'] = additional_data['employment_types']

        # Organisation
        if 'hiringOrganization' in schema and isinstance(schema['hiringOrganization'], dict):
            schema['hiringOrganization']['name'] = client_info.get('company_name', '')
            if client_info.get('website'):
                schema['hiringOrganization']['sameAs'] = client_info['website']

        # Salaire
        if 'salary' in additional_data and isinstance(additional_data['salary'], dict):
            if 'baseSalary' in schema and isinstance(schema['baseSalary'], dict):
                schema['baseSalary']['currency'] = additional_data['salary'].get('currency', 'EUR')

                min_salary = additional_data['salary'].get('min', '')
                max_salary = additional_data['salary'].get('max', '')

                if min_salary or max_salary:
                    if 'value' in schema['baseSalary']:
                        if min_salary and max_salary:
                            schema['baseSalary']['value'] = {
                                "@type": "QuantitativeValue",
                                "minValue": min_salary,
                                "maxValue": max_salary,
                                "unitText": "YEAR"
                            }
                        else:
                            schema['baseSalary']['value'] = {
                                "@type": "QuantitativeValue",
                                "value": min_salary or max_salary,
                                "unitText": "YEAR"
                            }


class ServiceFiller(SchemaFillerBase):
    """Filler pour les schemas Service - SANS reviews intégrées"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Service spécifique
        if 'service_name' in additional_data and additional_data['service_name']:
            schema['name'] = additional_data['service_name']

        if 'service_type' in additional_data and additional_data['service_type']:
            schema['serviceType'] = additional_data['service_type']

        if 'service_description' in additional_data and additional_data['service_description']:
            schema['description'] = additional_data['service_description']

        # Provider
        if 'provider' in schema and isinstance(schema['provider'], dict):
            schema['provider']['name'] = client_info.get('company_name', '')
            if client_info.get('website'):
                schema['provider']['@id'] = f"{client_info['website'].rstrip('/')}#organization"

        # Zone de service
        if 'area_served' in additional_data and additional_data['area_served']:
            if len(additional_data['area_served']) == 1:
                schema['areaServed'] = {
                    "@type": "Place",
                    "name": additional_data['area_served'][0]
                }
            else:
                schema['areaServed'] = [
                    {"@type": "Place", "name": area}
                    for area in additional_data['area_served']
                ]

        # Audience (public cible)
        if 'audience_type' in additional_data and additional_data['audience_type']:
            schema['audience'] = {
                "@type": "Audience",
                "audienceType": additional_data['audience_type']
            }

        # Catalogue d'offres
        if 'offers_catalog' in additional_data and additional_data['offers_catalog']:
            schema['hasOfferCatalog'] = {
                "@type": "OfferCatalog",
                "name": f"Catalogue {additional_data.get('service_name', 'Services')}",
                "itemListElement": []
            }

            for offer in additional_data['offers_catalog']:
                offer_item = {
                    "@type": "Offer",
                    "name": offer.get('name', ''),
                    "description": offer.get('description', '')
                }
                if offer.get('price'):
                    # Gérer les prix qui peuvent être des strings comme "1000€" ou "À partir de 500€"
                    price_str = offer['price']
                    # Essayer d'extraire juste le nombre
                    import re
                    price_match = re.search(r'\d+', price_str)
                    if price_match:
                        offer_item['price'] = price_match.group()
                        offer_item['priceCurrency'] = 'EUR'
                    else:
                        # Si pas de nombre trouvé, mettre le texte tel quel
                        offer_item['priceSpecification'] = {
                            "@type": "PriceSpecification",
                            "price": price_str,
                            "priceCurrency": "EUR"
                        }

                schema['hasOfferCatalog']['itemListElement'].append(offer_item)

        # Caractéristiques supplémentaires
        if 'price_range' in additional_data and additional_data['price_range']:
            schema['priceRange'] = additional_data['price_range']

        if 'availability' in additional_data and additional_data['availability']:
            # Mapper vers les valeurs Schema.org si possible
            availability_mapping = {
                "Immédiate": "https://schema.org/InStock",
                "Sous 24h": "https://schema.org/InStock",
                "Sous 48h": "https://schema.org/InStock",
                "Sur rendez-vous": "https://schema.org/PreOrder",
                "Selon planning": "https://schema.org/PreOrder"
            }
            schema['availability'] = availability_mapping.get(
                additional_data['availability'],
                additional_data['availability']
            )

        if 'service_duration' in additional_data and additional_data['service_duration']:
            # Essayer de convertir en format ISO 8601 si possible
            duration = additional_data['service_duration']
            # Pour l'instant, on le met tel quel, mais on pourrait parser "3 mois" -> "P3M"
            schema['duration'] = duration

        if 'delivery_method' in additional_data and additional_data['delivery_method']:
            schema['availableChannel'] = {
                "@type": "ServiceChannel",
                "serviceChannelType": ", ".join(additional_data['delivery_method'])
            }

        if 'certifications' in additional_data and additional_data['certifications']:
            # Les certifications arrivent comme une liste
            if isinstance(additional_data['certifications'], list):
                schema['award'] = additional_data['certifications']
            else:
                schema['award'] = [additional_data['certifications']]

        if 'guarantees' in additional_data and additional_data['guarantees']:
            schema['termsOfService'] = additional_data['guarantees']

        if 'process_steps' in additional_data and additional_data['process_steps']:
            # Les étapes arrivent comme une liste
            if isinstance(additional_data['process_steps'], list):
                # Nettoyer les étapes (enlever les numéros si présents)
                clean_steps = []
                for step in additional_data['process_steps']:
                    # Enlever les numéros du début (1., 2., etc.)
                    import re
                    clean_step = re.sub(r'^\d+\.\s*', '', step.strip())
                    if clean_step:
                        clean_steps.append(clean_step)

                if clean_steps:
                    schema['serviceOutput'] = {
                        "@type": "Thing",
                        "description": "Processus: " + " → ".join(clean_steps)
                    }
            else:
                schema['serviceOutput'] = {
                    "@type": "Thing",
                    "description": f"Processus: {additional_data['process_steps']}"
                }

        # PLUS DE REVIEWS OU AGGREGATERATING ICI !
        # Les reviews doivent être des schémas séparés sélectionnés dans la liste

class ReviewFiller(SchemaFillerBase):
    """Filler pour les schemas Review avec détection intelligente du type"""

    def __init__(self):
        super().__init__()
        self.context_schemas = []

    def set_context(self, context_schemas: List[str]):
        """Définit le contexte des autres schemas sélectionnés"""
        self.context_schemas = context_schemas

    def _determine_item_type(self, additional_data: Optional[Dict]) -> str:
        """
        Détermine le type approprié pour itemReviewed
        NE JAMAIS retourner 'Thing' !
        """
        # Vérifier si un type explicite est fourni ET qu'il n'est pas 'Thing'
        if additional_data and 'review_type' in additional_data:
            review_type = additional_data['review_type']
            if review_type and review_type != 'Thing':
                return review_type

        # Détecter basé sur le contexte des autres schemas
        if self.context_schemas:
            type_mapping = {
                'Service': 'Service',
                'Product': 'Product',
                'LocalBusiness': 'LocalBusiness',
                'Restaurant': 'Restaurant',
                'Store': 'Store',
                'Organization': 'Organization',
                'Event': 'Event',
                'Course': 'Course',
                'SoftwareApplication': 'SoftwareApplication',
                'Hotel': 'Hotel',
                'Book': 'Book',
                'Movie': 'Movie'
            }

            for schema_type in self.context_schemas:
                if schema_type in type_mapping:
                    return type_mapping[schema_type]

        # Détecter basé sur les données
        if additional_data:
            if 'service_name' in additional_data or 'service_type' in additional_data:
                return 'Service'
            elif 'product_name' in additional_data or 'product_sku' in additional_data:
                return 'Product'
            elif 'organization_type' in additional_data:
                return 'Organization'
            elif 'local_business_type' in additional_data:
                return 'LocalBusiness'
            elif 'item_name' in additional_data or 'itemreviewed_name' in additional_data:
                # Essayer de déduire du nom
                item_name = (additional_data.get('item_name') or
                             additional_data.get('itemreviewed_name', '')).lower()
                if any(word in item_name for word in ['service', 'consulting', 'agency', 'agence', 'marketing']):
                    return 'Service'
                elif any(word in item_name for word in ['product', 'produit', 'item']):
                    return 'Product'
                elif any(word in item_name for word in ['restaurant', 'café', 'bistro']):
                    return 'Restaurant'

        # Par défaut pour une agence ou entreprise de services
        return 'Service'

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        # TOUJOURS corriger le type, même sans données additionnelles
        if 'itemReviewed' not in schema:
            schema['itemReviewed'] = {}

        # Déterminer le type approprié (JAMAIS Thing)
        item_type = self._determine_item_type(additional_data)

        # FORCER le type correct
        schema['itemReviewed']['@type'] = item_type

        if not additional_data:
            # Même sans données, on met les valeurs par défaut
            schema['itemReviewed']['name'] = client_info.get('company_name', 'Service')
            if client_info.get('website'):
                schema['itemReviewed']['url'] = client_info['website']
            return

        # Nom de l'élément évalué
        item_name = (
                additional_data.get('item_name') or
                additional_data.get('itemreviewed_name') or
                additional_data.get('service_name') or
                additional_data.get('product_name') or
                client_info.get('company_name', 'Service')
        )
        schema['itemReviewed']['name'] = item_name

        # URL de l'élément
        item_url = (
                additional_data.get('item_url') or
                additional_data.get('itemreviewed_url') or
                client_info.get('website', '')
        )
        if item_url:
            schema['itemReviewed']['url'] = item_url

        # Auteur de l'avis
        if 'author_name' in additional_data and additional_data['author_name']:
            author_type = additional_data.get('author_type', 'Person')

            if 'author' not in schema or not isinstance(schema['author'], dict):
                schema['author'] = {"@type": author_type}

            schema['author']['name'] = additional_data['author_name']

            if author_type == 'Person' and 'author_url' in additional_data and additional_data['author_url']:
                schema['author']['url'] = additional_data['author_url']

        # Date de publication
        if 'date_published' in additional_data and additional_data['date_published']:
            schema['datePublished'] = additional_data['date_published']
        else:
            schema['datePublished'] = datetime.now().isoformat()

        # Titre et corps de l'avis
        if 'review_headline' in additional_data and additional_data['review_headline']:
            schema['headline'] = additional_data['review_headline']

        if 'review_body' in additional_data and additional_data['review_body']:
            schema['reviewBody'] = additional_data['review_body']

        # Note
        if 'rating_value' in additional_data:
            if 'reviewRating' not in schema or not isinstance(schema['reviewRating'], dict):
                schema['reviewRating'] = {"@type": "Rating"}

            schema['reviewRating']['ratingValue'] = str(additional_data['rating_value'])
            schema['reviewRating']['bestRating'] = str(additional_data.get('best_rating', 5))
            schema['reviewRating']['worstRating'] = str(additional_data.get('worst_rating', 1))

        # Aspects évalués (structure personnalisée)
        if 'review_aspects' in additional_data and additional_data['review_aspects']:
            schema['reviewAspect'] = []
            for aspect in additional_data['review_aspects']:
                aspect_item = {
                    "@type": "PropertyValue",
                    "name": aspect['name'],
                    "value": aspect['rating']
                }
                if aspect.get('comment'):
                    aspect_item['description'] = aspect['comment']
                schema['reviewAspect'].append(aspect_item)

        # Recommandation
        if 'would_recommend' in additional_data and additional_data['would_recommend']:
            if additional_data['would_recommend'] == 'Oui':
                schema['positiveNotes'] = {"@type": "ItemList", "itemListElement": ["Recommandé"]}
            elif additional_data['would_recommend'] == 'Non':
                schema['negativeNotes'] = {"@type": "ItemList", "itemListElement": ["Non recommandé"]}

        # Tags
        if 'review_tags' in additional_data and additional_data['review_tags']:
            schema['keywords'] = ", ".join([tag.strip() for tag in additional_data['review_tags']])

        # Images
        if 'review_images' in additional_data and additional_data['review_images']:
            schema['associatedMedia'] = []
            for img_url in additional_data['review_images']:
                schema['associatedMedia'].append({
                    "@type": "ImageObject",
                    "url": img_url
                })

        # Publisher (si pas déjà défini)
        if 'publisher' not in schema or not schema['publisher']:
            schema['publisher'] = {
                "@type": "Organization",
                "name": client_info.get('company_name', 'Website')
            }


class AggregateRatingFiller(SchemaFillerBase):
    """Filler pour les schemas AggregateRating avec type correct"""

    def __init__(self):
        super().__init__()
        self.context_schemas = []

    def set_context(self, context_schemas: List[str]):
        """Définit le contexte des autres schemas sélectionnés"""
        self.context_schemas = context_schemas

    def _determine_item_type(self, additional_data: Optional[Dict]) -> str:
        """Détermine le type approprié - JAMAIS Thing"""
        # Vérifier le type explicite
        if additional_data and 'target_type' in additional_data:
            target_type = additional_data['target_type']
            if target_type and target_type != 'Thing':
                return target_type

        # Vérifier le contexte
        if self.context_schemas:
            for schema_type in ['Service', 'Product', 'LocalBusiness', 'Organization',
                                'Restaurant', 'Store', 'Event', 'Course']:
                if schema_type in self.context_schemas:
                    return schema_type

        # Par défaut
        return 'Service'

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        if not additional_data:
            return

        # Note moyenne et nombre d'avis (champs requis)
        if 'rating_value' in additional_data:
            schema['ratingValue'] = str(additional_data['rating_value'])

        if 'review_count' in additional_data:
            schema['reviewCount'] = str(additional_data['review_count'])

        # Échelle de notation
        if 'best_rating' in additional_data:
            schema['bestRating'] = str(additional_data['best_rating'])

        if 'worst_rating' in additional_data:
            schema['worstRating'] = str(additional_data['worst_rating'])

        # Nombre de notations
        if 'rating_count' in additional_data:
            schema['ratingCount'] = str(additional_data['rating_count'])
        elif 'review_count' in additional_data:
            schema['ratingCount'] = str(additional_data['review_count'])

        # Élément évalué (si AggregateRating est utilisé seul)
        if 'target_name' in additional_data and additional_data['target_name']:
            # Déterminer le type approprié - JAMAIS Thing !
            target_type = self._determine_item_type(additional_data)

            schema['itemReviewed'] = {
                "@type": target_type,
                "name": additional_data['target_name']
            }

            if 'target_url' in additional_data and additional_data['target_url']:
                schema['itemReviewed']['url'] = additional_data['target_url']

        # Distribution des notes
        if 'rating_distribution' in additional_data and additional_data['rating_distribution']:
            schema['ratingDistribution'] = []

            for rating_level, count in additional_data['rating_distribution'].items():
                distribution_item = {
                    "@type": "RatingDistribution",
                    "ratingValue": rating_level,
                    "ratingCount": count
                }
                schema['ratingDistribution'].append(distribution_item)

        # Source des avis
        if 'review_source' in additional_data and additional_data['review_source']:
            schema['reviewSource'] = {
                "@type": "Organization",
                "name": additional_data['review_source']
            }

        # URL de la page d'avis
        if 'reviews_url' in additional_data and additional_data['reviews_url']:
            schema['url'] = additional_data['reviews_url']

        # Date de mise à jour
        if 'last_updated' in additional_data and additional_data['last_updated']:
            schema['dateModified'] = additional_data['last_updated']

        # Période des avis
        if 'review_period' in additional_data and additional_data['review_period']:
            schema[
                'temporalCoverage'] = f"{additional_data['review_period']['start']}/{additional_data['review_period']['end']}"


class SoftwareApplicationFiller(SchemaFillerBase):
    """Filler pour les schemas SoftwareApplication"""

    def fill(self, schema: Dict, client_info: Dict, additional_data: Optional[Dict]) -> None:
        super().fill(schema, client_info, additional_data)

        if not additional_data:
            return

        # Informations de base
        if 'app_name' in additional_data and additional_data['app_name']:
            schema['name'] = additional_data['app_name']

        if 'app_category' in additional_data and additional_data['app_category']:
            schema['applicationCategory'] = additional_data['app_category']

        if 'app_subcategory' in additional_data and additional_data['app_subcategory']:
            schema['applicationSubCategory'] = additional_data['app_subcategory']

        # Systèmes d'exploitation
        if 'operating_systems' in additional_data and additional_data['operating_systems']:
            schema['operatingSystem'] = ", ".join(additional_data['operating_systems'])

        if 'software_version' in additional_data and additional_data['software_version']:
            schema['softwareVersion'] = additional_data['software_version']

        if 'file_size' in additional_data and additional_data['file_size']:
            schema['fileSize'] = additional_data['file_size']

        # URLs
        if 'download_url' in additional_data and additional_data['download_url']:
            schema['downloadUrl'] = additional_data['download_url']

        if 'install_url' in additional_data and additional_data['install_url']:
            schema['installUrl'] = additional_data['install_url']

        if 'software_requirements' in additional_data and additional_data['software_requirements']:
            schema['softwareRequirements'] = additional_data['software_requirements']

        # Prix et offres
        if 'offers' in schema and isinstance(schema['offers'], dict):
            if 'price' in additional_data and additional_data['price']:
                schema['offers']['price'] = additional_data['price']
            else:
                schema['offers']['price'] = "0"

            if 'price_currency' in additional_data:
                schema['offers']['priceCurrency'] = additional_data['price_currency']

            if 'pricing_model' in additional_data:
                if additional_data['pricing_model'] == "Abonnement":
                    schema['offers']['@type'] = "Subscription"
                elif additional_data['pricing_model'] == "Essai gratuit":
                    schema['offers']['trialDuration'] = "P30D"  # 30 jours d'essai

        # Fonctionnalités
        if 'features' in additional_data and additional_data['features']:
            schema['featureList'] = additional_data['features']

        # Screenshots
        if 'screenshots' in additional_data and additional_data['screenshots']:
            schema['screenshot'] = additional_data['screenshots']

        # URLs de support
        if 'documentation_url' in additional_data and additional_data['documentation_url']:
            schema['softwareHelp'] = {
                "@type": "CreativeWork",
                "url": additional_data['documentation_url']
            }

        if 'support_url' in additional_data and additional_data['support_url']:
            schema['supportingData'] = additional_data['support_url']

        if 'privacy_policy_url' in additional_data and additional_data['privacy_policy_url']:
            schema['privacyPolicy'] = additional_data['privacy_policy_url']

        if 'terms_url' in additional_data and additional_data['terms_url']:
            schema['termsOfService'] = additional_data['terms_url']

        # Permissions (pour apps mobiles)
        if 'permissions' in additional_data and additional_data['permissions']:
            schema['permissions'] = ", ".join(additional_data['permissions'])

        # Publisher/Developer
        schema['author'] = {
            "@type": "Organization",
            "name": client_info.get('company_name', ''),
            "url": client_info.get('website', '')
        }


# Dictionnaire de mappage des types vers les fillers
SCHEMA_FILLERS = {
    'Organization': OrganizationFiller(),
    'LocalBusiness': LocalBusinessFiller(),
    'Restaurant': RestaurantFiller(),
    'Product': ProductFiller(),
    'Article': ArticleFiller(),
    'NewsArticle': ArticleFiller(),
    'BlogPosting': ArticleFiller(),
    'Event': EventFiller(),
    'FAQPage': FAQPageFiller(),
    'BreadcrumbList': BreadcrumbListFiller(),
    'WebSite': WebSiteFiller(),
    'HowTo': HowToFiller(),
    'Person': PersonFiller(),
    'JobPosting': JobPostingFiller(),
    'Service': ServiceFiller(),
    'SoftwareApplication': SoftwareApplicationFiller(),
    'Recipe': SchemaFillerBase(),
    'VideoObject': SchemaFillerBase(),
    'Course': SchemaFillerBase(),
    'Review': ReviewFiller(),  # Utilise le nouveau ReviewFiller corrigé
    'AggregateRating': AggregateRatingFiller(),  # Utilise le nouveau AggregateRatingFiller corrigé
}