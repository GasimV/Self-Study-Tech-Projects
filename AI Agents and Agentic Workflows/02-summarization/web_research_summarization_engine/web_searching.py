from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import re
from typing import List


GENERIC_SEARCH_TERMS = {
    "about", "activities", "attractions", "best", "current", "guide",
    "history", "infrastructure", "overview", "state", "things", "tourism",
    "travel", "what", "where",
}

def web_search(
    web_query: str,
    num_results: int) -> List[str]:
    search = DuckDuckGoSearchAPIWrapper(
        backend="duckduckgo",
        time=None,
    )
    try:
        results = search.results(web_query, max(num_results * 3, num_results))
    except Exception as error:
        print(f"Search failed for {web_query!r}: {error}")
        return []

    query_terms = {
        term.lower()
        for term in re.findall(r"[A-Za-z0-9]+", web_query)
        if len(term) >= 4 and term.lower() not in GENERIC_SEARCH_TERMS
    }

    relevant_urls = []
    for result in results:
        searchable_text = " ".join(
            str(result.get(field, ""))
            for field in ("title", "snippet", "body", "link")
        ).lower()
        if not query_terms or any(term in searchable_text for term in query_terms):
            relevant_urls.append(result["link"])

    return relevant_urls[:num_results]

# NOTE: Other web search engine wrappers provided by LangChain are
# TavilySearchResults and GoogleSearchAPIWrapper.
# Both require an API key, so the DuckDuckGoSearchAPIWrapper is used because it doesn’t.
