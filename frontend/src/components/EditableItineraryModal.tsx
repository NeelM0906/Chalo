import React, { useState, useEffect } from 'react';
import { Itinerary, Stop } from '../types';
import { XIcon, ClockIcon, WalkIcon, MapPinIcon, HeartIcon, PlusIcon, TrashIcon } from './icons';
import { useFavorites } from '../context/FavoritesContext';
import { useTrip } from '../context/TripContext';
import { refreshSpot, refreshCategory, getAvailableSpots } from '../services/apiService';
import RefreshButton from './RefreshButton';
import CategoryRefreshButton from './CategoryRefreshButton';
import MapEmbed from './MapEmbed';

interface EditableItineraryModalProps {
  itinerary: Itinerary;
  onClose: () => void;
  location: string;
  maxDistanceMiles?: number;
}

interface AddSpotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddSpot: (spot: Stop) => void;
  location: string;
  excludedIds: string[];
  maxDistanceMiles: number;
}

const AddSpotModal: React.FC<AddSpotModalProps> = ({ 
  isOpen, 
  onClose, 
  onAddSpot, 
  location, 
  excludedIds, 
  maxDistanceMiles 
}) => {
  const [availableSpots, setAvailableSpots] = useState<Stop[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'Restaurant', label: 'Restaurants' },
    { value: 'Cafe', label: 'Cafes' },
    { value: 'Park', label: 'Parks' },
    { value: 'Museum', label: 'Museums' },
    { value: 'Gallery', label: 'Galleries' },
    { value: 'Attraction', label: 'Attractions' },
    { value: 'Shop', label: 'Shopping' }
  ];

  useEffect(() => {
    if (isOpen) {
      fetchAvailableSpots();
    }
  }, [isOpen, selectedCategory]);

  const fetchAvailableSpots = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await getAvailableSpots(
        location,
        selectedCategory || undefined,
        excludedIds,
        maxDistanceMiles
      );
      setAvailableSpots(response.spots);
    } catch (error) {
      console.error('Error fetching available spots:', error);
      setError(error instanceof Error ? error.message : 'Failed to load available spots');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddSpot = (spot: Stop) => {
    onAddSpot(spot);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-60 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-secondary rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col border border-gray-700"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="p-6 border-b border-gray-700 flex justify-between items-center">
          <h3 className="text-xl font-bold text-white">Add a Spot</h3>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-card">
            <XIcon className="w-6 h-6 text-gray-400"/>
          </button>
        </header>

        <div className="p-6 overflow-y-auto">
          {/* Category Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Filter by Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 bg-card border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accent"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-md text-red-300">
              {error}
            </div>
          )}

          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto"></div>
              <p className="text-gray-400 mt-2">Loading available spots...</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {availableSpots.length === 0 ? (
                <p className="text-gray-400 text-center py-8">
                  No available spots found. Try adjusting the category filter.
                </p>
              ) : (
                availableSpots.map(spot => (
                  <div key={spot.id} className="bg-card rounded-lg p-4 border border-gray-700">
                    <div className="flex gap-4">
                      <img 
                        src={spot.image_url} 
                        alt={spot.name}
                        className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
                      />
                      <div className="flex-1">
                        <h4 className="font-semibold text-white">{spot.name}</h4>
                        <p className="text-sm text-accent">{spot.category}</p>
                        <p className="text-sm text-gray-300 mt-1 line-clamp-2">
                          {spot.description}
                        </p>
                      </div>
                      <button
                        onClick={() => handleAddSpot(spot)}
                        className="px-4 py-2 bg-accent text-primary font-medium rounded-lg hover:bg-cyan-300 transition-colors flex-shrink-0"
                      >
                        Add
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface EditableStopItemProps {
  stop: Stop;
  index: number;
  isLast: boolean;
  location: string;
  onRefresh: (stopId: string) => void;
  onCategoryRefresh: (stopId: string) => void;
  onRemove: (stopId: string) => void;
  onAddAfter: (index: number) => void;
  isRefreshing: boolean;
  isCategoryRefreshing: boolean;
  canRemove: boolean;
}

const EditableStopItem: React.FC<EditableStopItemProps> = ({ 
  stop, 
  index,
  isLast, 
  location, 
  onRefresh, 
  onCategoryRefresh,
  onRemove,
  onAddAfter,
  isRefreshing, 
  isCategoryRefreshing,
  canRemove
}) => {
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

  const mapsQuery = encodeURIComponent(`${stop.name}, ${location}`);
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${mapsQuery}`;

  return (
    <div className="relative group">
      <div className="flex items-start gap-4">
        <div className="flex flex-col items-center self-stretch">
          <div className="w-8 h-8 rounded-full bg-accent text-primary flex items-center justify-center font-bold flex-shrink-0 z-10">
            {index + 1}
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
                onClick={(e) => {
                  e.stopPropagation();
                  onRefresh(stop.id);
                }}
                isLoading={isRefreshing}
                size="sm"
                disabled={isCategoryRefreshing}
              />
              <CategoryRefreshButton 
                onClick={(e) => {
                  e.stopPropagation();
                  onCategoryRefresh(stop.id);
                }}
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
              {canRemove && (
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemove(stop.id);
                  }}
                  className="p-2 rounded-full bg-red-600/40 hover:bg-red-600/60 transition-colors"
                  aria-label="Remove stop"
                >
                  <TrashIcon className="w-6 h-6 text-white" />
                </button>
              )}
            </div>
          </div>
          <h4 className="font-bold text-lg text-white">
            <a href={mapsUrl} target="_blank" rel="noopener noreferrer" className="hover:underline hover:text-accent transition-colors duration-200">
              {stop.name}
            </a>
          </h4>
          <div className="flex items-center gap-2">
            <p className="text-sm text-accent font-semibold">{stop.category}</p>
          </div>
          <p className="mt-2 text-gray-300">{stop.description}</p>
        </div>
      </div>
      
      {/* Add spot button */}
      <div className="flex justify-center -mt-8 mb-4">
        <button
          onClick={() => onAddAfter(index)}
          className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-2 rounded-full bg-accent/20 hover:bg-accent/30 border-2 border-accent/50 hover:border-accent"
          aria-label="Add spot after this one"
        >
          <PlusIcon className="w-5 h-5 text-accent" />
        </button>
      </div>

      {!isLast && (
        <div className="flex items-center gap-2 -mt-8 mb-4 ml-[52px] text-gray-400">
          <WalkIcon className="w-4 h-4" />
          <span>{stop.walking_time_minutes} min walk to next stop</span>
        </div>
      )}
    </div>
  );
};

const EditableItineraryModal: React.FC<EditableItineraryModalProps> = ({ 
  itinerary, 
  onClose, 
  location,
  maxDistanceMiles = 1.5
}) => {
  const { startTrip } = useTrip();
  const [stops, setStops] = useState<Stop[]>(itinerary.stops);
  const [refreshingStopId, setRefreshingStopId] = useState<string | null>(null);
  const [categoryRefreshingStopId, setCategoryRefreshingStopId] = useState<string | null>(null);
  const [seenSpotIds, setSeenSpotIds] = useState<string[]>(
    itinerary.stops.map(stop => stop.id)
  );
  const [error, setError] = useState<string | null>(null);
  const [totalDuration, setTotalDuration] = useState<number>(itinerary.duration_minutes);
  const [showAddSpotModal, setShowAddSpotModal] = useState(false);
  const [addAfterIndex, setAddAfterIndex] = useState<number>(-1);

  // Recalculate total duration when stops change
  useEffect(() => {
    const newDuration = stops.reduce((total, stop) => {
      return total + stop.walking_time_minutes + 30; // Assume 30 min per stop
    }, 0);
    setTotalDuration(newDuration);
  }, [stops]);

  const handleRefreshSpot = async (stopId: string) => {
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
      
      setStops(currentStops => 
        currentStops.map(s => s.id === stopId ? newSpot : s)
      );
      
      setSeenSpotIds(ids => [...ids, newSpot.id]);
      
    } catch (error) {
      console.error('Failed to refresh spot:', error);
      setError(error instanceof Error ? error.message : 'Failed to refresh spot');
    } finally {
      setRefreshingStopId(null);
    }
  };

  const handleCategoryRefresh = async (stopId: string) => {
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
      
      setStops(currentStops => 
        currentStops.map(s => s.id === stopId ? newSpot : s)
      );
      
      setSeenSpotIds(ids => [...ids, newSpot.id]);
      
    } catch (error) {
      console.error('Failed to refresh category:', error);
      setError(error instanceof Error ? error.message : 'Failed to refresh category');
    } finally {
      setCategoryRefreshingStopId(null);
    }
  };

  const handleRemoveStop = (stopId: string) => {
    if (stops.length <= 1) {
      setError("Cannot remove the last stop. An itinerary must have at least one stop.");
      return;
    }
    
    setStops(currentStops => currentStops.filter(s => s.id !== stopId));
    setError(null);
  };

  const handleAddAfter = (index: number) => {
    setAddAfterIndex(index);
    setShowAddSpotModal(true);
  };

  const handleAddSpot = (newSpot: Stop) => {
    const insertIndex = addAfterIndex + 1;
    setStops(currentStops => [
      ...currentStops.slice(0, insertIndex),
      newSpot,
      ...currentStops.slice(insertIndex)
    ]);
    setSeenSpotIds(ids => [...ids, newSpot.id]);
    setError(null);
  };

  const handleStartTrip = () => {
    const updatedItinerary: Itinerary = {
      ...itinerary,
      stops: stops,
      duration_minutes: totalDuration
    };
    
    startTrip(updatedItinerary, location);
    onClose();
    window.location.hash = '#/trip';
  };

  return (
    <>
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
                <span>~{Math.round(totalDuration / 60 * 10) / 10} hours total • {stops.length} stops</span>
              </div>
            </div>
            <button onClick={onClose} className="p-2 rounded-full hover:bg-card" aria-label="Close modal">
              <XIcon className="w-6 h-6 text-gray-400"/>
            </button>
          </header>

          <div className="p-6 overflow-y-auto">
            <p className="text-gray-300 mb-4">{itinerary.description}</p>
            <p className="text-sm text-gray-400 mb-8">
              Hover over stops to add new ones, or use the refresh buttons to change existing stops.
            </p>
            
            {error && (
              <div className="mb-6 p-3 bg-red-900/30 border border-red-700 rounded-md text-red-300">
                {error}
              </div>
            )}
            
            <div className="flex flex-col">
              {stops.map((stop, index) => (
                <EditableStopItem 
                  key={stop.id} 
                  stop={stop} 
                  index={index}
                  isLast={index === stops.length - 1} 
                  location={location}
                  onRefresh={handleRefreshSpot}
                  onCategoryRefresh={handleCategoryRefresh}
                  onRemove={handleRemoveStop}
                  onAddAfter={handleAddAfter}
                  isRefreshing={refreshingStopId === stop.id}
                  isCategoryRefreshing={categoryRefreshingStopId === stop.id}
                  canRemove={stops.length > 1}
                />
              ))}
            </div>
            
            {/* Add spot at the end */}
            <div className="flex justify-center mt-4 mb-6">
              <button
                onClick={() => handleAddAfter(stops.length - 1)}
                className="px-4 py-2 bg-accent/20 hover:bg-accent/30 border-2 border-accent/50 hover:border-accent rounded-lg transition-colors flex items-center gap-2 text-accent"
              >
                <PlusIcon className="w-5 h-5" />
                Add final stop
              </button>
            </div>
            
            <MapEmbed stops={stops} location={location} />
            
            <div className="mt-6 pt-6 border-t border-gray-700">
              <button
                onClick={handleStartTrip}
                className="w-full px-6 py-3 bg-accent text-primary font-bold rounded-md hover:bg-cyan-300 transition-colors flex items-center justify-center gap-2"
              >
                <MapPinIcon className="w-5 h-5" />
                Start this trip
              </button>
            </div>
          </div>
        </div>
      </div>

      <AddSpotModal
        isOpen={showAddSpotModal}
        onClose={() => setShowAddSpotModal(false)}
        onAddSpot={handleAddSpot}
        location={location}
        excludedIds={seenSpotIds}
        maxDistanceMiles={maxDistanceMiles}
      />

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
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </>
  );
};

export default EditableItineraryModal;