import asyncio
import uuid
from app.api.trip_routes import generate_trip, orchestrator
from app.models.trip_model import TripResponse
from app.core.llm import llm
from app.core.logger import get_logger

logger = get_logger(__name__)

async def test_qwen():
    destination = "goa"
    budget = 50000
    days = 5
    thread_id = str(uuid.uuid4())
    
    logger.info("Generating trip...")
    result = generate_trip(
        destination=destination,
        budget=budget,
        days=days,
        thread_id=thread_id
    )
    
    config = {"configurable": {"thread_id": thread_id}}
    state = orchestrator.get_state(config)
    while state and state.next:
        result = orchestrator.invoke(None, config)
        state = orchestrator.get_state(config)

    final_message = result["messages"][-1].content
    logger.info("FINAL MESSAGE FROM ORCHESTRATOR:")
    logger.info(final_message)
    
    logger.info("EXTRACTING WITH STRUCTURED OUTPUT...")
    structured_llm = llm.with_structured_output(TripResponse)
    
    extraction_prompt = f"""
You are a strict data extraction AI. Your task is to perfectly parse the unstructured travel itinerary below into the requested JSON schema.
Follow these RULES strictly:
1. 'itinerary' dictionary keys MUST be the day names (e.g., 'Day 1', 'Day 2', etc.). Do NOT use website names or sources as keys.
2. If the text does not contain a specific price or cost, estimate a realistic integer number based on the context. Do NOT use 0 unless it's genuinely free.
3. For 'hotel_recommendations', extract the actual names of the hotels. Do NOT extract cities or beaches (like 'Candolim' or 'Baga Beach') as hotel names. If no specific hotel name is found, invent a realistic placeholder name (e.g., 'Taj Resort Goa') and a realistic price.
4. Ensure the output strictly conforms to the expected schema.

Itinerary Text:
{final_message}
"""
    parsed_response = structured_llm.invoke(extraction_prompt)
    print("PARSED RESPONSE:")
    print(parsed_response.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(test_qwen())
