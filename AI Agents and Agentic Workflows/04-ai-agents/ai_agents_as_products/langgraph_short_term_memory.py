"""Azerbaijan short-term thread memory in an Azerbaijani travel system."""

import asyncio
import os
import sys
import uuid
from enum import Enum
from pathlib import Path
from typing import Literal, Sequence

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# AsyncHtmlLoader reads USER_AGENT while it is being imported.
load_dotenv()
os.environ.setdefault("USER_AGENT", "AzerbaijanMemoryAssistant/1.0")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.types import Command


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "bge-m3:latest")
CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "gemma4:12b-it-q8_0")
EMBEDDING_BATCH_SIZE = 32

HOTEL_DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "multi_agent_systems"
    / "hotel_db"
    / "azerbaijan_hotels.db"
)

AZERBAIJAN_DESTINATION_URLS = [
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

MOCK_BNB_OFFERS = [
    {"bnb_id": 1, "bnb_name": "Barda Heritage Guesthouse", "town": "Barda", "available_rooms": 3, "price_per_room_azn": 75.0},
    {"bnb_id": 2, "bnb_name": "Baku Old City Guesthouse", "town": "Baku", "available_rooms": 4, "price_per_room_azn": 130.0},
    {"bnb_id": 3, "bnb_name": "Tovuz Vineyard Guesthouse", "town": "Tovuz", "available_rooms": 3, "price_per_room_azn": 80.0},
    {"bnb_id": 4, "bnb_name": "Nizami Guesthouse", "town": "Ganja", "available_rooms": 3, "price_per_room_azn": 85.0},
    {"bnb_id": 5, "bnb_name": "Salyan Riverside Guesthouse", "town": "Salyan", "available_rooms": 3, "price_per_room_azn": 70.0},
    {"bnb_id": 6, "bnb_name": "Quba Orchard Guesthouse", "town": "Quba", "available_rooms": 4, "price_per_room_azn": 95.0},
    {"bnb_id": 7, "bnb_name": "Shahdag Guesthouse", "town": "Qusar", "available_rooms": 3, "price_per_room_azn": 120.0},
    {"bnb_id": 8, "bnb_name": "Xachmaz Forest Guesthouse", "town": "Xachmaz", "available_rooms": 4, "price_per_room_azn": 85.0},
    {"bnb_id": 9, "bnb_name": "Sheki Silk Road Guesthouse", "town": "Sheki", "available_rooms": 3, "price_per_room_azn": 100.0},
    {"bnb_id": 10, "bnb_name": "Gabala Mountain View BnB", "town": "Gabala", "available_rooms": 3, "price_per_room_azn": 125.0},
    {"bnb_id": 11, "bnb_name": "Lankaran Citrus Guesthouse", "town": "Lankaran", "available_rooms": 4, "price_per_room_azn": 85.0},
    {"bnb_id": 12, "bnb_name": "Shamakhi Observatory BnB", "town": "Shamakhi", "available_rooms": 3, "price_per_room_azn": 90.0},
    {"bnb_id": 13, "bnb_name": "Alinja BnB", "town": "Nakhchivan", "available_rooms": 3, "price_per_room_azn": 95.0},
    {"bnb_id": 14, "bnb_name": "Naftalan Spa Guesthouse", "town": "Naftalan", "available_rooms": 4, "price_per_room_azn": 110.0},
    {"bnb_id": 15, "bnb_name": "Goygol Lakeside Guesthouse", "town": "Goygol", "available_rooms": 3, "price_per_room_azn": 100.0},
]

WEATHER_OPTIONS = ("sunny", "foggy", "rainy", "windy")


class AgentType(str, Enum):
    """Specialists available to the router."""

    travel_info_agent = "travel_info_agent"
    accommodation_booking_agent = "accommodation_booking_agent"


class AgentTypeOutput(BaseModel):
    """Structured output returned by the router model."""

    agent: AgentType = Field(
        ...,
        description="Which agent should handle the query?",
    )


def normalize_town(town: str) -> str:
    """Normalize common English and Azerbaijani town spellings."""
    aliases = {
        "bakı": "baku",
        "gəncə": "ganja",
        "gence": "ganja",
        "xaçmaz": "xachmaz",
        "khachmaz": "xachmaz",
        "şəki": "sheki",
        "shaki": "sheki",
        "qəbələ": "gabala",
        "qabala": "gabala",
        "lənkəran": "lankaran",
        "şamaxı": "shamakhi",
        "naxçıvan": "nakhchivan",
        "göygöl": "goygol",
    }
    normalized = " ".join(town.strip().casefold().split())
    return aliases.get(normalized, normalized)


async def build_vectorstore(urls: Sequence[str]) -> Chroma:
    """Download Azerbaijani destination pages and build a Chroma store."""
    print("Downloading Azerbaijani destination pages ...")
    raw_docs = await AsyncHtmlLoader(list(urls)).aload()
    docs = Html2TextTransformer().transform_documents(raw_docs)
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=128,
    ).split_documents(docs)

    print(
        f"Embedding {len(chunks)} chunks in batches of "
        f"{EMBEDDING_BATCH_SIZE} ..."
    )
    vectorstore = Chroma(
        embedding_function=OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
    )

    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        end = min(start + EMBEDDING_BATCH_SIZE, len(chunks))
        vectorstore.add_documents(chunks[start:end])
        print(f"\rEmbedded {end}/{len(chunks)} chunks", end="", flush=True)

    print("\nVector store ready.\n")
    return vectorstore


async def build_travel_assistant():
    """Build the router workflow and compile it with in-memory checkpoints."""
    if not HOTEL_DB_PATH.exists():
        raise FileNotFoundError(
            f"Hotel database not found: {HOTEL_DB_PATH}. Create it from "
            "multi_agent_systems/hotel_db/azerbaijan_hotels_schema.sql first."
        )

    vectorstore = await build_vectorstore(AZERBAIJAN_DESTINATION_URLS)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    @tool(
        description=(
            "Search embedded reference content about Azerbaijani cities, "
            "destinations, attractions, activities, and other travel facts."
        )
    )
    def search_travel_info(query: str) -> str:
        """Search travel information about destinations in Azerbaijan."""
        documents = retriever.invoke(query)
        return "\n---\n".join(document.page_content for document in documents)

    @tool(
        description=(
            "Get deterministic mock weather for an Azerbaijani town. Always "
            "use this tool for weather questions; the result is not live data."
        )
    )
    def weather_forecast(town: str) -> dict:
        """Return deterministic demonstration weather for a town."""
        normalized_town = normalize_town(town)
        seed = sum(ord(character) for character in normalized_town)
        return {
            "town": town.strip(),
            "weather": WEATHER_OPTIONS[seed % len(WEATHER_OPTIONS)],
            "temperature_c": 18 + seed % 14,
            "data_source": "mock",
        }

    @tool(
        description=(
            "Check mock BnB or guesthouse availability and per-room prices in "
            "AZN for an Azerbaijani destination and requested room count."
        )
    )
    def check_bnb_availability(destination: str, num_rooms: int = 1) -> list[dict]:
        """Return available mock BnB offers for an Azerbaijani town."""
        requested_town = normalize_town(destination)
        offers = [
            offer
            for offer in MOCK_BNB_OFFERS
            if normalize_town(str(offer["town"])) == requested_town
            and int(offer["available_rooms"]) >= num_rooms
        ]
        if offers:
            return offers
        return [
            {
                "error": (
                    f"No available BnBs found in {destination} for "
                    f"{num_rooms} room(s)."
                )
            }
        ]

    model = ChatOllama(
        model=CHAT_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
        reasoning=False,
    )

    travel_info_agent = create_agent(
        model=model,
        tools=[search_travel_info, weather_forecast],
        name="travel_info_agent",
        system_prompt=(
            "You are an Azerbaijan travel-information assistant. Use tools for "
            "all destination, attraction, and weather facts. Always call "
            "weather_forecast for weather questions and identify its output as "
            "mock rather than live weather. Do not invent missing facts."
        ),
    )

    hotel_db = SQLDatabase.from_uri(f"sqlite:///{HOTEL_DB_PATH.as_posix()}")
    hotel_tools = SQLDatabaseToolkit(db=hotel_db, llm=model).get_tools()
    accommodation_booking_agent = create_agent(
        model=model,
        tools=[*hotel_tools, check_bnb_availability],
        name="accommodation_booking_agent",
        system_prompt=(
            "You are an Azerbaijan accommodation assistant. Use the read-only "
            "SQLite tools for hotel availability and single/double-room prices. "
            "Use check_bnb_availability for BnBs and guesthouses. If no type is "
            "specified, check both; assume one room when no count is provided. "
            "All prices are in AZN. Join hotels with hotel_room_offers on "
            "hotel_id and never invent properties, availability, or prices."
        ),
    )

    router_model = model.with_structured_output(AgentTypeOutput)
    router_prompt = (
        "Route an Azerbaijan travel request to exactly one specialist. Choose "
        "travel_info_agent for destinations, attractions, activities, or "
        "weather. Choose accommodation_booking_agent for hotels, BnBs, "
        "guesthouses, availability, or prices. Booking intent takes priority."
    )

    def router_agent_node(
        state: MessagesState,
    ) -> Command[
        Literal["travel_info_agent", "accommodation_booking_agent"]
    ]:
        """Select the specialist that should handle the latest user message."""
        latest_message = state["messages"][-1]
        if not isinstance(latest_message, HumanMessage):
            return Command(goto=AgentType.travel_info_agent.value)

        decision = router_model.invoke(
            [
                SystemMessage(content=router_prompt),
                HumanMessage(content=latest_message.content),
            ]
        )
        return Command(goto=decision.agent.value)

    builder = StateGraph(MessagesState)
    builder.add_node("router_agent", router_agent_node)
    builder.add_node("travel_info_agent", travel_info_agent)
    builder.add_node("accommodation_booking_agent", accommodation_booking_agent)
    builder.add_edge("travel_info_agent", END)
    builder.add_edge("accommodation_booking_agent", END)
    builder.set_entry_point("router_agent")

    # The current create_agent API manages each specialist's tool loop. The
    # outer custom graph only performs explicit routing, so RemainingSteps,
    # create_react_agent, and a custom hard-limit state are unnecessary.
    return builder.compile(checkpointer=InMemorySaver())


async def chat_loop() -> None:
    """Chat repeatedly using one thread so earlier turns remain available."""
    travel_assistant = await build_travel_assistant()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Thread ID: {thread_id}")
    print("Azerbaijan Travel Assistant with short-term memory")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.casefold() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        result = await travel_assistant.ainvoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        print(f"Assistant: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    asyncio.run(chat_loop())
