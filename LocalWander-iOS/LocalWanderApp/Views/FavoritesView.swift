import SwiftUI

struct FavoritesView: View {
    @EnvironmentObject var favoritesManager: FavoritesManager
    
    var body: some View {
        NavigationView {
            Group {
                if favoritesManager.favorites.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "heart.slash")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No adventures saved yet")
                            .font(.title2)
                            .fontWeight(.semibold)
                        
                        Text("Go explore and like some stops to see them here!")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollView {
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            ForEach(favoritesManager.favorites) { stop in
                                FavoriteStopCard(stop: stop)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("My Saved Adventures")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

struct FavoriteStopCard: View {
    let stop: Stop
    @EnvironmentObject var favoritesManager: FavoritesManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            AsyncImage(url: URL(string: stop.imageURL)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
            }
            .frame(height: 120)
            .clipped()
            .cornerRadius(8)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(stop.name)
                    .font(.headline)
                    .lineLimit(2)
                
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
                    
                    Spacer()
                    
                    Button(action: {
                        favoritesManager.removeFavorite(stop)
                    }) {
                        Image(systemName: "heart.fill")
                            .foregroundColor(.red)
                    }
                }
            }
            .padding(.horizontal, 8)
            .padding(.bottom, 8)
        }
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

#Preview {
    FavoritesView()
        .environmentObject(FavoritesManager())
} 