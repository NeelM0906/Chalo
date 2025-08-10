# Chalo - Custom Recommendation Engine

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
- Backend is fully integrated with Google Maps (Geocoding, Places, Distance Matrix) and includes an AI agent endpoint

## Google Maps and AI Setup

The backend uses Google Maps APIs for location data and optionally Gemini for conversational generation. You'll need:

1. **Google Cloud Project** with billing enabled
2. **Enable these APIs:**
   - Geocoding API
   - Places API (New)
   - Distance Matrix API
3. **Create API keys** with appropriate restrictions
   - Server key for Places/Geocoding/Distance Matrix: `GOOGLE_PLACES_API_KEY`
   - Browser key for Maps Embed: `MAPS_EMBED_API_KEY`
   - Optional Gemini key: `GEMINI_API_KEY`
4. **Add keys** to `backend/.env`

### API Usage
- **Geocoding**: Convert addresses to coordinates
- **Places Search**: Find nearby businesses and attractions
- **Place Details**: Get comprehensive place information
- **Distance Matrix**: Calculate real walking distances

## Current Implementation

✅ **Fully Integrated Chalo Search Engine**
- Real-time Google Maps API integration (server-side)
- 9 category search (restaurants, cafes, parks, museums, etc.)
- 1.5-mile radius local discovery
- Concurrent processing and rate limiting

✅ **Intelligent Itinerary Generation**
- Mixed itineraries with natural variety (default)
- Preset and custom category filters
- Real walking time calculations and logical ordering
- Rich descriptions with ratings and reviews

✅ **Conversational Agent**
- Endpoint: POST `/api/agent-recommendations`
- Rule-based intent parsing with Gemini fallback
- Dynamic category search mapped from user requests

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

## Local Guide Speech Agent

A minimal conversational agent that:
- Reads recommendation content from an AI engine output (expects a JSON with a `text` field)
- Speaks the recommendation locally using an offline, open-source TTS engine (`pyttsx3` / eSpeak on Linux)
- Saves the audio as a WAV file

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

Using the bundled sample AI engine output:

```bash
python main.py --query "What should I do this afternoon?"
```

Custom AI engine JSON path (must contain a `text` field):

```bash
python main.py --query "Best places for dinner?" --ai-json /path/to/ai_engine_output.json --out /workspace/output/dinner.wav
```

Optional: adjust voice and rate (depends on your installed voices):

```bash
python main.py --query "Family-friendly activities" --voice english --rate 165
```

### Integrating a real AI engine

Replace `AIEngine.query` in `app/ai_engine.py` to call your service and return a dict with at least:

```json
{"text": "... your recommendation text ..."}
```

The agent will speak exactly the `text` content it receives.

### Online TTS (no local speech computation)

This app now uses gTTS (Google Translate TTS) to synthesize speech online. Your text is sent to the service, and an MP3 is returned and saved locally. No on-device speech generation occurs.

- Default output: MP3
- Flags:
  - `--lang`: language code (e.g., `en`, `en-GB`, `es`, `fr`)
  - `--tld`: region TLD (e.g., `com`, `co.uk`) which can affect accent
  - `--slow`: slower speech

Example:

```bash
python main.py --query "Food near the river" --lang en --tld com --slow
```