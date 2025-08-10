import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import random
import time
import json
from dotenv import load_dotenv

from new_engine import ChaloSearchEngine
from itinerary_generator import ItineraryGenerator
from category_exclusion_manager import CategoryExclusionManager
from AI_engine import ask_yelp_ai, transform_yelp_ai_response, UserContext

# Load environment variables
load_dotenv()

app = FastAPI(title="Chalo API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development mode)
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine and itinerary generator
# Read Google Maps API key from environment
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

search_engine = ChaloSearchEngine(API_KEY)
itinerary_generator = ItineraryGenerator()
category_exclusion_manager = CategoryExclusionManager()

# Global cache for search results to enable refresh functionality
search_results_cache = {}

# Data models
class Stop(BaseModel):
    id: str
    name: str
    category: str
    walking_time_minutes: int
    description: Optional[str] = None
    image_url: str

class Itinerary(BaseModel):
    id: str
    title: str
    description: str
    duration_minutes: int
    stops: List[Stop]

class GroundingChunk(BaseModel):
    web: dict

class ItineraryResponse(BaseModel):
    itineraries: List[Itinerary]
    sources: List[GroundingChunk]

class LocationRequest(BaseModel):
    location: str
    preset: Optional[str] = None  # For preset searches like "Nature & Parks"
    max_price_level: Optional[str] = None  # "10-20", "20-50", "50+"
    max_distance_miles: Optional[float] = 1.5  # Default 1.5 miles
    
class RefreshSpotRequest(BaseModel):
    location: str
    category: str
    excluded_ids: List[str] = []  # IDs of spots to exclude (already seen)

class RefreshCategoryRequest(BaseModel):
    location: str
    current_category: str
    excluded_spot_ids: List[str] = []

class CustomTripRequest(BaseModel):
    location: str
    categories: List[str]  # List of category IDs like ['cafe', 'restaurant', 'park']
    max_distance_miles: float = 1.5

class AddSpotRequest(BaseModel):
    location: str
    position: int  # 0-based index where to insert the spot
    category: Optional[str] = None  # Optional category filter
    excluded_ids: List[str] = []  # IDs of spots to exclude

class RemoveSpotRequest(BaseModel):
    spot_id: str

class GetAvailableSpotsRequest(BaseModel):
    location: str
    category: Optional[str] = None
    excluded_ids: List[str] = []
    max_distance_miles: float = 1.5

class AIEngineBusinessLocation(BaseModel):
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    formatted_address: Optional[str] = None


class AIEngineCoordinates(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None


class AIEngineBusiness(BaseModel):
    id: Optional[str] = None
    alias: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    photos: Optional[List[str]] = None
    phoos: Optional[List[str]] = None
    location: AIEngineBusinessLocation
    coordinates: AIEngineCoordinates
    review_count: Optional[int] = None
    price: Optional[str] = None
    rating: Optional[float] = None
    AboutThisBizBio: Optional[str] = None
    AboutThisBizHistory: Optional[str] = None
    AboutThisBizSpecialties: Optional[str] = None
    AboutThisBizYearEstablished: Optional[str] = None


class AIDayPlanStop(BaseModel):
    time: Optional[str] = None
    name: str
    category: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    duration_minutes: Optional[int] = None


class AIDayPlan(BaseModel):
    id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    total_duration_minutes: Optional[int] = None
    total_stops: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    map_url: Optional[str] = None
    tips: Optional[list[str]] = None
    budget: Optional[str] = None
    transportation: Optional[str] = None
    weather_note: Optional[str] = None
    stops: list[AIDayPlanStop]
    additional_info: Optional[dict] = None


class AIEngineChatResponse(BaseModel):
    chat_id: Optional[str] = None
    text: Optional[str] = None
    businesses: List[AIEngineBusiness]
    plan: Optional[AIDayPlan] = None
    plans: Optional[list[AIDayPlan]] = None
class AgentRequest(BaseModel):
    user_request: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_miles: Optional[float] = 1.5

@app.get("/")
async def root():
    return {
        "message": "Chalo API", 
        "status": "running",
        "api_key_configured": bool(API_KEY)
    }

@app.post("/api/itineraries", response_model=ItineraryResponse)
async def get_itineraries(request: LocationRequest):
    """
    Generate itineraries for a given location using Chalo search engine.
    Supports both mixed (default) and preset category searches with price and distance filters.
    """
    try:
        if not request.location or len(request.location.strip()) < 2:
            raise HTTPException(status_code=400, detail="Location must be at least 2 characters long")
        
        location = request.location.strip()
        preset = request.preset
        max_price_level = request.max_price_level
        max_distance_miles = request.max_distance_miles or 1.5
        
        if preset:
            print(f"Generating {preset} itineraries for: {location}")
        else:
            print(f"Generating mixed itineraries for: {location}")
        
        print(f"Filters - Price: {max_price_level or 'Any'}, Distance: {max_distance_miles} miles")
        
        # CACHING DISABLED FOR TESTING - Always perform fresh search

        
        # Always search fresh (no cache check)
        search_results = search_engine.search_all_categories(location, max_distance_miles)
        
        # Cache results for refresh functionality (but we don't read from cache first)
        cache_key = f"{location}_{max_distance_miles}"
        search_results_cache[cache_key] = search_results
        search_results_cache[location] = search_results
        
        # Generate itineraries from search results with filters
        itineraries = itinerary_generator.generate_itineraries(
            search_results, location, preset, max_price_level, max_distance_miles
        )
        
        if not itineraries:
            error_msg = f"Could not find enough places to create itineraries for '{location}'"
            if preset:
                error_msg += f" in the '{preset}' category"
            if max_price_level:
                error_msg += f" within ${max_price_level} price range"
            error_msg += f" within {max_distance_miles} miles"
            error_msg += ". Try adjusting your filters or a different area."
            
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Create sources from search results
        sources = itinerary_generator.create_sources_from_search(search_results)
        
        search_type = f"{preset} " if preset else "mixed "
        print(f"Generated {len(itineraries)} {search_type}itineraries with {len(sources)} sources")
        
        return ItineraryResponse(
            itineraries=itineraries,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating itineraries: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while generating itineraries. Please try again."
        )

@app.post("/api/refresh-spot")
async def refresh_spot(request: RefreshSpotRequest):
    """
    Replace a specific spot in an itinerary with a new alternative using cached results
    """
    try:
        category = request.category
        location = request.location
        
        print(f"Refreshing spot: {category} in {location}")
        
        # Use cached search results if available
        if location not in search_results_cache:
            raise HTTPException(
                status_code=404,
                detail=f"No cached results found for {location}. Please search for itineraries first."
            )
        
        search_results = search_results_cache[location]
        
        # Find places that match the category from cached results
        all_places = []
        for category_results in search_results.get('results_by_category', {}).values():
            for place in category_results:
                # Skip places we've already seen
                if place.get('place_id') in request.excluded_ids:
                    continue
                    
                # Check if this place matches the requested category
                place_category = itinerary_generator.categorize_place(place)
                if (category.lower() in place_category.lower() or 
                    place_category.lower() in category.lower() or
                    itinerary_generator.get_broad_type(place) == itinerary_generator.get_broad_type({'types': [category.lower()]})):
                    all_places.append(place)
        
        if not all_places:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find an alternative {category} spot in cached results for {location}."
            )
            
        # Sort by rating and pick a random good one (not always the best to add variety)
        all_places.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', 0)))
        top_places = all_places[:min(5, len(all_places))]  # Top 5 places
        selected_place = random.choice(top_places)
        
        # Create a stop from this place
        alternative_spot = itinerary_generator.create_stop_from_place(selected_place)
            
        print(f"Found alternative spot: {alternative_spot.get('name')} (from cached results)")
        return alternative_spot
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error refreshing spot: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while refreshing the spot."
        )

@app.post("/api/refresh-category")
async def refresh_category(request: RefreshCategoryRequest):
    """
    Replace a spot with an alternative from a different category using exclusion logic
    """
    try:
        location = request.location
        current_category = request.current_category
        excluded_spot_ids = request.excluded_spot_ids
        
        # Validate required parameters
        if not location or len(location.strip()) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Location must be at least 2 characters long"
            )
        
        if not current_category or len(current_category.strip()) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Current category is required"
            )
        
        location = location.strip()
        current_category = current_category.strip()
        
        print(f"Refreshing category from '{current_category}' in {location}")
        
        # Check if we have cached search results for this location
        if location not in search_results_cache:
            raise HTTPException(
                status_code=404,
                detail=f"No cached results found for {location}. Please search for itineraries first."
            )
        
        search_results = search_results_cache[location]
        
        # Exclude the current category from future recommendations
        category_exclusion_manager.exclude_category(location, current_category)
        
        # Get all available categories (not excluded)
        all_categories = []
        for category_results in search_results.get('results_by_category', {}).values():
            for place in category_results:
                place_category = itinerary_generator.categorize_place(place)
                if place_category not in all_categories:
                    all_categories.append(place_category)
        
        available_categories = category_exclusion_manager.get_available_categories(location, all_categories)
        
        # Remove current category from available options
        if current_category in available_categories:
            available_categories.remove(current_category)
        
        if not available_categories:
            raise HTTPException(
                status_code=404,
                detail="No alternative categories available. All categories have been recently used."
            )
        
        # Find places from alternative categories
        alternative_places = []
        for category_results in search_results.get('results_by_category', {}).values():
            for place in category_results:
                # Skip places we've already seen
                if place.get('place_id') in excluded_spot_ids:
                    continue
                
                place_category = itinerary_generator.categorize_place(place)
                
                # Only include places from available (non-excluded) categories
                if place_category in available_categories:
                    alternative_places.append(place)
        
        if not alternative_places:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find alternative spots from different categories in cached results for {location}."
            )
        
        # Sort by rating and pick a random good one for variety
        alternative_places.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', 0)))
        top_places = alternative_places[:min(5, len(alternative_places))]
        selected_place = random.choice(top_places)
        
        # Create a stop from this place
        alternative_spot = itinerary_generator.create_stop_from_place(selected_place)
        
        # Increment turn counter for exclusion management
        category_exclusion_manager.increment_turn(location)
        
        selected_category = itinerary_generator.categorize_place(selected_place)
        print(f"Found alternative spot: {alternative_spot.get('name')} (category: {selected_category})")
        
        return alternative_spot
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error refreshing category: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while refreshing the category."
        )

@app.post("/api/agent-recommendations", response_model=AIEngineChatResponse)
async def get_agent_recommendations(request: AgentRequest):
    """
    AI search powered by Yelp AI Chat v2.

    Accepts a natural language query and optional location (as a string) or coordinates.
    Returns chat text and a normalized list of businesses.
    """
    try:
        # Validate input
        if not request.user_request or len(request.user_request.strip()) < 3:
            raise HTTPException(status_code=400, detail="User request must be at least 3 characters long")

        # Resolve coordinates: prefer explicit lat/lng; else geocode location string if provided
        latitude = request.latitude
        longitude = request.longitude
        resolved_location = (request.location or "").strip() if request.location else None

        if (latitude is None or longitude is None) and resolved_location:
            try:
                import requests as _req
                geocode_url = (
                    f"https://maps.googleapis.com/maps/api/geocode/json?address={resolved_location}&key={API_KEY}"
                )
                geocode_resp = _req.get(geocode_url, timeout=10)
                if geocode_resp.ok:
                    geo_data = geocode_resp.json()
                    results = geo_data.get("results", [])
                    if results:
                        loc = results[0].get("geometry", {}).get("location", {})
                        latitude = latitude or loc.get("lat")
                        longitude = longitude or loc.get("lng")
            except Exception:
                # Non-fatal: continue without coordinates
                pass

        user_context = UserContext(
            locale="en_US",
            latitude=latitude,
            longitude=longitude,
        )

        print(
            f"AI Engine Request: '{request.user_request.strip()}', "
            f"coords=({user_context.latitude},{user_context.longitude}), location='{resolved_location or ''}'"
        )

        # Craft a plan-seeking prompt so the AI can optionally return a structured day plan JSON
        base_query = request.user_request.strip()
        miles_txt = f"within ~{request.distance_miles or 1.5} miles"
        loc_txt = f" around {resolved_location}" if resolved_location else " nearby"
        plan_instruction = (
            "\n\nPlease propose a single cohesive local day plan "
            f"{miles_txt}{loc_txt}. Provide both a short natural-language summary and, if possible, "
            "a machine-readable JSON object named plan with this shape:"
            " {title, summary, total_duration_minutes, total_stops, start_time, end_time, map_url, tips[], "
            "budget, transportation, weather_note, stops:[{time, name, category, notes, address, image_url, duration_minutes}]}. "
            "Return the JSON inside a single fenced code block labeled json."
        )
        composed_query = base_query + plan_instruction

        # Call Yelp AI with increased timeout and a single retry. On failure, fallback to local sample.
        raw = ask_yelp_ai(composed_query, user_context)
        transformed = transform_yelp_ai_response(raw)

        # Ensure shape matches Pydantic model
        businesses_payload: list[AIEngineBusiness] = []
        for b in transformed.get("businesses", []):
            businesses_payload.append(
                AIEngineBusiness(
                    id=b.get("id"),
                    alias=b.get("alias"),
                    name=b.get("name"),
                    url=b.get("url"),
                    image_url=b.get("image_url"),
                    photos=b.get("photos"),
                    phoos=b.get("phoos"),
                    location=AIEngineBusinessLocation(**(b.get("location") or {})),
                    coordinates=AIEngineCoordinates(**(b.get("coordinates") or {})),
                    review_count=b.get("review_count"),
                    price=b.get("price"),
                    rating=b.get("rating"),
                    AboutThisBizBio=b.get("AboutThisBizBio"),
                    AboutThisBizHistory=b.get("AboutThisBizHistory"),
                    AboutThisBizSpecialties=b.get("AboutThisBizSpecialties"),
                    AboutThisBizYearEstablished=b.get("AboutThisBizYearEstablished"),
                )
            )

        plan_payload = None
        plans_payload: list[AIDayPlan] = []
        if isinstance(transformed.get("plan"), dict):
            plan_dict = transformed.get("plan") or {}
            try:
                # Coerce stops
                stops_payload: list[AIDayPlanStop] = []
                for s in plan_dict.get("stops", []) or []:
                    stops_payload.append(AIDayPlanStop(**s))
                plan_payload = AIDayPlan(
                    id=plan_dict.get("id"),
                    title=plan_dict.get("title") or "AI Day Plan",
                    summary=plan_dict.get("summary"),
                    total_duration_minutes=plan_dict.get("total_duration_minutes"),
                    total_stops=plan_dict.get("total_stops"),
                    start_time=plan_dict.get("start_time"),
                    end_time=plan_dict.get("end_time"),
                    map_url=plan_dict.get("map_url"),
                    tips=plan_dict.get("tips"),
                    budget=plan_dict.get("budget"),
                    transportation=plan_dict.get("transportation"),
                    weather_note=plan_dict.get("weather_note"),
                    stops=stops_payload,
                    additional_info=plan_dict.get("additional_info"),
                )
            except Exception:
                plan_payload = None

        if isinstance(transformed.get("plans"), list):
            for p in transformed.get("plans") or []:
                if isinstance(p, dict):
                    try:
                        stops_payload: list[AIDayPlanStop] = []
                        for s in p.get("stops", []) or []:
                            stops_payload.append(AIDayPlanStop(**s))
                        plans_payload.append(
                            AIDayPlan(
                                id=p.get("id"),
                                title=p.get("title") or "AI Day Plan",
                                summary=p.get("summary"),
                                total_duration_minutes=p.get("total_duration_minutes"),
                                total_stops=p.get("total_stops"),
                                start_time=p.get("start_time"),
                                end_time=p.get("end_time"),
                                map_url=p.get("map_url"),
                                tips=p.get("tips"),
                                budget=p.get("budget"),
                                transportation=p.get("transportation"),
                                weather_note=p.get("weather_note"),
                                stops=stops_payload,
                                additional_info=p.get("additional_info"),
                            )
                        )
                    except Exception:
                        pass

        # Fallback: synthesize a minimal plan from businesses if no plan provided and no multiple plans
        if plan_payload is None and not plans_payload and businesses_payload:
            try:
                print("Synthesizing AIDayPlan from businesses…")
                # Build minimal stops (name, address, image)
                stops_payload: list[AIDayPlanStop] = []
                for b in businesses_payload[:6]:
                    stops_payload.append(
                        AIDayPlanStop(
                            name=b.name or "Spot",
                            category=None,
                            notes=None,
                            address=(b.location.formatted_address if b.location else None),
                            image_url=b.image_url,
                            duration_minutes=None,
                        )
                    )
                synthesized_title = (
                    (request.user_request[:80] + ("…" if len(request.user_request) > 80 else "")).strip()
                ) or "AI Day Plan"
                plan_payload = AIDayPlan(
                    title=synthesized_title,
                    summary=transformed.get("text"),
                    total_duration_minutes=None,
                    total_stops=len(stops_payload),
                    start_time=None,
                    end_time=None,
                    map_url=None,
                    tips=None,
                    budget=None,
                    transportation=None,
                    weather_note=None,
                    stops=stops_payload,
                    additional_info={"synthesized_from_businesses": True},
                )
                print("Synthesized plan with", len(stops_payload), "stops")
            except Exception as synth_err:
                print("Failed to synthesize plan:", synth_err)
                plan_payload = None

        return AIEngineChatResponse(
            chat_id=transformed.get("chat_id"),
            text=transformed.get("text"),
            businesses=businesses_payload,
            plan=plan_payload,
            plans=plans_payload or None,
        )

        

    except HTTPException:
        raise
    except Exception as e:
        print(f"AI Engine API Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )

@app.get("/api/maps-config")
async def get_maps_config():
    """Get Google Maps API configuration for frontend"""
    return {
        "maps_api_key": API_KEY  # Using the same API key for Maps Embed API
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_key_configured": bool(API_KEY),
        "timestamp": "2025-01-23T12:00:00Z"
    }

# TESTING MODE: Endpoints for toggling testing mode
@app.post("/api/testing/enable")
async def enable_testing_mode():
    """Enable testing mode - uses saved Manhattan data instead of API calls"""
    search_engine.set_testing_mode(True)
    return {
        "status": "success",
        "message": "Testing mode enabled - using saved Manhattan data",
        "testing_mode": True
    }

@app.post("/api/testing/disable")
async def disable_testing_mode():
    """Disable testing mode - returns to normal API calls"""
    search_engine.set_testing_mode(False)
    return {
        "status": "success",
        "message": "Testing mode disabled - using live API calls",
        "testing_mode": False
    }

@app.get("/api/testing/status")
async def get_testing_status():
    """Get current testing mode status"""
    return {
        "testing_mode": search_engine.testing_mode,
        "data_file": search_engine.testing_data_file if search_engine.testing_mode else None
    }

@app.post("/api/custom-trips", response_model=ItineraryResponse)
async def get_custom_trips(request: CustomTripRequest):
    """
    Generate custom trips based on user-selected categories and distance preferences.
    Uses the new_engine.py functionality for category-specific searches.
    """
    try:
        if not request.location or len(request.location.strip()) < 2:
            raise HTTPException(status_code=400, detail="Location must be at least 2 characters long")
        
        if not request.categories or len(request.categories) == 0:
            raise HTTPException(status_code=400, detail="At least one category must be selected")
        
        location = request.location.strip()
        max_distance_miles = request.max_distance_miles or 1.5
        
        print(f"Generating custom trips for: {location}")
        print(f"Categories: {request.categories}")
        print(f"Distance: {max_distance_miles} miles")
        
        # CACHING DISABLED FOR TESTING - Always perform fresh search

        
        # Convert category IDs to search queries
        category_queries = []
        category_mapping = {
            'cafe': 'cafes and bakeries near me',
            'restaurant': 'restaurants near me',
            'park': 'parks near me',
            'museum': 'museums near me',
            'art_gallery': 'galleries near me',
            'tourist_attraction': 'tourist attractions near me'
        }
        
        for category_id in request.categories:
            if category_id in category_mapping:
                category_queries.append(category_mapping[category_id])
        
        if not category_queries:
            raise HTTPException(status_code=400, detail="Invalid categories selected")
        
        # Always search fresh (no cache check)
        search_results = search_engine.search_specific_categories(
            location, category_queries, max_distance_miles
        )
        
        # Cache results for refresh functionality (but we don't read from cache first)
        cache_key = f"{location}_{','.join(sorted(request.categories))}_{max_distance_miles}"
        search_results_cache[cache_key] = search_results
        # Also cache with location key for refresh endpoints
        search_results_cache[location] = search_results
        
        # Generate custom itineraries with user category preferences
        itineraries = itinerary_generator.generate_custom_itineraries(
            search_results, location, max_distance_miles, request.categories
        )
        
        if not itineraries:
            total_places = sum(len(places) for places in search_results.get('results_by_category', {}).values())
            error_msg = f"Could not create custom trips for '{location}' with selected categories"
            if total_places == 0:
                error_msg += f" - no places found within {max_distance_miles} miles"
            else:
                error_msg += f" - found {total_places} places but could not create valid itineraries"
            error_msg += ". Try selecting different categories or increasing distance range."
            
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Limit to 3 itineraries for custom trips
        limited_itineraries = itineraries[:3]
        
        # Create sources from search results
        sources = itinerary_generator.create_sources_from_search(search_results)
        
        print(f"Generated {len(limited_itineraries)} custom trips with {len(sources)} sources")
        
        return ItineraryResponse(
            itineraries=limited_itineraries,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating custom trips: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while generating custom trips. Please try again."
        )

@app.post("/api/get-available-spots")
async def get_available_spots(request: GetAvailableSpotsRequest):
    """
    Get available spots that can be added to an itinerary
    """
    try:
        location = request.location.strip()
        
        if not location or len(location) < 2:
            raise HTTPException(status_code=400, detail="Location must be at least 2 characters long")
        
        print(f"Getting available spots for: {location}")
        
        # Use cached search results if available, otherwise search fresh
        if location not in search_results_cache:
            # Perform fresh search
            search_results = search_engine.search_all_categories(location, request.max_distance_miles)
            search_results_cache[location] = search_results
        else:
            search_results = search_results_cache[location]
        
        # Find available places
        available_places = []
        for category_results in search_results.get('results_by_category', {}).values():
            for place in category_results:
                # Skip excluded places
                if place.get('place_id') in request.excluded_ids:
                    continue
                
                # Filter by category if specified
                if request.category:
                    place_category = itinerary_generator.categorize_place(place)
                    if request.category.lower() not in place_category.lower():
                        continue
                
                # Check distance constraint
                distance_meters = place.get('distance_meters', 0)
                max_distance_meters = request.max_distance_miles * 1609.34
                if distance_meters <= max_distance_meters:
                    available_places.append(place)
        
        if not available_places:
            raise HTTPException(
                status_code=404,
                detail=f"No available spots found for {location}"
            )
        
        # Sort by rating and distance
        available_places.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', 0)))
        
        # Convert to stops (limit to top 20 for performance)
        available_spots = []
        for place in available_places[:20]:
            spot = itinerary_generator.create_stop_from_place(place)
            available_spots.append(spot)
        
        print(f"Found {len(available_spots)} available spots")
        return {"spots": available_spots}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting available spots: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while getting available spots."
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)