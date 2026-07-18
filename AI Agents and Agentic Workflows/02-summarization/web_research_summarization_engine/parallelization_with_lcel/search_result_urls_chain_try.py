from ..utilities import to_obj
from .search_result_urls_chain import search_result_urls_chain

# test chain invocation
web_search_str = '{"search_query": "Khankendi Azerbaijan attractions", "user_question": "What can I see and do in the Azerbaijani town of Khankendi?"}'
web_search_dict = to_obj(web_search_str)
result_urls_list = search_result_urls_chain.invoke(web_search_dict)
print(result_urls_list)
# Output:
# python -m web_research_summarization_engine.parallelization_with_lcel.search_result_urls_chain_try

# [{"result['url']": 'https://en.wikipedia.org/wiki/Stepanakert', 'search_query': 'Khankendi Azerbaijan attractions', 'user_question': 'What can I see and do in the Azerbaijani town of Khankendi?'}, {"result['url']": 'https://www.tripadvisor.com/Attractions-g667458-Activities-Khankendi_Nagorny_Karabakh.html', 'search_query': 'Khankendi Azerbaijan attractions', 'user_question': 'What can I see and do in the Azerbaijani town of Khankendi?'}, {"result['url']": 'https://www.tripadvisor.ie/Tourism-g667458-Khankendi_Nagorny_Karabakh-Vacations.html', 'search_query': 'Khankendi Azerbaijan attractions', 'user_question': 'What can I see and do in the Azerbaijani town of Khankendi?'}]