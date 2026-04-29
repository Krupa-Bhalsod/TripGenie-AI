"""
Tavily search tool with advanced parameters for better retrieval quality.
Uses search_depth='advanced' and include_answer=True for richer results.
"""
from tavily import TavilyClient
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)


def search_web(query: str, max_results: int = 7, search_depth: str = "advanced") -> dict:
    """
    Execute a Tavily web search with advanced settings.
    
    Args:
        query: The search query (should be constraint-enriched, not generic).
        max_results: Number of results to return.
        search_depth: 'basic' or 'advanced'. Always use 'advanced' for hotel/activity searches.
    
    Returns:
        Tavily response dict with 'results', 'answer', etc.
    """
    logger.info(f"[Tavily] Searching: {query!r}")
    try:
        response = tavily.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=True,       # AI-synthesized answer from top results
            include_raw_content=False, # Keep payload small
        )
        result_count = len(response.get("results", []))
        logger.info(f"[Tavily] Got {result_count} results for: {query!r}")
        return response
    except Exception as e:
        logger.error(f"[Tavily] Search failed for query {query!r}: {e}")
        return {"results": [], "answer": "", "error": str(e)}


def multi_search(queries: list[str], max_results_per_query: int = 5) -> list[dict]:
    """
    Run multiple targeted Tavily searches and return all results.
    Deduplicates by URL.
    
    Args:
        queries: List of constraint-aware search queries.
        max_results_per_query: Results per individual query.
    
    Returns:
        Flat list of unique result dicts with 'url', 'title', 'content', 'score'.
    """
    seen_urls: set[str] = set()
    all_results: list[dict] = []
    answers: list[str] = []

    for query in queries:
        response = search_web(query, max_results=max_results_per_query)
        if response.get("answer"):
            answers.append(response["answer"])
        for result in response.get("results", []):
            url = result.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                all_results.append(result)

    # Attach combined answer
    return all_results, " | ".join(answers) if answers else ""