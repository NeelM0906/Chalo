import Foundation
import Combine

class APIService: ObservableObject {
    private let baseURL = "http://localhost:8000"
    
    func getItineraries(location: String, preset: String? = nil, priceFilter: String? = nil, distanceFilter: Double = 1.5) async throws -> [Itinerary] {
        var components = URLComponents(string: "\(baseURL)/api/itineraries")!
        
        var queryItems = [URLQueryItem(name: "location", value: location)]
        if let preset = preset {
            queryItems.append(URLQueryItem(name: "preset", value: preset))
        }
        if let priceFilter = priceFilter {
            queryItems.append(URLQueryItem(name: "price_filter", value: priceFilter))
        }
        queryItems.append(URLQueryItem(name: "distance_filter", value: String(distanceFilter)))
        
        components.queryItems = queryItems
        
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        
        let request = URLRequest(url: url)
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.serverError
        }
        
        let decoder = JSONDecoder()
        let result = try decoder.decode(ItineraryResponse.self, from: data)
        return result.itineraries
    }
    
    func refreshSpot(location: String, category: String, excludedIds: [String] = []) async throws -> Stop {
        let url = URL(string: "\(baseURL)/api/refresh-spot")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = RefreshSpotRequest(location: location, category: category, excludedIds: excludedIds)
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.serverError
        }
        
        let decoder = JSONDecoder()
        return try decoder.decode(Stop.self, from: data)
    }
}

struct ItineraryResponse: Codable {
    let itineraries: [Itinerary]
}

struct RefreshSpotRequest: Codable {
    let location: String
    let category: String
    let excludedIds: [String]
    
    enum CodingKeys: String, CodingKey {
        case location
        case category
        case excludedIds = "excluded_ids"
    }
}

enum APIError: Error, LocalizedError {
    case invalidURL
    case serverError
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .serverError:
            return "Server error occurred"
        case .decodingError:
            return "Failed to decode response"
        }
    }
} 