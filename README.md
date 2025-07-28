# Local Wander - Custom Recommendation Engine

A modular travel discovery application with a React frontend and Python FastAPI backend. Users can discover hyper-local adventures and itineraries powered by a custom recommendation engine.

## Project Structure

```
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── context/         # React context providers
│   │   ├── services/        # API service layer
│   │   ├── types.ts         # TypeScript type definitions
│   │   ├── App.tsx          # Main app component
│   │   └── index.tsx        # App entry point
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
├── backend/                  # Python FastAPI backend
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
└── README.md
```

## Features

- **Mixed Itineraries (Default)** - Naturally varied adventures with diverse place types
- **Preset Category Filters** - Optional focus on Nature, Food, Culture, Shopping, or History
- **Location-based recommendations** - Enter a location to get local adventure suggestions
- **Detailed itineraries** - Each itinerary includes multiple stops with categories, walking times, and descriptions
- **Source transparency** - Shows sources used to generate recommendations
- **Favorites system** - Users can save favorite stops
- **Modal details** - Detailed view of itineraries

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a `.env` file with your Google Maps API key:
   ```bash
   echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the FastAPI server:
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

**Quick Start:** Use `./start-backend.sh` to automate steps 3-5

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## API Endpoints

- `GET /` - Health check
- `POST /api/itineraries` - Generate itineraries for a location
  - Request body: `{"location": "string", "preset": "optional category filter"}`
  - Response: `{"itineraries": [...], "sources": [...]}`

## Development Notes

- The frontend uses Vite with React 19 and TypeScript
- The backend uses FastAPI with Pydantic for data validation
- CORS is configured to allow requests from the frontend development server
- The current backend includes placeholder data - replace with your custom recommendation engine

## Google Maps API Setup

The backend uses Google Maps APIs for location data. You'll need:

1. **Google Cloud Project** with billing enabled
2. **Enable these APIs:**
   - Geocoding API
   - Places API (New)
   - Distance Matrix API
3. **Create an API key** with appropriate restrictions
4. **Add the API key** to `backend/.env`

### API Usage
- **Geocoding**: Convert addresses to coordinates
- **Places Search**: Find nearby businesses and attractions
- **Place Details**: Get comprehensive place information
- **Distance Matrix**: Calculate real walking distances

## Current Implementation

✅ **Fully Integrated LocalWander Search Engine**
- Real-time Google Maps API integration
- 9 category search (restaurants, cafes, parks, museums, etc.)
- 1.5-mile radius local discovery
- Concurrent processing for performance
- Rate limiting for API compliance

✅ **Intelligent Itinerary Generation**
- **Mixed itineraries** with natural variety (default)
- **Preset category filters** (Nature, Food, Culture, Shopping, History)
- Food stops naturally positioned in middle of journeys
- Real walking time calculations
- Logical stop ordering by distance
- Rich place descriptions with ratings and reviews

✅ **Production-Ready Features**
- Error handling and validation
- Health check endpoints
- CORS configuration
- Environment variable management

## Next Steps

1. ~~Implement your custom recommendation engine~~ ✅ **COMPLETE**
2. Add database integration for caching and user data
3. Implement user authentication if needed
4. Add more sophisticated error handling and logging
5. Deploy to production environment