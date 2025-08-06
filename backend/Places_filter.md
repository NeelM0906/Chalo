To filter places by rating using the Google Places API, specifically the Places Aggregate API, you can utilize the RatingFilter within your request.
Here's how to apply a rating filter:
Specify Insight Type: When using the Places Aggregate API, you need to choose an InsightType of either INSIGHT_COUNT (to get a count of places matching the criteria) or INSIGHT_PLACES (to get the place IDs of matching places).
Include RatingFilter: Within the filters object of your request, include a ratingFilter object.
Set minRating and maxRating: Inside the ratingFilter, you can specify:
minRating: The minimum average user rating a place must have to be included in the results. Values must be between 1.0 and 5.0.
maxRating: The maximum average user rating a place can have to be included in the results. Values must be between 1.0 and 5.0.
Both minRating and maxRating are optional. If omitted, places without ratings will also be included in the results.
Example (Conceptual JSON for a computeInsights request):
Code

{
  "insightType": "INSIGHT_PLACES",
  "filters": {
    "locationFilter": {
      "circle": {
        "center": {
          "latitude": 34.052235,
          "longitude": -118.243683
        },
        "radius": 1000.0
      }
    },
    "typeFilter": {
      "includedTypes": ["restaurant"]
    },
    "ratingFilter": {
      "minRating": 4.0,
      "maxRating": 5.0
    }
  }
}
This example would return place IDs for restaurants within a 1km radius of the specified coordinates that have an average user rating between 4.0 and 5.0 (inclusive).