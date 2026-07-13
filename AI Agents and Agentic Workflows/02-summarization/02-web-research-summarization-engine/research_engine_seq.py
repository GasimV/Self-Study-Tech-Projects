from web_searching import web_search
from web_scraping import web_scrape
from llm_models import get_llm
from pydantic import BaseModel, Field
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

#print(assistant_instructions)

# (.venv) PS E:\...\AI Agents and Agentic Workflows\02-summarization\02-web-research-summarization-engine> python research_engine_seq.py

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
