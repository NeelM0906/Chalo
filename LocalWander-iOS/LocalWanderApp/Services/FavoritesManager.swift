import Foundation
import SwiftUI

class FavoritesManager: ObservableObject {
    @Published var favorites: [Stop] = []
    private let userDefaults = UserDefaults.standard
    private let favoritesKey = "favorites"
    
    init() {
        loadFavorites()
    }
    
    func addFavorite(_ stop: Stop) {
        if !favorites.contains(stop) {
            favorites.append(stop)
            saveFavorites()
        }
    }
    
    func removeFavorite(_ stop: Stop) {
        favorites.removeAll { $0.id == stop.id }
        saveFavorites()
    }
    
    func isFavorite(_ stop: Stop) -> Bool {
        favorites.contains(stop)
    }
    
    private func saveFavorites() {
        if let encoded = try? JSONEncoder().encode(favorites) {
            userDefaults.set(encoded, forKey: favoritesKey)
        }
    }
    
    private func loadFavorites() {
        if let data = userDefaults.data(forKey: favoritesKey),
           let decoded = try? JSONDecoder().decode([Stop].self, from: data) {
            favorites = decoded
        }
    }
} 