import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

def search_places_nearby(
    location: tuple[float, float],
    radius: int = 1000,
    place_types: list[str] = None,
    max_results: int = 10
) -> list[dict]:
    if place_types is None:
        place_types = [
            'restaurant', 'bar', 'cafe',
            'entertainment', 'shopping_mall', 'park'
        ]

    results: list[dict] = []
    for place_type in place_types:
        response = gmaps.places_nearby(
            location=location,
            radius=radius,
            type=place_type
        )
        for place in response.get("results", []):
            results.append(place)
            if len(results) >= max_results:
                # as soon as we hit the cap, return
                return results

    # if fewer than max_results were found across all types
    return results
