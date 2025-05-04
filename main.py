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

from utils import resolve_station_code

mcp = FastMCP("GR Fetch")


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
    print(plan_journey("Tbilisi", "Batumi", "today"))
