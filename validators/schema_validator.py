"""
Module pour valider et tester la compatibilité des schemas
"""
import json
import requests
from typing import Dict, List, Tuple, Optional
from jsonschema import validate, ValidationError
import validators


class SchemaValidator:
    """Classe pour valider les schemas selon les standards Schema.org"""

    def __init__(self):
        self.google_test_url = "https://validator.schema.org/"
        self.required_fields = {
            'Organization': ['name', 'url'],
            'LocalBusiness': ['name', 'address', 'telephone'],
            'Product': ['name', 'image', 'description'],
            'Article': ['headline', 'image', 'datePublished', 'author', 'publisher'],
            'FAQPage': ['mainEntity'],
            'BreadcrumbList': ['itemListElement'],
            'WebSite': ['name', 'url'],
            'Person': ['name'],
            'Event': ['name', 'startDate', 'location'],
            'VideoObject': ['name', 'description', 'thumbnailUrl', 'uploadDate'],
            'Review': ['itemReviewed', 'author', 'reviewRating'],
            'AggregateRating': ['ratingValue', 'reviewCount']
        }

    def validate_schema(self, schema: Dict) -> Tuple[bool, List[str]]:
        """
        Valide un schema individuel

        Args:
            schema: Schema à valider

        Returns:
            Tuple (est_valide, liste_erreurs)
        """
        errors = []

        # Vérifier la présence du @context et @type
        if '@context' not in schema:
            errors.append("Le champ @context est manquant")
        elif schema['@context'] != "https://schema.org":
            errors.append("Le @context doit être 'https://schema.org'")

        if '@type' not in schema:
            errors.append("Le champ @type est manquant")
            return False, errors

        schema_type = schema['@type']

        # Vérifier les champs requis selon le type
        if schema_type in self.required_fields:
            for field in self.required_fields[schema_type]:
                if field not in schema or not schema[field]:
                    errors.append(f"Le champ requis '{field}' est manquant ou vide")

        # Validations spécifiques par type
        if schema_type == 'Organization':
            errors.extend(self._validate_organization(schema))
        elif schema_type == 'LocalBusiness':
            errors.extend(self._validate_local_business(schema))
        elif schema_type == 'Product':
            errors.extend(self._validate_product(schema))
        elif schema_type == 'Article':
            errors.extend(self._validate_article(schema))
        elif schema_type == 'FAQPage':
            errors.extend(self._validate_faq(schema))
        elif schema_type == 'Event':
            errors.extend(self._validate_event(schema))
        elif schema_type == 'Review':
            errors.extend(self._validate_review(schema))

        return len(errors) == 0, errors

    def _validate_organization(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour Organization"""
        errors = []

        # Valider l'URL
        if 'url' in schema and schema['url']:
            if not validators.url(schema['url']):
                errors.append("L'URL de l'organisation n'est pas valide")

        # Valider les réseaux sociaux
        if 'sameAs' in schema and isinstance(schema['sameAs'], list):
            for url in schema['sameAs']:
                if not validators.url(url):
                    errors.append(f"L'URL de réseau social '{url}' n'est pas valide")

        return errors

    def _validate_local_business(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour LocalBusiness"""
        errors = []

        # Valider l'adresse
        if 'address' in schema:
            address = schema['address']
            if not isinstance(address, dict) or '@type' not in address:
                errors.append("L'adresse doit être un objet PostalAddress valide")
            elif address.get('@type') != 'PostalAddress':
                errors.append("Le type d'adresse doit être 'PostalAddress'")

        # Valider les coordonnées géographiques
        if 'geo' in schema:
            geo = schema['geo']
            if not isinstance(geo, dict) or '@type' not in geo:
                errors.append("Les coordonnées géographiques doivent être un objet GeoCoordinates")
            else:
                try:
                    lat = float(geo.get('latitude', 0))
                    lng = float(geo.get('longitude', 0))
                    if not (-90 <= lat <= 90):
                        errors.append("La latitude doit être entre -90 et 90")
                    if not (-180 <= lng <= 180):
                        errors.append("La longitude doit être entre -180 et 180")
                except (ValueError, TypeError):
                    errors.append("Les coordonnées géographiques doivent être des nombres valides")

        return errors

    def _validate_product(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour Product"""
        errors = []

        # Valider les offres
        if 'offers' in schema:
            offers = schema['offers']
            if not isinstance(offers, dict) or '@type' not in offers:
                errors.append("Les offres doivent être un objet Offer valide")
            else:
                # Valider le prix
                if 'price' in offers:
                    try:
                        price = float(str(offers['price']).replace(',', '.'))
                        if price < 0:
                            errors.append("Le prix ne peut pas être négatif")
                    except ValueError:
                        errors.append("Le prix doit être un nombre valide")

                # Valider la disponibilité
                if 'availability' in offers:
                    valid_availability = [
                        "https://schema.org/InStock",
                        "https://schema.org/OutOfStock",
                        "https://schema.org/PreOrder",
                        "https://schema.org/BackOrder"
                    ]
                    if offers['availability'] not in valid_availability:
                        errors.append("La disponibilité doit être une valeur schema.org valide")

        return errors

    def _validate_article(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour Article"""
        errors = []

        # Valider les dates
        for date_field in ['datePublished', 'dateModified']:
            if date_field in schema and schema[date_field]:
                # Vérifier le format ISO 8601
                try:
                    from datetime import datetime
                    datetime.fromisoformat(schema[date_field].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"La date '{date_field}' doit être au format ISO 8601")

        # Valider l'auteur
        if 'author' in schema:
            author = schema['author']
            if not isinstance(author, dict) or '@type' not in author:
                errors.append("L'auteur doit être un objet Person ou Organization")

        # Valider le publisher
        if 'publisher' in schema:
            publisher = schema['publisher']
            if not isinstance(publisher, dict) or '@type' not in publisher:
                errors.append("Le publisher doit être un objet Organization")
            elif 'logo' in publisher:
                logo = publisher['logo']
                if not isinstance(logo, dict) or 'url' not in logo:
                    errors.append("Le logo du publisher doit contenir une URL")

        return errors

    def _validate_faq(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour FAQPage"""
        errors = []

        if 'mainEntity' in schema:
            if not isinstance(schema['mainEntity'], list):
                errors.append("mainEntity doit être une liste de questions")
            else:
                for i, question in enumerate(schema['mainEntity']):
                    if not isinstance(question, dict):
                        errors.append(f"La question {i + 1} n'est pas un objet valide")
                    else:
                        if '@type' not in question or question['@type'] != 'Question':
                            errors.append(f"La question {i + 1} doit être de type 'Question'")
                        if 'name' not in question or not question['name']:
                            errors.append(f"La question {i + 1} doit avoir un texte")
                        if 'acceptedAnswer' not in question:
                            errors.append(f"La question {i + 1} doit avoir une réponse")
                        elif not isinstance(question['acceptedAnswer'], dict):
                            errors.append(f"La réponse de la question {i + 1} doit être un objet Answer")

        return errors

    def _validate_event(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour Event"""
        errors = []

        # Valider les dates
        if 'startDate' in schema and 'endDate' in schema:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(schema['startDate'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(schema['endDate'].replace('Z', '+00:00'))
                if end < start:
                    errors.append("La date de fin doit être après la date de début")
            except ValueError:
                errors.append("Les dates doivent être au format ISO 8601")

        # Valider la location
        if 'location' in schema:
            location = schema['location']
            if not isinstance(location, dict) or '@type' not in location:
                errors.append("La location doit être un objet Place valide")

        return errors

    def _validate_review(self, schema: Dict) -> List[str]:
        """Validations spécifiques pour Review"""
        errors = []

        # Valider la note
        if 'reviewRating' in schema:
            rating = schema['reviewRating']
            if not isinstance(rating, dict) or '@type' not in rating:
                errors.append("reviewRating doit être un objet Rating")
            else:
                try:
                    rating_value = float(rating.get('ratingValue', 0))
                    best_rating = float(rating.get('bestRating', 5))
                    worst_rating = float(rating.get('worstRating', 1))

                    if not (worst_rating <= rating_value <= best_rating):
                        errors.append("La note doit être entre worstRating et bestRating")
                except (ValueError, TypeError):
                    errors.append("Les valeurs de rating doivent être des nombres")

        return errors

    def test_compatibility(self, schemas: List[Dict]) -> Dict:
        """
        Teste la compatibilité d'un ensemble de schemas

        Args:
            schemas: Liste des schemas à tester

        Returns:
            Résultats des tests avec recommandations
        """
        results = {
            'total_schemas': len(schemas),
            'valid_schemas': 0,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }

        schema_types = []

        for i, schema in enumerate(schemas):
            is_valid, errors = self.validate_schema(schema)

            if is_valid:
                results['valid_schemas'] += 1
            else:
                results['errors'].extend([f"Schema {i + 1}: {error}" for error in errors])

            if '@type' in schema:
                schema_types.append(schema['@type'])

        # Vérifier les doublons
        if len(schema_types) != len(set(schema_types)):
            duplicates = [t for t in schema_types if schema_types.count(t) > 1]
            results['warnings'].append(f"Schemas dupliqués détectés: {', '.join(set(duplicates))}")

        # Recommandations
        if 'Organization' not in schema_types and 'LocalBusiness' not in schema_types:
            results['recommendations'].append(
                "Ajoutez un schema Organization ou LocalBusiness pour identifier votre entreprise")

        if 'WebSite' not in schema_types:
            results['recommendations'].append(
                "Ajoutez un schema WebSite pour améliorer l'apparence dans les résultats de recherche")

        if 'BreadcrumbList' not in schema_types:
            results['recommendations'].append("Ajoutez un schema BreadcrumbList pour améliorer la navigation")

        return results

    def format_test_results(self, results: Dict, language: str = 'fr') -> str:
        """
        Formate les résultats de test pour l'affichage

        Args:
            results: Résultats des tests
            language: Langue d'affichage

        Returns:
            Résultats formatés
        """
        messages = {
            'fr': {
                'summary': f"✓ {results['valid_schemas']} schemas valides sur {results['total_schemas']}",
                'errors': "❌ Erreurs détectées:",
                'warnings': "⚠️ Avertissements:",
                'recommendations': "💡 Recommandations:",
                'success': "✅ Tous les schemas sont valides!"
            },
            'en': {
                'summary': f"✓ {results['valid_schemas']} valid schemas out of {results['total_schemas']}",
                'errors': "❌ Errors detected:",
                'warnings': "⚠️ Warnings:",
                'recommendations': "💡 Recommendations:",
                'success': "✅ All schemas are valid!"
            },
            'es': {
                'summary': f"✓ {results['valid_schemas']} schemas válidos de {results['total_schemas']}",
                'errors': "❌ Errores detectados:",
                'warnings': "⚠️ Advertencias:",
                'recommendations': "💡 Recomendaciones:",
                'success': "✅ ¡Todos los schemas son válidos!"
            }
        }

        lang_messages = messages.get(language, messages['fr'])
        output = [lang_messages['summary']]

        if results['errors']:
            output.append(f"\n{lang_messages['errors']}")
            output.extend(f"  • {error}" for error in results['errors'])

        if results['warnings']:
            output.append(f"\n{lang_messages['warnings']}")
            output.extend(f"  • {warning}" for warning in results['warnings'])

        if results['recommendations']:
            output.append(f"\n{lang_messages['recommendations']}")
            output.extend(f"  • {rec}" for rec in results['recommendations'])

        if not results['errors'] and not results['warnings']:
            output.append(f"\n{lang_messages['success']}")

        return '\n'.join(output)