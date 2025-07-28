import React from 'react';
import { Itinerary } from '../types';
import { ClockIcon, MapPinIcon, LogoIcon } from './icons';

interface ItineraryCardProps {
  itinerary: Itinerary;
  onSelect: (itinerary: Itinerary) => void;
}

const ItineraryCard: React.FC<ItineraryCardProps> = ({ itinerary, onSelect }) => {
  const totalStops = itinerary.stops.length;
  const imageUrl = itinerary.stops?.[0]?.image_url;

  return (
    <div 
      className="bg-card rounded-lg border border-gray-700 hover:border-accent transition-all duration-300 cursor-pointer transform hover:-translate-y-1 group flex flex-col overflow-hidden"
      onClick={() => onSelect(itinerary)}
      role="button"
      tabIndex={0}
      aria-label={`View details for ${itinerary.title}`}
      onKeyPress={(e) => (e.key === 'Enter' || e.key === ' ') && onSelect(itinerary)}
    >
      <div className="w-full h-48 bg-secondary flex items-center justify-center overflow-hidden">
        {imageUrl ? (
          <img src={imageUrl} alt={itinerary.title} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-800">
            <LogoIcon className="w-16 h-16 text-gray-600" />
          </div>
        )}
      </div>
      <div className="p-6 flex flex-col flex-grow">
        <h3 className="text-xl font-bold text-white tracking-tight mb-2 group-hover:text-accent transition-colors">{itinerary.title}</h3>
        <p className="text-gray-400 mb-4 text-sm flex-grow">{itinerary.description}</p>
        
        <div className="flex items-center justify-between text-sm text-gray-300 border-t border-gray-700 pt-4 mt-auto">
          <div className="flex items-center gap-2">
            <ClockIcon className="w-5 h-5 text-accent" />
            <span>~{Math.round(itinerary.duration_minutes / 60 * 10) / 10} hours</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPinIcon className="w-5 h-5 text-accent" />
            <span>{totalStops} stops</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ItineraryCard;
