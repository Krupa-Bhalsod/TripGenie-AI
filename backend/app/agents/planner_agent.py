from app.core.llm import create_agent
from app.tools.travel_tools import itinerary_tool
from app.core.prompt_loader import load_prompt


planner_agent = create_agent(
    tools=[
        itinerary_tool
    ],
    system_prompt=load_prompt("planner_agent")
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
