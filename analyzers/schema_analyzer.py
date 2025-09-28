"""
Module pour analyser et recommander des schemas
"""
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
from config import Config


class SchemaAnalyzer:
    """Classe pour analyser les schemas et faire des recommandations"""

    def __init__(self):
        self.priority_schemas = Config.SCHEMA_TYPES_PRIORITY
        self.schema_relationships = {
            'Product': ['Offer', 'AggregateRating', 'Review', 'Brand'],
            'LocalBusiness': ['PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification', 'AggregateRating'],
            'Article': ['Person', 'Organization', 'ImageObject'],
            'Event': ['Place', 'PostalAddress', 'Offer'],
            'Recipe': ['NutritionInformation', 'AggregateRating', 'VideoObject'],
            'Organization': ['ContactPoint', 'PostalAddress', 'Logo']
        }

    def analyze_page_schemas(self, schemas: Dict, schema_types: Set) -> Dict:
        """
        Analyse les schemas d'une page individuelle

        Args:
            schemas: Dictionnaire des schemas extraits
            schema_types: Set des types de schemas trouvés

        Returns:
            Analyse de la page
        """
        analysis = {
            'total_schemas': 0,
            'schema_types_found': list(schema_types),
            'schema_distribution': {},
            'optimization_score': 0,
            'recommendations': []
        }

        # Compter le total de schemas
        for format_type, schema_list in schemas.items():
            if isinstance(schema_list, list):
                count = len(schema_list)
                analysis['total_schemas'] += count
                analysis['schema_distribution'][format_type] = count

        # Calculer un score d'optimisation basique (sur 100)
        priority_found = len([t for t in schema_types if t in ['Organization', 'LocalBusiness', 'WebSite', 'WebPage']])
        analysis['optimization_score'] = min(100, (priority_found * 25) + (len(schema_types) * 5))

        # Générer des recommandations basiques
        if 'Organization' not in schema_types:
            analysis['recommendations'].append(
                'Ajouter un schema Organization pour améliorer la visibilité de votre marque')

        if 'BreadcrumbList' not in schema_types:
            analysis['recommendations'].append('Ajouter un schema BreadcrumbList pour améliorer la navigation')

        if analysis['total_schemas'] == 0:
            analysis['recommendations'].append('Aucun schema détecté - commencez par ajouter des schemas de base')

        return analysis

    def analyze_serp_schemas(self, serp_results: Dict) -> Dict:
        """
        Analyse les schemas trouvés dans les résultats SERP

        Args:
            serp_results: Résultats de l'analyse SERP

        Returns:
            Analyse détaillée
        """
        analysis = {
            'total_urls': len(serp_results.get('urls_analyzed', [])),
            'schema_coverage': {},
            'position_analysis': {},
            'competitive_schemas': [],
            'schema_combinations': []
        }

        # Analyser la couverture par schema
        schema_freq = serp_results.get('schema_frequency', {})
        for schema_type, count in schema_freq.items():
            coverage = (count / analysis['total_urls']) * 100
            analysis['schema_coverage'][schema_type] = {
                'count': count,
                'percentage': round(coverage, 1)
            }

        # Analyser par position
        schema_positions = serp_results.get('schema_by_position', {})
        for schema_type, positions in schema_positions.items():
            avg_position = sum(positions) / len(positions)
            analysis['position_analysis'][schema_type] = {
                'positions': positions,
                'average_position': round(avg_position, 1),
                'in_top_3': len([p for p in positions if p <= 3])
            }

        # Identifier les schemas compétitifs (présents dans le top 3)
        for schema_type, data in analysis['position_analysis'].items():
            if data['in_top_3'] >= 2:
                analysis['competitive_schemas'].append(schema_type)

        # Analyser les combinaisons de schemas
        analysis['schema_combinations'] = self._analyze_combinations(serp_results)

        return analysis

    def _analyze_combinations(self, serp_results: Dict) -> List[Dict]:
        """Analyse les combinaisons de schemas utilisées ensemble"""
        combinations = []
        urls_data = serp_results.get('urls_analyzed', [])

        # Compter les combinaisons
        combo_counter = Counter()
        for url_data in urls_data:
            schemas = tuple(sorted(url_data.get('schema_types', [])))
            if len(schemas) > 1:
                combo_counter[schemas] += 1

        # Formater les résultats
        for combo, count in combo_counter.most_common(5):
            combinations.append({
                'schemas': list(combo),
                'count': count,
                'percentage': round((count / len(urls_data)) * 100, 1)
            })

        return combinations

    def compare_with_page(self,
                          serp_analysis: Dict,
                          page_schemas: Set[str]) -> Dict:
        """
        Compare les schemas d'une page avec l'analyse SERP

        Args:
            serp_analysis: Analyse des résultats SERP
            page_schemas: Schemas présents sur la page

        Returns:
            Comparaison et recommandations
        """
        comparison = {
            'current_schemas': list(page_schemas),
            'missing_competitive': [],
            'missing_common': [],
            'unique_schemas': [],
            'score': 0
        }

        # Schemas compétitifs manquants
        competitive = set(serp_analysis.get('competitive_schemas', []))
        comparison['missing_competitive'] = list(competitive - page_schemas)

        # Schemas communs manquants (>50% de présence)
        for schema_type, data in serp_analysis.get('schema_coverage', {}).items():
            if data['percentage'] > 50 and schema_type not in page_schemas:
                comparison['missing_common'].append(schema_type)

        # Schemas uniques à la page
        all_serp_schemas = set(serp_analysis.get('schema_coverage', {}).keys())
        comparison['unique_schemas'] = list(page_schemas - all_serp_schemas)

        # Calculer un score de compétitivité
        score = 0
        if page_schemas:
            # Points pour les schemas compétitifs
            score += len(page_schemas & competitive) * 30
            # Points pour les schemas communs
            common_schemas = {s for s, d in serp_analysis.get('schema_coverage', {}).items()
                              if d['percentage'] > 30}
            score += len(page_schemas & common_schemas) * 10
            # Pénalité pour schemas compétitifs manquants
            score -= len(comparison['missing_competitive']) * 20

        comparison['score'] = max(0, min(100, score))

        return comparison

    def recommend_schemas(self,
                          comparison: Dict,
                          serp_analysis: Dict,
                          page_type: Optional[str] = None) -> List[Dict]:
        """
        Génère des recommandations de schemas

        Args:
            comparison: Résultats de comparaison
            serp_analysis: Analyse SERP
            page_type: Type de page (optionnel)

        Returns:
            Liste de recommandations priorisées
        """
        recommendations = []

        # Recommander les schemas compétitifs manquants
        for schema in comparison['missing_competitive']:
            position_data = serp_analysis['position_analysis'].get(schema, {})
            recommendations.append({
                'schema': schema,
                'priority': 'high',
                'reason': 'competitive_advantage',
                'details': {
                    'avg_position': position_data.get('average_position', 'N/A'),
                    'top_3_count': position_data.get('in_top_3', 0)
                }
            })

        # Recommander les schemas communs manquants
        for schema in comparison['missing_common']:
            if schema not in [r['schema'] for r in recommendations]:
                coverage = serp_analysis['schema_coverage'].get(schema, {})
                recommendations.append({
                    'schema': schema,
                    'priority': 'medium',
                    'reason': 'common_practice',
                    'details': {
                        'coverage': coverage.get('percentage', 0)
                    }
                })

        # Recommandations basées sur le type de page
        if page_type:
            type_recommendations = self._get_page_type_recommendations(page_type)
            for schema in type_recommendations:
                if schema not in comparison['current_schemas'] and \
                        schema not in [r['schema'] for r in recommendations]:
                    recommendations.append({
                        'schema': schema,
                        'priority': 'low',
                        'reason': 'page_type_suggestion',
                        'details': {
                            'page_type': page_type
                        }
                    })

        # Trier par priorité
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations[:10]  # Limiter à 10 recommandations

    def _get_page_type_recommendations(self, page_type: str) -> List[str]:
        """Retourne les schemas recommandés selon le type de page"""
        recommendations = {
            'homepage': ['Organization', 'WebSite', 'BreadcrumbList'],
            'product': ['Product', 'Offer', 'AggregateRating', 'Review', 'BreadcrumbList'],
            'article': ['Article', 'BreadcrumbList', 'Person', 'Organization'],
            'local': ['LocalBusiness', 'PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification'],
            'contact': ['Organization', 'ContactPoint', 'PostalAddress'],
            'about': ['Organization', 'Person', 'BreadcrumbList'],
            'faq': ['FAQPage', 'BreadcrumbList'],
            'event': ['Event', 'Place', 'Offer', 'BreadcrumbList']
        }

        return recommendations.get(page_type, ['Organization', 'BreadcrumbList'])

    def get_schema_insights(self, schema_type: str) -> Dict:
        """
        Fournit des insights sur un type de schema spécifique

        Args:
            schema_type: Type de schema

        Returns:
            Insights et bonnes pratiques
        """
        insights = {
            'Organization': {
                'benefits': ['Améliore la reconnaissance de la marque', 'Affiche le Knowledge Graph'],
                'best_practices': ['Inclure logo haute résolution', 'Ajouter tous les profils sociaux'],
                'related_schemas': ['ContactPoint', 'PostalAddress']
            },
            'LocalBusiness': {
                'benefits': ['Affichage dans Google Maps', 'Horaires d\'ouverture visibles'],
                'best_practices': ['Coordonnées GPS précises', 'Horaires détaillés par jour'],
                'related_schemas': ['PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification']
            },
            'Product': {
                'benefits': ['Rich snippets produit', 'Étoiles dans les résultats'],
                'best_practices': ['Prix et disponibilité à jour', 'Images haute qualité'],
                'related_schemas': ['Offer', 'AggregateRating', 'Review']
            },
            'Article': {
                'benefits': ['Apparition dans Google Actualités', 'Meilleure indexation'],
                'best_practices': ['Dates de publication précises', 'Auteur identifié'],
                'related_schemas': ['Person', 'Organization', 'ImageObject']
            },
            'FAQPage': {
                'benefits': ['FAQ directement dans les SERP', 'Plus d\'espace visuel'],
                'best_practices': ['Questions pertinentes', 'Réponses concises'],
                'related_schemas': ['Question', 'Answer']
            }
        }

        return insights.get(schema_type, {
            'benefits': ['Améliore la compréhension du contenu'],
            'best_practices': ['Suivre les guidelines Schema.org'],
            'related_schemas': []
        })