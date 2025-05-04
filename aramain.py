# aramain.py - Full Script Modified to Run Server Directly

import ssl
import urllib.request
import urllib.parse
import json
import sys
import re
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    model_validator,
    ValidationError,
)
from mcp.server.fastmcp import FastMCP
import webbrowser
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
print("Attempted to load variables from .env file.", file=sys.stderr)

# --- Configuration ---
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

print(f"Read MONGODB_URI: {'Set' if MONGODB_URI else 'Not Set'}", file=sys.stderr)
print(f"Read MONGODB_DATABASE: {MONGODB_DATABASE}", file=sys.stderr)
print(f"Read MONGODB_COLLECTION: {MONGODB_COLLECTION}", file=sys.stderr)

if not MONGODB_URI:
    print("CRITICAL ERROR: MONGODB_URI environment variable not set.", file=sys.stderr)
    sys.exit(1)
if not MONGODB_DATABASE:
    print("CRITICAL ERROR: MONGODB_DATABASE environment variable not set.", file=sys.stderr)
    sys.exit(1)
if not MONGODB_COLLECTION:
    print("CRITICAL ERROR: MONGODB_COLLECTION environment variable not set.", file=sys.stderr)
    sys.exit(1)

# --- Database Connection ---
mongo_client = None
db = None
sightseeing_collection = None
try:
    print("Attempting to connect to MongoDB Atlas...", file=sys.stderr)
    mongo_client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        appName="MCPSightseeingGuide",
    )
    mongo_client.admin.command("ismaster")
    print(
        f"Successfully connected to MongoDB Atlas. Database: '{MONGODB_DATABASE}', Collection: '{MONGODB_COLLECTION}'", file=sys.stderr
    )
    db = mongo_client[MONGODB_DATABASE]
    sightseeing_collection = db[MONGODB_COLLECTION]

    # --- Verify the text index exists ---
    try:
        print("Verifying index information...", file=sys.stderr)
        index_info = sightseeing_collection.index_information()
        # print(f"Raw index info from pymongo: {index_info}", file=sys.stderr) # Optional debug

        text_index_exists = False
        required_text_fields = {"Attraction Name", "Description"}
        for idx_name, idx_data in index_info.items():
            # print(f"Checking index: Name='{idx_name}', Data={idx_data}", file=sys.stderr) # Optional debug
            if "weights" in idx_data and isinstance(idx_data.get("weights"), dict):
                indexed_fields_in_weights = set(idx_data["weights"].keys())
                if required_text_fields.issubset(indexed_fields_in_weights):
                    text_index_exists = True
                    print(
                        f"CONFIRMED: Text index '{idx_name}' covers required fields via weights.", file=sys.stderr
                    )
                    break

        if not text_index_exists:
            print("CRITICAL WARNING: Did not find a suitable MongoDB text index...", file=sys.stderr) # Shortened warning
            # ... (rest of original warning messages if desired) ...
        else:
            print("Text index check passed.", file=sys.stderr)

    except OperationFailure as idx_err:
        print(f"Warning: Could not verify MongoDB index information: {idx_err}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: An unexpected error occurred during index verification: {e!r}", file=sys.stderr)

except ConnectionFailure as e:
    print(f"CRITICAL ERROR: Failed to connect to MongoDB Atlas: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"CRITICAL ERROR: An unexpected error occurred during MongoDB setup: {e!r}", file=sys.stderr)
    sys.exit(1)


# --- MCP Initialization ---
mcp = FastMCP("Georgian_Sightseeing_Finder_Service")


# --- Pydantic Models for Sightseeing Data ---
class SightseeingSpot(BaseModel):
    """Represents a single sightseeing spot retrieved from the database."""
    id: str = Field(..., alias="_id")
    attraction_name: str = Field(..., alias="Attraction Name")
    image_url: Optional[str] = Field(None, alias="Image URL")
    description: Optional[str] = Field(None, alias="Description")
    location_info_str: Optional[str] = Field(None, alias="Location Info")
    page_url: Optional[str] = Field(None, alias="Page URL")
    category_url: Optional[str] = Field(None, alias="Category URL")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[str] = None
    category: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def parse_coordinates_from_location_info(cls, data: Any) -> Any:
        if isinstance(data, dict):
            location_str = data.get("Location Info")
            if isinstance(location_str, str):
                lat_match = re.search(r"lat=([+-]?\d+\.?\d*)", location_str, re.IGNORECASE)
                lng_match = re.search(r"lng=([+-]?\d+\.?\d*)", location_str, re.IGNORECASE)
                if lat_match and lng_match:
                    try:
                        data["latitude"] = float(lat_match.group(1))
                        data["longitude"] = float(lng_match.group(1))
                    except (ValueError, IndexError):
                        print(f"Warning: Could not parse floats from location info: '{location_str}' for doc _id={data.get('_id', 'N/A')}", file=sys.stderr)
        return data

    @computed_field
    @property
    def google_maps_url(self) -> Optional[str]:
        if self.latitude is not None and self.longitude is not None:
            if -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180:
                query_params = urllib.parse.urlencode({"q": f"{self.latitude},{self.longitude}"})
                return f"https://www.google.com/maps?{query_params}"
        return None

    class Config:
        populate_by_name = True
        from_attributes = True
        # extra = 'ignore'


class SightseeingListResponse(BaseModel):
    """Response structure containing a list of sightseeing spots."""
    count: int
    sightseeings: List[SightseeingSpot]


# --- MCP Tool for Sightseeing Search ---
@mcp.tool(name="Find_Sightseeings_By_Description")
def find_sightseeings_by_description(
    query_description: str, limit: int = 1
) -> SightseeingListResponse:
    """
    Finds Georgian sightseeing spots matching a user's descriptive query... (rest of docstring)
    """
    if mongo_client is None or sightseeing_collection is None:
        print("ERROR in Find_Sightseeings: Database connection object is None.", file=sys.stderr)
        raise ValueError("Database connection is not available.")
    if not query_description or not query_description.strip():
        raise ValueError("Query description cannot be empty.")

    query_filter = {"$text": {"$search": query_description.strip()}}
    print(f"Executing MongoDB Text Search for: \"{query_description.strip()}\"", file=sys.stderr)
    print(f"Query Filter: {query_filter}", file=sys.stderr)

    try:
        mongo_docs_cursor = sightseeing_collection.find(query_filter).limit(limit)
        spots = []
        processed_ids = set()
        for doc in mongo_docs_cursor:
            doc_id_str = str(doc.get("_id"))
            if doc_id_str in processed_ids: continue
            doc["_id"] = doc_id_str
            try:
                spot_model = SightseeingSpot.model_validate(doc)
                spots.append(spot_model)
                processed_ids.add(doc_id_str)
            except ValidationError as validation_error:
                print(f"Warning: Skipping document _id={doc_id_str} due to Pydantic validation error:", file=sys.stderr)
                print(f"Validation Errors: {validation_error.errors()}", file=sys.stderr)
            except Exception as other_error:
                print(f"Warning: Skipping document _id={doc_id_str} due to unexpected error during model validation: {other_error!r}", file=sys.stderr)

        actual_count = len(spots)
        print(f"Text search processed. Returning {actual_count} valid results.", file=sys.stderr)
        return SightseeingListResponse(count=actual_count, sightseeings=spots)

    except OperationFailure as e:
        print(f"ERROR: MongoDB operation failed during text search: {e}", file=sys.stderr)
        error_detail = str(e.details) if hasattr(e, "details") else str(e)
        if "text index required" in error_detail or "$text operator requires a text index" in error_detail:
            raise ValueError("CRITICAL SEARCH FAILURE: The required text index...") # Shortened
        else:
            raise ValueError(f"Database query error occurred: {error_detail}")
    except Exception as e:
        print(f"ERROR: Unexpected error in find_sightseeings_by_description: {e!r}", file=sys.stderr)
        raise ValueError("An unexpected server error occurred while searching.")


# --- Other Tools (Optional - Keep if needed) ---
@mcp.resource(uri="resource://current_time", name="Current Time", mime_type="text/plain")
def get_current_time() -> str:
    """Returns server's current ISO-formatted time"""
    return datetime.now().isoformat()

@mcp.tool(name="Open_URL_in_Browser")
def open_url_in_browser(url: str) -> str:
    """Opens the given URL in the default web browser."""
    if not url or not url.startswith(("http://", "https://")):
        return f"Failed to open URL: Invalid or missing URL provided ('{url}')."
    try:
        print(f"Attempting to open URL in browser: {url}", file=sys.stderr)
        success = webbrowser.open(url, new=2)
        if success: return f"Attempted to open {url} in the default browser."
        else: return f"Failed to open {url}. Browser might not be accessible."
    except Exception as e:
        print(f"ERROR: Could not open URL {url} in browser: {e}", file=sys.stderr)
        return f"Failed to open {url}: An error occurred ({type(e).__name__})."


# --- Server Execution / Testing Block ---

if __name__ == "__main__":
    # This block NOW runs the server when script is executed directly
    # (e.g., by Claude using `.venv/bin/python aramain.py`)
    try:
        print("Starting FastMCP server (direct execution)...", file=sys.stderr)
        # --- IMPORTANT ---
        # Assuming mcp.run() is the correct method for FastMCP to start listening
        # on stdio for MCP messages. Verify with FastMCP documentation if needed.
        mcp.run()
        print("FastMCP server finished running.", file=sys.stderr)
    except KeyboardInterrupt:
         print("\nServer stopped by user (Ctrl+C).", file=sys.stderr)
    except Exception as server_err:
        print(f"CRITICAL ERROR: FastMCP server failed during run: {server_err!r}", file=sys.stderr)
        sys.exit(1) # Exit if server crashes during run
    finally:
        # Cleanup: Close the MongoDB connection when the server stops or crashes
        if mongo_client:
            try:
                mongo_client.close()
                print("MongoDB connection closed after server shutdown.", file=sys.stderr)
            except Exception as close_err:
                print(f"Error closing MongoDB connection during shutdown: {close_err}", file=sys.stderr)

    # --- Testing code is now commented out or moved ---
    # If you want to run tests, create a separate test_aramain.py file
    # or uncomment the code below temporarily, but remember the server won't start then.
    """
    print("\n--- [Direct Script Execution - Testing Mode] ---", file=sys.stderr)
    print("--- Testing 'find_sightseeings_by_description' tool ---", file=sys.stderr)
    # ... (your testing loop here, printing to stderr) ...
    if mongo_client:
        mongo_client.close()
        print("\n[Testing Mode] MongoDB connection closed.", file=sys.stderr)
    """