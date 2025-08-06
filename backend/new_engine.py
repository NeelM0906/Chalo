import requests
import json
import os
import time
import hashlib
import concurrent.futures
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# ==============================================================================
# Chalo Search Parameters (for compatibility)
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
        # Testing mode functionality
        self.testing_mode = False
        self.testing_data_file = "search_results/search_results_manhattan_NY_20250724_185116.json"

    def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """Convert address to latitude/longitude coordinates"""
        params = {'address': address, 'key': self.api_key}
        
        try:
            response = requests.get(GEOCODING_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                formatted_address = data['results'][0]['formatted_address']
                print(f"Geocoded: {formatted_address}")
                return location['lat'], location['lng']
            else:
                print(f"Geocoding Error for {address}: {data['status']} - {data.get('error_message', 'No error message.')}")
                return None, None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {address}: {e}")
            return None, None

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
                return float(distance_value)  # Returns distance in meters
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Distance calculation failed: {e}")
            return None

    def search_category(self, lat: float, lng: float, category: str, min_rating: float = 4.4) -> List[Dict]:
        """Search for places in a specific category and filter by rating"""
        params = {
            'location': f'{lat},{lng}',
            'type': category,
            'rankby': 'distance',
            'key': self.api_key
        }
        
        response = requests.get(NEARBY_SEARCH_BASE_URL, params=params)
        data = response.json()
        
        # Get place IDs first, then fetch detailed information
        place_ids = []
        if data.get('results'):
            for result in data['results']:
                rating = result.get('rating')
                if rating is not None and rating >= min_rating:
                    place_ids.append(result['place_id'])
        
        # Fetch detailed place information including photos
        filtered_results = []
        for place_id in place_ids[:10]:  # Limit to top 10 to save API calls
            time.sleep(0.2)  # Rate limiting
            place_details = self.get_place_details(place_id)
            if place_details:
                # Calculate distance from origin
                place_location = place_details.get('geometry', {}).get('location', {})
                place_lat = place_location.get('lat')
                place_lng = place_location.get('lng')
                
                if place_lat and place_lng:
                    time.sleep(0.1)  # Rate limiting
                    distance_meters = self.calculate_distance(lat, lng, place_lat, place_lng)
                    
                    if distance_meters is not None:
                        place_details['distance_meters'] = distance_meters
                        place_details['distance_miles'] = round(distance_meters / 1609.34, 2)
                        place_details['search_category'] = category
                        
                        # Format the place data properly
                        formatted_place = self.format_place_data(place_details, lat, lng)
                        if formatted_place:
                            filtered_results.append(formatted_place)
        
        # Sort by distance (closest first)
        filtered_results.sort(key=lambda x: x.get('distance_meters', float('inf')))
        return filtered_results

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
                result = data['result']

                return result
            else:
                print(f"Place details error: {data['status']}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Place details request failed: {e}")
            return None

    def calculate_distance_between_places(self, place1: Dict, place2: Dict) -> Optional[float]:
        """Calculate distance between two places"""
        place1_location = place1.get('geometry', {}).get('location', {})
        place2_location = place2.get('geometry', {}).get('location', {})
        
        lat1 = place1_location.get('lat')
        lng1 = place1_location.get('lng')
        lat2 = place2_location.get('lat')
        lng2 = place2_location.get('lng')
        
        if not all([lat1, lng1, lat2, lng2]):
            return None
        
        time.sleep(0.1)  # Rate limiting
        return self.calculate_distance(lat1, lng1, lat2, lng2)

    def find_clustered_places(self, results_by_category: Dict, max_distance_miles: float = 0.5) -> List[List[Dict]]:
        """Find places that are clustered within max_distance_miles of each other"""
        all_places = []
        
        # Flatten all places with category info, limit to top 3 per category for efficiency
        for category, places in results_by_category.items():
            for place in places[:3]:  # Only use top 3 places per category
                place['category_name'] = category
                all_places.append(place)
        
        if len(all_places) < 2:
            return []
        
        print(f"   Analyzing {len(all_places)} top-rated places for clustering...")
        
        max_distance_meters = max_distance_miles * 1609.34
        
        # Simple approach: find the best starting point and build cluster around it
        best_cluster = []
        
        for i, center_place in enumerate(all_places):
            cluster = [center_place]
            
            # Find all places within max_distance of this center place
            for j, other_place in enumerate(all_places):
                if i != j:
                    distance_meters = self.calculate_distance_between_places(center_place, other_place)
                    if distance_meters and distance_meters <= max_distance_meters:
                        cluster.append(other_place)
            
            # If this cluster is better than our current best, use it
            if len(cluster) > len(best_cluster):
                best_cluster = cluster
                
            # If we found a good cluster, stop searching to save API calls
            if len(cluster) >= 4:
                break
        
        return [best_cluster] if len(best_cluster) > 1 else []

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
        
        # Convert keyword to Google Places API type
        category_type = self.keyword_to_place_type(keyword)
        results = self.search_category(user_lat, user_lng, category_type, min_rating=4.4)
        
        # Filter by search radius - results are already formatted by search_category
        filtered_results = []
        for result in results:
            if result.get('distance_meters', float('inf')) <= search_radius_meters:
                filtered_results.append(result)

        # Sort by rating and distance
        filtered_results.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', float('inf'))))
        return category_query, filtered_results[:10]  # Return top 10 results

    def keyword_to_place_type(self, keyword: str) -> str:
        """Convert keyword to Google Places API type"""
        keyword_mapping = {
            'restaurants': 'restaurant',
            'cafes and bakeries': 'cafe',
            'parks': 'park',
            'delis': 'restaurant',  # Delis are often categorized as restaurants
            'thrift stores': 'store',
            'tourist attractions': 'tourist_attraction',
            'museums': 'museum',
            'galleries': 'art_gallery',
            'markets': 'store'
        }
        return keyword_mapping.get(keyword, keyword)

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

    def format_place_data(self, place_result: Dict, origin_lat: float, origin_lng: float) -> Optional[Dict]:
        """Format place data into Chalo structure"""
        try:
            place_location = place_result.get('geometry', {}).get('location', {})
            place_lat = place_location.get('lat')
            place_lng = place_location.get('lng')
            
            if not place_lat or not place_lng:
                return None

            # Use existing distance if available, otherwise calculate
            distance_meters = place_result.get('distance_meters')
            if distance_meters is None:
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
                'address': place_result.get('formatted_address') or place_result.get('vicinity'),
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
        for category in categories:
            print(f"Searching {category}...")
            category_query, results = self.process_category_search(category, origin_address, search_radius_meters)
            all_results[category] = results
            print(f"✓ Completed: {category} - Found {len(results)} places")

        # Create summary
        total_places = sum(len(results) for results in all_results.values())
        summary = {
            'search_metadata': {
                'origin_address': origin_address,
                'search_radius_meters': search_radius_meters,
                'search_radius_miles': search_radius_miles,
                'itinerary_radius_meters': ITINERARY_RADIUS_METERS,
                'itinerary_radius_miles': ITINERARY_RADIUS_METERS / 1609.34,
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
        """Search all categories and return organized results - CACHING DISABLED FOR TESTING"""
        # TESTING MODE: Check if testing mode is enabled
        if self.testing_mode:
            print(f"TESTING MODE: Using saved Manhattan data for {origin_address}")
            return self.load_testing_data()
        

        
        # Always perform fresh search (no cache check)
        results = self.search_specific_categories(origin_address, CHALO_CATEGORIES, search_radius_miles)
        
        # Save results to file for review
        self.save_results_to_file(results, origin_address)
        
        # Skip saving to cache for testing
        # self.save_cached_results(cache_key, results)
        
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
                    "search_radius_meters": SEARCH_RADIUS_METERS,
                    "search_radius_miles": 2.5,
                    "itinerary_radius_meters": ITINERARY_RADIUS_METERS,
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
                    "search_radius_meters": SEARCH_RADIUS_METERS,
                    "search_radius_miles": 2.5,
                    "itinerary_radius_meters": ITINERARY_RADIUS_METERS,
                    "itinerary_radius_miles": 1.5,
                    "categories_searched": 9,
                    "total_places_found": 0,
                    "timestamp": "testing_mode_error"
                },
                "results_by_category": {}
            }

    def select_best_itinerary(self, clusters: List[List[Dict]], selected_categories: List[Tuple], target_spots: int = 5) -> Optional[List[Dict]]:
        """Select the best itinerary from available clusters"""
        category_names = [name for _, name in selected_categories]
        best_itinerary = None
        best_score = 0
        
        for cluster in clusters:
            # Check category representation
            cluster_categories = set(place['category_name'] for place in cluster)
            category_coverage = len(cluster_categories.intersection(set(category_names)))
            
            # Select one place per category, prioritizing higher ratings
            itinerary = []
            used_categories = set()
            
            # Sort cluster by rating (highest first)
            sorted_cluster = sorted(cluster, key=lambda x: x.get('rating', 0), reverse=True)
            
            # First pass: one place per category
            for place in sorted_cluster:
                if place['category_name'] not in used_categories and len(itinerary) < target_spots:
                    itinerary.append(place)
                    used_categories.add(place['category_name'])
            
            # Second pass: fill remaining spots with highest-rated places
            for place in sorted_cluster:
                if place not in itinerary and len(itinerary) < target_spots:
                    itinerary.append(place)
            
            # Score this itinerary
            score = category_coverage * 10 + len(itinerary)  # Prioritize category coverage
            
            if score > best_score:
                best_score = score
                best_itinerary = itinerary
        
        return best_itinerary

    def generate_itinerary(self, results_by_category: Dict, selected_categories: List[Tuple]) -> Optional[List[Dict]]:
        """Generate a walking itinerary from search results"""
        print("\n" + "="*60)
        print("GENERATING ITINERARY")
        print("="*60)
        
        # Try tight clustering first (0.5 miles)
        print("🔍 Looking for tightly clustered places (≤0.5 miles apart)...")
        tight_clusters = self.find_clustered_places(results_by_category, max_distance_miles=0.5)
        
        itinerary = None
        if tight_clusters:
            itinerary = self.select_best_itinerary(tight_clusters, selected_categories, target_spots=5)
            if itinerary:
                print(f"   Found tight cluster with {len(itinerary)} places")
        
        # If no good tight cluster, try looser clustering (1.0 miles)
        if not itinerary or len(itinerary) < 3:
            print("🔍 Expanding search to moderately spaced places (≤1.0 miles apart)...")
            loose_clusters = self.find_clustered_places(results_by_category, max_distance_miles=1.0)
            
            if loose_clusters:
                itinerary = self.select_best_itinerary(loose_clusters, selected_categories, target_spots=5)
                if itinerary:
                    print(f"   Found loose cluster with {len(itinerary)} places")
        
        if not itinerary:
            print("❌ Could not generate a suitable walking itinerary")
            return None
        
        # Calculate walking route distances (only between consecutive stops)
        print("📏 Calculating walking distances between consecutive stops...")
        for i in range(len(itinerary) - 1):
            distance_meters = self.calculate_distance_between_places(itinerary[i], itinerary[i+1])
            if distance_meters:
                itinerary[i]['next_stop_distance_miles'] = round(distance_meters / 1609.34, 2)
            else:
                itinerary[i]['next_stop_distance_miles'] = None
        
        return itinerary

    def display_itinerary(self, itinerary: Optional[List[Dict]]):
        """Display the generated itinerary"""
        if not itinerary:
            return
        
        print("\n" + "="*60)
        print("🗺️  SUGGESTED WALKING ITINERARY")
        print("="*60)
        
        total_walking_distance = 0
        categories_covered = set()
        
        for i, place in enumerate(itinerary, 1):
            name = place.get('name', 'N/A')
            category = place.get('category_name', 'N/A')
            rating = place.get('rating', 'N/A')
            vicinity = place.get('address', place.get('vicinity', 'N/A'))
            
            categories_covered.add(category)
            
            print(f"\n{i}. {name}")
            print(f"   🏷️  {category}")
            print(f"   ⭐ {rating}")
            print(f"   📍 {vicinity}")
            
            # Show walking distance to next stop
            next_distance = place.get('next_stop_distance_miles')
            if next_distance is not None:
                total_walking_distance += next_distance
                print(f"   🚶 Walk {next_distance} miles to next stop")
            elif i < len(itinerary):
                print(f"   🚶 Walk to next stop")
        
        print("\n" + "-"*60)
        print("📊 ITINERARY SUMMARY")
        print("-"*60)
        print(f"🎯 Total stops: {len(itinerary)}")
        print(f"🏷️  Categories covered: {len(categories_covered)} ({', '.join(sorted(categories_covered))})")
        if total_walking_distance > 0:
            print(f"🚶 Total walking distance: {round(total_walking_distance, 2)} miles")
        print(f"⏱️  Estimated time: {len(itinerary) * 30}-{len(itinerary) * 45} minutes")


# ==============================================================================
# CLI Interface (for standalone usage)
# ==============================================================================

def main():
    """CLI interface for standalone usage"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY environment variable not found")
        return
    
    # Initialize search engine
    search_engine = ChaloSearchEngine(api_key)
    
    address = input("Enter address: ").strip()
    if not address:
        print("No address provided")
        return
    
    lat, lng = search_engine.geocode_address(address)
    if not lat:
        print("Geocoding failed")
        return
    
    # Available categories
    available_categories = {
        '1': ('cafe', 'Cafes'),
        '2': ('restaurant', 'Restaurants'), 
        '3': ('park', 'Parks'),
        '4': ('museum', 'Museums'),
        '5': ('art_gallery', 'Art Galleries'),
        '6': ('tourist_attraction', 'Tourist Attractions')
    }
    
    print("\nAvailable categories:")
    for key, (_, display_name) in available_categories.items():
        print(f"{key}. {display_name}")
    
    selected = input("\nSelect categories (e.g., 1,3 for cafes and parks): ").strip()
    if not selected:
        print("No categories selected")
        return
    
    # Parse selected categories
    selected_keys = [key.strip() for key in selected.split(',')]
    selected_categories = []
    
    for key in selected_keys:
        if key in available_categories:
            category_type, display_name = available_categories[key]
            selected_categories.append((category_type, display_name))
        else:
            print(f"Invalid selection: {key}")
            return
    
    print(f"\nSearching near: {address}")
    print(f"Categories: {', '.join([name for _, name in selected_categories])}")
    print("Filtering: Places with rating 4.4 and above only")
    
    # Search all selected categories and organize by category
    results_by_category = {}
    all_results = []
    
    for category_type, display_name in selected_categories:
        print(f"Searching {display_name.lower()}...")
        results = search_engine.search_category(lat, lng, category_type, min_rating=4.4)
        
        # Convert to the expected format
        formatted_results = []
        for result in results:
            formatted_place = search_engine.format_place_data(result, lat, lng)
            if formatted_place:
                formatted_results.append(formatted_place)
        
        print(f"  Found {len(formatted_results)} highly-rated {display_name.lower()}")
        results_by_category[display_name] = formatted_results
        all_results.extend(formatted_results)
    
    # Save results organized by category
    organized_results = {
        "search_info": {
            "location": address,
            "coordinates": {"lat": lat, "lng": lng},
            "categories_searched": [name for _, name in selected_categories],
            "min_rating_filter": 4.4,
            "total_places_found": len(all_results)
        },
        "results_by_category": {}
    }
    
    for display_name in [name for _, name in selected_categories]:
        category_results = results_by_category[display_name]
        organized_results["results_by_category"][display_name.lower()] = {
            "count": len(category_results),
            "places": category_results
        }
    
    with open('search_results.json', 'w') as f:
        json.dump(organized_results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("SEARCH SUMMARY")
    print("="*60)
    print(f"📍 Location: {address}")
    print(f"⭐ Filter: Places with rating 4.4+ only")
    print(f"📊 Total places found: {len(all_results)}")
    print("\nBreakdown by category:")
    for display_name in [name for _, name in selected_categories]:
        count = len(results_by_category[display_name])
        print(f"  • {display_name}: {count} places")
    
    # Show results organized by category
    if all_results:
        print("\n" + "="*60)
        print("DETAILED RESULTS")
        print("="*60)
        
        for display_name in [name for _, name in selected_categories]:
            category_results = results_by_category[display_name]
            if category_results:
                print(f"\n🏷️  {display_name.upper()}")
                print("-" * 30)
                for i, result in enumerate(category_results[:3], 1):  # Show top 3 per category
                    name = result.get('name', 'N/A')
                    vicinity = result.get('address', 'N/A')
                    rating = result.get('rating', 'N/A')
                    distance_miles = result.get('distance_miles')
                    
                    print(f"  {i}. {name}")
                    print(f"     📍 {vicinity}")
                    print(f"     ⭐ {rating}")
                    if distance_miles is not None:
                        print(f"     🚶 {distance_miles} miles")
                    print()
            else:
                print(f"\n🏷️  {display_name.upper()}")
                print("-" * 30)
                print("  No highly-rated places found in this category")
                print()
    else:
        print("\nNo places found with rating 4.4 or above in the selected categories.")
        return
    
    # Generate and display itinerary
    itinerary = search_engine.generate_itinerary(results_by_category, selected_categories)
    search_engine.display_itinerary(itinerary)
    
    # Save itinerary to results
    if itinerary:
        organized_results["suggested_itinerary"] = {
            "total_stops": len(itinerary),
            "categories_covered": len(set(place['category_name'] for place in itinerary)),
            "places": itinerary
        }
        
        # Re-save with itinerary included
        with open('search_results.json', 'w') as f:
            json.dump(organized_results, f, indent=2)

if __name__ == "__main__":
    main()