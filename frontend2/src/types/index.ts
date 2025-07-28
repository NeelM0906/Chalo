export interface Stop {
  id: string;
  name: string;
  category: string;
  description: string;
  address: string;
  rating?: number;
  price_level?: number;
  opening_hours?: string[];
  website?: string;
  phone?: string;
  photos?: string[];
}

export interface Itinerary {
  id: string;
  title: string;
  description: string;
  duration: string;
  stops: Stop[];
  total_walking_time?: string;
  estimated_cost?: string;
}

export interface GroundingChunk {
  title: string;
  content: string;
  url?: string;
}