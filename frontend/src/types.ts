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

// AI day plan types (optional structure returned by AI engine)
export interface AIDayPlanStop {
  time?: string; // e.g., "09:00 AM"
  name: string;
  category?: string;
  notes?: string;
  address?: string;
  image_url?: string;
  duration_minutes?: number;
  // Enrichment fields (matched from AIBusiness)
  price?: string;
  rating?: number;
  url?: string;
  lat?: number;
  lng?: number;
}

export interface AIDayPlan {
  id?: string;
  title: string;
  summary?: string;
  total_duration_minutes?: number;
  total_stops?: number;
  total_distance_miles?: number;
  start_time?: string;
  end_time?: string;
  map_url?: string;
  tips?: string[];
  budget?: string;
  transportation?: string;
  weather_note?: string;
  stops: AIDayPlanStop[];
  additional_info?: Record<string, any>;
}

export interface AIEngineResponse {
  chat_id?: string;
  text?: string;
  businesses: AIBusiness[];
  plan?: AIDayPlan;
  plans?: AIDayPlan[];
  extras?: Record<string, any>;
}