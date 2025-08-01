import React from 'react';

interface TripHeaderProps {
  title: string;
  duration: number;
  location: string;
  onEndTrip: () => void;
}

const TripHeader: React.FC<TripHeaderProps> = ({ title, duration, location, onEndTrip }) => {
  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours} hr`;
    }
    return `${hours} hr ${remainingMinutes} min`;
  };

  const handleBackToHome = () => {
    window.location.hash = '#/';
  };

  return (
    <div className="bg-card border border-gray-600 rounded-lg p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-white mb-2">Your current trip</h1>
          <h2 className="text-xl text-accent mb-2">{title}</h2>
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 text-gray-300">
            <span className="text-sm">📍 {location}</span>
            <span className="hidden sm:inline text-gray-500">•</span>
            <span className="text-sm">⏱️ {formatDuration(duration)}</span>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            onClick={handleBackToHome}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-500 transition-colors"
          >
            Back to Home
          </button>
          <button
            onClick={onEndTrip}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-500 transition-colors"
          >
            End Trip
          </button>
        </div>
      </div>
    </div>
  );
};

export default TripHeader;