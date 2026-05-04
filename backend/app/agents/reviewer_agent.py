from app.core.llm import create_agent
from app.core.logger import get_logger
from app.core.prompt_loader import load_prompt

logger = get_logger(__name__)

reviewer_agent = create_agent(
    tools=[],
    system_prompt=load_prompt("reviewer_agent")
)

def run_reviewer(query: str):
    logger.info("Reviewer agent started executing")
    result = reviewer_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }
    )
    logger.info("Reviewer agent ended execution")
    return result
