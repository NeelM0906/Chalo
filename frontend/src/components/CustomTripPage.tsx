import React, { useState, useCallback } from 'react';
import { Itinerary } from '../types';
import { getCustomTrips } from '../services/apiService';
import ChaloEyesAnimation from './ChaloEyesAnimation';
import ItineraryCard from './ItineraryCard';
import EditableItineraryModal from './EditableItineraryModal';
import {
  TreeIcon,
  PaletteIcon,
  UtensilsIcon,
  LandmarkIcon,
  ShoppingBagIcon,
  MapPinIcon
} from './icons';

interface CategoryOption {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  apiValue: string;
}

const CATEGORY_OPTIONS: CategoryOption[] = [
  { id: 'cafes', name: 'Cafes', icon: UtensilsIcon, apiValue: 'cafe' },
  { id: 'restaurants', name: 'Restaurants', icon: UtensilsIcon, apiValue: 'restaurant' },
  { id: 'parks', name: 'Parks', icon: TreeIcon, apiValue: 'park' },
  { id: 'museums', name: 'Museums', icon: PaletteIcon, apiValue: 'museum' },
  { id: 'galleries', name: 'Art Galleries', icon: PaletteIcon, apiValue: 'art_gallery' },
  { id: 'attractions', name: 'Tourist Attractions', icon: LandmarkIcon, apiValue: 'tourist_attraction' },
];

const DISTANCE_OPTIONS = [
  { value: 0.5, label: '0.5 miles' },
  { value: 1, label: '1 mile' },
  { value: 1.5, label: '1.5 miles' },
  { value: 2, label: '2 miles' },
];

const CustomTripPage: React.FC = () => {
  const [location, setLocation] = useState<string>('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedDistance, setSelectedDistance] = useState<number>(1.5);
  const [itineraries, setItineraries] = useState<Itinerary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItinerary, setSelectedItinerary] = useState<Itinerary | null>(null);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  const handleCategoryToggle = (categoryId: string) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleSearch = useCallback(async () => {
    if (!location.trim()) {
      setError('Please enter a location.');
      return;
    }

    if (selectedCategories.length === 0) {
      setError('Please select at least one category.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setItineraries([]);
    setHasSearched(true);

    try {
      // Create a minimum 3-second delay for better UX
      const minDelay = new Promise(resolve => setTimeout(resolve, 3000));

      // Convert selected category IDs to API values
      const apiCategories = selectedCategories.map(categoryId => {
        const categoryOption = CATEGORY_OPTIONS.find(option => option.id === categoryId);
        return categoryOption?.apiValue || categoryId;
      });

      // Use the custom trips API endpoint
      const apiCall = getCustomTrips(
        location.trim(),
        apiCategories,
        selectedDistance
      );

      // Wait for both the API call and minimum delay
      const [result] = await Promise.all([apiCall, minDelay]);

      if (result.itineraries && result.itineraries.length > 0) {
        // The backend already limits to 3 itineraries for custom trips
        setItineraries(result.itineraries);
      } else {
        setError('Could not generate custom trips for this location and preferences. Please try a different location or adjust your selections.');
      }
    } catch (e) {
      console.error(e);
      if (e instanceof Error) {
        if (e.message.includes('Unable to connect to the server')) {
          setError('Unable to connect to the recommendation service. Please ensure the backend server is running on port 8000.');
        } else {
          setError(e.message);
        }
      } else {
        setError('An unexpected error occurred while generating your custom trips. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [location, selectedCategories, selectedDistance]);

  const handleSelectItinerary = (itinerary: Itinerary) => {
    setSelectedItinerary(itinerary);
  };

  const handleCloseModal = () => {
    setSelectedItinerary(null);
  };

  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white">
          Custom Trip Builder
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mt-4">
          Create personalized adventures by choosing your location, preferences, and distance.
        </p>
      </div>

      {/* Step 1: Location Input */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">1. Enter Your Location</h2>
        <div className="max-w-md mx-auto">
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter address or neighborhood..."
            className="w-full px-4 py-3 bg-card border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Step 2: Category Selection */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">2. Choose Your Preferences</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
          {CATEGORY_OPTIONS.map((category) => {
            const IconComponent = category.icon;
            const isSelected = selectedCategories.includes(category.id);

            return (
              <button
                key={category.id}
                onClick={() => handleCategoryToggle(category.id)}
                disabled={isLoading}
                className={`p-4 rounded-lg border-2 transition-all duration-200 ${isSelected
                  ? 'border-accent bg-accent/10 text-accent'
                  : 'border-gray-600 bg-card text-gray-300 hover:border-gray-500 hover:text-white'
                  } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <IconComponent className="w-8 h-8 mx-auto mb-2" />
                <span className="text-sm font-medium">{category.name}</span>
              </button>
            );
          })}
        </div>
        {selectedCategories.length > 0 && (
          <p className="text-center text-accent mt-4">
            {selectedCategories.length} categor{selectedCategories.length === 1 ? 'y' : 'ies'} selected
          </p>
        )}
      </div>

      {/* Step 3: Distance Selection */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">3. Select Distance Range</h2>
        <div className="flex flex-wrap justify-center gap-4 max-w-2xl mx-auto">
          {DISTANCE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setSelectedDistance(option.value)}
              disabled={isLoading}
              className={`px-6 py-3 rounded-lg border-2 transition-all duration-200 ${selectedDistance === option.value
                ? 'border-accent bg-accent/10 text-accent'
                : 'border-gray-600 bg-card text-gray-300 hover:border-gray-500 hover:text-white'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <div className="text-center mb-12">
        <button
          onClick={handleSearch}
          disabled={isLoading || !location.trim() || selectedCategories.length === 0}
          className="px-8 py-4 bg-accent hover:bg-accent/90 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold rounded-lg transition-colors duration-200 text-lg"
        >
          {isLoading ? 'Generating Trips...' : 'Generate Custom Trips'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="text-center mb-8">
          <p className="text-red-400 text-lg">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-16">
          <div className="text-center">
            <ChaloEyesAnimation size={64} />
            <p className="text-gray-400 mt-4 text-lg">Creating your custom adventures...</p>
          </div>
        </div>
      )}

      {/* Results */}
      {!isLoading && hasSearched && itineraries.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-center mb-2 text-white">
            Your Custom Trip Options
          </h2>
          <p className="text-center text-gray-400 mb-8">
            Generated for: <span className="font-semibold text-accent">{location}</span>
            <span className="text-gray-500"> • {selectedDistance} mile{selectedDistance !== 1 ? 's' : ''} radius</span>
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {itineraries.map((itinerary) => (
              <ItineraryCard
                key={itinerary.id}
                itinerary={itinerary}
                onSelect={handleSelectItinerary}
              />
            ))}
          </div>
        </div>
      )}

      {/* No Results State */}
      {!isLoading && hasSearched && itineraries.length === 0 && !error && (
        <div className="text-center py-16 px-6 bg-card rounded-lg border border-gray-700">
          <div className="flex justify-center items-center mb-4">
            <MapPinIcon className="w-12 h-12 text-gray-500" />
          </div>
          <p className="text-xl font-semibold text-white">No trips found</p>
          <p className="text-gray-400 mt-2">Try adjusting your location, categories, or distance range.</p>
        </div>
      )}

      {/* Editable Itinerary Modal */}
      {selectedItinerary && (
        <EditableItineraryModal
          itinerary={selectedItinerary}
          onClose={handleCloseModal}
          location={location}
          maxDistanceMiles={selectedDistance}
        />
      )}
    </div>
  );
};

export default CustomTripPage;