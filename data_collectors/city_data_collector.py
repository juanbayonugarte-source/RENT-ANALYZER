"""City open data collector (template for various city data portals)."""
import requests
import pandas as pd
from typing import Dict, List, Optional

class CityDataCollector:
    """Collect data from city open data portals."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the city data collector.
        
        Args:
            base_url: Base URL for the city's open data API
            api_key: API key if required
        """
        self.base_url = base_url
        self.api_key = api_key
    
    def get_crime_data(self, lat: float, lon: float, radius_km: float = 1.0) -> pd.DataFrame:
        """
        Get crime data near a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            
        Returns:
            DataFrame with crime incidents
        """
        # Example implementation for Socrata-based APIs (used by many cities)
        # This is a template - adjust for specific city API
        
        if not self.base_url:
            # Return sample data for demonstration
            return self._get_sample_crime_data()
        
        try:
            url = f"{self.base_url}/resource/crime.json"
            params = {
                '$where': f"within_circle(location, {lat}, {lon}, {int(radius_km * 1000)})",
                '$limit': 1000
            }
            
            if self.api_key:
                params['$$app_token'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            df = pd.DataFrame(response.json())
            return df
            
        except Exception as e:
            print(f"Error fetching crime data: {e}")
            return pd.DataFrame()
    
    def get_school_ratings(self, zip_code: str) -> pd.DataFrame:
        """
        Get school ratings for a zip code.
        
        Args:
            zip_code: ZIP code
            
        Returns:
            DataFrame with school information
        """
        if not self.base_url:
            return self._get_sample_school_data()
        
        try:
            url = f"{self.base_url}/resource/schools.json"
            params = {
                'zip': zip_code,
                '$limit': 100
            }
            
            if self.api_key:
                params['$$app_token'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            df = pd.DataFrame(response.json())
            return df
            
        except Exception as e:
            print(f"Error fetching school data: {e}")
            return pd.DataFrame()
    
    def get_permits_and_development(self, neighborhood: str) -> pd.DataFrame:
        """
        Get building permits and development activity.
        
        Args:
            neighborhood: Neighborhood name
            
        Returns:
            DataFrame with permit data
        """
        if not self.base_url:
            return self._get_sample_permit_data()
        
        try:
            url = f"{self.base_url}/resource/permits.json"
            params = {
                'neighborhood': neighborhood,
                '$limit': 500
            }
            
            if self.api_key:
                params['$$app_token'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            df = pd.DataFrame(response.json())
            return df
            
        except Exception as e:
            print(f"Error fetching permit data: {e}")
            return pd.DataFrame()
    
    def _get_sample_crime_data(self) -> pd.DataFrame:
        """Generate sample crime data for demonstration."""
        import numpy as np
        
        data = {
            'incident_type': np.random.choice(
                ['Theft', 'Assault', 'Vandalism', 'Burglary'], 100
            ),
            'severity': np.random.choice(['Low', 'Medium', 'High'], 100),
            'date': pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
        }
        return pd.DataFrame(data)
    
    def _get_sample_school_data(self) -> pd.DataFrame:
        """Generate sample school data for demonstration."""
        import numpy as np
        
        data = {
            'school_name': [f'School {i}' for i in range(1, 11)],
            'rating': np.random.randint(5, 11, 10),
            'type': np.random.choice(['Elementary', 'Middle', 'High'], 10),
            'student_count': np.random.randint(200, 1500, 10)
        }
        return pd.DataFrame(data)
    
    def _get_sample_permit_data(self) -> pd.DataFrame:
        """Generate sample permit data for demonstration."""
        import numpy as np
        
        data = {
            'permit_type': np.random.choice(
                ['New Construction', 'Renovation', 'Addition'], 50
            ),
            'value': np.random.randint(50000, 5000000, 50),
            'status': np.random.choice(['Approved', 'Pending', 'Completed'], 50),
            'date': pd.date_range(end=pd.Timestamp.now(), periods=50, freq='W')
        }
        return pd.DataFrame(data)
    
    def calculate_crime_score(self, crime_df: pd.DataFrame) -> float:
        """
        Calculate a safety score based on crime data (0-100, higher is safer).
        
        Args:
            crime_df: DataFrame with crime data
            
        Returns:
            Safety score (0-100)
        """
        if crime_df.empty:
            return 75.0  # Default neutral score
        
        # Simple scoring: fewer crimes = higher score
        crime_count = len(crime_df)
        
        # Normalize (assuming 0-50 crimes per year is the range)
        score = max(0, 100 - (crime_count * 2))
        
        return score
