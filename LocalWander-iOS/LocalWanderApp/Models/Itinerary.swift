import Foundation

struct Itinerary: Identifiable, Codable {
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