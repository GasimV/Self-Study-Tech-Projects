from ..llm_models import get_llm
from ..prompts import (ASSISTANT_SELECTION_PROMPT_TEMPLATE)
from ..utilities import to_obj

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

assistant_instructions_chain_auto_extract = (
    {"user_question": RunnablePassthrough()} 
    | ASSISTANT_SELECTION_PROMPT_TEMPLATE
    | get_llm() 
    | StrOutputParser() 
    | RunnableLambda(to_obj)
)