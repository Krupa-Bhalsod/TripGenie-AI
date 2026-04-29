"""
Legacy travel tools — kept for backward compatibility.
New architecture uses query_builder.py + tavily_tool.py directly via orchestrator tools.
"""
from app.tools.tavily_tool import search_web


def itinerary_tool(destination: str, days: int) -> dict:
    """Search for itinerary information. Prefer using query_builder for new code."""
    from app.tools.query_builder import build_activity_queries
    queries = build_activity_queries(destination, budget=10000, days=days, interests=[])
    return search_web(queries[0])


def budget_split_tool(budget: int) -> dict:
    """Split budget into stay, food, and activities categories."""
    return {
        "stay": int(budget * 0.4),
        "food": int(budget * 0.3),
        "activities": int(budget * 0.3),
    }


def hotel_lookup_tool(destination: str, budget_per_night: int) -> dict:
    """Lookup hotels. Prefer using search_hotels_tool in orchestrator for new code."""
    query = f"Best hotels in {destination} under ₹{budget_per_night} per night budget traveler"
    return search_web(query)


def activity_search_tool(destination: str) -> dict:
    """Search for activities. Prefer using search_activities_tool in orchestrator for new code."""
    query = f"Top tourist attractions and local food spots in {destination} 2024"
    return search_web(query)