# Implementation Plan

- [x] 1. Create backend category exclusion management system
  - Implement CategoryExclusionManager class with in-memory storage for tracking excluded categories per location
  - Add methods for excluding categories, checking exclusions, and managing turn-based counters
  - Create location-based key system for isolating exclusions by geographic area
  - _Requirements: 3.1, 3.2, 3.3, 4.2, 4.4_

- [x] 2. Implement backend category refresh endpoint
  - Create new `/api/refresh-category` endpoint with proper request/response models
  - Add RefreshCategoryRequest Pydantic model with location, current_category, and excluded_spot_ids fields
  - Implement request validation and error handling for invalid or missing parameters
  - _Requirements: 4.1, 2.5_

- [x] 3. Enhance ItineraryGenerator with category refresh logic
  - Add generate_alternative_category_spot method that finds spots from different categories
  - Implement category filtering logic that excludes current category and excluded categories
  - Add broad type diversity prioritization to ensure good category variety
  - Integrate with existing place search and stop creation functionality
  - _Requirements: 1.2, 4.3, 5.1, 5.2_

- [x] 4. Create CategoryRefreshButton frontend component
  - Build new React component with loading states and proper styling
  - Add distinct visual styling to differentiate from existing RefreshButton
  - Implement proper accessibility attributes and ARIA labels
  - Add hover tooltips explaining category refresh functionality
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 5. Update frontend API service with category refresh function
  - Add refreshCategory function to apiService.ts with proper TypeScript types
  - Implement error handling and response parsing for category refresh endpoint
  - Add proper request body formatting and HTTP method configuration
  - _Requirements: 4.1, 2.5_

- [x] 6. Enhance StopItem component with dual refresh functionality
  - Add new onCategoryRefresh prop and handler function
  - Integrate CategoryRefreshButton component positioned near category text
  - Update component state management to handle both refresh types simultaneously
  - Add proper loading states for both refresh operations
  - _Requirements: 2.1, 2.2, 2.4_

- [x] 7. Update ItineraryDetailModal state management
  - Add categoryRefreshingStopId state for tracking category refresh operations
  - Implement excludedCategories state array for frontend exclusion tracking
  - Add categoryExclusionTurns counter for turn-based exclusion management
  - Create handleCategoryRefresh function with proper error handling
  - _Requirements: 1.3, 3.1, 3.4_

- [x] 8. Implement frontend category exclusion tracking
  - Add logic to track excluded categories locally in modal state
  - Implement turn counter that resets exclusions after 5 operations
  - Add location-specific exclusion management that resets when location changes
  - Create helper functions for managing exclusion state updates
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 9. Add comprehensive error handling and user feedback
  - Implement error states for no alternative categories available
  - Add user-friendly error messages for different failure scenarios
  - Create fallback behavior when category refresh fails
  - Add success feedback and smooth UI transitions for successful refreshes
  - _Requirements: 1.4, 2.5, 3.5_

- [x] 10. Integrate walking time and itinerary flow updates
  - Update walking time calculations when category refresh replaces a stop
  - Ensure proper integration with existing map embed and itinerary display
  - Maintain proper stop ordering and flow after category refresh
  - Update total duration calculations for the itinerary
  - _Requirements: 1.5, 5.3, 5.5_

- [x] 11. Add proper TypeScript types and interfaces
  - Update Stop interface if needed for category refresh functionality
  - Add proper typing for all new API functions and component props
  - Create interfaces for exclusion tracking and state management
  - Ensure type safety across all new functionality
  - _Requirements: 4.1, 2.1_

- [x] 12. Implement comprehensive testing suite
  - Write unit tests for CategoryExclusionManager class methods
  - Create tests for new API endpoint with various request scenarios
  - Add component tests for CategoryRefreshButton and enhanced StopItem
  - Write integration tests for end-to-end category refresh workflow
  - Test error handling and edge cases (no alternatives, all categories excluded)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_