"""
Fonctions utilitaires pour l'application
"""
import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import re


def is_valid_url(url: str) -> bool:
    """
    Vérifie si une URL est valide

    Args:
        url: URL à vérifier

    Returns:
        True si l'URL est valide
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url: str) -> str:
    """
    Normalise une URL (ajoute https:// si nécessaire)

    Args:
        url: URL à normaliser

    Returns:
        URL normalisée
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')


def format_json_for_display(data: Dict) -> str:
    """
    Formate un JSON pour l'affichage

    Args:
        data: Données JSON

    Returns:
        JSON formaté
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


def create_download_button(data: Any, filename: str, label: str, file_type: str = "json"):
    """
    Crée un bouton de téléchargement

    Args:
        data: Données à télécharger
        filename: Nom du fichier
        label: Label du bouton
        file_type: Type de fichier
    """
    if file_type == "json":
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            data_str = str(data)
        mime_type = "application/json"
    elif file_type == "html":
        data_str = data
        mime_type = "text/html"
    else:
        data_str = str(data)
        mime_type = "text/plain"

    st.download_button(
        label=label,
        data=data_str,
        file_name=filename,
        mime=mime_type
    )


def display_schema_summary(schemas: List[Dict], language: str = 'fr'):
    """
    Affiche un résumé des schemas

    Args:
        schemas: Liste des schemas
        language: Langue d'affichage
    """
    if not schemas:
        return

    # Compter les types
    schema_types = {}
    for schema in schemas:
        schema_type = schema.get('@type', 'Unknown')
        schema_types[schema_type] = schema_types.get(schema_type, 0) + 1

    # Créer un DataFrame pour l'affichage
    df_data = []
    for schema_type, count in schema_types.items():
        df_data.append({
            'Type': schema_type,
            'Count': count
        })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)


def get_domain_from_url(url: str) -> str:
    """
    Extrait le domaine d'une URL

    Args:
        url: URL complète

    Returns:
        Domaine
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path
    except:
        return url


def clean_text(text: str, max_length: int = 100) -> str:
    """
    Nettoie et tronque un texte

    Args:
        text: Texte à nettoyer
        max_length: Longueur maximale

    Returns:
        Texte nettoyé
    """
    # Supprimer les tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Supprimer les espaces multiples
    text = ' '.join(text.split())
    # Tronquer si nécessaire
    if len(text) > max_length:
        text = text[:max_length] + '...'
    return text


def merge_schemas(schemas_list: List[List[Dict]]) -> List[Dict]:
    """
    Fusionne plusieurs listes de schemas en évitant les doublons

    Args:
        schemas_list: Liste de listes de schemas

    Returns:
        Liste fusionnée sans doublons
    """
    seen = set()
    merged = []

    for schemas in schemas_list:
        for schema in schemas:
            # Créer un identifiant unique basé sur le type et certains champs
            schema_id = f"{schema.get('@type', '')}_{schema.get('name', '')}_{schema.get('url', '')}"

            if schema_id not in seen:
                seen.add(schema_id)
                merged.append(schema)

    return merged


def calculate_serp_score(position: int, has_schemas: bool, schema_count: int) -> float:
    """
    Calcule un score SEO basé sur la position et les schemas

    Args:
        position: Position dans les SERP
        has_schemas: Présence de schemas
        schema_count: Nombre de schemas

    Returns:
        Score entre 0 et 100
    """
    # Score de base selon la position
    position_score = max(0, 100 - (position - 1) * 10)

    # Bonus pour les schemas
    schema_bonus = 0
    if has_schemas:
        schema_bonus = min(20, schema_count * 5)

    return min(100, position_score + schema_bonus)


def generate_schema_report(analysis_results: Dict, language: str = 'fr') -> str:
    """
    Génère un rapport textuel de l'analyse

    Args:
        analysis_results: Résultats de l'analyse
        language: Langue du rapport

    Returns:
        Rapport formaté
    """
    reports = {
        'fr': {
            'title': '📊 Rapport d\'analyse des schemas',
            'summary': 'Résumé de l\'analyse',
            'coverage': 'Couverture des schemas',
            'recommendations': 'Recommandations',
            'competitive': 'Schemas compétitifs'
        },
        'en': {
            'title': '📊 Schema Analysis Report',
            'summary': 'Analysis Summary',
            'coverage': 'Schema Coverage',
            'recommendations': 'Recommendations',
            'competitive': 'Competitive Schemas'
        },
        'es': {
            'title': '📊 Informe de análisis de schemas',
            'summary': 'Resumen del análisis',
            'coverage': 'Cobertura de schemas',
            'recommendations': 'Recomendaciones',
            'competitive': 'Schemas competitivos'
        }
    }

    lang_texts = reports.get(language, reports['fr'])

    report = [f"# {lang_texts['title']}\n"]

    # Résumé
    report.append(f"## {lang_texts['summary']}")
    report.append(f"- URLs analysées: {analysis_results.get('total_urls', 0)}")
    report.append(f"- Types de schemas trouvés: {len(analysis_results.get('schema_coverage', {}))}")
    report.append("")

    # Couverture
    report.append(f"## {lang_texts['coverage']}")
    for schema_type, data in analysis_results.get('schema_coverage', {}).items():
        report.append(f"- **{schema_type}**: {data['count']} sites ({data['percentage']}%)")
    report.append("")

    # Schemas compétitifs
    if analysis_results.get('competitive_schemas'):
        report.append(f"## {lang_texts['competitive']}")
        for schema in analysis_results['competitive_schemas']:
            report.append(f"- {schema}")
        report.append("")

    return '\n'.join(report)


def estimate_implementation_time(schemas: List[str]) -> Dict[str, int]:
    """
    Estime le temps d'implémentation pour chaque schema

    Args:
        schemas: Liste des types de schemas

    Returns:
        Temps estimé en minutes pour chaque schema
    """
    time_estimates = {
        'Organization': 15,
        'LocalBusiness': 30,
        'Product': 20,
        'Article': 15,
        'FAQPage': 25,
        'BreadcrumbList': 10,
        'WebSite': 10,
        'Person': 10,
        'Event': 20,
        'Recipe': 30,
        'VideoObject': 15,
        'Review': 15,
        'AggregateRating': 10
    }

    estimates = {}
    for schema in schemas:
        estimates[schema] = time_estimates.get(schema, 20)

    return estimates


def create_progress_bar(current: int, total: int, label: str = ""):
    """
    Crée une barre de progression

    Args:
        current: Valeur actuelle
        total: Valeur totale
        label: Label de la barre
    """
    progress = current / total if total > 0 else 0
    st.progress(progress, text=label)


def format_schema_for_copy(schemas: List[Dict]) -> str:
    """
    Formate les schemas pour la copie dans le presse-papier

    Args:
        schemas: Liste des schemas

    Returns:
        Code HTML formaté avec les scripts JSON-LD
    """
    output = []

    for schema in schemas:
        script = f'<script type="application/ld+json">\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n</script>'
        output.append(script)

    return '\n\n'.join(output)


def get_schema_icon(schema_type: str) -> str:
    """
    Retourne une icône emoji pour chaque type de schema

    Args:
        schema_type: Type de schema

    Returns:
        Emoji correspondant
    """
    icons = {
        'Organization': '🏢',
        'LocalBusiness': '🏪',
        'Product': '📦',
        'Article': '📄',
        'FAQPage': '❓',
        'BreadcrumbList': '🍞',
        'WebSite': '🌐',
        'Person': '👤',
        'Event': '📅',
        'Recipe': '🍳',
        'VideoObject': '🎥',
        'Review': '⭐',
        'AggregateRating': '📊'
    }

    return icons.get(schema_type, '📋')