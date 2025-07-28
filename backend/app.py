from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import random
from dotenv import load_dotenv

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

# Data models
class Stop(BaseModel):
    id: str
    name: str
    category: str
    walking_time_minutes: int
    description: Optional[str] = None
    image_url: str

class RefreshSpotRequest(BaseModel):
    location: str
    category: str
    excluded_ids: List[str] = []  # IDs of spots to exclude (already seen)

@app.get("/")
async def root():
    return {"message": "Local Wander API - Refresh Spot Service"}

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
        
        # For testing purposes, just return a mock spot
        stock_images = [
            'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1470&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1541167760496-1628856ab772?q=80&w=1637&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1472851294608-062f824d29cc?q=80&w=1470&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1469&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1544&auto=format&fit=crop'
        ]
        
        mock_spot = {
            'id': f"stop-{uuid.uuid4()}",
            'name': f"Alternative {category} in {location}",
            'category': category,
            'walking_time_minutes': random.randint(5, 15),
            'description': f"This is an alternative {category.lower()} spot in {location}.",
            'image_url': random.choice(stock_images)
        }
            
        print(f"Found alternative spot: {mock_spot['name']}")
        return mock_spot
        
    except Exception as e:
        print(f"Error refreshing spot: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while refreshing the spot."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)