from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import random
from dotenv import load_dotenv

from localwander_engine import ChaloSearchEngine
from itinerary_generator import ItineraryGenerator
from category_exclusion_manager import CategoryExclusionManager

# Load environment variables
load_dotenv()

app = FastAPI(title="Chalo API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3001"],  # Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine and itinerary generator
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")

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
        
        # Create cache key that includes distance filter
        cache_key = f"{location}_{max_distance_miles}"
        
        # Check cache first
        if cache_key in search_results_cache:
            print(f"Using cached search results for {cache_key}")
            search_results = search_results_cache[cache_key]
        else:
            # Search for places using Chalo engine with custom radius
            search_results = search_engine.search_all_categories(location, max_distance_miles)
            
            # Cache search results for refresh functionality
            search_results_cache[cache_key] = search_results
            # Also cache with location key for backward compatibility
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)