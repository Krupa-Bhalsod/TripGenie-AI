from app.core.llm import create_agent
from app.tools.travel_tools import budget_split_tool


budget_agent = create_agent(
    tools=[
        budget_split_tool
    ],
    system_prompt="""
You are a meticulous financial planner and budget specialist for TripGenie AI.
Your task is to analyze the total trip budget and break it down realistically into categories: Stay, Food, Activities, and Local Transport.
Ensure that the planned expenses align with the user's constraints.
Provide a realistic cost estimation for daily expenses based on the destination's cost of living.
If the budget is too low for the requested duration and destination, politely point this out and suggest where they can cut costs (e.g., choosing hostels over hotels, street food over fine dining).
Present the budget split clearly and provide an estimated total cost that is less than or equal to the user's total budget.
"""
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
