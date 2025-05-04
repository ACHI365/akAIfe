import ssl
import urllib.request
import urllib.parse
import json
import sys
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
import webbrowser
import http.cookiejar

from utils import resolve_station_code

mcp = FastMCP("GR Fetch")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class BaseStation(BaseModel):
    id: int
    code: str
    name: str
    cultureName: Optional[str] = None


class StationInfo(BaseModel):
    station: BaseStation
    id: int
    index: int
    arrivalDateTime: datetime
    departureDateTime: datetime
    arrivalTime: str
    departureTime: str
    arrivalTimeHour: int
    arrivalTimeMinute: int
    departureTimeHour: int
    departureTimeMinute: int
    isStandingStation: bool
    standingTime: int
    dayNumber: int


class RouteType(BaseModel):
    id: int
    code: str
    name: str
    cultureName: Optional[str] = None


class Price(BaseModel):
    amount: float
    currencyCode: str


class SeatClass(BaseModel):
    id: int
    guid: str
    index: int
    code: str
    name: str
    icon: Optional[str] = None
    color: Optional[str]
    isActive: bool
    isNumerised: bool


class AvailableSeatsClass(BaseModel):
    seatClass: SeatClass
    availableNumberOfSeats: int
    priceOfSeats: Price
    carriageModel: Optional[Any]
    carriageRang: Optional[Any]
    carriageType: Optional[Any]
    seatGroupProperty: Optional[Any]
    priceOfSeatsCash: Optional[Any]


class Ride(BaseModel):
    id: int
    guid: str
    directionId: int
    selectionTypeId: int
    saleFlag: bool
    rideNumber: int
    rideStartDate: datetime
    rideEndDate: datetime
    startDate: datetime
    endDate: datetime
    routeType: RouteType
    rideStartStation: StationInfo
    rideEndStation: StationInfo
    previousStation: Optional[StationInfo]
    actualStation: StationInfo
    startStation: StationInfo
    endStation: StationInfo
    availableSeatsClasses: List[AvailableSeatsClass]
    availableSeatsGroups: List[Any]


class Station(BaseModel):
    id: int
    station_id: str
    priority: Optional[int] = None
    station_code: str
    station_country: str
    station_country_id: str
    name: str
    name_ka: str
    name_en: str
    name_ru: str
    hide: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class StationsResponse(BaseModel):
    stations: List[Station]


@mcp.tool(name="Railway_Stations")
def get_stations() -> StationsResponse:
    url = "https://gr.com.ge/api/ticket-search"

    ctx = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(url, context=ctx, timeout=10) as resp:
            if resp.status != 200:
                raise ValueError(f"HTTP {resp.status}")
            data = json.load(resp)
        return StationsResponse(**data)

    except Exception as e:
        print(f"[gr_fetch] Error fetching stations: {e!r}", file=sys.stderr)
        raise


@mcp.resource(uri="resource://current_time", name="Current Time", mime_type="text/plain")
def get_current_time() -> str:
    """Returns server's current ISO-formatted time"""
    return datetime.now().isoformat()

@mcp.tool(name="Plan_Journey")
def plan_journey(origin: str, destination: str, when: str) -> Dict[str, Any]:
    """
    Plans a trip from origin to destination given a date phrase (e.g., "in a week").
    Returns available rides and a purchase URL.
    """
    # 1) Resolve date phrase
    now = datetime.now()
    phrase = when.strip().lower()
    # Exact YYYY-MM-DD
    m = re.match(r"^(\d{4}-\d{2}-\d{2})$", phrase)
    if phrase == "today":
        target_date = now
    elif phrase == "tomorrow":
        target_date = now + timedelta(days=1)
    elif phrase.startswith("in "):
        parts = phrase.split()
        try:
            num = int(parts[1])
            unit = parts[2].rstrip('s')
        except Exception:
            raise ValueError(f"Unsupported date phrase: '{when}'")
        if unit == "day":
            target_date = now + timedelta(days=num)
        elif unit == "week":
            target_date = now + timedelta(weeks=num)
        else:
            raise ValueError(
                f"Unsupported time unit: '{unit}' in phrase '{when}'")
    elif m:
        target_date = datetime.strptime(m.group(1), "%Y-%m-%d")
    else:
        raise ValueError(f"Could not parse date phrase: '{when}'")
    date_str = target_date.date().isoformat()

    # 2) Map station names to codes using fuzzy matching
    stations_data = get_stations()
    orig_code = resolve_station_code(origin, stations_data.stations)
    dest_code = resolve_station_code(destination, stations_data.stations)
    if not orig_code or not dest_code:
        raise ValueError("Origin or destination station not found")

    # 3) Query availability
    payload = {
        "child_passengers": 0,
        "disabled_passengers": 0,
        "standard_passengers": 1,
        "departureDateFrom": date_str,
        "startStationCode": orig_code,
        "endStationCode": dest_code,
        "routeType": 0
    }
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(
        "https://gr.com.ge/api/ticket-search",
        data=data,
        headers=headers,
        method="POST"
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        if resp.status >= 300:
            raise ValueError(f"HTTP {resp.status}")
        results = json.load(resp)

    if results and isinstance(results[0], list):
        rides_data = [item for sublist in results for item in sublist]
    else:
        rides_data = results

    if isinstance(rides_data, dict) and 'rides' in rides_data:
        rides_data = rides_data['rides']

    rides = [Ride(**r) for r in rides_data]

    params = {
        "startStationCode": orig_code,
        "endStationCode": dest_code,
        "departureDateFrom": date_str,
        **{k: payload[k] for k in ["standard_passengers", "child_passengers", "disabled_passengers"]}
    }
    purchase_url = f"https://gr.com.ge/en/search?{urllib.parse.urlencode(params)}"

    return {
        "date": date_str,
        "origin": origin,
        "destination": destination,
        "rides": [r.model_dump() for r in rides],
        "purchase_url": purchase_url
    }
@mcp.tool(name="List_Rental_Locations")
def list_rental_locations() -> list[dict]:
    """
    Fetches all available rental-location IDs and names from MyAuto.ge.

    Args: None

    Returns:
        List[Dict]: A list of location objects, each containing:
            - id (int): Location ID
            - name (str): Human-readable location name
            - parent_loc_id (int): Parent location ID, if any
            - ...any other fields the API provides
    """
    # Prepare SSL context
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Build a cookie-aware opener with browser headers
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj)
    )
    opener.addheaders = [
        ("User-Agent",       "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
        ("Accept",           "application/json, text/plain, */*"),
        ("Accept-Language",  "en-US,en;q=0.9"),
        ("Referer",          "https://www.myauto.ge/"),
        ("Origin",           "https://www.myauto.ge"),
        ("X-Requested-With", "XMLHttpRequest"),
    ]

    # Seed cookies by "visiting" the main site
    opener.open("https://www.myauto.ge/ka")

    # Now fetch the rental locations
    url = "https://api2.myauto.ge/ka/vehicle/locations"
    req = urllib.request.Request(url)  # headers already on opener
    with opener.open(req, timeout=10) as resp:
        if resp.status != 200:
            raise ValueError(f"HTTP {resp.status}")
        return json.load(resp)


@mcp.tool(name="Search_Rental_Cars")
def search_rental_cars(
    price_from: Optional[int] = None,
    price_to: Optional[int] = None,
    currency_id: int = 1,
    gear_types: str = "1.2",
    locs: int = 2,
    wheel_types: Optional[int] = None
) -> List[Dict]:
    """
    Fetch up to five of the best rental-car listings matching the given filters.

    Args:
        price_from (int, optional): Minimum daily price. If omitted, no lower bound is applied.
        price_to (int, optional): Maximum daily price. If omitted, no upper bound is applied.
        currency_id (int): Currency to use for pricing:
            - 1 = USD
            - 3 = GEL
        gear_types (str): Gearbox types to include, as dot-separated IDs:
            - "1" = manual
            - "2" = automatic
          e.g. "1.2" means both manual and automatic.
        locs (int, optional): Location ID for pickup. To find valid IDs, call `cars://locations` first.
        wheel_types (int, optional): Steering-wheel side:
            - 0 = left
            - 1 = right

    Returns:
        List[Dict]: Up to five cars with the lowest USD price. Each dictionary contains:
            - car_id (int): Internal ID of the car.
            - model (str): Model code/name.
            - year (int): Production year.
            - price_usd (float): Price in USD.
            - views (int): Total view count (as a proxy for popularity).
            - link (str): Public URL to the listing (e.g. https://www.myauto.ge/ka/pr/{car_id}).
    """
    # -- prepare SSL & cookie-aware opener to mimic a real browser session --
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj)
    )
    opener.addheaders = [
        ("User-Agent",       "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
        ("Accept",           "application/json, text/plain, */*"),
        ("Accept-Language",  "en-US,en;q=0.9"),
        ("Referer",          "https://www.myauto.ge/"),
        ("Origin",           "https://www.myauto.ge"),
        ("X-Requested-With", "XMLHttpRequest"),
    ]
    opener.open("https://www.myauto.ge/ka")  # seed cookies

    base_url = "https://api2.myauto.ge/ka/products"
    params = {
        "TypeID":      0,
        "ForRent":     1,
        "CurrencyID":  currency_id,
        "MileageType": 1,
        "GearTypes":   gear_types
    }
    if price_from is not None:
        params["PriceFrom"] = price_from
    if price_to is not None:
        params["PriceTo"] = price_to
    if locs is not None:
        params["Locs"] = locs
    if wheel_types is not None:
        params["WheelTypes"] = wheel_types

    all_cars = []
    page = 1

    # Page through until empty result
    while page < 5:
        params["Page"] = page
        qs = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{base_url}?{qs}")
        with opener.open(req) as resp:
            data = json.load(resp)
            page_items = data.get("data", {}).get("items", [])
        if not data:
            break
        all_cars.extend(page_items)
        page += 1

    # Sort by USD price and take the top five
    top_five = sorted(all_cars, key=lambda c: c.get("price_usd", float("inf")))[:5]

    # Slim down output and add public links
    results = []
    for car in top_five:
        cid = car["car_id"]
        results.append({
            "car_id":    cid,
            "model":     car.get("car_model"),
            "year":      car.get("prod_year"),
            "price_usd": car.get("price_usd"),
            "views":     car.get("views"),
            "link":      f"https://www.myauto.ge/ka/pr/{cid}"
        })

    return results

@mcp.tool(name="Open_URL_in_Browser")
def open_url_in_browser(url: str) -> str:
    """
    Opens the given URL in the default web browser in the background.
    """
    try:
        webbrowser.open(url, new=2)
        return f"Opened {url} in the browser."
    except Exception as e:
        return f"Failed to open {url}: {e}"


if __name__ == "__main__":
    print(search_rental_cars(locs=4))
