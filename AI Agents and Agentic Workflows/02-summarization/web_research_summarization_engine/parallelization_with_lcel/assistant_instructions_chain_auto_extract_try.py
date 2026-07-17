from .assistant_instructions_chain_auto_extract import assistant_instructions_chain_auto_extract

question = "What can I see and do in the Azerbaijani town of Khankendi?"

assistant_instructions_dict = assistant_instructions_chain_auto_extract.invoke(question)
print(assistant_instructions_dict)
# Output: python -m web_research_summarization_engine.parallelization_with_lcel.assistant_instructions_chain_auto_extract_try   

# {'assistant_type': 'Travel guide assistant', 'assistant_instructions': 'You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights.', 'user_question': 'What can I see and do in the Azerbaijani town of Khankendi?'}