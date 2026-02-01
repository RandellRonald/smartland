from shapely.geometry import Point
import geopandas as gpd
import backend.loader as loader
from backend.models.response_models import RiskTag, Explanation

TP_CANAL_THRESHOLD_METERS = 300
GENERAL_CANAL_THRESHOLD_METERS = 100

def analyze_flood_risk(point: Point):
    tags = []
    explanations = []

    # 1. Flood Hazard Zone Intersection
    in_flood_zone = False
    zone_name = "Unknown"
    
    if not loader.flood_zones_gdf.empty:
        # Check intersection
        hits = loader.flood_zones_gdf[loader.flood_zones_gdf.contains(point)]
        if not hits.empty:
            in_flood_zone = True
            # Assuming 'hazard_level' or 'name' exists
            if 'hazard_level' in hits.columns:
                zone_name = hits.iloc[0]['hazard_level']
    
    if in_flood_zone:
        tags.append(RiskTag(
            category="Flood",
            risk_level="HIGH",
            description="Located within a mapped Flood Hazard Zone."
        ))
        explanations.append(Explanation(
            category="Flood Susceptibility",
            text=[f"The location intersects with a known flood hazard polygon ({zone_name})."],
            source="KSDMA Hazard Map / Irrigation Dept.",
            year="2019"
        ))

    # 2. Canal Proximity
    if not loader.canals_gdf.empty:
        # Calculate distance to nearest canal
        # Project to a local CRS (e.g. EPSG:32643 - UTM Zone 43N) for accurate distance in meters
        # But for simplicity/speed without heavy dependencies, we might estimate or use a simple distance check if data is already projected.
        # Ideally: point_proj = point in meters, gdf_proj = gdf in meters.
        
        # We will use a crude approximation if CRS is 4326: 1 deg ~ 111km. 
        # Better: use project. 
        # But let's assume we can do a quick check if global 'canals_gdf' is 4326.
        # We should accept that distance() on 4326 returns degrees.
        
        # To be accurate:
        # point_meters = gpd.GeoSeries([point], crs="EPSG:4326").to_crs("EPSG:32643").iloc[0]
        # canals_meters = canals_gdf.to_crs("EPSG:32643")
        # distances = canals_meters.distance(point_meters)
        # min_dist = distances.min()
        
        try:
            point_series = gpd.GeoSeries([point], crs="EPSG:4326").to_crs(epsg=32643)
            canals_proj = loader.canals_gdf.to_crs(epsg=32643)
            
            distances = canals_proj.distance(point_series.iloc[0])
            min_dist = distances.min()
            
            nearest_idx = distances.idxmin()
            nearest_canal_name = canals_proj.iloc[nearest_idx].get('name', 'Unnamed Canal')
            
            if min_dist < TP_CANAL_THRESHOLD_METERS and "TP Canal" in str(nearest_canal_name):
                 tags.append(RiskTag(
                    category="Flood",
                    risk_level="HIGH",
                    description=f"Critical proximity ({int(min_dist)}m) to TP Canal."
                ))
                 explanations.append(Explanation(
                    category="Canal Proximity",
                    text=[f"Location is {int(min_dist)}m from {nearest_canal_name}, which is a major drainage channel."],
                    source="Irrigation Department",
                    year="2020"
                ))
            elif min_dist < GENERAL_CANAL_THRESHOLD_METERS:
                 tags.append(RiskTag(
                    category="Flood",
                    risk_level="MODERATE",
                    description=f"Proximity ({int(min_dist)}m) to drainage canal."
                ))
                 explanations.append(Explanation(
                    category="Canal Proximity",
                    text=[f"Location is {int(min_dist)}m from local canal network."],
                    source="Kochi Corporation Drainage Map",
                    year="2021"
                ))

        except Exception as e:
            print(f"Error in canal distance calc: {e}")

    return tags, explanations
