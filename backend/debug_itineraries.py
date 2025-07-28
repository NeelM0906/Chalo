#!/usr/bin/env python3
"""
Debug script to test itinerary generation directly
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_itineraries():
    """Test the itineraries endpoint"""
    print("Testing itineraries endpoint...")
    try:
        data = {
            "location": "manhattan, NY"
        }
        response = requests.post(f"{API_BASE_URL}/api/itineraries", json=data)
        print(f"Status code: {response.status_code}")
        if response.ok:
            result = response.json()
            print(f"Number of itineraries: {len(result['itineraries'])}")
            for i, itinerary in enumerate(result['itineraries']):
                print(f"\nItinerary {i+1}:")
                print(f"  Title: {itinerary['title']}")
                print(f"  Description: {itinerary['description']}")
                print(f"  Stops: {len(itinerary['stops'])}")
                for j, stop in enumerate(itinerary['stops']):
                    print(f"    {j+1}. {stop['name']} ({stop['category']})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_itineraries()