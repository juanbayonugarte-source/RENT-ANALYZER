"""Realty Mole API data collector."""
import requests
import logging
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class ZillowDataCollector:
    """Collect real estate data from Realty Mole API."""
    
    def __init__(self):
        """Initialize Realty Mole collector."""
        self.api_key = Config.REALTYMOLE_API_KEY
        self.base_url = "https://api.realtymole.com/api/v1"
        self.headers = {
            "x-api-key": self.api_key if self.api_key else ""
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
            logger.warning("Realty Mole API key not configured")
            return None
        
        try:
            # Get property estimate
            search_url = f"{self.base_url}/rentalPrice"
            params = {
                "address": f"{address}, {city}, {state}",
                "compCount": 5
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
                logger.error(f"Realty Mole API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Realty Mole data: {str(e)}")
            return None
    
    def get_neighborhood_rentals(self, city: str, state: str = "CA", limit: int = 20) -> list:
        """
        Get rental estimates for a neighborhood/city.
        
        Args:
            city: City name
            state: State abbreviation
            limit: Maximum number of listings (not used with Realty Mole)
            
        Returns:
            List of rental data
        """
        if not self.api_key:
            logger.warning("Realty Mole API key not configured")
            return []
        
        try:
            # Get average rental price for city
            search_url = f"{self.base_url}/rentalPrice"
            params = {
                "address": f"{city}, {state}",
                "compCount": min(limit, 10)
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
                logger.error(f"Realty Mole API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Realty Mole data: {str(e)}")
            return []
    
    def _parse_rental_data(self, data: Dict) -> Dict:
        """Parse Realty Mole API response for rental estimate."""
        try:
            return {
                'estimated_rent': data.get('rent'),
                'rent_range_low': data.get('rentRangeLow'),
                'rent_range_high': data.get('rentRangeHigh'),
                'price': data.get('price'),
                'bedrooms': data.get('bedrooms'),
                'bathrooms': data.get('bathrooms'),
                'sqft': data.get('squareFootage'),
                'property_type': data.get('propertyType'),
                'address': data.get('address'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude')
            }
        except Exception as e:
            logger.error(f"Error parsing Realty Mole data: {str(e)}")
        
        return {}
    
    def _parse_listings(self, data: Dict) -> list:
        """Parse rental data from Realty Mole."""
        listings = []
        
        try:
            # Realty Mole returns single property data, not multiple listings
            if 'rent' in data:
                listing = {
                    'price': data.get('rent', 0),
                    'rent_range_low': data.get('rentRangeLow', 0),
                    'rent_range_high': data.get('rentRangeHigh', 0),
                    'bedrooms': data.get('bedrooms', 0),
                    'bathrooms': data.get('bathrooms', 0),
                    'sqft': data.get('squareFootage', 0),
                    'address': data.get('address', ''),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'property_type': data.get('propertyType', '')
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
