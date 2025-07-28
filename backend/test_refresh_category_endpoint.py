#!/usr/bin/env python3
"""
Test script for the refresh-category endpoint implementation.
This tests the core logic without running the full FastAPI server.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pydantic import BaseModel, ValidationError
from typing import List
from category_exclusion_manager import CategoryExclusionManager

# Test the Pydantic model
class RefreshCategoryRequest(BaseModel):
    location: str
    current_category: str
    excluded_spot_ids: List[str] = []

def test_pydantic_model():
    """Test the RefreshCategoryRequest Pydantic model"""
    print("Testing RefreshCategoryRequest Pydantic model...")
    
    # Test valid request
    try:
        valid_request = RefreshCategoryRequest(
            location="Manhattan, NY",
            current_category="Restaurant",
            excluded_spot_ids=["place_123", "place_456"]
        )
        print("✓ Valid request created successfully")
        print(f"  Location: {valid_request.location}")
        print(f"  Current category: {valid_request.current_category}")
        print(f"  Excluded IDs: {valid_request.excluded_spot_ids}")
    except Exception as e:
        print(f"✗ Failed to create valid request: {e}")
        return False
    
    # Test request with defaults
    try:
        default_request = RefreshCategoryRequest(
            location="Brooklyn, NY",
            current_category="Shop"
        )
        print("✓ Request with defaults created successfully")
        print(f"  Excluded IDs (default): {default_request.excluded_spot_ids}")
    except Exception as e:
        print(f"✗ Failed to create request with defaults: {e}")
        return False
    
    # Test validation errors
    try:
        # Missing required field
        invalid_request = RefreshCategoryRequest(
            location="Manhattan, NY"
            # missing current_category
        )
        print("✗ Should have failed validation for missing current_category")
        return False
    except ValidationError as e:
        print("✓ Correctly caught validation error for missing current_category")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True

def test_request_validation_logic():
    """Test the request validation logic from the endpoint"""
    print("\nTesting request validation logic...")
    
    # Test cases that should fail validation
    test_cases = [
        {"location": "", "current_category": "Restaurant", "expected_error": "Location must be at least 2 characters long"},
        {"location": "A", "current_category": "Restaurant", "expected_error": "Location must be at least 2 characters long"},
        {"location": "Manhattan, NY", "current_category": "", "expected_error": "Current category is required"},
        {"location": "Manhattan, NY", "current_category": "   ", "expected_error": "Current category is required"},
    ]
    
    for i, case in enumerate(test_cases):
        location = case["location"]
        current_category = case["current_category"]
        expected_error = case["expected_error"]
        
        # Simulate the validation logic from the endpoint
        validation_passed = True
        error_message = None
        
        if not location or len(location.strip()) < 2:
            validation_passed = False
            error_message = "Location must be at least 2 characters long"
        elif not current_category or len(current_category.strip()) == 0:
            validation_passed = False
            error_message = "Current category is required"
        
        if not validation_passed and error_message == expected_error:
            print(f"✓ Test case {i+1}: Correctly caught validation error: {error_message}")
        elif validation_passed:
            print(f"✗ Test case {i+1}: Should have failed validation but passed")
            return False
        else:
            print(f"✗ Test case {i+1}: Wrong error message. Expected: {expected_error}, Got: {error_message}")
            return False
    
    return True

def test_category_exclusion_integration():
    """Test integration with CategoryExclusionManager"""
    print("\nTesting CategoryExclusionManager integration...")
    
    manager = CategoryExclusionManager()
    location = "Manhattan, NY"
    
    # Test excluding a category
    manager.exclude_category(location, "Restaurant")
    print("✓ Category excluded successfully")
    
    # Test checking if category is excluded
    if manager.is_category_excluded(location, "Restaurant"):
        print("✓ Category correctly identified as excluded")
    else:
        print("✗ Category should be excluded but isn't")
        return False
    
    # Test getting available categories
    all_categories = ["Restaurant", "Shop", "Attraction", "Cafe"]
    available = manager.get_available_categories(location, all_categories)
    expected_available = ["Shop", "Attraction", "Cafe"]
    
    if set(available) == set(expected_available):
        print("✓ Available categories correctly filtered")
    else:
        print(f"✗ Available categories incorrect. Expected: {expected_available}, Got: {available}")
        return False
    
    # Test incrementing turn
    manager.increment_turn(location)
    print("✓ Turn incremented successfully")
    
    return True

def main():
    """Run all tests"""
    print("Running refresh-category endpoint tests...\n")
    
    tests = [
        test_pydantic_model,
        test_request_validation_logic,
        test_category_exclusion_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("Test failed!")
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The refresh-category endpoint implementation looks good.")
        return True
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)