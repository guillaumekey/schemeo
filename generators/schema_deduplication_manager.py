"""
Module de gestion de la déduplication et optimisation des schemas
Version complète avec gestion intelligente des doublons et création automatique de Service pour Review
"""
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import json


class SchemaDeduplicationManager:
    """
    Gestionnaire avancé pour éviter les doublons et optimiser les schemas
    selon les meilleures pratiques Google et Schema.org
    """

    def __init__(self):
        # Relations hiérarchiques (héritage)
        self.schema_hierarchy = {
            'LocalBusiness': ['Organization'],  # LocalBusiness hérite d'Organization
            'Restaurant': ['LocalBusiness', 'Organization'],
            'Store': ['LocalBusiness', 'Organization'],
            'NewsArticle': ['Article'],
            'BlogPosting': ['Article'],
            'MedicalBusiness': ['LocalBusiness', 'Organization'],
        }

        # Définir les relations et dépendances entre schemas
        self.schema_dependencies = {
            'Product': {
                'can_embed': ['Offer', 'AggregateRating', 'Brand'],
                'can_reference': ['Review'],  # Review séparé mais lié
                'requires': []
            },
            'LocalBusiness': {
                'can_embed': ['PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification', 'AggregateRating',
                              'ContactPoint'],
                'can_reference': ['Review'],
                'requires': ['PostalAddress']
            },
            'Organization': {
                'can_embed': ['ContactPoint', 'PostalAddress', 'Logo', 'AggregateRating'],
                'can_reference': ['Review', 'Person'],
                'requires': []
            },
            'Service': {
                'can_embed': ['Offer', 'AggregateRating', 'Provider', 'AreaServed', 'HasOfferCatalog'],
                'can_reference': ['Review', 'Organization'],
                'requires': []
            },
            'Article': {
                'can_embed': ['Person', 'Organization', 'ImageObject'],
                'can_reference': [],
                'requires': ['Person', 'Organization']  # Author et Publisher
            },
            'Event': {
                'can_embed': ['Place', 'PostalAddress', 'Offer', 'Organizer'],
                'can_reference': [],
                'requires': []
            },
            'Recipe': {
                'can_embed': ['NutritionInformation', 'AggregateRating', 'VideoObject'],
                'can_reference': ['Review'],
                'requires': []
            },
            'FAQPage': {
                'can_embed': [],
                'can_reference': [],
                'requires': []
            },
            'Person': {
                'can_embed': ['PostalAddress'],
                'can_reference': ['Organization'],
                'requires': []
            },
            'WebSite': {
                'can_embed': ['SearchAction'],
                'can_reference': ['Organization'],
                'requires': []
            },
            'Review': {
                'can_embed': [],
                'can_reference': ['Service', 'Product', 'Organization', 'LocalBusiness'],
                'requires': []  # Nécessite un élément reviewable mais géré séparément
            }
        }

        # Schemas qui ne doivent jamais être dupliqués (singletons)
        self.singleton_schemas = {
            'WebSite',
            'Organization',
            'BreadcrumbList',
            'SearchAction',
            'FAQPage'
        }

        # Priorité d'ordre dans le @graph
        self.schema_priority = {
            'WebSite': 1,
            'Organization': 2,
            'LocalBusiness': 2,
            'Service': 3,
            'Product': 3,
            'Person': 4,
            'BreadcrumbList': 5,
            'Article': 6,
            'Review': 7,
            'FAQPage': 8,
            'Event': 9,
            'HowTo': 10
        }

    def analyze_selection(self, selected_schemas: List[str]) -> Dict:
        """
        Analyse approfondie de la sélection pour optimisation
        """
        analysis = {
            'hierarchical_conflicts': [],
            'can_be_merged': [],
            'can_be_embedded': [],
            'should_reference': [],
            'missing_dependencies': [],
            'duplicate_functionality': [],
            'recommendations': []
        }

        # Détecter les conflits hiérarchiques
        for schema in selected_schemas:
            if schema in self.schema_hierarchy:
                parents = self.schema_hierarchy[schema]
                for parent in parents:
                    if parent in selected_schemas:
                        analysis['hierarchical_conflicts'].append({
                            'child': schema,
                            'parent': parent,
                            'recommendation': f"Utiliser seulement {schema} car il hérite de {parent}"
                        })

        # Détecter les possibilités d'embedding
        for primary in selected_schemas:
            if primary in self.schema_dependencies:
                deps = self.schema_dependencies[primary]

                # Schemas qui peuvent être intégrés
                for secondary in selected_schemas:
                    if secondary in deps['can_embed']:
                        analysis['can_be_embedded'].append({
                            'parent': primary,
                            'child': secondary,
                            'type': 'embed'
                        })
                    elif secondary in deps.get('can_reference', []):
                        analysis['should_reference'].append({
                            'parent': primary,
                            'child': secondary,
                            'type': 'reference'
                        })

        # Vérifier les dépendances manquantes
        for schema in selected_schemas:
            if schema in self.schema_dependencies:
                required = self.schema_dependencies[schema].get('requires', [])
                for req in required:
                    if req not in selected_schemas:
                        analysis['missing_dependencies'].append({
                            'schema': schema,
                            'missing': req
                        })

        # IMPORTANT : Vérifier si Review a un élément reviewable
        if 'Review' in selected_schemas:
            reviewable_types = ['Service', 'Product', 'LocalBusiness', 'Restaurant',
                                'Store', 'Organization', 'Event', 'Course']
            has_reviewable = any(t in selected_schemas for t in reviewable_types)

            if not has_reviewable:
                analysis['missing_dependencies'].append({
                    'schema': 'Review',
                    'missing': 'Service (ou autre élément reviewable)',
                    'auto_fix': True
                })

        return analysis

    def optimize_schema_selection(self, selected_schemas: List[str]) -> Dict:
        """
        Optimisation intelligente avec gestion complète des doublons
        et ajout automatique de Service si Review est présent
        """
        optimization = {
            'primary_schemas': [],  # Schemas principaux à générer
            'embedded_schemas': defaultdict(list),  # Schemas à intégrer dans d'autres
            'linked_schemas': [],  # Schemas séparés mais liés
            'merged_schemas': [],  # Schemas à fusionner
            'skip_schemas': set(),  # Schemas à ignorer car traités autrement
            'warnings': [],
            'schema_config': {},  # Configuration spécifique par schema
            'auto_added': []  # Schemas ajoutés automatiquement
        }

        # Copie de travail
        remaining_schemas = set(selected_schemas)

        # AJOUT AUTOMATIQUE : Si Review sans élément reviewable, ajouter Service
        if 'Review' in remaining_schemas:
            reviewable_types = ['Service', 'Product', 'LocalBusiness', 'Restaurant',
                                'Store', 'Organization', 'Event', 'Course', 'SoftwareApplication']
            has_reviewable = any(t in remaining_schemas for t in reviewable_types)

            if not has_reviewable:
                # Ajouter Service automatiquement
                remaining_schemas.add('Service')
                optimization['auto_added'].append('Service')
                optimization['warnings'].append(
                    "✓ Service ajouté automatiquement pour supporter Review"
                )

        # Analyse préliminaire
        analysis = self.analyze_selection(list(remaining_schemas))

        # 1. Résoudre les conflits hiérarchiques
        for conflict in analysis['hierarchical_conflicts']:
            child = conflict['child']
            parent = conflict['parent']

            if child in remaining_schemas and parent in remaining_schemas:
                # Garder seulement l'enfant (plus spécifique)
                optimization['merged_schemas'].append({
                    'types': [parent, child],
                    'result_type': child,
                    'multi_type': True  # Utiliser @type multiple
                })
                optimization['warnings'].append(
                    f"✓ {parent} et {child} fusionnés (héritage)"
                )
                remaining_schemas.discard(parent)
                optimization['skip_schemas'].add(parent)

        # 2. Traiter WebSite en premier (singleton)
        if 'WebSite' in remaining_schemas:
            optimization['primary_schemas'].append('WebSite')
            remaining_schemas.discard('WebSite')
            optimization['schema_config']['WebSite'] = {
                'position': 0,  # Toujours en premier
                'embed_search': True
            }

        # 3. Gérer Organization/LocalBusiness
        has_org = 'Organization' in remaining_schemas
        has_local = 'LocalBusiness' in remaining_schemas
        has_restaurant = 'Restaurant' in remaining_schemas
        has_store = 'Store' in remaining_schemas

        if has_local or has_restaurant or has_store:
            # Déterminer le type le plus spécifique
            specific_type = None
            if has_restaurant:
                specific_type = 'Restaurant'
            elif has_store:
                specific_type = 'Store'
            else:
                specific_type = 'LocalBusiness'

            # Créer un schema avec types multiples si Organization aussi présent
            if has_org:
                optimization['merged_schemas'].append({
                    'types': ['Organization', specific_type],
                    'result_type': specific_type,
                    'multi_type': True
                })
                remaining_schemas.discard('Organization')
                optimization['skip_schemas'].add('Organization')

            optimization['primary_schemas'].append(specific_type)
            remaining_schemas.discard(specific_type)

            # Marquer les autres comme skip
            for schema in ['LocalBusiness', 'Restaurant', 'Store']:
                if schema != specific_type and schema in remaining_schemas:
                    remaining_schemas.discard(schema)
                    optimization['skip_schemas'].add(schema)
        elif has_org:
            optimization['primary_schemas'].append('Organization')
            remaining_schemas.discard('Organization')

        # 4. Gérer Service et Product
        for main_schema in ['Service', 'Product']:
            if main_schema in remaining_schemas:
                optimization['primary_schemas'].append(main_schema)
                remaining_schemas.discard(main_schema)

                # Configuration pour AggregateRating et Review
                optimization['schema_config'][main_schema] = {
                    'embed_aggregate': False,  # Par défaut
                    'reference_reviews': False
                }

        # 5. Gérer AggregateRating et Review
        has_aggregate = 'AggregateRating' in remaining_schemas
        has_review = 'Review' in remaining_schemas

        if has_aggregate or has_review:
            # Trouver l'entité principale
            main_entity = None
            for schema in ['Service', 'Product', 'LocalBusiness', 'Restaurant', 'Store', 'Organization']:
                if schema in optimization['primary_schemas'] or \
                        any(m['result_type'] == schema for m in optimization['merged_schemas']):
                    main_entity = schema
                    break

            if main_entity:
                # Initialiser la configuration si elle n'existe pas
                if main_entity not in optimization['schema_config']:
                    optimization['schema_config'][main_entity] = {}

                if has_aggregate and has_review:
                    # AggregateRating intégré, Review séparé
                    optimization['embedded_schemas'][main_entity].append('AggregateRating')
                    optimization['linked_schemas'].append('Review')
                    optimization['warnings'].append(
                        f"✓ AggregateRating dans {main_entity}, Review séparé"
                    )
                    remaining_schemas.discard('AggregateRating')
                    remaining_schemas.discard('Review')
                    optimization['schema_config'][main_entity]['embed_aggregate'] = True

                elif has_aggregate:
                    # Seulement AggregateRating
                    optimization['embedded_schemas'][main_entity].append('AggregateRating')
                    remaining_schemas.discard('AggregateRating')
                    optimization['schema_config'][main_entity]['embed_aggregate'] = True

                elif has_review:
                    # Seulement Review
                    optimization['linked_schemas'].append('Review')
                    remaining_schemas.discard('Review')
            else:
                # Pas d'entité principale, garder séparés
                if has_aggregate:
                    optimization['linked_schemas'].append('AggregateRating')
                    remaining_schemas.discard('AggregateRating')
                if has_review:
                    optimization['linked_schemas'].append('Review')
                    remaining_schemas.discard('Review')

        # 6. Gérer Person
        if 'Person' in remaining_schemas:
            optimization['linked_schemas'].append('Person')
            remaining_schemas.discard('Person')

        # 7. Gérer les Articles et variantes
        article_types = ['Article', 'NewsArticle', 'BlogPosting']
        present_articles = [a for a in article_types if a in remaining_schemas]

        if present_articles:
            # Garder le plus spécifique
            if 'NewsArticle' in present_articles:
                optimization['primary_schemas'].append('NewsArticle')
                for other in present_articles:
                    remaining_schemas.discard(other)
            elif 'BlogPosting' in present_articles:
                optimization['primary_schemas'].append('BlogPosting')
                for other in present_articles:
                    remaining_schemas.discard(other)
            else:
                optimization['primary_schemas'].append('Article')
                remaining_schemas.discard('Article')

        # 8. Gérer les schemas restants par ordre de priorité
        sorted_remaining = sorted(
            remaining_schemas,
            key=lambda x: self.schema_priority.get(x, 999)
        )

        for schema in sorted_remaining:
            if schema not in optimization['skip_schemas']:
                optimization['linked_schemas'].append(schema)

        return optimization


class SchemaGeneratorOptimized:
    """
    Générateur de schemas avec optimisation avancée et zéro doublon
    """

    def __init__(self, base_generator):
        self.base_generator = base_generator
        self.dedup_manager = SchemaDeduplicationManager()
        self.generated_schemas = {}  # Dictionnaire pour tracking par type
        self.generated_ids = set()  # Set des @id générés

    def generate_optimized_schemas(self,
                                   selected_schemas: List[str],
                                   client_info: Dict,
                                   additional_data: Dict = None,
                                   include_optional: bool = True) -> Tuple[List[Dict], List[str]]:
        """
        Génération optimisée avec garantie zéro doublon et Service automatique pour Review
        """
        messages = []
        self.generated_schemas = {}
        self.generated_ids = set()

        # 1. Optimisation de la sélection (inclut l'ajout automatique de Service si nécessaire)
        optimization = self.dedup_manager.optimize_schema_selection(selected_schemas)
        messages.extend(optimization['warnings'])

        # 2. Préparation des données
        prepared_data = self._prepare_data_context(additional_data, optimization)

        # Si Service a été ajouté automatiquement, préparer ses données
        if 'Service' in optimization['auto_added'] and prepared_data:
            if 'service_name' not in prepared_data:
                prepared_data['service_name'] = prepared_data.get('itemreviewed_name',
                                                                  'Agence marketing digital')
            if 'service_type' not in prepared_data:
                prepared_data['service_type'] = 'Marketing Agency'
            if 'service_description' not in prepared_data:
                prepared_data['service_description'] = client_info.get('description', '')

        # 3. Génération des schemas fusionnés
        for merge_config in optimization['merged_schemas']:
            schema = self._generate_merged_schema(
                merge_config,
                client_info,
                prepared_data,
                include_optional,
                optimization
            )
            if schema:
                self._register_schema(schema)

        # 4. Génération des schemas primaires
        for schema_type in optimization['primary_schemas']:
            # Vérifier si déjà généré
            if self._is_already_generated(schema_type):
                continue

            schema = self._generate_primary_schema(
                schema_type,
                client_info,
                prepared_data,
                include_optional,
                optimization
            )
            if schema:
                self._register_schema(schema)

        # 5. Génération des schemas liés
        for schema_type in optimization['linked_schemas']:
            if self._is_already_generated(schema_type):
                continue

            schema = self.base_generator.generate_schema(
                schema_type,
                client_info,
                prepared_data,
                include_optional
            )
            if schema:
                # Si c'est un Review, s'assurer qu'il référence le bon Service
                if schema_type == 'Review' and 'Service' in optimization['auto_added']:
                    # Forcer la référence au Service créé
                    schema['itemReviewed'] = {
                        "@id": f"{client_info.get('website', '')}#service"
                    }

                self._register_schema(schema)

        # 6. Assemblage final et nettoyage
        final_schemas = self._assemble_final_schemas(client_info)

        # 7. Vérification finale : s'assurer que Review a un élément reviewable
        final_schemas = self._ensure_review_has_target(final_schemas, client_info, prepared_data)

        # 8. Structure @graph si multiple
        if len(final_schemas) > 1:
            result = [{
                "@context": "https://schema.org",
                "@graph": final_schemas
            }]
        else:
            result = final_schemas

        messages.append(f"✨ {len(final_schemas)} schemas générés sans doublon")
        return result, messages

    def _ensure_review_has_target(self, schemas: List[Dict],
                                  client_info: Dict,
                                  data: Dict) -> List[Dict]:
        """
        Vérifie que chaque Review a un élément reviewable valide
        """
        has_review = any(s.get('@type') == 'Review' for s in schemas)

        if has_review:
            # Chercher un élément reviewable
            reviewable_types = ['Service', 'Product', 'LocalBusiness', 'Restaurant',
                                'Store', 'Organization', 'Event', 'Course']
            reviewable_schema = None

            for schema in schemas:
                schema_type = schema.get('@type')
                if isinstance(schema_type, list):
                    if any(t in reviewable_types for t in schema_type):
                        reviewable_schema = schema
                        break
                elif schema_type in reviewable_types:
                    reviewable_schema = schema
                    break

            # Si pas d'élément reviewable, créer un Service
            if not reviewable_schema:
                service_schema = {
                    "@context": "https://schema.org",
                    "@type": "Service",
                    "name": data.get('itemreviewed_name',
                                     data.get('service_name', 'Agence marketing digital')),
                    "description": data.get('service_description',
                                            client_info.get('description', '')),
                    "provider": {
                        "@id": f"{client_info.get('website', '')}#organization"
                    },
                    "serviceType": data.get('service_type', 'Marketing Agency'),
                    "@id": f"{client_info.get('website', '')}#service"
                }

                # Insérer le Service après WebSite si présent
                insert_pos = 0
                for i, schema in enumerate(schemas):
                    if schema.get('@type') == 'WebSite':
                        insert_pos = i + 1
                        break

                schemas.insert(insert_pos, service_schema)
                reviewable_schema = service_schema

            # Mettre à jour les Reviews pour référencer l'élément
            for schema in schemas:
                if schema.get('@type') == 'Review':
                    if '@id' in reviewable_schema:
                        schema['itemReviewed'] = {"@id": reviewable_schema['@id']}

        return schemas

    def _prepare_data_context(self, additional_data: Dict, optimization: Dict) -> Dict:
        """
        Prépare les données en fonction du contexte d'optimisation
        """
        if not additional_data:
            return {}

        prepared = additional_data.copy()

        # Conserver toutes les données si AggregateRating et Review coexistent
        has_both_ratings = any(
            'AggregateRating' in embedded
            for embedded in optimization['embedded_schemas'].values()
        ) and 'Review' in optimization['linked_schemas']

        if has_both_ratings:
            # Ne rien filtrer, garder tout
            return prepared

        return prepared

    def _generate_merged_schema(self,
                                merge_config: Dict,
                                client_info: Dict,
                                data: Dict,
                                include_optional: bool,
                                optimization: Dict) -> Optional[Dict]:
        """
        Génère un schema avec types multiples (fusion)
        """
        result_type = merge_config['result_type']
        schema = self.base_generator.generate_schema(
            result_type,
            client_info,
            data,
            include_optional
        )

        if schema and merge_config.get('multi_type'):
            # Appliquer les types multiples
            schema['@type'] = merge_config['types']

            # ID unique pour éviter les doublons
            schema['@id'] = f"{client_info.get('website', '')}#organization"

            # Ajouter les embeddings si configurés
            embedded = optimization['embedded_schemas'].get(result_type, [])
            if 'AggregateRating' in embedded:
                self._add_aggregate_rating(schema, data)

        return schema

    def _generate_primary_schema(self,
                                 schema_type: str,
                                 client_info: Dict,
                                 data: Dict,
                                 include_optional: bool,
                                 optimization: Dict) -> Optional[Dict]:
        """
        Génère un schema primaire avec ses embeddings
        """
        schema = self.base_generator.generate_schema(
            schema_type,
            client_info,
            data,
            include_optional
        )

        if not schema:
            return None

        # Ajouter les schemas intégrés
        embedded = optimization['embedded_schemas'].get(schema_type, [])
        config = optimization['schema_config'].get(schema_type, {})

        # Intégrer AggregateRating si configuré
        if 'AggregateRating' in embedded or config.get('embed_aggregate'):
            self._add_aggregate_rating(schema, data)

        # NE PAS intégrer Review dans le schema
        # Les Reviews doivent rester des schemas séparés

        return schema

    def _add_aggregate_rating(self, schema: Dict, data: Dict) -> None:
        """
        Ajoute un AggregateRating à un schema
        """
        if 'rating_value' in data:
            schema['aggregateRating'] = {
                "@type": "AggregateRating",
                "ratingValue": str(data.get('rating_value', '4.5')),
                "bestRating": str(data.get('best_rating', '5')),
                "worstRating": str(data.get('worst_rating', '1')),
                "ratingCount": str(data.get('review_count', '1'))
            }

    def _register_schema(self, schema: Dict) -> None:
        """
        Enregistre un schema généré pour éviter les doublons
        """
        if not schema:
            return

        # Extraire le type
        schema_type = schema.get('@type')
        if isinstance(schema_type, list):
            for t in schema_type:
                self.generated_schemas[t] = schema
        else:
            self.generated_schemas[schema_type] = schema

        # Enregistrer l'ID
        if '@id' in schema:
            self.generated_ids.add(schema['@id'])

    def _is_already_generated(self, schema_type: str) -> bool:
        """
        Vérifie si un type de schema a déjà été généré
        """
        return schema_type in self.generated_schemas

    def _assemble_final_schemas(self, client_info: Dict) -> List[Dict]:
        """
        Assemble et nettoie les schemas finaux sans doublons
        """
        final_schemas = []
        seen_combinations = set()
        website_url = client_info.get('website', '')

        # Trier par priorité
        priority_order = self.dedup_manager.schema_priority

        # Créer une liste unique de schemas
        unique_schemas = {}
        for schema_type, schema in self.generated_schemas.items():
            if not schema:
                continue

            # Créer une clé unique basée sur le type et l'ID
            schema_types = schema.get('@type', schema_type)
            if isinstance(schema_types, list):
                type_key = tuple(sorted(schema_types))
            else:
                type_key = (schema_types,)

            # Éviter les doublons basés sur la combinaison de types
            if type_key not in seen_combinations:
                seen_combinations.add(type_key)

                # Nettoyer le schema
                cleaned = self._clean_schema(schema)

                # Assurer un @id unique
                if '@id' not in cleaned:
                    cleaned['@id'] = self._generate_unique_id(
                        schema_types[0] if isinstance(schema_types, list) else schema_types,
                        website_url
                    )

                # Ajouter à la map avec priorité
                priority = min(
                    priority_order.get(t, 999)
                    for t in (schema_types if isinstance(schema_types, list) else [schema_types])
                )
                unique_schemas[cleaned['@id']] = (priority, cleaned)

        # Trier par priorité et assembler
        sorted_schemas = sorted(unique_schemas.values(), key=lambda x: x[0])
        final_schemas = [schema for _, schema in sorted_schemas]

        return final_schemas

    def _generate_unique_id(self, schema_type: str, base_url: str) -> str:
        """
        Génère un @id unique pour un schema
        """
        id_mapping = {
            'WebSite': '#website',
            'Organization': '#organization',
            'LocalBusiness': '#organization',
            'Restaurant': '#organization',
            'Store': '#organization',
            'Person': '#person',
            'Service': '#service',
            'Product': '#product',
            'Article': '#article',
            'NewsArticle': '#article',
            'BlogPosting': '#article',
            'BreadcrumbList': '#breadcrumb',
            'FAQPage': '#faq',
            'Review': '#review',
            'Event': '#event',
            'HowTo': '#howto'
        }

        suffix = id_mapping.get(schema_type, f'#{schema_type.lower()}')
        base_id = f"{base_url}{suffix}"

        # Si l'ID existe déjà, ajouter un compteur
        if base_id in self.generated_ids:
            counter = 1
            while f"{base_id}-{counter}" in self.generated_ids:
                counter += 1
            return f"{base_id}-{counter}"

        return base_id

    def _clean_schema(self, schema: Dict) -> Dict:
        """
        Nettoie un schema en supprimant les valeurs vides
        """
        if not isinstance(schema, dict):
            return schema

        cleaned = {}
        for key, value in schema.items():
            # Toujours garder les propriétés JSON-LD
            if key.startswith('@'):
                cleaned[key] = value
            else:
                # Nettoyer récursivement
                if isinstance(value, dict):
                    cleaned_value = self._clean_schema(value)
                    if cleaned_value:
                        cleaned[key] = cleaned_value
                elif isinstance(value, list):
                    cleaned_list = []
                    for item in value:
                        if isinstance(item, dict):
                            cleaned_item = self._clean_schema(item)
                            if cleaned_item:
                                cleaned_list.append(cleaned_item)
                        elif item not in [None, "", []]:
                            cleaned_list.append(item)
                    if cleaned_list:
                        cleaned[key] = cleaned_list
                elif value not in [None, "", []]:
                    cleaned[key] = value

        return cleaned if cleaned else None