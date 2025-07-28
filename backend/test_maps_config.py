#!/usr/bin/env python3
"""
Test script for the maps config endpoint
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_maps_config():
    """Test the maps config endpoint"""
    print("Testing maps config endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/maps-config")
        print(f"Status code: {response.status_code}")
        if response.ok:
            data = response.json()
            api_key = data.get('maps_api_key', '')
            if api_key:
                print(f"✅ Maps API key configured: {api_key[:20]}...")
                
                # Test a sample embed URL
                sample_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin=Times+Square,New+York,NY&destination=Central+Park,New+York,NY&mode=walking"
                print(f"✅ Sample embed URL generated successfully")
                print(f"   URL: {sample_url[:100]}...")
            else:
                print("❌ No API key found in response")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_maps_config()