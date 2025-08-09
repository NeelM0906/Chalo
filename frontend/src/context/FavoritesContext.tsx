import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Stop } from '../types';

interface FavoritesContextType {
  favorites: Stop[];
  addFavorite: (stop: Stop) => void;
  removeFavorite: (stopId: string) => void;
  isFavorite: (stopId: string) => boolean;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export const FavoritesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [favorites, setFavorites] = useState<Stop[]>(() => {
    try {
      const item = window.localStorage.getItem('chaloFavorites');
      return item ? JSON.parse(item) : [];
    } catch (error) {
      console.error('Error reading favorites from localStorage', error);
      return [];
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem('chaloFavorites', JSON.stringify(favorites));
    } catch (error) {
      console.error('Error writing favorites to localStorage', error);
    }
  }, [favorites]);

  const addFavorite = (stop: Stop) => {
    setFavorites((prevFavorites) => {
      if (prevFavorites.find(fav => fav.id === stop.id)) {
        return prevFavorites; // Already favorited
      }
      return [...prevFavorites, stop];
    });
  };

  const removeFavorite = (stopId: string) => {
    setFavorites((prevFavorites) => prevFavorites.filter(fav => fav.id !== stopId));
  };

  const isFavorite = (stopId: string) => {
    return favorites.some(fav => fav.id === stopId);
  };

  const value = { favorites, addFavorite, removeFavorite, isFavorite };

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  );
};

export const useFavorites = (): FavoritesContextType => {
  const context = useContext(FavoritesContext);
  if (context === undefined) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return context;
};
