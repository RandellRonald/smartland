from shapely.geometry import Point
import geopandas as gpd
import backend.loader as loader
from backend.models.response_models import RiskTag, Explanation

INDUSTRIAL_BUFFER_METERS = 500

def analyze_pollution_risk(point: Point):
    tags = []
    explanations = []

    # 1. Industrial Cluster Proximity
    if not loader.industrial_zones_gdf.empty:
        try:
            point_series = gpd.GeoSeries([point], crs="EPSG:4326").to_crs(epsg=32643)
            inds_proj = loader.industrial_zones_gdf.to_crs(epsg=32643)
            
            distances = inds_proj.distance(point_series.iloc[0])
            min_dist = distances.min()
            
            if min_dist < INDUSTRIAL_BUFFER_METERS:
                nearest_idx = distances.idxmin()
                cluster_name = inds_proj.iloc[nearest_idx].get('name', 'Industrial Cluster')
                category = inds_proj.iloc[nearest_idx].get('category', 'Red')

                tags.append(RiskTag(
                    category="Industrial",
                    risk_level="MODERATE" if category == "Orange" else "HIGH",
                    description=f"Within {int(min_dist)}m of {cluster_name}."
                ))
                explanations.append(Explanation(
                    category="Industrial Proximity",
                    text=[
                        f"Location is near {cluster_name}.",
                        f"Pollution Category: {category} (Air/Water emissions likely)."
                    ],
                    source="KSPCB / Industrial Estate Map",
                    year="2023"
                ))
        except Exception as e:
            print(f"Error in pollution calc: {e}")
            
    # 2. General District Tag (Always present as per prompt instructions for Industrial Risk)
    # The prompt says: "Also: Add district-level industrial accident susceptibility tag."
    explanations.append(Explanation(
        category="Regional Industrial Context",
        text=["Ernakulam district contains Major Accident Hazard (MAH) units."],
        source="Department of Factories & Boilers",
        year="2022"
    ))

    return tags, explanations
