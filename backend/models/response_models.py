from pydantic import BaseModel
from typing import List, Optional, Dict

class LocationInfo(BaseModel):
    latitude: float
    longitude: float
    ward: Optional[str] = None
    district: str = "Ernakulam"
    state: str = "Kerala"

class RiskTag(BaseModel):
    category: str  # e.g., "Flood", "Industrial", "Seismic"
    risk_level: str  # "HIGH", "MODERATE", "LOW", "SAFE", "INFO"
    description: str

class Explanation(BaseModel):
    category: str
    text: List[str]
    source: str
    year: str

class AnalysisResponse(BaseModel):
    location: LocationInfo
    risk_tags: List[RiskTag]
    explanations: List[Explanation]
    data_sources: List[str]

class ErrorResponse(BaseModel):
    status: str
    message: str
    supported_region_info: Optional[str] = None
