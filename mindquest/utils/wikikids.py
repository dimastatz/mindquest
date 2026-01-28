"""WikiKids search utilities."""

import requests


def search_wikikids(query: str, max_results: int = 3) -> str:
    """
    Search WikiKids for age-appropriate information.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        Formatted search results as a string.
    """
    try:
        # Use MediaWiki API to search WikiKids
        url = "https://kids.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 0,
            "srlimit": max_results,
            "format": "json",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        formatted_results = []
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            formatted_results.append(f"{i}. {title}: {snippet}")

        return (
            "\n".join(formatted_results) if formatted_results else "No results found."
        )
    except requests.RequestException as request_error:
        return f"Error searching WikiKids: {str(request_error)}"


def get_wikikids_summary(topic: str) -> str:
    """
    Get a summary of a topic from WikiKids.

    Args:
        topic: The topic to summarize.

    Returns:
        Summary text or error message.
    """
    try:
        url = "https://kids.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": topic,
            "prop": "extracts",
            "explaintext": True,
            "exintro": True,
            "format": "json",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():
            extract = page.get("extract", "")
            if extract:
                return extract[:500]  # Return first 500 chars

        return f"No summary found for '{topic}'."
    except requests.RequestException as request_error:
        return f"Error fetching summary: {str(request_error)}"
