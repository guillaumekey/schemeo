"""
Configuration centrale de l'application
Version finale avec tous les attributs nécessaires
"""
import os

# Essayer de charger dotenv si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv n'est pas installé, continuer sans
    pass


class Config:
    """Configuration globale de l'application"""

    # API Keys
    VALUESERP_API_KEY = os.getenv('VALUESERP_API_KEY', '')

    # ValueSERP API Settings
    VALUESERP_BASE_URL = "https://api.valueserp.com/search"

    # Application Settings
    DEFAULT_LANGUAGE = 'fr'
    SUPPORTED_LANGUAGES = ['fr', 'en', 'es']

    # Request Settings
    REQUEST_TIMEOUT = 30  # secondes
    USER_AGENT = 'SEO-Schema-Analyzer/1.0 (https://example.com; contact@example.com)'

    # Cache Settings
    CACHE_ENABLED = True
    CACHE_DURATION = 3600  # 1 hour in seconds (utilisé par cache.py)
    CACHE_EXPIRY_HOURS = 24
    MAX_CACHE_SIZE = 1000

    # Crawling settings
    MAX_URLS_PER_ANALYSIS = 10
    MAX_CONCURRENT_REQUESTS = 5
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 2  # secondes

    # File paths
    CACHE_DIR = 'cache'
    LOGS_DIR = 'logs'
    EXPORT_DIR = 'exports'

    # Export formats
    SUPPORTED_EXPORT_FORMATS = ['json', 'csv', 'xlsx', 'html']

    # UI Settings
    PAGE_TITLE = "SEO Schema Analyzer"
    PAGE_ICON = "🔍"
    LAYOUT = "wide"

    # Schema.org Settings
    STANDARD_SCHEMA_TYPES = {
        # Content types
        'Article', 'NewsArticle', 'BlogPosting', 'ScholarlyArticle', 'TechArticle',
        'Report', 'SocialMediaPosting', 'LiveBlogPosting',

        # Business & Organizations
        'Organization', 'Corporation', 'LocalBusiness', 'Store', 'Restaurant',
        'FoodEstablishment', 'Bakery', 'BarOrPub', 'Brewery', 'CafeOrCoffeeShop',
        'FastFoodRestaurant', 'IceCreamShop', 'Winery',

        # Products & Services
        'Product', 'Service', 'ProfessionalService', 'Offer', 'AggregateOffer',
        'Brand', 'Model', 'ProductModel',

        # People & Roles
        'Person', 'Patient', 'MedicalAudience', 'EducationalAudience',

        # Places
        'Place', 'AdministrativeArea', 'CivicStructure',
        'Landform', 'LandmarksOrHistoricalBuildings', 'Residence',
        'TouristDestination',

        # Events
        'Event', 'BusinessEvent', 'ChildrensEvent', 'ComedyEvent', 'CourseInstance',
        'DanceEvent', 'DeliveryEvent', 'EducationEvent', 'ExhibitionEvent',
        'Festival', 'FoodEvent', 'LiteraryEvent', 'MusicEvent', 'PublicationEvent',
        'SaleEvent', 'ScreeningEvent', 'SocialEvent', 'SportsEvent', 'TheaterEvent',
        'VisualArtsEvent',

        # Creative Works
        'CreativeWork', 'Book', 'Movie', 'MusicAlbum', 'MusicRecording',
        'Photograph', 'Recipe', 'Review', 'SoftwareApplication', 'TVSeries',
        'VideoObject', 'WebPage', 'WebSite',

        # Medical & Health
        'MedicalEntity', 'MedicalCondition', 'Drug', 'Hospital',
        'MedicalProcedure', 'MedicalClinic', 'Pharmacy', 'Physician',

        # Education
        'Course', 'EducationalOrganization', 'School',
        'CollegeOrUniversity', 'EducationalOccupationalProgram',

        # Data & Datasets
        'Dataset', 'DataCatalog', 'DataDownload',

        # Actions
        'Action', 'SearchAction', 'ReadAction', 'WatchAction', 'ListenAction',
        'ViewAction', 'PlayAction', 'ConsumeAction',

        # Intangibles
        'JobPosting', 'Occupation', 'Invoice', 'Order', 'Reservation',
        'Permit', 'Ticket', 'PropertyValue', 'QuantitativeValue',

        # Media Objects
        'ImageObject', 'AudioObject', 'MediaObject',

        # Lists and Enumerations
        'ItemList', 'BreadcrumbList', 'OfferCatalog', 'ListItem',

        # Geographic
        'PostalAddress', 'GeoCoordinates', 'GeoShape', 'ContactPoint',

        # Time-based
        'OpeningHoursSpecification', 'Schedule',

        # Nutritional
        'NutritionInformation',

        # Financial
        'PriceSpecification', 'PaymentMethod', 'LoanOrCredit',
        'BankAccount', 'FinancialProduct', 'FinancialService',

        # Entertainment
        'Game', 'VideoGame', 'MovieSeries', 'MusicGroup',
        'TheaterGroup', 'DanceGroup', 'PerformingGroup',

        # Vehicles
        'Vehicle', 'Car', 'Motorcycle', 'MotorizedBicycle',

        # FAQ and How-To
        'FAQPage', 'HowTo', 'Question', 'Answer',

        # Ratings and Reviews
        'Rating', 'AggregateRating',

        # Real Estate
        'RealEstateListing', 'Apartment', 'House',
        'SingleFamilyResidence',

        # Food & Nutrition
        'Menu', 'MenuItem', 'MenuSection',

        # Sports
        'SportsOrganization', 'SportsTeam',

        # Government & Civic
        'GovernmentOrganization', 'GovernmentService', 'GovernmentBuilding',
        'PublicToilet', 'Park', 'Beach',

        # Transportation
        'Airport', 'TrainStation', 'BusStation', 'BusStop', 'TaxiStand',

        # Accommodation
        'Hotel', 'Motel', 'Hostel', 'CampingPitch', 'LodgingBusiness',

        # Structured Data Testing
        'WebPageElement', 'WPHeader', 'WPFooter', 'WPSideBar',

        # Other
        'Thing', 'CreativeWorkSeries', 'CreativeWorkSeason', 'Clip',
        'RadioSeries', 'RadioSeason', 'RadioEpisode', 'PodcastSeries',
        'PodcastSeason', 'PodcastEpisode'
    }

    # Priority levels for schemas (for recommendations)
    SCHEMA_TYPES_PRIORITY = {
        'high': {
            'Organization', 'LocalBusiness', 'Person', 'Article', 'Product',
            'WebSite', 'BreadcrumbList', 'FAQPage'
        },
        'medium': {
            'Review', 'AggregateRating', 'Event', 'JobPosting', 'Recipe',
            'HowTo', 'VideoObject', 'ImageObject'
        },
        'low': {
            'PostalAddress', 'ContactPoint', 'OpeningHoursSpecification',
            'Offer', 'PriceSpecification', 'Brand'
        }
    }

    # Schema relationships (for recommendations)
    SCHEMA_RELATIONSHIPS = {
        'Organization': ['PostalAddress', 'ContactPoint', 'Person'],
        'LocalBusiness': ['PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification', 'AggregateRating'],
        'Product': ['Offer', 'AggregateRating', 'Review', 'Brand'],
        'Article': ['Person', 'Organization', 'ImageObject'],
        'Event': ['Place', 'PostalAddress', 'Offer'],
        'Recipe': ['NutritionInformation', 'AggregateRating', 'Person'],
        'JobPosting': ['Organization', 'PostalAddress'],
        'Review': ['Rating', 'Person', 'Organization']
    }

    @classmethod
    def get_schema_priority(cls, schema_type: str) -> str:
        """
        Retourne la priorité d'un type de schema

        Args:
            schema_type: Type de schema

        Returns:
            Niveau de priorité ('high', 'medium', 'low', 'unknown')
        """
        for priority, schemas in cls.SCHEMA_TYPES_PRIORITY.items():
            if schema_type in schemas:
                return priority
        return 'unknown'

    @classmethod
    def get_related_schemas(cls, schema_type: str) -> list:
        """
        Retourne les schemas liés à un type donné

        Args:
            schema_type: Type de schema principal

        Returns:
            Liste des schemas liés
        """
        return cls.SCHEMA_RELATIONSHIPS.get(schema_type, [])

    @classmethod
    def is_standard_schema(cls, schema_type: str) -> bool:
        """
        Vérifie si un schema est standard

        Args:
            schema_type: Type de schema

        Returns:
            True si le schema est standard
        """
        return schema_type in cls.STANDARD_SCHEMA_TYPES

    @classmethod
    def validate_config(cls) -> dict:
        """
        Valide la configuration

        Returns:
            Dictionnaire de validation
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Vérifier les variables requises
        if not cls.VALUESERP_BASE_URL:
            validation['valid'] = False
            validation['errors'].append("VALUESERP_BASE_URL manquante")

        if not cls.USER_AGENT:
            validation['warnings'].append("USER_AGENT non défini")

        if cls.REQUEST_TIMEOUT <= 0:
            validation['errors'].append("REQUEST_TIMEOUT doit être positif")

        if not hasattr(cls, 'CACHE_ENABLED'):
            validation['errors'].append("CACHE_ENABLED manquant")

        if not hasattr(cls, 'CACHE_DURATION'):
            validation['errors'].append("CACHE_DURATION manquant")

        return validation