"""
Constantes et énumérations pour les schemas Schema.org
"""
from typing import Dict, List


class SchemaConstants:
    """Classe contenant toutes les constantes Schema.org"""

    @staticmethod
    def get_required_fields() -> Dict[str, List[str]]:
        """Retourne les champs obligatoires pour chaque type de schema"""
        return {
            'Organization': ['name', '@context', '@type'],
            'LocalBusiness': ['name', '@context', '@type'],
            'Restaurant': ['name', '@context', '@type'],
            'Product': ['name', 'image', 'offers', '@context', '@type'],
            'Article': ['headline', 'image', 'datePublished', '@context', '@type'],
            'NewsArticle': ['headline', 'image', 'datePublished', '@context', '@type'],
            'BlogPosting': ['headline', 'image', 'datePublished', '@context', '@type'],
            'FAQPage': ['mainEntity', '@context', '@type'],
            'BreadcrumbList': ['itemListElement', '@context', '@type'],
            'WebSite': ['name', 'url', '@context', '@type'],
            'Person': ['name', '@context', '@type'],
            'Event': ['name', 'startDate', 'location', '@context', '@type'],
            'Recipe': ['name', 'image', 'recipeIngredient', 'recipeInstructions', '@context', '@type'],
            'VideoObject': ['name', 'description', 'thumbnailUrl', 'uploadDate', '@context', '@type'],
            'Review': ['itemReviewed', 'author', 'reviewRating', '@context', '@type'],
            'AggregateRating': ['ratingValue', 'reviewCount', '@context', '@type'],
            'HowTo': ['name', 'step', '@context', '@type'],
            'JobPosting': ['title', 'description', 'datePosted', 'hiringOrganization', '@context', '@type'],
            'Course': ['name', 'description', 'provider', '@context', '@type'],
            'Service': ['name', 'serviceType', '@context', '@type'],
            'SoftwareApplication': ['name', 'operatingSystem', 'applicationCategory', '@context', '@type']
        }

    @staticmethod
    def get_recommended_fields() -> Dict[str, List[str]]:
        """Retourne les champs recommandés par Google pour chaque type"""
        return {
            'Organization': ['url', 'logo', 'sameAs', 'contactPoint'],
            'LocalBusiness': ['address', 'geo', 'telephone', 'openingHoursSpecification', 'priceRange'],
            'Restaurant': ['address', 'geo', 'telephone', 'openingHoursSpecification', 'priceRange', 'servesCuisine'],
            'Product': ['description', 'sku', 'brand', 'aggregateRating', 'review'],
            'Article': ['author', 'publisher', 'dateModified', 'description'],
            'NewsArticle': ['author', 'publisher', 'dateModified', 'description', 'articleSection'],
            'BlogPosting': ['author', 'publisher', 'dateModified', 'description'],
            'Event': ['description', 'endDate', 'organizer', 'performer', 'offers'],
            'Recipe': ['author', 'datePublished', 'description', 'nutrition', 'prepTime', 'cookTime'],
            'FAQPage': [],  # Toutes les propriétés sont dans mainEntity
            'WebSite': ['potentialAction', 'description'],
            'VideoObject': ['duration', 'embedUrl', 'contentUrl'],
            'HowTo': ['description', 'totalTime', 'estimatedCost', 'tool', 'supply'],
            'JobPosting': ['jobLocation', 'baseSalary', 'employmentType', 'validThrough'],
            'Service': ['provider', 'areaServed', 'description']
        }

    @staticmethod
    def get_schema_enumerations() -> Dict[str, List[str]]:
        """Retourne les valeurs d'énumération valides pour Schema.org"""
        return {
            'availability': [
                'https://schema.org/InStock',
                'https://schema.org/OutOfStock',
                'https://schema.org/PreOrder',
                'https://schema.org/BackOrder',
                'https://schema.org/Discontinued',
                'https://schema.org/InStoreOnly',
                'https://schema.org/LimitedAvailability',
                'https://schema.org/OnlineOnly',
                'https://schema.org/PreSale',
                'https://schema.org/SoldOut'
            ],
            'itemCondition': [
                'https://schema.org/NewCondition',
                'https://schema.org/UsedCondition',
                'https://schema.org/RefurbishedCondition',
                'https://schema.org/DamagedCondition'
            ],
            'eventAttendanceMode': [
                'https://schema.org/OfflineEventAttendanceMode',
                'https://schema.org/OnlineEventAttendanceMode',
                'https://schema.org/MixedEventAttendanceMode'
            ],
            'eventStatus': [
                'https://schema.org/EventScheduled',
                'https://schema.org/EventCancelled',
                'https://schema.org/EventMovedOnline',
                'https://schema.org/EventPostponed',
                'https://schema.org/EventRescheduled'
            ],
            'dayOfWeek': [
                'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday'
            ],
            'employmentType': [
                'FULL_TIME', 'PART_TIME', 'CONTRACTOR', 'TEMPORARY',
                'INTERN', 'VOLUNTEER', 'PER_DIEM', 'OTHER'
            ],
            'returnPolicyCategory': [
                'https://schema.org/MerchantReturnFiniteReturnWindow',
                'https://schema.org/MerchantReturnNotPermitted',
                'https://schema.org/MerchantReturnUnlimitedWindow',
                'https://schema.org/MerchantReturnUnspecified'
            ],
            'applicationCategory': [
                'GameApplication',
                'SocialNetworkingApplication',
                'TravelApplication',
                'ShoppingApplication',
                'SportsApplication',
                'LifestyleApplication',
                'BusinessApplication',
                'DesignApplication',
                'DeveloperApplication',
                'DriverApplication',
                'EducationalApplication',
                'HealthApplication',
                'FinanceApplication',
                'SecurityApplication',
                'BrowserApplication',
                'CommunicationApplication',
                'DesktopEnhancementApplication',
                'EntertainmentApplication',
                'MultimediaApplication',
                'HomeApplication',
                'UtilitiesApplication',
                'ReferenceApplication'
            ],
            'priceRange': ['€', '€€', '€€€', '€€€€', '$', '$$', '$$$', '$$$$'],
            'unitCode': [
                'GRM',  # Gramme
                'KGM',  # Kilogramme
                'LBR',  # Livre
                'ONZ',  # Once
                'CMT',  # Centimètre
                'MTR',  # Mètre
                'INH',  # Pouce
                'FOT',  # Pied
                'MLT',  # Millilitre
                'LTR',  # Litre
                'GAL',  # Gallon
            ],
            'currencies': ['EUR', 'USD', 'GBP', 'CHF', 'CAD', 'AUD', 'JPY', 'CNY']
        }

    @staticmethod
    def get_schema_relationships() -> Dict[str, List[str]]:
        """Retourne les relations recommandées entre schemas"""
        return {
            'Product': ['Offer', 'AggregateRating', 'Review', 'Brand'],
            'LocalBusiness': ['PostalAddress', 'GeoCoordinates', 'OpeningHoursSpecification', 'AggregateRating'],
            'Article': ['Person', 'Organization', 'ImageObject'],
            'Event': ['Place', 'PostalAddress', 'Offer', 'VirtualLocation'],
            'Recipe': ['NutritionInformation', 'AggregateRating', 'VideoObject'],
            'Organization': ['ContactPoint', 'PostalAddress', 'Logo'],
            'WebSite': ['SearchAction', 'Organization'],
            'FAQPage': ['Question', 'Answer'],
            'HowTo': ['HowToStep', 'HowToTool', 'HowToSupply'],
            'Course': ['CourseInstance', 'Organization'],
            'JobPosting': ['Organization', 'Place', 'MonetaryAmount']
        }

    @staticmethod
    def get_priority_schemas() -> List[str]:
        """Retourne les schemas prioritaires pour le SEO"""
        return [
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
            'AggregateRating',
            'HowTo',
            'JobPosting'
        ]

    @staticmethod
    def get_google_supported_schemas() -> List[str]:
        """Retourne les schemas officiellement supportés par Google pour les résultats enrichis"""
        return [
            'Article', 'NewsArticle', 'BlogPosting',
            'BreadcrumbList',
            'Course', 'CourseInstance',
            'Dataset',
            'Event',
            'FAQPage',
            'HowTo',
            'JobPosting',
            'LocalBusiness', 'Restaurant', 'Store',
            'Movie',
            'Product',
            'Recipe',
            'Review', 'AggregateRating',
            'SoftwareApplication',
            'VideoObject',
            'WebSite',
            'Organization',
            'Person'
        ]