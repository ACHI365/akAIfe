"""
Utility functions for station code resolution.
"""
from typing import List, Optional, Any

def resolve_station_code(user_input: str, stations: List[Any]) -> Optional[str]:
    """
    Resolves a station code from user input using fuzzy matching.
    Args:
        user_input (str): The station name or partial name provided by the user.
        stations (List[Any]): List of station objects with name attributes.
    Returns:
        Optional[str]: The resolved station code, or None if not found.
    """
    user_input = user_input.strip().lower()
    name_to_code = {}
    for s in stations:
        for n in [s.name, getattr(s, 'name_ka', None), getattr(s, 'name_en', None), getattr(s, 'name_ru', None)]:
            if n:
                name_to_code[n.strip().lower()] = s.station_code
    if user_input in name_to_code:
        return name_to_code[user_input]
    # Simple substring match
    matches = [code for name, code in name_to_code.items() if user_input in name]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # If multiple matches, prefer the shortest name
        shortest = min((name for name in name_to_code if user_input in name), key=len)
        return name_to_code[shortest]
    return None
