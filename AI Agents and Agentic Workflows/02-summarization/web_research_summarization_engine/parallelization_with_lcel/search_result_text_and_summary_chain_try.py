from ..utilities import to_obj
from .search_result_text_and_summary_chain import search_result_text_and_summary_chain

# test chain invocation
result_url_str = '{"result_url": "https://president.az/en/articles/view/69239/print", "search_query": "Khankendi Azerbaijan attractions", "user_question": "What can I see and do in the Azerbaijani town of Khankendi?"}'
result_url_dict = to_obj(result_url_str)

search_text_summary = search_result_text_and_summary_chain.invoke(result_url_dict)
print(search_text_summary)
# Output:
# python -m web_research_summarization_engine.parallelization_with_lcel.search_result_text_and_summary_chain_try

# {'summary': "Source Url: https://president.az/en/articles/view/69239/print\nSummary: Khankendi is one of the relatively young cities in Azerbaijan and was built as a residential area for Garabagh khans in the late 18th century. It’s located near Panahabad (Shusha) and is inhabited by Azerbaijani residents.\n\n**Here's a summary of Khankendi attractions, based on the text:**\n\n*   **Historical Significance:** Khankendi has a rich history dating back to the 18-19th centuries as a residence for Garabagh khans.\n*   **Restoration & Reconstruction:** The city was fully restored by Azerbaijan’s sovereignty in September 2023, following the Victory in the Patriotic War. This led to significant development efforts.\n*   **Development Projects:** President Ilham Aliyev has initiated numerous projects:\n    *   Kindergarten No. 1, secondary school No. 4 named after Nizami Ganjavi, and a renovated Secondary School No. 1.\n    *   University Faculty of Business and Economics was reopened with full renovation.\n    *   A modern closed-type 110/35/10 kV substation has been commissioned to improve urban grid standards.\n    *   Extensive measures are being taken to restore residential settlements, including the Karkijahan settlement.\n*   **Tourism:** The region offers nature (mountains, monuments), underground and surface resources, and tourism opportunities.  The “Bulud” hotel is part of this effort.\n*   **Victory Park:** A park has been created to reflect the people’s struggle for historical justice and territorial integrity, highlighting their heroism during the 44-day Patriotic War.\n\n", 'user_question': 'What can I see and do in the Azerbaijani town of Khankendi?'}