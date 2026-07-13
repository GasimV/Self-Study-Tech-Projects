from web_searching import web_search
from web_scraping import web_scrape
from llm_models import get_llm
from pydantic import BaseModel, Field, RootModel
from prompts import (
    ASSISTANT_SELECTION_PROMPT_TEMPLATE,
    WEB_SEARCH_PROMPT_TEMPLATE,
    SUMMARY_PROMPT_TEMPLATE,
    RESEARCH_REPORT_PROMPT_TEMPLATE
)

NUM_SEARCH_QUERIES = 3
NUM_SEARCH_RESULTS_PER_QUERY = 5
RESULT_TEXT_MAX_CHARS = 12000

question = 'What can I see and do in the Azerbaijani town of Khankendi?'

llm = get_llm()


class AssistantSelection(BaseModel):
    assistant_type: str = Field(description="The selected research assistant type")
    assistant_instructions: str = Field(description="Instructions for that assistant")
    user_question: str = Field(description="The original user question, unchanged")

# select research assistant instructions
assistant_selection_prompt = ASSISTANT_SELECTION_PROMPT_TEMPLATE.format(
    user_question=question
)
selection_llm = llm.with_structured_output(
    AssistantSelection,
    method="json_schema",
)
assistant_instructions = selection_llm.invoke(assistant_selection_prompt)
print(assistant_instructions)
# (.venv) PS E:\...\AI Agents and Agentic Workflows\02-summarization\02-web-research-summarization-engine> python research_engine_seq.py
# Output:
# content='{\n    "assistant_type": "Travel advisor",\n    "assistant_instructions": "You are a travel specialist assisting individuals
# planning vacations, focusing on discovering attractive destinations. Focus is on practical and insightful information for creating
# an enjoyable experience.", \n    "user_question": "What can I see and do in the Azerbaijani town of Khankendi?"\n}'
# additional_kwargs={} response_metadata={'model': 'gemma3:1b', 'created_at': '2026-07-13T03:45:49.3497322Z',
# 'done': True, 'done_reason': 'stop', 'total_duration': 36558063000, 'load_duration': 31956807100, 'prompt_eval_count': 472,
# 'prompt_eval_duration': 1479605000, 'eval_count': 76, 'eval_duration': 3110431000, 'logprobs': None, 'model_name': 'gemma3:1b',
# 'model_provider': 'ollama'} id='lc_run--019f5994-3454-71e3-a342-e00634fe247c-0' tool_calls=[] invalid_tool_calls=[]
# usage_metadata={'input_tokens': 472, 'output_tokens': 76, 'total_tokens': 548}

# The relevant information is in the "content" property.
# To convert it into a Python object, we can proceed as follows:
assistant_instructions_dict = assistant_instructions.model_dump()
print(assistant_instructions_dict)
# Output:
# {'assistant_type': 'Travel guide assistant', 'assistant_instructions': 'You are a world-travelled AI tour guide assistant.
# Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations,
# including history, attractions, and cultural insights.', 'user_question': 'What can I see and do in the Azerbaijani town of Khankendi?'}

# generate search queries
web_search_prompt = WEB_SEARCH_PROMPT_TEMPLATE.format(
    assistant_instructions=assistant_instructions_dict["assistant_instructions"],
    num_search_queries=NUM_SEARCH_QUERIES,
    user_question=assistant_instructions_dict["user_question"]
)

class WebSearchQuery(BaseModel):
    search_query: str
    user_question: str

class WebSearchQueryList(RootModel[list[WebSearchQuery]]):
    pass

web_search_llm = llm.with_structured_output(
    WebSearchQueryList,
    method="json_schema",
)
web_search_queries = web_search_llm.invoke(web_search_prompt)
web_search_queries_list = web_search_queries.model_dump()
print(web_search_queries_list)
# Output:
# [{'search_query': 'Khankendi history overview', 'user_question': 'Can you provide a detailed historical timeline for Khankendi,
# focusing on its key events that shaped its identity and development as a region?'},
# {'search_query': 'cultural attractions in Khankendi Azerbaijan', 'user_question': 'Beyond the main tourist sites, what are
# some lesser-known cultural traditions, crafts, or artistic expressions prevalent within Khankendi?
# What’s the significance of local folklore?'},
# {'search_query': 'Khankendi tourism infrastructure and current state', 'user_question': 'What is the current level of tourism
# development in Khankendi? Are there any specific challenges facing tourists, and what improvements are being made to enhance
# visitor experiences (e.g., accommodation, facilities, accessibility)?'}]

searches_and_result_urls = [
    {
        "result_urls": web_search(
            web_query=wq["search_query"],
            num_results=NUM_SEARCH_RESULTS_PER_QUERY
        ),
        "search_query": wq["search_query"]
    }
    for wq in web_search_queries_list
]
print(searches_and_result_urls)
# Output:
# [{'result_urls': ['https://caliber.az/en/post/khankendi-the-khan-is-back-to-its-throne', 'https://khankendihotels.az/',
# 'https://caspiannews.com/news-detail/khankendi-preserves-historical-identity-through-toponyms-cultural-heritage-2026-4-10-45/',
# 'https://www.tiktok.com/@diyardandiyara_2/video/7634889731771288853', 'https://team.7msport.com/677043/index.shtml'],
# 'search_query': 'Khankendi history overview'}, {'result_urls': ['https://en.wikipedia.org/wiki/Stepanakert',
# 'https://www.destimap.com/index.php?act=place&p=Khankendi,-Azerbaijan',
# 'https://www.tripadvisor.ie/Tourism-g667458-Khankendi_Nagorny_Karabakh-Vacations.html', 'https://mapcarta.com/Khankendi',
# 'https://www.tiktok.com/@subhantravel/video/7507227133274672391'], 'search_query': 'cultural attractions in Khankendi Azerbaijan'},
# {'result_urls': ['https://en.wikipedia.org/wiki/Microsoft', 'https://www.microsoft.com/en-us?msockid=1bf05dcf21186cd322a94a5a200a6dd2',
# 'https://account.microsoft.com/account', 'https://www.office.com/', 'https://signup.live.com/'],
# 'search_query': 'Khankendi tourism infrastructure & opportunities'}]

# flatten the search result urls
search_query_and_result_url_list = []
for qr in searches_and_result_urls:
    search_query_and_result_url_list.extend([{
        "search_query": qr["search_query"],
        "result_url": r}
        for r in qr["result_urls"]]
    )
print(search_query_and_result_url_list)
# Output:
# [{'search_query': 'Khankendi history overview', 'result_url': 'https://fr.wikipedia.org/wiki/Patrouille_de_France'},
# {'search_query': 'Khankendi history overview', 'result_url': ''},
# {'search_query': 'Khankendi history overview', 'result_url': 'https://www.facebook.com/patrouilledefrance.officiel/'},
# {'search_query': 'Khankendi history overview', 'result_url': 'https://www.facebook.com/patrouilledefrance.officiel/posts/1273283854359917/'},
# {'search_query': 'Khankendi history overview', 'result_url': 'https://airshowdisplay.fr/actualites/calendrier-2026-et-tournee-us-patrouille-de-france'},
# {'search_query': 'cultural attractions in Khankendi Azerbaijan', 'result_url': 'https://zormor.com/destinations/asia-azerbaijan-khankendi'},
# {'search_query': 'cultural attractions in Khankendi Azerbaijan', 'result_url': 'https://president.az/en/articles/view/69239'},
# {'search_query': 'cultural attractions in Khankendi Azerbaijan', 'result_url': 'https://www.tripadvisor.com/Attractions-g667458-Activities-Khankendi_Nagorny_Karabakh.html'},
# {'search_query': 'cultural attractions in Khankendi Azerbaijan', 'result_url': 'https://caspiannews.com/news-detail/khankendi-preserves-historical-identity-through-toponyms-cultural-heritage-2026-4-10-45/'},
# {'search_query': 'cultural attractions in Khankendi Azerbaijan', 'result_url': 'https://pinktravel.az/en/blog/khankendi-today-guide'},
# {'search_query': 'activities and tourism in Khankendi Azerbaijan', 'result_url': 'https://simplicable.com/life/activities'},
# {'search_query': 'activities and tourism in Khankendi Azerbaijan', 'result_url': 'https://www.funaroundme.com/'},
# {'search_query': 'activities and tourism in Khankendi Azerbaijan', 'result_url': 'https://www.checkwhatsgood.com/'},
# {'search_query': 'activities and tourism in Khankendi Azerbaijan', 'result_url': 'https://www.tripadvisor.com/Attractions-g2260696-Activities-c56-Sremska_Mitrovica_Vojvodina.html'},
# {'search_query': 'activities and tourism in Khankendi Azerbaijan', 'result_url': 'https://activibees.com/'}]

# scrape the result text from each result url
result_text_list = [{
    'result_text': web_scrape(
        url=re['result_url'])[:RESULT_TEXT_MAX_CHARS],
    'result_url': re['result_url'],
    'search_query': re['search_query']}
        for re in search_query_and_result_url_list]
print(result_text_list)

