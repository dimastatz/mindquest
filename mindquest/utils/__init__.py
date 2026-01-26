"""Utility functions for interacting with WikiKids API."""

import requests
from typing import Optional


def search_wikikids(topic: str, max_results: int = 5) -> str:
    """
    Search WikiKids for age-appropriate information about a topic.
    
    Args:
        topic: The topic to search for.
        max_results: Maximum number of results to return.
    
    Returns:
        A string containing formatted search results from WikiKids.
    """
    # WikiKids API endpoint
    base_url = "https://simple.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "srsearch": topic,
        "srwhat": "text",
        "srprop": "snippet",
        "list": "search",
        "srlimit": max_results,
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        
        if not search_results:
            return f"No results found for topic: {topic}"
        
        formatted_results = []
        for result in search_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "").replace("<span class='searchmatch'>", "").replace("</span>", "")
            formatted_results.append(f"**{title}**: {snippet}...")
        
        return "\n".join(formatted_results)
    
    except requests.RequestException as e:
        return f"Error searching WikiKids: {str(e)}"


def get_wikikids_summary(topic: str) -> str:
    """
    Get a brief summary of a topic from WikiKids.
    
    Args:
        topic: The topic to get a summary for.
    
    Returns:
        A string containing a brief summary of the topic.
    """
    base_url = "https://simple.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "titles": topic,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        if pages:
            page = next(iter(pages.values()))
            extract = page.get("extract", "")
            return extract if extract else f"No information found for: {topic}"
        
        return f"No information found for: {topic}"
    
    except requests.RequestException as e:
        return f"Error fetching WikiKids summary: {str(e)}"
