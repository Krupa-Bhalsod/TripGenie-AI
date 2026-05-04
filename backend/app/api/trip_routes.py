"""
Trip Planning API Routes with deepagents streaming support.
"""
import uuid
import json
import asyncio
from fastapi import APIRouter, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.trip_model import TripRequest, TripResponse, AgentLogEntry, Trip
from app.agents.orchestrator import generate_trip, stream_trip, orchestrator
from app.db.sqlite import get_db
from app.core.llm import llm
from app.core.exceptions import APIError
from app.core.logger import get_logger
from app.tools.query_builder import parse_destination_input

logger = get_logger(__name__)

router = APIRouter()

DUMMY_USER = "test@example.com"


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_messages(raw) -> list:
    """
    Safely normalize the 'messages' field from a LangGraph state update.
    """
    if raw is None:
        return []

    type_name = type(raw).__name__
    if type_name in ("Overwrite", "Add", "Replace") or hasattr(raw, "value"):
        inner = getattr(raw, "value", None)
        if inner is None:
            return []
        if isinstance(inner, (list, tuple)):
            return list(inner)
        return [inner]

    if isinstance(raw, (list, tuple)):
        return list(raw)

    return [raw]


# ─── Streaming Endpoint (Primary) ─────────────────────────────────────────────

@router.post("/plan/stream")
async def plan_trip_stream(request: TripRequest):
    """
    Stream trip planning progress via deepagents streaming.
    Returns Server-Sent Events (SSE) with real-time agent updates.
    """
    thread_id = str(uuid.uuid4())
    logger.info(f"Starting streaming trip for '{request.destination}' thread={thread_id}")

    async def event_generator():
        yield f"data: {json.dumps({'type': 'start', 'thread_id': thread_id, 'destination': request.destination})}\n\n"

        try:
            queue: asyncio.Queue = asyncio.Queue()
            loop = asyncio.get_event_loop()
            import concurrent.futures

            def stream_to_queue():
                try:
                    stream_iter = stream_trip(
                        destination=request.destination,
                        budget=request.budget,
                        days=request.days,
                        interests=request.interests,
                        hotel_amenities=request.hotel_amenities,
                        thread_id=thread_id,
                    )
                    for chunk in stream_iter:
                        loop.call_soon_threadsafe(queue.put_nowait, chunk)
                except Exception as e:
                    logger.error(f"Error inside stream_trip: {e}")
                    loop.call_soon_threadsafe(queue.put_nowait, {"_error": str(e)})
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None)

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(stream_to_queue)

            while True:
                chunk = await queue.get()
                if chunk is None:
                    break

                if not isinstance(chunk, dict): continue
                if "_error" in chunk:
                    yield f"data: {json.dumps({'type': 'error', 'message': chunk['_error']})}\n\n"
                    break

                for node_name, update in chunk.items():
                    if not isinstance(update, dict): continue
                    messages = _normalize_messages(update.get("messages", []))

                    for msg in messages:
                        msg_type = getattr(msg, "type", "")
                        if msg_type == "ai":
                            content = getattr(msg, "content", "")
                            tool_calls = getattr(msg, "tool_calls", [])
                            if tool_calls:
                                for tc in tool_calls:
                                    tool_name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
                                    yield f"data: {json.dumps({'type': 'tool_call', 'agent': node_name, 'tool': tool_name})}\n\n"
                            elif content:
                                yield f"data: {json.dumps({'type': 'agent_update', 'agent': node_name, 'message': str(content)[:200]})}\n\n"
                        elif msg_type == "tool":
                            tool_name = getattr(msg, "name", "")
                            yield f"data: {json.dumps({'type': 'tool_result', 'agent': node_name, 'tool': tool_name, 'status': 'done'})}\n\n"

            yield f"data: {json.dumps({'type': 'complete', 'thread_id': thread_id})}\n\n"

        except Exception as e:
            logger.error(f"Streaming generator error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ─── Standard Endpoint (Non-Streaming) ────────────────────────────────────────

@router.post("/plan", response_model=TripResponse)
async def plan_trip(request: TripRequest, db: Session = Depends(get_db)):
    """
    Plan a trip (non-streaming). Returns structured TripResponse.
    """
    thread_id = str(uuid.uuid4())

    try:
        logger.info(f"Planning trip to '{request.destination}' for {request.days} days")

        result = await asyncio.to_thread(
            generate_trip,
            destination=request.destination,
            budget=request.budget,
            days=request.days,
            interests=request.interests,
            hotel_amenities=request.hotel_amenities,
            thread_id=thread_id,
        )

        messages = result.get("messages", [])
        final_message = ""
        for msg in reversed(messages):
            content = getattr(msg, "content", "")
            if content and getattr(msg, "type", "") == "ai":
                final_message = content
                break

        if not final_message:
            final_message = str(messages[-1].content) if messages else "Trip plan generated."

        structured_llm = llm.with_structured_output(TripResponse)
        validated_cities = parse_destination_input(request.destination)

        extraction_prompt = f"""Extract travel itinerary into JSON:
        VALIDATED CITIES: {validated_cities}
        ITINERARY TEXT: {final_message}
        """
        parsed_response = structured_llm.invoke(extraction_prompt)

        parsed_response.destinations = validated_cities
        parsed_response.budget = request.budget
        parsed_response.days = request.days

        # Save to SQLite
        db_trip = Trip(
            user_id=DUMMY_USER,
            destination=request.destination,
            budget=request.budget,
            days=request.days,
            itinerary=parsed_response.itinerary,
            hotels=[h.model_dump() for h in parsed_response.hotels],
            budget_breakdown=parsed_response.budget_breakdown.model_dump() if parsed_response.budget_breakdown else None,
            estimated_total_cost=parsed_response.estimated_total_cost,
            city_highlights=[c.model_dump() for c in parsed_response.city_highlights],
            transport_guide=parsed_response.transport_guide,
            citations=parsed_response.citations,
            confidence_score=parsed_response.confidence_score,
            agent_log=[l.model_dump() for l in parsed_response.agent_log],
            destinations=parsed_response.destinations,
            city_plans=parsed_response.city_plans,
            multi_city_route=parsed_response.multi_city_route
        )
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        
        parsed_response.id = db_trip.id
        parsed_response.user_id = db_trip.user_id
        
        return parsed_response

    except Exception as e:
        logger.error(f"Trip generation failed: {e}")
        raise APIError(
            user_message="Failed to plan the trip.",
            exception_string="TripGenerationError",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ─── History & Retrieval ──────────────────────────────────────────────────────

@router.get("/history")
async def get_trip_history(db: Session = Depends(get_db)):
    """Get all trips for the dummy user."""
    trips = db.query(Trip).filter(Trip.user_id == DUMMY_USER).all()
    return trips


@router.get("/{trip_id}")
async def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get a specific trip by ID."""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == DUMMY_USER).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
