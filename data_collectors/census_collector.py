"""US Census API data collector."""
import requests
import pandas as pd
from typing import Dict, List, Optional
from config import Config

class CensusDataCollector:
    """Collect demographic and economic data from US Census API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Census data collector."""
        self.api_key = api_key or Config.CENSUS_API_KEY
        self.base_url = Config.CENSUS_BASE_URL
        
    def get_demographics(self, state: str, county: str = "*", tract: str = "*") -> pd.DataFrame:
        """
        Get demographic data for specified geographic area.
        
        Args:
            state: State FIPS code or name
            county: County FIPS code or "*" for all
            tract: Census tract or "*" for all
            
        Returns:
            DataFrame with demographic data
        """
        # ACS 5-Year variables for demographics
        variables = [
            'B01003_001E',  # Total Population
            'B19013_001E',  # Median Household Income
            'B25064_001E',  # Median Gross Rent
            'B15003_022E',  # Bachelor's degree
            'B15003_023E',  # Master's degree
            'B25003_002E',  # Owner occupied
            'B25003_003E',  # Renter occupied
            'B01002_001E',  # Median Age
            'B02001_002E',  # White alone
            'B02001_003E',  # Black alone
            'B02001_005E',  # Asian alone
            'B03003_003E',  # Hispanic or Latino
            'B23025_005E',  # Unemployed
        ]
        
        url = f"{self.base_url}/{Config.CENSUS_YEAR}/acs/acs5"
        params = {
            'get': ','.join(variables + ['NAME']),
            'for': f'tract:{tract}',
            'in': f'state:{state} county:{county}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            
            # Rename columns for readability
            df.columns = [
                'total_population', 'median_income', 'median_rent',
                'bachelors', 'masters', 'owner_occupied', 'renter_occupied',
                'median_age', 'white', 'black', 'asian', 'hispanic',
                'unemployed', 'name', 'state', 'county', 'tract'
            ]
            
            # Convert to numeric
            numeric_cols = df.columns.difference(['name', 'state', 'county', 'tract'])
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            
            # Calculate derived metrics
            df['college_educated_pct'] = (
                (df['bachelors'] + df['masters']) / df['total_population'] * 100
            )
            df['renter_pct'] = (
                df['renter_occupied'] / (df['owner_occupied'] + df['renter_occupied']) * 100
            )
            df['unemployment_rate'] = (
                df['unemployed'] / df['total_population'] * 100
            )
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Census data: {e}")
            return pd.DataFrame()
    
    def get_income_distribution(self, state: str, county: str = "*") -> pd.DataFrame:
        """Get income distribution data."""
        variables = [
            'B19001_002E',  # Less than $10,000
            'B19001_003E',  # $10,000 to $14,999
            'B19001_004E',  # $15,000 to $19,999
            'B19001_005E',  # $20,000 to $24,999
            'B19001_006E',  # $25,000 to $29,999
            'B19001_007E',  # $30,000 to $34,999
            'B19001_008E',  # $35,000 to $39,999
            'B19001_009E',  # $40,000 to $44,999
            'B19001_010E',  # $45,000 to $49,999
            'B19001_011E',  # $50,000 to $59,999
            'B19001_012E',  # $60,000 to $74,999
            'B19001_013E',  # $75,000 to $99,999
            'B19001_014E',  # $100,000 to $124,999
            'B19001_015E',  # $125,000 to $149,999
            'B19001_016E',  # $150,000 to $199,999
            'B19001_017E',  # $200,000 or more
        ]
        
        url = f"{self.base_url}/{Config.CENSUS_YEAR}/acs/acs5"
        params = {
            'get': ','.join(variables + ['NAME']),
            'for': f'county:{county}',
            'in': f'state:{state}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching income distribution: {e}")
            return pd.DataFrame()
    
    def get_housing_characteristics(self, state: str, county: str = "*", tract: str = "*") -> pd.DataFrame:
        """Get housing characteristics."""
        variables = [
            'B25001_001E',  # Total housing units
            'B25002_002E',  # Occupied housing units
            'B25002_003E',  # Vacant housing units
            'B25024_002E',  # 1 unit detached
            'B25024_003E',  # 1 unit attached
            'B25024_007E',  # 10 to 19 units
            'B25024_008E',  # 20 to 49 units
            'B25024_009E',  # 50 or more units
            'B25034_010E',  # Built 2000 to 2009
            'B25034_011E',  # Built 2010 or later
        ]
        
        url = f"{self.base_url}/{Config.CENSUS_YEAR}/acs/acs5"
        params = {
            'get': ','.join(variables + ['NAME']),
            'for': f'tract:{tract}',
            'in': f'state:{state} county:{county}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching housing data: {e}")
            return pd.DataFrame()
    
    def extract_neighborhood_from_name(self, name: str) -> str:
        """
        Extract a readable neighborhood name from Census tract name.
        
        Args:
            name: Census tract name (e.g., "Census Tract 201, San Francisco County, California")
            
        Returns:
            Simplified name
        """
        if pd.isna(name) or not name:
            return "Unknown Area"
        
        # Try to extract meaningful parts
        parts = name.split(',')
        if len(parts) >= 2:
            tract = parts[0].replace('Census Tract', 'Tract').strip()
            county = parts[1].strip().replace(' County', '')
            return f"{county} - {tract}"
        
        return name.strip()
