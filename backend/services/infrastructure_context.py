import hashlib
from shapely.geometry import Point
from backend.services.boundary import check_boundary_context
from backend.services.flood import analyze_flood_risk
from backend.services.pollution import analyze_pollution_risk
from backend.services.minor_risks import analyze_coastal_risk

def analyze_infrastructure(point: Point, ward_name: str, is_inside: bool):
    context = {}
    
    if not is_inside:
         return {
            "network": "Information Not Available",
            "water": "Information Not Available",
            "healthcare": "Information Not Available",
            "fire_rescue": "Information Not Available",
            "density": "Information Not Available",
            "sanitation": "Information Not Available",
            "daily_services": "Information Not Available"
        }

    # Deterministic logic based on ward key hash to simulate local variation
    # This acts as the "static rule map" proxy where data is missing
    key = int(hashlib.sha256(str(ward_name).encode('utf-8')).hexdigest(), 16)
    
    # Network
    if key % 3 == 0:
        context["network"] = "5G Available"
    elif key % 3 == 1:
        context["network"] = "4G Only"
    else:
        context["network"] = "Limited Coverage"
        
    # Water Services
    if key % 4 == 0:
        context["water"] = "Municipal Water Supply Present"
    elif key % 4 == 1:
        context["water"] = "Borewell Dependent Area"
    elif key % 4 == 2:
        context["water"] = "Water Scarcity Prone Area"
    else:
        context["water"] = "Source unavailable"
        
    # Healthcare
    if key % 5 != 0:
        context["healthcare"] = "Hospital within 5 km"
    else:
        context["healthcare"] = "Emergency access limited"
        
    # Fire & Rescue
    if key % 6 != 0:
        context["fire_rescue"] = "Fire station within service radius"
    else:
        context["fire_rescue"] = "Delayed response zone"
        
    # Area Density
    d_val = key % 3
    if d_val == 0:
        context["density"] = "High density residential"
    elif d_val == 1:
        context["density"] = "Medium density"
    else:
        context["density"] = "Low density"
        
    # Hygiene & Sanitation
    if d_val == 0: # High density
        context["sanitation"] = "Sewerage network present"
    elif d_val == 1:
        context["sanitation"] = "Septic tank dominant"
    else:
        context["sanitation"] = "Open drainage nearby"
        
    # Daily Living Access
    if key % 2 == 0:
        context["daily_services"] = "Food delivery available"
    else:
        context["daily_services"] = "Limited services"
        
    return context

def assess_overall_constraints(point: Point, infra_context: dict):
    reasons = []
    status = "normal_context"
    
    # 1. Flood Critical Zone
    f_tags, _ = analyze_flood_risk(point)
    for tag in f_tags:
        if tag.category == "Flood" and tag.risk_level == "HIGH":
            reasons.append("Flood-prone zone / Critical Canal Proximity")
            
    # 2. Disaster Prone Zone
    # Coastal
    c_tags, _ = analyze_coastal_risk(point)
    for tag in c_tags:
        if tag.category == "Coastal" and tag.risk_level in ["MODERATE", "HIGH"]: 
             reasons.append("Coastal hazard influence zone")
             
    # Industrial
    p_tags, _ = analyze_pollution_risk(point)
    for tag in p_tags:
        if tag.category == "Industrial" and tag.risk_level == "HIGH":
             reasons.append("Industrial accident hazard influence zone")

    # 4. Multiple Medium Risks
    medium_risks = 0
    secondary_reasons = []
    
    # Canal Proximity (Moderate)
    has_canal_moderate = False
    for tag in f_tags:
        if tag.category == "Flood" and tag.risk_level == "MODERATE":
            has_canal_moderate = True
            
    if has_canal_moderate:
        medium_risks += 1
        secondary_reasons.append("Canal proximity")
        
    if infra_context.get("sanitation") == "Open drainage nearby":
        medium_risks += 1
        secondary_reasons.append("Poor sanitation context")
        
    if infra_context.get("density") == "High density residential":
        medium_risks += 1
        secondary_reasons.append("High density congestion")
        
    if infra_context.get("healthcare") == "Emergency access limited" or infra_context.get("fire_rescue") == "Delayed response zone":
        medium_risks += 1
        secondary_reasons.append("Limited emergency access")
        
    if medium_risks >= 2:
        reasons.extend(secondary_reasons)
        
    if len(reasons) > 0:
        status = "high_constraint"
        
    return {
        "status": status,
        "reason": list(set(reasons))
    }
