"""
Module complet pour scraper et extraire les schemas des pages web
Version finale avec corrections pour @graph et détection robuste
"""
import requests
import json
from bs4 import BeautifulSoup
import extruct
import re
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin
from config import Config


class SchemaScraper:
    """Classe complète pour scraper et extraire les schemas des pages"""

    def __init__(self):
        self.session = requests.Session()

        # Headers réalistes pour éviter les blocages
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape le contenu HTML d'une URL avec fallback multiple User-Agents

        Args:
            url: URL à scraper

        Returns:
            Contenu HTML ou None si erreur
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.1 Safari/537.36',
            'Mozilla/5.0 (compatible; SEOAnalyzer/1.0; +https://example.com/bot)'
        ]

        for i, ua in enumerate(user_agents):
            try:
                # Créer une nouvelle session pour chaque tentative
                session = requests.Session()
                session.headers.update({
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })

                response = session.get(
                    url,
                    timeout=30,
                    allow_redirects=True,
                    verify=True
                )
                response.raise_for_status()

                # Vérifier que c'est du HTML
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type:
                    print(f"Type de contenu inattendu: {content_type}")
                    continue

                return response.text

            except requests.exceptions.SSLError:
                try:
                    # Réessayer sans vérification SSL
                    response = session.get(
                        url,
                        timeout=30,
                        allow_redirects=True,
                        verify=False
                    )
                    response.raise_for_status()
                    return response.text
                except Exception as e:
                    print(f"Erreur SSL fallback pour User-Agent {i + 1}: {e}")
                    continue

            except requests.exceptions.Timeout:
                print(f"Timeout avec User-Agent {i + 1}")
                continue

            except requests.exceptions.RequestException as e:
                print(f"Erreur avec User-Agent {i + 1}: {e}")
                continue

        print(f"Échec du scraping pour {url} avec tous les User-Agents")
        return None

    def extract_schemas(self, url: str, html: Optional[str] = None) -> Dict:
        """
        Extrait tous les schemas d'une page avec détection améliorée

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
            print(f"Analyse de {url}...")
            print(f"Taille HTML: {len(html)} caractères")

            # Parser le HTML avec BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # 1. EXTRACTION JSON-LD MANUELLE (méthode principale)
            json_ld_schemas = []

            # Chercher tous les scripts JSON-LD
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            print(f"Trouvé {len(json_ld_scripts)} scripts JSON-LD")

            for i, script in enumerate(json_ld_scripts):
                try:
                    script_content = script.string or script.get_text()
                    if script_content:
                        script_content = script_content.strip()

                        # Parser le JSON
                        data = json.loads(script_content)

                        if isinstance(data, list):
                            json_ld_schemas.extend(data)
                            print(f"Script {i + 1}: liste de {len(data)} éléments")
                        else:
                            json_ld_schemas.append(data)
                            print(f"Script {i + 1}: objet unique")

                except json.JSONDecodeError as e:
                    print(f"Erreur JSON dans script {i + 1}: {e}")
                except Exception as e:
                    print(f"Erreur générale script {i + 1}: {e}")

            # 2. EXTRACTION AVEC EXTRUCT (backup)
            extruct_data = {'microdata': [], 'rdfa': [], 'opengraph': []}
            try:
                extruct_data = extruct.extract(
                    html,
                    base_url=url,
                    syntaxes=['json-ld', 'microdata', 'rdfa', 'opengraph']
                )

                # Ajouter les données extruct JSON-LD si on n'a rien trouvé manuellement
                extruct_json_ld = extruct_data.get('json-ld', [])
                if extruct_json_ld and not json_ld_schemas:
                    json_ld_schemas.extend(extruct_json_ld)
                    print(f"Ajouté {len(extruct_json_ld)} schemas via extruct")

            except Exception as e:
                print(f"Erreur extruct: {e}")

            # 3. EXTRACTION MICRODATA MANUELLE
            microdata_items = []
            try:
                microdata_elements = soup.find_all(attrs={"itemtype": True})
                print(f"Trouvé {len(microdata_elements)} éléments microdata")

                for element in microdata_elements:
                    microdata_item = self._extract_microdata_item(element)
                    if microdata_item:
                        microdata_items.append(microdata_item)

            except Exception as e:
                print(f"Erreur extraction microdata: {e}")

            # 4. COMPILATION DES RÉSULTATS
            schemas = {
                'json-ld': self._process_json_ld(json_ld_schemas),
                'microdata': microdata_items or extruct_data.get('microdata', []),
                'rdfa': extruct_data.get('rdfa', []),
                'opengraph': extruct_data.get('opengraph', [])
            }

            # 5. STATISTIQUES
            total_schemas = (
                    len(schemas['json-ld']) +
                    len(schemas['microdata']) +
                    len(schemas['rdfa']) +
                    len(schemas['opengraph'])
            )

            print(f"Résultats finaux:")
            print(f"   JSON-LD: {len(schemas['json-ld'])}")
            print(f"   Microdata: {len(schemas['microdata'])}")
            print(f"   RDFa: {len(schemas['rdfa'])}")
            print(f"   OpenGraph: {len(schemas['opengraph'])}")
            print(f"   TOTAL: {total_schemas}")

            return schemas

        except Exception as e:
            print(f"Erreur lors de l'extraction des schemas de {url}: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _extract_microdata_item(self, element) -> Optional[Dict]:
        """
        Extrait un item microdata d'un élément HTML

        Args:
            element: Élément BeautifulSoup

        Returns:
            Dictionnaire représentant l'item microdata
        """
        try:
            itemtype = element.get('itemtype')
            if not itemtype:
                return None

            item = {
                'type': itemtype,
                'properties': {}
            }

            # Chercher toutes les propriétés dans cet élément
            prop_elements = element.find_all(attrs={"itemprop": True})

            for prop_element in prop_elements:
                prop_name = prop_element.get('itemprop')
                if not prop_name:
                    continue

                # Extraire la valeur selon le type d'élément
                if prop_element.name == 'meta':
                    value = prop_element.get('content', '')
                elif prop_element.name == 'a':
                    value = prop_element.get('href', prop_element.get_text().strip())
                elif prop_element.name == 'img':
                    value = prop_element.get('src', prop_element.get('alt', ''))
                elif prop_element.name == 'time':
                    value = prop_element.get('datetime', prop_element.get_text().strip())
                else:
                    value = prop_element.get_text().strip()

                if value:
                    if prop_name in item['properties']:
                        # Si la propriété existe déjà, créer une liste
                        if not isinstance(item['properties'][prop_name], list):
                            item['properties'][prop_name] = [item['properties'][prop_name]]
                        item['properties'][prop_name].append(value)
                    else:
                        item['properties'][prop_name] = value

            return item if item['properties'] else None

        except Exception as e:
            print(f"Erreur extraction microdata item: {e}")
            return None

    def _process_json_ld(self, json_ld_data: List[Dict]) -> List[Dict]:
        """
        Traite et nettoie les données JSON-LD avec support complet des @graph
        CORRECTION PRINCIPALE pour les structures @graph

        Args:
            json_ld_data: Données JSON-LD brutes

        Returns:
            Données JSON-LD nettoyées et dédupliquées
        """
        processed = []
        seen_items = set()

        print(f"Traitement de {len(json_ld_data)} items JSON-LD")

        for i, item in enumerate(json_ld_data):
            if not isinstance(item, dict):
                continue

            print(f"Item {i + 1}: {list(item.keys())}")

            # CORRECTION PRINCIPALE: Gérer les @graph
            if '@graph' in item:
                print(f"Structure @graph détectée")
                graph_items = item.get('@graph', [])

                if isinstance(graph_items, list):
                    print(f"   {len(graph_items)} éléments dans le @graph")

                    for j, graph_item in enumerate(graph_items):
                        if isinstance(graph_item, dict) and '@type' in graph_item:
                            schema_type = graph_item.get('@type', '')
                            print(f"   Graph item {j + 1}: @type = {schema_type}")

                            # Dédupliquer et ajouter
                            processed_item = self._deduplicate_schema(graph_item, seen_items)
                            if processed_item:
                                processed.append(processed_item)
                                print(f"      Ajouté: {schema_type}")
                            else:
                                print(f"      Ignoré (dupliqué): {schema_type}")
                else:
                    print(f"   @graph n'est pas une liste: {type(graph_items)}")

            elif '@type' in item:
                # Schema individuel (pas dans un @graph)
                schema_type = item.get('@type', '')
                print(f"Schema individuel: @type = {schema_type}")

                processed_item = self._deduplicate_schema(item, seen_items)
                if processed_item:
                    processed.append(processed_item)
                    print(f"   Ajouté: {schema_type}")
                else:
                    print(f"   Ignoré (dupliqué): {schema_type}")
            else:
                print(f"Item sans @type ni @graph ignoré")

        print(f"Traitement terminé: {len(json_ld_data)} items -> {len(processed)} schemas uniques")
        return processed

    def _deduplicate_schema(self, schema: Dict, seen_items: Set) -> Optional[Dict]:
        """
        Déduplique un schema en utilisant @id ou contenu

        Args:
            schema: Schema à vérifier
            seen_items: Set des items déjà vus

        Returns:
            Schema si unique, None si dupliqué
        """
        # Utiliser @id si présent
        schema_id = schema.get('@id')
        if schema_id:
            if schema_id in seen_items:
                return None
            seen_items.add(schema_id)
            return schema

        # Créer une signature basée sur @type et quelques champs clés
        schema_type = schema.get('@type', '')
        if isinstance(schema_type, list):
            schema_type = schema_type[0] if schema_type else ''

        name = schema.get('name', '')
        url = schema.get('url', '')

        signature = f"{schema_type}:{name}:{url}"

        if signature in seen_items:
            return None

        seen_items.add(signature)
        return schema

    def get_schema_types(self, schemas: Dict) -> Set[str]:
        """
        Extrait tous les types de schemas uniques - VERSION INCLUSIVE

        Args:
            schemas: Dictionnaire des schemas

        Returns:
            Ensemble des types de schemas (jamais None)
        """
        types = set()

        try:
            if not schemas or not isinstance(schemas, dict):
                return types

            print(f"Extraction des types de schemas...")

            # JSON-LD
            json_ld_items = schemas.get('json-ld', [])
            if isinstance(json_ld_items, list):
                print(f"Analyse de {len(json_ld_items)} items JSON-LD")
                for item in json_ld_items:
                    if isinstance(item, dict) and '@type' in item:
                        schema_type = item['@type']

                        if isinstance(schema_type, str):
                            type_name = schema_type.split('/')[-1] if '/' in schema_type else schema_type
                            clean_type = type_name.split(':')[-1] if ':' in type_name else type_name
                            if clean_type and len(clean_type) > 1:
                                types.add(clean_type)
                                print(f"  Trouvé: {clean_type}")

                        elif isinstance(schema_type, list):
                            for t in schema_type:
                                if isinstance(t, str):
                                    type_name = t.split('/')[-1] if '/' in t else t
                                    clean_type = type_name.split(':')[-1] if ':' in type_name else type_name
                                    if clean_type and len(clean_type) > 1:
                                        types.add(clean_type)
                                        print(f"  Trouvé: {clean_type}")

            # Microdata
            microdata_items = schemas.get('microdata', [])
            if isinstance(microdata_items, list):
                print(f"Analyse de {len(microdata_items)} items Microdata")
                for item in microdata_items:
                    if isinstance(item, dict) and 'type' in item:
                        type_url = item['type']
                        if isinstance(type_url, str):
                            if 'schema.org' in type_url:
                                type_name = type_url.split('/')[-1]
                            else:
                                type_name = type_url

                            if type_name and len(type_name) > 1:
                                types.add(type_name)
                                print(f"  Trouvé: {type_name}")

            # RDFa
            rdfa_items = schemas.get('rdfa', [])
            if isinstance(rdfa_items, list):
                for item in rdfa_items:
                    if isinstance(item, dict) and '@type' in item:
                        schema_types = item['@type']
                        if isinstance(schema_types, list):
                            for schema_type in schema_types:
                                if isinstance(schema_type, str):
                                    type_name = schema_type.split('/')[-1] if '/' in schema_type else schema_type
                                    clean_type = type_name.split(':')[-1] if ':' in type_name else type_name
                                    if clean_type and len(clean_type) > 1:
                                        types.add(clean_type)

            print(f"Total des types trouvés: {len(types)}")
            if types:
                print(f"Types: {', '.join(sorted(types))}")
            else:
                print("Aucun type de schema détecté")

        except Exception as e:
            print(f"Erreur dans get_schema_types: {e}")
            import traceback
            traceback.print_exc()

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

        try:
            # JSON-LD
            json_ld_items = schemas.get('json-ld', [])
            if isinstance(json_ld_items, list):
                for schema in json_ld_items:
                    if isinstance(schema, dict) and '@type' in schema:
                        s_type = schema['@type']

                        # Normaliser le type
                        if isinstance(s_type, str):
                            type_name = s_type.split('/')[-1] if '/' in s_type else s_type
                            clean_type = type_name.split(':')[-1] if ':' in type_name else type_name
                            if clean_type == schema_type:
                                matching_schemas.append(schema)
                        elif isinstance(s_type, list):
                            for t in s_type:
                                if isinstance(t, str):
                                    type_name = t.split('/')[-1] if '/' in t else t
                                    clean_type = type_name.split(':')[-1] if ':' in type_name else type_name
                                    if clean_type == schema_type:
                                        matching_schemas.append(schema)
                                        break

            # Microdata
            microdata_items = schemas.get('microdata', [])
            if isinstance(microdata_items, list):
                for schema in microdata_items:
                    if isinstance(schema, dict) and 'type' in schema:
                        type_url = schema['type']
                        if isinstance(type_url, str) and 'schema.org' in type_url:
                            type_name = type_url.split('/')[-1]
                            if type_name == schema_type:
                                matching_schemas.append(schema)

        except Exception as e:
            print(f"Erreur dans get_schemas_by_type: {e}")

        return matching_schemas

    def analyze_multiple_urls(self, urls: List[str]) -> Dict:
        """
        Analyse plusieurs URLs et compile les résultats

        Args:
            urls: Liste des URLs à analyser

        Returns:
            Dictionnaire avec l'analyse compilée
        """
        results = {
            'urls_analyzed': [],
            'schema_frequency': {},
            'schema_by_position': {},
            'total_urls': len(urls)
        }

        for position, url in enumerate(urls, 1):
            try:
                print(f"\nAnalyse URL {position}/{len(urls)}: {url}")

                schemas = self.extract_schemas(url)
                schema_types = self.get_schema_types(schemas)

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

    def analyze_serp_results(self, serp_results: List[Dict]) -> Dict:
        """
        Analyse les résultats SERP pour extraire les schemas

        Args:
            serp_results: Liste des résultats organiques de ValueSERP

        Returns:
            Dictionnaire avec l'analyse des schemas
        """
        # Extraire les URLs des résultats SERP
        urls = []
        for result in serp_results:
            if 'link' in result:
                urls.append(result['link'])

        # Limiter à 10 URLs maximum
        urls = urls[:10]

        print(f"Analyse des schemas pour {len(urls)} URLs du SERP")

        # Utiliser la méthode existante analyze_multiple_urls
        analysis_results = self.analyze_multiple_urls(urls)

        # Ajouter des métadonnées supplémentaires
        analysis_results['serp_data'] = serp_results
        analysis_results['analyzed_at'] = __import__('datetime').datetime.now().isoformat()

        return analysis_results

    def debug_schema_detection(self, url: str) -> Dict:
        """
        Méthode de débogage pour analyser pourquoi les schémas ne sont pas détectés

        Args:
            url: URL à analyser

        Returns:
            Rapport de débogage détaillé
        """
        debug_info = {
            'url': url,
            'html_size': 0,
            'scripts_found': 0,
            'json_ld_scripts': [],
            'microdata_elements': 0,
            'extraction_errors': [],
            'raw_schemas': {},
            'processing_log': []
        }

        try:
            print(f"\nDÉBOGAGE DÉTAILLÉ POUR: {url}")
            print("=" * 80)

            # 1. SCRAPING
            print("1️⃣ ÉTAPE SCRAPING...")
            html = self.scrape_url(url)

            if not html:
                debug_info['extraction_errors'].append("Impossible de récupérer le HTML")
                return debug_info

            debug_info['html_size'] = len(html)
            print(f"   HTML récupéré: {len(html):,} caractères")

            # 2. PARSING HTML
            print("2️⃣ ÉTAPE PARSING...")
            soup = BeautifulSoup(html, 'html.parser')

            # 3. RECHERCHE SCRIPTS JSON-LD
            print("3️⃣ RECHERCHE SCRIPTS JSON-LD...")
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            debug_info['scripts_found'] = len(json_ld_scripts)
            print(f"   Scripts JSON-LD trouvés: {len(json_ld_scripts)}")

            for i, script in enumerate(json_ld_scripts):
                content = script.string or script.get_text()
                if content:
                    content = content.strip()
                    debug_info['json_ld_scripts'].append({
                        'index': i,
                        'length': len(content),
                        'preview': content[:200] + "..." if len(content) > 200 else content,
                        'raw_content': content
                    })
                    print(f"   Script {i + 1}: {len(content)} caractères")

            # 4. EXTRACTION AVEC EXTRUCT
            print("4️⃣ EXTRACTION AVEC EXTRUCT...")
            try:
                extruct_data = extruct.extract(html, base_url=url)

                for format_type in ['json-ld', 'microdata', 'rdfa', 'opengraph']:
                    data = extruct_data.get(format_type, [])
                    debug_info['raw_schemas'][format_type] = data
                    print(f"   {format_type}: {len(data)} éléments")

            except Exception as e:
                debug_info['extraction_errors'].append(f"Erreur extruct: {str(e)}")
                print(f"   Erreur extruct: {e}")

            # 5. RÉSUMÉ
            print("5️⃣ RÉSUMÉ DU DIAGNOSTIC...")
            if debug_info['scripts_found'] == 0:
                print("   PROBLÈME: Aucun script JSON-LD détecté")
            else:
                print("   OK: Scripts JSON-LD détectés")

        except Exception as e:
            debug_info['extraction_errors'].append(f"Erreur générale: {str(e)}")
            print(f"Erreur générale: {e}")

        return debug_info

    def test_graph_extraction(self, url: str):
        """
        Test spécifique pour les structures @graph
        """
        print(f"\nTEST SPÉCIFIQUE POUR: {url}")
        print("=" * 60)

        # Récupérer le HTML et parser
        html = self.scrape_url(url)
        if not html:
            print("Impossible de récupérer le HTML")
            return set()

        soup = BeautifulSoup(html, 'html.parser')
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        print(f"{len(json_ld_scripts)} scripts JSON-LD trouvés")

        # Parser chaque script
        all_schemas = []
        for i, script in enumerate(json_ld_scripts):
            content = script.string or script.get_text()
            if not content:
                continue

            content = content.strip()
            print(f"\nScript {i + 1}:")
            print(f"   Taille: {len(content)} caractères")

            try:
                data = json.loads(content)
                print(f"   JSON valide")

                if isinstance(data, dict):
                    if '@graph' in data:
                        graph_items = data.get('@graph', [])
                        print(f"   @graph avec {len(graph_items)} éléments")

                        for j, item in enumerate(graph_items):
                            if '@type' in item:
                                item_type = item.get('@type')
                                print(f"      {j + 1}. @type: {item_type}")

                    elif '@type' in data:
                        print(f"   Schema simple: {data.get('@type')}")

                    all_schemas.append(data)

            except json.JSONDecodeError as e:
                print(f"   Erreur JSON: {e}")

        # Traiter avec la méthode corrigée
        print(f"\nTRAITEMENT AVEC MÉTHODE CORRIGÉE:")
        processed_schemas = self._process_json_ld(all_schemas)

        # Extraire les types
        types = self.get_schema_types({'json-ld': processed_schemas})

        print(f"\nRÉSULTAT FINAL:")
        print(f"   Schemas traités: {len(processed_schemas)}")
        print(f"   Types détectés: {types}")
        print(f"   Nombre de types: {len(types)}")

        return types