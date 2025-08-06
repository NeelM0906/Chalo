import os
from google_adk.agents import LlmAgent
from new_engine import ChaloSearchEngine
from itinerary_generator import ItineraryGenerator

def understand_user_request(user_request: str) -> list[str]:
    """
    Uses a large language model to understand the user's request and extract a list of desired activities.
    """
    nlu_agent = LlmAgent(
        llm="gemini-1.5-flash",
        prompt="""
You are an expert at understanding user requests for planning a trip.
Analyze the user's request and extract the desired activities.
Return the activities as a JSON object with a key called "activities", which is a list of strings.

User's request: {user_input}
"""
    )
    result = nlu_agent.run(user_input=user_request)
    return result.get("activities", [])

def find_places(activity: str, location: str) -> list[dict]:
    """
    Finds places related to a given activity in a specific location.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    search_engine = ChaloSearchEngine(api_key)
    search_results = search_engine.search_specific_categories(location, [activity])
    return search_results.get("results_by_category", {}).get(activity, [])

def generate_itinerary(places: list[dict], location: str) -> dict:
    """
    Generates an itinerary from a list of places.
    """
    itinerary_generator = ItineraryGenerator()
    search_results = {"results_by_category": {}}
    for place in places:
        category = place.get("search_category")
        if category not in search_results["results_by_category"]:
            search_results["results_by_category"][category] = []
        search_results["results_by_category"][category].append(place)

    itineraries = itinerary_generator.generate_itineraries(search_results, location)
    return itineraries[0] if itineraries else {}
