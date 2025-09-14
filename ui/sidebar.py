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

        # Sélection de la langue avec rerun forcé
        def get_language_display(lang_code):
            """Fonction pour afficher le nom de la langue de façon dynamique"""
            language_names = {
                'fr': {
                    'fr': '🇫🇷 Français',
                    'en': '🇬🇧 Anglais',
                    'es': '🇪🇸 Espagnol'
                },
                'en': {
                    'fr': '🇫🇷 French',
                    'en': '🇬🇧 English',
                    'es': '🇪🇸 Spanish'
                },
                'es': {
                    'fr': '🇫🇷 Francés',
                    'en': '🇬🇧 Inglés',
                    'es': '🇪🇸 Español'
                }
            }
            current_lang = st.session_state.get('language', 'fr')
            return language_names.get(current_lang, language_names['fr']).get(lang_code, lang_code)

        # Stocker l'ancienne langue pour détecter le changement
        old_language = st.session_state.get('language', Config.DEFAULT_LANGUAGE)

        new_language = st.selectbox(
            get_text('language', st.session_state.language),
            options=Config.SUPPORTED_LANGUAGES,
            format_func=get_language_display,
            index=Config.SUPPORTED_LANGUAGES.index(st.session_state.language),
            key="language_selector"
        )

        # Détecter et forcer le rerun si la langue a changé
        if new_language != old_language:
            st.session_state.language = new_language
            st.rerun()

        # Configuration de l'API
        st.session_state.api_key = st.text_input(
            get_text('api_key', st.session_state.language),
            value=st.session_state.api_key,
            type="password",
            placeholder=get_text('api_key_placeholder', st.session_state.language)
        )

        # Informations sur le cache
        with st.expander(f"🗄️ {get_text('cache', st.session_state.language)}"):
            if st.button(get_text('clear_cache', st.session_state.language)):
                cache_manager.clear()
                st.success(get_text('cache_cleared', st.session_state.language))

            stats = cache_manager.get_stats()
            st.write(f"{get_text('valid_entries', st.session_state.language)}: {stats['valid_entries']}")
            st.write(f"{get_text('expired_entries', st.session_state.language)}: {stats['expired_entries']}")

            # Affichage d'informations supplémentaires si disponibles
            if 'total_entries' in stats:
                st.write(f"{get_text('total_entries', st.session_state.language)}: {stats['total_entries']}")

            if 'cache_enabled' in stats:
                cache_status = "✅" if stats['cache_enabled'] else "❌"
                st.write(f"{get_text('cache_enabled', st.session_state.language)}: {cache_status}")