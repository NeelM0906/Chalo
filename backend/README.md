# Local Wander Backend

FastAPI backend for the Local Wander recommendation engine.

## Structure

- `main.py` - Main FastAPI application with API endpoints
- `requirements.txt` - Python dependencies

## API Endpoints

### POST /api/itineraries

Generate itineraries for a given location.

**Request:**
```json
{
  "location": "San Francisco, CA"
}
```

**Response:**
```json
{
  "itineraries": [
    {
      "id": "itinerary-uuid",
      "title": "Hidden Gems of San Francisco",
      "description": "Discover the secret spots locals love in your neighborhood.",
      "duration_minutes": 180,
      "stops": [
        {
          "id": "stop-uuid",
          "name": "Local Coffee Roastery",
          "category": "Cafe",
          "walking_time_minutes": 0,
          "description": "Start your adventure with artisanal coffee from local beans.",
          "image_url": "https://images.unsplash.com/..."
        }
      ]
    }
  ],
  "sources": []
}
```

## Development

The current implementation includes placeholder data. Replace the logic in the `/api/itineraries` endpoint with your custom recommendation engine.

Key areas to implement:
1. Location parsing and validation
2. Data source integration (maps, reviews, local business data)
3. Recommendation algorithm
4. Image URL generation or integration with image services
5. Source tracking for transparency