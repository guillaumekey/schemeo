"""
Templates complets pour tous les types de schemas Schema.org
"""
from datetime import datetime


class SchemaTemplates:
    """Classe contenant tous les templates de schemas"""

    @staticmethod
    def get_all_templates():
        """Retourne tous les templates de schemas"""
        return {
            'Organization': {
                "@context": "https://schema.org",
                "@type": "Organization",
                # Propriétés essentielles
                "name": "",
                "url": "",
                "logo": {
                    "@type": "ImageObject",
                    "url": "",
                    "width": 300,
                    "height": 300
                },
                "description": "",
                "alternateName": "",
                # Coordonnées et localisation
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                    "addressLocality": "",
                    "addressRegion": "",
                    "postalCode": "",
                    "addressCountry": ""
                },
                "contactPoint": [{
                    "@type": "ContactPoint",
                    "contactType": "customer service",
                    "telephone": "",
                    "email": "",
                    "areaServed": "",
                    "availableLanguage": []
                }],
                "telephone": "",
                "email": "",
                "faxNumber": "",
                # Identifiants d'entreprise
                "legalName": "",
                "taxID": "",
                "vatID": "",
                "duns": "",
                "naics": "",
                "isicV4": "",
                "leiCode": "",
                "globalLocationNumber": "",
                # Structure organisationnelle
                "parentOrganization": None,
                "subOrganization": [],
                "department": [],
                "memberOf": [],
                "founder": None,
                "numberOfEmployees": {
                    "@type": "QuantitativeValue",
                    "value": ""
                },
                # Dates et historique
                "foundingDate": "",
                "foundingLocation": {
                    "@type": "Place",
                    "name": "",
                    "address": ""
                },
                # Évaluations
                "aggregateRating": None,
                "review": [],
                "award": [],
                # Propriétés sociales
                "sameAs": [],
                "knowsAbout": [],
                "slogan": ""
            },

            'LocalBusiness': {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                # Hérite d'Organization
                "name": "",
                "url": "",
                "logo": {
                    "@type": "ImageObject",
                    "url": "",
                    "width": 300,
                    "height": 300
                },
                "description": "",
                "image": [],
                # Adresse et localisation
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                    "addressLocality": "",
                    "addressRegion": "",
                    "postalCode": "",
                    "addressCountry": ""
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": "",
                    "longitude": ""
                },
                "hasMap": "",
                # Contact
                "telephone": "",
                "email": "",
                # Horaires
                "openingHours": "",  # Format simple
                "openingHoursSpecification": [],
                "specialOpeningHoursSpecification": [],
                # Commerce
                "currenciesAccepted": "",
                "paymentAccepted": "",
                "priceRange": "",
                "acceptsReservations": "",
                # Équipements
                "amenityFeature": [],
                "maximumAttendeeCapacity": "",
                "smokingAllowed": "",
                # Évaluations
                "aggregateRating": None,
                "review": [],
                # Réseaux sociaux
                "sameAs": []
            },

            'Restaurant': {
                "@context": "https://schema.org",
                "@type": "Restaurant",
                # Hérite de LocalBusiness + spécificités
                "name": "",
                "url": "",
                "image": [],
                "description": "",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                    "addressLocality": "",
                    "addressRegion": "",
                    "postalCode": "",
                    "addressCountry": ""
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": "",
                    "longitude": ""
                },
                "telephone": "",
                "email": "",
                "priceRange": "",
                "currenciesAccepted": "",
                "paymentAccepted": "",
                # Spécifique Restaurant
                "servesCuisine": [],
                "hasMenu": "",
                "acceptsReservations": True,
                "starRating": None,
                # Horaires
                "openingHoursSpecification": [],
                # Évaluations
                "aggregateRating": None,
                "review": []
            },

            'Product': {
                "@context": "https://schema.org",
                "@type": "Product",
                # Identification
                "name": "",
                "description": "",
                "image": [],
                "sku": "",
                "gtin": "",
                "gtin8": "",
                "gtin12": "",
                "gtin13": "",
                "gtin14": "",
                "mpn": "",
                "productID": "",
                # Marque et fabricant
                "brand": {
                    "@type": "Brand",
                    "name": ""
                },
                "manufacturer": {
                    "@type": "Organization",
                    "name": ""
                },
                "model": "",
                # Caractéristiques
                "size": "",
                "color": "",
                "material": "",
                "weight": {
                    "@type": "QuantitativeValue",
                    "value": "",
                    "unitCode": ""
                },
                "width": {
                    "@type": "QuantitativeValue",
                    "value": "",
                    "unitCode": ""
                },
                "height": {
                    "@type": "QuantitativeValue",
                    "value": "",
                    "unitCode": ""
                },
                "depth": {
                    "@type": "QuantitativeValue",
                    "value": "",
                    "unitCode": ""
                },
                # Offres
                "offers": {
                    "@type": "Offer",
                    "price": "",
                    "priceCurrency": "",
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition",
                    "priceValidUntil": "",
                    "seller": {
                        "@type": "Organization",
                        "name": ""
                    },
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingRate": {
                            "@type": "MonetaryAmount",
                            "value": "",
                            "currency": ""
                        },
                        "shippingDestination": {
                            "@type": "DefinedRegion",
                            "addressCountry": ""
                        }
                    },
                    "hasMerchantReturnPolicy": {
                        "@type": "MerchantReturnPolicy",
                        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                        "merchantReturnDays": 30
                    }
                },
                # Relations
                "isVariantOf": None,
                "isAccessoryOrSparePartFor": None,
                "isConsumableFor": None,
                "isRelatedTo": [],
                # Évaluations
                "aggregateRating": None,
                "review": []
            },

            'Article': {
                "@context": "https://schema.org",
                "@type": "Article",
                # Propriétés requises
                "headline": "",
                "image": [],
                "datePublished": "",
                # Propriétés recommandées
                "author": {
                    "@type": "Person",
                    "name": "",
                    "url": ""
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "",
                        "width": 60,
                        "height": 60
                    }
                },
                "dateModified": "",
                "description": "",
                # Contenu
                "articleBody": "",
                "articleSection": "",
                "wordCount": "",
                "keywords": "",
                "backstory": "",
                # Accessibilité
                "speakable": {
                    "@type": "SpeakableSpecification",
                    "xpath": []
                },
                # Liens et références
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": ""
                }
            },

            'NewsArticle': {
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                # Hérite d'Article avec spécificités actualités
                "headline": "",
                "image": [],
                "datePublished": "",
                "dateModified": "",
                "author": {
                    "@type": "Person",
                    "name": "",
                    "url": ""
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "",
                    "logo": {
                        "@type": "ImageObject",
                        "url": ""
                    }
                },
                "description": "",
                "articleBody": "",
                "articleSection": "",
                # Spécifique aux actualités
                "dateline": "",
                "printEdition": "",
                "printPage": "",
                "printSection": ""
            },

            'FAQPage': {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": []
            },

            'BreadcrumbList': {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": []
            },

            'WebSite': {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "",
                "url": "",
                "description": "",
                "publisher": {
                    "@type": "Organization",
                    "name": ""
                },
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": {
                        "@type": "EntryPoint",
                        "urlTemplate": ""
                    },
                    "query-input": "required name=search_term_string"
                }
            },

            'Person': {
                "@context": "https://schema.org",
                "@type": "Person",
                "name": "",
                "givenName": "",
                "familyName": "",
                "additionalName": "",
                "jobTitle": "",
                "worksFor": {
                    "@type": "Organization",
                    "name": ""
                },
                "email": "",
                "telephone": "",
                "image": "",
                "url": "",
                "sameAs": [],
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                    "addressLocality": "",
                    "addressRegion": "",
                    "postalCode": "",
                    "addressCountry": ""
                },
                "birthDate": "",
                "birthPlace": "",
                "nationality": "",
                "alumniOf": [],
                "award": [],
                "knowsAbout": []
            },

            'Event': {
                "@context": "https://schema.org",
                "@type": "Event",
                "name": "",
                "description": "",
                "startDate": "",
                "endDate": "",
                "eventStatus": "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "location": {
                    "@type": "Place",
                    "name": "",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "",
                        "addressLocality": "",
                        "addressRegion": "",
                        "postalCode": "",
                        "addressCountry": ""
                    }
                },
                "image": [],
                "organizer": {
                    "@type": "Organization",
                    "name": "",
                    "url": ""
                },
                "performer": [],
                "sponsor": [],
                "offers": {
                    "@type": "Offer",
                    "name": "",
                    "price": "",
                    "priceCurrency": "",
                    "availability": "https://schema.org/InStock",
                    "url": "",
                    "validFrom": ""
                },
                "duration": "",
                "maximumAttendeeCapacity": "",
                "remainingAttendeeCapacity": ""
            },

            'Recipe': {
                "@context": "https://schema.org",
                "@type": "Recipe",
                "name": "",
                "description": "",
                "image": [],
                "author": {
                    "@type": "Person",
                    "name": ""
                },
                "datePublished": "",
                "prepTime": "",
                "cookTime": "",
                "totalTime": "",
                "recipeYield": "",
                "recipeCategory": "",
                "recipeCuisine": "",
                "recipeIngredient": [],
                "recipeInstructions": [],
                "nutrition": {
                    "@type": "NutritionInformation",
                    "calories": "",
                    "carbohydrateContent": "",
                    "proteinContent": "",
                    "fatContent": "",
                    "fiberContent": "",
                    "sugarContent": "",
                    "sodiumContent": ""
                },
                "aggregateRating": None,
                "video": None,
                "keywords": "",
                "suitableForDiet": []
            },

            'VideoObject': {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": "",
                "description": "",
                "thumbnailUrl": [],
                "uploadDate": "",
                "duration": "",
                "contentUrl": "",
                "embedUrl": "",
                "interactionStatistic": {
                    "@type": "InteractionCounter",
                    "interactionType": {"@type": "WatchAction"},
                    "userInteractionCount": ""
                },
                "expires": "",
                "hasPart": [],
                "publication": [],
                "regionsAllowed": []
            },

            'Review': {
                "@context": "https://schema.org",
                "@type": "Review",
                "itemReviewed": {
                    "@type": "Thing",
                    "name": ""
                },
                "author": {
                    "@type": "Person",
                    "name": ""
                },
                "datePublished": "",
                "reviewBody": "",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "",
                    "bestRating": "5",
                    "worstRating": "1"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": ""
                }
            },

            'AggregateRating': {
                "@context": "https://schema.org",
                "@type": "AggregateRating",
                "ratingValue": "",
                "reviewCount": "",
                "bestRating": "5",
                "worstRating": "1",
                "ratingCount": ""
            },

            'HowTo': {
                "@context": "https://schema.org",
                "@type": "HowTo",
                "name": "",
                "description": "",
                "image": [],
                "totalTime": "",
                "estimatedCost": {
                    "@type": "MonetaryAmount",
                    "currency": "",
                    "value": ""
                },
                "tool": [],
                "supply": [],
                "step": [],
                "video": None
            },

            'JobPosting': {
                "@context": "https://schema.org",
                "@type": "JobPosting",
                "title": "",
                "description": "",
                "datePosted": "",
                "validThrough": "",
                "employmentType": [],
                "hiringOrganization": {
                    "@type": "Organization",
                    "name": "",
                    "sameAs": ""
                },
                "jobLocation": {
                    "@type": "Place",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "",
                        "addressLocality": "",
                        "addressRegion": "",
                        "postalCode": "",
                        "addressCountry": ""
                    }
                },
                "baseSalary": {
                    "@type": "MonetaryAmount",
                    "currency": "",
                    "value": {
                        "@type": "QuantitativeValue",
                        "value": "",
                        "unitText": "YEAR"
                    }
                },
                "experienceRequirements": "",
                "qualifications": "",
                "responsibilities": "",
                "skills": [],
                "benefits": [],
                "identifier": {
                    "@type": "PropertyValue",
                    "name": "",
                    "value": ""
                }
            },

            'Course': {
                "@context": "https://schema.org",
                "@type": "Course",
                "name": "",
                "description": "",
                "provider": {
                    "@type": "Organization",
                    "name": "",
                    "sameAs": ""
                },
                "educationalCredentialAwarded": "",
                "courseCode": "",
                "coursePrerequisites": [],
                "hasCourseInstance": []
            },

            'Service': {
                "@context": "https://schema.org",
                "@type": "Service",
                "name": "",
                "description": "",
                "serviceType": "",
                "provider": {
                    "@type": "Organization",
                    "name": ""
                },
                "areaServed": {
                    "@type": "Place",
                    "name": ""
                },
                "hasOfferCatalog": {
                    "@type": "OfferCatalog",
                    "name": "",
                    "itemListElement": []
                },
                "aggregateRating": None,
                "review": []
            },

            'BlogPosting': {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                # Hérite d'Article
                "headline": "",
                "image": [],
                "datePublished": "",
                "dateModified": "",
                "author": {
                    "@type": "Person",
                    "name": "",
                    "url": ""
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "",
                    "logo": {
                        "@type": "ImageObject",
                        "url": ""
                    }
                },
                "description": "",
                "articleBody": "",
                "articleSection": "",
                "keywords": "",
                # Spécifique Blog
                "blogPost": "",
                "isPartOf": {
                    "@type": "Blog",
                    "@id": "",
                    "name": ""
                }
            },

            'SoftwareApplication': {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "",
                "operatingSystem": "",
                "applicationCategory": "",
                "applicationSubCategory": "",
                "downloadUrl": "",
                "fileSize": "",
                "softwareVersion": "",
                "softwareRequirements": "",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "EUR"
                },
                "aggregateRating": None,
                "screenshot": [],
                "featureList": []
            }
        }