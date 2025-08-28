"""
Module pour scraper et extraire les schemas des pages web
"""
import requests
import json
from bs4 import BeautifulSoup
import extruct
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse
from config import Config


class SchemaScraper:
    """Classe pour scraper et extraire les schemas des pages"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT
        })

    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape le contenu HTML d'une URL

        Args:
            url: URL à scraper

        Returns:
            Contenu HTML ou None si erreur
        """
        try:
            response = self.session.get(
                url,
                timeout=Config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du scraping de {url}: {e}")
            return None

    def extract_schemas(self, url: str, html: Optional[str] = None) -> Dict:
        """
        Extrait tous les schemas d'une page

        Args:
            url: URL de la page
            html: Contenu HTML (optionnel, sera scrapé si non fourni)

        Returns:
            Dictionnaire contenant tous les schemas trouvés
        """
        if not html:
            html = self.scrape_url(url)
            if not html:
                return {}

        try:
            # Parser le HTML avec BeautifulSoup pour une extraction plus robuste
            soup = BeautifulSoup(html, 'html.parser')

            # Extraire les scripts JSON-LD manuellement d'abord
            json_ld_schemas = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    script_text = script.string
                    if script_text:
                        data = json.loads(script_text)
                        if isinstance(data, list):
                            json_ld_schemas.extend(data)
                        else:
                            json_ld_schemas.append(data)
                except json.JSONDecodeError as e:
                    print(f"Erreur parsing JSON-LD: {e}")
                    continue

            # Utiliser aussi extruct pour être complet
            extruct_data = extruct.extract(
                html,
                base_url=url,
                syntaxes=['json-ld', 'microdata', 'rdfa', 'opengraph']
            )

            # Fusionner les résultats
            all_json_ld = json_ld_schemas + extruct_data.get('json-ld', [])

            schemas = {
                'json-ld': self._process_json_ld(all_json_ld),
                'microdata': self._process_microdata(extruct_data.get('microdata', [])),
                'rdfa': extruct_data.get('rdfa', []),
                'opengraph': extruct_data.get('opengraph', [])
            }

            return schemas

        except Exception as e:
            print(f"Erreur lors de l'extraction des schemas de {url}: {e}")
            return {}

    def _process_json_ld(self, json_ld_data: List[Dict]) -> List[Dict]:
        """
        Traite et nettoie les données JSON-LD

        Args:
            json_ld_data: Données JSON-LD brutes

        Returns:
            Données JSON-LD nettoyées et dédupliquées
        """
        processed = []
        seen_ids = set()
        seen_schemas = []

        for item in json_ld_data:
            if isinstance(item, dict):
                # Gérer les @graph
                if '@graph' in item:
                    graph_items = item.get('@graph', [])
                    if isinstance(graph_items, list):
                        for graph_item in graph_items:
                            if isinstance(graph_item, dict) and '@type' in graph_item:
                                # Vérifier si on a déjà vu ce schema
                                schema_id = graph_item.get('@id', '')
                                if schema_id and schema_id not in seen_ids:
                                    seen_ids.add(schema_id)
                                    processed.append(graph_item)
                                elif not schema_id:
                                    # Si pas d'@id, vérifier par contenu
                                    schema_str = json.dumps(graph_item, sort_keys=True)
                                    if schema_str not in seen_schemas:
                                        seen_schemas.append(schema_str)
                                        processed.append(graph_item)
                elif '@type' in item:
                    # Vérifier si on a déjà vu ce schema
                    schema_id = item.get('@id', '')
                    if schema_id and schema_id not in seen_ids:
                        seen_ids.add(schema_id)
                        processed.append(item)
                    elif not schema_id:
                        # Si pas d'@id, vérifier par contenu
                        schema_str = json.dumps(item, sort_keys=True)
                        if schema_str not in seen_schemas:
                            seen_schemas.append(schema_str)
                            processed.append(item)

        return processed

    def _process_microdata(self, microdata: List[Dict]) -> List[Dict]:
        """
        Traite et nettoie les données Microdata

        Args:
            microdata: Données Microdata brutes

        Returns:
            Données Microdata nettoyées
        """
        processed = []

        for item in microdata:
            if isinstance(item, dict) and 'type' in item:
                processed.append(item)

        return processed

    def get_schema_types(self, schemas: Dict) -> Set[str]:
        """
        Extrait tous les types de schemas uniques

        Args:
            schemas: Dictionnaire des schemas

        Returns:
            Ensemble des types de schemas (jamais None)
        """
        types = set()

        try:
            # Vérifier que schemas est un dictionnaire valide
            if not schemas or not isinstance(schemas, dict):
                return types

            # JSON-LD
            json_ld_items = schemas.get('json-ld', [])
            if json_ld_items and isinstance(json_ld_items, list):
                for i, item in enumerate(json_ld_items):
                    if isinstance(item, dict) and '@type' in item:
                        schema_type = item['@type']
                        if isinstance(schema_type, list):
                            for t in schema_type:
                                if isinstance(t, str):
                                    # Nettoyer le type (enlever les préfixes comme "schema:")
                                    clean_type = t.split(':')[-1] if ':' in t else t
                                    # Ne garder que les types standards
                                    if clean_type in Config.STANDARD_SCHEMA_TYPES:
                                        types.add(clean_type)
                        elif isinstance(schema_type, str):
                            # Nettoyer le type
                            clean_type = schema_type.split(':')[-1] if ':' in schema_type else schema_type
                            # Ne garder que les types standards
                            if clean_type in Config.STANDARD_SCHEMA_TYPES:
                                types.add(clean_type)

            # Microdata
            microdata_items = schemas.get('microdata', [])
            if microdata_items and isinstance(microdata_items, list):
                for item in microdata_items:
                    if isinstance(item, dict) and 'type' in item:
                        # Les types microdata sont souvent des URLs
                        type_url = item['type']
                        if isinstance(type_url, str):
                            # Extraire le nom du type de l'URL
                            if 'schema.org' in type_url:
                                type_name = type_url.split('/')[-1]
                                if type_name and type_name in Config.STANDARD_SCHEMA_TYPES:
                                    types.add(type_name)
                            else:
                                # Si ce n'est pas une URL schema.org, vérifier si c'est standard
                                if type_url in Config.STANDARD_SCHEMA_TYPES:
                                    types.add(type_url)
                        elif isinstance(type_url, list):
                            for t in type_url:
                                if isinstance(t, str):
                                    if 'schema.org' in t:
                                        type_name = t.split('/')[-1]
                                        if type_name and type_name in Config.STANDARD_SCHEMA_TYPES:
                                            types.add(type_name)
                                    elif t in Config.STANDARD_SCHEMA_TYPES:
                                        types.add(t)

        except Exception as e:
            print(f"Erreur dans get_schema_types: {e}")
            import traceback
            traceback.print_exc()

        # Toujours retourner un ensemble, jamais None
        return types

    def get_schemas_by_type(self, schemas: Dict, schema_type: str) -> List[Dict]:
        """
        Récupère tous les schemas d'un type donné

        Args:
            schemas: Dictionnaire des schemas
            schema_type: Type de schema recherché

        Returns:
            Liste des schemas du type demandé
        """
        matching_schemas = []

        # JSON-LD
        json_ld_items = schemas.get('json-ld', [])
        for schema in json_ld_items:
            if isinstance(schema, dict) and '@type' in schema:
                s_type = schema['@type']
                if isinstance(s_type, str) and s_type == schema_type:
                    matching_schemas.append(schema)
                elif isinstance(s_type, list) and schema_type in s_type:
                    matching_schemas.append(schema)

        # Microdata
        microdata_items = schemas.get('microdata', [])
        for schema in microdata_items:
            if isinstance(schema, dict) and 'type' in schema:
                type_url = schema['type']
                if isinstance(type_url, str):
                    if type_url == schema_type or (
                            'schema.org' in type_url and
                            type_url.split('/')[-1] == schema_type
                    ):
                        matching_schemas.append(schema)

        return matching_schemas

    def get_rich_result_schemas(self, schemas: Dict) -> Set[str]:
        """
        Identifie les schemas qui peuvent générer des résultats enrichis Google

        Args:
            schemas: Dictionnaire des schemas

        Returns:
            Ensemble des types de schemas générant des rich snippets
        """
        # Schemas qui génèrent des résultats enrichis dans Google
        rich_result_types = {
            'Article', 'NewsArticle', 'BlogPosting',  # Articles
            'BreadcrumbList',  # Fils d'Ariane
            'Course',  # Cours
            'Event',  # Événements
            'FAQPage',  # FAQ
            'HowTo',  # Guide pratique
            'JobPosting',  # Offres d'emploi
            'LocalBusiness',  # Entreprise locale
            'Product',  # Produits
            'Recipe',  # Recettes
            'Review', 'AggregateRating',  # Avis et notes
            'VideoObject',  # Vidéos
            'Dataset',  # Ensembles de données
            'SoftwareApplication',  # Applications
            'Book',  # Livres
            'Movie',  # Films
            'MusicRecording',  # Musique
        }

        all_types = self.get_schema_types(schemas)
        return all_types & rich_result_types

    def analyze_schemas_detail(self, schemas: Dict) -> Dict:
        """
        Analyse détaillée des schemas avec distinction rich results

        Args:
            schemas: Dictionnaire des schemas

        Returns:
            Analyse détaillée
        """
        all_types = self.get_schema_types(schemas)
        rich_types = self.get_rich_result_schemas(schemas)

        return {
            'all_schemas': list(all_types),
            'rich_result_schemas': list(rich_types),
            'supporting_schemas': list(all_types - rich_types),
            'counts': {
                'total': len(all_types),
                'rich_results': len(rich_types),
                'supporting': len(all_types - rich_types)
            }
        }

    def analyze_multiple_urls(self, urls: List[str]) -> Dict:
        """
        Analyse plusieurs URLs et compile les résultats

        Args:
            urls: Liste des URLs à analyser

        Returns:
            Dictionnaire avec l'analyse complète
        """
        results = {
            'urls_analyzed': [],
            'all_schemas': {},
            'schema_frequency': {},
            'schema_by_position': {}
        }

        for position, url in enumerate(urls, 1):
            print(f"Analyse de {url} (position {position})...")

            try:
                schemas = self.extract_schemas(url)
                schema_types = self.get_schema_types(schemas)

                # S'assurer que schema_types est un ensemble valide
                if schema_types is None:
                    schema_types = set()

                results['urls_analyzed'].append({
                    'url': url,
                    'position': position,
                    'schemas': schemas,
                    'schema_types': list(schema_types)
                })

                # Compter la fréquence des schemas
                for schema_type in schema_types:
                    if schema_type not in results['schema_frequency']:
                        results['schema_frequency'][schema_type] = 0
                    results['schema_frequency'][schema_type] += 1

                    # Enregistrer les positions où apparaît chaque schema
                    if schema_type not in results['schema_by_position']:
                        results['schema_by_position'][schema_type] = []
                    results['schema_by_position'][schema_type].append(position)

            except Exception as e:
                print(f"Erreur lors de l'analyse de {url}: {e}")
                results['urls_analyzed'].append({
                    'url': url,
                    'position': position,
                    'schemas': {},
                    'schema_types': [],
                    'error': str(e)
                })

        return results