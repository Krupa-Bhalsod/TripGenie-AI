"""
Constraint-Aware Query Builder
Generates enriched, constraint-specific Tavily queries from user parameters.
This is the core fix for the retrieval quality problem.
NEVER use generic queries. ALWAYS bake in budget, interests, days, amenities.
"""
from app.core.logger import get_logger

logger = get_logger(__name__)


def build_hotel_queries(destination: str, budget: int, days: int, amenities: list[str]) -> list[str]:
    """
    Build 3 targeted hotel search queries incorporating all user constraints.
    Budget is the TOTAL budget — per-night hotel budget is estimated as 40% of daily budget.
    """
    daily_budget = budget // days
    hotel_budget_per_night = int(daily_budget * 0.4)

    amenities_str = " with " + " and ".join(amenities) if amenities else ""
    amenities_short = ", ".join(amenities) if amenities else "standard amenities"

    queries = [
        f"Best hotels in {destination} under ₹{hotel_budget_per_night} per night{amenities_str} budget traveler 2024",
        f"Affordable stays {destination} ₹{hotel_budget_per_night} nightly rate {amenities_short} reviews",
        f"Value for money accommodation {destination} under ₹{hotel_budget_per_night} night {days}-day trip",
    ]
    logger.info(f"[QueryBuilder] Hotel queries for {destination} @ ₹{hotel_budget_per_night}/night: {queries}")
    return queries, hotel_budget_per_night


def build_activity_queries(destination: str, budget: int, days: int, interests: list[str]) -> list[str]:
    """
    Build 3 targeted activity/attraction search queries incorporating all user constraints.
    """
    daily_activity_budget = int((budget // days) * 0.3)
    interests_str = " and ".join(interests) if interests else "sightseeing and culture"
    interests_tag = ", ".join(interests) if interests else "general sightseeing"

    queries = [
        f"Top {interests_str} experiences in {destination} within ₹{budget} total budget {days} days 2024",
        f"{days}-day {destination} itinerary {interests_tag} lovers affordable ₹{daily_activity_budget} per day activities",
        f"Free and budget-friendly {interests_tag} attractions {destination} worth visiting 2024",
    ]
    logger.info(f"[QueryBuilder] Activity queries for {destination}: {queries}")
    return queries


def build_destination_research_queries(destination: str) -> list[str]:
    """Build city highlights / overview queries."""
    return [
        f"{destination} travel guide highlights must-see attractions neighborhoods 2024",
        f"Best areas to stay in {destination} for tourists local food scene culture",
    ]


def build_transport_queries(cities: list[str]) -> list[str]:
    """Build transport logistics queries."""
    if len(cities) > 1:
        route = " to ".join(cities)
        return [
            f"Best way to travel {route} flight train bus cost 2024",
            f"Inter-city transport {route} duration tickets price 2024",
        ]
    city = cities[0]
    return [
        f"Local transportation guide {city} metro bus auto rickshaw cost for tourists 2024",
        f"Getting around {city} public transport options prices 2024",
    ]


def build_food_queries(destination: str, interests: list[str], budget: int, days: int) -> list[str]:
    """Build food and neighborhood queries."""
    daily_food_budget = int((budget // days) * 0.3)
    food_interests = [i for i in interests if i.lower() in ["food", "cuisine", "dining", "restaurants"]]
    food_tag = "local cuisine and street food" if not food_interests else " and ".join(food_interests)

    return [
        f"Best {food_tag} restaurants {destination} budget under ₹{daily_food_budget} per day 2024",
        f"Local food neighborhoods {destination} where to eat affordable authentic 2024",
    ]


def parse_destination_input(destination: str) -> list[str]:
    """
    Parse destination input into a list of city names.
    Supports: 'Tokyo', 'Tokyo, Kyoto', '["Paris", "Berlin"]'
    """
    import json
    import re

    destination = destination.strip()

    # Try JSON array format
    if destination.startswith("["):
        try:
            cities = json.loads(destination)
            return [c.strip() for c in cities if c.strip()]
        except json.JSONDecodeError:
            pass

    # Try comma-separated
    parts = [p.strip() for p in re.split(r",\s*", destination) if p.strip()]
    return parts
