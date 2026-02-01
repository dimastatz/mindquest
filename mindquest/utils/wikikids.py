"""WikiKids API integration utilities."""

import requests


def search_wikikids(query: str, max_results: int = 3) -> str:
    """
    Search WikiKids for age-appropriate information about a topic.

    Args:
        query: The search query.
        max_results: Maximum number of results to return.

    Returns:
        Formatted search results as a string.
    """
    try:
        url = "https://kids.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results,
            "format": "json",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("query", {}).get("search", [])
        if not results:
            return "No results found for the query."

        formatted_results = []
        for result in results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            # Remove HTML tags from snippet
            snippet = snippet.replace("<span class='searchmatch'>", "").replace(
                "</span>", ""
            )
            formatted_results.append(f"**{title}**: {snippet}")

        return "\n".join(formatted_results)
    except requests.RequestException as exception:
        return f"Error searching WikiKids: {str(exception)}"


def get_wikikids_summary(topic: str) -> str:
    """
    Fetch a summary of a topic from WikiKids.

    Args:
        topic: The topic to summarize.

    Returns:
        A summary of the topic as a string.
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
        if not pages:
            return "No summary found for the topic."

        page = next(iter(pages.values()))
        extract = page.get("extract", "")

        if not extract:
            return "No summary found for the topic."

        return extract
    except requests.RequestException as exception:
        return f"Error fetching summary from WikiKids: {str(exception)}"
