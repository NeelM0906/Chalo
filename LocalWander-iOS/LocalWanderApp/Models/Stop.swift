import Foundation

struct Stop: Identifiable, Codable, Hashable {
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
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: Stop, rhs: Stop) -> Bool {
        lhs.id == rhs.id
    }
} 