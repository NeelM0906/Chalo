import { Itinerary, GroundingChunk, Stop } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse {
    itineraries: Itinerary[];
    sources: GroundingChunk[];
}

interface ErrorResponse {
    detail: string;
}

export const getItineraries = async (
    location: string, 
    preset?: string, 
    maxPriceLevel?: string, 
    maxDistanceMiles?: number
): Promise<ApiResponse> => {
    try {
        const requestBody: any = { location };
        if (preset) {
            requestBody.preset = preset;
        }
        if (maxPriceLevel) {
            requestBody.max_price_level = maxPriceLevel;
        }
        if (maxDistanceMiles) {
            requestBody.max_distance_miles = maxDistanceMiles;
        }

        const response = await fetch(`${API_BASE_URL}/api/itineraries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            // Try to get error details from response
            let errorMessage = `HTTP error! status: ${response.status}`;

            try {
                const errorData: ErrorResponse = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // If we can't parse error response, use default message
            }

            if (response.status === 400) {
                throw new Error(errorMessage);
            }
            if (response.status === 404) {
                throw new Error(errorMessage);
            }
            if (response.status === 429) {
                throw new Error('Too many requests. Please try again later.');
            }
            if (response.status === 500) {
                throw new Error('Server error occurred. Please try again.');
            }

            throw new Error(errorMessage);
        }

        const data: ApiResponse = await response.json();

        if (!data.itineraries || !Array.isArray(data.itineraries)) {
            throw new Error('Invalid data format received from API.');
        }

        return data;
    } catch (error) {
        console.error('Error fetching itineraries:', error);

        if (error instanceof Error) {
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Unable to connect to the server. Please ensure the backend is running on port 8000.');
            }
            throw error;
        }

        throw new Error('Failed to generate itineraries from the recommendation engine.');
    }
};

export const refreshSpot = async (
    location: string,
    category: string,
    excludedIds: string[] = []
): Promise<Stop> => {
    try {
        // Use main backend for refresh spot
        const response = await fetch(`${API_BASE_URL}/api/refresh-spot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ location, category, excluded_ids: excludedIds }),
        });

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;

            try {
                const errorData: ErrorResponse = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // If we can't parse error response, use default message
            }

            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('Error refreshing spot:', error);
        throw error;
    }
};

export const refreshCategory = async (
    location: string,
    currentCategory: string,
    excludedSpotIds: string[] = []
): Promise<Stop> => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/refresh-category`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                location, 
                current_category: currentCategory, 
                excluded_spot_ids: excludedSpotIds 
            }),
        });

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;

            try {
                const errorData: ErrorResponse = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // If we can't parse error response, use default message
            }

            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('Error refreshing category:', error);
        throw error;
    }
};

export const getCustomTrips = async (
    location: string,
    categories: string[],
    maxDistanceMiles: number
): Promise<ApiResponse> => {
    try {
        const requestBody = {
            location,
            categories,
            max_distance_miles: maxDistanceMiles
        };

        const response = await fetch(`${API_BASE_URL}/api/custom-trips`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            // Try to get error details from response
            let errorMessage = `HTTP error! status: ${response.status}`;

            try {
                const errorData: ErrorResponse = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // If we can't parse error response, use default message
            }

            if (response.status === 400) {
                throw new Error(errorMessage);
            }
            if (response.status === 404) {
                throw new Error(errorMessage);
            }
            if (response.status === 429) {
                throw new Error('Too many requests. Please try again later.');
            }
            if (response.status === 500) {
                throw new Error('Server error occurred. Please try again.');
            }

            throw new Error(errorMessage);
        }

        const data: ApiResponse = await response.json();

        if (!data.itineraries || !Array.isArray(data.itineraries)) {
            throw new Error('Invalid data format received from API.');
        }

        return data;
    } catch (error) {
        console.error('Error fetching custom trips:', error);

        if (error instanceof Error) {
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Unable to connect to the server. Please ensure the backend is running on port 8000.');
            }
            throw error;
        }

        throw new Error('Failed to generate custom trips from the recommendation engine.');
    }
};

export const getAvailableSpots = async (
    location: string,
    category?: string,
    excludedIds: string[] = [],
    maxDistanceMiles: number = 1.5
): Promise<{ spots: Stop[] }> => {
    try {
        const requestBody = {
            location,
            category,
            excluded_ids: excludedIds,
            max_distance_miles: maxDistanceMiles
        };

        const response = await fetch(`${API_BASE_URL}/api/get-available-spots`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;

            try {
                const errorData: ErrorResponse = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // If we can't parse error response, use default message
            }

            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('Error getting available spots:', error);
        throw error;
    }
};

export const healthCheck = async (): Promise<boolean> => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return response.ok;
    } catch {
        return false;
    }
};

