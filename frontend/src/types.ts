export interface Stop {
  id: string;
  name: string;
  category: string;
  walking_time_minutes: number;
  description?: string;
  image_url: string;
}

export interface Itinerary {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  stops: Stop[];
}

export interface GroundingChunk {
  web: {
    uri: string;
    title: string;
  };
}

export interface CategoryRefreshRequest {
  location: string;
  current_category: string;
  excluded_spot_ids: string[];
}

export interface RefreshSpotRequest {
  location: string;
  category: string;
  excluded_ids: string[];
}

export interface AddSpotRequest {
  location: string;
  position: number;
  category?: string;
  excluded_ids: string[];
}

export interface GetAvailableSpotsRequest {
  location: string;
  category?: string;
  excluded_ids: string[];
  max_distance_miles: number;
}

export interface AvailableSpotsResponse {
  spots: Stop[];
}

// Agent-specific types
export interface AgentRequest {
  user_request: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  distance_miles?: number;
}

export interface AIBusinessLocation {
  address1?: string;
  address2?: string;
  city?: string;
  zip_code?: string;
  state?: string;
  country?: string;
  formatted_address?: string;
}

export interface AICoordinates {
  lat?: number;
  lng?: number;
}

export interface AIBusiness {
  id?: string;
  alias?: string;
  name?: string;
  url?: string;
  image_url?: string;
  photos?: string[];
  phoos?: string[];
  location: AIBusinessLocation;
  coordinates: AICoordinates;
  review_count?: number;
  price?: string;
  rating?: number;
  AboutThisBizBio?: string;
  AboutThisBizHistory?: string;
  AboutThisBizSpecialties?: string;
  AboutThisBizYearEstablished?: string;
}

export interface AIEngineResponse {
  chat_id?: string;
  text?: string;
  businesses: AIBusiness[];
}