from tavily import TavilyClient

from backend.core.config import settings


client = TavilyClient(api_key=settings.tavily_api_key)


def search_web(query: str) -> list[dict]:
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=settings.max_search_results,
        include_raw_content=False,
    )
    return response.get("results", [])
