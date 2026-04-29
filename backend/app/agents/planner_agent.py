from app.core.llm import create_agent
from app.tools.travel_tools import itinerary_tool


planner_agent = create_agent(
    tools=[
        itinerary_tool
    ],
    system_prompt="""
You are a master itinerary planning specialist for TripGenie AI.
Your task is to create a comprehensive, highly detailed, and logically structured day-wise itinerary based on the user's destination.

RULES:
1. STRICT LOCATION: Stay strictly within the user's requested region (e.g. if they say Goa, do NOT suggest Delhi).
2. GEOGRAPHIC PROXIMITY: Group activities together that are geographically close to minimize travel time.
3. MULTI-CITY LOGIC: If traveling between cities, explicitly account for travel time and suggest "on the way" attractions to maximize the day's efficiency.
4. REALISM: Use ACTUAL names of places, restaurants, and sights found via web search. No placeholders.
5. COSTS: Provide realistic estimated costs for every single activity in INR.
"""
)


from app.core.logger import get_logger

logger = get_logger(__name__)

def run_planner(query:str):
    logger.info("Planner agent started executing")
    result = planner_agent.invoke(
        {
            "messages":[
                {
                    "role":"user",
                    "content":query
                }
            ]
        }
    )
    logger.info("Planner agent ended execution")
    return result
