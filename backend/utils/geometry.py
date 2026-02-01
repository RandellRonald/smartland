from shapely.geometry import Point

def create_point(lat: float, lon: float) -> Point:
    """
    Creates a Shapely Point from latitude and longitude.
    """
    return Point(lon, lat)  # Shapely uses (x, y) -> (lon, lat)
