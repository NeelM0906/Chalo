# Chalo Backend

FastAPI backend for the Chalo recommendation engine with live Google Maps integration and an AI agent endpoint.

## Structure

- `main.py` — FastAPI application and API endpoints
- `new_engine.py` — Chalo search engine (Google Geocoding, Places, Distance Matrix)
- `itinerary_generator.py` — Itinerary generation logic
- `agent_tools.py` — Conversational agent (intent parsing + dynamic search)
- `requirements.txt` — Python dependencies

## API Endpoints

- POST `/api/itineraries` — Generate itineraries for a location (supports `preset`, `max_price_level`, `max_distance_miles`)
- POST `/api/custom-trips` — Generate itineraries for selected categories and distance
- POST `/api/refresh-spot` — Replace a spot using cached results
- POST `/api/refresh-category` — Replace a spot from a different category with exclusion logic
- POST `/api/get-available-spots` — List candidate spots to add
- POST `/api/agent-recommendations` — AI conversational route suggestions
- GET `/api/maps-config` — Returns browser-safe Maps Embed key for client map embeds
- GET `/api/health` — Health check

### Testing mode (uses saved data instead of live API)
- POST `/api/testing/enable`
- POST `/api/testing/disable`
- GET `/api/testing/status`

## Environment

Create `backend/.env` with keys (names shown for clarity):
```
GOOGLE_PLACES_API_KEY=...
MAPS_EMBED_API_KEY=...
GEMINI_API_KEY=...
```

## Development

Install and run:
```bash
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`.