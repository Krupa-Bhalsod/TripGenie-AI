from app.core.llm import create_agent
from app.tools.travel_tools import hotel_lookup_tool
from app.core.prompt_loader import load_prompt


hotel_agent = create_agent(
    tools=[
        hotel_lookup_tool
    ],
    system_prompt=load_prompt("hotel_agent")
)


from app.core.logger import get_logger

logger = get_logger(__name__)

def run_hotel(query):
    logger.info("Hotel agent started executing")
    result = hotel_agent.invoke(
      {
       "messages":[
         {
           "role":"user",
           "content":query
         }
       ]
      }
    )
    logger.info("Hotel agent ended execution")
    return result
