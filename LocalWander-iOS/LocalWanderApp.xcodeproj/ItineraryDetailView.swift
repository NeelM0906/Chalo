import SwiftUI

struct ItineraryDetailView: View {
    let itinerary: Itinerary
    let location: String

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(itinerary.title)
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text(itinerary.description)
                    .font(.body)
                    .foregroundColor(.secondary)

                Text("Location: \(location)")
                    .font(.subheadline)
                    .foregroundColor(.blue)

                Divider()

                Text("Stops")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .padding(.bottom, 4)

                ForEach(itinerary.stops) { stop in
                    VStack(alignment: .leading, spacing: 6) {
                        Text(stop.name)
                            .font(.headline)
                        Text(stop.category)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        if let description = stop.description {
                            Text(description)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                        Text("Walking time: \(stop.walkingTimeMinutes) min")
                            .font(.caption2)
                            .foregroundColor(.gray)
                    }
                    .padding(.vertical, 6)
                    Divider()
                }
            }
            .padding()
        }
        .navigationTitle("Itinerary Details")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    let itinerary = Itinerary(
        id: "1",
        title: "Sample Adventure",
        description: "A fun adventure through your city.",
        durationMinutes: 90,
        stops: [
            Stop(id: "1", name: "Cafe", category: "Food", walkingTimeMinutes: 5, description: "A local cafe.", imageURL: ""),
            Stop(id: "2", name: "Park", category: "Nature", walkingTimeMinutes: 10, description: "A beautiful park.", imageURL: "")
        ]
    )
    ItineraryDetailView(itinerary: itinerary, location: "Downtown")
}
