from .assistant_instructions_chain import assistant_instructions_chain

question = "What can I see and do in the Azerbaijani town of Khankendi?"

assistant_instructions = assistant_instructions_chain.invoke(question)
print(assistant_instructions)
# Output:
# content='{\n    "assistant_type": "Travel guide assistant",\n    
# "assistant_instructions": "You are a world-travelled AI tour guide assistant. 
# Your main purpose is to draft engaging, insightful, unbiased, and well-structured 
# travel reports on given locations, including history, attractions, and cultural insights.",\n    
# "user_question": "What can I see and do in the Azerbaijani town of Khankendi?"\n}' 
# additional_kwargs={} response_metadata={'model': 'gemma3:1b', 'created_at': 
# '2026-07-17T03:02:33.0241431Z', 'done': True, 'done_reason': 'stop', 
# 'total_duration': 4792898400, 'load_duration': 629192100, 'prompt_eval_count': 473, 
# 'prompt_eval_duration': 444658000, 'eval_count': 90, 'eval_duration': 3703733000, 
# 'logprobs': None, 'model_name': 'gemma3:1b', 'model_provider': 'ollama'} 
# id='lc_run--019f6e06-8284-7ae0-9a76-3e87c7ce0deb-0' tool_calls=[] invalid_tool_calls=[] 
# usage_metadata={'input_tokens': 473, 'output_tokens': 90, 'total_tokens': 563}