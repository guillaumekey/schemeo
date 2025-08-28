"""
Application Streamlit principale pour l'analyseur de schemas SEO
Version refactorisée et modulaire avec navigation d'onglets
"""
import streamlit as st
from config import Config
from translations import get_text

# Import des sections de l'interface
from ui.search_section import search_section
from ui.results_section import results_section
from ui.my_page_section import my_page_section
from ui.generator_section import generator_section
from ui.test_section import test_section
from ui.sidebar import render_sidebar

# Configuration de la page
st.set_page_config(
    page_title="SEO Schema Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialisation de la session
def init_session_state():
    """Initialise les variables de session"""
    if 'language' not in st.session_state:
        st.session_state.language = Config.DEFAULT_LANGUAGE
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    if 'serp_results' not in st.session_state:
        st.session_state.serp_results = None
    if 'schema_analysis' not in st.session_state:
        st.session_state.schema_analysis = None
    if 'my_page_schemas' not in st.session_state:
        st.session_state.my_page_schemas = None
    if 'generated_schemas' not in st.session_state:
        st.session_state.generated_schemas = []
    # Nouvelle variable pour contrôler l'onglet actif
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0


def main():
    """Fonction principale de l'application"""
    # Initialiser la session
    init_session_state()

    # Sidebar pour les paramètres
    render_sidebar()

    # En-tête principal
    st.title(f"🔍 {get_text('app_title', st.session_state.language)}")
    st.markdown(get_text('app_description', st.session_state.language))

    # Liste des onglets
    tab_names = [
        f"🔎 {get_text('search_section', st.session_state.language)}",
        f"📊 {get_text('results_section', st.session_state.language)}",
        f"🌐 {get_text('my_page_section', st.session_state.language)}",
        f"🛠️ {get_text('generator_section', st.session_state.language)}",
        f"✅ {get_text('test_section', st.session_state.language)}"
    ]

    # Créer les onglets
    tabs = st.tabs(tab_names)

    # Afficher le contenu selon l'onglet actif ou sélectionné
    # Onglet 0: Recherche Google
    with tabs[0]:
        if st.session_state.active_tab == 0 or st.session_state.active_tab is None:
            search_section()

    # Onglet 1: Résultats d'analyse
    with tabs[1]:
        if st.session_state.active_tab == 1:
            results_section()
        else:
            results_section()

    # Onglet 2: Analyser ma page
    with tabs[2]:
        if st.session_state.active_tab == 2:
            my_page_section()
        else:
            my_page_section()

    # Onglet 3: Générateur de schemas
    with tabs[3]:
        # Forcer l'affichage si on a cliqué sur le bouton
        if st.session_state.active_tab == 3 or st.session_state.get('selected_schemas'):
            generator_section()
            # Réinitialiser l'onglet actif après affichage
            if st.session_state.active_tab == 3:
                st.session_state.active_tab = None
        else:
            generator_section()

    # Onglet 4: Test de compatibilité
    with tabs[4]:
        if st.session_state.active_tab == 4:
            test_section()
        else:
            test_section()


if __name__ == "__main__":
    main()