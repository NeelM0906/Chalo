# Requirements Document

## Introduction

This feature enhances the existing spot refresh functionality by adding the ability to refresh entire categories within itineraries. Currently, users can only refresh spots within the same category (e.g., restaurant → different restaurant). This new feature allows users to replace a spot with one from a completely different category (e.g., restaurant → shop or attraction), providing more diverse itinerary customization options.

The feature includes intelligent category exclusion logic that prevents the same category from being recommended again for 5 refresh operations, ensuring variety and preventing repetitive suggestions.

## Requirements

### Requirement 1

**User Story:** As a user viewing an itinerary, I want to refresh a spot to a completely different category, so that I can diversify my itinerary experience beyond the current category type.

#### Acceptance Criteria

1. WHEN I view a stop in an itinerary detail modal THEN I SHALL see two distinct refresh options: one for refreshing within the same category and one for refreshing to a different category
2. WHEN I click the category refresh button THEN the system SHALL replace the current stop with a new stop from a different category
3. WHEN I refresh a category THEN the system SHALL exclude that category from being recommended for the next 5 refresh operations for that location
4. WHEN no alternative categories are available THEN the system SHALL display an appropriate error message
5. WHEN the category refresh is successful THEN the new stop SHALL maintain proper walking time calculations and integration with the itinerary flow

### Requirement 2

**User Story:** As a user, I want clear visual distinction between spot refresh and category refresh options, so that I can easily understand and choose the type of refresh I want.

#### Acceptance Criteria

1. WHEN I view a stop THEN I SHALL see the existing spot refresh button in the top-right corner of the image
2. WHEN I view a stop THEN I SHALL see a new category refresh button positioned near the category text display
3. WHEN I hover over each refresh button THEN I SHALL see distinct tooltips explaining the difference between spot refresh and category refresh
4. WHEN either refresh operation is in progress THEN the respective button SHALL show a loading state
5. WHEN a refresh operation fails THEN I SHALL see a clear error message explaining what went wrong

### Requirement 3

**User Story:** As a user, I want the category exclusion system to work intelligently across my session, so that I get diverse recommendations without repetitive category suggestions.

#### Acceptance Criteria

1. WHEN I refresh a category for a specific location THEN that category SHALL be excluded from recommendations for the next 5 refresh operations for that location only
2. WHEN I perform 5 refresh operations after excluding a category THEN that category SHALL become available for recommendations again
3. WHEN I switch to a different location THEN the category exclusions SHALL be location-specific and not affect other locations
4. WHEN I refresh the browser or start a new session THEN the category exclusions SHALL reset (no persistence required)
5. WHEN all categories become excluded and no alternatives are available THEN the system SHALL provide a clear message and suggest resetting exclusions

### Requirement 4

**User Story:** As a developer, I want the backend API to efficiently handle category refresh requests with proper exclusion tracking, so that the system can scale and maintain performance.

#### Acceptance Criteria

1. WHEN a category refresh request is made THEN the system SHALL create a new `/api/refresh-category` endpoint
2. WHEN processing a category refresh THEN the system SHALL maintain an in-memory store of excluded categories per location
3. WHEN selecting an alternative category THEN the system SHALL prioritize categories that provide good diversity (different broad types)
4. WHEN tracking exclusions THEN the system SHALL implement a turn-based counter that resets categories after 5 operations
5. WHEN the server restarts THEN the exclusion tracking SHALL reset (no persistent storage required for MVP)

### Requirement 5

**User Story:** As a user, I want the category refresh to maintain the quality and relevance of recommendations, so that the new suggestions are still appropriate for my location and preferences.

#### Acceptance Criteria

1. WHEN a category is refreshed THEN the new spot SHALL be within the same distance radius as the original itinerary constraints
2. WHEN selecting an alternative spot THEN the system SHALL prioritize highly-rated and relevant places from the new category
3. WHEN replacing a spot THEN the walking time calculations SHALL be updated appropriately for the new location
4. WHEN a category refresh occurs THEN the new spot SHALL include proper image, description, and metadata
5. WHEN the refresh is complete THEN the itinerary flow and map integration SHALL work seamlessly with the new spot