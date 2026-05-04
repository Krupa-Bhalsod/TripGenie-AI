"""
Extended Trip Models with multi-city support, citations, confidence scores, and agent logs.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from sqlalchemy import Column, Integer, String, JSON, Float
from app.db.sqlite import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    destination = Column(String)
    budget = Column(Integer)
    days = Column(Integer)
    itinerary = Column(JSON)
    hotels = Column(JSON)
    budget_breakdown = Column(JSON)
    estimated_total_cost = Column(Integer)
    city_highlights = Column(JSON)
    transport_guide = Column(String)
    citations = Column(JSON)
    confidence_score = Column(Float)
    agent_log = Column(JSON)
    destinations = Column(JSON)
    city_plans = Column(JSON)
    multi_city_route = Column(JSON)


# ─── Sub-models ────────────────────────────────────────────────────────────────

class HotelRecommendation(BaseModel):
    hotel_name: str = Field(description="Exact name of the hotel.")
    nightly_price: int = Field(description="Estimated cost per night in INR.")
    amenities_found: List[str] = Field(default=[], description="Amenities confirmed at this hotel.")
    area: str = Field(default="", description="Neighborhood or area of the hotel.")
    reason: str = Field(default="", description="Why this hotel is recommended for this budget.")
    source_url: str = Field(default="", description="Source URL for this recommendation.")
    budget_compliant: bool = Field(default=True, description="Does price fit within user's hotel budget?")


class Activity(BaseModel):
    name: str = Field(description="Name of the activity or attraction.")
    cost: int = Field(description="Estimated cost in INR (0 for free).")
    category: str = Field(default="", description="Category: food / history / architecture / nature / etc.")
    description: str = Field(default="", description="Brief description.")


class DayPlan(BaseModel):
    city: str = Field(description="City being visited on this day.")
    activities: List[Activity] = Field(description="Activities for this day with individual costs.")
    hotel: Optional[HotelRecommendation] = Field(None, description="Hotel for this night.")
    food_highlights: List[str] = Field(default=[], description="Recommended places to eat.")
    day_total_cost: int = Field(description="Total cost for this day (activities + food + hotel).")
    local_tips: str = Field(default="", description="Local transport or logistics tip for the day.")


class BudgetBreakdown(BaseModel):
    accommodation: int = Field(description="Total accommodation cost.")
    activities: int = Field(description="Total activities cost.")
    food: int = Field(description="Total food cost.")
    transport: int = Field(description="Total local transport cost.")
    total: int = Field(description="Grand total.")
    within_budget: bool = Field(description="Whether total is within user budget.")


class CityHighlight(BaseModel):
    city: str
    overview: str = Field(description="2-3 sentence city overview.")
    best_areas: List[str] = Field(default=[], description="Best neighborhoods to stay in.")
    food_scene: str = Field(default="", description="Local food highlights.")
    local_transport: str = Field(default="", description="How to get around locally.")


class AgentLogEntry(BaseModel):
    agent: str
    status: str  # "running" | "done" | "error" | "skipped"
    message: str = ""
    timestamp: Optional[str] = None


# ─── Request / Response ────────────────────────────────────────────────────────

class TripRequest(BaseModel):
    destination: str = Field(description="City or comma-separated cities (e.g. 'Jaipur' or 'Tokyo, Kyoto')")
    budget: int = Field(description="Total trip budget in INR.", gt=0)
    days: int = Field(description="Number of travel days.", gt=0, le=30)
    interests: List[str] = Field(default=[], description="User interests: food, history, architecture, nature, etc.")
    hotel_amenities: List[str] = Field(default=[], description="Required hotel amenities: wifi, breakfast, pool, etc.")


class TripResponse(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    destinations: List[str] = Field(description="Validated city list.")
    budget: int
    days: int
    currency: str = Field(default="INR")
    city_plans: Dict[str, Any] = Field(description="Per-city itinerary plans keyed by city name.")
    multi_city_route: Optional[List[str]] = Field(None, description="Optimized visit order for multi-city trips.")
    itinerary: Dict[str, DayPlan] = Field(description="Day-by-day itinerary (Day 1, Day 2, ...).")
    hotels: List[HotelRecommendation] = Field(default=[], description="Top hotel recommendations.")
    budget_breakdown: Optional[BudgetBreakdown] = None
    estimated_total_cost: int = Field(description="Estimated total cost in INR.")
    city_highlights: List[CityHighlight] = Field(default=[], description="City overview cards.")
    transport_guide: str = Field(default="", description="Transport logistics guide.")
    citations: List[str] = Field(default=[], description="Source URLs backing recommendations.")
    confidence_score: float = Field(default=0.8, description="Retrieval confidence 0.0-1.0.")
    agent_log: List[AgentLogEntry] = Field(default=[], description="Agent execution log.")

    class Config:
        from_attributes = True
