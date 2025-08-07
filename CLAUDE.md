# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local Wander is a modular travel discovery application with a React TypeScript frontend and Python FastAPI backend. It helps users discover hyper-local adventures and itineraries powered by a custom recommendation engine that integrates with Google Maps APIs.

## Development Commands

### Backend (FastAPI + Python)
- **Start development server**: `python backend/main.py` (runs on http://localhost:8000)
- **Quick start with virtual environment**: `cd backend && ./start-backend.sh`
- **Install dependencies**: `cd backend && pip install -r requirements.txt`
- **Manual virtual environment setup**:
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Frontend (React + TypeScript + Vite)
- **Start development server**: `cd frontend && npm run dev` (runs on http://localhost:5173)
- **Build for production**: `cd frontend && npm run build`
- **Preview production build**: `cd frontend && npm run preview`
- **Install dependencies**: `cd frontend && npm install`

## Architecture Overview

### Backend Structure (`backend/`)
- **`main.py`**: FastAPI application entry point with all API endpoints
- **`new_engine.py`**: Core search engine (`ChaloSearchEngine` class) that interfaces with Google Maps APIs
- **`itinerary_generator.py`**: Handles itinerary creation and formatting from search results
- **`category_exclusion_manager.py`**: Manages category exclusion logic for variety in recommendations

### Frontend Structure (`frontend/src/`)
- **`App.tsx`**: Main application component with routing logic
- **`components/`**: Reusable React components (modals, buttons, cards, etc.)
- **`context/`**: React context providers for state management (TripContext, FavoritesContext)
- **`services/apiService.ts`**: API communication layer with typed interfaces
- **`types.ts`**: TypeScript type definitions shared across the app

### Key API Integrations
- **Google Geocoding API**: Address to coordinates conversion
- **Google Places API**: Nearby place searches and detailed place information
- **Google Distance Matrix API**: Real walking distance calculations

## Core Features Implementation

### Search Engine (`ChaloSearchEngine`)
- Searches 9 categories: restaurants, cafes, parks, delis, thrift stores, tourist attractions, museums, galleries, markets
- Uses concurrent processing for performance
- Implements rate limiting (0.1-0.5s delays between API calls)
- Filters results by rating (4.4+ minimum) and distance constraints
- Caches results for refresh functionality

### Itinerary Generation
- **Mixed itineraries**: Default mode with natural variety across categories
- **Preset filters**: Nature, Food, Culture, Shopping, History categories
- **Custom trips**: User-selected categories with distance preferences
- **Smart clustering**: Groups nearby places (0.5-1.0 mile radius) for walkable routes
- **Food placement logic**: Positions restaurants/cafes in middle of journeys

### API Endpoints
- `POST /api/itineraries`: Generate standard itineraries
- `POST /api/custom-trips`: Generate custom category-specific trips
- `POST /api/refresh-spot`: Replace individual spots in itineraries
- `POST /api/refresh-category`: Replace spots with different category alternatives
- `GET /api/maps-config`: Provide Google Maps API key for frontend
- `GET /api/health`: Health check endpoint

## Environment Setup

### Required Environment Variables
Create `backend/.env` with:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

### Google Cloud Setup Requirements
1. Enable APIs: Geocoding API, Places API (New), Distance Matrix API
2. Create API key with appropriate restrictions
3. Ensure billing is enabled on Google Cloud project

## Testing and Development Notes

### Testing Mode
- Backend supports testing mode via `/api/testing/enable` endpoint
- Uses cached Manhattan data instead of live API calls
- Controlled via `ChaloSearchEngine.set_testing_mode()`

### Data Flow
1. Frontend sends location request to backend
2. Backend geocodes location using Google Maps
3. Concurrent category searches using Places API
4. Distance calculations via Distance Matrix API
5. Itinerary generation with clustering algorithms
6. Results cached for refresh functionality

### Rate Limiting Strategy
- 0.1-0.5 second delays between API calls to respect Google's limits
- Concurrent processing where possible (category searches)
- Place details fetched only for top-rated places (rating >= 4.4)

## Development Patterns

### Error Handling
- FastAPI uses HTTPException for structured error responses
- Frontend displays user-friendly error messages
- API errors include helpful suggestions (adjust filters, try different location)

### State Management
- React Context for global state (trip data, favorites)
- Local component state for UI interactions
- API service layer abstracts backend communication

### Code Organization
- Backend follows modular structure with separate concerns
- Frontend uses component composition patterns
- Shared types between frontend/backend for consistency