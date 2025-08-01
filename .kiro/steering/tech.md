# Technology Stack

## Backend
- **Framework**: FastAPI with Python 3.x
- **API Integration**: Google Maps APIs (Geocoding, Places, Distance Matrix)
- **Dependencies**: 
  - `fastapi==0.104.1` - Web framework
  - `uvicorn==0.24.0` - ASGI server
  - `pydantic==2.5.0` - Data validation
  - `requests==2.31.0` - HTTP client
  - `python-dotenv==1.0.0` - Environment variables
- **Environment**: Virtual environment with `venv`
- **Configuration**: `.env` file for API keys and secrets

## Frontend Applications

### Primary Frontend (`frontend/`)
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Custom CSS with CSS variables
- **Dependencies**: 
  - `react@19.1.0` - UI framework
  - `lottie-react@2.4.1` - Animations
- **Port**: 5173 (development)

### Alternative Frontend (`frontend2/`)
- **Framework**: React 18 with TypeScript  
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Animation**: Motion library
- **Dependencies**:
  - `react@18.2.0` - UI framework
  - `motion@12.11.0` - Animations
  - `tailwindcss@3.4.3` - Styling
  - `lucide-react@0.383.0` - Icons
- **Port**: 3001 (development)

### Fancy Component Library (`fancy/`)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with Radix UI components
- **Animation**: Motion library, Matter.js physics
- **Documentation**: MDX with custom registry system
- **Build System**: Custom scripts for component registry and docs

## Development Commands

### Backend
```bash
# Quick start (automated)
./start-backend.sh

# Manual setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
# Primary frontend
./start-frontend.sh
# or manually: cd frontend && npm install && npm run dev

# Alternative frontend  
./start-frontend2.sh
# or manually: cd frontend2 && npm install && npm run dev

# Fancy component library
cd fancy && npm install && npm run dev
```

### Testing
- Backend testing files use pytest patterns (`test_*.py`)
- Integration tests available for category refresh and API endpoints
- Testing mode available for backend (uses cached Manhattan data)

## API Configuration
- **CORS**: Configured for localhost:5173 and localhost:3001
- **Google Maps APIs Required**:
  - Geocoding API (address to coordinates)
  - Places API (New) (nearby search and details)
  - Distance Matrix API (walking distances)
- **Rate Limiting**: Built-in delays and concurrent request management
- **Caching**: File-based caching system for search results

## Environment Setup
- Backend requires `GOOGLE_MAPS_API_KEY` in `.env` file
- All frontends connect to backend on `http://localhost:8000`
- Development servers auto-reload on file changes