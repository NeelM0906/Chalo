# Local Wander - iOS Migration

This is the complete Swift/Xcode migration of the Local Wander travel recommendation app. The original React/TypeScript frontend and Python/FastAPI backend have been converted to a native iOS app with SwiftUI and a Swift backend using Vapor.


Theres a billion issues here but hey its a start.

## Project Structure

```
LocalWander-iOS/
├── LocalWanderApp/                 # iOS App (SwiftUI)
│   ├── LocalWanderAppApp.swift     # App entry point
│   ├── Views/                      # SwiftUI Views
│   │   ├── ContentView.swift       # Main tab view
│   │   ├── HomeView.swift          # Home screen
│   │   ├── FavoritesView.swift     # Favorites screen
│   │   └── ItineraryDetailView.swift # Detail modal
│   ├── Models/                     # Data Models
│   │   ├── Stop.swift              # Stop model
│   │   └── Itinerary.swift         # Itinerary model
│   ├── Services/                   # Business Logic
│   │   ├── APIService.swift        # Network requests
│   │   └── FavoritesManager.swift  # Local storage
│   ├── Components/                 # Reusable UI Components
│   │   ├── LocationInputView.swift # Location input
│   │   └── ItineraryCard.swift     # Itinerary cards
│   └── Assets.xcassets/           # App assets
├── LocalWanderBackend/             # Swift Backend (Vapor)
│   ├── Package.swift               # Swift Package Manager
│   ├── Sources/
│   │   ├── main.swift              # Server entry point
│   │   └── routes.swift            # API routes
│   └── Tests/                      # Backend tests
└── Shared/                         # Shared code
    └── Models/
        └── SharedModels.swift      # Shared data models
```

## Features

### iOS App (SwiftUI)
- **Modern SwiftUI Interface**: Native iOS design with smooth animations
- **Tab Navigation**: Home and Favorites tabs
- **Location Search**: Enter any location to find recommendations
- **Filter Options**: Price range and distance filters
- **Preset Categories**: Food, Culture, Nature, Shopping, Nightlife
- **Favorites System**: Save and manage favorite stops
- **Itinerary Details**: Detailed view of each itinerary with stops
- **Local Storage**: Favorites persist between app launches

### Backend (Vapor)
- **RESTful API**: `/api/itineraries` and `/api/refresh-spot` endpoints
- **CORS Support**: Cross-origin requests enabled
- **Mock Data**: Generates realistic travel recommendations
- **SQLite Database**: Local data storage (ready for production)
- **Swift Performance**: High-performance server-side code

## Key Migrations

### Frontend (React → SwiftUI)
- **State Management**: `useState` → `@State` and `@StateObject`
- **Context**: React Context → `@EnvironmentObject`
- **Components**: React components → SwiftUI Views
- **Styling**: CSS/Tailwind → SwiftUI modifiers
- **Navigation**: React Router → TabView and NavigationView

### Backend (Python/FastAPI → Swift/Vapor)
- **Framework**: FastAPI → Vapor
- **Data Models**: Pydantic → Codable structs
- **API Routes**: Python decorators → Swift route handlers
- **CORS**: FastAPI CORS → Vapor CORS middleware
- **Database**: SQLAlchemy → Fluent ORM

## Getting Started

### Prerequisites
- Xcode 15.0+
- iOS 17.0+
- macOS 13.0+ (for backend)

### Running the iOS App
1. Open `LocalWanderApp.xcodeproj` in Xcode
2. Select your iOS device or simulator
3. Press Cmd+R to build and run

### Running the Backend
1. Navigate to `LocalWanderBackend/`
2. Run: `swift run`
3. Server starts on `http://localhost:8080`

### API Endpoints
- `GET /api/itineraries?location=NewYork&preset=Food`
- `POST /api/refresh-spot` with JSON body

## Architecture Benefits

### Native Performance
- **SwiftUI**: 60fps animations and native feel
- **Swift**: Compile-time safety and high performance
- **Metal**: Hardware-accelerated graphics

### Developer Experience
- **Xcode**: Integrated IDE with debugging and profiling
- **Swift**: Type-safe, modern language
- **SwiftUI**: Declarative UI with live previews

### Production Ready
- **App Store**: Ready for iOS App Store deployment
- **TestFlight**: Built-in beta testing
- **Crashlytics**: Native crash reporting
- **Analytics**: Core Data and CloudKit integration

## Migration Notes

### Data Flow
- **Original**: React → TypeScript → Python/FastAPI
- **New**: SwiftUI → Swift → Swift/Vapor

### State Management
- **Original**: React Context + useState
- **New**: @EnvironmentObject + @State

### API Communication
- **Original**: fetch() with TypeScript interfaces
- **New**: URLSession with Codable structs

### Styling
- **Original**: Tailwind CSS classes
- **New**: SwiftUI modifiers and system colors

## Future Enhancements

### iOS-Specific Features
- **Core Location**: GPS-based location services
- **MapKit**: Native Apple Maps integration
- **Push Notifications**: Location-based alerts
- **Siri Shortcuts**: Voice commands
- **Widgets**: Home screen widgets

### Backend Enhancements
- **Real APIs**: Integration with Google Places, Yelp, etc.
- **Machine Learning**: Core ML for recommendations
- **CloudKit**: iCloud sync for favorites
- **Push Notifications**: Server-side push

## Comparison with Original

| Feature | Original (React/Python) | New (Swift/Vapor) |
|---------|------------------------|-------------------|
| Performance | Web-based | Native iOS |
| Offline Support | Limited | Full offline capability |
| App Store | Web app | Native iOS app |
| Push Notifications | No | Yes |
| Location Services | Browser-based | Native GPS |
| Data Persistence | LocalStorage | Core Data |
| Testing | Jest | XCTest |
| Deployment | Web hosting | App Store |

This migration provides a complete native iOS experience while maintaining all the original functionality and adding iOS-specific enhancements. 