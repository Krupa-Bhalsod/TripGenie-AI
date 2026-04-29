"""
Trip Planning API Routes with deepagents streaming support.
"""
import uuid
import json
import asyncio
from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from bson import ObjectId

from app.models.trip_model import TripRequest, TripResponse, AgentLogEntry
from app.agents.orchestrator import generate_trip, stream_trip, orchestrator
from app.db.mongodb import mongodb
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

    LangGraph stream_mode='updates' can return reducer wrappers such as
    Overwrite(value=[...]) or Add(value=[...]) instead of plain lists when
    using annotated message channels.  This function unwraps any known wrapper
    and guarantees an iterable list is always returned.
    """
    if raw is None:
        logger.debug("[normalize_messages] messages is None → []")
        return []

    type_name = type(raw).__name__
    logger.debug(f"[normalize_messages] raw type={type_name}")

    # Detect LangGraph reducer wrappers (Overwrite, Add, Replace, etc.)
    if type_name in ("Overwrite", "Add", "Replace") or hasattr(raw, "value"):
        inner = getattr(raw, "value", None)
        logger.debug(f"[normalize_messages] unwrapped {type_name} → inner type={type(inner).__name__ if inner is not None else 'NoneType'}")
        if inner is None:
            return []
        if isinstance(inner, (list, tuple)):
            return list(inner)
        return [inner]

    if isinstance(raw, (list, tuple)):
        return list(raw)

    # Single message object — wrap it
    logger.debug("[normalize_messages] wrapping single object in list")
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
            # Stream chunks as they arrive using a queue-based approach
            queue: asyncio.Queue = asyncio.Queue()
            loop = asyncio.get_event_loop()
            import concurrent.futures

            def stream_to_queue():
                try:
                    logger.debug(f"Initializing stream_trip for {thread_id}")
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
                    logger.error(f"Error inside stream_trip for {thread_id}: {e}", exc_info=True)
                    loop.call_soon_threadsafe(queue.put_nowait, {"_error": str(e)})
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None)  # Sentinel

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(stream_to_queue)

            while True:
                chunk = await queue.get()
                if chunk is None:
                    break

                # ── Per-chunk guard: bad chunks skip, stream continues ─────
                try:
                    if not isinstance(chunk, dict):
                        logger.debug(f"[stream] non-dict chunk type={type(chunk).__name__}, skipping")
                        continue

                    if "_error" in chunk:
                        yield f"data: {json.dumps({'type': 'error', 'message': chunk['_error']})}\n\n"
                        break

                    logger.debug(f"[stream] chunk keys={list(chunk.keys())}")

                    # Parse deepagents chunk: dict of node_name -> state updates
                    for node_name, update in chunk.items():
                        # ── Per-node guard ────────────────────────────────
                        try:
                            if not isinstance(update, dict):
                                logger.debug(f"[stream] node={node_name} update type={type(update).__name__}, skipping")
                                continue

                            raw_messages = update.get("messages", [])
                            logger.debug(f"[stream] node={node_name} raw messages type={type(raw_messages).__name__}")

                            messages = _normalize_messages(raw_messages)
                            logger.debug(f"[stream] node={node_name} normalized count={len(messages)}")

                            for msg in messages:
                                # ── Per-message guard ─────────────────────
                                try:
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
                                except Exception as msg_err:
                                    logger.debug(f"[stream] skipping message in node={node_name}: {msg_err}")
                                    continue

                        except Exception as node_err:
                            logger.debug(f"[stream] skipping node={node_name}: {node_err}")
                            continue

                except Exception as chunk_err:
                    logger.warning(f"[stream] skipping malformed chunk: {chunk_err}")
                    continue

            yield f"data: {json.dumps({'type': 'complete', 'thread_id': thread_id})}\n\n"
            logger.info(f"Finished streaming for {thread_id}")

        except Exception as e:
            logger.error(f"Streaming generator error: {e}", exc_info=True)
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
async def plan_trip(request: TripRequest):
    """
    Plan a trip (non-streaming). Returns structured TripResponse.
    Validates city input, runs the full 8-agent pipeline, and returns structured output.
    """
    thread_id = str(uuid.uuid4())

    try:
        logger.info(f"Planning trip to '{request.destination}' for {request.days} days @ ₹{request.budget}")

        result = await asyncio.to_thread(
            generate_trip,
            destination=request.destination,
            budget=request.budget,
            days=request.days,
            interests=request.interests,
            hotel_amenities=request.hotel_amenities,
            thread_id=thread_id,
        )

        # Extract final message from agent
        messages = result.get("messages", [])
        final_message = ""
        for msg in reversed(messages):
            content = getattr(msg, "content", "")
            if content and getattr(msg, "type", "") == "ai":
                final_message = content
                break

        if not final_message:
            final_message = str(messages[-1].content) if messages else "Trip plan generated."

        # Parse into structured TripResponse via LLM
        structured_llm = llm.with_structured_output(TripResponse)
        validated_cities = parse_destination_input(request.destination)

        extraction_prompt = f"""You are a strict data extraction AI. Parse the travel itinerary below into the exact JSON schema requested.

EXTRACTION RULES:
1. 'destinations': list of city names from the itinerary.
2. 'itinerary': dict keyed by 'Day 1', 'Day 2', etc. Each day has 'city', 'activities' (list of {{name, cost, category, description}}), 'hotel' ({{hotel_name, nightly_price, amenities_found, area, reason, source_url, budget_compliant}}), 'food_highlights' (list), 'day_total_cost', 'local_tips'.
3. 'hotels': top 3 hotel recommendations extracted from the text.
4. 'budget_breakdown': {{accommodation, activities, food, transport, total, within_budget}}.
5. 'estimated_total_cost': integer in INR.
6. 'transport_guide': string summary of transport logistics.
7. 'citations': list of URLs mentioned in the text.
8. 'confidence_score': 0.9 if hotels have source URLs, 0.7 otherwise.
9. Currency is INR. All costs must be integers.
10. If a field is missing from the text, provide a reasonable default.
11. 'city_plans': empty dict is fine.
12. 'multi_city_route': list of city names in visit order (or null for single city).

VALIDATED CITIES: {validated_cities}
USER BUDGET: ₹{request.budget}
DAYS: {request.days}

ITINERARY TEXT:
{final_message}
"""
        parsed_response = structured_llm.invoke(extraction_prompt)

        # Override with ground-truth user inputs
        parsed_response.destinations = validated_cities
        parsed_response.budget = request.budget
        parsed_response.days = request.days

        # Save to MongoDB
        trip_dict = parsed_response.model_dump()
        trip_dict["user_id"] = DUMMY_USER
        trip_dict["thread_id"] = thread_id
        trip_dict["raw_plan"] = final_message[:5000]  # Store raw for debugging

        await mongodb.db["trips"].insert_one(trip_dict)
        logger.info(f"Trip saved: thread={thread_id}")

        return parsed_response

    except APIError:
        raise
    except Exception as e:
        logger.error(f"Trip generation failed: {e}", exc_info=True)
        raise APIError(
            user_message="Failed to plan the trip. Please try again.",
            exception_string="TripGenerationError",
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ─── History & Retrieval ──────────────────────────────────────────────────────

@router.get("/history")
async def get_trip_history():
    """Get all trips for the dummy user."""
    cursor = mongodb.db["trips"].find({"user_id": DUMMY_USER}, {"raw_plan": 0})
    trips = await cursor.to_list(length=100)
    for trip in trips:
        trip["_id"] = str(trip["_id"])
    return trips


@router.get("/{trip_id}")
async def get_trip(trip_id: str):
    """Get a specific trip by ID."""
    try:
        trip = await mongodb.db["trips"].find_one(
            {"_id": ObjectId(trip_id), "user_id": DUMMY_USER},
            {"raw_plan": 0}
        )
        if not trip:
            raise APIError(
                user_message="Trip not found.",
                exception_string="NotFoundError",
                message=f"No trip with id {trip_id}",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        trip["_id"] = str(trip["_id"])
        return trip
    except APIError:
        raise
    except Exception as e:
        raise APIError(
            user_message="Invalid Trip ID.",
            exception_string="InvalidIdError",
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
