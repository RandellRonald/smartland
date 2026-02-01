from shapely.geometry import Point
from shapely.geometry import Point
import backend.loader as loader

def check_boundary_context(point: Point):
    """
    Checks if the point is within the Kochi service area.
    Returns:
        is_inside (bool): True if inside supported area.
        ward_info (str/None): Name of the ward if found.
    """
    # 1. Check Service Area (Kochi Corporation)
    # If the boundary GDF is empty (missing data), we might default to True or False.
    # For this strict implementation, if data is missing, it's effectively "outside" or broken.
    # However, to allow the app to run without data initially, we might need a fail-safe.
    
    is_inside = False
    
    if not loader.kochi_boundary_gdf.empty:
        # Check if point intersects any polygon in the boundary file
        is_inside = loader.kochi_boundary_gdf.contains(point).any()
    else:
        # Fallback for demo if no data exists yet: 
        # Assume valid for demo purposes or strictly reject? 
        # The prompt says validation "Status: out_of_service_area" if outside.
        # But if data is missing, we can't validate. We will assume False.
        pass

    # 2. Identify Ward
    ward_name = None
    if not loader.ward_boundary_gdf.empty:
        # Find which ward contains the point
        containing_wards = loader.ward_boundary_gdf[loader.ward_boundary_gdf.contains(point)]
        if not containing_wards.empty:
            # Assuming 'ward_name' or 'name' column exists
            columns = containing_wards.columns
            if 'ward_name' in columns:
                ward_name = containing_wards.iloc[0]['ward_name']
            elif 'name' in columns:
                ward_name = containing_wards.iloc[0]['name']
            else:
                ward_name = "Unknown Ward"

    return is_inside, ward_name
