import SwiftUI

struct ItineraryCard: View {
    let itinerary: Itinerary
    let onSelect: () -> Void
    @EnvironmentObject var favoritesManager: FavoritesManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header with image
            ZStack(alignment: .topTrailing) {
                AsyncImage(url: URL(string: itinerary.stops.first?.imageURL ?? "")) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                }
                .frame(height: 150)
                .clipped()
                .cornerRadius(12)
                
                // Favorite button for first stop
                if let firstStop = itinerary.stops.first {
                    Button(action: {
                        if favoritesManager.isFavorite(firstStop) {
                            favoritesManager.removeFavorite(firstStop)
                        } else {
                            favoritesManager.addFavorite(firstStop)
                        }
                    }) {
                        Image(systemName: favoritesManager.isFavorite(firstStop) ? "heart.fill" : "heart")
                            .foregroundColor(favoritesManager.isFavorite(firstStop) ? .red : .white)
                            .padding(8)
                            .background(Color.black.opacity(0.3))
                            .clipShape(Circle())
                    }
                    .padding(8)
                }
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text(itinerary.title)
                    .font(.title3)
                    .fontWeight(.bold)
                    .lineLimit(2)
                
                Text(itinerary.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
                
                HStack {
                    Image(systemName: "clock")
                        .font(.caption)
                    Text("\(itinerary.durationMinutes) min")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text("\(itinerary.stops.count) stops")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Button(action: onSelect) {
                    Text("View Details")
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.blue)
                        .cornerRadius(8)
                }
            }
            .padding(.horizontal, 12)
            .padding(.bottom, 12)
        }
        .background(Color(.systemBackground))
        .cornerRadius(16)
        .shadow(radius: 4)
    }
}

#Preview {
    ItineraryCard(
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
                )
            ]
        ),
        onSelect: {}
    )
    .environmentObject(FavoritesManager())
    .padding()
} 