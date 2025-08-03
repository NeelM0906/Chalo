// Ensure this file is added to your main app target (File Inspector > Target Membership). If you see 'Cannot find ... in scope' errors, try cleaning the build (Shift+Cmd+K) and rebuilding (Cmd+B).

import SwiftUI

struct ItineraryDetailView: View {
    var body: some View {
        Text("Itinerary Details")
            .font(.largeTitle)
            .padding()
    }
}

struct ItineraryDetailView_Previews: PreviewProvider {
    static var previews: some View {
        ItineraryDetailView()
    }
}
