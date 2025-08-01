# Product Overview

**Chalo** (formerly Local Wander) is a hyper-local travel discovery application that generates spontaneous micro-adventures and itineraries for any location. The product helps users rediscover their neighborhoods and explore new areas through AI-powered recommendations.

## Core Features

- **Mixed Itineraries**: Default mode that creates naturally varied adventures with diverse place types
- **Preset Category Filters**: Focused adventures in Nature, Food, Culture, Shopping, or History
- **Location-based Discovery**: Enter any location to get local adventure suggestions within customizable radius (default 1.5 miles)
- **Detailed Itineraries**: Multi-stop journeys with categories, walking times, descriptions, and ratings
- **Real-time Refresh**: Users can refresh individual spots or swap categories for variety
- **Favorites System**: Save and manage favorite spots across adventures
- **Source Transparency**: Shows data sources used for recommendations

## Architecture

The application uses a **modular three-tier architecture**:
- **Frontend**: React TypeScript applications with multiple UI variants
- **Backend**: Python FastAPI service with Google Maps API integration
- **Search Engine**: Custom LocalWander engine for place discovery and itinerary generation

## Target Use Cases

- Spontaneous local exploration
- Tourist discovery in new cities
- Neighborhood rediscovery for residents
- Curated adventures by interest category
- Walking-distance micro-adventures