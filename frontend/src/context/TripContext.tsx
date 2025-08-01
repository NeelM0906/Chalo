import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Itinerary } from '../types';

interface StoredTrip {
  itinerary: Itinerary;
  location: string;
  startedAt: string; // ISO timestamp
}

interface TripContextType {
  currentTrip: Itinerary | null;
  tripLocation: string | null;
  startTrip: (itinerary: Itinerary, location: string) => void;
  endTrip: () => void;
}

const TripContext = createContext<TripContextType | undefined>(undefined);

const STORAGE_KEY = 'localwander_current_trip';

interface TripProviderProps {
  children: ReactNode;
}

export const TripProvider: React.FC<TripProviderProps> = ({ children }) => {
  const [currentTrip, setCurrentTrip] = useState<Itinerary | null>(null);
  const [tripLocation, setTripLocation] = useState<string | null>(null);

  // Load trip from localStorage on mount
  useEffect(() => {
    try {
      const storedTrip = localStorage.getItem(STORAGE_KEY);
      if (storedTrip) {
        const parsedTrip: StoredTrip = JSON.parse(storedTrip);
        setCurrentTrip(parsedTrip.itinerary);
        setTripLocation(parsedTrip.location);
      }
    } catch (error) {
      console.error('Failed to load trip from localStorage:', error);
      // Clear corrupted data
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const startTrip = (itinerary: Itinerary, location: string) => {
    const tripData: StoredTrip = {
      itinerary,
      location,
      startedAt: new Date().toISOString()
    };

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tripData));
      setCurrentTrip(itinerary);
      setTripLocation(location);
    } catch (error) {
      console.error('Failed to save trip to localStorage:', error);
      // Still set the state even if localStorage fails
      setCurrentTrip(itinerary);
      setTripLocation(location);
    }
  };

  const endTrip = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to remove trip from localStorage:', error);
    }
    setCurrentTrip(null);
    setTripLocation(null);
  };

  const value: TripContextType = {
    currentTrip,
    tripLocation,
    startTrip,
    endTrip
  };

  return (
    <TripContext.Provider value={value}>
      {children}
    </TripContext.Provider>
  );
};

export const useTrip = (): TripContextType => {
  const context = useContext(TripContext);
  if (context === undefined) {
    throw new Error('useTrip must be used within a TripProvider');
  }
  return context;
};