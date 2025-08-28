"""
Validateurs pour les formats de données Schema.org
"""
from typing import Any, Tuple
from datetime import datetime
import re


class SchemaDataValidator:
    """Classe pour valider les formats de données Schema.org"""

    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """
        Valide le format d'une donnée selon les standards Schema.org

        Args:
            field_name: Nom du champ
            value: Valeur à valider

        Returns:
            Tuple (est_valide, message_erreur)
        """
        # Validation des dates
        if field_name in ['datePublished', 'dateModified', 'startDate', 'endDate',
                          'validThrough', 'datePosted', 'uploadDate', 'foundingDate']:
            return self._validate_date(value, field_name)

        # Validation des coordonnées
        if field_name in ['latitude', 'longitude']:
            return self._validate_coordinates(value, field_name)

        # Validation des durées ISO 8601
        if field_name in ['duration', 'totalTime', 'prepTime', 'cookTime']:
            return self._validate_duration(value, field_name)

        # Validation des URLs
        if field_name in ['url', 'logo', 'image', 'sameAs', 'hasMap',
                          'downloadUrl', 'contentUrl', 'embedUrl']:
            return self._validate_url(value, field_name)

        # Validation des emails
        if field_name == 'email':
            return self._validate_email(value)

        # Validation des numéros de téléphone
        if field_name in ['telephone', 'faxNumber']:
            return self._validate_phone(value)

        # Validation des codes pays
        if field_name == 'addressCountry':
            return self._validate_country_code(value)

        # Validation des devises
        if field_name in ['priceCurrency', 'currency']:
            return self._validate_currency(value)

        # Validation des prix
        if field_name in ['price', 'minPrice', 'maxPrice']:
            return self._validate_price(value)

        # Validation des heures
        if field_name in ['opens', 'closes']:
            return self._validate_time(value, field_name)

        return True, ""

    def _validate_date(self, value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide un format de date ISO 8601"""
        if not value:
            return True, ""

        try:
            # Accepter plusieurs formats
            if 'T' in str(value):
                # Format DateTime complet
                datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            else:
                # Format Date simple
                datetime.strptime(str(value), '%Y-%m-%d')
            return True, ""
        except:
            return False, f"Le champ {field_name} doit être au format ISO 8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)"

    def _validate_coordinates(self, value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide des coordonnées géographiques"""
        try:
            coord = float(value)
            if field_name == 'latitude' and not (-90 <= coord <= 90):
                return False, "La latitude doit être entre -90 et 90"
            if field_name == 'longitude' and not (-180 <= coord <= 180):
                return False, "La longitude doit être entre -180 et 180"
            return True, ""
        except:
            return False, f"Le champ {field_name} doit être un nombre valide"

    def _validate_duration(self, value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide une durée au format ISO 8601"""
        if not value:
            return True, ""

        # Pattern pour durée ISO 8601
        pattern = r'^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$'

        if not re.match(pattern, str(value)):
            return False, f"Le champ {field_name} doit être au format ISO 8601 (ex: PT30M, PT1H30M)"

        return True, ""

    def _validate_url(self, value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide une URL"""
        if not value:
            return True, ""

        # Pattern simple pour URL
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)$'

        if isinstance(value, str):
            if not re.match(url_pattern, value):
                return False, f"Le champ {field_name} doit être une URL valide commençant par http:// ou https://"
        elif isinstance(value, list):
            for url in value:
                if not re.match(url_pattern, str(url)):
                    return False, f"Toutes les URLs dans {field_name} doivent être valides"

        return True, ""

    def _validate_email(self, value: Any) -> Tuple[bool, str]:
        """Valide une adresse email"""
        if not value:
            return True, ""

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, str(value)):
            return False, "L'adresse email n'est pas valide"

        return True, ""

    def _validate_phone(self, value: Any) -> Tuple[bool, str]:
        """Valide un numéro de téléphone"""
        if not value:
            return True, ""

        # Accepter différents formats de téléphone
        phone_pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'

        if not re.match(phone_pattern, str(value).replace(' ', '')):
            return False, "Le numéro de téléphone n'est pas dans un format valide"

        return True, ""

    def _validate_country_code(self, value: Any) -> Tuple[bool, str]:
        """Valide un code pays ISO 3166-1 alpha-2"""
        if not value:
            return True, ""

        # Liste des codes pays valides
        valid_codes = [
            'AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
            'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ', 'BA', 'BW', 'BV', 'BR',
            'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC',
            'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO',
            'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'TF', 'GA',
            'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT',
            'HM', 'VA', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP',
            'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI',
            'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX',
            'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI',
            'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN',
            'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU', 'RW', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS',
            'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'SS',
            'ES', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK',
            'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UM', 'UY', 'UZ', 'VU',
            'VE', 'VN', 'VG', 'VI', 'WF', 'EH', 'YE', 'ZM', 'ZW'
        ]

        if str(value).upper() not in valid_codes:
            return False, f"Le code pays doit être un code ISO 3166-1 alpha-2 valide (ex: FR, US, GB)"

        return True, ""

    def _validate_currency(self, value: Any) -> Tuple[bool, str]:
        """Valide un code devise ISO 4217"""
        if not value:
            return True, ""

        # Liste des principales devises
        valid_currencies = [
            'EUR', 'USD', 'GBP', 'CHF', 'CAD', 'AUD', 'JPY', 'CNY', 'SEK', 'NOK', 'DKK',
            'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK', 'RUB', 'TRY', 'INR', 'IDR', 'MYR',
            'SGD', 'HKD', 'KRW', 'THB', 'PHP', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN',
            'UYU', 'ZAR', 'AED', 'SAR', 'ILS', 'EGP', 'MAD', 'NGN', 'KES', 'GHS'
        ]

        if str(value).upper() not in valid_currencies:
            return False, f"Le code devise doit être un code ISO 4217 valide (ex: EUR, USD, GBP)"

        return True, ""

    def _validate_price(self, value: Any) -> Tuple[bool, str]:
        """Valide un format de prix"""
        if not value:
            return True, ""

        # Accepter différents formats de prix
        try:
            # Convertir en string et nettoyer
            price_str = str(value).replace(',', '.').replace(' ', '').replace('€', '').replace('$', '')

            # Vérifier si c'est un nombre valide
            price_float = float(price_str)

            if price_float < 0:
                return False, "Le prix ne peut pas être négatif"

            return True, ""
        except:
            return False, "Le prix doit être un nombre valide (ex: 19.99, 19,99)"

    def _validate_time(self, value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide un format d'heure"""
        if not value:
            return True, ""

        # Pattern pour heure au format HH:MM ou HH:MM:SS
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'

        if not re.match(time_pattern, str(value)):
            return False, f"Le champ {field_name} doit être au format HH:MM (ex: 09:00, 18:30)"

        return True, ""