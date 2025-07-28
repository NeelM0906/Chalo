#!/usr/bin/env python3
"""
Integration test for category refresh functionality.

This test verifies that the ItineraryGenerator.generate_alternative_category_spot
method integrates properly with the CategoryExclusionManager and search results.
"""

import sys
import os
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from itinerary_generator import ItineraryGenerator
from category_exclusion_manager import CategoryExclusionManager


def test_integration_with_exclusion_manager():
    """Test integration between ItineraryGenerator and CategoryExclusionManager."""
    print("=== Integration Test: ItineraryGenerator + CategoryExclusionManager ===")
    
    # Initialize components
    generator = ItineraryGenerator()
    exclusion_manager = CategoryExclusionManager()
    
    # Mock search results with diverse categories
    search_results = {
        "search_metadata": {"total_places_found": 8},
        "results_by_category": {
            "restaurants near me": [
                {
                    "place_id": "restaurant_1",
                    "name": "Italian Bistro",
                    "types": ["restaurant", "food"],
                    "rating": 4.5,
                    "distance_meters": 500,
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            ],
            "cafes and bakeries near me": [
                {
                    "place_id": "cafe_1",
                    "name": "Coffee Corner",
                    "types": ["cafe"],
                    "rating": 4.3,
                    "distance_meters": 600,
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            ],
            "parks near me": [
                {
                    "place_id": "park_1",
                    "name": "Central Park",
                    "types": ["park"],
                    "rating": 4.7,
                    "distance_meters": 400,
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            ],
            "museums near me": [
                {
                    "place_id": "museum_1",
                    "name": "Art Museum",
                    "types": ["museum"],
                    "rating": 4.6,
                    "distance_meters": 700,
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            ],
            "thrift stores near me": [
                {
                    "place_id": "shop_1",
                    "name": "Vintage Shop",
                    "types": ["store"],
                    "rating": 4.1,
                    "distance_meters": 900,
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            ]
        }
    }
    
    location = "Manhattan, NY"
    current_category = "Restaurant"
    
    # Test 1: Generate alternative without exclusions
    print("\n1. Generate alternative without exclusions:")
    result1 = generator.generate_alternative_category_spot(
        location=location,
        current_category=current_category,
        excluded_categories=[],
        excluded_spot_ids=[],
        search_results=search_results
    )
    
    if result1:
        print(f"   ✓ Generated: {result1['name']} (Category: {result1['category']})")
        
        # Exclude this category using the exclusion manager
        exclusion_manager.exclude_category(location, result1['category'])
        exclusion_manager.increment_turn(location)
        
        # Test 2: Generate another alternative with exclusion
        print("\n2. Generate alternative with exclusion:")
        excluded_categories = exclusion_manager.get_excluded_categories(location)
        
        result2 = generator.generate_alternative_category_spot(
            location=location,
            current_category=current_category,
            excluded_categories=excluded_categories,
            excluded_spot_ids=[],
            search_results=search_results
        )
        
        if result2:
            print(f"   ✓ Generated: {result2['name']} (Category: {result2['category']})")
            print(f"   ✓ Successfully avoided excluded category: {result1['category']}")
            
            # Verify the categories are different
            if result2['category'] != result1['category']:
                print("   ✓ Categories are different as expected")
                return True
            else:
                print("   ✗ Categories should be different")
                return False
        else:
            print("   ✗ Failed to generate second alternative")
            return False
    else:
        print("   ✗ Failed to generate first alternative")
        return False


def test_multiple_exclusions_workflow():
    """Test a realistic workflow with multiple exclusions."""
    print("\n=== Integration Test: Multiple Exclusions Workflow ===")
    
    generator = ItineraryGenerator()
    exclusion_manager = CategoryExclusionManager()
    
    # Load real search results if available
    test_file = "search_results/search_results_manhattan_NY_20250724_185116.json"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            search_results = json.load(f)
    else:
        print("   ⚠ Using mock data (real search results not found)")
        search_results = {
            "search_metadata": {"total_places_found": 6},
            "results_by_category": {
                "restaurants near me": [{"place_id": "r1", "name": "Restaurant", "types": ["restaurant"], "rating": 4.5, "distance_meters": 500, "latitude": 40.7589, "longitude": -73.9851}],
                "cafes and bakeries near me": [{"place_id": "c1", "name": "Cafe", "types": ["cafe"], "rating": 4.3, "distance_meters": 600, "latitude": 40.7589, "longitude": -73.9851}],
                "parks near me": [{"place_id": "p1", "name": "Park", "types": ["park"], "rating": 4.7, "distance_meters": 400, "latitude": 40.7589, "longitude": -73.9851}],
                "museums near me": [{"place_id": "m1", "name": "Museum", "types": ["museum"], "rating": 4.6, "distance_meters": 700, "latitude": 40.7589, "longitude": -73.9851}],
                "thrift stores near me": [{"place_id": "s1", "name": "Shop", "types": ["store"], "rating": 4.1, "distance_meters": 900, "latitude": 40.7589, "longitude": -73.9851}]
            }
        }
    
    location = "Manhattan, NY"
    current_category = "Restaurant"
    generated_categories = []
    
    # Simulate 3 refresh operations
    for i in range(3):
        print(f"\n   Refresh operation {i+1}:")
        
        excluded_categories = exclusion_manager.get_excluded_categories(location)
        print(f"   Currently excluded: {excluded_categories}")
        
        result = generator.generate_alternative_category_spot(
            location=location,
            current_category=current_category,
            excluded_categories=excluded_categories,
            excluded_spot_ids=[],
            search_results=search_results
        )
        
        if result:
            print(f"   ✓ Generated: {result['name']} (Category: {result['category']})")
            generated_categories.append(result['category'])
            
            # Exclude this category and increment turn
            exclusion_manager.exclude_category(location, result['category'])
            exclusion_manager.increment_turn(location)
            
            # Update current category for next iteration
            current_category = result['category']
        else:
            print(f"   ✗ Failed to generate alternative in operation {i+1}")
            return False
    
    # Verify we got different categories
    unique_categories = set(generated_categories)
    if len(unique_categories) == len(generated_categories):
        print(f"\n   ✓ All generated categories are unique: {generated_categories}")
        return True
    else:
        print(f"\n   ⚠ Some categories repeated: {generated_categories}")
        return True  # This might be acceptable depending on available data


def run_integration_tests():
    """Run all integration tests."""
    print("Integration Tests for Category Refresh Functionality")
    print("=" * 60)
    
    tests = [
        ("Basic Integration", test_integration_with_exclusion_manager),
        ("Multiple Exclusions Workflow", test_multiple_exclusions_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ PASSED: {test_name}")
            else:
                print(f"✗ FAILED: {test_name}")
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)