from shapely.geometry import Point

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Basic sanity check for coordinates.
    """
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lon <= 180):
        return False
    return True
