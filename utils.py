def resolve_station_code(user_input, stations):
    user_input = user_input.strip().lower()
    name_to_code = {}
    for s in stations:
        for n in [s.name, s.name_ka, s.name_en, s.name_ru]:
            if n:
                name_to_code[n.strip().lower()] = s.station_code
    if user_input in name_to_code:
        return name_to_code[user_input]
    # Simple substring match
    matches = [code for name, code in name_to_code.items()
               if user_input in name]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # If multiple matches, prefer the shortest name
        shortest = min(
            (name for name in name_to_code if user_input in name), key=len)
        return name_to_code[shortest]
    return None
