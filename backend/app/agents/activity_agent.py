from app.core.llm import create_agent
from app.tools.travel_tools import activity_search_tool


activity_agent = create_agent(
    tools=[
       activity_search_tool
    ],
    system_prompt="""
You are an activity and attractions specialist.
Your task is to find REAL, exciting things to do and places to eat in the user's destination.

RULES:
1. STRICT LOCATION: Stay strictly within the user's requested region. Do NOT suggest activities in other states or countries.
2. GEOGRAPHIC PROXIMITY: If moving between cities, specifically find "on the way" attractions or sights to visit.
3. REAL DATA: Use actual names of attractions, restaurants, and food items found via web search. No placeholders.
"""
)


from app.core.logger import get_logger

logger = get_logger(__name__)

def run_activity(query):
    logger.info("Activity agent started executing")
    result = activity_agent.invoke(
       {
        "messages":[
          {
            "role":"user",
            "content":query
          }
        ]
       }
    )
    logger.info("Activity agent ended execution")
    return result
