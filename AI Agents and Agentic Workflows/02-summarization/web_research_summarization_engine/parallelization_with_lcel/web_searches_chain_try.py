from ..utilities import to_obj
from .web_searches_chain import web_searches_chain

# test chain invocation
assistant_instruction_str = '{"assistant_type": "Tour guide assistant", "assistant_instructions": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights.", "user_question": "What can I see and do in the Azerbijani town of Khankendi?"}'
assistant_instruction_dict = to_obj(assistant_instruction_str)
web_searches_list = web_searches_chain.invoke(assistant_instruction_dict)
print(web_searches_list)

# Output:
# python -m web_research_summarization_engine.parallelization_with_lcel.web_searches_chain_try

# [{'search_query': 'Azerbijan – tourist destinations, activities, history, cultural highlights', 'user_question': 'What can I see and do in the Azerbijani town of Khankendi?'}, {'search_query': 'Khankendi tourism guide – key sights, local experiences, best times to visit, accessibility', 'user_question': 'What can I see and do in the Azerbijani town of Khankendi?'}]