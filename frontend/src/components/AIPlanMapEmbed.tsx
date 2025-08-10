import React, { useEffect, useState } from 'react';
import { AIDayPlanStop } from '../types';

interface AIPlanMapEmbedProps {
  stops: AIDayPlanStop[];
}

const AIPlanMapEmbed: React.FC<AIPlanMapEmbedProps> = ({ stops }) => {
  const [apiKey, setApiKey] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchApiKey = async () => {
      try {
        const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const resp = await fetch(`${base}/api/maps-config`);
        if (!resp.ok) throw new Error('maps-config failed');
        const data = await resp.json();
        if (data?.maps_api_key) setApiKey(data.maps_api_key);
        else throw new Error('no key');
      } catch {
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
        <h4 className="text-lg font-semibold mb-3 text-white">Route</h4>
        <div className="w-full h-80 bg-gray-800 rounded-lg flex items-center justify-center">
          <div className="text-gray-400">Loading map...</div>
        </div>
      </div>
    );
  }

  if (error || !apiKey) {
    return (
      <div className="mt-6">
        <h4 className="text-lg font-semibold mb-3 text-white">Route</h4>
        <div className="w-full h-80 bg-red-900/20 border border-red-700 rounded-lg flex items-center justify-center">
          <div className="text-red-300">Error in map embedding process</div>
        </div>
      </div>
    );
  }

  if (!Array.isArray(stops) || stops.length < 2) {
    return null;
  }

  const addrOrName = (s: AIDayPlanStop) => encodeURIComponent(s.address || s.name);

  const origin = addrOrName(stops[0]);
  const destination = addrOrName(stops[stops.length - 1]);
  const waypoints = stops.length > 2
    ? stops.slice(1, -1).map(addrOrName).join('|')
    : '';

  const src = `https://www.google.com/maps/embed/v1/directions?key=${apiKey}&origin=${origin}&destination=${destination}${waypoints ? `&waypoints=${waypoints}` : ''}&mode=walking&zoom=15`;

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold mb-3 text-white">Route</h4>
      <div className="w-full h-80 rounded-lg overflow-hidden border border-gray-700">
        <iframe
          width="100%"
          height="100%"
          frameBorder={0}
          style={{ border: 0 }}
          referrerPolicy="no-referrer-when-downgrade"
          src={src}
          allowFullScreen
          title="AI Plan Walking Directions"
        />
      </div>
    </div>
  );
};

export default AIPlanMapEmbed;


