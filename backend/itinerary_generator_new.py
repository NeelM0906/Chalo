import random
import uuid
from typing import List, Dict, Optional, Set
from datetime import datetime
import math

class ItineraryGenerator:
    """Generates itineraries from Chalo search results"""
    
    # Stock images for places without photos
    STOCK_IMAGES = [
        'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1470&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1541167760496-1628856ab772?q=80&w=1637&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1472851294608-062f824d29cc?q=80&w=1470&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1469&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1544&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1471&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1550399105-c4db5fb85c18?q=80&w=1471&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1374&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1533109721025-d1ae7de64092?q=80&w=1374&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1506126613408-4e64f3835bde?q=80&w=1470&auto=format&fit=crop'
    ]
    
    # Preset categories mapping
    PRESET_CATEGORIES = {
        "Nature & Parks": ['parks near me'],
        "Art & Culture": ['museums near me', 'galleries near me', 'tourist attractions near me'],
        "Foodie Delights": ['restaurants near me', 'cafes and bakeries near me', 'delis near me'],
        "Historical Landmarks": ['tourist attractions near me'],
        "Shopping & Boutiques": ['thrift stores near me', 'markets near me']
    }
    
    # Broad type mapping for diversity in mixed itineraries
    BROAD_TYPE_MAPPING = {
        'Restaurant': 'food',
        'Cafe': 'food',
        'Bakery': 'food',
        'Deli': 'food',
        'Park': 'nature',
        'Attraction': 'culture',
        'Museum': 'culture',
        'Gallery': 'culture',
        'Shopping': 'shopping',
        'Shop': 'shopping',
        'Bookstore': 'shopping',
        'Library': 'culture',
        'Landmark': 'culture',
        'Local Spot': 'misc'
    }
    
    def __init__(self):
        self.image_index = 0
    
    def get_next_image(self) -> str:
        """Get next stock image in rotation"""
        image = self.STOCK_IMAGES[self.image_index % len(self.STOCK_IMAGES)]
        self.image_index += 1
        return image
    
    def categorize_place(self, place: Dict) -> str:
        """Determine the category for a place based on its types"""
        types = place.get('types', [])
        
        # Category mapping based on Google Place types
        category_mapping = {
            'restaurant': 'Restaurant',
            'food': 'Restaurant', 
            'meal_takeaway': 'Restaurant',
            'cafe': 'Cafe',
            'bakery': 'Bakery',
            'park': 'Park',
            'tourist_attraction': 'Attraction',
            'museum': 'Museum',
            'art_gallery': 'Gallery',
            'shopping_mall': 'Shopping',
            'store': 'Shop',
            'clothing_store': 'Shop',
            'book_store': 'Bookstore',
            'library': 'Library',
            'church': 'Landmark',
            'synagogue': 'Landmark',
            'mosque': 'Landmark',
            'amusement_park': 'Attraction',
            'zoo': 'Attraction',
            'movie_theater': 'Attraction',
            'bowling_alley': 'Attraction',
            'aquarium': 'Attraction'
        }
        
        for place_type in types:
            if place_type in category_mapping:
                return category_mapping[place_type]
        
        # Default category
        return 'Local Spot'
    
    def get_broad_type(self, place: Dict) -> str:
        """Get the broad type of a place (food, nature, culture, shopping)"""
        category = self.categorize_place(place)
        return self.BROAD_TYPE_MAPPING.get(category, 'misc')
    
    def calculate_walking_time(self, distance_meters: Optional[float]) -> int:
        """Calculate walking time in minutes based on distance"""
        if not distance_meters:
            return random.randint(5, 15)
        
        # Average walking speed: 3 mph = 1.34 m/s
        walking_speed_ms = 1.34
        time_seconds = distance_meters / walking_speed_ms
        time_minutes = max(1, round(time_seconds / 60))
        
        return min(time_minutes, 30)  # Cap at 30 minutes
    
    def create_stop_from_place(self, place: Dict, walking_time: int = 0) -> Dict:
        """Convert a place to a Stop object"""
        # Use place photo or fallback to stock image
        image_url = place.get('photo_url') or self.get_next_image()
        
        # Create description from available data
        description_parts = []
        
        if place.get('editorial_summary'):
            description_parts.append(place['editorial_summary'])
        elif place.get('latest_review'):
            description_parts.append(f"Visitor says: {place['latest_review']}")
        
        if place.get('rating'):
            rating_text = f"Rated {place['rating']}/5"
            if place.get('user_ratings_total'):
                rating_text += f" ({place['user_ratings_total']} reviews)"
            description_parts.append(rating_text)
        
        if place.get('price_level'):
            price_symbols = '$' * place['price_level']
            description_parts.append(f"Price level: {price_symbols}")
        
        description = '. '.join(description_parts) if description_parts else f"A local {self.categorize_place(place).lower()} worth exploring."
        
        return {
            'id': f"stop-{uuid.uuid4()}",
            'name': place.get('name', 'Local Spot'),
            'category': self.categorize_place(place),
            'walking_time_minutes': walking_time,
            'description': description,
            'image_url': image_url
        }
    
    def create_mixed_itinerary(self, places_by_category: Dict, location: str, itinerary_index: int) -> Optional[Dict]:
        """Create a naturally mixed itinerary with diverse place types"""
        from new_engine import ITINERARY_RADIUS_METERS
        
        # Pool all places and ensure they're within itinerary radius
        all_places = []
        for category, places in places_by_category.items():
            for place in places:
                # Only include places within 1.5 miles for final itinerary
                if place.get('distance_meters', 0) <= ITINERARY_RADIUS_METERS:
                    all_places.append(place)
        
        if len(all_places) < 3:
            print(f"Not enough places within itinerary radius: {len(all_places)}")
            return None
        
        # Shuffle for variety
        random.shuffle(all_places)
        
        # Force diversity by selecting from different broad types
        selected_places = []
        type_counts = {'food': 0, 'culture': 0, 'nature': 0, 'shopping': 0, 'misc': 0}
        max_per_type = 2  # Maximum 2 places of each type
        
        # First pass: try to get one of each type
        for broad_type in ['nature', 'culture', 'food', 'shopping', 'misc']:
            for place in all_places:
                if self.get_broad_type(place) == broad_type and type_counts[broad_type] == 0:
                    selected_places.append(place)
                    type_counts[broad_type] += 1
                    break
        
        # Second pass: fill remaining spots with variety
        target_stops = random.randint(3, 5)
        for place in all_places:
            if len(selected_places) >= target_stops:
                break
            if place in selected_places:
                continue
                
            broad_type = self.get_broad_type(place)
            if type_counts[broad_type] < max_per_type:
                selected_places.append(place)
                type_counts[broad_type] += 1
        
        if len(selected_places) < 3:
            print(f"Could not create diverse itinerary: only {len(selected_places)} places selected")
            return None
        
        print(f"Mixed itinerary {itinerary_index}: {[self.get_broad_type(p) for p in selected_places]}")
        
        # Sort by distance for logical walking flow
        selected_places.sort(key=lambda x: x.get('distance_meters', 0))
        
        # Create stops with walking times
        stops = []
        total_duration = 0
        
        for i, place in enumerate(selected_places):
            walking_time = 0 if i == 0 else self.calculate_walking_time(place.get('distance_meters'))
            stop = self.create_stop_from_place(place, walking_time)
            stops.append(stop)
            
            # Add walking time + estimated visit time
            total_duration += walking_time + random.randint(20, 45)  # 20-45 min per stop
        
        # Create mixed itinerary titles
        title_templates = [
            f"Best of {location}",
            f"Explore {location} Like a Local",
            f"{location} Highlights",
            f"Discover {location}",
            f"Mixed Adventure in {location}"
        ]
        
        title = title_templates[itinerary_index % len(title_templates)]
        description = f"A perfect mix of local experiences in {location}."
        
        return {
            'id': f"itinerary-{uuid.uuid4()}",
            'title': title,
            'description': description,
            'duration_minutes': total_duration,
            'stops': stops
        }
    
    def generate_itineraries(self, search_results: Dict, location: str, preset: Optional[str] = None) -> List[Dict]:
        """Generate ONLY mixed itineraries - no themed ones"""
        places_by_category = search_results.get('results_by_category', {})
        
        # Filter out empty categories
        places_by_category = {k: v for k, v in places_by_category.items() if v}
        
        if not places_by_category:
            return []
        
        print(f"Generating MIXED itineraries for {location}")
        
        # Always create mixed itineraries (ignore preset for now)
        itineraries = []
        for i in range(5):  # Create 5 mixed itineraries
            itinerary = self.create_mixed_itinerary(places_by_category, location, i)
            if itinerary:
                itineraries.append(itinerary)
        
        return itineraries[:5]  # Return up to 5 mixed itineraries
    
    def create_sources_from_search(self, search_results: Dict) -> List[Dict]:
        """Create source information from search results"""
        sources = []
        
        # Add Google Places as a source
        sources.append({
            'web': {
                'uri': 'https://maps.google.com',
                'title': 'Google Places & Maps'
            }
        })
        
        return sources