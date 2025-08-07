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
  location: string;
  distance_miles: number;
}

export interface AgentStop {
  place_name: string;
  category: string;
  why_recommended: string;
  walking_time_to_next: number;
}

export interface AgentRoute {
  name: string;
  description: string;
  stops: AgentStop[];
  total_duration_minutes: number;
  local_tip: string;
}

export interface AgentUserIntent {
  search_queries: string[];
  mood_context: string;
  experience_type: string;
}

export interface AgentResponse {
  user_intent: AgentUserIntent;
  recommendations: {
    routes: AgentRoute[];
  };
  search_context: any;
}