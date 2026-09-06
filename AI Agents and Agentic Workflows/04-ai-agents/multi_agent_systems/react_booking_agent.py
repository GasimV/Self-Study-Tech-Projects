# This is a combined single agent with access to all travel, weather, hotel,
# and BnB tools.

# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------

import os
import asyncio
from pathlib import Path
from typing import Sequence, TypedDict, Literal, Optional, List, Dict
from dotenv import load_dotenv
import random

# AsyncHtmlLoader reads USER_AGENT while it is being imported.
load_dotenv()
os.environ.setdefault("USER_AGENT", "AzerbaijanBookingAssistant/1.0")

from langchain.agents import create_agent
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit


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

AZERBAIJAN_DESTINATION_URLS = [ #A
    "https://en.wikipedia.org/wiki/Barda,_Azerbaijan",
    "https://en.wikivoyage.org/wiki/Baku",
    "https://en.wikipedia.org/wiki/Tovuz",
    "https://en.wikivoyage.org/wiki/Ganja",
    "https://en.wikipedia.org/wiki/Salyan,_Azerbaijan",
    "https://en.wikivoyage.org/wiki/Quba",
    "https://en.wikivoyage.org/wiki/Qusar",
    "https://en.wikivoyage.org/wiki/Khachmaz",
    "https://en.wikivoyage.org/wiki/Sheki",
    "https://en.wikipedia.org/wiki/Qabala",
    "https://en.wikivoyage.org/wiki/Lankaran",
    "https://en.wikivoyage.org/wiki/Shamakhi",
    "https://en.wikivoyage.org/wiki/Nakhchivan",
    "https://en.wikivoyage.org/wiki/Naftalan",
    "https://en.wikipedia.org/wiki/Goygol_(city)",
]

async def build_vectorstore(urls: Sequence[str]) -> Chroma: #B
    """Download destination pages and create a Chroma vector store."""
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
            build_vectorstore(AZERBAIJAN_DESTINATION_URLS))
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
# 2. Define the travel tools
# ----------------------------------------------------------------------------

@tool(
    description=(
        "Search embedded reference content about destinations in Azerbaijan. "
        "Use this tool to find cities, towns, attractions, and travel details, "
        "including Barda, Baku, Tovuz, Ganja, Salyan, Quba, Qusar, Xachmaz, "
        "Sheki, Gabala, Lankaran, Shamakhi, Nakhchivan, Naftalan, and Goygol."
    )
) #A
def search_travel_info(query: str) -> str: #B
    """Search embedded reference content about destinations in Azerbaijan."""
    docs = ti_retriever.invoke(query) #C
    top = docs[:4] if isinstance(docs, list) else docs #C
    return "\n---\n".join(d.page_content for d in top) #D

#A Define the tool using the @tool decorator
#B Define the tool function, which takes a query, performs a semantic search and returns a string response from the vectorstore
#C Perform a semantic search on the vectorstore and return the top 4 results
#D Joins the top 4 results into a single string

@tool(
    description=(
        "Get the weather forecast for an Azerbaijani town. Always use this tool "
        "when the user asks about weather, including current-weather questions."
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


#A Define the travel tools list
#B Instantiate the local Gemma model through Ollama

# ----------------------------------------------------------------------------
# 4. Build the travel agent with the current LangChain API
# ----------------------------------------------------------------------------

TRAVEL_SYSTEM_PROMPT = (
    "You are a helpful Azerbaijan travel assistant that can search travel "
    "information and get weather forecasts. Use only the tools to find facts, "
    "including destination names, and do not supplement results with internal "
    "knowledge. Always call weather_forecast when weather is requested. For "
    "broad questions, first use search_travel_info to find candidate cities, "
    "then call weather_forecast for those cities."
)

travel_info_agent = create_agent(
    model=llm_model,
    tools=TOOLS,
    system_prompt=TRAVEL_SYSTEM_PROMPT,
)

# create_agent manages message state and the model -> tools -> model loop.
# AgentState, RemainingSteps, create_react_agent, and legacy hard limits are not
# needed for this basic agent.

# ----------------------------------------------------------------------------
# 5. Simple CLI interface
# ----------------------------------------------------------------------------

def chat_loop(): #A
    print("Azerbaijan Travel and Booking Assistant (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip() #B
        if user_input.lower() in {"exit", "quit"}: #C
            break
        state = {"messages": [HumanMessage(content=user_input)]} #D
        result = accommodation_booking_agent.invoke(state) #E
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

# -----------------------------------------------------------------------------
# SQLDatabaseToolkit for Hotel Booking (SQLite)
# -----------------------------------------------------------------------------
HOTEL_DB_PATH = (
    Path(__file__).resolve().parent / "hotel_db" / "azerbaijan_hotels.db"
)
if not HOTEL_DB_PATH.exists():
    raise FileNotFoundError(
        f"Hotel database not found: {HOTEL_DB_PATH}. "
        "Create it from hotel_db/azerbaijan_hotels_schema.sql first."
    )

hotel_db = SQLDatabase.from_uri(
    f"sqlite:///{HOTEL_DB_PATH.as_posix()}"
)
hotel_toolkit = SQLDatabaseToolkit(db=hotel_db, llm=llm_model)
hotel_db_toolkit_tools = hotel_toolkit.get_tools()

# -----------------------------------------------------------------------------
# BnBBookingService (Mock REST API client)
# -----------------------------------------------------------------------------

class BnBOffer(TypedDict): #A
    bnb_id: int
    bnb_name: str
    town: str
    available_rooms: int
    price_per_room: float

class BnBBookingService: #B
    @staticmethod
    def get_offers_near_town(town: str, num_rooms: int) \
        -> List[BnBOffer]: #C
        # Mocked REST API response: two BnBs per Azerbaijani destination.
        # All prices are per room in AZN.
        mock_bnb_offers = [ #D
            {"bnb_id": 1, "bnb_name": "Barda Heritage Guesthouse",
             "town": "Barda", "available_rooms": 3, "price_per_room": 75.0},
            {"bnb_id": 2, "bnb_name": "Karabakh Plain BnB",
             "town": "Barda", "available_rooms": 2, "price_per_room": 70.0},
            {"bnb_id": 3, "bnb_name": "Baku Old City Guesthouse",
             "town": "Baku", "available_rooms": 4, "price_per_room": 130.0},
            {"bnb_id": 4, "bnb_name": "Caspian Boulevard BnB",
             "town": "Baku", "available_rooms": 2, "price_per_room": 145.0},
            {"bnb_id": 5, "bnb_name": "Tovuz Vineyard Guesthouse",
             "town": "Tovuz", "available_rooms": 3, "price_per_room": 80.0},
            {"bnb_id": 6, "bnb_name": "Tovuz Garden BnB",
             "town": "Tovuz", "available_rooms": 2, "price_per_room": 76.0},
            {"bnb_id": 7, "bnb_name": "Nizami Guesthouse",
             "town": "Ganja", "available_rooms": 3, "price_per_room": 85.0},
            {"bnb_id": 8, "bnb_name": "Javad Khan BnB",
             "town": "Ganja", "available_rooms": 2, "price_per_room": 90.0},
            {"bnb_id": 9, "bnb_name": "Salyan Riverside Guesthouse",
             "town": "Salyan", "available_rooms": 3, "price_per_room": 70.0},
            {"bnb_id": 10, "bnb_name": "Mughan BnB",
             "town": "Salyan", "available_rooms": 2, "price_per_room": 68.0},
            {"bnb_id": 11, "bnb_name": "Quba Orchard Guesthouse",
             "town": "Quba", "available_rooms": 4, "price_per_room": 95.0},
            {"bnb_id": 12, "bnb_name": "Mountain Gate BnB",
             "town": "Quba", "available_rooms": 2, "price_per_room": 110.0},
            {"bnb_id": 13, "bnb_name": "Shahdag Guesthouse",
             "town": "Qusar", "available_rooms": 3, "price_per_room": 120.0},
            {"bnb_id": 14, "bnb_name": "Highlands BnB",
             "town": "Qusar", "available_rooms": 2, "price_per_room": 100.0},
            {"bnb_id": 15, "bnb_name": "Xachmaz Forest Guesthouse",
             "town": "Xachmaz", "available_rooms": 4, "price_per_room": 85.0},
            {"bnb_id": 16, "bnb_name": "Nabran Road BnB",
             "town": "Xachmaz", "available_rooms": 2, "price_per_room": 92.0},
            {"bnb_id": 17, "bnb_name": "Sheki Silk Road Guesthouse",
             "town": "Sheki", "available_rooms": 3, "price_per_room": 100.0},
            {"bnb_id": 18, "bnb_name": "Sheki Caravan BnB",
             "town": "Sheki", "available_rooms": 2, "price_per_room": 95.0},
            {"bnb_id": 19, "bnb_name": "Gabala Mountain View BnB",
             "town": "Gabala", "available_rooms": 3, "price_per_room": 125.0},
            {"bnb_id": 20, "bnb_name": "Tufandag Guesthouse",
             "town": "Gabala", "available_rooms": 2, "price_per_room": 135.0},
            {"bnb_id": 21, "bnb_name": "Lankaran Citrus Guesthouse",
             "town": "Lankaran", "available_rooms": 4, "price_per_room": 85.0},
            {"bnb_id": 22, "bnb_name": "Caspian South BnB",
             "town": "Lankaran", "available_rooms": 2, "price_per_room": 90.0},
            {"bnb_id": 23, "bnb_name": "Shamakhi Observatory BnB",
             "town": "Shamakhi", "available_rooms": 3, "price_per_room": 90.0},
            {"bnb_id": 24, "bnb_name": "Shirvan Guesthouse",
             "town": "Shamakhi", "available_rooms": 2, "price_per_room": 82.0},
            {"bnb_id": 25, "bnb_name": "Alinja BnB",
             "town": "Nakhchivan", "available_rooms": 3, "price_per_room": 95.0},
            {"bnb_id": 26, "bnb_name": "Momine Khatun Guesthouse",
             "town": "Nakhchivan", "available_rooms": 2, "price_per_room": 105.0},
            {"bnb_id": 27, "bnb_name": "Naftalan Spa Guesthouse",
             "town": "Naftalan", "available_rooms": 4, "price_per_room": 110.0},
            {"bnb_id": 28, "bnb_name": "Wellness BnB",
             "town": "Naftalan", "available_rooms": 2, "price_per_room": 120.0},
            {"bnb_id": 29, "bnb_name": "Goygol Lakeside Guesthouse",
             "town": "Goygol", "available_rooms": 3, "price_per_room": 100.0},
            {"bnb_id": 30, "bnb_name": "German Quarter BnB",
             "town": "Goygol", "available_rooms": 2, "price_per_room": 88.0},
        ]
        town_aliases = {
            "khachmaz": "xachmaz",
            "qabala": "gabala",
            "shaki": "sheki",
        }
        requested_town = town_aliases.get(town.casefold(), town.casefold())
        offers = [
            offer for offer in mock_bnb_offers
            if offer["town"].casefold() == requested_town
            and offer["available_rooms"] >= num_rooms
        ]
        return offers
    
#A Define the return type of the BnB availability tool
#B Define the BnB availability tool
#C Call the BnB booking service to get the offers
#D Mocked BnB offers

# -----------------------------------------------------------------------------
# BnB Availability Tool
# -----------------------------------------------------------------------------

@tool(
    description=(
        "Check BnB room availability and per-room prices in AZN for a "
        "destination in Azerbaijan. Use this for BnB or guesthouse requests."
    )
) #A
def check_bnb_availability(destination: str, num_rooms: int) \
    -> List[Dict]: #B

    offers = BnBBookingService.get_offers_near_town(
        destination, num_rooms)
    if not offers:
        return [{"error": f"No available BnBs found in {destination} for {num_rooms} rooms."}]
    return offers


#A Define the BnB availability tool
#B Define the input and return type of the BnB availability tool

# -----------------------------------------------------------------------------
# Combined Travel and Accommodation Booking Agent
# -----------------------------------------------------------------------------
BOOKING_TOOLS = (
    TOOLS
    + hotel_db_toolkit_tools
    + [check_bnb_availability]
) #A

BOOKING_SYSTEM_PROMPT = (
    "You are an Azerbaijan travel and accommodation booking assistant. Use "
    "search_travel_info for attractions, tourism details, and destination facts. "
    "Always call weather_forecast for weather questions, including questions "
    "about current conditions. Use the SQL database tools to check hotel room "
    "availability and prices, and use check_bnb_availability for BnB or "
    "guesthouse offers. For mixed requests, call every tool needed to answer all "
    "parts. Prices are in AZN. Use only tool results for facts, availability, "
    "prices, property names, and towns; do not invent information or offers. If "
    "the user does not specify an accommodation type, check both hotels and "
    "BnBs. Query the database with read-only SELECT statements and join hotels "
    "to hotel_room_offers using hotel_id when availability or prices are needed."
)

accommodation_booking_agent = create_agent( #B
    model=llm_model,
    tools=BOOKING_TOOLS,
    system_prompt=BOOKING_SYSTEM_PROMPT,
)

#A Combine travel, weather, hotel database, and BnB availability tools
#B Create the combined travel and accommodation booking agent


if __name__ == "__main__":
    chat_loop() 


# ----------------------------------------------------------------------------
# Before and after: combined tool access
# ----------------------------------------------------------------------------
#
# BEFORE: The CLI invoked an accommodation-only agent whose tools were limited
# to the hotel database and BnB availability. It could book accommodation but
# refused travel-information and weather requests.
#
# Azerbaijan Accommodation Booking Assistant (type 'exit' to quit)
# You: what is the weather in Barda and its main tourist destinations?
# Assistant: I'm sorry, but I don't have access to real-time weather information
# or a general tourism guide. I am specifically designed to help you find and
# book accommodations in Azerbaijan.
#
# You: yes, please find available hotels and BnBs in Barda.
# Assistant: I couldn't find any hotels in Barda, but I found these BnBs:
# - Barda Heritage Guesthouse: 3 rooms, 75.0 AZN per room
# - Karabakh Plain BnB: 2 rooms, 70.0 AZN per room
#
# You: do you know what is the weather in Baku?
# Assistant: I'm sorry, but I don't have access to real-time weather information.
# I can only assist you with booking hotels and BnBs in Azerbaijan.
#
# AFTER: The booking agent received the travel-search and weather tools in
# addition to its hotel and BnB tools. The expanded system prompt tells it which
# tool to use for each part of a mixed request, so it answers instead of refusing.
#
# Azerbaijan Travel and Booking Assistant (type 'exit' to quit)
# You: what is the weather in Barda and its main tourist destinations?
# Assistant: The current weather in Barda is sunny with a temperature of 19°C.
# Barda's main destinations and landmarks include:
# - Ancient Bridge
# - Imamzadeh Mausoleum
# - Barda Mausoleum
# - Barda Juma Mosque
# - State Art Gallery
# - Sabir Garden Park
# - Barda Sports Center
#
# You: do you know what is the weather in Baku?
# Assistant: The current weather in Baku is windy with a temperature of 31°C.
#
# You: do you know what is the weather in Barda?
# Assistant: The current weather in Barda is windy with a temperature of 26°C.
#
# Note: WeatherForecastService generates random demonstration data, so Barda's
# condition and temperature can change between calls. Replace it with a real
# weather API for factual real-time results.
