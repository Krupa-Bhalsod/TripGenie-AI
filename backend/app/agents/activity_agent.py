from app.core.llm import create_agent
from app.tools.travel_tools import activity_search_tool
from app.core.prompt_loader import load_prompt


activity_agent = create_agent(
    tools=[
       activity_search_tool
    ],
    system_prompt=load_prompt("activity_agent")
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
