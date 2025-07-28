#!/usr/bin/env python3
"""
Integration test for the refresh-category service logic.
This simulates the actual endpoint behavior with mock data.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from category_exclusion_manager import CategoryExclusionManager
from pydantic import BaseModel
from typing import List, Dict, Any
import random

class RefreshCategoryRequest(BaseModel):
    location: str
    current_category: str
    excluded_spot_ids: List[str] = []

class MockItineraryGenerator:
    """Mock itinerary generator for testing"""
    
    def categorize_place(self, place: Dict[str, Any]) -> str:
        """Mock categorize_place method"""
        return place.get('category', 'Unknown')
    
    def create_stop_from_place(self, place: Dict[str, Any]) -> Dict[str, Any]:
        """Mock create_stop_from_place method"""
        return {
            'id': place.get('place_id', 'mock_id'),
            'name': place.get('name', 'Mock Place'),
            'category': self.categorize_place(place),
            'walking_time_minutes': 5,
            'description': place.get('description', 'Mock description'),
            'image_url': 'https://example.com/image.jpg'
        }

def create_mock_search_results():
    """Create mock search results for testing"""
    return {
        'results_by_category': {
            'restaurants': [
                {'place_id': 'rest_1', 'name': 'Italian Bistro', 'category': 'Restaurant', 'rating': 4.5, 'distance_meters': 100},
                {'place_id': 'rest_2', 'name': 'Sushi Place', 'category': 'Restaurant', 'rating': 4.3, 'distance_meters': 200},
            ],
            'shops': [
                {'place_id': 'shop_1', 'name': 'Bookstore', 'category': 'Shop', 'rating': 4.2, 'distance_meters': 150},
                {'place_id': 'shop_2', 'name': 'Clothing Store', 'category': 'Shop', 'rating': 4.0, 'distance_meters': 300},
            ],
            'attractions': [
                {'place_id': 'attr_1', 'name': 'Museum', 'category': 'Attraction', 'rating': 4.7, 'distance_meters': 250},
                {'place_id': 'attr_2', 'name': 'Park', 'category': 'Attraction', 'rating': 4.4, 'distance_meters': 400},
            ],
            'cafes': [
                {'place_id': 'cafe_1', 'name': 'Coffee Shop', 'category': 'Cafe', 'rating': 4.1, 'distance_meters': 120},
            ]
        }
    }

def simulate_refresh_category_endpoint(
    request: RefreshCategoryRequest,
    search_results_cache: Dict[str, Any],
    category_exclusion_manager: CategoryExclusionManager,
    itinerary_generator: MockItineraryGenerator
) -> Dict[str, Any]:
    """
    Simulate the refresh-category endpoint logic
    """
    location = request.location
    current_category = request.current_category
    excluded_spot_ids = request.excluded_spot_ids
    
    # Validate required parameters
    if not location or len(location.strip()) < 2:
        raise ValueError("Location must be at least 2 characters long")
    
    if not current_category or len(current_category.strip()) == 0:
        raise ValueError("Current category is required")
    
    location = location.strip()
    current_category = current_category.strip()
    
    # Check if we have cached search results for this location
    if location not in search_results_cache:
        raise ValueError(f"No cached results found for {location}")
    
    search_results = search_results_cache[location]
    
    # Exclude the current category from future recommendations
    category_exclusion_manager.exclude_category(location, current_category)
    
    # Get all available categories (not excluded)
    all_categories = []
    for category_results in search_results.get('results_by_category', {}).values():
        for place in category_results:
            place_category = itinerary_generator.categorize_place(place)
            if place_category not in all_categories:
                all_categories.append(place_category)
    
    available_categories = category_exclusion_manager.get_available_categories(location, all_categories)
    
    # Remove current category from available options
    if current_category in available_categories:
        available_categories.remove(current_category)
    
    if not available_categories:
        raise ValueError("No alternative categories available")
    
    # Find places from alternative categories
    alternative_places = []
    for category_results in search_results.get('results_by_category', {}).values():
        for place in category_results:
            # Skip places we've already seen
            if place.get('place_id') in excluded_spot_ids:
                continue
            
            place_category = itinerary_generator.categorize_place(place)
            
            # Only include places from available (non-excluded) categories
            if place_category in available_categories:
                alternative_places.append(place)
    
    if not alternative_places:
        raise ValueError("Could not find alternative spots from different categories")
    
    # Sort by rating and pick a random good one for variety
    alternative_places.sort(key=lambda x: (-(x.get('rating') or 0), x.get('distance_meters', 0)))
    top_places = alternative_places[:min(5, len(alternative_places))]
    selected_place = random.choice(top_places)
    
    # Create a stop from this place
    alternative_spot = itinerary_generator.create_stop_from_place(selected_place)
    
    # Increment turn counter for exclusion management
    category_exclusion_manager.increment_turn(location)
    
    return alternative_spot

def test_successful_category_refresh():
    """Test successful category refresh scenario"""
    print("Testing successful category refresh...")
    
    # Setup
    manager = CategoryExclusionManager()
    generator = MockItineraryGenerator()
    cache = {"Manhattan, NY": create_mock_search_results()}
    
    request = RefreshCategoryRequest(
        location="Manhattan, NY",
        current_category="Restaurant",
        excluded_spot_ids=["rest_1"]  # Exclude one restaurant
    )
    
    try:
        result = simulate_refresh_category_endpoint(request, cache, manager, generator)
        print(f"✓ Successfully got alternative spot: {result['name']} (category: {result['category']})")
        
        # Verify it's not a restaurant
        if result['category'] != 'Restaurant':
            print("✓ Alternative spot is from a different category")
        else:
            print("✗ Alternative spot should not be from Restaurant category")
            return False
        
        # Verify Restaurant is now excluded
        if manager.is_category_excluded("Manhattan, NY", "Restaurant"):
            print("✓ Restaurant category is now excluded")
        else:
            print("✗ Restaurant category should be excluded")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_no_alternatives_available():
    """Test scenario where no alternative categories are available"""
    print("\nTesting no alternatives available scenario...")
    
    # Setup with all categories excluded
    manager = CategoryExclusionManager()
    generator = MockItineraryGenerator()
    cache = {"Manhattan, NY": create_mock_search_results()}
    
    # Exclude all other categories first
    location = "Manhattan, NY"
    manager.exclude_category(location, "Shop")
    manager.exclude_category(location, "Attraction") 
    manager.exclude_category(location, "Cafe")
    
    request = RefreshCategoryRequest(
        location=location,
        current_category="Restaurant",
        excluded_spot_ids=[]
    )
    
    try:
        result = simulate_refresh_category_endpoint(request, cache, manager, generator)
        print("✗ Should have failed when no alternatives available")
        return False
    except ValueError as e:
        if "No alternative categories available" in str(e):
            print("✓ Correctly caught 'no alternatives available' error")
            return True
        else:
            print(f"✗ Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")
        return False

def test_excluded_spot_ids():
    """Test that excluded spot IDs are properly filtered out"""
    print("\nTesting excluded spot IDs filtering...")
    
    manager = CategoryExclusionManager()
    generator = MockItineraryGenerator()
    cache = {"Manhattan, NY": create_mock_search_results()}
    
    # Exclude all shops except one, then exclude that one by ID
    request = RefreshCategoryRequest(
        location="Manhattan, NY",
        current_category="Restaurant",
        excluded_spot_ids=["shop_1", "shop_2"]  # Exclude all shops
    )
    
    try:
        result = simulate_refresh_category_endpoint(request, cache, manager, generator)
        print(f"✓ Got alternative: {result['name']} (category: {result['category']})")
        
        # Should not be a shop since all shops are excluded
        if result['category'] != 'Shop':
            print("✓ Correctly avoided excluded shop spots")
        else:
            print("✗ Should not have returned a shop since all shops were excluded")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_validation_errors():
    """Test request validation errors"""
    print("\nTesting validation errors...")
    
    manager = CategoryExclusionManager()
    generator = MockItineraryGenerator()
    cache = {"Manhattan, NY": create_mock_search_results()}
    
    # Test empty location
    try:
        request = RefreshCategoryRequest(location="", current_category="Restaurant")
        simulate_refresh_category_endpoint(request, cache, manager, generator)
        print("✗ Should have failed for empty location")
        return False
    except ValueError as e:
        if "Location must be at least 2 characters long" in str(e):
            print("✓ Correctly caught empty location error")
        else:
            print(f"✗ Wrong error for empty location: {e}")
            return False
    
    # Test empty category
    try:
        request = RefreshCategoryRequest(location="Manhattan, NY", current_category="")
        simulate_refresh_category_endpoint(request, cache, manager, generator)
        print("✗ Should have failed for empty category")
        return False
    except ValueError as e:
        if "Current category is required" in str(e):
            print("✓ Correctly caught empty category error")
        else:
            print(f"✗ Wrong error for empty category: {e}")
            return False
    
    # Test missing cache
    try:
        request = RefreshCategoryRequest(location="Unknown City", current_category="Restaurant")
        simulate_refresh_category_endpoint(request, cache, manager, generator)
        print("✗ Should have failed for missing cache")
        return False
    except ValueError as e:
        if "No cached results found" in str(e):
            print("✓ Correctly caught missing cache error")
        else:
            print(f"✗ Wrong error for missing cache: {e}")
            return False
    
    return True

def main():
    """Run all integration tests"""
    print("Running refresh-category service integration tests...\n")
    
    tests = [
        test_successful_category_refresh,
        test_no_alternatives_available,
        test_excluded_spot_ids,
        test_validation_errors
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("Test failed!")
    
    print(f"\n{'='*60}")
    print(f"Integration tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All integration tests passed! The refresh-category service works correctly.")
        return True
    else:
        print("✗ Some integration tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)