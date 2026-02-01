import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

# Data Store Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data_store')

BOUNDARIES_DIR = os.path.join(DATA_DIR, 'boundaries')
CANALS_DIR = os.path.join(DATA_DIR, 'canals')
HAZARDS_DIR = os.path.join(DATA_DIR, 'hazards')

# Global Data Cache
kochi_boundary_gdf = None
ward_boundary_gdf = None
flood_zones_gdf = None
canals_gdf = None
industrial_zones_gdf = None
groundwater_gdf = None
coastal_gdf = None

def load_geodataframe(path):
    """
    Helper to load a GeoJSON file. Returns an empty GDF if file not found.
    """
    if not os.path.exists(path):
        print(f"Warning: Data file not found at {path}. using empty GDF.")
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
    
    try:
        gdf = gpd.read_file(path)
        # Ensure CRS is EPSG:4326 for consistency
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        return gdf
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

def load_data():
    global kochi_boundary_gdf, ward_boundary_gdf, flood_zones_gdf, canals_gdf
    global industrial_zones_gdf, groundwater_gdf, coastal_gdf

    print("Loading datasets...")

    # 1. Boundaries
    kochi_boundary_gdf = load_geodataframe(os.path.join(BOUNDARIES_DIR, 'kochi_corporation.geojson'))
    ward_boundary_gdf = load_geodataframe(os.path.join(BOUNDARIES_DIR, 'kochi_wards.geojson'))

    # 2. Hazards
    flood_zones_gdf = load_geodataframe(os.path.join(HAZARDS_DIR, 'flood_zones.geojson'))
    
    # 3. Canals
    canals_gdf = load_geodataframe(os.path.join(CANALS_DIR, 'canals.geojson'))

    # 4. Industrial
    industrial_zones_gdf = load_geodataframe(os.path.join(HAZARDS_DIR, 'industrial_risk_zones.geojson'))

    # 5. Groundwater
    groundwater_gdf = load_geodataframe(os.path.join(DATA_DIR, 'hazards', 'groundwater.geojson')) # Assuming in hazards for simplicity or general data dir

    # 6. Coastal
    coastal_gdf = load_geodataframe(os.path.join(HAZARDS_DIR, 'coastal_hazard_zones.geojson'))

    print("Data loading complete.")

# Trigger load on module import or explicit call
# In a real app, you might want to call this explicitly in startup
