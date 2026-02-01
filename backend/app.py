from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.loader import load_data
from backend.utils.geometry import create_point
from backend.utils.validators import validate_coordinates
from backend.models.response_models import AnalysisResponse, ErrorResponse, LocationInfo

# Import Services
from backend.services.boundary import check_boundary_context
from backend.services.flood import analyze_flood_risk
from backend.services.pollution import analyze_pollution_risk
from backend.services.minor_risks import (
    analyze_groundwater_risk,
    analyze_seismic_risk,
    analyze_coastal_risk,
    analyze_climate_context
)

app = FastAPI(title="Kochi Environmental Risk Analyzer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

@app.on_event("startup")
async def startup_event():
    load_data()

@app.post("/analyze-location", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
async def analyze_location(request: LocationRequest):
    lat = request.latitude
    lon = request.longitude

    # 1. Basic Validation
    if not validate_coordinates(lat, lon):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")

    point = create_point(lat, lon)

    # 2. Boundary Check
    is_inside, ward_name = check_boundary_context(point)
    
    if not is_inside:
        # Return strict error as per spec
        return ErrorResponse(
            status="out_of_service_area",
            message="Location outside supported Kochi service area.",
            supported_region_info="This tool covers Kochi Municipal Corporation and immediate Ernakulam environs."
        )

    # 3. Risk Analysis
    risk_tags = []
    explanations = []
    data_sources = []

    # Flood
    f_tags, f_expl = analyze_flood_risk(point)
    risk_tags.extend(f_tags)
    explanations.extend(f_expl)

    # Pollution
    p_tags, p_expl = analyze_pollution_risk(point)
    risk_tags.extend(p_tags)
    explanations.extend(p_expl)

    # Groundwater
    g_tags, g_expl = analyze_groundwater_risk(point)
    risk_tags.extend(g_tags)
    explanations.extend(g_expl)

    # Seismic
    s_tags, s_expl = analyze_seismic_risk(point)
    risk_tags.extend(s_tags)
    explanations.extend(s_expl)

    # Coastal
    c_tags, c_expl = analyze_coastal_risk(point)
    risk_tags.extend(c_tags)
    explanations.extend(c_expl)

    # Climate
    _, cl_expl = analyze_climate_context(point)
    explanations.extend(cl_expl)

    # Collect Sources
    data_sources = [e.source for e in explanations]

    return AnalysisResponse(
        location=LocationInfo(
            latitude=lat,
            longitude=lon,
            ward=ward_name
        ),
        risk_tags=risk_tags,
        explanations=explanations,
        data_sources=list(set(data_sources))
    )

from backend.services.infrastructure_context import analyze_infrastructure, assess_overall_constraints

@app.get("/infrastructure-context")
async def get_infrastructure_context(lat: float, lon: float):
    # 1. Validate (duplicate validation but necessary for standalone endpoint correctness)
    if not validate_coordinates(lat, lon):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
        
    point = create_point(lat, lon)
    
    # 2. Get basic context
    is_inside, ward_name = check_boundary_context(point)
    
    # 3. Get Infrastructure Context
    infra_data = analyze_infrastructure(point, ward_name, is_inside)
    
    # 4. Assessment
    assessment = assess_overall_constraints(point, infra_data)
    
    # Combine results
    # We return a flat dictionary with both parts
    return {
        **infra_data,
        "overall_assessment": assessment
    }
