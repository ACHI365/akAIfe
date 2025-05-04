import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

def search_places_nearby(location: tuple[float, float], radius: int = 1000, place_types: list[str] = None):
    if place_types is None:
        place_types = ['restaurant', 'bar', 'cafe', 'entertainment', 'shopping_mall', 'park']

    results = []
    for place_type in place_types:
        response = gmaps.places_nearby(
            location=location,
            radius=radius,
            type=place_type
        )
        results.extend(response.get("results", []))
    
    return results