"""
Constraint Filtering and Reranking Utilities
Post-retrieval processing to enforce budget, amenities, and interest constraints.
Discards non-compliant results and reranks remaining by value score.
"""
import re
from app.core.logger import get_logger

logger = get_logger(__name__)

# Known luxury chains that should NEVER appear in low-budget results
LUXURY_CHAINS = {
    "taj", "leela", "oberoi", "ritz", "four seasons", "hilton", "marriott",
    "hyatt", "ik ibis luxury", "westin", "st. regis", "w hotel", "waldorf",
    "intercontinental", "sheraton", "sofitel", "fairmont", "mandarin oriental",
    "jw marriott", "renaissance", "luxury collection", "edition", "andaz",
    "park hyatt", "grand hyatt",
}

# Budget thresholds for luxury classification (INR per night)
LUXURY_BUDGET_FLOOR = 8000  # If budget < this, discard obvious luxury chains


def extract_price_from_text(text: str) -> int | None:
    """
    Extract the first price mentioned in text (INR).
    Handles formats: ₹5000, Rs. 5000, INR 5000, 5,000, 5000/night.
    Returns integer price or None if not found.
    """
    # Normalize unicode rupee sign
    text = text.replace("₹", "INR ").replace("Rs.", "INR").replace("Rs ", "INR ")
    
    patterns = [
        r"INR\s*([\d,]+)",
        r"([\d,]+)\s*(?:per night|/night|a night|nightly)",
        r"\$\s*([\d,]+)",  # USD fallback
        r"([\d,]+)\s*(?:INR|rupees)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                price = int(match.group(1).replace(",", ""))
                if 100 < price < 500000:  # Sanity bounds
                    return price
            except ValueError:
                continue
    return None


def is_luxury_chain(hotel_name: str) -> bool:
    """Check if a hotel name belongs to a known luxury chain."""
    name_lower = hotel_name.lower()
    return any(chain in name_lower for chain in LUXURY_CHAINS)


def filter_hotel_results(
    raw_results: list[dict],
    hotel_budget_per_night: int,
    required_amenities: list[str],
    destination: str,
) -> tuple[list[dict], float]:
    """
    Filter raw Tavily hotel results against hard constraints.
    
    Returns:
        (filtered_results, confidence_score)
        confidence_score: 0.0-1.0 indicating retrieval quality
    """
    filtered = []
    discarded = 0

    for result in raw_results:
        title = result.get("title", "")
        content = result.get("content", "")
        combined = f"{title} {content}"

        # 1. Check for obvious luxury chain violation on low budgets
        if hotel_budget_per_night < LUXURY_BUDGET_FLOOR and is_luxury_chain(title):
            logger.info(f"[Filter] Discarding luxury chain '{title}' for budget ₹{hotel_budget_per_night}/night")
            discarded += 1
            continue

        # 2. Extract price and check against budget
        extracted_price = extract_price_from_text(combined)
        if extracted_price and extracted_price > hotel_budget_per_night * 1.3:  # 30% tolerance
            logger.info(f"[Filter] Discarding '{title}' — price ₹{extracted_price} exceeds budget ₹{hotel_budget_per_night}")
            discarded += 1
            continue

        # 3. Check destination match (basic containment)
        city_lower = destination.lower().split()[0]  # First word of city
        if city_lower not in combined.lower():
            logger.info(f"[Filter] Discarding '{title}' — city '{destination}' not found in content")
            discarded += 1
            continue

        # 4. Amenity score (soft check — not hard discard)
        amenity_score = 0
        if required_amenities:
            matched = sum(1 for a in required_amenities if a.lower() in combined.lower())
            amenity_score = matched / len(required_amenities)
        else:
            amenity_score = 1.0

        # 5. Relevance score from Tavily (0-1)
        relevance = result.get("score", 0.5)

        result["_amenity_score"] = amenity_score
        result["_relevance_score"] = relevance
        result["_extracted_price"] = extracted_price
        filtered.append(result)

    # Rerank: prioritize amenity match + relevance
    filtered.sort(key=lambda r: (r["_amenity_score"] * 0.6 + r["_relevance_score"] * 0.4), reverse=True)

    total = len(raw_results)
    kept = len(filtered)
    confidence = kept / total if total > 0 else 0.0

    logger.info(f"[Filter] Hotels: {kept} kept, {discarded} discarded (confidence={confidence:.2f})")
    return filtered, confidence


def filter_activity_results(
    raw_results: list[dict],
    interests: list[str],
    destination: str,
) -> list[dict]:
    """
    Filter raw Tavily activity results by destination match and interest relevance.
    """
    filtered = []

    for result in raw_results:
        title = result.get("title", "")
        content = result.get("content", "")
        combined = f"{title} {content}".lower()

        # Destination match
        city_lower = destination.lower().split()[0]
        if city_lower not in combined:
            continue

        # Interest relevance score
        interest_score = 0.0
        if interests:
            matched = sum(1 for i in interests if i.lower() in combined)
            interest_score = matched / len(interests)
        else:
            interest_score = 0.5  # Neutral for no preferences

        result["_interest_score"] = interest_score
        result["_relevance_score"] = result.get("score", 0.5)
        filtered.append(result)

    # Rerank by interest match + Tavily relevance
    filtered.sort(key=lambda r: (r["_interest_score"] * 0.5 + r["_relevance_score"] * 0.5), reverse=True)
    logger.info(f"[Filter] Activities: {len(filtered)}/{len(raw_results)} kept for {destination}")
    return filtered


def budget_compliance_check(estimated_total: int, user_budget: int) -> tuple[bool, str]:
    """Check if estimated total is within user budget with 10% tolerance."""
    if estimated_total <= user_budget:
        return True, "Budget compliant"
    elif estimated_total <= user_budget * 1.1:
        return True, f"Slightly over budget by ₹{estimated_total - user_budget} (within 10% tolerance)"
    else:
        overage = estimated_total - user_budget
        return False, f"Over budget by ₹{overage}. Total ₹{estimated_total} exceeds budget ₹{user_budget}"


def format_results_for_agent(results: list[dict], max_items: int = 5) -> str:
    """
    Format filtered Tavily results into a clean string for agent consumption.
    Only passes relevant fields — avoids token bloat.
    """
    lines = []
    for i, r in enumerate(results[:max_items], 1):
        title = r.get("title", "N/A")
        content = r.get("content", "")[:400]  # Truncate to 400 chars
        url = r.get("url", "")
        price_note = f" [~₹{r['_extracted_price']}/night]" if r.get("_extracted_price") else ""
        lines.append(f"{i}. {title}{price_note}\n   {content}\n   Source: {url}")
    return "\n\n".join(lines)
