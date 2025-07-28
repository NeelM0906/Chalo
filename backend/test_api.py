#!/usr/bin/env python3
"""
Test script for the API endpoints
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_refresh_spot():
    """Test the refresh spot endpoint"""
    print("\nTesting refresh spot endpoint...")
    try:
        data = {
            "location": "New York, NY",
            "category": "Restaurant",
            "excluded_ids": []
        }
        response = requests.post(f"{API_BASE_URL}/api/refresh-spot", json=data)
        print(f"Status code: {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def list_endpoints():
    """List all available endpoints"""
    print("\nListing available endpoints...")
    try:
        response = requests.get(f"{API_BASE_URL}/openapi.json")
        if response.ok:
            data = response.json()
            paths = data.get("paths", {})
            print("Available endpoints:")
            for path in paths:
                print(f"  {path}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health()
    test_refresh_spot()
    list_endpoints()