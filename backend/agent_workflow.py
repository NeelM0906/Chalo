import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_adk.agents import SequentialAgent, ToolAgent
from google_adk.tools import FunctionTool
from backend.agent_tools import understand_user_request, find_places, generate_itinerary

def run_agent(user_request: str):
    """
    Runs the itinerary generation agent.
    """
    # Create tools
    understand_user_request_tool = FunctionTool(fn=understand_user_request, name="understand_user_request")
    find_places_tool = FunctionTool(fn=find_places, name="find_places")
    generate_itinerary_tool = FunctionTool(fn=generate_itinerary, name="generate_itinerary")

    # Create agents
    nlu_agent = ToolAgent(tools=[understand_user_request_tool])
    places_agent = ToolAgent(tools=[find_places_tool])
    itinerary_agent = ToolAgent(tools=[generate_itinerary_tool])

    # Define the workflow
    workflow = SequentialAgent(
        agents=[
            nlu_agent,
            places_agent,
            itinerary_agent
        ]
    )

    # Run the agent
    result = workflow.run(user_input=user_request)
    return result

if __name__ == "__main__":
    user_request = "I'm in the mood for thai food, something sweet and then a lil walk in San Francisco"
    itinerary = run_agent(user_request)
    print(itinerary)
