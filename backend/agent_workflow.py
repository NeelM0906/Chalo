import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent_tools import run_agent_recommendations

def run_agent(user_request: str, location: str = "San Francisco", distance_miles: float = 1.5):
    """
    Runs the conversational travel agent for personalized recommendations.
    
    Args:
        user_request: Natural language request like "thai food and something sweet"
        location: Location to search in
        distance_miles: Search radius in miles
    
    Returns:
        Dict with user_intent, recommendations, and search_context
    """
    return run_agent_recommendations(user_request, location, distance_miles)

if __name__ == "__main__":
    # Test the new agent
    test_cases = [
        {
            "request": "I'm in the mood for thai food, something sweet and then a lil walk",
            "location": "San Francisco",
            "distance": 1.5
        },
        {
            "request": "chinese food and activities", 
            "location": "New York",
            "distance": 2.0
        },
        {
            "request": "coffee and desserts",
            "location": "Los Angeles", 
            "distance": 1.0
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test['request']} in {test['location']}")
        print(f"{'='*60}")
        
        result = run_agent(test['request'], test['location'], test['distance'])
        
        print(f"User Intent: {result['user_intent']}")
        print(f"Routes Found: {len(result['recommendations'].get('routes', []))}")
        
        for route in result['recommendations'].get('routes', []):
            print(f"\nRoute: {route['name']}")
            print(f"Description: {route['description']}")
            print(f"Stops: {len(route.get('stops', []))}")
            print(f"Duration: {route.get('total_duration_minutes', 0)} minutes")
            if route.get('local_tip'):
                print(f"Tip: {route['local_tip']}")
        
        print(f"\nSearch Context: {len(result['search_context'].get('results_by_category', {}))} categories searched")
