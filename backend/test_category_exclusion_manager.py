"""
Test suite for CategoryExclusionManager.

This module contains unit tests to verify the functionality of the
CategoryExclusionManager class.
"""

import unittest
from category_exclusion_manager import CategoryExclusionManager


class TestCategoryExclusionManager(unittest.TestCase):
    """Test cases for CategoryExclusionManager functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = CategoryExclusionManager()
        self.test_location = "Manhattan, NY"
        self.test_categories = ["Restaurant", "Shop", "Attraction", "Cafe", "Museum"]
    
    def test_initial_state(self):
        """Test that manager starts with empty state."""
        self.assertEqual(len(self.manager.exclusions), 0)
        self.assertEqual(len(self.manager.location_turns), 0)
        self.assertFalse(self.manager.is_category_excluded(self.test_location, "Restaurant"))
    
    def test_exclude_category(self):
        """Test excluding a category for a location."""
        self.manager.exclude_category(self.test_location, "Restaurant")
        
        self.assertTrue(self.manager.is_category_excluded(self.test_location, "Restaurant"))
        self.assertFalse(self.manager.is_category_excluded(self.test_location, "Shop"))
        
        # Check exclusion info
        exclusion_info = self.manager.get_exclusion_info(self.test_location)
        self.assertEqual(exclusion_info["Restaurant"], 5)
    
    def test_multiple_category_exclusions(self):
        """Test excluding multiple categories for the same location."""
        self.manager.exclude_category(self.test_location, "Restaurant")
        self.manager.exclude_category(self.test_location, "Shop")
        
        self.assertTrue(self.manager.is_category_excluded(self.test_location, "Restaurant"))
        self.assertTrue(self.manager.is_category_excluded(self.test_location, "Shop"))
        self.assertFalse(self.manager.is_category_excluded(self.test_location, "Attraction"))
        
        excluded = self.manager.get_excluded_categories(self.test_location)
        self.assertIn("Restaurant", excluded)
        self.assertIn("Shop", excluded)
        self.assertEqual(len(excluded), 2)
    
    def test_location_isolation(self):
        """Test that exclusions are isolated by location."""
        location1 = "Manhattan, NY"
        location2 = "Brooklyn, NY"
        
        self.manager.exclude_category(location1, "Restaurant")
        self.manager.exclude_category(location2, "Shop")
        
        self.assertTrue(self.manager.is_category_excluded(location1, "Restaurant"))
        self.assertFalse(self.manager.is_category_excluded(location1, "Shop"))
        
        self.assertTrue(self.manager.is_category_excluded(location2, "Shop"))
        self.assertFalse(self.manager.is_category_excluded(location2, "Restaurant"))
    
    def test_turn_increment_and_expiration(self):
        """Test that categories become available after 5 turns."""
        self.manager.exclude_category(self.test_location, "Restaurant")
        
        # Category should be excluded initially
        self.assertTrue(self.manager.is_category_excluded(self.test_location, "Restaurant"))
        
        # After 4 turns, still excluded
        for i in range(4):
            self.manager.increment_turn(self.test_location)
            self.assertTrue(self.manager.is_category_excluded(self.test_location, "Restaurant"))
        
        # After 5th turn, should be available
        self.manager.increment_turn(self.test_location)
        self.assertFalse(self.manager.is_category_excluded(self.test_location, "Restaurant"))
    
    def test_get_available_categories(self):
        """Test getting available categories."""
        all_categories = ["Restaurant", "Shop", "Attraction", "Cafe"]
        
        # Initially all should be available
        available = self.manager.get_available_categories(self.test_location, all_categories)
        self.assertEqual(set(available), set(all_categories))
        
        # Exclude some categories
        self.manager.exclude_category(self.test_location, "Restaurant")
        self.manager.exclude_category(self.test_location, "Shop")
        
        available = self.manager.get_available_categories(self.test_location, all_categories)
        expected_available = ["Attraction", "Cafe"]
        self.assertEqual(set(available), set(expected_available))
    
    def test_location_key_normalization(self):
        """Test that location keys are normalized consistently."""
        # These should be treated as the same location
        location_variants = [
            "Manhattan, NY",
            "manhattan, ny",
            "  Manhattan, NY  ",
            "MANHATTAN, NY"
        ]
        
        # Exclude category for first variant
        self.manager.exclude_category(location_variants[0], "Restaurant")
        
        # Should be excluded for all variants
        for variant in location_variants:
            self.assertTrue(self.manager.is_category_excluded(variant, "Restaurant"))
    
    def test_turn_counting(self):
        """Test turn counting functionality."""
        self.assertEqual(self.manager.get_turn_count(self.test_location), 0)
        
        self.manager.increment_turn(self.test_location)
        self.assertEqual(self.manager.get_turn_count(self.test_location), 1)
        
        self.manager.increment_turn(self.test_location)
        self.assertEqual(self.manager.get_turn_count(self.test_location), 2)
    
    def test_reset_location_exclusions(self):
        """Test resetting exclusions for a location."""
        self.manager.exclude_category(self.test_location, "Restaurant")
        self.manager.exclude_category(self.test_location, "Shop")
        self.manager.increment_turn(self.test_location)
        
        # Verify exclusions exist
        self.assertTrue(self.manager.is_category_excluded(self.test_location, "Restaurant"))
        self.assertEqual(self.manager.get_turn_count(self.test_location), 1)
        
        # Reset and verify clean state
        self.manager.reset_location_exclusions(self.test_location)
        self.assertFalse(self.manager.is_category_excluded(self.test_location, "Restaurant"))
        self.assertFalse(self.manager.is_category_excluded(self.test_location, "Shop"))
        self.assertEqual(self.manager.get_turn_count(self.test_location), 0)
    
    def test_status_summary(self):
        """Test status summary functionality."""
        # Initial state
        summary = self.manager.get_status_summary()
        self.assertEqual(summary["total_locations_tracked"], 0)
        self.assertEqual(summary["total_active_exclusions"], 0)
        
        # Add some exclusions
        self.manager.exclude_category("Manhattan, NY", "Restaurant")
        self.manager.exclude_category("Manhattan, NY", "Shop")
        self.manager.exclude_category("Brooklyn, NY", "Cafe")
        
        summary = self.manager.get_status_summary()
        self.assertEqual(summary["total_locations_tracked"], 2)
        self.assertEqual(summary["total_active_exclusions"], 3)


if __name__ == "__main__":
    unittest.main()