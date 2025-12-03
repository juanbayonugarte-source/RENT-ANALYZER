"""Walk Score API data collector."""
import requests
import logging
from typing import Dict, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

class WalkScoreCollector:
    """Collect walkability, transit, and bike scores from Walk Score API."""
    
    def __init__(self):
        """Initialize Walk Score collector."""
        self.api_key = Config.WALKSCORE_API_KEY
        self.base_url = "https://api.walkscore.com/score"
    
    def get_scores(self, latitude: float, longitude: float, address: str = "") -> Dict:
        """
        Get Walk Score, Transit Score, and Bike Score for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            address: Street address (optional, improves accuracy)
            
        Returns:
            Dictionary with walk, transit, and bike scores
        """
        if not self.api_key:
            logger.warning("Walk Score API key not configured")
            return self._get_default_scores()
        
        try:
            params = {
                'format': 'json',
                'lat': latitude,
                'lon': longitude,
                'transit': 1,
                'bike': 1,
                'wsapikey': self.api_key
            }
            
            if address:
                params['address'] = address
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_scores(data)
            else:
                logger.error(f"Walk Score API error: {response.status_code}")
                return self._get_default_scores()
                
        except Exception as e:
            logger.error(f"Error fetching Walk Score data: {str(e)}")
            return self._get_default_scores()
    
    def _parse_scores(self, data: Dict) -> Dict:
        """Parse Walk Score API response."""
        scores = {
            'walk_score': data.get('walkscore', 50),
            'walk_description': data.get('description', 'Unknown'),
            'transit_score': None,
            'transit_description': None,
            'bike_score': None,
            'bike_description': None
        }
        
        # Transit score (if available)
        if 'transit' in data:
            transit = data['transit']
            scores['transit_score'] = transit.get('score')
            scores['transit_description'] = transit.get('description')
        
        # Bike score (if available)
        if 'bike' in data:
            bike = data['bike']
            scores['bike_score'] = bike.get('score')
            scores['bike_description'] = bike.get('description')
        
        return scores
    
    def _get_default_scores(self) -> Dict:
        """Return default scores when API is unavailable."""
        return {
            'walk_score': 50,
            'walk_description': 'Somewhat Walkable',
            'transit_score': 50,
            'transit_description': 'Some Transit',
            'bike_score': 50,
            'bike_description': 'Bikeable'
        }
    
    def get_walk_score_only(self, latitude: float, longitude: float) -> int:
        """
        Get just the walk score number.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Walk score (0-100)
        """
        scores = self.get_scores(latitude, longitude)
        return scores.get('walk_score', 50)
    
    def interpret_walk_score(self, score: int) -> str:
        """
        Interpret walk score into description.
        
        Args:
            score: Walk score (0-100)
            
        Returns:
            Description string
        """
        if score >= 90:
            return "Walker's Paradise"
        elif score >= 70:
            return "Very Walkable"
        elif score >= 50:
            return "Somewhat Walkable"
        elif score >= 25:
            return "Car-Dependent"
        else:
            return "Very Car-Dependent"
    
    def interpret_transit_score(self, score: Optional[int]) -> str:
        """
        Interpret transit score into description.
        
        Args:
            score: Transit score (0-100)
            
        Returns:
            Description string
        """
        if score is None:
            return "No Transit Data"
        elif score >= 90:
            return "Rider's Paradise"
        elif score >= 70:
            return "Excellent Transit"
        elif score >= 50:
            return "Good Transit"
        elif score >= 25:
            return "Some Transit"
        else:
            return "Minimal Transit"
    
    def interpret_bike_score(self, score: Optional[int]) -> str:
        """
        Interpret bike score into description.
        
        Args:
            score: Bike score (0-100)
            
        Returns:
            Description string
        """
        if score is None:
            return "No Bike Data"
        elif score >= 90:
            return "Biker's Paradise"
        elif score >= 70:
            return "Very Bikeable"
        elif score >= 50:
            return "Bikeable"
        else:
            return "Somewhat Bikeable"
