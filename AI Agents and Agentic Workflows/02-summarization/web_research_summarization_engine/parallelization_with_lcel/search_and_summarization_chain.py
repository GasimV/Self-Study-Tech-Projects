from ..llm_models import get_llm
from ..prompts import (
    RESEARCH_REPORT_PROMPT_TEMPLATE
)
#from .assistant_instructions_chain import assistant_instructions_chain
from .assistant_instructions_chain_auto_extract import (
    assistant_instructions_chain_auto_extract,
)
from .web_searches_chain import web_searches_chain
from .search_result_urls_chain import search_result_urls_chain
from .search_result_text_and_summary_chain import search_result_text_and_summary_chain

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

search_and_summarization_chain = (
    search_result_urls_chain 
    | search_result_text_and_summary_chain.map() # parallelize for each url
    | RunnableLambda(lambda x: 
        {
            'summary': '\n'.join([i['summary'] for i in x]), 
            'user_question': x[0]['user_question'] if len(x) > 0 else ''
        })
)

web_research_chain = (
    assistant_instructions_chain_auto_extract 
    | web_searches_chain 
    | search_and_summarization_chain.map() # parallelize for each web search
    | RunnableLambda(lambda x:
       {
           'research_summary': '\n\n'.join([i['summary'] for i in x]),
           'user_question': x[0]['user_question'] if len(x) > 0 else ''
        })
    | RESEARCH_REPORT_PROMPT_TEMPLATE | get_llm() | StrOutputParser()
)

# The map() operator triggers multiple instances of the Result Text and Summary chain,
# one for each dictionary from the Search Result URLs chain containing a URL. This
# allows each instance to run in parallel.

# Runnable.map() in LCEL:

# The Runnable.map() method returns a new Runnable that maps a list of inputs to a list of outputs. It allows you to run an input list through a chain concurrently rather than 
# processing items one by one in a loop.

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI

# model = ChatOpenAI()
# prompt = ChatPromptTemplate.from_template("Tell me a 1-sentence joke about {topic}")
# chain = prompt | model

# # Using .map() to process multiple topics concurrently
# map_chain = chain.map()
# results = map_chain.invoke([{"topic": "bears"}, {"topic": "computers"}, {"topic": "coffee"}])

# for joke in results:
#     print(joke.content)

# The Joined Summaries sub-chain is integrated directly within the larger 
# Search and Summarization chain rather than as a separate entity. 
# This subchain merges summaries from each instance of the Result Text and Summary chain,
# functioning as a core part of the overall process.