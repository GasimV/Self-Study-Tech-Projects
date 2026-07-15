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


class ResearchReport(BaseModel):
    report_markdown: str = Field(
        description="The complete research report formatted as Markdown"
    )

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
# The research question is pipeline state, not something the model should rewrite.
for web_search_query in web_search_queries_list:
    web_search_query["user_question"] = question
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

# Scrape result text, excluding pages that failed or returned no useful text.
result_text_list = []
for result in search_query_and_result_url_list:
    result_text = web_scrape(url=result["result_url"])
    if not result_text:
        continue

    result_text_list.append({
        "result_text": result_text[:RESULT_TEXT_MAX_CHARS],
        "result_url": result["result_url"],
        "search_query": result["search_query"],
    })
print(result_text_list[:1])

# summarize each result text
result_text_summary_list = []
for rt in result_text_list:
    summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(
        search_query=rt["search_query"],
        search_result_text=rt["result_text"]
    )
    text_summary = llm.invoke(summary_prompt)

    result_text_summary_list.append({
        "text_summary": text_summary.content,
        "result_url": rt["result_url"],
        "search_query": rt["search_query"]
    })
print(result_text_summary_list[:1])
# Output:
# [{'text_summary': "Khankendi is a significant city located in the heart of the Qarabagh region of Azerbaijan and serves as the
# administrative and economic hub of the area. It’s known for its historical and cultural importance, particularly due to its ancient
# traditions and resilient spirit. The text highlights Khankendi's role as a center of deep historical and cultural significance
# within the broader context of the Qarabagh region.",
# 'result_url': 'https://khankendihotels.az/',
# 'search_query': 'Khankendi history overview'}]

# create a text including result summary and url from each result
stringified_summary_list = [
    f'Source URL: {sr["result_url"]}\nSummary: {sr["text_summary"]}'
        for sr in result_text_summary_list]
print(stringified_summary_list[:1])
# Output:
# ["Source URL: https://caliber.az/en/post/khankendi-the-khan-is-back-to-its-throne\nSummary: Khankendi is a relatively young city
# compared to other Azerbaijan cities, established in the 18th century as a residence for the khans of the Karabakh Khanate.
# It was initially a recreational town for the royal family and later became a settlement for the khans’ relatives.
# After the Karabakh Khanate's incorporation into Russian Empire, Khankendi was designated as a headquarters for Armenian families,
# leading to significant ethnic tensions. Following the Soviet Union’s collapse in 1991, Armenians migrated to Khankendi,
# resulting in a massive relocation policy and the establishment of an Armenian Republic.
# The Soviet government encouraged Armenian migration to Khankendi, with the aim of consolidating their presence.
# The Soviet Union's occupation of Karabakh led to the displacement of Azerbaijani population, and the Armenian authorities propped up
# a separatist entity in the occupied region. On September 19th, 2023, Azerbaijani army launched an anti-terror
# operation to oust separatists. The swift 23-hour campaign led to the surrender of separatist forces and
# the full restoration of Azerbaijan's sovereignty across the region."]

# merge all summary entries into one
appended_result_summaries = "\n".join(stringified_summary_list)
print(appended_result_summaries)
# This outputs a single text block with all summaries and URLs:
# Source URL: https://www....
# Summary:
# ...
# Source URL: https://.../
# Summary:
# ...

# compile report from summaries
research_report_prompt = RESEARCH_REPORT_PROMPT_TEMPLATE.format(
    research_summary=appended_result_summaries,
    user_question=question
)
report_llm = llm.with_structured_output(
    ResearchReport,
    method="json_schema",
)
research_report = report_llm.invoke(research_report_prompt)
research_report_dict = research_report.model_dump()
print(research_report_dict["report_markdown"])
# Output:
# Khankendi Azerbaijan: A Detailed Overview of Attractions and Activities

# **Introduction:**
# The Azerbaijani town of Khankendi, nestled within the Karabakh region of Azerbaijan, represents a compelling case study in post-war reconstruction, cultural preservation, and tourism development. This report will delve into what visitors can expect to see and do in Khankendi, drawing upon information from various sources – including historical records, tourist guides, and recent developments – to provide an exhaustive overview.

# **1. Historical Context & Significance:**
# The story of Khankendi begins with its strategic location within the mountainous region of Karabakh, historically a vital crossroads for trade and cultural exchange between East Anatolia and Central Asia.

# ....

# **2. Key Attractions & Activities – A Detailed Exploration:**
# Khankendi offers a unique blend of historical sites, architectural marvels, natural beauty, and cultural experiences.  Here’s a breakdown of the most prominent attractions:

# ...

# **3. Practical Considerations & Visitor Experience:**

# ...

# **4.  Challenges and Future Prospects:**
# The reconstruction of Khankendi has been a complex undertaking, facing challenges related to security concerns, economic instability, and the need for sustainable tourism practices.

# However, with ongoing efforts focused on infrastructure improvements, cultural preservation, and community engagement, Khankendi is poised for continued growth as a significant tourist destination. The focus on developing sustainable tourism practices – minimizing environmental impact while maximizing visitor experience – will be crucial to ensuring its long-term success.

# **5.  Conclusion:**
# Khankendi represents more than just a historical site; it’s a dynamic cultural hub, shaped by the resilience of its people and the ambition of its reconstruction efforts. The combination of its rich history, stunning natural beauty, and vibrant local culture makes Khankendi an unforgettable destination for travelers seeking to experience Azerbaijan's unique heritage.

# **Sources:**
# ....
