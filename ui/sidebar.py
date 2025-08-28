"""
Module pour la barre latérale de l'application
"""
import streamlit as st
from config import Config
from translations import get_text
from utils.cache import cache_manager


def render_sidebar():
    """Affiche la barre latérale avec les paramètres"""
    with st.sidebar:
        st.title(f"⚙️ {get_text('settings', st.session_state.language)}")

        # Sélection de la langue
        st.session_state.language = st.selectbox(
            get_text('language', st.session_state.language),
            options=Config.SUPPORTED_LANGUAGES,
            format_func=lambda x: {'fr': '🇫🇷 Français', 'en': '🇬🇧 English', 'es': '🇪🇸 Español'}[x],
            index=Config.SUPPORTED_LANGUAGES.index(st.session_state.language)
        )

        # Configuration de l'API
        st.session_state.api_key = st.text_input(
            get_text('api_key', st.session_state.language),
            value=st.session_state.api_key,
            type="password",
            placeholder=get_text('api_key_placeholder', st.session_state.language)
        )

        # Informations sur le cache
        with st.expander("🗄️ Cache"):
            if st.button("Vider le cache"):
                cache_manager.clear()
                st.success("Cache vidé!")

            stats = cache_manager.get_stats()
            st.write(f"Entrées valides: {stats['valid_entries']}")
            st.write(f"Entrées expirées: {stats['expired_entries']}")