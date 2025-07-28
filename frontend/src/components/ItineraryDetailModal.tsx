import React, { useState, useEffect } from 'react';
import { Itinerary, Stop } from '../types';
import { XIcon, ClockIcon, WalkIcon, MapPinIcon, HeartIcon, RefreshIcon } from './icons';
import { useFavorites } from '../context/FavoritesContext';
import { refreshSpot, refreshCategory } from '../services/apiService';
import RefreshButton from './RefreshButton';
import CategoryRefreshButton from './CategoryRefreshButton';
import MapEmbed from './MapEmbed';

interface ItineraryDetailModalProps {
  itinerary: Itinerary;
  onClose: () => void;
  location: string;
}

interface StopItemProps {
    stop: Stop;
    isLast: boolean;
    location: string;
    onRefresh: (stopId: string) => void;
    onCategoryRefresh: (stopId: string) => void;
    isRefreshing: boolean;
    isCategoryRefreshing: boolean;
}

const StopItem: React.FC<StopItemProps> = ({ stop, isLast, location, onRefresh, onCategoryRefresh, isRefreshing, isCategoryRefreshing }) => {
    const { addFavorite, removeFavorite, isFavorite } = useFavorites();
    const favorited = isFavorite(stop.id);

    const handleFavoriteClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (favorited) {
            removeFavorite(stop.id);
        } else {
            addFavorite(stop);
        }
    };
    
    const handleRefreshClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        onRefresh(stop.id);
    };

    const handleCategoryRefreshClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        onCategoryRefresh(stop.id);
    };

    const mapsQuery = encodeURIComponent(`${stop.name}, ${location}`);
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${mapsQuery}`;

    return (
    <div className="relative">
        <div className="flex items-start gap-4">
            <div className="flex flex-col items-center self-stretch">
                <div className="w-8 h-8 rounded-full bg-accent text-primary flex items-center justify-center font-bold flex-shrink-0 z-10">
                    <MapPinIcon className="w-5 h-5"/>
                </div>
                {!isLast && <div className="w-px h-full bg-gray-600 border border-dashed border-gray-600 absolute top-4 left-4 -z-0"></div>}
            </div>
            <div className="flex-1 pb-16">
                <div className="relative mb-4">
                    {stop.image_url && (
                        <img 
                            src={stop.image_url} 
                            alt={`Image of ${stop.name}`} 
                            className="w-full h-48 object-cover rounded-lg border border-gray-700"
                        />
                    )}
                    <div className="absolute top-2 right-2 flex gap-2">
                        <RefreshButton 
                            onClick={handleRefreshClick}
                            isLoading={isRefreshing}
                            size="sm"
                            disabled={isCategoryRefreshing}
                        />
                        <CategoryRefreshButton 
                            onClick={handleCategoryRefreshClick}
                            isLoading={isCategoryRefreshing}
                            size="sm"
                            disabled={isRefreshing}
                        />
                        <button 
                            onClick={handleFavoriteClick} 
                            className="p-2 rounded-full bg-black/40 hover:bg-black/60 transition-colors"
                            aria-label={favorited ? 'Remove from favorites' : 'Add to favorites'}
                        >
                            <HeartIcon className={`w-6 h-6 transition-all duration-200 ${favorited ? 'text-red-500 fill-current' : 'text-white stroke-current fill-none'}`} strokeWidth={favorited ? 0 : 2} />
                        </button>
                    </div>
                </div>
                <h4 className="font-bold text-lg text-white">
                    <a href={mapsUrl} target="_blank" rel="noopener noreferrer" className="hover:underline hover:text-accent transition-colors duration-200">
                        {stop.name}
                    </a>
                </h4>
                <div className="flex items-center gap-2">
                    <p className="text-sm text-accent font-semibold">{stop.category}</p>
                    <CategoryRefreshButton 
                        onClick={handleCategoryRefreshClick}
                        isLoading={isCategoryRefreshing}
                        size="sm"
                        disabled={isRefreshing}
                    />
                </div>
                <p className="mt-2 text-gray-300">{stop.description}</p>
            </div>
        </div>
        {!isLast && (
            <div className="flex items-center gap-2 -mt-12 mb-4 ml-[52px] text-gray-400">
                <WalkIcon className="w-4 h-4" />
                <span>{stop.walking_time_minutes} min walk from previous stop</span>
            </div>
        )}
    </div>
)};


const ItineraryDetailModal: React.FC<ItineraryDetailModalProps> = ({ itinerary, onClose, location }) => {
  const [stops, setStops] = useState<Stop[]>(itinerary.stops);
  const [refreshingStopId, setRefreshingStopId] = useState<string | null>(null);
  const [categoryRefreshingStopId, setCategoryRefreshingStopId] = useState<string | null>(null);
  const [seenSpotIds, setSeenSpotIds] = useState<string[]>(
    itinerary.stops.map(stop => stop.id)
  );
  const [excludedCategories, setExcludedCategories] = useState<string[]>([]);
  const [categoryExclusionTurns, setCategoryExclusionTurns] = useState<number>(0);
  const [currentLocation, setCurrentLocation] = useState<string>(location);
  const [error, setError] = useState<string | null>(null);
  const [totalDuration, setTotalDuration] = useState<number>(itinerary.duration_minutes);

  // Reset exclusions when location changes
  useEffect(() => {
    if (location !== currentLocation) {
      setExcludedCategories([]);
      setCategoryExclusionTurns(0);
      setCurrentLocation(location);
    }
  }, [location, currentLocation]);

  // Recalculate total duration when stops change
  useEffect(() => {
    const newDuration = stops.reduce((total, stop) => {
      return total + stop.walking_time_minutes + 30; // Assume 30 min per stop
    }, 0);
    setTotalDuration(newDuration);
  }, [stops]);
  
  const handleRefreshSpot = async (stopId: string) => {
    // Find the stop to refresh
    const stopToRefresh = stops.find(s => s.id === stopId);
    if (!stopToRefresh) return;
    
    setRefreshingStopId(stopId);
    setError(null);
    
    try {
      const newSpot = await refreshSpot(
        location, 
        stopToRefresh.category,
        seenSpotIds
      );
      
      // Update the stops array with the new spot
      setStops(currentStops => 
        currentStops.map(s => s.id === stopId ? newSpot : s)
      );
      
      // Add the new spot ID to seen spots
      setSeenSpotIds(ids => [...ids, newSpot.id]);
      
    } catch (error) {
      console.error('Failed to refresh spot:', error);
      setError(error instanceof Error ? error.message : 'Failed to refresh spot');
    } finally {
      setRefreshingStopId(null);
    }
  };

  const handleCategoryRefresh = async (stopId: string) => {
    // Find the stop to refresh
    const stopToRefresh = stops.find(s => s.id === stopId);
    if (!stopToRefresh) return;
    
    setCategoryRefreshingStopId(stopId);
    setError(null);
    
    try {
      const newSpot = await refreshCategory(
        location, 
        stopToRefresh.category,
        seenSpotIds
      );
      
      // Update the stops array with the new spot
      setStops(currentStops => 
        currentStops.map(s => s.id === stopId ? newSpot : s)
      );
      
      // Add the new spot ID to seen spots
      setSeenSpotIds(ids => [...ids, newSpot.id]);
      
      // Update exclusion tracking
      setExcludedCategories(current => {
        if (!current.includes(stopToRefresh.category)) {
          return [...current, stopToRefresh.category];
        }
        return current;
      });
      
      // Increment turn counter
      setCategoryExclusionTurns(current => {
        const newTurns = current + 1;
        // Reset exclusions after 5 turns
        if (newTurns >= 5) {
          setExcludedCategories([]);
          return 0;
        }
        return newTurns;
      });
      
    } catch (error) {
      console.error('Failed to refresh category:', error);
      let errorMessage = 'Failed to refresh category';
      
      if (error instanceof Error) {
        if (error.message.includes('No alternative categories available')) {
          errorMessage = 'All categories have been recently used. Try refreshing the same category instead, or search for a new location.';
        } else if (error.message.includes('Could not find alternative spots')) {
          errorMessage = 'No alternative spots found from different categories. Try refreshing the same category instead.';
        } else if (error.message.includes('No cached results found')) {
          errorMessage = 'Please search for itineraries first before refreshing categories.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setCategoryRefreshingStopId(null);
    }
  };
  
  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4 animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="itinerary-title"
    >
      <div 
        className="bg-secondary rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col border border-gray-700 shadow-2xl animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="p-6 border-b border-gray-700 flex justify-between items-center sticky top-0 bg-secondary z-10">
          <div>
            <h2 id="itinerary-title" className="text-2xl font-bold text-white">{itinerary.title}</h2>
            <div className="flex items-center gap-2 text-gray-400 text-sm mt-1">
                <ClockIcon className="w-4 h-4 text-accent" />
                <span>~{Math.round(totalDuration / 60 * 10) / 10} hours total</span>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-card" aria-label="Close modal">
            <XIcon className="w-6 h-6 text-gray-400"/>
          </button>
        </header>

        <div className="p-6 overflow-y-auto">
            <p className="text-gray-300 mb-8">{itinerary.description}</p>
            
            {error && (
              <div className="mb-6 p-3 bg-red-900/30 border border-red-700 rounded-md text-red-300">
                {error}
              </div>
            )}
            
            <div className="flex flex-col">
              {stops.map((stop, index) => (
                <StopItem 
                  key={stop.id} 
                  stop={stop} 
                  isLast={index === stops.length - 1} 
                  location={location}
                  onRefresh={handleRefreshSpot}
                  onCategoryRefresh={handleCategoryRefresh}
                  isRefreshing={refreshingStopId === stop.id}
                  isCategoryRefreshing={categoryRefreshingStopId === stop.id}
                />
              ))}
            </div>
            
            {/* Embedded Map showing walking directions */}
            <MapEmbed stops={stops} location={location} />
        </div>
      </div>
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slide-up {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        .animate-fade-in { animation: fade-in 0.3s ease-out forwards; }
        .animate-slide-up { animation: slide-up 0.4s ease-out forwards; }
      `}</style>
    </div>
  );
};

export default ItineraryDetailModal;