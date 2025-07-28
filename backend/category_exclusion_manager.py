"""
Category Exclusion Manager for tracking excluded categories per location.

This module implements the category exclusion logic that prevents the same category
from being recommended again for 5 refresh operations, ensuring variety and 
preventing repetitive suggestions.
"""

from typing import Dict, List, Optional
import hashlib


class CategoryExclusionManager:
    """
    Manages category exclusions per location with turn-based counters.
    
    This class tracks which categories have been excluded for each location
    and implements a turn-based system where categories become available
    again after 5 refresh operations.
    """
    
    def __init__(self):
        """Initialize the exclusion manager with empty storage."""
        # Structure: {location_key: {category: turns_remaining}}
        self.exclusions: Dict[str, Dict[str, int]] = {}
        # Track total turns per location for cleanup
        self.location_turns: Dict[str, int] = {}
    
    def _get_location_key(self, location: str) -> str:
        """
        Generate a consistent location key for storage.
        
        Args:
            location: The location string (e.g., "Manhattan, NY")
            
        Returns:
            A normalized location key for consistent storage
        """
        # Normalize location string: lowercase, strip whitespace
        normalized = location.lower().strip()
        # Use hash for consistent key generation and to handle special characters
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def exclude_category(self, location: str, category: str) -> None:
        """
        Exclude a category for a specific location for 5 turns.
        
        Args:
            location: The location where the category should be excluded
            category: The category to exclude (e.g., "Restaurant", "Shop")
        """
        location_key = self._get_location_key(location)
        
        # Initialize location if not exists
        if location_key not in self.exclusions:
            self.exclusions[location_key] = {}
            self.location_turns[location_key] = 0
        
        # Exclude category for 5 turns
        self.exclusions[location_key][category] = 5
        
        print(f"Excluded category '{category}' for location '{location}' (key: {location_key}) for 5 turns")
    
    def is_category_excluded(self, location: str, category: str) -> bool:
        """
        Check if a category is currently excluded for a location.
        
        Args:
            location: The location to check
            category: The category to check
            
        Returns:
            True if the category is excluded, False otherwise
        """
        location_key = self._get_location_key(location)
        
        if location_key not in self.exclusions:
            return False
        
        return self.exclusions[location_key].get(category, 0) > 0
    
    def increment_turn(self, location: str) -> None:
        """
        Increment the turn counter for a location and update exclusions.
        
        This should be called after each refresh operation to decrement
        the remaining turns for all excluded categories.
        
        Args:
            location: The location to increment turns for
        """
        location_key = self._get_location_key(location)
        
        # Increment total turns for this location (initialize if needed)
        self.location_turns[location_key] = self.location_turns.get(location_key, 0) + 1
        
        # If no exclusions exist for this location, we're done
        if location_key not in self.exclusions:
            return
        
        # Decrement turns remaining for all excluded categories
        categories_to_remove = []
        for category, turns_remaining in self.exclusions[location_key].items():
            if turns_remaining > 0:
                self.exclusions[location_key][category] = turns_remaining - 1
                if self.exclusions[location_key][category] <= 0:
                    categories_to_remove.append(category)
        
        # Remove categories that are no longer excluded
        for category in categories_to_remove:
            del self.exclusions[location_key][category]
            print(f"Category '{category}' is now available again for location '{location}'")
        
        # Clean up empty location entries
        if not self.exclusions[location_key]:
            del self.exclusions[location_key]
            del self.location_turns[location_key]
    
    def get_available_categories(self, location: str, all_categories: List[str]) -> List[str]:
        """
        Get list of categories that are not currently excluded for a location.
        
        Args:
            location: The location to check
            all_categories: List of all possible categories
            
        Returns:
            List of categories that are available (not excluded)
        """
        available = []
        for category in all_categories:
            if not self.is_category_excluded(location, category):
                available.append(category)
        
        return available
    
    def get_excluded_categories(self, location: str) -> List[str]:
        """
        Get list of currently excluded categories for a location.
        
        Args:
            location: The location to check
            
        Returns:
            List of excluded categories with their remaining turns
        """
        location_key = self._get_location_key(location)
        
        if location_key not in self.exclusions:
            return []
        
        return list(self.exclusions[location_key].keys())
    
    def get_exclusion_info(self, location: str) -> Dict[str, int]:
        """
        Get detailed exclusion information for a location.
        
        Args:
            location: The location to check
            
        Returns:
            Dictionary mapping excluded categories to their remaining turns
        """
        location_key = self._get_location_key(location)
        
        if location_key not in self.exclusions:
            return {}
        
        return self.exclusions[location_key].copy()
    
    def reset_location_exclusions(self, location: str) -> None:
        """
        Reset all exclusions for a specific location.
        
        Args:
            location: The location to reset exclusions for
        """
        location_key = self._get_location_key(location)
        
        if location_key in self.exclusions:
            del self.exclusions[location_key]
        
        if location_key in self.location_turns:
            del self.location_turns[location_key]
        
        print(f"Reset all exclusions for location '{location}'")
    
    def get_turn_count(self, location: str) -> int:
        """
        Get the total number of turns (refresh operations) for a location.
        
        Args:
            location: The location to check
            
        Returns:
            Total number of refresh operations performed for this location
        """
        location_key = self._get_location_key(location)
        return self.location_turns.get(location_key, 0)
    
    def get_status_summary(self) -> Dict:
        """
        Get a summary of the current exclusion manager status.
        
        Returns:
            Dictionary with summary information for debugging/monitoring
        """
        total_locations = len(self.exclusions)
        total_exclusions = sum(len(cats) for cats in self.exclusions.values())
        
        return {
            "total_locations_tracked": total_locations,
            "total_active_exclusions": total_exclusions,
            "locations": {
                # Convert back to readable format for debugging
                loc_key: {
                    "excluded_categories": list(cats.keys()),
                    "total_turns": self.location_turns.get(loc_key, 0)
                }
                for loc_key, cats in self.exclusions.items()
            }
        }