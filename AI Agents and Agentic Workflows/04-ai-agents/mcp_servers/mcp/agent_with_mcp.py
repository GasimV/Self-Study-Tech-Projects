"""Azerbaijan travel agent using a local tool and a weather MCP server."""

import asyncio
import os
from typing import Sequence

from dotenv import load_dotenv


# AsyncHtmlLoader reads USER_AGENT while it is being imported.
load_dotenv()
os.environ.setdefault("USER_AGENT", "AzerbaijanMCPTravelAssistant/1.0")

from langchain.agents import create_agent
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "bge-m3:latest")
CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "gemma4:12b-it-q8_0")
WEATHER_MCP_URL = os.environ.get(
    "WEATHER_MCP_URL",
    "http://127.0.0.1:8020/weather-mcp",
)
EMBEDDING_BATCH_SIZE = 32


# Reference pages for Azerbaijani cities and travel destinations.
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


async def build_vectorstore(urls: Sequence[str]) -> Chroma:
    """Download destination pages and build an in-memory Chroma store."""
    print("Downloading Azerbaijani destination pages ...")
    raw_docs = await AsyncHtmlLoader(list(urls)).aload()
    docs = Html2TextTransformer().transform_documents(raw_docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=128,
    )
    chunks = splitter.split_documents(docs)

    print(
        f"Embedding {len(chunks)} chunks in batches of "
        f"{EMBEDDING_BATCH_SIZE} ..."
    )
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
    vectorstore = Chroma(embedding_function=embedding_model)

    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        end = min(start + EMBEDDING_BATCH_SIZE, len(chunks))
        vectorstore.add_documents(chunks[start:end])
        print(
            f"\rEmbedded {end}/{len(chunks)} chunks",
            end="",
            flush=True,
        )

    print("\nVector store ready.\n")
    return vectorstore


def create_travel_search_tool(vectorstore: Chroma):
    """Create a travel-search tool backed by the supplied vector store."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    @tool(
        description=(
            "Search embedded reference content about Azerbaijani destinations. "
            "Use it for cities, towns, attractions, activities, and other "
            "destination-specific travel facts. The input should be a clear "
            "semantic search query."
        )
    )
    def search_travel_info(query: str) -> str:
        """Search reference content about travel destinations in Azerbaijan."""
        documents = retriever.invoke(query)
        return "\n---\n".join(document.page_content for document in documents)

    return search_travel_info


async def load_weather_mcp_tools():
    """Load LangChain-compatible tools from the local weather MCP server."""
    mcp_client = MultiServerMCPClient(
        {
            "azerbaijan_weather": {
                "url": WEATHER_MCP_URL,
                # langchain-mcp-adapters 0.1.x uses this transport spelling.
                "transport": "streamable_http",
            }
        }
    )
    return await mcp_client.get_tools(server_name="azerbaijan_weather")


SYSTEM_PROMPT = """
You are a helpful Azerbaijan travel assistant with two kinds of tools:

- search_travel_info searches reference content for Azerbaijani destinations,
  attractions, activities, and other travel facts.
- get_weather_conditions obtains structured mock weather from the local
  Azerbaijani weather MCP server.

Use tools for factual destination and weather claims; do not supplement their
results with internal knowledge. Always call get_weather_conditions when weather
is requested. The MCP weather values are deterministic demonstration data, not
live observations, so describe them as mock conditions rather than real-time
weather. For a combined travel-and-weather question, use both tool types. For a
broad request asking which destinations match a weather condition, first find
candidate Azerbaijani destinations and then check several of them with the MCP
weather tool. If a tool cannot provide the requested information, state that
clearly and do not invent an answer.
""".strip()


async def build_agent():
    """Load MCP tools and local knowledge, then create the travel agent."""
    try:
        weather_tools = await load_weather_mcp_tools()
    except Exception as exc:
        raise RuntimeError(
            "Could not load the weather MCP tools. Start weather_mcp.py at "
            f"{WEATHER_MCP_URL} before running this agent."
        ) from exc

    vectorstore = await build_vectorstore(AZERBAIJAN_DESTINATION_URLS)
    search_travel_info = create_travel_search_tool(vectorstore)

    model = ChatOllama(
        model=CHAT_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
        reasoning=False,
    )

    # create_agent is the current LangChain agent API. It manages the
    # model -> tools -> model loop, so create_react_agent, RemainingSteps,
    # a custom AgentState, and manual graph wiring are unnecessary here.
    return create_agent(
        model=model,
        tools=[search_travel_info, *weather_tools],
        name="azerbaijan_mcp_travel_agent",
        system_prompt=SYSTEM_PROMPT,
    )


async def chat_loop(agent) -> None:
    """Run a simple interactive command-line chat loop."""
    print("Azerbaijan MCP Travel Assistant (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}
        )
        response = result["messages"][-1]
        print(f"Assistant: {response.content}\n")


async def main() -> None:
    """Build and run the Azerbaijan MCP travel assistant."""
    agent = await build_agent()
    await chat_loop(agent)


if __name__ == "__main__":
    asyncio.run(main())