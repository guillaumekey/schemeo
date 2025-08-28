"""
Module pour le sélecteur de pays avec liste complète
"""
import streamlit as st


def get_countries_dict():
    """Retourne le dictionnaire complet des pays"""
    return {
        'FR': '🇫🇷 France',
        'BE': '🇧🇪 Belgique',
        'CH': '🇨🇭 Suisse',
        'CA': '🇨🇦 Canada',
        'US': '🇺🇸 États-Unis',
        'GB': '🇬🇧 Royaume-Uni',
        'DE': '🇩🇪 Allemagne',
        'ES': '🇪🇸 Espagne',
        'IT': '🇮🇹 Italie',
        'PT': '🇵🇹 Portugal',
        'NL': '🇳🇱 Pays-Bas',
        'LU': '🇱🇺 Luxembourg',
        'AT': '🇦🇹 Autriche',
        'PL': '🇵🇱 Pologne',
        'CZ': '🇨🇿 République tchèque',
        'SK': '🇸🇰 Slovaquie',
        'HU': '🇭🇺 Hongrie',
        'RO': '🇷🇴 Roumanie',
        'BG': '🇧🇬 Bulgarie',
        'GR': '🇬🇷 Grèce',
        'SE': '🇸🇪 Suède',
        'DK': '🇩🇰 Danemark',
        'NO': '🇳🇴 Norvège',
        'FI': '🇫🇮 Finlande',
        'IE': '🇮🇪 Irlande',
        'IS': '🇮🇸 Islande',
        'HR': '🇭🇷 Croatie',
        'SI': '🇸🇮 Slovénie',
        'EE': '🇪🇪 Estonie',
        'LV': '🇱🇻 Lettonie',
        'LT': '🇱🇹 Lituanie',
        'MT': '🇲🇹 Malte',
        'CY': '🇨🇾 Chypre',
        'TR': '🇹🇷 Turquie',
        'RU': '🇷🇺 Russie',
        'UA': '🇺🇦 Ukraine',
        'BY': '🇧🇾 Biélorussie',
        'MD': '🇲🇩 Moldavie',
        'AL': '🇦🇱 Albanie',
        'BA': '🇧🇦 Bosnie-Herzégovine',
        'RS': '🇷🇸 Serbie',
        'ME': '🇲🇪 Monténégro',
        'MK': '🇲🇰 Macédoine du Nord',
        'AD': '🇦🇩 Andorre',
        'MC': '🇲🇨 Monaco',
        'SM': '🇸🇲 Saint-Marin',
        'VA': '🇻🇦 Vatican',
        'LI': '🇱🇮 Liechtenstein',
        'MX': '🇲🇽 Mexique',
        'BR': '🇧🇷 Brésil',
        'AR': '🇦🇷 Argentine',
        'CL': '🇨🇱 Chili',
        'CO': '🇨🇴 Colombie',
        'PE': '🇵🇪 Pérou',
        'VE': '🇻🇪 Venezuela',
        'UY': '🇺🇾 Uruguay',
        'PY': '🇵🇾 Paraguay',
        'BO': '🇧🇴 Bolivie',
        'EC': '🇪🇨 Équateur',
        'GY': '🇬🇾 Guyana',
        'SR': '🇸🇷 Suriname',
        'CR': '🇨🇷 Costa Rica',
        'PA': '🇵🇦 Panama',
        'GT': '🇬🇹 Guatemala',
        'HN': '🇭🇳 Honduras',
        'SV': '🇸🇻 Salvador',
        'NI': '🇳🇮 Nicaragua',
        'BZ': '🇧🇿 Belize',
        'DO': '🇩🇴 République dominicaine',
        'CU': '🇨🇺 Cuba',
        'JM': '🇯🇲 Jamaïque',
        'HT': '🇭🇹 Haïti',
        'JP': '🇯🇵 Japon',
        'CN': '🇨🇳 Chine',
        'KR': '🇰🇷 Corée du Sud',
        'KP': '🇰🇵 Corée du Nord',
        'IN': '🇮🇳 Inde',
        'PK': '🇵🇰 Pakistan',
        'BD': '🇧🇩 Bangladesh',
        'LK': '🇱🇰 Sri Lanka',
        'NP': '🇳🇵 Népal',
        'BT': '🇧🇹 Bhoutan',
        'AF': '🇦🇫 Afghanistan',
        'IR': '🇮🇷 Iran',
        'IQ': '🇮🇶 Irak',
        'SA': '🇸🇦 Arabie saoudite',
        'AE': '🇦🇪 Émirats arabes unis',
        'QA': '🇶🇦 Qatar',
        'KW': '🇰🇼 Koweït',
        'BH': '🇧🇭 Bahreïn',
        'OM': '🇴🇲 Oman',
        'YE': '🇾🇪 Yémen',
        'JO': '🇯🇴 Jordanie',
        'LB': '🇱🇧 Liban',
        'SY': '🇸🇾 Syrie',
        'IL': '🇮🇱 Israël',
        'PS': '🇵🇸 Palestine',
        'EG': '🇪🇬 Égypte',
        'LY': '🇱🇾 Libye',
        'TN': '🇹🇳 Tunisie',
        'DZ': '🇩🇿 Algérie',
        'MA': '🇲🇦 Maroc',
        'MR': '🇲🇷 Mauritanie',
        'SN': '🇸🇳 Sénégal',
        'ML': '🇲🇱 Mali',
        'BF': '🇧🇫 Burkina Faso',
        'NE': '🇳🇪 Niger',
        'NG': '🇳🇬 Nigeria',
        'GH': '🇬🇭 Ghana',
        'CI': '🇨🇮 Côte d\'Ivoire',
        'BJ': '🇧🇯 Bénin',
        'TG': '🇹🇬 Togo',
        'CM': '🇨🇲 Cameroun',
        'CF': '🇨🇫 République centrafricaine',
        'TD': '🇹🇩 Tchad',
        'SD': '🇸🇩 Soudan',
        'SS': '🇸🇸 Soudan du Sud',
        'ET': '🇪🇹 Éthiopie',
        'ER': '🇪🇷 Érythrée',
        'DJ': '🇩🇯 Djibouti',
        'SO': '🇸🇴 Somalie',
        'KE': '🇰🇪 Kenya',
        'UG': '🇺🇬 Ouganda',
        'RW': '🇷🇼 Rwanda',
        'BI': '🇧🇮 Burundi',
        'TZ': '🇹🇿 Tanzanie',
        'MZ': '🇲🇿 Mozambique',
        'MW': '🇲🇼 Malawi',
        'ZM': '🇿🇲 Zambie',
        'ZW': '🇿🇼 Zimbabwe',
        'BW': '🇧🇼 Botswana',
        'NA': '🇳🇦 Namibie',
        'ZA': '🇿🇦 Afrique du Sud',
        'LS': '🇱🇸 Lesotho',
        'SZ': '🇸🇿 Eswatini',
        'MG': '🇲🇬 Madagascar',
        'MU': '🇲🇺 Maurice',
        'SC': '🇸🇨 Seychelles',
        'KM': '🇰🇲 Comores',
        'AO': '🇦🇴 Angola',
        'CG': '🇨🇬 Congo',
        'CD': '🇨🇩 République démocratique du Congo',
        'GA': '🇬🇦 Gabon',
        'GQ': '🇬🇶 Guinée équatoriale',
        'ST': '🇸🇹 Sao Tomé-et-Principe',
        'CV': '🇨🇻 Cap-Vert',
        'GN': '🇬🇳 Guinée',
        'GW': '🇬🇼 Guinée-Bissau',
        'LR': '🇱🇷 Liberia',
        'SL': '🇸🇱 Sierra Leone',
        'GM': '🇬🇲 Gambie',
        'AU': '🇦🇺 Australie',
        'NZ': '🇳🇿 Nouvelle-Zélande',
        'PG': '🇵🇬 Papouasie-Nouvelle-Guinée',
        'FJ': '🇫🇯 Fidji',
        'SB': '🇸🇧 Îles Salomon',
        'VU': '🇻🇺 Vanuatu',
        'NC': '🇳🇨 Nouvelle-Calédonie',
        'PF': '🇵🇫 Polynésie française',
        'WS': '🇼🇸 Samoa',
        'TO': '🇹🇴 Tonga',
        'TH': '🇹🇭 Thaïlande',
        'VN': '🇻🇳 Vietnam',
        'PH': '🇵🇭 Philippines',
        'ID': '🇮🇩 Indonésie',
        'MY': '🇲🇾 Malaisie',
        'SG': '🇸🇬 Singapour',
        'BN': '🇧🇳 Brunei',
        'TL': '🇹🇱 Timor oriental',
        'MM': '🇲🇲 Myanmar',
        'KH': '🇰🇭 Cambodge',
        'LA': '🇱🇦 Laos',
        'MN': '🇲🇳 Mongolie',
        'KZ': '🇰🇿 Kazakhstan',
        'UZ': '🇺🇿 Ouzbékistan',
        'TM': '🇹🇲 Turkménistan',
        'KG': '🇰🇬 Kirghizistan',
        'TJ': '🇹🇯 Tadjikistan',
        'AZ': '🇦🇿 Azerbaïdjan',
        'AM': '🇦🇲 Arménie',
        'GE': '🇬🇪 Géorgie'
    }


def get_country_groups():
    """Retourne les pays groupés par région"""
    return {
        'Europe': ['FR', 'BE', 'CH', 'LU', 'DE', 'AT', 'NL', 'IT', 'ES', 'PT', 'GB', 'IE',
                   'SE', 'NO', 'DK', 'FI', 'IS', 'PL', 'CZ', 'SK', 'HU', 'RO', 'BG', 'GR',
                   'HR', 'SI', 'EE', 'LV', 'LT', 'MT', 'CY', 'AD', 'MC', 'SM', 'VA', 'LI'],
        'Amérique du Nord': ['CA', 'US', 'MX'],
        'Amérique du Sud': ['BR', 'AR', 'CL', 'CO', 'PE', 'VE', 'UY', 'PY', 'BO', 'EC',
                            'GY', 'SR'],
        'Amérique centrale & Caraïbes': ['CR', 'PA', 'GT', 'HN', 'SV', 'NI', 'BZ', 'DO',
                                         'CU', 'JM', 'HT'],
        'Asie': ['JP', 'CN', 'KR', 'IN', 'PK', 'BD', 'LK', 'NP', 'BT', 'TH', 'VN',
                 'PH', 'ID', 'MY', 'SG', 'BN', 'TL', 'MM', 'KH', 'LA', 'MN'],
        'Moyen-Orient': ['TR', 'SA', 'AE', 'QA', 'KW', 'BH', 'OM', 'YE', 'JO', 'LB',
                         'SY', 'IL', 'PS', 'IR', 'IQ', 'AF'],
        'Afrique': ['EG', 'LY', 'TN', 'DZ', 'MA', 'ZA', 'NG', 'KE', 'ET', 'GH', 'CI',
                    'CM', 'SN', 'TZ', 'UG', 'MG', 'MU', 'SC'],
        'Océanie': ['AU', 'NZ', 'FJ', 'PG', 'NC', 'PF'],
        'Europe de l\'Est & Asie centrale': ['RU', 'UA', 'BY', 'MD', 'KZ', 'UZ', 'TM',
                                             'KG', 'TJ', 'AZ', 'AM', 'GE']
    }


def render_country_selector():
    """Affiche le sélecteur de pays avec option de regroupement"""
    countries = get_countries_dict()
    country_groups = get_country_groups()

    # Option pour grouper par région ou afficher tous les pays
    display_mode = st.radio(
        "Affichage des pays",
        ["Par région", "Tous les pays"],
        horizontal=True,
        key="country_display_mode"
    )

    if display_mode == "Par région":
        selected_region = st.selectbox(
            "Région",
            options=list(country_groups.keys()),
            key="selected_region"
        )

        country_options = country_groups[selected_region]
        default_index = 0
        if 'FR' in country_options:
            default_index = country_options.index('FR')

        country = st.selectbox(
            "Pays",
            options=country_options,
            format_func=lambda x: countries[x],
            index=default_index
        )
    else:
        # Afficher tous les pays triés par nom
        all_countries = sorted(countries.keys(), key=lambda x: countries[x])
        default_index = all_countries.index('FR') if 'FR' in all_countries else 0

        country = st.selectbox(
            "Pays",
            options=all_countries,
            format_func=lambda x: countries[x],
            index=default_index
        )

    return country