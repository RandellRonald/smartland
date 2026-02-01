from shapely.geometry import Point
import geopandas as gpd
import backend.loader as loader
from backend.models.response_models import RiskTag, Explanation

# Groundwater
def analyze_groundwater_risk(point: Point):
    tags = []
    explanations = []
    status = "Safe" # Default for Ernakulam as per research
    
    if not loader.groundwater_gdf.empty:
         hits = loader.groundwater_gdf[loader.groundwater_gdf.contains(point)]
         if not hits.empty:
             if 'category' in hits.columns:
                 status = hits.iloc[0]['category']
    
    tags.append(RiskTag(
        category="Groundwater",
        risk_level="LOW" if status == "Safe" else "MODERATE",
        description=f"Block status: {status}"
    ))
    explanations.append(Explanation(
        category="Groundwater Availability",
        text=[f"Located in a {status} assessment block."],
        source="CGWB Dynamic Groundwater Resources",
        year="2022"
    ))
    return tags, explanations

# Seismic
def analyze_seismic_risk(point: Point):
    # Static for Kochi
    return [
        RiskTag(category="Seismic", risk_level="MODERATE", description="Zone III (Moderate Damage Risk)")
    ], [
        Explanation(
            category="Structure",
            text=["Kochi falls under Seismic Zone III.", "IS 1893:2016 standards apply."],
            source="Bureau of Indian Standards",
            year="2016"
        )
    ]

# Coastal
def analyze_coastal_risk(point: Point):
    tags = []
    explanations = []
    
    if not loader.coastal_gdf.empty:
        # Simple distance check to coastline
        try:
             # Reproject for meters
            point_series = gpd.GeoSeries([point], crs="EPSG:4326").to_crs(epsg=32643)
            coast_proj = loader.coastal_gdf.to_crs(epsg=32643)
            dist = coast_proj.distance(point_series.iloc[0]).min()
            
            if dist < 500: # 500m coastal regulation zone approx
                 tags.append(RiskTag(category="Coastal", risk_level="MODERATE", description="Within Coastal Regulation Zone influence."))
                 explanations.append(Explanation(category="Coastal Hazard", text=[f"Distance to coast: {int(dist)}m"], source="KCZMA", year="2019"))
        except:
            pass
            
    return tags, explanations

# Climate
def analyze_climate_context(point: Point):
    return [], [
        Explanation(
            category="Climate Context",
            text=["Decadal trend shows increasing rainfall intensity.", "Temp anomaly +0.6C observed."],
            source="IMD Gridded Data",
            year="2023"
        )
    ]
