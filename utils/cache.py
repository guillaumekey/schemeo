"""
Module de gestion du cache pour optimiser les performances
"""
import json
import time
import hashlib
from typing import Any, Optional, Dict
from functools import wraps
from config import Config


class CacheManager:
    """Gestionnaire de cache simple en mémoire"""

    def __init__(self):
        self.cache = {}
        self.timestamps = {}

    def _get_cache_key(self, key_data: Any) -> str:
        """
        Génère une clé de cache unique

        Args:
            key_data: Données pour générer la clé

        Returns:
            Clé de cache
        """
        if isinstance(key_data, (dict, list)):
            key_str = json.dumps(key_data, sort_keys=True)
        else:
            key_str = str(key_data)

        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: Any) -> Optional[Any]:
        """
        Récupère une valeur du cache

        Args:
            key: Clé de cache

        Returns:
            Valeur en cache ou None
        """
        if not Config.CACHE_ENABLED:
            return None

        cache_key = self._get_cache_key(key)

        if cache_key in self.cache:
            # Vérifier l'expiration
            timestamp = self.timestamps.get(cache_key, 0)
            if time.time() - timestamp < Config.CACHE_DURATION:
                return self.cache[cache_key]
            else:
                # Supprimer l'entrée expirée
                del self.cache[cache_key]
                del self.timestamps[cache_key]

        return None

    def set(self, key: Any, value: Any):
        """
        Stocke une valeur dans le cache

        Args:
            key: Clé de cache
            value: Valeur à stocker
        """
        if not Config.CACHE_ENABLED:
            return

        cache_key = self._get_cache_key(key)
        self.cache[cache_key] = value
        self.timestamps[cache_key] = time.time()

    def clear(self):
        """Vide complètement le cache"""
        self.cache.clear()
        self.timestamps.clear()

    def remove(self, key: Any):
        """
        Supprime une entrée spécifique du cache

        Args:
            key: Clé à supprimer
        """
        cache_key = self._get_cache_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
            del self.timestamps[cache_key]

    def get_stats(self) -> Dict:
        """
        Retourne des statistiques sur le cache

        Returns:
            Statistiques du cache
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0

        for cache_key, timestamp in self.timestamps.items():
            if current_time - timestamp < Config.CACHE_DURATION:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_enabled': Config.CACHE_ENABLED
        }


# Instance globale du cache
cache_manager = CacheManager()


def cached(cache_key_prefix: str = ""):
    """
    Décorateur pour mettre en cache les résultats d'une fonction

    Args:
        cache_key_prefix: Préfixe pour la clé de cache

    Returns:
        Fonction décorée
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Construire la clé de cache
            cache_key = {
                'prefix': cache_key_prefix or func.__name__,
                'args': args,
                'kwargs': kwargs
            }

            # Vérifier le cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Exécuter la fonction
            result = func(*args, **kwargs)

            # Stocker dans le cache
            cache_manager.set(cache_key, result)

            return result

        return wrapper

    return decorator


# Fonctions utilitaires pour le cache Streamlit
def get_cached_serp_results(keyword: str, location: str, language: str) -> Optional[Dict]:
    """
    Récupère les résultats SERP du cache

    Args:
        keyword: Mot-clé recherché
        location: Localisation
        language: Langue

    Returns:
        Résultats en cache ou None
    """
    cache_key = {
        'type': 'serp_results',
        'keyword': keyword,
        'location': location,
        'language': language
    }

    return cache_manager.get(cache_key)


def set_cached_serp_results(keyword: str, location: str, language: str, results: Dict):
    """
    Stocke les résultats SERP dans le cache

    Args:
        keyword: Mot-clé recherché
        location: Localisation
        language: Langue
        results: Résultats à stocker
    """
    cache_key = {
        'type': 'serp_results',
        'keyword': keyword,
        'location': location,
        'language': language
    }

    cache_manager.set(cache_key, results)


def get_cached_schema_analysis(url: str) -> Optional[Dict]:
    """
    Récupère l'analyse de schema du cache

    Args:
        url: URL analysée

    Returns:
        Analyse en cache ou None
    """
    cache_key = {
        'type': 'schema_analysis',
        'url': url
    }

    return cache_manager.get(cache_key)


def set_cached_schema_analysis(url: str, analysis: Dict):
    """
    Stocke l'analyse de schema dans le cache

    Args:
        url: URL analysée
        analysis: Analyse à stocker
    """
    cache_key = {
        'type': 'schema_analysis',
        'url': url
    }

    cache_manager.set(cache_key, analysis)