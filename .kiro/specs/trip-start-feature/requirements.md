# Requirements Document

## Introduction

This feature addresses two user interface improvements for the LocalWander application:
1. Changing the search button text from "Wander" to "Chalo" to better reflect the brand identity
2. Adding a "Start this trip" functionality that allows users to enter a dedicated trip mode for a selected itinerary

## Requirements

### Requirement 1: Button Text Update

**User Story:** As a user, I want the search button to say "Chalo" instead of "Wander", so that the interface reflects the updated branding.

#### Acceptance Criteria

1. WHEN the user views the location input form THEN the submit button SHALL display "Chalo" instead of "Wander"
2. WHEN the user clicks the search button while loading THEN the button SHALL display "Chaloing..." instead of "Wandering..."
3. WHEN the button is disabled THEN it SHALL maintain the "Chalo" text styling

### Requirement 2: Trip Start Feature

**User Story:** As a user, I want to start a dedicated trip mode for a selected itinerary, so that I can focus on following the trip without distractions.

#### Acceptance Criteria

1. WHEN the user views an itinerary detail modal THEN there SHALL be a "Start this trip" button at the bottom of the modal
2. WHEN the user clicks "Start this trip" THEN they SHALL be navigated to a new dedicated trip page
3. WHEN the user is on the trip page THEN the page SHALL display "Your current trip" as the header
4. WHEN the user is on the trip page THEN the page SHALL show the selected itinerary with all stops and descriptions
5. WHEN the user is on the trip page THEN the page SHALL include the embedded map showing the walking directions
6. WHEN the user is on the trip page THEN there SHALL be navigation to return to the main application
7. WHEN the user navigates away from the trip page THEN the trip state SHALL be preserved until they start a new trip
8. WHEN the user starts a new trip THEN any previous trip SHALL be replaced with the new selection