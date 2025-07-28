import requests
import json
import os
import concurrent.futures
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# ==============================================================================
# Chalo Search Parameters
# ==============================================================================
CHALO_CATEGORIES = [
    "restaurants near me",
    "cafes and bakeries near me", 
    "parks near me",
    "delis near me",
    "thrift stores near me",
    "tourist attractions near me",
    "museums near me",
    "galleries near me",
    "markets near me"
]

SEARCH_RADIUS_METERS = 4023  # Approximately 2.5 miles for search
ITINERARY_RADIUS_METERS = 2414  # Approximately 1.5 miles for final itinerary
DEFAULT_LOCATION = "Hells Kitchen, NY"

# Google Maps API Configuration
GEOCODING_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
NEARBY_SEARCH_BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_BASE_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DISTANCE_MATRIX_BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

class ChaloSearchEngine:
    """Chalo search engine for discovering and organizing local places"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TESTING MODE: Add testing mode flag
        self.testing_mode = False
        self.testing_data_file = "search_results/search_results_manhattan_NY_20250724_185116.json"

    def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """Convert address to latitude/longitude coordinates"""
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            response = requests.get(GEOCODING_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                print(f"Geocoding Error for {address}: {data['status']} - {data.get('error_message', 'No error message.')}")
                return None, None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {address}: {e}")
            return None, None

    def find_nearby_places(self, user_location_str: str, keyword: str, radius: int) -> List[str]:
        """Find nearby places using Google Places API"""
        params = {
            'location': user_location_str,
            'radius': radius,
            'keyword': keyword,
            'key': self.api_key
        }
        
        try:
            print(f"Searching for '{keyword}' near {user_location_str}...")
            response = requests.get(NEARBY_SEARCH_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                return [place['place_id'] for place in data.get('results', [])[:15]]
            else:
                print(f"Places search error: {data['status']}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Places search request failed: {e}")
            return []

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a specific place"""
        params = {
            'place_id': place_id,
            'fields': 'name,geometry,formatted_address,rating,price_level,types,opening_hours,reviews,photos,formatted_phone_number,website,editorial_summary',
            'key': self.api_key
        }
        
        try:
            response = requests.get(PLACE_DETAILS_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                return data['result']
            else:
                print(f"Place details error: {data['status']}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Place details request failed: {e}")
            return None

    def calculate_distance(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Optional[float]:
        """Calculate distance between two points using Distance Matrix API"""
        params = {
            'origins': f"{origin_lat},{origin_lng}",
            'destinations': f"{dest_lat},{dest_lng}",
            'units': 'imperial',
            'key': self.api_key
        }
        
        try:
            response = requests.get(DISTANCE_MATRIX_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if (data['status'] == 'OK' and 
                data['rows'] and 
                data['rows'][0]['elements'] and 
                data['rows'][0]['elements'][0]['status'] == 'OK'):
                
                distance_value = data['rows'][0]['elements'][0]['distance']['value']
                return float(distance_value)
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Distance calculation failed: {e}")
            return None

    def format_opening_hours(self, hours_data: Dict) -> Optional[Dict]:
        """Format opening hours data"""
        if not hours_data or 'weekday_text' not in hours_data:
            return None
            
        hours_dict = {}
        for item in hours_data['weekday_text']:
            if ': ' in item:
                day, hours = item.split(': ', 1)
                hours_dict[day] = hours
        return hours_dict

    def parse_category_query(self, query: str) -> Tuple[str, str]:
        """Parse category query to extract keyword and location"""
        query = query.lower()
        if " near " in query:
            parts = query.split(" near ")
            return parts[0], parts[1]
        else:
            return query.replace(" near me", ""), "me"

    def process_category_search(self, category_query: str, origin_address: str, search_radius_meters: int = SEARCH_RADIUS_METERS) -> Tuple[str, List[Dict]]:
        """Process a single category search and return formatted results"""
        keyword, location_str = self.parse_category_query(category_query)
        if location_str == "me":
            location_str = origin_address

        # Geocode the origin address
        user_lat, user_lng = self.geocode_address(location_str)
        if not user_lat:
            return category_query, []

        time.sleep(0.5)  # Rate limiting
        user_location_str = f"{user_lat},{user_lng}"
        place_ids = self.find_nearby_places(user_location_str, keyword, search_radius_meters)
        
        if not place_ids:
            return category_query, []

        time.sleep(0.5)  # Rate limiting

        # Process place details concurrently (reduced workers to save API calls)
        filtered_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_place_id = {
                executor.submit(self.get_place_details, place_id): place_id 
                for place_id in place_ids
            }
            
            for future in concurrent.futures.as_completed(future_to_place_id):
                result = future.result()
                time.sleep(0.5)  # Increased rate limiting to save API calls
                
                if result:
                    place_data = self.format_place_data(result, user_lat, user_lng)
                    if place_data and place_data.get('distance_meters', float('inf')) <= search_radius_meters:
                        filtered_results.append(place_data)

        # Sort by rating and distance
        filtered_results.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', float('inf'))))
        return category_query, filtered_results[:10]  # Return top 10 results

    def format_place_data(self, place_result: Dict, origin_lat: float, origin_lng: float) -> Optional[Dict]:
        """Format place data into Chalo structure"""
        try:
            place_location = place_result.get('geometry', {}).get('location', {})
            place_lat = place_location.get('lat')
            place_lng = place_location.get('lng')
            
            if not place_lat or not place_lng:
                return None

            # Calculate distance from origin
            distance_meters = self.calculate_distance(origin_lat, origin_lng, place_lat, place_lng)

            # Format opening hours
            opening_hours = self.format_opening_hours(place_result.get('opening_hours', {}))

            # Get photo URL if available
            photo_url = None
            if place_result.get('photos'):
                photo_ref = place_result['photos'][0].get('photo_reference')
                if photo_ref:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={self.api_key}"

            # Get latest review
            latest_review = None
            if place_result.get('reviews'):
                review_text = place_result['reviews'][0].get('text', '')
                latest_review = review_text[:200] + "..." if len(review_text) > 200 else review_text

            formatted_place = {
                'place_id': place_result.get('place_id'),
                'name': place_result.get('name'),
                'latitude': place_lat,
                'longitude': place_lng,
                'address': place_result.get('formatted_address'),
                'distance_meters': distance_meters,
                'distance_miles': round(distance_meters / 1609.34, 2) if distance_meters else None,
                'rating': place_result.get('rating'),
                'user_ratings_total': place_result.get('user_ratings_total'),
                'price_level': place_result.get('price_level'),
                'types': place_result.get('types', []),
                'opening_hours': opening_hours,
                'phone_number': place_result.get('formatted_phone_number'),
                'website': place_result.get('website'),
                'photo_url': photo_url,
                'latest_review': latest_review,
                'editorial_summary': place_result.get('editorial_summary', {}).get('overview')
            }

            return formatted_place

        except Exception as e:
            print(f"Error formatting place data: {e}")
            return None

    def search_specific_categories(self, origin_address: str, categories: List[str], search_radius_miles: float = 2.5) -> Dict:
        """Search specific categories and return organized results"""
        search_radius_meters = int(search_radius_miles * 1609.34)
        
        print(f"Chalo Search Engine - Specific Categories")
        print(f"Origin: {origin_address}")
        print(f"Search Radius: {search_radius_meters} meters ({search_radius_miles} miles)")
        print(f"Categories: {len(categories)}")
        print("-" * 60)

        # Process specified categories
        all_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_category = {
                executor.submit(self.process_category_search, category, origin_address, search_radius_meters): category 
                for category in categories
            }
            
            for future in concurrent.futures.as_completed(future_to_category):
                category, results = future.result()
                all_results[category] = results
                print(f"✓ Completed: {category} - Found {len(results)} places")

        # Create summary
        total_places = sum(len(results) for results in all_results.values())
        summary = {
            'search_metadata': {
                'origin_address': origin_address,
                'search_radius_meters': search_radius_meters,
                'search_radius_miles': search_radius_miles,
                'itinerary_radius_meters': search_radius_meters,  # Use same radius for itinerary
                'itinerary_radius_miles': search_radius_miles,
                'categories_searched': len(categories),
                'total_places_found': total_places,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'results_by_category': all_results
        }

        print("-" * 60)
        print(f"Chalo Specific Search Complete!")
        print(f"Total places found: {total_places}")

        return summary

    def get_cache_key(self, origin_address: str, categories: List[str]) -> str:
        """Generate a cache key for the search"""
        key_string = f"{origin_address}_{','.join(sorted(categories))}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def save_results_to_file(self, results: Dict, origin_address: str) -> str:
        """Save search results to a JSON file for review"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        safe_location = origin_address.replace(' ', '_').replace(',', '').replace('/', '_')
        filename = f"search_results_{safe_location}_{timestamp}.json"
        filepath = os.path.join('search_results', filename)
        
        # Create directory if it doesn't exist
        os.makedirs('search_results', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Search results saved to: {filepath}")
        return filepath
    
    def load_cached_results(self, cache_key: str) -> Optional[Dict]:
        """Load cached results if they exist and are recent (within 1 hour)"""
        cache_file = os.path.join('cache', f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
            
        # Check if cache is recent (within 1 hour)
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age > 3600:  # 1 hour in seconds
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def save_cached_results(self, cache_key: str, results: Dict):
        """Save results to cache"""
        os.makedirs('cache', exist_ok=True)
        cache_file = os.path.join('cache', f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def search_all_categories(self, origin_address: str, search_radius_miles: float = 2.5) -> Dict:
        """Search all categories and return organized results with caching"""
        # TESTING MODE: Check if testing mode is enabled
        if self.testing_mode:
            print(f"TESTING MODE: Using saved Manhattan data for {origin_address}")
            return self.load_testing_data()
        
        cache_key = self.get_cache_key(origin_address, CHALO_CATEGORIES)
        
        # Try to load from cache first
        cached_results = self.load_cached_results(cache_key)
        if cached_results:
            print(f"Using cached results for {origin_address}")
            return cached_results
        
        # If no cache, perform search
        results = self.search_specific_categories(origin_address, CHALO_CATEGORIES, search_radius_miles)
        
        # Save results to file for review
        self.save_results_to_file(results, origin_address)
        
        # Save to cache
        self.save_cached_results(cache_key, results)
        
        return results 
   # TESTING MODE: Methods for testing mode functionality
    def set_testing_mode(self, enabled: bool):
        """Enable or disable testing mode"""
        self.testing_mode = enabled
        print(f"Testing mode {'enabled' if enabled else 'disabled'}")
    
    def load_testing_data(self) -> Dict:
        """Load saved Manhattan search results for testing"""
        try:
            with open(self.testing_data_file, 'r') as f:
                data = json.load(f)
                print(f"Loaded testing data: {data['search_metadata']['total_places_found']} places")
                return data
        except FileNotFoundError:
            print(f"Testing data file not found: {self.testing_data_file}")
            # Return empty structure if file not found
            return {
                "search_metadata": {
                    "origin_address": "manhattan, NY",
                    "search_radius_meters": 4023,
                    "search_radius_miles": 2.5,
                    "itinerary_radius_meters": 2414,
                    "itinerary_radius_miles": 1.5,
                    "categories_searched": 9,
                    "total_places_found": 0,
                    "timestamp": "testing_mode"
                },
                "results_by_category": {}
            }
        except Exception as e:
            print(f"Error loading testing data: {e}")
            return {
                "search_metadata": {
                    "origin_address": "manhattan, NY",
                    "search_radius_meters": 4023,
                    "search_radius_miles": 2.5,
                    "itinerary_radius_meters": 2414,
                    "itinerary_radius_miles": 1.5,
                    "categories_searched": 9,
                    "total_places_found": 0,
                    "timestamp": "testing_mode_error"
                },
                "results_by_category": {}
            }