import React from 'react';
import { Stop } from '../types';
import { useFavorites } from '../context/FavoritesContext';
import { ClockIcon, HeartIcon, LogoIcon } from './icons';

interface TripItineraryProps {
  stops: Stop[];
  location: string;
}

const TripItinerary: React.FC<TripItineraryProps> = ({ stops, location }) => {
  const { addFavorite, removeFavorite, isFavorite } = useFavorites();

  const handleFavoriteToggle = (stop: Stop) => {
    if (isFavorite(stop.id)) {
      removeFavorite(stop.id);
    } else {
      addFavorite(stop);
    }
  };

  const formatWalkingTime = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min walk`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours} hr walk`;
    }
    return `${hours} hr ${remainingMinutes} min walk`;
  };

  return (
    <div className="space-y-4">
      {stops.map((stop, index) => (
        <div key={stop.id} className="bg-card border border-gray-600 rounded-lg overflow-hidden">
          <div className="flex flex-col md:flex-row">
            {/* Image Section */}
            <div className="w-full md:w-1/3 h-48 md:h-auto bg-secondary flex items-center justify-center overflow-hidden">
              {stop.image_url ? (
                <img 
                  src={stop.image_url} 
                  alt={stop.name} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-800">
                  <LogoIcon className="w-16 h-16 text-gray-600" />
                </div>
              )}
            </div>

            {/* Content Section */}
            <div className="flex-1 p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-accent text-primary text-xs font-bold px-2 py-1 rounded">
                      Stop {index + 1}
                    </span>
                    <span className="text-xs text-gray-400 uppercase tracking-wide">
                      {stop.category}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{stop.name}</h3>
                </div>
                <button
                  onClick={() => handleFavoriteToggle(stop)}
                  className={`p-2 rounded-full transition-colors ${
                    isFavorite(stop.id)
                      ? 'text-red-500 hover:text-red-400'
                      : 'text-gray-400 hover:text-red-500'
                  }`}
                  aria-label={isFavorite(stop.id) ? 'Remove from favorites' : 'Add to favorites'}
                >
                  <HeartIcon 
                    className={`w-6 h-6 ${isFavorite(stop.id) ? 'fill-current' : ''}`} 
                  />
                </button>
              </div>

              {stop.description && (
                <p className="text-gray-300 mb-4 text-sm leading-relaxed">
                  {stop.description}
                </p>
              )}

              {/* Walking Time */}
              {stop.walking_time_minutes > 0 && (
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <ClockIcon className="w-4 h-4 text-accent" />
                  <span>{formatWalkingTime(stop.walking_time_minutes)}</span>
                  {index < stops.length - 1 && (
                    <span className="text-gray-500">to next stop</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TripItinerary;