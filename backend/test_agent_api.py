#!/usr/bin/env python3
"""
Test script for the agent API endpoint
Run this after starting the server with: python main.py
"""

import requests
import json
import sys

def test_agent_api():
    """Test the agent recommendations API endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/agent-recommendations"
    
    test_cases = [
        {
            "name": "Thai food and desserts",
            "data": {
                "user_request": "thai food and something sweet",
                "location": "San Francisco",
                "distance_miles": 1.5
            }
        },
        {
            "name": "Chinese food and activities",
            "data": {
                "user_request": "chinese food and activities",
                "location": "New York",
                "distance_miles": 2.0
            }
        },
        {
            "name": "Coffee and walk",
            "data": {
                "user_request": "coffee and a walk in the park",
                "location": "Los Angeles",
                "distance_miles": 1.0
            }
        }
    ]
    
    print("🤖 Testing Agent API Endpoint")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Request: {test_case['data']}")
        
        try:
            response = requests.post(endpoint, json=test_case['data'], timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                routes = result.get('recommendations', {}).get('routes', [])
                
                print(f"✅ Success! Generated {len(routes)} routes")
                
                for j, route in enumerate(routes, 1):
                    print(f"  {j}. {route['name']}")
                    print(f"     Stops: {len(route.get('stops', []))}")
                    print(f"     Duration: {route.get('total_duration_minutes', 0)} minutes")
                    print(f"     Description: {route.get('description', '')[:80]}...")
                    
                    if route.get('stops'):
                        print(f"     First stop: {route['stops'][0].get('place_name', 'N/A')}")
                    
                    if route.get('local_tip'):
                        print(f"     Tip: {route['local_tip'][:60]}...")
                    print()
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the server is running on localhost:8000")
            print("   Start server with: python main.py")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Agent API testing complete!")
    return True

if __name__ == "__main__":
    success = test_agent_api()
    sys.exit(0 if success else 1)