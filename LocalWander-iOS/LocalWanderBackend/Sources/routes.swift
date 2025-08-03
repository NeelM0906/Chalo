import Vapor
import Fluent

func routes(_ app: Application) throws {
    // Health check
    app.get { req async in
        return ["message": "Local Wander API - Backend Service"]
    }
    
    // API routes
    let apiGroup = app.grouped("api")
    
    // Get itineraries
    apiGroup.get("itineraries") { req async throws -> ItineraryResponse in
        guard let location = req.query[String.self, at: "location"] else {
            throw Abort(.badRequest, reason: "Location parameter is required")
        }
        
        let preset = req.query[String.self, at: "preset"]
        let priceFilter = req.query[String.self, at: "price_filter"]
        let distanceFilter = req.query[Double.self, at: "distance_filter"] ?? 1.5
        
        // Mock data for now - in a real app, this would query a database or external API
        let itineraries = generateMockItineraries(
            location: location,
            preset: preset,
            priceFilter: priceFilter,
            distanceFilter: distanceFilter
        )
        
        return ItineraryResponse(itineraries: itineraries)
    }
    
    // Refresh spot
    apiGroup.post("refresh-spot") { req async throws -> Stop in
        let request = try req.content.decode(RefreshSpotRequest.self)
        
        // Mock response - in a real app, this would query for alternatives
        let mockStop = generateMockStop(
            location: request.location,
            category: request.category,
            excludedIds: request.excludedIds
        )
        
        return mockStop
    }
}

// MARK: - Models

struct ItineraryResponse: Content {
    let itineraries: [Itinerary]
}

struct Itinerary: Content {
    let id: String
    let title: String
    let description: String
    let durationMinutes: Int
    let stops: [Stop]
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case description
        case durationMinutes = "duration_minutes"
        case stops
    }
}

struct Stop: Content {
    let id: String
    let name: String
    let category: String
    let walkingTimeMinutes: Int
    let description: String?
    let imageURL: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case category
        case walkingTimeMinutes = "walking_time_minutes"
        case description
        case imageURL = "image_url"
    }
}

struct RefreshSpotRequest: Content {
    let location: String
    let category: String
    let excludedIds: [String]
    
    enum CodingKeys: String, CodingKey {
        case location
        case category
        case excludedIds = "excluded_ids"
    }
}

// MARK: - Mock Data Generation

func generateMockItineraries(location: String, preset: String?, priceFilter: String?, distanceFilter: Double) -> [Itinerary] {
    let stockImages = [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1470&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1541167760496-1628856ab772?q=80&w=1637&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1472851294608-062f824d29cc?q=80&w=1470&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1469&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1544&auto=format&fit=crop"
    ]
    
    let categories = preset?.lowercased() == "food" ? ["Restaurant", "Cafe", "Bar"] :
                   preset?.lowercased() == "culture" ? ["Museum", "Gallery", "Theater"] :
                   preset?.lowercased() == "nature" ? ["Park", "Garden", "Trail"] :
                   preset?.lowercased() == "shopping" ? ["Boutique", "Market", "Mall"] :
                   preset?.lowercased() == "nightlife" ? ["Bar", "Club", "Lounge"] :
                   ["Restaurant", "Museum", "Park", "Cafe", "Gallery"]
    
    var itineraries: [Itinerary] = []
    
    for i in 1...3 {
        let stops = (1...3).map { stopIndex in
            let category = categories.randomElement() ?? "Restaurant"
            return Stop(
                id: "stop-\(i)-\(stopIndex)",
                name: "\(category) \(stopIndex) in \(location)",
                category: category,
                walkingTimeMinutes: Int.random(in: 5...15),
                description: "A great \(category.lowercased()) in \(location)",
                imageURL: stockImages.randomElement() ?? stockImages[0]
            )
        }
        
        let itinerary = Itinerary(
            id: "itinerary-\(i)",
            title: "\(preset ?? "Local") Adventure \(i) in \(location)",
            description: "Explore the best of \(location) with this curated itinerary",
            durationMinutes: stops.reduce(0) { $0 + $1.walkingTimeMinutes } + 30,
            stops: stops
        )
        
        itineraries.append(itinerary)
    }
    
    return itineraries
}

func generateMockStop(location: String, category: String, excludedIds: [String]) -> Stop {
    let stockImages = [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1470&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1541167760496-1628856ab772?q=80&w=1637&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1472851294608-062f824d29cc?q=80&w=1470&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1469&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1544&auto=format&fit=crop"
    ]
    
    return Stop(
        id: "stop-\(UUID().uuidString)",
        name: "Alternative \(category) in \(location)",
        category: category,
        walkingTimeMinutes: Int.random(in: 5...15),
        description: "This is an alternative \(category.lowercased()) spot in \(location).",
        imageURL: stockImages.randomElement() ?? stockImages[0]
    )
} 