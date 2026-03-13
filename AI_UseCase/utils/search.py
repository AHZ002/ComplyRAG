from tavily import TavilyClient
from config.config import TAVILY_API_KEY


def web_search(query: str, max_results: int = 3) -> tuple[str, list[str]]:
    """
    Perform a web search using Tavily API.
    Returns a tuple of (context string, list of source URLs)
    """
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic"
        )

        results = response.get("results", [])

        if not results:
            return "No relevant web results found.", []

        # Extract content and URLs
        context_parts = []
        urls = []

        for r in results:
            content = r.get("content", "")
            url = r.get("url", "")
            if content:
                context_parts.append(f"Source: {url}\n{content}")
            if url:
                urls.append(url)

        context = "\n\n".join(context_parts)
        return context, urls

    except Exception as e:
        return f"Web search failed: {str(e)}", []