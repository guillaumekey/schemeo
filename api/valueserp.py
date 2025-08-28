"""
Module pour interagir avec l'API ValueSERP
"""
import requests
from typing import List, Dict, Optional
from config import Config


class ValueSERPAPI:
    """Classe pour gérer les requêtes à l'API ValueSERP"""

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
            location: Localisation pour la recherche
            language: Langue de recherche
            num: Nombre de résultats

        Returns:
            Résultats de recherche ou None si erreur
        """
        params = {
            'api_key': self.api_key,
            'q': keyword,
            'location': location,
            'hl': language,
            'gl': language[:2],
            'num': num,
            'output': 'json'
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur ValueSERP: {e}")
            return None

    def get_search_results(self, keyword: str, **kwargs) -> List[Dict]:
        """
        Récupère les résultats de recherche organiques

        Args:
            keyword: Mot-clé de recherche
            **kwargs: Arguments supplémentaires pour la recherche

        Returns:
            Liste des résultats organiques
        """
        data = self.search_google(keyword, **kwargs)

        if not data:
            return []

        return data.get('organic_results', [])