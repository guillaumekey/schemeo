"""
Module pour la section de test de compatibilité des schemas
"""
import streamlit as st
import json
import re
from validators.schema_validator import SchemaValidator


def test_section():
    """Section de test de compatibilité"""
    st.subheader("✅ Test de compatibilité des schemas")

    # Option 1: Tester les schemas générés
    if st.session_state.generated_schemas:
        if st.button("Tester les schemas générés"):
            validator = SchemaValidator()
            results = validator.test_compatibility(st.session_state.generated_schemas)

            # Afficher les résultats
            formatted_results = validator.format_test_results(results, st.session_state.language)
            st.text(formatted_results)

            # Détails des erreurs
            if results['errors']:
                with st.expander("📋 Détails des erreurs"):
                    for error in results['errors']:
                        st.error(error)

    # Option 2: Coller du JSON-LD
    st.divider()
    st.subheader("📝 Ou collez votre JSON-LD")

    json_input = st.text_area(
        "Code JSON-LD",
        height=200,
        placeholder='<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "..."\n}\n</script>'
    )

    if st.button("Tester ce code"):
        if json_input:
            try:
                # Extraire le JSON du script si nécessaire
                json_match = re.search(r'<script[^>]*>([^<]+)</script>', json_input, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = json_input

                # Parser le JSON
                schema = json.loads(json_str.strip())

                # Tester
                validator = SchemaValidator()
                if isinstance(schema, list):
                    results = validator.test_compatibility(schema)
                else:
                    results = validator.test_compatibility([schema])

                # Afficher les résultats
                formatted_results = validator.format_test_results(results, st.session_state.language)
                st.text(formatted_results)

            except json.JSONDecodeError as e:
                st.error(f"Erreur de parsing JSON: {e}")
            except Exception as e:
                st.error(f"Erreur: {e}")