import Foundation

// Shared models between iOS app and backend
// These ensure consistency in data structures

public struct SharedStop: Codable, Identifiable, Hashable {
    public let id: String
    public let name: String
    public let category: String
    public let walkingTimeMinutes: Int
    public let description: String?
    public let imageURL: String
    
    public init(id: String, name: String, category: String, walkingTimeMinutes: Int, description: String?, imageURL: String) {
        self.id = id
        self.name = name
        self.category = category
        self.walkingTimeMinutes = walkingTimeMinutes
        self.description = description
        self.imageURL = imageURL
    }
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case category
        case walkingTimeMinutes = "walking_time_minutes"
        case description
        case imageURL = "image_url"
    }
}

public struct SharedItinerary: Codable, Identifiable {
    public let id: String
    public let title: String
    public let description: String
    public let durationMinutes: Int
    public let stops: [SharedStop]
    
    public init(id: String, title: String, description: String, durationMinutes: Int, stops: [SharedStop]) {
        self.id = id
        self.title = title
        self.description = description
        self.durationMinutes = durationMinutes
        self.stops = stops
    }
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case description
        case durationMinutes = "duration_minutes"
        case stops
    }
}

public struct SharedItineraryResponse: Codable {
    public let itineraries: [SharedItinerary]
    
    public init(itineraries: [SharedItinerary]) {
        self.itineraries = itineraries
    }
}

public struct SharedRefreshSpotRequest: Codable {
    public let location: String
    public let category: String
    public let excludedIds: [String]
    
    public init(location: String, category: String, excludedIds: [String]) {
        self.location = location
        self.category = category
        self.excludedIds = excludedIds
    }
    
    enum CodingKeys: String, CodingKey {
        case location
        case category
        case excludedIds = "excluded_ids"
    }
} 