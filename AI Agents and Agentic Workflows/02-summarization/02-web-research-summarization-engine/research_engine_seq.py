from web_searching import web_search
from web_scraping import web_scrape
from llm_models import get_llm
from utilities import to_obj
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

# select research assistant instructions
assistant_selection_prompt = ASSISTANT_SELECTION_PROMPT_TEMPLATE.format(
    user_question=question
)
assistant_instructions = llm.invoke(assistant_selection_prompt)

print(assistant_instructions)