import SwiftUI

struct LocationInputView: View {
    @Binding var location: String
    let onSearch: () -> Void
    
    var body: some View {
        HStack {
            Image(systemName: "location.fill")
                .foregroundColor(.blue)
            
            TextField("Enter a location...", text: $location)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .onSubmit {
                    onSearch()
                }
            
            Button(action: onSearch) {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.white)
                    .padding(8)
                    .background(Color.blue)
                    .cornerRadius(8)
            }
        }
        .padding(.horizontal)
    }
}

#Preview {
    LocationInputView(location: .constant("New York")) {
        print("Search tapped")
    }
} 