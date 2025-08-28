"""
Module pour générer des schemas Schema.org complets avec toutes les propriétés
Version optimisée pour éviter les redondances et corriger le problème Review
"""
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

# Import des modules internes
from .schema_templates import SchemaTemplates
from .schema_constants import SchemaConstants
from .schema_fillers import SCHEMA_FILLERS
from .schema_validators import SchemaDataValidator
from .schema_deduplication_manager import SchemaDeduplicationManager, SchemaGeneratorOptimized


class SchemaGenerator:
    """Classe pour générer des schemas Schema.org complets et optimisés"""

    def __init__(self):
        self.templates = SchemaTemplates.get_all_templates()
        self.constants = SchemaConstants()
        self.validator = SchemaDataValidator()

        # Charger les configurations depuis les constantes
        self.required_fields = self.constants.get_required_fields()
        self.recommended_fields = self.constants.get_recommended_fields()
        self.enumerations = self.constants.get_schema_enumerations()

        # Tracking des schemas sélectionnés pour contexte
        self.selected_schemas = []

    def generate_schema(self,
                        schema_type: str,
                        client_info: Dict,
                        additional_data: Optional[Dict] = None,
                        include_optional: bool = True,
                        context_schemas: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Génère un schema complet avec toutes les propriétés

        Args:
            schema_type: Type de schema à générer
            client_info: Informations du client
            additional_data: Données supplémentaires spécifiques
            include_optional: Inclure les champs optionnels
            context_schemas: Liste des autres schemas sélectionnés pour contexte

        Returns:
            Schema généré ou None si le type n'existe pas
        """
        if schema_type not in self.templates:
            return None

        # Stocker le contexte si fourni
        if context_schemas:
            self.selected_schemas = context_schemas

        # Copier le template
        schema = json.loads(json.dumps(self.templates[schema_type]))

        # CORRECTION SPÉCIALE POUR REVIEW - IMPORTANT !
        if schema_type == 'Review':
            schema = self._fix_review_schema(schema, client_info, additional_data)

        # Nettoyer les champs vides si on ne veut pas les optionnels
        if not include_optional:
            schema = self._clean_empty_fields(schema, schema_type)

        # Utiliser le filler approprié
        if schema_type in SCHEMA_FILLERS:
            filler = SCHEMA_FILLERS[schema_type]
            # Passer le contexte au filler si c'est Review
            if schema_type == 'Review' and hasattr(filler, 'set_context'):
                filler.set_context(self.selected_schemas)
            filler.fill(schema, client_info, additional_data)

            # RE-CORRECTION après le filler pour Review (au cas où le filler écrase)
            if schema_type == 'Review':
                schema = self._fix_review_schema_after_filler(schema, client_info, additional_data)

        # Valider les champs requis
        self._validate_required_fields(schema, schema_type)

        return schema

    def _fix_review_schema(self, schema: Dict, client_info: Dict,
                           additional_data: Optional[Dict]) -> Dict:
        """
        Corrige le schema Review pour avoir un itemReviewed valide

        Google n'accepte pas 'Thing' comme type pour itemReviewed
        """
        if 'itemReviewed' not in schema:
            schema['itemReviewed'] = {}

        # Déterminer le type approprié pour itemReviewed
        item_type = self._determine_item_reviewed_type(additional_data)

        # Appliquer le type correct
        schema['itemReviewed']['@type'] = item_type

        # Nom de l'élément évalué
        if additional_data:
            # Chercher le nom dans plusieurs endroits possibles
            item_name = (
                    additional_data.get('item_name') or
                    additional_data.get('itemreviewed_name') or
                    additional_data.get('service_name') or
                    additional_data.get('product_name') or
                    client_info.get('company_name', 'Service')
            )
            schema['itemReviewed']['name'] = item_name

            # URL si disponible
            item_url = (
                    additional_data.get('item_url') or
                    additional_data.get('itemreviewed_url') or
                    client_info.get('website')
            )
            if item_url:
                schema['itemReviewed']['url'] = item_url
        else:
            # Valeurs par défaut
            schema['itemReviewed']['name'] = client_info.get('company_name', 'Service')
            if client_info.get('website'):
                schema['itemReviewed']['url'] = client_info['website']

        return schema

    def _fix_review_schema_after_filler(self, schema: Dict, client_info: Dict,
                                        additional_data: Optional[Dict]) -> Dict:
        """
        Re-corrige le schema Review après le filler au cas où il aurait remis 'Thing'
        """
        if 'itemReviewed' in schema and isinstance(schema['itemReviewed'], dict):
            current_type = schema['itemReviewed'].get('@type', '')

            # Si c'est Thing ou vide, le corriger
            if current_type == 'Thing' or not current_type:
                item_type = self._determine_item_reviewed_type(additional_data)
                schema['itemReviewed']['@type'] = item_type

        return schema

    def _determine_item_reviewed_type(self, additional_data: Optional[Dict]) -> str:
        """
        Détermine le type approprié pour itemReviewed

        Types acceptés par Google:
        - Service (recommandé pour les agences)
        - Product
        - Organization / LocalBusiness
        - Restaurant, Store, Hotel
        - Event, Course
        - Book, Movie, CreativeWork
        - SoftwareApplication

        NE PAS utiliser: Thing, Intangible
        """
        if not additional_data:
            # Par défaut pour une agence
            return 'Service'

        # Vérifier le type explicite
        if 'review_type' in additional_data:
            review_type = additional_data['review_type']
            # Vérifier que ce n'est pas 'Thing'
            if review_type and review_type != 'Thing':
                return review_type

        # Détecter basé sur les autres schemas sélectionnés
        if hasattr(self, 'selected_schemas') and self.selected_schemas:
            # Mapping prioritaire
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
                'MobileApplication': 'MobileApplication',
                'Hotel': 'Hotel',
                'Book': 'Book',
                'Movie': 'Movie'
            }

            for schema_type in self.selected_schemas:
                if schema_type in type_mapping:
                    return type_mapping[schema_type]

        # Détecter basé sur les données
        if 'service_name' in additional_data or 'service_type' in additional_data:
            return 'Service'
        elif 'product_name' in additional_data or 'product_sku' in additional_data:
            return 'Product'
        elif 'organization_type' in additional_data:
            return 'Organization'
        elif 'local_business_type' in additional_data:
            return 'LocalBusiness'

        # Par défaut pour une agence de marketing
        return 'Service'

    def generate_multiple_schemas(self, schema_types: List[str],
                            client_info: Dict,
                            additional_data: Optional[Dict] = None,
                            include_optional: bool = True) -> List[Dict]:
        """
        Génère plusieurs schemas en évitant les redondances

        Args:
            schema_types: Liste des types de schemas à générer
            client_info: Informations du client
            additional_data: Données supplémentaires
            include_optional: Inclure les champs optionnels

        Returns:
            Liste des schemas générés optimisés
        """
        # Stocker pour le contexte
        self.selected_schemas = schema_types

        # Détecter et fusionner les schemas compatibles
        optimized_types = self._optimize_schema_types(schema_types)

        schemas = []

        # Si on génère plusieurs schemas, utiliser @graph pour les lier
        if len(optimized_types) > 1:
            graph_schema = {
                "@context": "https://schema.org",
                "@graph": []
            }

            # Générer un ID unique pour l'organisation principale
            org_id = f"{client_info.get('website', '')}#organization"
            website_id = f"{client_info.get('website', '')}#website"

            for schema_info in optimized_types:
                if isinstance(schema_info, tuple):
                    # Schema fusionné
                    schema_type_list, schema_id = schema_info
                    schema = self._generate_merged_schema(
                        schema_type_list,
                        client_info,
                        additional_data,
                        include_optional
                    )
                    if schema:
                        schema['@id'] = schema_id
                        graph_schema['@graph'].append(schema)
                else:
                    # Schema simple
                    schema_type = schema_info
                    schema = self.generate_schema(
                        schema_type,
                        client_info,
                        additional_data,
                        include_optional,
                        context_schemas=schema_types
                    )

                    if schema:
                        # Ajouter les @id appropriés
                        if schema_type in ['Organization', 'LocalBusiness', 'Restaurant']:
                            schema['@id'] = org_id
                        elif schema_type == 'WebSite':
                            schema['@id'] = website_id
                            # Lier au publisher
                            if 'publisher' in schema:
                                schema['publisher'] = {"@id": org_id}
                        elif schema_type == 'Service':
                            schema['@id'] = f"{client_info.get('website', '')}#service"
                            # Lier au provider
                            if 'provider' in schema:
                                schema['provider'] = {"@id": org_id}
                        elif schema_type in ['Article', 'NewsArticle', 'BlogPosting']:
                            # Lier à l'organisation
                            if 'publisher' in schema:
                                schema['publisher'] = {"@id": org_id}
                            if 'author' in schema and isinstance(schema['author'], dict):
                                if schema['author'].get('@type') == 'Organization':
                                    schema['author'] = {"@id": org_id}

                        graph_schema['@graph'].append(schema)

                        graph_schema['@graph'] = self._ensure_reviewable_item_exists(
                            graph_schema['@graph'],
                            client_info,
                            additional_data or {}
                        )

            return [graph_schema]
        else:
            # Un seul schema ou schema fusionné
            if isinstance(optimized_types[0], tuple):
                # Schema fusionné
                schema_type_list, _ = optimized_types[0]
                schema = self._generate_merged_schema(
                    schema_type_list,
                    client_info,
                    additional_data,
                    include_optional
                )
                if schema:
                    schemas.append(schema)
            else:
                # Schema simple
                schema = self.generate_schema(
                    optimized_types[0],
                    client_info,
                    additional_data,
                    include_optional,
                    context_schemas=schema_types
                )
                if schema:
                    schemas.append(schema)

        return schemas

    def _optimize_schema_types(self, schema_types: List[str]) -> List[Union[str, Tuple[List[str], str]]]:
        """
        Optimise la liste des types de schemas en fusionnant les compatibles

        Args:
            schema_types: Liste des types de schemas

        Returns:
            Liste optimisée avec schemas simples ou tuples (schemas_fusionnés, id)
        """
        optimized = []
        processed = set()

        # Règles de fusion
        fusion_rules = {
            frozenset(['Organization', 'LocalBusiness']): (['Organization', 'LocalBusiness'], '#organization'),
            frozenset(['Organization', 'Restaurant']): (['Organization', 'Restaurant'], '#organization'),
            frozenset(['LocalBusiness', 'Restaurant']): (['LocalBusiness', 'Restaurant'], '#business'),
            frozenset(['Organization', 'LocalBusiness', 'Restaurant']): (
                ['Organization', 'LocalBusiness', 'Restaurant'], '#organization'),
            frozenset(['Article', 'NewsArticle']): (['Article', 'NewsArticle'], '#article'),
            frozenset(['Article', 'BlogPosting']): (['Article', 'BlogPosting'], '#article'),
        }

        # Vérifier les possibilités de fusion
        schema_set = set(schema_types)

        for fusion_key, (merged_types, schema_id) in fusion_rules.items():
            if fusion_key.issubset(schema_set):
                # Ajouter le schema fusionné
                optimized.append((merged_types, f"{schema_id}"))
                processed.update(fusion_key)

        # Ajouter les schemas non fusionnés
        for schema_type in schema_types:
            if schema_type not in processed:
                optimized.append(schema_type)

        return optimized

    def _generate_merged_schema(self,
                                schema_types: List[str],
                                client_info: Dict,
                                additional_data: Optional[Dict],
                                include_optional: bool) -> Optional[Dict]:
        """
        Génère un schema fusionné avec plusieurs @type

        Args:
            schema_types: Liste des types à fusionner
            client_info: Informations du client
            additional_data: Données supplémentaires
            include_optional: Inclure les champs optionnels

        Returns:
            Schema fusionné
        """
        if not schema_types:
            return None

        # Prendre le premier type comme base
        base_type = schema_types[0]
        schema = self.generate_schema(base_type, client_info, additional_data, include_optional)

        if not schema:
            return None

        # Modifier le @type pour inclure tous les types
        schema['@type'] = schema_types

        # Fusionner les champs spécifiques des autres types
        for schema_type in schema_types[1:]:
            template = self.templates.get(schema_type, {})

            # Ajouter les champs uniques de ce type
            for key, value in template.items():
                if key not in schema and key not in ['@context', '@type']:
                    schema[key] = value

            # Appliquer le filler si disponible
            if schema_type in SCHEMA_FILLERS:
                filler = SCHEMA_FILLERS[schema_type]
                filler.fill(schema, client_info, additional_data)

        # Nettoyer les champs vides
        if not include_optional:
            schema = self._clean_merged_schema(schema)

        return schema

    def _clean_merged_schema(self, schema: Dict) -> Dict:
        """
        Nettoie un schema fusionné en supprimant les champs vides non requis

        Args:
            schema: Schema à nettoyer

        Returns:
            Schema nettoyé
        """

        def clean_dict(d: Dict) -> Dict:
            cleaned = {}
            for k, v in d.items():
                # Toujours garder @context, @type et @id
                if k in ['@context', '@type', '@id']:
                    cleaned[k] = v
                elif v and v != "" and v != [] and v != {}:
                    if isinstance(v, dict):
                        cleaned_sub = clean_dict(v)
                        if cleaned_sub:
                            cleaned[k] = cleaned_sub
                    elif isinstance(v, list) and len(v) > 0:
                        cleaned[k] = v
                    elif not isinstance(v, (dict, list)) and v:
                        cleaned[k] = v
            return cleaned

        return clean_dict(schema)

    def _clean_empty_fields(self, schema: Dict, schema_type: str) -> Dict:
        """Supprime les champs vides non requis"""
        required = self.required_fields.get(schema_type, [])

        def clean_dict(d: Dict) -> Dict:
            cleaned = {}
            for k, v in d.items():
                if k in required or (v and v != "" and v != [] and v != {}):
                    if isinstance(v, dict):
                        cleaned_sub = clean_dict(v)
                        if cleaned_sub or k in required:
                            cleaned[k] = cleaned_sub
                    elif isinstance(v, list) and len(v) > 0:
                        cleaned[k] = v
                    elif not isinstance(v, (dict, list)) and v:
                        cleaned[k] = v
                    elif k in required:
                        cleaned[k] = v
            return cleaned

        return clean_dict(schema)

    def _validate_required_fields(self, schema: Dict, schema_type: str):
        """Valide que tous les champs requis sont présents"""
        required = self.required_fields.get(schema_type, [])
        missing = []

        for field in required:
            if field not in schema or not schema[field]:
                missing.append(field)

        if missing:
            print(f"Attention: Champs requis manquants pour {schema_type}: {missing}")

    def get_schema_documentation(self, schema_type: str) -> Dict:
        """
        Retourne la documentation complète pour un type de schema

        Args:
            schema_type: Type de schema

        Returns:
            Documentation avec champs requis, recommandés et tous les champs
        """
        if schema_type not in self.templates:
            return {}

        return {
            'type': schema_type,
            'required_fields': self.required_fields.get(schema_type, []),
            'recommended_fields': self.recommended_fields.get(schema_type, []),
            'all_fields': list(self.templates[schema_type].keys()),
            'template': self.templates[schema_type]
        }

    def validate_data_format(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """
        Valide le format d'une donnée selon les standards Schema.org

        Args:
            field_name: Nom du champ
            value: Valeur à valider

        Returns:
            Tuple (est_valide, message_erreur)
        """
        return self.validator.validate_field(field_name, value)

    def format_for_insertion(self, schemas: List[Dict]) -> str:
        """
        Formate les schemas pour insertion dans une page HTML

        Args:
            schemas: Liste des schemas

        Returns:
            Code HTML formaté avec les scripts JSON-LD
        """
        html_output = []

        for schema in schemas:
            # Minifier le JSON pour la production
            minified = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))

            # Créer le script tag
            script = f'<script type="application/ld+json">\n{minified}\n</script>'
            html_output.append(script)

        return '\n'.join(html_output)

    def get_available_schema_types(self) -> List[str]:
        """Retourne la liste de tous les types de schemas disponibles"""
        return list(self.templates.keys())

    def get_priority_schemas(self) -> List[str]:
        """Retourne la liste des schemas prioritaires pour le SEO"""
        return self.constants.get_priority_schemas()

    def get_google_supported_schemas(self) -> List[str]:
        """Retourne la liste des schemas supportés par Google"""
        return self.constants.get_google_supported_schemas()

    def get_schema_relationships(self, schema_type: str) -> List[str]:
        """Retourne les schemas liés recommandés pour un type donné"""
        relationships = self.constants.get_schema_relationships()
        return relationships.get(schema_type, [])