"""
Fonctions utilitaires pour le générateur de schemas
"""
import streamlit as st
import json
from datetime import datetime


def display_schema_preview(schema):
    """Affiche un aperçu visuel du schema"""
    schema_type = schema.get('@type', 'Unknown')

    # Informations de base
    if 'name' in schema and schema['name']:
        st.write(f"**Nom:** {schema['name']}")

    if 'description' in schema and schema['description']:
        st.write(f"**Description:** {schema['description'][:200]}...")

    # Informations spécifiques par type
    if schema_type in ['Organization', 'LocalBusiness']:
        if 'address' in schema and isinstance(schema['address'], dict):
            addr = schema['address']
            parts = [
                addr.get('streetAddress', ''),
                addr.get('postalCode', ''),
                addr.get('addressLocality', ''),
                addr.get('addressCountry', '')
            ]
            address_str = ', '.join([p for p in parts if p])
            if address_str:
                st.write(f"**Adresse:** {address_str}")

        if 'telephone' in schema and schema['telephone']:
            st.write(f"**Téléphone:** {schema['telephone']}")

    elif schema_type == 'Product':
        if 'offers' in schema and isinstance(schema['offers'], dict):
            offer = schema['offers']
            if 'price' in offer and offer['price']:
                currency = offer.get('priceCurrency', 'EUR')
                st.write(f"**Prix:** {offer['price']} {currency}")

            if 'availability' in offer:
                availability = offer['availability'].split('/')[-1]
                st.write(f"**Disponibilité:** {availability}")

    elif schema_type in ['Article', 'NewsArticle']:
        if 'headline' in schema and schema['headline']:
            st.write(f"**Titre:** {schema['headline']}")

        if 'author' in schema and isinstance(schema['author'], dict):
            author_name = schema['author'].get('name', '')
            if author_name:
                st.write(f"**Auteur:** {author_name}")

        if 'datePublished' in schema:
            st.write(f"**Publié le:** {schema['datePublished'][:10]}")

    elif schema_type == 'Event':
        if 'startDate' in schema:
            st.write(f"**Début:** {schema['startDate'][:10]}")

        if 'location' in schema:
            if isinstance(schema['location'], dict):
                loc_name = schema['location'].get('name', '')
                if loc_name:
                    st.write(f"**Lieu:** {loc_name}")
            elif isinstance(schema['location'], list):
                st.write(f"**Mode:** Événement hybride")


def generate_wordpress_code(schemas):
    """Génère le code PHP pour WordPress"""
    php_code = """<?php
// Ajoutez ce code dans votre fichier functions.php ou dans un plugin personnalisé

function add_custom_schema_markup() {
    if (is_front_page() || is_home()) {
        ?>
        <!-- Schema.org Structured Data -->
"""

    for schema in schemas:
        json_str = json.dumps(schema, indent=4, ensure_ascii=False)
        php_code += f"""        <script type="application/ld+json">
        {json_str}
        </script>
"""

    php_code += """        <!-- End Schema.org Structured Data -->
        <?php
    }
}
add_action('wp_head', 'add_custom_schema_markup');
?>"""

    return php_code


def generate_implementation_doc(schema_types, schemas):
    """Génère une documentation d'implémentation"""
    doc = f"""# Documentation d'implémentation des schemas

## Schemas générés
Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Types de schemas:
"""

    for schema_type in schema_types:
        doc += f"- {schema_type}\n"

    doc += """
## Instructions d'implémentation

### 1. Validation
Avant d'implémenter les schemas sur votre site :
1. Testez avec [Google Rich Results Test](https://search.google.com/test/rich-results)
2. Vérifiez avec [Schema.org Validator](https://validator.schema.org/)
3. Utilisez l'inspecteur d'URL dans Google Search Console

### 2. Placement du code
- **Recommandé**: Dans la section `<head>` de votre page
- **Alternative**: Dans le `<body>` (avant la fermeture)
- **Important**: Un seul bloc JSON-LD par type de schema

### 3. Maintenance
- Mettez à jour les informations régulièrement
- Surveillez les erreurs dans Search Console
- Adaptez selon les nouvelles recommandations Google

### 4. Bonnes pratiques
- Les données structurées doivent correspondre au contenu visible
- Utilisez des URLs complètes (avec https://)
- Respectez les formats de date ISO 8601
- Incluez des images haute résolution

## Champs utilisés par schema
"""

    # Analyser les champs utilisés
    for schema in schemas:
        if '@graph' in schema:
            for sub_schema in schema['@graph']:
                doc += f"\n### {sub_schema.get('@type', 'Unknown')}\n"
                doc += list_populated_fields(sub_schema)
        else:
            doc += f"\n### {schema.get('@type', 'Unknown')}\n"
            doc += list_populated_fields(schema)

    return doc


def list_populated_fields(schema, prefix=""):
    """Liste les champs remplis dans un schema"""
    result = ""

    for key, value in schema.items():
        if key.startswith('@'):
            continue

        full_key = f"{prefix}{key}" if prefix else key

        if isinstance(value, dict) and value:
            result += f"- **{full_key}**: Object\n"
            result += list_populated_fields(value, f"  {full_key}.")
        elif isinstance(value, list) and value:
            result += f"- **{full_key}**: Array[{len(value)}]\n"
        elif value and value != "":
            if isinstance(value, str) and len(value) > 50:
                result += f"- **{full_key}**: {value[:50]}...\n"
            else:
                result += f"- **{full_key}**: {value}\n"

    return result