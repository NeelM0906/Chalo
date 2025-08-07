import os
import json
import requests
from new_engine import ChaloSearchEngine
from itinerary_generator import ItineraryGenerator

class GeminiClient:
    """Simple Gemini API client for agent functionality"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "AIzaSyBqEMWlxcFmX94S3rhN7tiddnUm4AmPIF8")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
    def generate_content(self, prompt: str, user_input: str) -> dict:
        """Generate content using Gemini API"""
        try:
            # Format the prompt with user input
            formatted_prompt = prompt.format(user_input=user_input)
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": formatted_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 2048,
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the generated text
            if "candidates" in result and result["candidates"]:
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Try to parse as JSON
                try:
                    return json.loads(generated_text)
                except json.JSONDecodeError:
                    # If not valid JSON, return as text
                    return {"text": generated_text}
            else:
                return {"error": "No response generated"}
                
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {"error": str(e)}

class AgentSearchEngine(ChaloSearchEngine):
    """Enhanced search engine for agent-based dynamic queries"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.intent_to_query_mapping = {
            # Food categories - all cuisines map to food searches
            "food": "restaurants",
            "chinese food": "chinese restaurants",
            "thai food": "thai restaurants", 
            "mexican food": "mexican restaurants",
            "indian food": "indian restaurants",
            "japanese food": "japanese restaurants",
            "korean food": "korean restaurants",
            "vietnamese food": "vietnamese restaurants",
            "lebanese food": "lebanese restaurants",
            "mediterranean food": "mediterranean restaurants",
            "turkish food": "turkish restaurants",
            "greek food": "greek restaurants",
            "halal food": "halal restaurants",
            "italian food": "italian restaurants",
            "american food": "american restaurants",
            "pizza": "pizza restaurants",
            "burgers": "burger restaurants",
            "sushi": "sushi restaurants",
            "bbq": "bbq restaurants",
            "seafood": "seafood restaurants",
            
            # Sweet/dessert categories
            "desserts": "desserts",
            "sweets": "bakeries",
            "ice cream": "ice cream shops",
            "bakery": "bakeries",
            "pastries": "bakeries",
            "sweet bite": "desserts",
            "something sweet": "desserts",
            
            # Drinks
            "coffee": "cafes",
            "drinks": "bars",
            "cocktails": "bars",
            "beer": "bars",
            "wine": "wine bars",
            
            # Activities
            "activities": "tourist_attraction",
            "things to do": "tourist_attraction", 
            "attractions": "tourist_attraction",
            "sightseeing": "tourist_attraction",
            "museums": "museum",
            "art": "art_gallery",
            "galleries": "art_gallery",
            "parks": "park",
            "nature": "park",
            "outdoors": "park",
            "walking": "park",
            "shopping": "shopping_mall",
            "shops": "store",
            "markets": "store",
            
            # Entertainment
            "entertainment": "amusement_park",
            "fun": "amusement_park",
            "nightlife": "night_club",
            "music": "night_club",
            "dancing": "night_club"
        }
    
    def search_agent_queries(self, location: str, extracted_queries: list, distance_miles: float = 1.5) -> dict:
        """Search based on agent-extracted queries instead of fixed categories"""
        print(f"Agent Search: {extracted_queries} near {location} within {distance_miles} miles")
        
        # Convert extracted queries to Google Places API types
        search_categories = []
        for query in extracted_queries:
            # Normalize query to lowercase
            normalized_query = query.lower().strip()
            
            # Map to Google Places type
            places_type = self.intent_to_query_mapping.get(normalized_query, "restaurant")
            search_categories.append(places_type)
        
        # Remove duplicates while preserving order
        unique_categories = []
        for category in search_categories:
            if category not in unique_categories:
                unique_categories.append(category)
        
        print(f"Mapped to Google Places types: {unique_categories}")
        
        # Use existing search functionality with dynamic categories
        results_by_category = {}
        
        # Geocode location first
        lat, lng = self.geocode_address(location)
        if not lat:
            print(f"Failed to geocode location: {location}")
            return {"results_by_category": {}}
        
        # Search each category
        for i, category_type in enumerate(unique_categories):
            original_query = extracted_queries[i] if i < len(extracted_queries) else category_type
            print(f"Searching {original_query} ({category_type})...")
            
            # Use existing search_category method
            places = self.search_category(lat, lng, category_type, min_rating=4.0)
            
            # Filter by distance
            max_distance_meters = distance_miles * 1609.34
            filtered_places = []
            for place in places:
                if place.get('distance_meters', 0) <= max_distance_meters:
                    # Add the original query as search_category for context
                    place['search_category'] = original_query
                    filtered_places.append(place)
            
            results_by_category[original_query] = filtered_places
            print(f"Found {len(filtered_places)} places for {original_query}")
        
        return {"results_by_category": results_by_category}

def understand_user_request(user_request: str) -> dict:
    """
    Enhanced NLU to extract diverse food preferences, activities, and mood context
    Uses rule-based parsing with Gemini API fallback
    """
    
    # First try rule-based parsing for common patterns
    def rule_based_parsing(text: str) -> dict:
        text = text.lower().strip()
        search_queries = []
        
        # Food/cuisine patterns
        cuisines = [
            "chinese", "thai", "mexican", "indian", "japanese", "korean", 
            "vietnamese", "lebanese", "mediterranean", "turkish", "greek", 
            "halal", "italian", "american", "pizza", "burger", "sushi", 
            "bbq", "seafood"
        ]
        
        for cuisine in cuisines:
            if cuisine in text:
                search_queries.append(f"{cuisine} food")
        
        # Generic food terms
        food_terms = ["food", "eat", "restaurant", "dining"]
        if any(term in text for term in food_terms) and not search_queries:
            search_queries.append("food")
        
        # Sweet/dessert patterns
        sweet_terms = [
            "sweet", "dessert", "ice cream", "bakery", "pastry", 
            "cake", "cookie", "candy", "chocolate"
        ]
        if any(term in text for term in sweet_terms):
            search_queries.append("desserts")
        
        # Drink patterns
        if "coffee" in text:
            search_queries.append("coffee")
        if any(term in text for term in ["drink", "cocktail", "beer", "wine", "bar"]):
            search_queries.append("drinks")
        
        # Activity patterns
        activity_terms = [
            "walk", "activity", "activities", "things to do", "sightseeing",
            "museum", "park", "shopping", "shop", "attraction", "tour"
        ]
        if any(term in text for term in activity_terms):
            search_queries.append("activities")
        
        if "park" in text or "nature" in text or "outdoor" in text:
            search_queries.append("parks")
        if "museum" in text or "art" in text or "gallery" in text:
            search_queries.append("museums")
        if "shop" in text or "shopping" in text or "market" in text:
            search_queries.append("shopping")
        
        # Determine experience type
        experience_type = "casual"
        if any(term in text for term in ["upscale", "fancy", "fine dining", "elegant"]):
            experience_type = "upscale"
        elif any(term in text for term in ["adventure", "explore", "discover"]):
            experience_type = "adventure"
        elif any(term in text for term in ["relax", "chill", "peaceful", "quiet"]):
            experience_type = "relaxed"
        
        return {
            "search_queries": list(set(search_queries)) if search_queries else ["food"],
            "mood_context": text,
            "experience_type": experience_type
        }
    
    # Try rule-based parsing first
    try:
        result = rule_based_parsing(user_request)
        print(f"Rule-based parsing result: {result}")
        return result
    except Exception as e:
        print(f"Rule-based parsing error: {e}")
    
    # Fallback to Gemini API if available
    try:
        gemini_client = GeminiClient()
        
        prompt = """
You are an expert at understanding diverse travel and food preferences from natural language.

Analyze the user's request and extract:
1. Food preferences - normalize ALL specific cuisines to just the cuisine name + "food" (e.g., "chinese food", "thai food")
2. Sweet/dessert preferences - identify when user wants desserts, sweets, ice cream, etc.
3. Activity preferences - parks, museums, shopping, sightseeing, etc.
4. Drink preferences - coffee, cocktails, bars, etc.
5. Overall mood and experience type

IMPORTANT RULES:
- For cuisines: "chinese" → "chinese food", "thai" → "thai food", "mexican" → "mexican food"
- For sweets: "something sweet", "dessert", "ice cream" → "desserts"
- For activities: "walk", "sightseeing" → "activities"
- Keep queries simple and searchable

Return ONLY valid JSON in this exact format:
{{
  "search_queries": ["chinese food", "desserts"],
  "mood_context": "brief description of what user is looking for",
  "experience_type": "casual/upscale/adventure/relaxed"
}}

Examples:
- "chinese food and something sweet" → {{"search_queries": ["chinese food", "desserts"], "mood_context": "wants chinese cuisine followed by dessert", "experience_type": "casual"}}
- "thai food and activities" → {{"search_queries": ["thai food", "activities"], "mood_context": "wants thai cuisine and things to do", "experience_type": "casual"}}
- "coffee and a walk in the park" → {{"search_queries": ["coffee", "parks"], "mood_context": "wants coffee and outdoor relaxation", "experience_type": "relaxed"}}

User's request: {user_input}
"""
        
        result = gemini_client.generate_content(prompt, user_request)
        
        # Ensure we have the expected structure
        if isinstance(result, dict) and "search_queries" in result:
            return {
                "search_queries": result.get("search_queries", []),
                "mood_context": result.get("mood_context", ""),
                "experience_type": result.get("experience_type", "casual")
            }
    except Exception as e:
        print(f"Gemini API Error: {e}")
    
    # Final fallback
    return {
        "search_queries": ["food"],
        "mood_context": user_request,
        "experience_type": "casual"
    }

def generate_agent_recommendations(search_results: dict, user_context: dict, location: str) -> dict:
    """
    Generate conversational, context-aware route recommendations
    Uses rule-based generation with Gemini API fallback
    """
    
    # Prepare search results summary
    places_summary = {}
    all_places = []
    
    for category, places in search_results.get("results_by_category", {}).items():
        places_summary[category] = []
        for place in places[:5]:  # Limit to top 5 per category
            place_info = {
                "name": place.get("name"),
                "rating": place.get("rating"),
                "address": place.get("address"),
                "distance_miles": place.get("distance_miles"),
                "category": category
            }
            places_summary[category].append(place_info)
            all_places.append(place_info)
    
    # Rule-based route generation
    def create_rule_based_routes():
        if not all_places:
            return []
        
        routes = []
        
        # Sort places by rating
        sorted_places = sorted(all_places, key=lambda x: x.get("rating", 0), reverse=True)
        
        # Route 1: Best rated places
        if len(sorted_places) >= 2:
            route1_places = sorted_places[:min(3, len(sorted_places))]
            stops = []
            for i, place in enumerate(route1_places):
                stops.append({
                    "place_name": place["name"],
                    "category": place["category"],
                    "why_recommended": f"Highly rated ({place.get('rating', 'N/A')}/5) {place['category']} spot",
                    "walking_time_to_next": 8 if i < len(route1_places) - 1 else 0
                })
            
            routes.append({
                "name": f"Top Rated {location} Experience",
                "description": f"Perfect for {user_context.get('mood_context', 'your preferences')} - featuring the highest-rated spots in the area",
                "stops": stops,
                "total_duration_minutes": len(stops) * 30 + sum(s["walking_time_to_next"] for s in stops),
                "local_tip": "These places consistently get rave reviews from locals and visitors alike!"
            })
        
        # Route 2: Diverse experience (if we have multiple categories)
        categories = list(places_summary.keys())
        if len(categories) >= 2:
            diverse_places = []
            for category in categories[:3]:  # Max 3 categories
                if places_summary[category]:
                    diverse_places.append(places_summary[category][0])  # Best from each category
            
            if diverse_places:
                stops = []
                for i, place in enumerate(diverse_places):
                    stops.append({
                        "place_name": place["name"],
                        "category": place["category"],
                        "why_recommended": f"Great {place['category']} option to satisfy your cravings",
                        "walking_time_to_next": 10 if i < len(diverse_places) - 1 else 0
                    })
                
                routes.append({
                    "name": f"Mixed {location} Adventure",
                    "description": f"A perfect blend matching your mood for {user_context.get('mood_context', 'variety')}",
                    "stops": stops,
                    "total_duration_minutes": len(stops) * 35 + sum(s["walking_time_to_next"] for s in stops),
                    "local_tip": "This route gives you the best of different experiences in one walk!"
                })
        
        # Route 3: Quick & close (shortest distances)
        close_places = sorted([p for p in all_places if p.get("distance_miles") is not None and p.get("distance_miles") < 0.5], 
                             key=lambda x: x.get("distance_miles", 999))[:2]
        
        if close_places:
            stops = []
            for i, place in enumerate(close_places):
                stops.append({
                    "place_name": place["name"],
                    "category": place["category"],
                    "why_recommended": f"Conveniently close ({place.get('distance_miles', 'N/A')} miles away)",
                    "walking_time_to_next": 5 if i < len(close_places) - 1 else 0
                })
            
            routes.append({
                "name": f"Quick {location} Bite",
                "description": f"Perfect for a quick outing - {user_context.get('mood_context', 'close and convenient')}",
                "stops": stops,
                "total_duration_minutes": len(stops) * 25 + sum(s["walking_time_to_next"] for s in stops),
                "local_tip": "These spots are super close to each other - perfect for a leisurely stroll!"
            })
        
        return routes[:3]  # Return max 3 routes
    
    # Try rule-based generation first
    try:
        routes = create_rule_based_routes()
        if routes:
            return {"routes": routes}
    except Exception as e:
        print(f"Rule-based recommendation error: {e}")
    
    # Try Gemini API as fallback
    try:
        gemini_client = GeminiClient()
        
        prompt = """
You are a fun, knowledgeable local travel expert and food enthusiast. Based on the user's preferences and available places, suggest 2-3 mini walking routes that perfectly match their mood.

Create engaging, conversational route suggestions that feel like recommendations from a local friend.

User wanted: {mood_context}
Experience type: {experience_type}
Location: {location}
Available places by category: {search_results}

Create 2-3 route suggestions with:
- Catchy, appealing route names (e.g., "Sweet & Spicy Adventure", "Foodie's Paradise Walk")
- Conversational description explaining why this route matches their mood
- 2-4 stops per route with logical walking flow
- Local insider tips and personality
- Estimated walking time between stops

Return ONLY valid JSON in this exact format:
{{
  "routes": [
    {{
      "name": "Route Name",
      "description": "Why this route is perfect for what you're craving...",
      "stops": [
        {{
          "place_name": "Actual place name from search results",
          "category": "chinese food/desserts/etc",
          "why_recommended": "What makes this place special",
          "walking_time_to_next": 5
        }}
      ],
      "total_duration_minutes": 90,
      "local_tip": "Insider advice about the route"
    }}
  ]
}}

IMPORTANT: Only use actual place names from the search results provided. Make sure walking times are realistic (2-15 minutes between stops).
"""
        
        # Format the prompt with context
        formatted_input = f"""
User wanted: {user_context.get("mood_context", "")}
Experience type: {user_context.get("experience_type", "casual")}
Location: {location}
Available places by category: {json.dumps(places_summary, indent=2)}
"""
        
        result = gemini_client.generate_content(prompt, formatted_input)
        
        if isinstance(result, dict) and "routes" in result:
            return result
    except Exception as e:
        print(f"Gemini API Error: {e}")
    
    # Final fallback
    return {
        "routes": [{
            "name": f"Discover {location}",
            "description": f"A great local experience based on your preferences: {user_context.get('mood_context', '')}",
            "stops": [],
            "total_duration_minutes": 60,
            "local_tip": "Enjoy exploring the area!"
        }]
    }

def run_agent_recommendations(user_request: str, location: str, distance_miles: float = 1.5) -> dict:
    """
    Main agent workflow for conversational travel recommendations
    """
    print(f"Agent Request: '{user_request}' in {location} within {distance_miles} miles")
    
    try:
        # Step 1: Enhanced NLU
        print("Step 1: Understanding user request...")
        intent_data = understand_user_request(user_request)
        print(f"Extracted intent: {intent_data}")
        
        # Step 2: Dynamic search
        print("Step 2: Searching for places...")
        api_key = "AIzaSyBqEMWlxcFmX94S3rhN7tiddnUm4AmPIF8"
        agent_search_engine = AgentSearchEngine(api_key)
        search_results = agent_search_engine.search_agent_queries(
            location, intent_data["search_queries"], distance_miles
        )
        
        # Check if we found any places
        total_places = sum(len(places) for places in search_results.get("results_by_category", {}).values())
        print(f"Found {total_places} total places")
        
        if total_places == 0:
            return {
                "user_intent": intent_data,
                "recommendations": {
                    "routes": [{
                        "name": f"No Results for {location}",
                        "description": f"Sorry, we couldn't find places matching '{user_request}' in {location}. Try a different location or broader preferences.",
                        "stops": [],
                        "total_duration_minutes": 0,
                        "local_tip": "Consider expanding your search radius or trying different keywords."
                    }]
                },
                "search_context": search_results
            }
        
        # Step 3: Context-aware recommendations
        print("Step 3: Generating recommendations...")
        recommendations = generate_agent_recommendations(
            search_results, intent_data, location
        )
        
        return {
            "user_intent": intent_data,
            "recommendations": recommendations,
            "search_context": search_results
        }
        
    except Exception as e:
        print(f"Agent workflow error: {e}")
        return {
            "user_intent": {"search_queries": [], "mood_context": user_request, "experience_type": "casual"},
            "recommendations": {
                "routes": [{
                    "name": "Error",
                    "description": "Sorry, we encountered an error processing your request. Please try again.",
                    "stops": [],
                    "total_duration_minutes": 0,
                    "local_tip": "Try rephrasing your request or check your location."
                }]
            },
            "search_context": {"results_by_category": {}}
        }
