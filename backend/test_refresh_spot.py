#!/usr/bin/env python3
"""
Test script for the refresh spot endpoint
"""

import requests
import json
import sys
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = "http://localhost:8000"

def test_refresh_spot():
    """Test the refresh spot endpoint"""
    print("🔍 Testing refresh spot...")
    
    # Test data
    location = "New York, NY"
    category = "Restaurant"
    excluded_ids = ["test-id-1", "test-id-2"]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/refresh-spot",
            json={"location": location, "category": category, "excluded_ids": excluded_ids},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Refresh spot successful!")
            print(f"   - New spot: {data.get('name')} ({data.get('category')})")
            print(f"   - Description: {data.get('description')}")
            return True
        else:
            print(f"❌ Refresh spot failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Refresh spot error: {e}")
        return False

if __name__ == "__main__":
    test_refresh_spot()