"""OpenStreetMap data collector for amenities and distances."""
import requests
import time
from typing import Dict, List, Tuple, Optional
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from config import Config

class OSMDataCollector:
    """Collect location and amenity data from OpenStreetMap."""
    
    def __init__(self):
        """Initialize the OSM data collector."""
        self.geolocator = Nominatim(user_agent=Config.OSM_USER_AGENT)
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates.
        
        Args:
            address: Street address or location name
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            location = self.geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None
    
    def get_neighborhood_amenities(
        self, 
        lat: float, 
        lon: float, 
        radius: int = 1000
    ) -> Dict[str, int]:
        """
        Get counts of various amenities near a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            
        Returns:
            Dictionary with amenity counts
        """
        amenity_types = {
            'schools': ['school', 'kindergarten', 'college', 'university'],
            'transit': ['bus_station', 'subway_entrance', 'train_station'],
            'restaurants': ['restaurant', 'cafe', 'fast_food'],
            'parks': ['park'],
            'hospitals': ['hospital', 'clinic', 'doctors'],
            'shopping': ['supermarket', 'mall', 'convenience']
        }
        
        results = {}
        
        for category, tags in amenity_types.items():
            count = 0
            for tag in tags:
                query = f"""
                [out:json];
                (
                  node["amenity"="{tag}"](around:{radius},{lat},{lon});
                  way["amenity"="{tag}"](around:{radius},{lat},{lon});
                );
                out count;
                """
                
                try:
                    response = requests.post(self.overpass_url, data={'data': query})
                    if response.status_code == 200:
                        data = response.json()
                        count += data.get('elements', [{}])[0].get('tags', {}).get('nodes', 0)
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"Error querying {tag}: {e}")
            
            results[category] = count
        
        return results
    
    def get_nearest_amenity_distance(
        self, 
        lat: float, 
        lon: float, 
        amenity_type: str
    ) -> Optional[float]:
        """
        Get distance to nearest amenity of specified type.
        
        Args:
            lat: Latitude
            lon: Longitude
            amenity_type: Type of amenity (e.g., 'school', 'hospital')
            
        Returns:
            Distance in kilometers or None
        """
        query = f"""
        [out:json];
        (
          node["amenity"="{amenity_type}"](around:5000,{lat},{lon});
          way["amenity"="{amenity_type}"](around:5000,{lat},{lon});
        );
        out center 1;
        """
        
        try:
            response = requests.post(self.overpass_url, data={'data': query})
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                
                if elements:
                    element = elements[0]
                    if 'lat' in element and 'lon' in element:
                        amenity_coords = (element['lat'], element['lon'])
                    elif 'center' in element:
                        amenity_coords = (element['center']['lat'], element['center']['lon'])
                    else:
                        return None
                    
                    distance = geodesic((lat, lon), amenity_coords).kilometers
                    return distance
        except Exception as e:
            print(f"Error finding nearest {amenity_type}: {e}")
        
        return None
    
    def get_transit_accessibility(self, lat: float, lon: float) -> Dict[str, any]:
        """
        Calculate transit accessibility score.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with transit metrics
        """
        # Count transit stops within walking distance (800m = ~10 min walk)
        transit_types = ['bus_station', 'subway_entrance', 'tram_stop', 'train_station']
        
        total_stops = 0
        for transit_type in transit_types:
            query = f"""
            [out:json];
            (
              node["amenity"="{transit_type}"](around:800,{lat},{lon});
              node["railway"="{transit_type}"](around:800,{lat},{lon});
            );
            out count;
            """
            
            try:
                response = requests.post(self.overpass_url, data={'data': query})
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('elements', []))
                    total_stops += count
                time.sleep(0.5)
            except Exception as e:
                print(f"Error querying {transit_type}: {e}")
        
        # Score based on number of stops (0-100 scale)
        transit_score = min(100, total_stops * 10)
        
        return {
            'transit_stops_nearby': total_stops,
            'transit_score': transit_score,
            'walkable_to_transit': total_stops > 0
        }
    
    def analyze_neighborhood(self, lat: float, lon: float) -> pd.DataFrame:
        """
        Comprehensive neighborhood analysis.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            DataFrame with neighborhood metrics
        """
        amenities = self.get_neighborhood_amenities(lat, lon)
        transit = self.get_transit_accessibility(lat, lon)
        
        # Combine all metrics
        data = {
            'latitude': lat,
            'longitude': lon,
            **amenities,
            **transit
        }
        
        return pd.DataFrame([data])
