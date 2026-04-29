"""
TripGenie AI — Main Orchestrator using deepagents with SubAgents.
Architecture: 8 specialized subagents coordinated by a supervisor deep agent.
Uses deepagents native streaming for real-time agent progress.
"""
import json
import re
from langchain_ollama import ChatOllama
from deepagents import create_deep_agent, SubAgent
from langgraph.checkpoint.memory import MemorySaver

from app.tools.tavily_tool import multi_search
from app.tools.query_builder import (
    build_hotel_queries,
    build_activity_queries,
    build_destination_research_queries,
    build_transport_queries,
    build_food_queries,
    parse_destination_input,
)
from app.tools.constraint_filter import (
    filter_hotel_results,
    filter_activity_results,
    format_results_for_agent,
    budget_compliance_check,
)
from app.core.logger import get_logger

logger = get_logger(__name__)

# ─── LLM (Local Ollama) ────────────────────────────────────────────────────────
llm = ChatOllama(model="qwen2.5", temperature=0.0)

# ─── Memory ────────────────────────────────────────────────────────────────────
memory = MemorySaver()

# ─── Planning State (shared across tool calls in a session) ───────────────────
_plan_state: dict = {}


# ─── Tool: City Validation ────────────────────────────────────────────────────
NON_CITY_INPUTS = {
    # Continents
    "africa", "asia", "europe", "north america", "south america", "australia", "antarctica", "oceania",
    # Major countries
    "india", "china", "usa", "united states", "united states of america", "uk", "united kingdom",
    "france", "germany", "japan", "italy", "spain", "brazil", "canada", "australia", "russia",
    "mexico", "argentina", "south korea", "indonesia", "turkey", "saudi arabia", "egypt",
    "thailand", "malaysia", "vietnam", "philippines", "pakistan", "bangladesh", "nepal", "sri lanka",
    # Indian states
    "rajasthan", "kerala", "goa", "maharashtra", "gujarat", "karnataka", "tamil nadu", "andhra pradesh",
    "telangana", "uttar pradesh", "madhya pradesh", "west bengal", "punjab", "haryana", "himachal pradesh",
    "uttarakhand", "bihar", "jharkhand", "odisha", "assam", "meghalaya", "manipur", "nagaland",
    # US states
    "california", "new york state", "texas", "florida", "illinois", "ohio", "pennsylvania",
    # Generic regions
    "southeast asia", "middle east", "south asia", "western europe", "northern europe",
    "latin america", "caribbean", "scandinavia", "balkans", "north india", "south india",
}


def validate_cities_tool(destination: str) -> str:
    """
    Validate that destination contains only city names, not countries/states/regions.
    Returns JSON with 'valid' bool, 'cities' list, and 'error' if invalid.
    """
    logger.info(f"[CityValidator] Validating: {destination!r}")
    cities = parse_destination_input(destination)

    if not cities:
        return json.dumps({"valid": False, "cities": [], "error": "No destination provided."})

    invalid = []
    for city in cities:
        city_lower = city.lower().strip()
        if city_lower in NON_CITY_INPUTS:
            invalid.append(city)

    if invalid:
        error_msg = (
            f"'{', '.join(invalid)}' is not a city. "
            "Please provide specific city names only (e.g., 'Jaipur', 'Tokyo', 'Paris'). "
            "Countries, states, and regions are not supported."
        )
        logger.warning(f"[CityValidator] Rejected: {invalid}")
        return json.dumps({"valid": False, "cities": [], "error": error_msg})

    logger.info(f"[CityValidator] Validated cities: {cities}")
    return json.dumps({"valid": True, "cities": cities, "error": None})


# ─── Tool: Constraint-Aware Hotel Search ──────────────────────────────────────
def search_hotels_tool(city: str, budget: int, days: int, amenities_json: str) -> str:
    """
    Search for hotels in a city using constraint-aware queries.
    Filters results by budget and amenities BEFORE returning to agent.
    Returns a formatted string of budget-compliant hotel options with sources.
    
    Args:
        city: City name to search hotels in.
        budget: Total trip budget in INR.
        days: Number of trip days.
        amenities_json: JSON string of required amenities list.
    """
    try:
        amenities = json.loads(amenities_json) if amenities_json else []
    except Exception:
        amenities = []

    # Build constraint-aware queries
    queries, hotel_budget_per_night = build_hotel_queries(city, budget, days, amenities)
    
    # Run multiple targeted searches
    raw_results, answer_summary = multi_search(queries, max_results_per_query=5)
    
    # Filter against constraints
    filtered, confidence = filter_hotel_results(raw_results, hotel_budget_per_night, amenities, city)

    # If too few results, retry with even stricter query
    if len(filtered) < 2:
        logger.warning(f"[HotelSearch] Insufficient results ({len(filtered)}). Retrying with stricter query.")
        retry_queries = [
            f"Cheap budget hotels {city} ₹{hotel_budget_per_night} or less per night guesthouse hostel",
            f"Economy accommodation {city} under ₹{hotel_budget_per_night} night reviews",
        ]
        retry_results, _ = multi_search(retry_queries, max_results_per_query=5)
        retry_filtered, retry_conf = filter_hotel_results(retry_results, hotel_budget_per_night, amenities, city)
        filtered.extend(retry_filtered)
        confidence = max(confidence, retry_conf)

    # Store citations in plan state
    citations = [r.get("url", "") for r in filtered if r.get("url")]
    if "_citations" not in _plan_state:
        _plan_state["_citations"] = []
    _plan_state["_citations"].extend(citations)

    if not filtered:
        return (
            f"No hotels found within ₹{hotel_budget_per_night}/night budget in {city} with amenities {amenities}. "
            f"Consider increasing budget or relaxing amenity requirements. "
            f"Tavily summary: {answer_summary}"
        )

    formatted = format_results_for_agent(filtered, max_items=5)
    result = (
        f"Hotel Budget: ₹{hotel_budget_per_night}/night | Total Trip Budget: ₹{budget} | Days: {days}\n"
        f"Required Amenities: {', '.join(amenities) if amenities else 'None specified'}\n"
        f"Retrieval Confidence: {confidence:.0%}\n\n"
        f"Budget-Compliant Hotels in {city}:\n{formatted}\n\n"
        f"Tavily Insight: {answer_summary}"
    )
    return result


# ─── Tool: Constraint-Aware Activity Search ───────────────────────────────────
def search_activities_tool(city: str, budget: int, days: int, interests_json: str) -> str:
    """
    Search for activities and attractions using constraint-aware queries filtered by interests and budget.
    
    Args:
        city: City name to search activities in.
        budget: Total trip budget in INR.
        days: Number of trip days.
        interests_json: JSON string of user interests list.
    """
    try:
        interests = json.loads(interests_json) if interests_json else []
    except Exception:
        interests = []

    queries = build_activity_queries(city, budget, days, interests)
    raw_results, answer_summary = multi_search(queries, max_results_per_query=5)
    filtered = filter_activity_results(raw_results, interests, city)

    citations = [r.get("url", "") for r in filtered if r.get("url")]
    if "_citations" not in _plan_state:
        _plan_state["_citations"] = []
    _plan_state["_citations"].extend(citations)

    if not filtered:
        return (
            f"Could not find specific {interests} activities in {city} within ₹{budget} budget. "
            f"Tavily summary: {answer_summary}"
        )

    formatted = format_results_for_agent(filtered, max_items=6)
    daily_activity_budget = int((budget // days) * 0.3)
    return (
        f"Activity Budget: ~₹{daily_activity_budget}/day | Interests: {', '.join(interests) if interests else 'General sightseeing'}\n\n"
        f"Activities & Attractions in {city}:\n{formatted}\n\n"
        f"Tavily Insight: {answer_summary}"
    )


# ─── Tool: Destination Research ───────────────────────────────────────────────
def research_destination_tool(city: str) -> str:
    """
    Research a city's highlights, best areas, food scene, and local transport.
    Returns grounded city intelligence for itinerary context.
    
    Args:
        city: City name to research.
    """
    queries = build_destination_research_queries(city)
    raw_results, answer = multi_search(queries, max_results_per_query=4)

    formatted = format_results_for_agent(raw_results, max_items=4)
    return f"City Research for {city}:\n{formatted}\n\nSummary: {answer}"


# ─── Tool: Transport Research ─────────────────────────────────────────────────
def research_transport_tool(cities_json: str) -> str:
    """
    Research transportation between cities and local transport within each city.
    
    Args:
        cities_json: JSON string of city name list (e.g., '["Jaipur", "Agra"]').
    """
    try:
        cities = json.loads(cities_json)
    except Exception:
        cities = [cities_json]

    queries = build_transport_queries(cities)
    raw_results, answer = multi_search(queries, max_results_per_query=4)
    formatted = format_results_for_agent(raw_results, max_items=4)
    return f"Transport Guide for {' → '.join(cities)}:\n{formatted}\n\nSummary: {answer}"


# ─── Tool: Food Research ──────────────────────────────────────────────────────
def research_food_tool(city: str, budget: int, days: int, interests_json: str) -> str:
    """
    Research local food scene, affordable restaurants, and street food options.
    
    Args:
        city: City name.
        budget: Total trip budget.
        days: Number of days.
        interests_json: JSON string of user interests.
    """
    try:
        interests = json.loads(interests_json) if interests_json else []
    except Exception:
        interests = []

    queries = build_food_queries(city, interests, budget, days)
    raw_results, answer = multi_search(queries, max_results_per_query=4)
    formatted = format_results_for_agent(raw_results, max_items=4)
    daily_food_budget = int((budget // days) * 0.3)
    return (
        f"Food Budget: ~₹{daily_food_budget}/day\n"
        f"Local Food in {city}:\n{formatted}\n\nSummary: {answer}"
    )


# ─── Tool: Budget Compliance Check ────────────────────────────────────────────
def check_budget_compliance_tool(estimated_total: int, user_budget: int) -> str:
    """
    Check if estimated itinerary cost is within user budget.
    Returns compliance status and guidance.
    
    Args:
        estimated_total: Estimated total cost in INR.
        user_budget: User's total budget in INR.
    """
    compliant, message = budget_compliance_check(estimated_total, user_budget)
    return json.dumps({"compliant": compliant, "message": message, "estimated": estimated_total, "budget": user_budget})


# ─── SubAgent Definitions ─────────────────────────────────────────────────────

city_validation_subagent: SubAgent = {
    "name": "city_validation_agent",
    "description": (
        "Validates that the destination input contains ONLY specific city names — "
        "not countries, states, or regions. Call this FIRST for every trip request. "
        "Returns a list of validated city names or an error if input is invalid."
    ),
    "system_prompt": """You are the City Validation Agent for TripGenie AI.

Your ONLY job is to validate that the user's destination contains specific city names.

STEPS:
1. Call the `validate_cities_tool` with the exact destination string from the user.
2. If it returns valid=false, report the error clearly: say which inputs were rejected and why.
3. If valid=true, return the list of validated cities.

STRICT RULES:
- Country names (India, Japan, France) are INVALID.
- State/region names (Rajasthan, Kerala, Southeast Asia) are INVALID.
- Only specific cities (Jaipur, Tokyo, Paris, Kyoto) are VALID.
- If invalid, do NOT proceed — return the error immediately.

Return the result as JSON with keys: "valid", "cities", "error".""",
    "tools": [validate_cities_tool],
}

destination_research_subagent: SubAgent = {
    "name": "destination_research_agent",
    "description": (
        "Researches each validated city to gather: highlights, best areas to stay, "
        "food scene overview, and local transport guide. Call once per city."
    ),
    "system_prompt": """You are the Destination Research Agent for TripGenie AI.

For each city provided:
1. Call `research_destination_tool` with the city name.
2. Synthesize the results into a city overview with:
   - Top 5 highlights / must-see attractions
   - Best neighborhoods to stay
   - Local food scene summary
   - Transport overview

Keep responses factual and grounded in search results.
Cite sources (URLs) at the end of each city section.""",
    "tools": [research_destination_tool],
}

hotel_discovery_subagent: SubAgent = {
    "name": "hotel_discovery_agent",
    "description": (
        "Discovers budget-appropriate hotels for each city using constraint-aware search queries. "
        "Automatically filters out hotels exceeding the user's budget. "
        "Must be called with exact budget, days, and amenities — these are HARD constraints."
    ),
    "system_prompt": """You are the Hotel Discovery Agent for TripGenie AI.

CRITICAL RULES:
- Budget is a HARD constraint. Never recommend hotels above the per-night budget.
- Amenities are HARD requirements. If the user asked for wifi + breakfast, only include hotels offering both.
- Never suggest The Leela, Taj, Oberoi, Ritz, or any 5-star luxury chain for budgets under ₹3000/night.

STEPS for each city:
1. Call `search_hotels_tool` with city, budget, days, and amenities_json.
2. Present the 3 best budget-compliant options in this format:
   - Hotel Name | ~₹X/night | Area
   - Amenities: [list]
   - Why recommended: [brief reason]
   - Source: [URL]

If no hotels fit the budget, say so explicitly and suggest budget adjustment.
DO NOT invent hotel names. Only use hotels returned by the search tool.""",
    "tools": [search_hotels_tool],
}

activity_research_subagent: SubAgent = {
    "name": "activity_research_agent",
    "description": (
        "Discovers activities, attractions, and experiences matching user interests for each city. "
        "Filters by interest category and budget. Returns grounded, real-world activities with costs."
    ),
    "system_prompt": """You are the Activity Research Agent for TripGenie AI.

CRITICAL RULES:
- Only recommend activities that match the user's stated interests.
- All activities must be physically located within the specified city.
- Provide realistic estimated costs in INR for each activity.
- Include free activities where possible (parks, viewpoints, markets).

STEPS for each city:
1. Call `search_activities_tool` with city, budget, days, and interests_json.
2. Return a categorized list of activities:
   - [Category]: Activity Name | ~₹X | Brief description
   
Group by category (History, Food, Architecture, Nature, etc.)
Prioritize activities matching user interests.
DO NOT invent attraction names. Only use results from the search tool.""",
    "tools": [search_activities_tool],
}

itinerary_planning_subagent: SubAgent = {
    "name": "itinerary_planning_agent",
    "description": (
        "Creates the final day-by-day itinerary using the grounded hotel and activity data "
        "already discovered. Takes all research as context and synthesizes a structured plan."
    ),
    "system_prompt": """You are the Itinerary Planning Agent for TripGenie AI.

You receive pre-researched, budget-filtered hotel and activity data. Your job is synthesis.

STRICT RULES:
1. ONLY use hotels and activities from the research provided — do NOT invent new ones.
2. GEOGRAPHIC PROXIMITY: Group activities that are geographically close to minimize travel time.
3. BUDGET TRACKING: Calculate cost for each day. Keep running total.
4. INTERESTS FIRST: Prioritize activities matching user interests.
5. REALISTIC PACING: Max 3-4 major activities per day.
6. INCLUDE: Meal recommendations, local transport tips, estimated costs.

FORMAT each day as:
**Day X — [City]**
Morning: [Activity] (~₹X)
Afternoon: [Activity] (~₹X)
Evening: [Activity] (~₹X)
Dinner: [Restaurant recommendation] (~₹X)
Hotel: [Hotel name] (~₹X/night)
Day Total: ~₹X

At the end, provide:
- Total Estimated Cost: ₹X
- Budget Status: [Within / Over by ₹X]""",
    "tools": [],
}

transport_subagent: SubAgent = {
    "name": "transport_agent",
    "description": (
        "Researches local transportation within each city and inter-city logistics "
        "for multi-city trips. Provides practical getting-around guidance with costs."
    ),
    "system_prompt": """You are the Transport Agent for TripGenie AI.

For single-city trips: research local transport (metro, bus, auto, taxi costs).
For multi-city trips: research the best way to travel between cities (flight/train/bus, cost, duration).

STEPS:
1. Call `research_transport_tool` with the cities JSON array.
2. Return a practical transport guide covering:
   - Inter-city: Best mode, cost, booking tips
   - Local: Daily transport options and estimated costs

Be specific with prices in INR and durations.""",
    "tools": [research_transport_tool],
}

food_subagent: SubAgent = {
    "name": "food_research_agent",
    "description": (
        "Discovers local food recommendations, affordable restaurants, street food spots, "
        "and food neighborhoods for each city within the user's food budget."
    ),
    "system_prompt": """You are the Food Research Agent for TripGenie AI.

STEPS for each city:
1. Call `research_food_tool` with city, budget, days, and interests_json.
2. Return:
   - Top street food spots with estimated costs
   - 2-3 recommended local restaurants (budget-appropriate)
   - Signature local dishes to try
   - Best food neighborhoods

Always keep recommendations within the per-day food budget.""",
    "tools": [research_food_tool],
}

budget_validator_subagent: SubAgent = {
    "name": "budget_validator_agent",
    "description": (
        "Validates that the final itinerary cost does not exceed the user's budget. "
        "Must be called BEFORE finalizing the plan. If over budget, flags violations."
    ),
    "system_prompt": """You are the Budget Validator Agent for TripGenie AI.

STEPS:
1. Calculate total estimated cost from the itinerary.
2. Call `check_budget_compliance_tool` with estimated_total and user_budget.
3. If NOT compliant:
   - Identify the biggest cost drivers (usually hotels).
   - Suggest specific cuts (downgrade hotel tier, remove costly activity, etc.).
   - Return a REJECTION with specific actionable fixes.
4. If compliant: Return APPROVED with final budget breakdown.

The itinerary CANNOT be approved if total exceeds budget by more than 10%.""",
    "tools": [check_budget_compliance_tool],
}


# ─── Supervisor Orchestrator ──────────────────────────────────────────────────

SUPERVISOR_PROMPT = """You are the TripGenie AI Supervisor — an intelligent travel planning orchestrator.

You manage a team of specialized subagents to produce personalized, budget-compliant travel itineraries grounded in real data.

## PIPELINE (follow this exact order every time):

### STEP 1 — City Validation (MANDATORY FIRST)
→ Delegate to `city_validation_agent` with the destination string.
→ If validation FAILS: return the error immediately. DO NOT proceed.
→ If validation PASSES: note the validated city list.

### STEP 2 — Parallel Research
For each validated city, delegate to ALL of these agents:
→ `destination_research_agent` — city highlights and overview
→ `hotel_discovery_agent` — budget-filtered hotel options (include exact budget, days, amenities)
→ `activity_research_agent` — interest-matched activities (include exact budget, days, interests)
→ `food_research_agent` — local food scene (include budget, days, interests)

Also delegate to:
→ `transport_agent` — local + inter-city transport logistics

### STEP 3 — Itinerary Synthesis
→ Delegate to `itinerary_planning_agent` with ALL research collected above.
→ Provide the agent with: hotels found, activities found, food found, transport guide, budget, days, interests.

### STEP 4 — Budget Validation
→ Delegate to `budget_validator_agent` with the draft itinerary's total cost and user budget.
→ If REJECTED: send back to itinerary_planning_agent with the validator's feedback. Try once more.
→ If APPROVED: proceed to finalization.

### STEP 5 — Final Output
Compile the complete structured response including:
- Validated city list
- Day-by-day itinerary
- Hotel recommendations (budget-compliant)
- Budget breakdown (accommodation / activities / food / transport / total)
- Transport guide
- Food highlights per city
- Source citations (URLs from research)
- Confidence score based on retrieval quality

## HARD CONSTRAINTS (never violate):
- Budget: NEVER recommend options exceeding user budget. Hotels above per-night limit must be excluded.
- City scope: NEVER suggest activities/hotels outside the validated city list.
- Interests: Prioritize user's stated interests in all recommendations.
- Amenities: Only recommend hotels with the required amenities.
- Grounding: Only use data returned by search tools. Do NOT invent hotels or attractions.

## MULTI-CITY RULES:
- Allocate days proportionally (or per user guidance) across cities.
- Research inter-city transport via transport_agent.
- Sequence cities by geographic proximity to minimize travel.

Start every response by confirming which cities have been validated before proceeding."""


def create_orchestrator():
    """Create the TripGenie supervisor with all subagents."""
    return create_deep_agent(
        model=llm,
        tools=[],  # Supervisor uses no direct tools — delegates to subagents
        system_prompt=SUPERVISOR_PROMPT,
        subagents=[
            city_validation_subagent,
            destination_research_subagent,
            hotel_discovery_subagent,
            activity_research_subagent,
            itinerary_planning_subagent,
            transport_subagent,
            food_subagent,
            budget_validator_subagent,
        ],
        checkpointer=memory,
        debug=False,
        name="tripgenie_supervisor",
    )


orchestrator = create_orchestrator()


# ─── Main Planning Function ───────────────────────────────────────────────────

def generate_trip(
    destination: str,
    budget: int,
    days: int,
    interests: list,
    hotel_amenities: list,
    thread_id: str,
) -> dict:
    """
    Generate a trip plan using the supervisor + subagent pipeline.
    Returns the final orchestrator state with messages.
    """
    global _plan_state
    _plan_state = {}  # Reset per-request state

    interests_str = json.dumps(interests) if interests else "[]"
    amenities_str = json.dumps(hotel_amenities) if hotel_amenities else "[]"
    interests_display = ", ".join(interests) if interests else "general sightseeing"
    amenities_display = ", ".join(hotel_amenities) if hotel_amenities else "standard amenities"

    query = f"""Plan a {days}-day trip with the following parameters:

Destination: {destination}
Total Budget: ₹{budget} INR (this is a HARD limit)
Duration: {days} days
Interests: {interests_display}
Required Hotel Amenities: {amenities_display}

IMPORTANT CONSTRAINTS:
- Budget ₹{budget} is ABSOLUTE. Hotels must be under ₹{int(budget/days * 0.4)} per night.
- Only recommend hotels offering: {amenities_display}
- Focus activities on: {interests_display}
- All recommendations must be within {destination} only.
- Include source URLs for all hotels and major attractions.

Begin with city validation, then follow the full pipeline."""

    config = {"configurable": {"thread_id": thread_id}}

    # Check for interrupted state and resume
    try:
        state = orchestrator.get_state(config)
        if state and state.next:
            logger.info(f"Resuming interrupted run for thread {thread_id}")
            return orchestrator.invoke(None, config)
    except Exception:
        pass

    logger.info(f"Starting new trip generation for thread {thread_id} to '{destination}'")
    return orchestrator.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config,
    )


def stream_trip(
    destination: str,
    budget: int,
    days: int,
    interests: list,
    hotel_amenities: list,
    thread_id: str,
):
    """
    Stream trip generation events using deepagents native streaming.
    Yields events as they occur for real-time agent progress.
    """
    global _plan_state
    _plan_state = {}

    interests_str = json.dumps(interests) if interests else "[]"
    interests_display = ", ".join(interests) if interests else "general sightseeing"
    amenities_display = ", ".join(hotel_amenities) if hotel_amenities else "standard amenities"

    query = f"""Plan a {days}-day trip with the following parameters:

Destination: {destination}
Total Budget: ₹{budget} INR (this is a HARD limit)
Duration: {days} days
Interests: {interests_display}
Required Hotel Amenities: {amenities_display}

IMPORTANT CONSTRAINTS:
- Budget ₹{budget} is ABSOLUTE. Hotels must be under ₹{int(budget/days * 0.4)} per night.
- Only recommend hotels offering: {amenities_display}
- Focus activities on: {interests_display}
- All recommendations must be within {destination} only.
- Include source URLs for all hotels and major attractions.

Begin with city validation, then follow the full pipeline."""

    config = {"configurable": {"thread_id": thread_id}}

    return orchestrator.stream(
        {"messages": [{"role": "user", "content": query}]},
        config,
        stream_mode="updates",
    )