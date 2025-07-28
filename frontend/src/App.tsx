import React, { useState, useCallback, useEffect } from 'react';
import { Itinerary, Stop } from './types';
import { getItineraries } from './services/apiService';
import LocationInput from './components/LocationInput';
import ItineraryCard from './components/ItineraryCard';
import ItineraryDetailModal from './components/ItineraryDetailModal';
import WanderingEyesAnimation from './components/WanderingEyesAnimation';

import PresetButtons from './components/PresetButtons';
import FilterDropdowns from './components/FilterDropdowns';
import { LogoIcon, HeartIcon, XIcon, MapPinIcon, UsersIcon } from './components/icons';
import { FavoritesProvider, useFavorites } from './context/FavoritesContext';
import WanderBuddiesPage from './components/WanderBuddiesPage';

// --- Home Page Component ---
const HomePage: React.FC = () => {
  const [location, setLocation] = useState<string>('');
  const [itineraries, setItineraries] = useState<Itinerary[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItinerary, setSelectedItinerary] = useState<Itinerary | null>(null);
  const [currentPreset, setCurrentPreset] = useState<string | null>(null);
  const [priceFilter, setPriceFilter] = useState<string>('');
  const [distanceFilter, setDistanceFilter] = useState<number>(1.5);

  const handleSearch = useCallback(async (searchLocation: string, preset?: string) => {
    if (!searchLocation) {
      setError('Please provide a location.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setItineraries([]);

    setLocation(searchLocation);
    setCurrentPreset(preset || null);

    try {
      // Create a minimum 3-second delay for better UX
      const minDelay = new Promise(resolve => setTimeout(resolve, 3000));
      const apiCall = getItineraries(
        searchLocation,
        preset,
        priceFilter || undefined,
        distanceFilter
      );
      
      // Wait for both the API call and minimum delay
      const [result] = await Promise.all([apiCall, minDelay]);
      if (result.itineraries && result.itineraries.length > 0) {
        setItineraries(result.itineraries);

      } else {
        const errorMsg = preset
          ? `Could not generate ${preset} itineraries for this location. Please try a different location or category.`
          : 'Could not generate itineraries for this location. Please try a different one.';
        setError(errorMsg);
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
        setError('An unexpected error occurred while fetching your adventures. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [priceFilter, distanceFilter]);

  const handlePresetSearch = useCallback(async (preset: string) => {
    if (!location) {
      setError('Please enter a location first, then select a category.');
      return;
    }
    await handleSearch(location, preset);
  }, [location, handleSearch]);

  const handleSelectItinerary = (itinerary: Itinerary) => {
    setSelectedItinerary(itinerary);
  };

  const handleCloseModal = () => {
    setSelectedItinerary(null);
  };

  return (
    <>
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white">
          Rediscover Your Neighborhood
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mt-4">
          Enter a location to instantly generate hyper-local micro-adventures.
        </p>
      </div>

      <LocationInput onSearch={(loc) => handleSearch(loc)} isLoading={isLoading} />

      <FilterDropdowns
        priceFilter={priceFilter}
        distanceFilter={distanceFilter}
        onPriceChange={setPriceFilter}
        onDistanceChange={setDistanceFilter}
        isLoading={isLoading}
      />

      <PresetButtons onPresetSearch={handlePresetSearch} isLoading={isLoading} />

      {error && <p className="text-center text-red-400 mt-8 text-lg">{error}</p>}

      {isLoading && (
        <div className="flex justify-center items-center py-16">
          <div className="text-center">
            <WanderingEyesAnimation size={64} />
            <p className="text-gray-400 mt-4 text-lg">Discovering your next adventure...</p>
          </div>
        </div>
      )}

      {!isLoading && itineraries.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-center mb-2 text-white">
            {currentPreset ? `${currentPreset} Adventures` : 'Your Spontaneous Journeys'}
          </h2>
          <p className="text-center text-gray-400 mb-8">
            Generated for: <span className="font-semibold text-accent">{location}</span>
            {currentPreset && <span className="text-gray-500"> • {currentPreset}</span>}
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

      {selectedItinerary && (
        <ItineraryDetailModal
          itinerary={selectedItinerary}
          onClose={handleCloseModal}
          location={location}
        />
      )}
    </>
  );
};

// --- Favorite Card Component ---
const FavoriteCard: React.FC<{ stop: Stop }> = ({ stop }) => {
  const { removeFavorite } = useFavorites();
  return (
    <div className="bg-card rounded-lg border border-gray-700 flex flex-col overflow-hidden group">
      <div className="w-full h-48 bg-secondary flex items-center justify-center overflow-hidden relative">
        <img src={stop.image_url} alt={stop.name} className="w-full h-full object-cover" />
        <button
          onClick={() => removeFavorite(stop.id)}
          className="absolute top-2 right-2 p-2 rounded-full bg-black/40 hover:bg-black/60 transition-colors"
          aria-label="Remove from favorites"
        >
          <XIcon className="w-5 h-5 text-white" />
        </button>
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="font-bold text-white">{stop.name}</h3>
        <p className="text-sm text-accent font-semibold">{stop.category}</p>
        <p className="text-gray-400 mt-2 text-sm flex-grow">{stop.description}</p>
      </div>
    </div>
  );
};

// --- Favorites Page Component ---
const FavoritesPage: React.FC = () => {
  const { favorites } = useFavorites();
  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    window.location.hash = '#/';
  };

  return (
    <div>
      <div className="mb-12 text-center">
        <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white">
          My Saved Adventures
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mt-4">
          Your collection of hand-picked spots to visit.
        </p>
      </div>

      {favorites.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {favorites.map(stop => (
            <FavoriteCard key={stop.id} stop={stop} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 px-6 bg-card rounded-lg border border-gray-700">
          <div className="flex justify-center items-center mb-4">
            <MapPinIcon className="w-12 h-12 text-gray-500" />
          </div>
          <p className="text-xl font-semibold text-white">No adventures saved yet.</p>
          <p className="text-gray-400 mt-2">Go <a href="#/" onClick={handleNavClick} className="text-accent hover:underline">explore</a> and like some stops to see them here!</p>
        </div>
      )}
    </div>
  )
}

// --- Main App Content & Router ---
const AppContent: React.FC = () => {
  const [route, setRoute] = useState(window.location.hash);
  const { favorites } = useFavorites();

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, path: string) => {
    e.preventDefault();
    window.location.hash = path;
  };

  useEffect(() => {
    const handleHashChange = () => setRoute(window.location.hash);
    window.addEventListener('hashchange', handleHashChange, false);
    return () => window.removeEventListener('hashchange', handleHashChange, false);
  }, []);

  let page;
  switch (route) {
    case '#/favorites':
      page = <FavoritesPage />;
      break;
    case '#/buddies':
      page = <WanderBuddiesPage />;
      break;
    default:
      page = <HomePage />;
  }

  return (
    <div className="min-h-screen font-sans">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center sticky top-0 z-10 bg-primary/80 backdrop-blur-sm">
        <a href="#/" onClick={(e) => handleNavClick(e, '#/')} className="flex items-center gap-3 text-white hover:text-accent transition-colors">
          <LogoIcon className="w-8 h-8 text-accent" />
          <span className="text-xl sm:text-2xl font-black tracking-tighter">Chalo</span>
        </a>
        <div className="flex items-center gap-2">
          <a href="#/buddies" onClick={(e) => handleNavClick(e, '#/buddies')} className="relative p-2 rounded-full hover:bg-card transition-colors" aria-label="View Wander Buddies">
            <UsersIcon className="w-7 h-7 text-accent" />
          </a>
          <a href="#/favorites" onClick={(e) => handleNavClick(e, '#/favorites')} className="relative p-2 rounded-full hover:bg-card transition-colors" aria-label={`View ${favorites.length} favorites`}>
            <HeartIcon className="w-7 h-7 text-accent" />
            {favorites.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center border-2 border-primary">
                {favorites.length}
              </span>
            )}
          </a>
        </div>
      </header>
      <main className="container mx-auto px-4 pb-8 md:pb-12">
        {page}
      </main>
      <footer className="text-center py-6 text-gray-500 text-sm">
        <p>Powered by custom recommendation engine. Adventures may be unpredictable.</p>
      </footer>
    </div>
  );
};

// --- App Wrapper with Provider ---
const App: React.FC = () => (
  <FavoritesProvider>
    <AppContent />
  </FavoritesProvider>
);

export default App;