
import React, { useState } from 'react';
import { CompassIcon, WanderingEyesIcon } from './icons';

interface LocationInputProps {
  onSearch: (location: string) => void;
  isLoading: boolean;
}

const LocationInput: React.FC<LocationInputProps> = ({ onSearch, isLoading }) => {
  const [inputValue, setInputValue] = useState('');
  const [geoError, setGeoError] = useState<string | null>(null);
  const [isGeoLoading, setIsGeoLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(inputValue);
  };

  const reverseGeocode = async (lat: number, lng: number): Promise<string> => {
    try {
      // Fetch Google Maps API key from backend
      const configResponse = await fetch('/api/maps-config');
      if (!configResponse.ok) {
        throw new Error('Failed to get API configuration');
      }
      const config = await configResponse.json();
      const apiKey = config.maps_api_key;

      // Call Google Geocoding API
      const geocodeResponse = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${apiKey}`
      );

      if (!geocodeResponse.ok) {
        throw new Error('Geocoding request failed');
      }

      const geocodeData = await geocodeResponse.json();

      if (geocodeData.status !== 'OK' || !geocodeData.results.length) {
        throw new Error('No address found for your location');
      }

      // Return the formatted address
      return geocodeData.results[0].formatted_address;
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      throw new Error('Failed to get address from your location');
    }
  };

  const handleGeoLocate = () => {
    if (!navigator.geolocation) {
      setGeoError('Geolocation is not supported by your browser.');
      return;
    }

    setGeoError(null);
    setIsGeoLoading(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          console.log('Got GPS coordinates:', latitude, longitude);

          // Reverse geocode to get address
          const address = await reverseGeocode(latitude, longitude);
          console.log('Reverse geocoded address:', address);

          // Search with the real address
          onSearch(address);
        } catch (error) {
          console.error('Geolocation error:', error);
          setGeoError(error instanceof Error ? error.message : 'Failed to get your location');
        } finally {
          setIsGeoLoading(false);
        }
      },
      (error) => {
        setIsGeoLoading(false);
        let errorMessage = 'Failed to get your location.';

        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied. Please enable location permissions.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out.';
            break;
        }

        setGeoError(errorMessage);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  return (
    <div className="max-w-xl mx-auto">
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter a zip code or address..."
          disabled={isLoading}
          className="flex-grow w-full px-5 py-3 bg-card border border-gray-600 rounded-md focus:ring-2 focus:ring-accent focus:outline-none transition-all text-white placeholder-gray-400"
        />
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleGeoLocate}
            disabled={isLoading || isGeoLoading}
            className="p-3 bg-card border border-gray-600 rounded-md hover:bg-gray-700 disabled:opacity-50 transition-colors flex items-center justify-center"
            aria-label="Use my current location"
          >
            {isGeoLoading ? (
              <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <CompassIcon className="w-6 h-6 text-accent" />
            )}
          </button>
          <button
            type="submit"
            disabled={isLoading || !inputValue}
            className="w-full sm:w-auto px-6 py-3 bg-accent text-primary font-bold rounded-md hover:bg-cyan-300 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <WanderingEyesIcon className="w-8 h-4" />
            {isLoading ? 'Chaloing...' : 'Chalo'}
          </button>
        </div>
      </form>
      {geoError && <p className="text-red-400 text-sm mt-2 text-center">{geoError}</p>}
    </div>
  );
};

export default LocationInput;
