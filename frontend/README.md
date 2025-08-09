# Chalo Frontend

React TypeScript frontend for the Chalo application.

## Structure

- `src/components/` - React components (LocationInput, ItineraryCard, etc.)
- `src/context/` - React context providers (FavoritesContext)
- `src/services/` - API service layer (apiService.ts)
- `src/types.ts` - TypeScript type definitions
- `src/App.tsx` - Main application component
- `src/index.tsx` - Application entry point

## Key Components

- **LocationInput** - Search input for locations
- **ItineraryCard** - Display card for each itinerary
- **ItineraryDetailModal** - Detailed view modal
- **SourceList** - Shows sources used for recommendations
- **FavoritesContext** - Manages user's favorite stops

## Features Preserved

- Clean, modern UI with dark theme
- Responsive design
- Favorites system with localStorage persistence
- Modal interactions
- Loading states and error handling
- Source transparency

## Development

The frontend connects to the FastAPI backend running on `http://localhost:8000`. The Vite config includes a proxy to handle API requests during development.