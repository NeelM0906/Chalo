import SwiftUI

struct ContentView: View {
    @StateObject private var favoritesManager = FavoritesManager()
    
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("Home")
                }
            
            FavoritesView()
                .tabItem {
                    Image(systemName: "heart.fill")
                    Text("Favorites")
                }
        }
        .environmentObject(favoritesManager)
    }
}

#Preview {
    ContentView()
} 