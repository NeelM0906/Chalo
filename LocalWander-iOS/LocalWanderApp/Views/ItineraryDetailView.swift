import SwiftUI

struct ItineraryDetailView: View {
    let itinerary: Itinerary
    let location: String
    @EnvironmentObject var favoritesManager: FavoritesManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header Image
                    AsyncImage(url: URL(string: itinerary.stops.first?.imageURL ?? "")) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                    }
                    .frame(height: 200)
                    .clipped()
                    
                    VStack(alignment: .leading, spacing: 16) {
                        // Title and Description
                        VStack(alignment: .leading, spacing: 8) {
                            Text(itinerary.title)
                                .font(.title)
                                .fontWeight(.bold)
                            
                            Text(itinerary.description)
                                .font(.body)
                                .foregroundColor(.secondary)
                            
                            HStack {
                                Image(systemName: "clock")
                                Text("\(itinerary.durationMinutes) minutes")
                                
                                Spacer()
                                
                                Image(systemName: "location")
                                Text(location)
                            }
                            .font(.caption)
                            .foregroundColor(.secondary)
                        }
                        
                        Divider()
                        
                        // Stops List
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Stops")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            ForEach(Array(itinerary.stops.enumerated()), id: \.element.id) { index, stop in
                                StopRow(stop: stop, index: index + 1)
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Itinerary Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct StopRow: View {
    let stop: Stop
    let index: Int
    @EnvironmentObject var favoritesManager: FavoritesManager
    
    var body: some View {
        HStack(spacing: 12) {
            // Stop number
            ZStack {
                Circle()
                    .fill(Color.blue)
                    .frame(width: 30, height: 30)
                
                Text("\(index)")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
            }
            
            // Stop image
            AsyncImage(url: URL(string: stop.imageURL)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
            }
            .frame(width: 60, height: 60)
            .clipped()
            .cornerRadius(8)
            
            // Stop details
            VStack(alignment: .leading, spacing: 4) {
                Text(stop.name)
                    .font(.headline)
                    .lineLimit(1)
                
                Text(stop.category)
                    .font(.caption)
                    .foregroundColor(.blue)
                    .fontWeight(.medium)
                
                if let description = stop.description {
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                
                HStack {
                    Image(systemName: "clock")
                        .font(.caption)
                    Text("\(stop.walkingTimeMinutes) min")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            // Favorite button
            Button(action: {
                if favoritesManager.isFavorite(stop) {
                    favoritesManager.removeFavorite(stop)
                } else {
                    favoritesManager.addFavorite(stop)
                }
            }) {
                Image(systemName: favoritesManager.isFavorite(stop) ? "heart.fill" : "heart")
                    .foregroundColor(favoritesManager.isFavorite(stop) ? .red : .gray)
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    ItineraryDetailView(
        itinerary: Itinerary(
            id: "1",
            title: "Downtown Food Tour",
            description: "Explore the best local eateries in downtown",
            durationMinutes: 120,
            stops: [
                Stop(
                    id: "1",
                    name: "Local Cafe",
                    category: "Food",
                    walkingTimeMinutes: 5,
                    description: "Cozy local cafe",
                    imageURL: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4"
                ),
                Stop(
                    id: "2",
                    name: "Art Gallery",
                    category: "Culture",
                    walkingTimeMinutes: 10,
                    description: "Contemporary art space",
                    imageURL: "https://images.unsplash.com/photo-1541167760496-1628856ab772"
                )
            ]
        ),
        location: "New York"
    )
    .environmentObject(FavoritesManager())
} 