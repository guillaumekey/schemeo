"""
Configuration des localisations pour l'API ValueSERP
Format requis: utiliser les noms EXACTS de l'API Locations ValueSERP
"""

# Localisations EXACTES selon l'API ValueSERP Locations
VALUESERP_LOCATIONS = {
    # Format corrigé selon la documentation ValueSERP
    'France': 'France',
    'United Kingdom': 'United Kingdom',  # ou "London,England,United Kingdom" pour Londres spécifiquement
    'United States': 'United States',
    'Germany': 'Germany',
    'Spain': 'Spain',
    'Italy': 'Italy',
    'Canada': 'Canada',
    'Netherlands': 'Netherlands',
    'Belgium': 'Belgium',
    'Switzerland': 'Switzerland',
    'Portugal': 'Portugal',
    'Austria': 'Austria',
    'Sweden': 'Sweden',
    'Denmark': 'Denmark',
    'Norway': 'Norway',
    'Australia': 'Australia',
    'Japan': 'Japan',
    'South Korea': 'South Korea',
    'Brazil': 'Brazil',
    'Mexico': 'Mexico'
}

# Localisations spécifiques par ville (format exact ValueSERP)
CITY_SPECIFIC_LOCATIONS = {
    'London, UK': 'London,England,United Kingdom',
    'Paris, France': 'Paris,Ile-de-France,France',
    'New York, USA': 'New York,New York,United States',
    'Berlin, Germany': 'Berlin,Berlin,Germany',
    'Madrid, Spain': 'Madrid,Madrid,Spain',
    'Rome, Italy': 'Rome,Lazio,Italy',
    'Toronto, Canada': 'Toronto,Ontario,Canada',
    'Sydney, Australia': 'Sydney,New South Wales,Australia',
    'Tokyo, Japan': 'Tokyo,Tokyo,Japan'
}


def get_location_for_valueserp(display_name: str) -> str:
    """
    Retourne la localisation au format ValueSERP

    Args:
        display_name: Nom d'affichage du pays/région

    Returns:
        Localisation au format ValueSERP
    """
    # Vérifier d'abord les localisations spécifiques par ville
    if display_name in CITY_SPECIFIC_LOCATIONS:
        return CITY_SPECIFIC_LOCATIONS[display_name]

    # Sinon utiliser les localisations par pays
    return VALUESERP_LOCATIONS.get(display_name, 'United States')


def get_available_locations() -> list:
    """
    Retourne la liste des localisations disponibles
    """
    return list(VALUESERP_LOCATIONS.keys())


def get_reliable_locations() -> dict:
    """
    Retourne les localisations les plus fiables et testées

    Returns:
        Dictionnaire des localisations garanties fonctionnelles
    """
    return {
        'France': 'France',
        'United Kingdom': 'United Kingdom',
        'United States': 'United States',
        'Germany': 'Germany',
        'Spain': 'Spain',
        'Italy': 'Italy',
        'Canada': 'Canada'
    }


def get_city_specific_locations() -> dict:
    """
    Retourne les localisations spécifiques par ville
    """
    return CITY_SPECIFIC_LOCATIONS


def validate_location_format(location: str) -> bool:
    """
    Valide si une localisation est dans un format ValueSERP acceptable

    Args:
        location: Localisation à valider

    Returns:
        True si le format semble valide
    """
    # Accepter les noms de pays simples
    if location in VALUESERP_LOCATIONS.values():
        return True

    # Accepter les formats ville,région,pays
    if ',' in location:
        parts = location.split(',')
        if len(parts) == 3:
            return True

    return False


def suggest_location_fix(invalid_location: str) -> str:
    """
    Suggère une correction pour une localisation

    Args:
        invalid_location: Localisation à corriger

    Returns:
        Suggestion de localisation valide
    """
    location_lower = invalid_location.lower()

    # Mapping des corrections courantes
    corrections = {
        'uk': 'United Kingdom',
        'usa': 'United States',
        'us': 'United States',
        'deutschland': 'Germany',
        'espana': 'Spain',
        'italia': 'Italy'
    }

    return corrections.get(location_lower, 'United States')


# Fonction pour tester une localisation avec l'API
def test_location_with_api(api_key: str, location: str) -> dict:
    """
    Test une localisation avec l'API ValueSERP

    Args:
        api_key: Clé API ValueSERP
        location: Localisation à tester

    Returns:
        Résultat du test
    """
    import requests

    try:
        response = requests.get(
            'https://api.valueserp.com/search',
            params={
                'api_key': api_key,
                'q': 'test',
                'location': location,
                'num': 1
            },
            timeout=30
        )

        if response.status_code == 200:
            return {
                'success': True,
                'message': f'Localisation "{location}" fonctionne',
                'status_code': response.status_code
            }
        elif response.status_code == 400:
            return {
                'success': False,
                'message': f'Localisation "{location}" invalide (400)',
                'status_code': response.status_code,
                'details': 'Paramètres invalides - vérifiez le format de localisation'
            }
        else:
            return {
                'success': False,
                'message': f'Erreur {response.status_code}',
                'status_code': response.status_code
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'Erreur de test: {str(e)}',
            'status_code': None
        }


def get_recommended_locations() -> dict:
    """
    Retourne les localisations recommandées avec exemples

    Returns:
        Dictionnaire avec conseils d'utilisation
    """
    return {
        'Simple (recommandé)': {
            'France': 'France',
            'United Kingdom': 'United Kingdom',
            'United States': 'United States',
            'Germany': 'Germany'
        },
        'Spécifique par ville': {
            'Londres': 'London,England,United Kingdom',
            'Paris': 'Paris,Ile-de-France,France',
            'New York': 'New York,New York,United States',
            'Berlin': 'Berlin,Berlin,Germany'
        },
        'Conseils': [
            'Utilisez les noms de pays simples pour plus de fiabilité',
            'Les formats ville,région,pays nécessitent des noms EXACTS',
            'Consultez l\'API Locations ValueSERP pour les noms complets',
            'Testez toujours vos localisations avant utilisation'
        ]
    }