from app.core.llm import create_agent
from app.tools.travel_tools import budget_split_tool
from app.core.prompt_loader import load_prompt


budget_agent = create_agent(
    tools=[
        budget_split_tool
    ],
    system_prompt=load_prompt("budget_agent")
)


from app.core.logger import get_logger

logger = get_logger(__name__)

def run_budget(query):
    logger.info("Budget agent started executing")
    result = budget_agent.invoke(
        {
         "messages":[
           {
            "role":"user",
            "content":query
           }
         ]
        }
    )
    logger.info("Budget agent ended execution")
    return result
