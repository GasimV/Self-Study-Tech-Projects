from langchain_ollama import ChatOllama

def get_llm():
    return ChatOllama(
        model="gemma3:1b",
        temperature=0,
        seed=42,
    )
