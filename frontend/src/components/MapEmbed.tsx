import React, { useState, useEffect } from 'react';
import { Stop } from '../types';

interface MapEmbedProps {
  stops: Stop[];
  location: string;
}

const MapEmbed: React.FC<MapEmbedProps> = ({ stops, location }) => {
  const [apiKey, setApiKey] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Fetch API key from backend
    const fetchApiKey = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/maps-config`);
        if (response.ok) {
          const data = await response.json();
          setApiKey(data.maps_api_key);
        } else {
          setError('Error in map embedding process');
        }
      } catch (err) {
        setError('Error in map embedding process');
      } finally {
        setLoading(false);
      }
    };

    fetchApiKey();
  }, []);

  if (loading) {
    return (
      <div className="mt-6">
        <h4 className="text-lg font-semibold mb-3 text-white">Walking Route</h4>
        <div className="w-full h-96 bg-gray-800 rounded-lg flex items-center justify-center">
          <div className="text-gray-400">Loading map...</div>
        </div>
      </div>
    );
  }

  if (error || !apiKey) {
    return (
      <div className="mt-6">
        <h4 className="text-lg font-semibold mb-3 text-white">Walking Route</h4>
        <div className="w-full h-96 bg-red-900/20 border border-red-700 rounded-lg flex items-center justify-center">
          <div className="text-red-300">Error in map embedding process</div>
        </div>
      </div>
    );
  }

  if (stops.length < 2) {
    return (
      <div className="mt-6">
        <h4 className="text-lg font-semibold mb-3 text-white">Walking Route</h4>
        <div className="w-full h-96 bg-gray-800 rounded-lg flex items-center justify-center">
          <div className="text-gray-400">Need at least 2 stops to show directions</div>
        </div>
      </div>
    );
  }

  // Build directions URL
  const origin = encodeURIComponent(`${stops[0].name}, ${location}`);
  const destination = encodeURIComponent(`${stops[stops.length - 1].name}, ${location}`);
  
  // Create waypoints from middle stops (if any)
  const waypoints = stops.length > 2 
    ? stops.slice(1, -1).map(stop => encodeURIComponent(`${stop.name}, ${location}`)).join('|')
    : '';

  const mapUrl = `https://www.google.com/maps/embed/v1/directions?key=${apiKey}&origin=${origin}&destination=${destination}${waypoints ? `&waypoints=${waypoints}` : ''}&mode=walking&zoom=15`;

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold mb-3 text-white">Walking Route</h4>
      <div className="w-full h-96 rounded-lg overflow-hidden border border-gray-700">
        <iframe
          width="100%"
          height="100%"
          frameBorder="0"
          style={{ border: 0 }}
          referrerPolicy="no-referrer-when-downgrade"
          src={mapUrl}
          allowFullScreen
          title="Walking directions between stops"
          onError={() => setError('Error in map embedding process')}
        />
      </div>
      <div className="mt-2 text-sm text-gray-400">
        Walking directions from {stops[0].name} to {stops[stops.length - 1].name}
        {stops.length > 2 && ` via ${stops.length - 2} stop${stops.length > 3 ? 's' : ''}`}
      </div>
    </div>
  );
};

export default MapEmbed;