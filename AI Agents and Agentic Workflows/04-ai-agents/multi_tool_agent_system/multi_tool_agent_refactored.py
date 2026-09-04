# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------

import os
import asyncio
from typing import Sequence, TypedDict, Literal, Optional
from dotenv import load_dotenv
import random

# AsyncHtmlLoader reads USER_AGENT while it is being imported.
load_dotenv()
os.environ.setdefault("USER_AGENT", "AzerbaijanTravelAssistant/1.0")

from langchain.agents import create_agent
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# -----------------------------------------------------------------------------
# Load environment variables
# -----------------------------------------------------------------------------

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = "bge-m3:latest"
CHAT_MODEL = "gemma4:12b-it-q8_0"
EMBEDDING_BATCH_SIZE = 32

# -----------------------------------------------------------------------------
# 1. Prepare knowledge base at startup
# -----------------------------------------------------------------------------

AZERBAIJAN_DESTINATIONS = [ #A
    "Azerbaijan",
    "Baku",
    "Sheki",
    "Ganja",
    "Quba",
]

async def build_vectorstore(destinations: Sequence[str]) -> Chroma: #B
    """Download WikiVoyage pages and create a Chroma vector store."""
    urls = [f"https://en.wikivoyage.org/wiki/{slug}" for slug in destinations] #C
    loader = AsyncHtmlLoader(urls) #C
    print("Downloading destination pages ...") #C
    raw_docs = await loader.aload() #C
    docs = Html2TextTransformer().transform_documents(raw_docs) #C

    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128) #D
    chunks = sum([splitter.split_documents([d]) for d in docs], []) #D

    print(
        f"Embedding {len(chunks)} chunks in batches of "
        f"{EMBEDDING_BATCH_SIZE} ..."
    ) #E
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
    vectordb_client = Chroma(
        embedding_function=embedding_model,
    ) #E

    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        end = min(start + EMBEDDING_BATCH_SIZE, len(chunks))
        vectordb_client.add_documents(chunks[start:end])
        print(
            f"\rEmbedded {end}/{len(chunks)} chunks",
            end="",
            flush=True,
        )

    print()
    print("Vector store ready.\n")
    return vectordb_client #F


# Singleton pattern (build once)
_ti_vectorstore_client: Chroma | None = None #G

def get_travel_info_vectorstore() -> Chroma: #H
    global _ti_vectorstore_client
    if _ti_vectorstore_client is None:
        _ti_vectorstore_client = asyncio.run(
            build_vectorstore(AZERBAIJAN_DESTINATIONS))
    return _ti_vectorstore_client #I

ti_vectorstore_client = get_travel_info_vectorstore() #J
ti_retriever = ti_vectorstore_client.as_retriever() #K

#A Destination list; you can add more destinations here
#B Function to build the vectorstore and return a reference to the vectorstore client
#C Load the destination pages asynchronously from the web into a list of documents
#D Split the documents into chunks of 1024 characters with 128 characters of overlap    
#E Embed the chunks and store them in the vectorstore
#F Return the vectorstore client
#G Initialize a cache for the vectorstore client instance as None
#H Function to trigger the creation of the vectorstore and return a reference to the cache of its client instance
#I Return the a reference to the cache of the vectorstore client instance
#J Instantiate the vectorstore client
#K Instantiate the vectorstore retriever


# ----------------------------------------------------------------------------
# 2. Define the tools
# ----------------------------------------------------------------------------

@tool(
    description=(
        "Search embedded Wikivoyage content about destinations in Azerbaijan. "
        "Use this tool to find suitable cities, towns, villages, attractions, "
        "and other destination-specific travel information."
    )
) #A
def search_travel_info(query: str) -> str: #B
    """Search embedded Wikivoyage content about destinations in Azerbaijan."""
    docs = ti_retriever.invoke(query) #C
    top = docs[:4] if isinstance(docs, list) else docs #C
    return "\n---\n".join(d.page_content for d in top) #D

#A Define the tool using the @tool decorator
#B Define the tool function, which takes a query, performs a semantic search and returns a string response from the vectorstore
#C Perform a semantic search on the vectorstore and return the top 4 results
#D Joins the top 4 results into a single string

@tool(
    description=(
        "Get the weather forecast for a town. Always use this tool when the user "
        "asks about weather, including current-weather questions."
    )
)
def weather_forecast(town: str) -> dict:
    """Get a weather forecast for a town, including weather and temperature."""
    forecast = WeatherForecastService.get_forecast(town)
    if forecast is None:
        return {"error": f"No weather data available for '{town}'."}
    return forecast

# ----------------------------------------------------------------------------
# 3. Configure LLM with tool awareness
# ----------------------------------------------------------------------------
TOOLS = [search_travel_info, weather_forecast] #A

llm_model = ChatOllama(
    model=CHAT_MODEL, #B
    base_url=OLLAMA_BASE_URL,
    temperature=0,
    reasoning=False,
) #B


#A Define the tools list
#B Instantiate the local Gemma model through Ollama

# ----------------------------------------------------------------------------
# 4. Build the agent with the current LangChain API
# ----------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful Azerbaijan travel assistant that can search travel "
    "information and get weather forecasts. Use only the tools to find the "
    "information you need, including destination names. Do not supplement tool "
    "results with internal knowledge. If the tools do not provide the requested "
    "information, say that it is unavailable. Always call weather_forecast when "
    "weather information is requested, including questions about current "
    "conditions. For broad questions asking which Azerbaijani cities have "
    "particular weather, first use search_travel_info to find candidate cities, "
    "then check several of them with weather_forecast and report the matching "
    "results. Do not refuse the request or ask the user to choose a city first."
)

travel_info_agent = create_agent(
    model=llm_model,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
)

# create_agent manages the message state and model -> tools -> model loop.
# A custom AgentState, RemainingSteps, and create_react_agent are not needed.

# ----------------------------------------------------------------------------
# 5. Simple CLI interface
# ----------------------------------------------------------------------------

def chat_loop(): #A
    print("Azerbaijan Travel Assistant (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip() #B
        if user_input.lower() in {"exit", "quit"}: #C
            break
        state = {"messages": [HumanMessage(content=user_input)]} #D
        result = travel_info_agent.invoke(state) #E
        response_msg = result["messages"][-1] #F
        print(f"Assistant: {response_msg.content}\n") #G

#A Define the chat loop
#B Get the user input
#C Check if the user input is "exit" or "quit" to exit the loop
#D Create the initial state with a HumanMessage containing the user input
#E Invoke the graph with the initial state
#F Get the last message from the result, which contains the final answer
#G Print the assistant's final answer, from the content of the last message


# -----------------------------------------------------------------------------
# WeatherForecastService (Mock)
# -----------------------------------------------------------------------------

class WeatherForecast(TypedDict):
    town: str
    weather: Literal["sunny", "foggy", "rainy", "windy"]
    temperature: int

class WeatherForecastService:

    _weather_options = ["sunny", "foggy", "rainy", "windy"]
    _temp_min = 18
    _temp_max = 31

    @classmethod
    def get_forecast(cls, town: str) -> Optional[WeatherForecast]: #A
        weather = random.choice(cls._weather_options)
        temperature = random.randint(cls._temp_min, cls._temp_max)
        return WeatherForecast(town=town, weather=weather, temperature=temperature)

#A Define the get_forecast method, which returns a WeatherForecast object

if __name__ == "__main__":
    chat_loop() 


# ----------------------------------------------------------------------------
# Example successful create_agent run
# ----------------------------------------------------------------------------
#
# Downloading destination pages ...
# Fetching pages: 100%|########################################| 5/5 [00:01<00:00, 4.22it/s]
# Embedding 294 chunks in batches of 32 ...
# Embedded 294/294 chunks
# Vector store ready.
#
# Azerbaijan Travel Assistant (type 'exit' to quit)
# You: Suggest Azerbaijani towns with rainy weather
# Assistant: Based on the current weather information, Ganja is an Azerbaijani
# town experiencing rainy weather.
