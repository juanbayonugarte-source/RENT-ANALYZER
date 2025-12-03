"""Zillow data collector via RapidAPI."""
import requests
import logging
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class ZillowDataCollector:
    """Collect real estate data from Zillow via RapidAPI."""
    
    def __init__(self):
        """Initialize Zillow collector."""
        self.api_key = Config.RAPIDAPI_KEY
        self.base_url = "https://zillow-com1.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key if self.api_key else "",
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
        }
    
    def get_rental_estimate(self, address: str, city: str, state: str = "CA") -> Optional[Dict]:
        """
        Get rental estimate for a specific address.
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
            
        Returns:
            Dictionary with rental data or None
        """
        if not self.api_key:
            logger.warning("Zillow API key not configured")
            return None
        
        try:
            # Search for property
            search_url = f"{self.base_url}/propertyExtendedSearch"
            params = {
                "location": f"{city}, {state}",
                "status_type": "ForRent"
            }
            
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_rental_data(data)
            else:
                logger.error(f"Zillow API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Zillow data: {str(e)}")
            return None
    
    def get_neighborhood_rentals(self, city: str, state: str = "CA", limit: int = 20) -> list:
        """
        Get rental listings for a neighborhood/city.
        
        Args:
            city: City name
            state: State abbreviation
            limit: Maximum number of listings
            
        Returns:
            List of rental listings
        """
        if not self.api_key:
            logger.warning("Zillow API key not configured")
            return []
        
        try:
            search_url = f"{self.base_url}/propertyExtendedSearch"
            params = {
                "location": f"{city}, {state}",
                "status_type": "ForRent",
                "resultsPerPage": min(limit, 40)
            }
            
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_listings(data)
            else:
                logger.error(f"Zillow API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Zillow listings: {str(e)}")
            return []
    
    def _parse_rental_data(self, data: Dict) -> Dict:
        """Parse Zillow API response for rental estimate."""
        try:
            if 'props' in data and len(data['props']) > 0:
                prop = data['props'][0]
                return {
                    'estimated_rent': prop.get('price'),
                    'bedrooms': prop.get('bedrooms'),
                    'bathrooms': prop.get('bathrooms'),
                    'sqft': prop.get('livingArea'),
                    'property_type': prop.get('propertyType'),
                    'address': prop.get('address'),
                    'zillow_url': prop.get('detailUrl')
                }
        except Exception as e:
            logger.error(f"Error parsing Zillow data: {str(e)}")
        
        return {}
    
    def _parse_listings(self, data: Dict) -> list:
        """Parse multiple rental listings."""
        listings = []
        
        try:
            if 'props' in data:
                for prop in data['props']:
                    listing = {
                        'price': prop.get('price', 0),
                        'bedrooms': prop.get('bedrooms', 0),
                        'bathrooms': prop.get('bathrooms', 0),
                        'sqft': prop.get('livingArea', 0),
                        'address': prop.get('address', ''),
                        'latitude': prop.get('latitude'),
                        'longitude': prop.get('longitude'),
                        'property_type': prop.get('propertyType', ''),
                        'url': prop.get('detailUrl', '')
                    }
                    listings.append(listing)
        except Exception as e:
            logger.error(f"Error parsing listings: {str(e)}")
        
        return listings
    
    def get_market_trends(self, city: str, state: str = "CA") -> Optional[Dict]:
        """
        Get market trends for a city.
        
        Args:
            city: City name
            state: State abbreviation
            
        Returns:
            Dictionary with market trend data
        """
        # Note: This would require Zillow's market data API endpoint
        # Placeholder for future implementation
        return {
            'median_rent': None,
            'rent_trend': None,
            'inventory': None
        }
