from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from typing import List

def web_search(
    web_query: str,
    num_results: int) -> List[str]:
    search = DuckDuckGoSearchAPIWrapper(
        backend="duckduckgo",
        time=None,
    )
    return [r["link"]
            for r in search.results(web_query, num_results)]

# NOTE: Other web search engine wrappers provided by LangChain are
# TavilySearchResults and GoogleSearchAPIWrapper.
# Both require an API key, so the DuckDuckGoSearchAPIWrapper is used because it doesn’t.
