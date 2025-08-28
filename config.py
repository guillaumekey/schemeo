"""
Configuration centrale de l'application
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

    # Schema.org Settings
    STANDARD_SCHEMA_TYPES = {
        # Content types
        'Article', 'NewsArticle', 'BlogPosting', 'ScholarlyArticle', 'TechArticle',
        'Report', 'SocialMediaPosting', 'LiveBlogPosting',

        # Business & Organizations
        'Organization', 'Corporation', 'LocalBusiness', 'Store', 'Restaurant',
        'FoodEstablishment', 'Bakery', 'BarOrPub', 'Brewery', 'CafeOrCoffeeShop',
        'FastFoodRestaurant', 'IceCreamShop', 'Restaurant', 'Winery',

        # Products & Services
        'Product', 'Service', 'ProfessionalService', 'Offer', 'AggregateOffer',
        'Brand', 'Model', 'ProductModel',

        # People & Roles
        'Person', 'Patient', 'MedicalAudience', 'EducationalAudience',

        # Places
        'Place', 'LocalBusiness', 'AdministrativeArea', 'CivicStructure',
        'Landform', 'LandmarksOrHistoricalBuildings', 'Residence',
        'TouristAttraction', 'TouristDestination',

        # Events
        'Event', 'BusinessEvent', 'ChildrensEvent', 'ComedyEvent', 'CourseInstance',
        'DanceEvent', 'DeliveryEvent', 'EducationEvent', 'EventSeries', 'ExhibitionEvent',
        'Festival', 'FoodEvent', 'LiteraryEvent', 'MusicEvent', 'PublicationEvent',
        'SaleEvent', 'ScreeningEvent', 'SocialEvent', 'SportsEvent', 'TheaterEvent',
        'VisualArtsEvent',

        # Creative Works
        'CreativeWork', 'Book', 'Course', 'Episode', 'Game', 'MediaObject',
        'Movie', 'MusicPlaylist', 'MusicRecording', 'Painting', 'Photograph',
        'PublicationIssue', 'PublicationVolume', 'Review', 'Sculpture',
        'Series', 'SoftwareApplication', 'TVEpisode', 'TVSeason', 'TVSeries',
        'VideoGame', 'VideoObject', 'WebApplication',

        # Structured Data
        'BreadcrumbList', 'ItemList', 'CollectionPage', 'ProfilePage',
        'SearchResultsPage', 'WebPage', 'WebSite', 'AboutPage', 'CheckoutPage',
        'ContactPage', 'FAQPage', 'QAPage', 'MedicalWebPage', 'RealEstateListing',

        # Reviews & Ratings
        'Review', 'AggregateRating', 'Rating', 'ClaimReview', 'CriticReview',
        'EmployerReview', 'UserReview',

        # Questions & Answers
        'Question', 'Answer', 'FAQPage', 'QAPage',

        # How-to & Instructions
        'HowTo', 'HowToDirection', 'HowToSection', 'HowToStep', 'HowToSupply',
        'HowToTip', 'HowToTool',

        # Medical & Health
        'MedicalEntity', 'MedicalCondition', 'Drug', 'Hospital',
        'MedicalProcedure', 'MedicalClinic', 'Pharmacy', 'Physician',

        # Education
        'Course', 'CourseInstance', 'EducationalOrganization', 'School',
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
        'ImageObject', 'VideoObject', 'AudioObject', 'MediaObject',

        # Lists and Enumerations
        'ItemList', 'BreadcrumbList', 'OfferCatalog', 'ListItem',

        # Geographic
        'PostalAddress', 'GeoCoordinates', 'GeoShape', 'ContactPoint',

        # Time-based
        'OpeningHoursSpecification', 'Schedule',

        # Recipe
        'Recipe', 'NutritionInformation',

        # Financial
        'Invoice', 'PriceSpecification', 'PaymentMethod', 'LoanOrCredit',
        'BankAccount', 'FinancialProduct', 'FinancialService',

        # Entertainment
        'Game', 'VideoGame', 'MovieSeries', 'MusicAlbum', 'MusicGroup',
        'TheaterGroup', 'DanceGroup', 'PerformingGroup',

        # Vehicles
        'Vehicle', 'Car', 'Motorcycle', 'BusOrCoach',

        # Real Estate
        'RealEstateListing', 'Residence', 'Apartment', 'House',
        'SingleFamilyResidence',

        # Food & Nutrition
        'NutritionInformation', 'Recipe', 'Menu', 'MenuItem', 'MenuSection',

        # Sports
        'SportsOrganization', 'SportsTeam', 'SportsEvent',

        # Government & Civic
        'GovernmentOrganization', 'GovernmentService', 'GovernmentBuilding',
        'CivicStructure', 'PublicToilet', 'Park', 'Beach',

        # Transportation
        'Airport', 'TrainStation', 'BusStation', 'BusStop', 'TaxiStand',

        # Accommodation
        'Hotel', 'Motel', 'Hostel', 'CampingPitch', 'LodgingBusiness',

        # Other
        'Thing', 'CreativeWorkSeries', 'CreativeWorkSeason', 'Clip',
        'RadioSeries', 'RadioSeason', 'RadioEpisode', 'PodcastSeries',
        'PodcastSeason', 'PodcastEpisode'
    }

    SCHEMA_TYPES_PRIORITY = [
        'Organization',
        'LocalBusiness',
        'Product',
        'Article',
        'FAQPage',
        'BreadcrumbList',
        'WebSite',
        'Person',
        'Event',
        'Recipe',
        'VideoObject',
        'Review',
        'AggregateRating'
    ]

    # Scraping Settings
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Cache Settings
    CACHE_ENABLED = True
    CACHE_DURATION = 3600  # 1 hour in seconds