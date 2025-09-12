"""
Module pour la section de test - Version simplifiée avec lien externe
"""
import streamlit as st


def test_section():
    """Section de test simplifiée avec lien vers Google Rich Results Test"""

    st.subheader("✅ Test de vos schemas")

    st.markdown("""
    Pour tester la validité et la compatibilité de vos schemas, utilisez l'outil officiel de Google :
    """)

    # Lien vers Google Rich Results Test
    st.link_button(
        "🔗 Tester avec Google Rich Results Test",
        "https://search.google.com/test/rich-results",
        help="Ouvre l'outil officiel Google Rich Results Test dans un nouvel onglet"
    )

    st.markdown("""
    **Comment utiliser l'outil :**
    1. Copiez l'URL de votre page ou collez directement le code de vos schemas
    2. Cliquez sur "Tester l'URL" ou "Tester le code"
    3. Vérifiez les résultats et corrigez les éventuelles erreurs
    4. Assurez-vous que vos schemas sont éligibles aux résultats enrichis
    """)

    st.info("""
    💡 **Conseil :** Testez systématiquement vos schemas après chaque modification 
    pour vous assurer qu'ils respectent les standards de Google.
    """)