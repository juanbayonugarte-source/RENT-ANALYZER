"""Initialize data_collectors package."""
from .census_collector import CensusDataCollector
from .fred_collector import FREDDataCollector
from .osm_collector import OSMDataCollector
from .city_data_collector import CityDataCollector
from .zillow_collector import ZillowDataCollector
from .walkscore_collector import WalkScoreCollector

__all__ = [
    'CensusDataCollector',
    'FREDDataCollector',
    'OSMDataCollector',
    'CityDataCollector',
    'ZillowDataCollector',
    'WalkScoreCollector'
]
