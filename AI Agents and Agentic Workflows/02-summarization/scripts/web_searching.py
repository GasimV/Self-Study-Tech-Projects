from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from typing import List

def web_search(
    web_query: str,
    num_results: int) -> List[str]:
    search = DuckDuckGoSearchAPIWrapper()
    return [r["link"]
            for r in search.results(web_query, num_results)]
