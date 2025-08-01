# Design Document

## Overview

This design implements two key improvements to the LocalWander application:
1. A simple text change from "Wander" to "Chalo" in the search button
2. A comprehensive trip start feature that creates a dedicated, focused experience for users following a selected itinerary

The trip start feature introduces a new route and component architecture that maintains the existing modal-based itinerary viewing while adding a dedicated trip mode.

## Architecture

### Component Structure
```
App.tsx (existing)
├── HomePage (existing)
├── FavoritesPage (existing) 
├── WanderBuddiesPage (existing)
└── TripPage (new)
    ├── TripHeader (new)
    ├── TripItinerary (new)
    └── MapEmbed (existing, reused)
```

### Routing Enhancement
The existing hash-based routing system will be extended to support:
- `#/` - Home page (existing)
- `#/favorites` - Favorites page (existing)
- `#/buddies` - Wander buddies page (existing)
- `#/trip` - Active trip page (new)

### State Management
A new trip context will be created to manage:
- Current active trip data
- Trip start/stop functionality
- Trip persistence across navigation

## Components and Interfaces

### 1. Button Text Update

**LocationInput Component Changes:**
- Update button text from "Wander" to "Chalo"
- Update loading text from "Wandering..." to "Chaloing..."
- Maintain all existing functionality and styling

### 2. Trip Context (New)

```typescript
interface TripContextType {
  currentTrip: Itinerary | null;
  startTrip: (itinerary: Itinerary, location: string) => void;
  endTrip: () => void;
  tripLocation: string | null;
}
```

**Responsibilities:**
- Store current active trip data
- Provide trip management functions
- Persist trip data in localStorage
- Handle trip state across app navigation

### 3. TripPage Component (New)

**Props:**
```typescript
interface TripPageProps {
  // No props needed - uses trip context
}
```

**Features:**
- Display "Your current trip" header
- Show complete itinerary with stops
- Include embedded map
- Provide navigation back to main app
- Handle case when no trip is active

### 4. TripHeader Component (New)

**Props:**
```typescript
interface TripHeaderProps {
  title: string;
  duration: number;
  location: string;
  onEndTrip: () => void;
}
```

**Features:**
- Display trip title and duration
- Show location information
- Provide "End Trip" functionality
- Include navigation back to home

### 5. TripItinerary Component (New)

**Props:**
```typescript
interface TripItineraryProps {
  stops: Stop[];
  location: string;
}
```

**Features:**
- Display all stops in trip format
- Show walking times and directions
- Include stop images and descriptions
- Maintain favorite functionality
- Exclude refresh functionality (trip mode is for following, not modifying)

### 6. ItineraryDetailModal Enhancement

**New Features:**
- Add "Start this trip" button at bottom of modal
- Button triggers trip start functionality
- Button styled consistently with existing design
- Button positioned after map embed

## Data Models

### Trip Storage
```typescript
interface StoredTrip {
  itinerary: Itinerary;
  location: string;
  startedAt: string; // ISO timestamp
}
```

**localStorage key:** `localwander_current_trip`

### Enhanced Routing State
```typescript
type AppRoute = '#/' | '#/favorites' | '#/buddies' | '#/trip';
```

## Error Handling

### Trip Context Errors
- Handle localStorage access failures
- Gracefully handle corrupted trip data
- Provide fallback when trip data is invalid

### TripPage Error States
- Display message when no active trip exists
- Provide navigation back to home page
- Handle missing trip data gracefully

### Navigation Errors
- Ensure proper fallback to home page
- Handle invalid route states
- Maintain app stability during route changes

## Testing Strategy

### Unit Tests
1. **LocationInput Component**
   - Verify button text displays "Chalo"
   - Verify loading text displays "Chaloing..."
   - Test button disabled states

2. **Trip Context**
   - Test trip start functionality
   - Test trip end functionality
   - Test localStorage persistence
   - Test data retrieval and validation

3. **TripPage Component**
   - Test rendering with active trip
   - Test rendering without active trip
   - Test navigation functionality

### Integration Tests
1. **Trip Flow**
   - Test complete flow from itinerary selection to trip start
   - Test navigation between trip page and other pages
   - Test trip persistence across browser refresh

2. **Modal Integration**
   - Test "Start this trip" button functionality
   - Test modal closure after trip start
   - Test trip context updates

### User Experience Tests
1. **Button Text Update**
   - Verify visual consistency with existing design
   - Test accessibility of updated button text

2. **Trip Experience**
   - Test trip page layout and usability
   - Verify map functionality in trip mode
   - Test responsive design on mobile devices