import os
import json
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data_store')
BOUNDARIES_DIR = os.path.join(DATA_DIR, 'boundaries')
CANALS_DIR = os.path.join(DATA_DIR, 'canals')
HAZARDS_DIR = os.path.join(DATA_DIR, 'hazards')

# Ensure dirs exist
os.makedirs(BOUNDARIES_DIR, exist_ok=True)
os.makedirs(CANALS_DIR, exist_ok=True)
os.makedirs(HAZARDS_DIR, exist_ok=True)

def save_geojson(gdf, filename):
    path = filename # Filename includes dir
    gdf.to_file(path, driver='GeoJSON')
    print(f"Created {path}")

def generate_data():
    # 1. Kochi Boundary (Approximate Box around Kochi City)
    # Lat: 9.9 to 10.05, Lon: 76.2 to 76.35
    kochi_poly = Polygon([
        (76.2, 9.9), (76.35, 9.9), (76.35, 10.05), (76.2, 10.05), (76.2, 9.9)
    ])
    kochi_gdf = gpd.GeoDataFrame({'name': ['Kochi Corporation']}, geometry=[kochi_poly], crs="EPSG:4326")
    save_geojson(kochi_gdf, os.path.join(BOUNDARIES_DIR, 'kochi_corporation.geojson'))

    # 2. Wards (Split the box into 4 for demo)
    wards = []
    names = []
    # Ward 1
    wards.append(Polygon([(76.2, 9.9), (76.27, 9.9), (76.27, 9.97), (76.2, 9.97), (76.2, 9.9)]))
    names.append("Fort Kochi")
    # Ward 2
    wards.append(Polygon([(76.27, 9.9), (76.35, 9.9), (76.35, 9.97), (76.27, 9.97), (76.27, 9.9)]))
    names.append("Ernakulam Central")
    
    wards_gdf = gpd.GeoDataFrame({'ward_name': names}, geometry=wards, crs="EPSG:4326")
    save_geojson(wards_gdf, os.path.join(BOUNDARIES_DIR, 'kochi_wards.geojson'))

    # 3. Flood Zones (A small area in the center)
    flood_poly = Polygon([
        (76.25, 9.95), (76.30, 9.95), (76.30, 9.98), (76.25, 9.98), (76.25, 9.95)
    ])
    flood_gdf = gpd.GeoDataFrame({'hazard_level': ['High Flood Risk']}, geometry=[flood_poly], crs="EPSG:4326")
    save_geojson(flood_gdf, os.path.join(HAZARDS_DIR, 'flood_zones.geojson'))

    # 4. TP Canal (Line)
    # Running through the city
    tp_canal = LineString([(76.28, 9.94), (76.29, 9.96), (76.30, 9.98)])
    canals_gdf = gpd.GeoDataFrame({'name': ['TP Canal']}, geometry=[tp_canal], crs="EPSG:4326")
    save_geojson(canals_gdf, os.path.join(CANALS_DIR, 'canals.geojson'))

    # 5. Industrial Zones (Eloor Area - approx North)
    eloor_poly = Polygon([
        (76.28, 10.02), (76.32, 10.02), (76.32, 10.04), (76.28, 10.04), (76.28, 10.02)
    ])
    ind_gdf = gpd.GeoDataFrame({'name': ['Eloor Industrial Cluster'], 'category': ['Red']}, geometry=[eloor_poly], crs="EPSG:4326")
    save_geojson(ind_gdf, os.path.join(HAZARDS_DIR, 'industrial_risk_zones.geojson'))
    
    # 6. Groundwater
    gw_poly = kochi_poly # Whole city safe
    gw_gdf = gpd.GeoDataFrame({'category': ['Safe']}, geometry=[gw_poly], crs="EPSG:4326")
    save_geojson(gw_gdf, os.path.join(HAZARDS_DIR, 'groundwater.geojson'))

    # 7. Coastal (West side strip)
    coast_line = LineString([(76.2, 9.9), (76.2, 10.05)])
    coast_gdf = gpd.GeoDataFrame({'name': ['Coastline']}, geometry=[coast_line], crs="EPSG:4326")
    save_geojson(coast_gdf, os.path.join(HAZARDS_DIR, 'coastal_hazard_zones.geojson'))

if __name__ == "__main__":
    generate_data()
