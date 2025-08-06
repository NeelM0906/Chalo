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
    
    def get_price_range(self, place: Dict) -> str:
        """Convert Google Places price_level to our price ranges"""
        price_level = place.get('price_level')
        if price_level is None or price_level == 0:
            return "Varies"
        elif price_level == 1:
            return "10-20"
        elif price_level == 2:
            return "20-50"
        elif price_level >= 3:
            return "50+"
        else:
            return "Varies"
    
    def matches_price_filter(self, place: Dict, max_price_level: Optional[str]) -> bool:
        """Check if place matches the price filter"""
        if not max_price_level:
            return True
        
        place_price_range = self.get_price_range(place)
        
        # If place has no price info, include it
        if place_price_range == "Varies":
            return True
        
        # Define price hierarchy for filtering
        price_hierarchy = ["10-20", "20-50", "50+"]
        
        try:
            max_price_index = price_hierarchy.index(max_price_level)
            place_price_index = price_hierarchy.index(place_price_range)
            return place_price_index <= max_price_index
        except ValueError:
            # If price level not in hierarchy, include it
            return True

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
    
    def calculate_distance_between_places(self, place1: Dict, place2: Dict) -> float:
        """Calculate distance in meters between two places using Haversine formula"""
        import math
        
        lat1 = place1.get('latitude')
        lon1 = place1.get('longitude')
        lat2 = place2.get('latitude')
        lon2 = place2.get('longitude')
        
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0
        
        # Haversine formula
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_area_density(self, total_places: int, search_radius_miles: float) -> str:
        """Determine area density: dense, moderate, or sparse"""
        area_sq_miles = math.pi * (search_radius_miles ** 2)
        places_per_sq_mile = total_places / area_sq_miles
        
        print(f"Density calculation: {total_places} places in {area_sq_miles:.2f} sq miles = {places_per_sq_mile:.1f} places/sq mile")
        
        if places_per_sq_mile >= 10:  # Dense urban areas like Soho, Manhattan (85 places in 7.07 sq miles = 12 places/sq mile)
            return "dense"
        elif places_per_sq_mile >= 5:  # Moderate density suburbs/neighborhoods
            return "moderate" 
        else:  # Sparse rural or spread-out areas
            return "sparse"
    
    def validate_route_quality(self, places: List[Dict]) -> bool:
        """Check route quality based on actual walking time constraints that matter to users"""
        if len(places) < 2:
            return True
        
        # Quality factors that actually matter to users
        total_walking_time = 0
        max_single_walk = 0
        walking_details = []
        
        for i in range(1, len(places)):
            distance_meters = self.calculate_distance_between_places(places[i-1], places[i])
            walking_time = self.calculate_walking_time(distance_meters)
            distance_miles = distance_meters / 1609.34
            
            total_walking_time += walking_time
            max_single_walk = max(max_single_walk, walking_time)
            walking_details.append(f"{distance_miles:.2f}mi ({walking_time}min)")
        
        # Realistic constraints that users care about
        total_time_ok = total_walking_time <= 45  # Max 45 min total walking
        max_walk_ok = max_single_walk <= 25       # No single walk > 25 min (adjusted from 20)
        variety_ok = len(places) >= 3             # Minimum variety
        
        print(f"Route quality check:")
        print(f"  Walking segments: {' -> '.join(walking_details)}")
        print(f"  Total walking time: {total_walking_time}min ({'✓' if total_time_ok else '✗'} ≤45min)")
        print(f"  Max single walk: {max_single_walk}min ({'✓' if max_walk_ok else '✗'} ≤25min)")
        print(f"  Place variety: {len(places)} places ({'✓' if variety_ok else '✗'} ≥3)")
        
        result = total_time_ok and max_walk_ok and variety_ok
        print(f"Route quality result: {'✓ PASS' if result else '✗ FAIL'}")
        return result
    
    def estimate_itinerary_duration(self, places: List[Dict]) -> int:
        """Estimate total duration for an itinerary"""
        if not places:
            return 0
        
        total_duration = 0
        
        for i, place in enumerate(places):
            # Add visit time based on place type
            category = self.categorize_place(place)
            if category in ['Restaurant', 'Cafe']:
                visit_time = random.randint(30, 45)  # Longer for food places
            elif category in ['Museum', 'Gallery']:
                visit_time = random.randint(25, 40)  # Medium for cultural places
            elif category == 'Park':
                visit_time = random.randint(20, 35)  # Medium for parks
            else:
                visit_time = random.randint(15, 30)  # Shorter for shops, etc.
            
            total_duration += visit_time
            
            # Add walking time to next place
            if i < len(places) - 1:
                distance_meters = self.calculate_distance_between_places(places[i], places[i + 1])
                walking_time = self.calculate_walking_time(distance_meters)
                total_duration += walking_time
        
        return total_duration
    
    def optimize_stop_order(self, places: List[Dict], max_distance_miles: float = 1.5, total_places_found: int = 50) -> List[Dict]:
        """Optimize stop order for minimal walking time and logical flow"""
        if len(places) <= 2:
            return places
        
        print(f"Optimizing route for {len(places)} places based on walking efficiency")
        
        # Simple but effective: greedy nearest-neighbor with quality weighting
        optimized = [places[0]]  # Start with first place
        remaining = places[1:].copy()
        
        while remaining:
            current_place = optimized[-1]
            best_next = None
            best_score = -1
            
            for place in remaining:
                distance_meters = self.calculate_distance_between_places(current_place, place)
                walking_time = self.calculate_walking_time(distance_meters)
                
                # Score based on: shorter walking time = higher score, better rating = higher score
                # Prioritize walking efficiency (70%) over place rating (30%)
                walking_score = max(0, (20 - walking_time) / 20)  # 0-1 scale, 20min walk = 0 score
                rating_score = (place.get('rating', 3.0) - 3.0) / 2.0  # -1 to 1 scale
                
                combined_score = 0.7 * walking_score + 0.3 * rating_score
                
                if combined_score > best_score:
                    best_next = place
                    best_score = combined_score
            
            # Always pick the best remaining option
            if best_next:
                optimized.append(best_next)
                remaining.remove(best_next)
            else:
                # Fallback: pick closest by walking time
                closest = min(remaining, key=lambda p: self.calculate_walking_time(
                    self.calculate_distance_between_places(current_place, p)
                ))
                optimized.append(closest)
                remaining.remove(closest)
        
        print(f"Route optimized: prioritized walking efficiency and place quality")
        return optimized
    
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
    
    def create_mixed_itinerary(self, places_by_category: Dict, location: str, itinerary_index: int, 
                              max_price_level: Optional[str] = None, max_distance_miles: float = 1.5) -> Optional[Dict]:
        """Create a naturally mixed itinerary with diverse place types"""

        # Convert max_distance_miles to meters
        max_distance_meters = max_distance_miles * 1609.34
        
        # Pool all places and apply filters
        all_places = []
        for category, places in places_by_category.items():
            for place in places:
                # Apply distance filter with safety check
                distance_meters = place.get('distance_meters', 0)
                if distance_meters is not None and distance_meters <= max_distance_meters:
                    # Apply price filter
                    if self.matches_price_filter(place, max_price_level):
                        all_places.append(place)
        
        # Adaptive minimum place threshold based on search radius and availability
        total_places_found = len(all_places)

        
        if max_distance_miles >= 3.0:
            min_places_required = 1  # Allow micro-itineraries for large search areas

        elif total_places_found < 6:
            min_places_required = 1  # Allow single-stop itineraries for very sparse areas

        elif total_places_found < 10:
            min_places_required = 2  # Relax for sparse areas
            print(f"Debug: Using min_places_required=2 for low-density area")
        else:
            min_places_required = 3  # Standard requirement
            print(f"Debug: Using min_places_required=3 for standard area")
        
        if len(all_places) < min_places_required:
            print(f"Not enough places within itinerary radius: {len(all_places)} (minimum: {min_places_required})")
            return None
        
        # Shuffle for variety
        random.shuffle(all_places)
        
        # Special handling for micro-itineraries when few places available OR for dense areas with quality options
        density = self.calculate_area_density(total_places_found, max_distance_miles)
        print(f"Debug: total_places_found={total_places_found}, min_places_required={min_places_required}, density={density}")
        
        micro_itinerary_condition = (total_places_found <= 10 and min_places_required <= 2) or (density == "dense" and len(all_places) >= 20)
        print(f"Debug: Checking micro-itinerary condition: {micro_itinerary_condition}")
        
        if micro_itinerary_condition and density == "dense":
            print(f"Debug: Dense area micro-itinerary - selecting quality places")
            # For dense areas, pick 2-3 high-quality places close together
            quality_places = sorted(all_places, key=lambda x: -(x.get('rating', 3.0)))[:min(6, len(all_places))]
            selected_places = quality_places[:min(3, len(quality_places))]
            if selected_places:
                print(f"Creating dense-area micro-itinerary with {len(selected_places)} places")
                return self.format_itinerary(selected_places, location, itinerary_index, is_micro=True)
        elif total_places_found <= 10 and min_places_required <= 2:
            print(f"Debug: Low-availability micro-itinerary condition met!")
            selected_places = all_places[:min(2, len(all_places))]
            if selected_places:
                print(f"Creating low-availability micro-itinerary with {len(selected_places)} places")
                return self.format_itinerary(selected_places, location, itinerary_index, is_micro=True)
        
        print(f"Debug: Proceeding with regular itinerary generation")
        
        # Fewer attempts needed with realistic constraints
        max_attempts = 5 if total_places_found >= 30 else 3
        print(f"Attempting to generate itinerary with {max_attempts} max attempts (realistic validation)")
        for attempt in range(max_attempts):
            # Force diversity by selecting from different broad types
            selected_places = []
            type_counts = {'food': 0, 'culture': 0, 'nature': 0, 'shopping': 0, 'misc': 0}
            max_per_type = 2  # Maximum 2 places of each type
            
            # Shuffle for variety in each attempt
            shuffled_places = all_places.copy()
            random.shuffle(shuffled_places)
            
            # First pass: try to get one of each type
            for broad_type in ['nature', 'culture', 'food', 'shopping', 'misc']:
                for place in shuffled_places:
                    if self.get_broad_type(place) == broad_type and type_counts[broad_type] == 0:
                        selected_places.append(place)
                        type_counts[broad_type] += 1
                        break
            
            # Second pass: fill remaining spots with variety, adapt target based on density
            if density == "dense":
                target_stops = min(5, len(shuffled_places))  # Dense areas: shorter distances, more efficient
            elif density == "moderate":
                target_stops = min(6, len(shuffled_places))  # Moderate: current logic
            else:  # sparse
                target_stops = min(4, len(shuffled_places))  # Sparse: longer walks, fewer stops
            for place in shuffled_places:
                if len(selected_places) >= target_stops:
                    break
                if place in selected_places:
                    continue
                    
                broad_type = self.get_broad_type(place)
                if type_counts[broad_type] < max_per_type:
                    selected_places.append(place)
                    type_counts[broad_type] += 1
            
            if len(selected_places) < min_places_required:
                continue
            
            # Sort by distance for logical walking flow
            selected_places.sort(key=lambda x: x.get('distance_meters', 0))
            
            # Optimize route order first, then validate
            selected_places = self.optimize_stop_order(selected_places, max_distance_miles, total_places_found)
            
            # Check route quality with user-focused constraints
            if not self.validate_route_quality(selected_places):
                print(f"Attempt {attempt + 1}: Route quality check failed, trying next combination")
                continue
            
            # Duration-first optimization: prioritize creating viable itineraries
            estimated_duration = self.estimate_itinerary_duration(selected_places)
            
            # For dense areas, be more flexible with duration (up to 180 min)
            density = self.calculate_area_density(total_places_found, max_distance_miles)
            max_duration = 180 if density == "dense" else 135
            
            if estimated_duration <= max_duration:
                print(f"Mixed itinerary {itinerary_index} (attempt {attempt + 1}): {[self.get_broad_type(p) for p in selected_places]}")
                print(f"Estimated duration: {estimated_duration} minutes (max: {max_duration})")
                break
            else:
                # Smart trimming: remove places that add least value
                while len(selected_places) > 2 and estimated_duration > max_duration:
                    # Remove place with lowest rating or highest walking time penalty
                    worst_place_idx = 0
                    worst_score = float('inf')
                    
                    for idx, place in enumerate(selected_places[1:], 1):  # Skip first place
                        # Score = rating (higher is better) - walking_time_penalty
                        rating = place.get('rating', 3.0)
                        prev_distance = self.calculate_distance_between_places(selected_places[idx-1], place) if idx > 0 else 0
                        walking_penalty = self.calculate_walking_time(prev_distance) * 0.5  # Convert to score penalty
                        
                        score = rating - (walking_penalty / 10)  # Lower score = worse
                        if score < worst_score:
                            worst_score = score
                            worst_place_idx = idx
                    
                    selected_places.pop(worst_place_idx)
                    estimated_duration = self.estimate_itinerary_duration(selected_places)
                
                if estimated_duration <= max_duration and len(selected_places) >= 2:
                    print(f"Mixed itinerary {itinerary_index} (attempt {attempt + 1}, optimized): {[self.get_broad_type(p) for p in selected_places]}")
                    print(f"Final duration: {estimated_duration} minutes")
                    break
                else:
                    print(f"Attempt {attempt + 1}: Could not optimize duration under {max_duration} minutes")
                    continue
        else:
            print(f"Could not create compliant itinerary after {max_attempts} attempts")
            # Fallback: create simple high-quality itinerary if we have good places
            if len(all_places) >= 3:
                print(f"Fallback: creating simple high-quality 3-place itinerary")
                best_places = sorted(all_places, key=lambda x: -(x.get('rating', 3.0)))[:3]
                # Sort by distance for logical flow
                best_places.sort(key=lambda x: x.get('distance_meters', 0))
                return self.format_itinerary(best_places, location, itinerary_index, is_micro=False)
            return None
        
        return self.format_itinerary(selected_places, location, itinerary_index, is_micro=False)
    
    def format_itinerary(self, selected_places: List[Dict], location: str, itinerary_index: int, is_micro: bool = False) -> Dict:
        """Format places into an itinerary structure"""
        # Create stops with walking times
        stops = []
        total_duration = 0
        
        for i, place in enumerate(selected_places):
            walking_time = 0 if i == 0 else self.calculate_walking_time(place.get('distance_meters'))
            stop = self.create_stop_from_place(place, walking_time)
            stops.append(stop)
            
            # Add walking time + estimated visit time (longer for micro-itineraries)
            visit_time = random.randint(45, 90) if is_micro else random.randint(20, 45)
            total_duration += walking_time + visit_time
        
        # Create appropriate titles for micro-itineraries
        if is_micro:
            title_templates = [
                f"Hidden Gem in {location}",
                f"Local Favorite in {location}",
                f"Must-Visit Spot in {location}",
                f"Discover {location}",
                f"Local Experience in {location}"
            ]
            description = f"A curated local experience in {location}. Perfect for a focused visit."
        else:
            title_templates = [
                f"Best of {location}",
                f"Explore {location} Like a Local",
                f"{location} Highlights",
                f"Discover {location}",
                f"Mixed Adventure in {location}"
            ]
            description = f"A perfect mix of local experiences in {location}."
        
        title = title_templates[itinerary_index % len(title_templates)]
        
        return {
            'id': f"itinerary-{uuid.uuid4()}",
            'title': title,
            'description': description,
            'duration_minutes': total_duration,
            'stops': stops
        }
    
    def generate_itineraries(self, search_results: Dict, location: str, preset: Optional[str] = None, 
                           max_price_level: Optional[str] = None, max_distance_miles: float = 1.5) -> List[Dict]:
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
            itinerary = self.create_mixed_itinerary(places_by_category, location, i, max_price_level, max_distance_miles)
            if itinerary:
                itineraries.append(itinerary)
        
        return itineraries[:5]  # Return up to 5 mixed itineraries
    
    def generate_custom_itineraries(self, search_results: Dict, location: str, max_distance_miles: float = 1.5) -> List[Dict]:
        """Generate custom itineraries with ZERO constraints - bulletproof method"""
        places_by_category = search_results.get('results_by_category', {})
        
        if not places_by_category:
            print("No places found in search results")
            return []
        
        print(f"🚀 CUSTOM ITINERARY GENERATION - NO CONSTRAINTS")
        print(f"Location: {location}")
        print(f"Max distance: {max_distance_miles} miles")
        
        # Flatten all places into single list
        all_places = []
        max_distance_meters = max_distance_miles * 1609.34
        
        for category_name, places in places_by_category.items():
            print(f"Category '{category_name}': {len(places)} places")
            for place in places:
                # Only filter by user's max distance
                distance_meters = place.get('distance_meters', 0)
                if distance_meters <= max_distance_meters:
                    all_places.append(place)
        
        print(f"Total places after distance filter: {len(all_places)}")
        
        if len(all_places) < 3:
            print(f"❌ Not enough places: {len(all_places)} (need minimum 3)")
            return []
        
        # Create 3 different itineraries
        itineraries = []
        for i in range(3):
            print(f"\n--- Creating Custom Itinerary {i+1} ---")
            itinerary = self.create_bulletproof_custom_itinerary(all_places, location, i)
            if itinerary:
                itineraries.append(itinerary)
                print(f"✅ Custom itinerary {i+1} created successfully")
            else:
                print(f"❌ Failed to create custom itinerary {i+1}")
        
        print(f"\n🎉 Generated {len(itineraries)} custom itineraries")
        return itineraries
    
    def create_bulletproof_custom_itinerary(self, all_places: List[Dict], location: str, itinerary_index: int) -> Dict:
        """Create custom itinerary with ZERO validation - guaranteed to work"""
        
        # Shuffle for variety
        available_places = all_places.copy()
        random.shuffle(available_places)
        
        # Select 4-5 places (or all if less than 5)
        num_stops = min(5, len(available_places))
        if num_stops < 3:
            num_stops = len(available_places)  # Use whatever we have
        
        selected_places = available_places[:num_stops]
        
        # Sort by distance from origin for logical walking order
        selected_places.sort(key=lambda x: x.get('distance_meters', 0))
        
        print(f"Selected {len(selected_places)} places:")
        for i, place in enumerate(selected_places):
            name = place.get('name', 'Unknown')
            distance = place.get('distance_miles', 0)
            category = self.categorize_place(place)
            print(f"  {i+1}. {name} ({category}) - {distance} miles")
        
        # Create stops directly - NO VALIDATION
        stops = []
        for i, place in enumerate(selected_places):
            # Calculate walking time to this stop (0 for first stop)
            if i == 0:
                walking_time = 0
            else:
                prev_place = selected_places[i-1]
                distance_meters = self.calculate_distance_between_places(prev_place, place)
                walking_time = self.calculate_walking_time(distance_meters)
            
            # Create stop
            stop = self.create_stop_from_place(place, walking_time)
            stops.append(stop)
        
        # Calculate total duration
        total_duration = 0
        for i, stop in enumerate(stops):
            total_duration += stop['walking_time_minutes']
            # Add visit time (30-45 minutes per stop)
            visit_time = random.randint(30, 45)
            total_duration += visit_time
        
        # Create itinerary
        itinerary = {
            'id': f"custom-itinerary-{uuid.uuid4()}",
            'title': f"Custom {location} Experience {itinerary_index + 1}",
            'description': f"A personalized itinerary in {location} with your selected categories.",
            'duration_minutes': total_duration,
            'stops': stops
        }
        
        print(f"Itinerary duration: {total_duration} minutes")
        return itinerary
    
    def generate_alternative_category_spot(
        self, 
        location: str, 
        current_category: str,
        excluded_categories: List[str],
        excluded_spot_ids: List[str],
        search_results: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Generate an alternative spot from a different category.
        
        This method finds spots from categories different from the current one,
        excluding both the current category and any categories in the excluded list.
        It prioritizes broad type diversity to ensure good category variety.
        
        Args:
            location: The location to search in
            current_category: The category to avoid (current spot's category)
            excluded_categories: List of categories to exclude from selection
            excluded_spot_ids: List of spot IDs to exclude from selection
            search_results: Optional pre-loaded search results to use
            
        Returns:
            A new stop dictionary or None if no alternatives found
        """
        if not search_results:
            # If no search results provided, we can't generate alternatives
            # In a real implementation, this would trigger a new search
            print(f"No search results provided for alternative category generation")
            return None
        
        places_by_category = search_results.get('results_by_category', {})
        
        # Get all available places, excluding current category and excluded categories
        all_excluded_categories = set(excluded_categories + [current_category])
        available_places = []
        
        for category_query, places in places_by_category.items():
            for place in places:
                place_category = self.categorize_place(place)
                
                # Skip if category is excluded
                if place_category in all_excluded_categories:
                    continue
                
                # Skip if place ID is in excluded spots (handle None place_id)
                place_id = place.get('place_id')
                if place_id and place_id in excluded_spot_ids:
                    continue
                
                # Only include places within itinerary radius
                from new_engine import ITINERARY_RADIUS_METERS
                if place.get('distance_meters', 0) <= ITINERARY_RADIUS_METERS:
                    available_places.append(place)
        
        if not available_places:
            print(f"No alternative category spots found for location: {location}")
            return None
        
        # Prioritize broad type diversity
        current_broad_type = self.BROAD_TYPE_MAPPING.get(current_category, 'misc')
        
        # Group places by broad type
        places_by_broad_type = {}
        for place in available_places:
            place_category = self.categorize_place(place)
            broad_type = self.BROAD_TYPE_MAPPING.get(place_category, 'misc')
            
            if broad_type not in places_by_broad_type:
                places_by_broad_type[broad_type] = []
            places_by_broad_type[broad_type].append(place)
        
        # Prioritize broad types different from current
        preferred_broad_types = [bt for bt in places_by_broad_type.keys() if bt != current_broad_type]
        
        selected_place = None
        
        # First, try to find a place from a different broad type
        if preferred_broad_types:
            # Sort preferred broad types by priority (nature > culture > food > shopping > misc)
            broad_type_priority = ['nature', 'culture', 'food', 'shopping', 'misc']
            preferred_broad_types.sort(key=lambda x: broad_type_priority.index(x) if x in broad_type_priority else 999)
            
            for broad_type in preferred_broad_types:
                candidates = places_by_broad_type[broad_type]
                if candidates:
                    # Sort by rating and distance for quality selection
                    candidates.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', float('inf'))))
                    selected_place = candidates[0]
                    break
        
        # If no different broad type found, fall back to any available place
        if not selected_place and available_places:
            # Sort all available places by rating and distance
            available_places.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', float('inf'))))
            selected_place = available_places[0]
        
        if not selected_place:
            return None
        
        # Calculate walking time (assume some reasonable walking time for category refresh)
        walking_time = self.calculate_walking_time(selected_place.get('distance_meters'))
        
        # Create stop from the selected place
        stop = self.create_stop_from_place(selected_place, walking_time)
        
        selected_category = self.categorize_place(selected_place)
        selected_broad_type = self.BROAD_TYPE_MAPPING.get(selected_category, 'misc')
        
        print(f"Generated alternative category spot: {selected_place.get('name')} "
              f"(Category: {selected_category}, Broad Type: {selected_broad_type})")
        
        return stop
    
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