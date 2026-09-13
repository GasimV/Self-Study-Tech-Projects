"""Azerbaijan travel system with guardrail middleware on each specialist."""

import asyncio
import os
import sys
import uuid
from enum import Enum
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# AsyncHtmlLoader reads USER_AGENT while it is being imported.
load_dotenv()
os.environ.setdefault("USER_AGENT", "AzerbaijanAgentGuardrailAssistant/1.0")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from langchain.agents import create_agent
from langchain.agents.middleware import before_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.types import Command

from langgraph_short_term_memory import (
    AZERBAIJAN_DESTINATION_URLS,
    CHAT_MODEL,
    MOCK_BNB_OFFERS,
    OLLAMA_BASE_URL,
    WEATHER_OPTIONS,
    build_vectorstore,
    normalize_town,
)


HOTEL_DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "multi_agent_systems"
    / "hotel_db"
    / "azerbaijan_hotels.db"
)


class AgentType(str, Enum):
    """Specialists available to the router."""

    travel_info_agent = "travel_info_agent"
    accommodation_booking_agent = "accommodation_booking_agent"


class AgentTypeOutput(BaseModel):
    """Structured routing decision."""

    agent: AgentType = Field(description="Which agent should handle the query?")


class GuardrailDecision(BaseModel):
    """Structured result from a specialist's scope guardrail."""

    is_in_scope: bool = Field(
        description=(
            "True only for travel, destination, attraction, weather, hotel, "
            "BnB, availability, or accommodation-price requests concerning "
            "Azerbaijan."
        )
    )
    reason: str = Field(description="Brief reason for the classification.")


async def build_travel_assistant():
    """Build an assistant whose specialists enforce their own guardrail."""
    if not HOTEL_DB_PATH.exists():
        raise FileNotFoundError(
            f"Hotel database not found: {HOTEL_DB_PATH}. Create it from "
            "multi_agent_systems/hotel_db/azerbaijan_hotels_schema.sql first."
        )

    vectorstore = await build_vectorstore(AZERBAIJAN_DESTINATION_URLS)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    @tool(
        description=(
            "Search approved reference content for facts about Azerbaijani "
            "destinations, attractions, and activities."
        )
    )
    def search_travel_info(query: str) -> str:
        """Search retrieved Azerbaijani travel content."""
        documents = retriever.invoke(query)
        return "\n---\n".join(document.page_content for document in documents)

    @tool(
        description=(
            "Get deterministic mock weather for an Azerbaijani town. Always "
            "use this tool for weather questions; its values are not live."
        )
    )
    def weather_forecast(town: str) -> dict:
        """Return deterministic demonstration weather for a town."""
        seed = sum(ord(character) for character in normalize_town(town))
        return {
            "town": town.strip(),
            "weather": WEATHER_OPTIONS[seed % len(WEATHER_OPTIONS)],
            "temperature_c": 18 + seed % 14,
            "data_source": "mock",
        }

    @tool(
        description=(
            "Check mock BnB or guesthouse availability and per-room prices "
            "in AZN for an Azerbaijani destination."
        )
    )
    def check_bnb_availability(
        destination: str, num_rooms: int = 1
    ) -> list[dict]:
        """Return available mock BnB offers for an Azerbaijani town."""
        requested_town = normalize_town(destination)
        offers = [
            offer
            for offer in MOCK_BNB_OFFERS
            if normalize_town(str(offer["town"])) == requested_town
            and int(offer["available_rooms"]) >= num_rooms
        ]
        return offers or [
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
    guardrail_model = model.with_structured_output(GuardrailDecision)
    scope_prompt = (
        "Classify the latest user request using the conversation context. "
        "Accept only requests about travel, destinations, attractions, "
        "weather, hotels, BnBs, availability, or accommodation prices in "
        "Azerbaijan. Reject unrelated topics and travel requests about other "
        "countries. Return the structured decision only."
    )

    def make_scope_guardrail(name: str):
        """Create an independent before-agent middleware for a specialist."""

        @before_agent(can_jump_to=["end"], name=name)
        async def specialist_scope_guardrail(state, runtime):
            messages = state.get("messages", [])
            latest_human = next(
                (
                    message
                    for message in reversed(messages)
                    if isinstance(message, HumanMessage)
                ),
                None,
            )
            if latest_human is None:
                return {
                    "messages": [
                        AIMessage(content="Please provide an Azerbaijan travel question.")
                    ],
                    "jump_to": "end",
                }

            decision = await guardrail_model.ainvoke(
                [SystemMessage(content=scope_prompt), *messages[-10:]]
            )
            if decision.is_in_scope:
                return None

            return {
                "messages": [
                    AIMessage(
                        content=(
                            "Sorry, I can only help with travel, weather, and "
                            "accommodation questions about Azerbaijan."
                        )
                    )
                ],
                "jump_to": "end",
            }

        return specialist_scope_guardrail

    travel_info_agent = create_agent(
        model=model,
        tools=[search_travel_info, weather_forecast],
        middleware=[make_scope_guardrail("travel_info_scope_guardrail")],
        name="travel_info_agent",
        system_prompt=(
            "You are an Azerbaijan travel-information assistant. Use tools "
            "for all destination, attraction, and weather facts. Identify "
            "weather output as mock and never invent missing facts."
        ),
    )

    hotel_database = SQLDatabase.from_uri(
        f"sqlite:///{HOTEL_DB_PATH.as_posix()}"
    )
    hotel_tools = SQLDatabaseToolkit(db=hotel_database, llm=model).get_tools()
    accommodation_booking_agent = create_agent(
        model=model,
        tools=[*hotel_tools, check_bnb_availability],
        middleware=[make_scope_guardrail("accommodation_scope_guardrail")],
        name="accommodation_booking_agent",
        system_prompt=(
            "You are an Azerbaijan accommodation assistant. Use the read-only "
            "SQLite tools for hotel availability and single/double-room "
            "prices. Use check_bnb_availability for BnBs. If no accommodation "
            "type is specified, check both and assume one room. Prices are in "
            "AZN. Join hotels with hotel_room_offers on hotel_id and do not "
            "invent properties, availability, or prices. Preserve constraints "
            "from the conversation: if a follow-up says 'cheapest', 'most "
            "expensive', 'another', 'there', or 'that city', keep the most "
            "recent destination, room type, room count, and accommodation type "
            "unless the user explicitly changes them. Never broaden a scoped "
            "city request to all of Azerbaijan. Query the tools again with the "
            "retained constraints before answering a comparison. Always use "
            "the SQLite tools before stating which hotels or hotel cities are "
            "available or unavailable. If asked which towns or cities have "
            "hotels, query all distinct hotel cities. If given multiple city "
            "names, query every requested city, return all matches, and name "
            "only the cities with no match; one missing city must not hide "
            "successful matches. A follow-up containing only city names or "
            "words such as 'them' or 'those' retains the preceding hotel or "
            "BnB intent. Never use travel-retrieval content for hotel facts."
        ),
    )

    router_model = model.with_structured_output(AgentTypeOutput)
    router_prompt = (
        "Route the latest user request to exactly one specialist using the "
        "recent conversation for context. A short correction such as 'I meant "
        "Quba' changes only the named destination: preserve the preceding "
        "intent, including hotel or BnB booking, room type, room count, and "
        "price or availability constraints. If the conversation is about "
        "accommodation, follow-ups that ask which towns have 'them', contain "
        "only one or more city names, or request another/cheaper option must "
        "remain accommodation_booking_agent. Do not route such follow-ups to "
        "general travel information. Choose "
        "travel_info_agent for destinations, attractions, activities, "
        "weather, or anything unrelated to accommodation. Choose "
        "accommodation_booking_agent for hotels, BnBs, guesthouses, "
        "availability, or prices. The selected specialist applies its own "
        "scope guardrail before its model runs."
    )

    def router_agent_node(
        state: MessagesState,
    ) -> Command[
        Literal["travel_info_agent", "accommodation_booking_agent"]
    ]:
        """Route first; the selected specialist validates scope afterward."""
        latest_human = next(
            (
                message
                for message in reversed(state["messages"])
                if isinstance(message, HumanMessage)
            ),
            None,
        )
        if latest_human is None:
            return Command(goto=AgentType.travel_info_agent.value)

        route = router_model.invoke(
            [
                SystemMessage(content=router_prompt),
                *state["messages"][-10:],
            ]
        )
        return Command(goto=route.agent.value)

    builder = StateGraph(MessagesState)
    builder.add_node("router_agent", router_agent_node)
    builder.add_node("travel_info_agent", travel_info_agent)
    builder.add_node("accommodation_booking_agent", accommodation_booking_agent)
    builder.add_edge("travel_info_agent", END)
    builder.add_edge("accommodation_booking_agent", END)
    builder.set_entry_point("router_agent")

    # Current create_agent middleware replaces the old create_react_agent
    # pre_model_hook. before_agent runs once per specialist invocation, while
    # create_agent manages that specialist's model/tool loop.
    return builder.compile(checkpointer=InMemorySaver())


async def chat_loop() -> None:
    """Run an interactive guarded assistant using one conversation thread."""
    travel_assistant = await build_travel_assistant()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Thread ID: {thread_id}")
    print("Azerbaijan Travel Assistant — agent-level guardrails")
    print("Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print()
            break
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
