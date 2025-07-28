#!/usr/bin/env python3
"""
Test script for LocalWander API integration
"""

import requests
import json
import sys
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_itineraries(location="New York, NY", preset=None):
    """Test the itineraries endpoint"""
    request_data = {"location": location}
    if preset:
        request_data["preset"] = preset
        print(f"🔍 Testing {preset} itineraries for: {location}")
    else:
        print(f"🔍 Testing mixed itineraries for: {location}")
        
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/itineraries",
            json=request_data,
            timeout=60  # Give it time for API calls
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Itineraries generated successfully!")
            print(f"   - Found {len(data['itineraries'])} itineraries")
            print(f"   - Found {len(data['sources'])} sources")
            
            for i, itinerary in enumerate(data['itineraries'], 1):
                print(f"   {i}. {itinerary['title']} ({itinerary['duration_minutes']} min, {len(itinerary['stops'])} stops)")
                # Print the first itinerary's stops to check variety
                if i == 1:
                    print(f"      Stops in first itinerary:")
                    for j, stop in enumerate(itinerary['stops'], 1):
                        print(f"        {j}. {stop['name']} ({stop['category']})")
            
            return True
        else:
            print(f"❌ Itineraries failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Itineraries error: {e}")
        return False

# Removed duplicate function as test_itineraries already supports presets

def main():
    print("🚀 LocalWander API Integration Test")
    print("=" * 50)
    
    # Check if API key is configured
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in environment")
        print("   Please ensure backend/.env contains your API key")
        sys.exit(1)
    
    print(f"✅ API key configured: {api_key[:20]}...")
    print()
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed - is the server running?")
        print("   Try: ./start-backend.sh")
        sys.exit(1)
    
    print()
    
    # Test itineraries
    test_location = input("Enter a location to test (or press Enter for 'New York, NY'): ").strip()
    if not test_location:
        test_location = "New York, NY"
    
    print("\n--- Testing Mixed Itineraries (Default) ---")
    mixed_success = test_itineraries(test_location)
    
    print("\n--- Testing Preset Itineraries ---")
    preset_success = test_itineraries(test_location, "Foodie Delights")
    
    if mixed_success and preset_success:
        print("\n🎉 All tests passed! Your LocalWander API is working correctly.")
        print("✅ Mixed itineraries: Working")
        print("✅ Preset itineraries: Working")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")
        if not mixed_success:
            print("❌ Mixed itineraries: Failed")
        if not preset_success:
            print("❌ Preset itineraries: Failed")
        sys.exit(1)

if __name__ == "__main__":
    main()