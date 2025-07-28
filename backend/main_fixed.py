from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from localwander_engine import LocalWanderSearchEngine
from itinerary_generator import ItineraryGenerator

# Load environment variables
load_dotenv()

app = FastAPI(title="Local Wander API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine and itinerary generator
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")

search_engine = LocalWanderSearchEngine(API_KEY)
itinerary_generator = ItineraryGenerator()

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
    
class RefreshSpotRequest(BaseModel):
    location: str
    category: str
    excluded_ids: List[str] = []  # IDs of spots to exclude (already seen)

@app.get("/")
async def root():
    return {
        "message": "Local Wander API", 
        "status": "running",
        "api_key_configured": bool(API_KEY)
    }

@app.post("/api/itineraries", response_model=ItineraryResponse)
async def get_itineraries(request: LocationRequest):
    """
    Generate itineraries for a given location using LocalWander search engine.
    Supports both mixed (default) and preset category searches.
    """
    try:
        if not request.location or len(request.location.strip()) < 2:
            raise HTTPException(status_code=400, detail="Location must be at least 2 characters long")
        
        location = request.location.strip()
        preset = request.preset
        
        if preset:
            print(f"Generating {preset} itineraries for: {location}")
        else:
            print(f"Generating mixed itineraries for: {location}")
        
        # Search for places using LocalWander engine
        search_results = search_engine.search_all_categories(location)
        
        # Generate itineraries from search results (mixed or preset-focused)
        itineraries = itinerary_generator.generate_itineraries(search_results, location, preset)
        
        if not itineraries:
            error_msg = f"Could not find enough places to create itineraries for '{location}'"
            if preset:
                error_msg += f" in the '{preset}' category"
            error_msg += ". Try a more specific location or a different area."
            
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
    Replace a specific spot in an itinerary with a new alternative
    """
    try:
        # Get the original spot's category and location
        category = request.category
        location = request.location
        
        print(f"Refreshing spot: {category} in {location}")
        print(f"Excluded IDs: {request.excluded_ids}")
        
        # Find an alternative spot from the same category
        alternative_spot = itinerary_generator.generate_alternative_spot(
            location, 
            category,
            request.excluded_ids
        )
        
        if not alternative_spot:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find an alternative {category} spot in {location}."
            )
            
        print(f"Found alternative spot: {alternative_spot.get('name')}")
        return alternative_spot
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error refreshing spot: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while refreshing the spot."
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_key_configured": bool(API_KEY),
        "timestamp": "2025-01-23T12:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)