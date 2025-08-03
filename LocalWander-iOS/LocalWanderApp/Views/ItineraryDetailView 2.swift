import SwiftUI

struct ItineraryDetailView: View {
    let itinerary: Itinerary
    let location: String
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text(itinerary.title)
                        .font(.title)
                        .fontWeight(.bold)
                        .padding(.bottom, 4)
                    
                    Text("Near: \(location)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .padding(.bottom)
                    
                    Text(itinerary.description)
                        .font(.body)
                        .padding(.bottom)
                    
                    Divider()
                    
                    ForEach(itinerary.stops) { stop in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(stop.name)
                                .font(.headline)
                            Text(stop.description ?? "No description available")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                        .padding(.vertical, 8)
                    }
                }
                .padding()
            }
            .navigationTitle(itinerary.title)
            .navigationBarTitleDisplayMode(.inline)
        }
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
                )
            ]
        ),
        location: "New York"
    )
}
