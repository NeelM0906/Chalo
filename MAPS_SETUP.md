# Google Maps Embed API Setup

## Enable the API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (the same one with your existing API key)
3. Go to **APIs & Services** > **Library**
4. Search for "Maps Embed API"
5. Click on "Maps Embed API" and click **Enable**

## API Key Configuration

Your existing Google Maps API key should work for the Maps Embed API. If you encounter issues:

1. Go to **APIs & Services** > **Credentials**
2. Click on your existing API key
3. Under **API restrictions**, make sure these APIs are enabled:
   - Maps Embed API ✓
   - Places API (New) ✓
   - Geocoding API ✓
   - Distance Matrix API ✓

## Testing

After enabling the API, restart your backend server and test the map embedding:

1. Restart backend: `./start-backend.sh`
2. Open frontend: `http://localhost:5173`
3. Search for a location
4. Click on any itinerary to open the detail modal
5. Scroll down to see the "Walking Route" map

## Troubleshooting

If you see "Error in map embedding process":
1. Check that Maps Embed API is enabled
2. Verify your API key has the correct permissions
3. Check browser console for specific error messages
4. Ensure your API key isn't restricted to specific domains (or add localhost to allowed domains)