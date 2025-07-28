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