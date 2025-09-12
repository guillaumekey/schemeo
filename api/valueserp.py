"""
Module pour interagir avec l'API ValueSERP
Version finale avec paramètres corrects selon l'interface ValueSERP
"""
import requests
import time
import random
from typing import List, Dict, Optional
from config import Config


class ValueSERPAPI:
    """Classe originale pour gérer les requêtes à l'API ValueSERP (compatibilité)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.VALUESERP_BASE_URL

    def search_google(self,
                      keyword: str,
                      location: str = "France",
                      language: str = "fr",
                      num: int = 10) -> Optional[Dict]:
        """
        Effectue une recherche Google via ValueSERP

        Args:
            keyword: Mot-clé de recherche
            location: Localisation (nom de pays)
            language: Langue de recherche
            num: Nombre de résultats

        Returns:
            Résultats de recherche ou None si erreur
        """
        # Mapping des paramètres selon la localisation
        location_params = self._get_location_params(location, language)

        params = {
            'api_key': self.api_key,
            'q': keyword,
            'location': location_params['location'],
            'hl': location_params['hl'],
            'gl': location_params['gl'],
            'google_domain': location_params['google_domain'],
            'num': num,
            'output': 'json'
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur ValueSERP: {e}")
            return None

    def _get_location_params(self, location: str, language: str) -> Dict[str, str]:
        """
        Retourne les paramètres corrects selon la localisation

        Args:
            location: Nom de la localisation
            language: Langue souhaitée

        Returns:
            Dictionnaire avec les paramètres corrects
        """
        # Mapping des localisations avec leurs paramètres spécifiques
        location_mapping = {
            'France': {
                'location': 'France',
                'hl': 'fr',
                'gl': 'fr',
                'google_domain': 'google.fr'
            },
            'United Kingdom': {
                'location': 'United kingdom',  # Exactement comme dans l'interface ValueSERP
                'hl': 'en',
                'gl': 'uk',  # Paramètre clé !
                'google_domain': 'google.co.uk'
            },
            'United States': {
                'location': 'United States',
                'hl': 'en',
                'gl': 'us',
                'google_domain': 'google.com'
            },
            'Germany': {
                'location': 'Germany',
                'hl': 'de',
                'gl': 'de',
                'google_domain': 'google.de'
            },
            'Spain': {
                'location': 'Spain',
                'hl': 'es',
                'gl': 'es',
                'google_domain': 'google.es'
            },
            'Italy': {
                'location': 'Italy',
                'hl': 'it',
                'gl': 'it',
                'google_domain': 'google.it'
            },
            'Canada': {
                'location': 'Canada',
                'hl': 'en',
                'gl': 'ca',
                'google_domain': 'google.ca'
            }
        }

        # Retourner les paramètres spécifiques ou des paramètres par défaut
        return location_mapping.get(location, {
            'location': location,
            'hl': language,
            'gl': language[:2],
            'google_domain': 'google.com'
        })

    def get_search_results(self, keyword: str, **kwargs) -> List[Dict]:
        """
        Récupère les résultats de recherche organiques
        """
        data = self.search_google(keyword, **kwargs)

        if not data:
            return []

        return data.get('organic_results', [])


class ValueSERPAPIWithRetry:
    """Version améliorée avec retry automatique et paramètres corrects"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.VALUESERP_BASE_URL
        self.max_retries = 3
        self.base_delay = 2

    def search_google_with_retry(self,
                                 keyword: str,
                                 location: str = "France",
                                 language: str = "fr",
                                 num: int = 10) -> Optional[Dict]:
        """
        Effectue une recherche avec mécanisme de retry et paramètres corrects
        """
        for attempt in range(self.max_retries + 1):
            try:
                result = self._make_request(keyword, location, language, num, attempt)

                if result is None:
                    continue

                # Si succès, retourner le résultat
                if 'error' not in result:
                    print(f"✅ Succès après {attempt + 1} tentative(s)")
                    return result

                # Si erreur 400, pas de retry (configuration incorrecte)
                if result.get('status_code') == 400:
                    print(f"❌ Erreur 400 - Configuration incorrecte")
                    return result

                # Si erreur 503, retry
                elif result.get('status_code') == 503:
                    if attempt < self.max_retries:
                        delay = self._calculate_delay(attempt)
                        print(f"⏳ Erreur 503 - Retry dans {delay}s (tentative {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(delay)
                        continue
                    else:
                        print("❌ Échec après tous les retries - Service ValueSERP indisponible")
                        return {
                            'error': 'Service ValueSERP temporairement indisponible après plusieurs tentatives',
                            'status_code': 503,
                            'suggestions': [
                                'Vérifier la page de statut ValueSERP : https://valueserp.statuspage.io/',
                                'Réessayer dans 10-15 minutes',
                                'Contacter le support ValueSERP si le problème persiste'
                            ]
                        }

                # Pour les autres erreurs, pas de retry
                else:
                    print(f"❌ Erreur non-retryable: {result.get('error', 'Erreur inconnue')}")
                    return result

            except Exception as e:
                print(f"❌ Exception lors de la tentative {attempt + 1}: {e}")
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
                    continue
                else:
                    return {
                        'error': f'Erreur après tous les retries: {str(e)}',
                        'status_code': 500
                    }

        return None

    def _make_request(self, keyword: str, location: str, language: str, num: int, attempt: int) -> Optional[Dict]:
        """Effectue une requête unique avec les paramètres corrects"""

        # Obtenir les paramètres corrects selon la localisation
        location_params = self._get_location_params(location, language)

        params = {
            'api_key': self.api_key,
            'q': keyword,
            'location': location_params['location'],
            'hl': location_params['hl'],
            'gl': location_params['gl'],
            'google_domain': location_params['google_domain'],
            'num': num,
            'output': 'json'
        }

        print(f"📡 Tentative {attempt + 1}: {keyword}")
        print(f"🌍 Localisation: {location_params['location']}")
        print(
            f"🔧 Paramètres: gl={location_params['gl']}, hl={location_params['hl']}, domain={location_params['google_domain']}")

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=45
            )

            print(f"🔗 URL: {response.url}")
            print(f"📊 Status Code: {response.status_code}")

            # Gestion spécifique des codes d'erreur
            if response.status_code == 400:
                print(f"❌ Erreur 400: Paramètres invalides")
                return {
                    'error': f'Paramètres invalides - vérifiez la configuration pour "{location}"',
                    'status_code': 400,
                    'debug_info': {
                        'used_params': location_params,
                        'original_location': location
                    }
                }
            elif response.status_code == 503:
                print("❌ Erreur 503: Service temporairement indisponible")
                return {
                    'error': 'Service temporairement indisponible (surcharge ou maintenance)',
                    'status_code': 503
                }
            elif response.status_code == 429:
                print("❌ Erreur 429: Limite de taux atteinte")
                return {
                    'error': 'Limite de taux atteinte - trop de requêtes',
                    'status_code': 429
                }
            elif response.status_code == 401:
                print("❌ Erreur 401: Clé API invalide")
                return {
                    'error': 'Clé API invalide ou expirée',
                    'status_code': 401
                }

            response.raise_for_status()
            result = response.json()

            # Vérifier si l'API retourne une erreur dans le JSON
            if 'error' in result:
                return {
                    'error': result['error'],
                    'status_code': response.status_code
                }

            print(f"✅ Succès: {len(result.get('organic_results', []))} résultats trouvés")
            return result

        except requests.exceptions.Timeout:
            print("⏰ Timeout: La requête a pris trop de temps")
            return {
                'error': 'Timeout - la requête a pris trop de temps',
                'status_code': 408
            }
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') and e.response else 500
            print(f"❌ Erreur requête: {e}")
            return {
                'error': f'Erreur réseau: {str(e)}',
                'status_code': status_code
            }

    def _get_location_params(self, location: str, language: str) -> Dict[str, str]:
        """
        Retourne les paramètres corrects selon la localisation
        Basé sur l'analyse de l'interface ValueSERP fonctionnelle
        """
        # Mapping exact basé sur l'interface ValueSERP
        location_mapping = {
            'France': {
                'location': 'France',
                'hl': 'fr',
                'gl': 'fr',
                'google_domain': 'google.fr'
            },
            'United Kingdom': {
                'location': 'United kingdom',  # Exactement comme dans l'API fonctionnelle
                'hl': 'en',
                'gl': 'uk',  # Clé du succès !
                'google_domain': 'google.co.uk'
            },
            'United States': {
                'location': 'United States',
                'hl': 'en',
                'gl': 'us',
                'google_domain': 'google.com'
            },
            'Germany': {
                'location': 'Germany',
                'hl': 'de',
                'gl': 'de',
                'google_domain': 'google.de'
            },
            'Spain': {
                'location': 'Spain',
                'hl': 'es',
                'gl': 'es',
                'google_domain': 'google.es'
            },
            'Italy': {
                'location': 'Italy',
                'hl': 'it',
                'gl': 'it',
                'google_domain': 'google.it'
            },
            'Canada': {
                'location': 'Canada',
                'hl': 'en',
                'gl': 'ca',
                'google_domain': 'google.ca'
            }
        }

        return location_mapping.get(location, {
            'location': location,
            'hl': language,
            'gl': language[:2],
            'google_domain': 'google.com'
        })

    def _calculate_delay(self, attempt: int) -> float:
        """Calcule le délai avec backoff exponentiel et jitter"""
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0.5, 1.5)
        return min(delay * jitter, 30)

    def test_location(self, location: str) -> Dict:
        """Teste une localisation spécifique avec les bons paramètres"""
        print(f"🧪 Test de la localisation: {location}")

        test_result = self._make_request("test", location, "en", 1, 0)

        if test_result and 'error' not in test_result:
            return {
                'success': True,
                'message': f'✅ Localisation "{location}" fonctionne parfaitement',
                'location_tested': location,
                'params_used': self._get_location_params(location, "en")
            }
        elif test_result and test_result.get('status_code') == 400:
            return {
                'success': False,
                'message': f'❌ Localisation "{location}" invalide',
                'status_code': 400,
                'debug_info': test_result.get('debug_info', {}),
                'location_tested': location
            }
        elif test_result and test_result.get('status_code') == 503:
            return {
                'success': None,
                'message': f'⚠️ Service indisponible - impossible de tester "{location}"',
                'status_code': 503,
                'location_tested': location
            }
        else:
            return {
                'success': False,
                'message': f'❌ Erreur lors du test de "{location}": {test_result.get("error", "Erreur inconnue") if test_result else "Aucune réponse"}',
                'location_tested': location
            }

    def get_service_status(self) -> Dict:
        """Vérifie le statut du service ValueSERP"""
        try:
            test_result = self.search_google_with_retry(
                keyword="test",
                location="France",
                language="fr",
                num=1
            )

            if test_result and 'error' not in test_result:
                return {
                    'status': 'operational',
                    'message': '✅ Service ValueSERP opérationnel',
                    'response_time': 'Normal'
                }
            elif test_result and test_result.get('status_code') == 503:
                return {
                    'status': 'degraded',
                    'message': '⚠️ Service ValueSERP en surcharge/maintenance',
                    'details': test_result.get('error', ''),
                    'suggestions': test_result.get('suggestions', [])
                }
            elif test_result and test_result.get('status_code') == 400:
                return {
                    'status': 'configuration_error',
                    'message': '⚠️ Problème de configuration des paramètres',
                    'details': test_result.get('error', ''),
                    'debug_info': test_result.get('debug_info', {})
                }
            else:
                return {
                    'status': 'error',
                    'message': '❌ Problème avec le service ValueSERP',
                    'details': test_result.get('error', 'Erreur inconnue') if test_result else 'Aucune réponse'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'❌ Impossible de tester le service: {str(e)}'
            }

    def get_search_results(self, keyword: str, **kwargs) -> list:
        """Version avec retry des résultats de recherche"""
        data = self.search_google_with_retry(keyword, **kwargs)

        if not data or 'error' in data:
            return []

        return data.get('organic_results', [])

    def test_api_connection(self) -> Dict[str, any]:
        """Teste la connexion à l'API ValueSERP"""
        test_result = self.search_google_with_retry(
            keyword="test",
            location="France",
            language="fr",
            num=1
        )

        if test_result and 'error' not in test_result:
            return {
                'success': True,
                'message': 'Connexion API ValueSERP réussie',
                'credits_used': test_result.get('search_metadata', {}).get('total_credits_used', 'N/A')
            }
        else:
            return {
                'success': False,
                'message': test_result.get('error', 'Erreur inconnue') if test_result else 'Aucune réponse',
                'status_code': test_result.get('status_code', 'N/A') if test_result else 'N/A',
                'debug_info': test_result.get('debug_info', {}) if test_result else {}
            }


# Fonction utilitaire pour les diagnostics
def diagnose_valueserp_issues(api_key: str) -> Dict:
    """Diagnostique complet des problèmes ValueSERP avec tests de paramètres"""
    api = ValueSERPAPIWithRetry(api_key)

    diagnosis = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'api_key_valid': bool(api_key and len(api_key) > 10),
        'service_status': api.get_service_status(),
        'location_tests': {},
        'parameter_analysis': {},
        'recommendations': []
    }

    # Tests de localisations
    test_locations = ['France', 'United Kingdom', 'United States']

    for location in test_locations:
        print(f"🧪 Test de {location}...")
        diagnosis['location_tests'][location] = api.test_location(location)

        # Analyser les paramètres utilisés
        params = api._get_location_params(location, "en")
        diagnosis['parameter_analysis'][location] = params

    # Recommandations basées sur les résultats
    service_status = diagnosis['service_status']['status']

    if service_status == 'operational':
        diagnosis['recommendations'].append('✅ Service opérationnel - paramètres corrects')
    elif service_status == 'degraded':
        diagnosis['recommendations'].extend([
            '⏳ Attendre 10-15 minutes avant de réessayer',
            '📊 Vérifier la page de statut : https://valueserp.statuspage.io/',
            '🔄 Le système de retry automatique devrait gérer le problème'
        ])
    elif service_status == 'configuration_error':
        diagnosis['recommendations'].extend([
            '🔧 Problème de configuration des paramètres détecté',
            '📝 Vérifier le mapping des localisations dans le code',
            '🧪 Tester avec l\'interface ValueSERP pour comparer'
        ])
    else:
        diagnosis['recommendations'].extend([
            '🔑 Vérifier la validité de la clé API',
            '🌐 Vérifier la connexion internet',
            '💬 Contacter le support ValueSERP'
        ])

    return diagnosis


def create_valueserp_client(api_key: str, use_retry: bool = True):
    """Factory pour créer le bon client ValueSERP"""
    if use_retry:
        return ValueSERPAPIWithRetry(api_key)
    else:
        return ValueSERPAPI(api_key)