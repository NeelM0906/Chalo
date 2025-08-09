import SwiftUI

struct HomeView: View {
    @StateObject private var apiService = APIService()
    @EnvironmentObject var favoritesManager: FavoritesManager
    
    @State private var location = ""
    @State private var itineraries: [Itinerary] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var selectedPreset: String?
    @State private var priceFilter = ""
    @State private var distanceFilter: Double = 1.5
    @State private var selectedItinerary: Itinerary?
    
    private let presets = ["Food", "Culture", "Nature", "Shopping", "Nightlife"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    VStack(spacing: 12) {
                        Text("Rediscover Your Neighborhood")
                            .font(.largeTitle)
                            .fontWeight(.black)
                            .multilineTextAlignment(.center)
                        
                        Text("Enter a location to instantly generate hyper-local micro-adventures.")
                            .font(.title3)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.horizontal)
                    
                    // Location Input
                    LocationInputView(location: $location, onSearch: performSearch)
                    
                    // Filters
                    VStack(spacing: 12) {
                        HStack {
                            Text("Price Range:")
                                .fontWeight(.medium)
                            Spacer()
                            Picker("Price", selection: $priceFilter) {
                                Text("Any").tag("")
                                Text("Budget").tag("budget")
                                Text("Mid-range").tag("mid")
                                Text("Luxury").tag("luxury")
                            }
                            .pickerStyle(MenuPickerStyle())
                        }
                        
                        HStack {
                            Text("Distance: \(String(format: "%.1f", distanceFilter)) km")
                                .fontWeight(.medium)
                            Spacer()
                            Slider(value: $distanceFilter, in: 0.5...5.0, step: 0.1)
                                .frame(width: 150)
                        }
                    }
                    .padding(.horizontal)
                    
                    // Preset Buttons
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(presets, id: \.self) { preset in
                                Button(action: {
                                    selectedPreset = preset
                                    performSearch()
                                }) {
                                    Text(preset)
                                        .fontWeight(.medium)
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 8)
                                        .background(selectedPreset == preset ? Color.blue : Color.gray.opacity(0.2))
                                        .foregroundColor(selectedPreset == preset ? .white : .primary)
                                        .cornerRadius(20)
                                }
                                .disabled(isLoading)
                            }
                        }
                        .padding(.horizontal)
                    }
                    
                    // Error Message
                    if let errorMessage = errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .padding()
                    }
                    
                    // Loading State
                    if isLoading {
                        VStack(spacing: 16) {
                            ProgressView()
                                .scaleEffect(1.5)
                            Text("Discovering your next adventure...")
                                .font(.title3)
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity, minHeight: 200)
                    }
                    
                    // Results
                    if !isLoading && !itineraries.isEmpty && errorMessage == nil {
                        LazyVStack(spacing: 16) {
                            ForEach(itineraries) { itinerary in
                                ItineraryCard(itinerary: itinerary, onSelect: { selectedItinerary = itinerary })
                            }
                        }
                        .padding(.horizontal)
                    }
                }
            }
            .navigationTitle("Chalo")
            .navigationBarTitleDisplayMode(.large)
        }
        .sheet(item: $selectedItinerary) { itinerary in
            ItineraryDetailView(itinerary: itinerary, location: location)
        }
    }
    
    private func performSearch() {
        guard !location.isEmpty else {
            errorMessage = "Please enter a location"
            return
        }
        
        isLoading = true
        errorMessage = nil
        itineraries = []
        
        Task {
            do {
                let results = try await apiService.getItineraries(
                    location: location,
                    preset: selectedPreset,
                    priceFilter: priceFilter.isEmpty ? nil : priceFilter,
                    distanceFilter: distanceFilter
                )
                
                await MainActor.run {
                    self.itineraries = results
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                    self.isLoading = false
                }
            }
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(FavoritesManager())
} 