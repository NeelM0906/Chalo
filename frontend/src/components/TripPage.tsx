import React from 'react';
import { useTrip } from '../context/TripContext';
import TripHeader from './TripHeader';
import TripItinerary from './TripItinerary';
import MapEmbed from './MapEmbed';

const TripPage: React.FC = () => {
  const { currentTrip, tripLocation, endTrip } = useTrip();

  const handleEndTrip = () => {
    endTrip();
    // Navigate back to home page
    window.location.hash = '#/';
  };

  // Handle case when no active trip exists
  if (!currentTrip || !tripLocation) {
    return (
      <div className="min-h-screen bg-primary text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto text-center">
            <h1 className="text-3xl font-bold mb-4">No Active Trip</h1>
            <p className="text-gray-400 mb-6">
              You don't have an active trip. Start a trip by selecting an itinerary from the home page.
            </p>
            <button
              onClick={() => window.location.hash = '#/'}
              className="px-6 py-3 bg-accent text-primary font-bold rounded-md hover:bg-cyan-300 transition-colors"
            >
              Go to Home Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Trip Header */}
          <TripHeader
            title={currentTrip.title}
            duration={currentTrip.duration_minutes}
            location={tripLocation}
            onEndTrip={handleEndTrip}
          />

          {/* Trip Itinerary */}
          <div className="mb-8">
            <TripItinerary
              stops={currentTrip.stops}
              location={tripLocation}
            />
          </div>

          {/* Map Embed */}
          <div className="bg-card border border-gray-600 rounded-lg p-6">
            <MapEmbed
              stops={currentTrip.stops}
              location={tripLocation}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripPage;