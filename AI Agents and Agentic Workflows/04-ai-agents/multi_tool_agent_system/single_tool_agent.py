# -----------------------------------------------------------------------------
# Import libraries
# -----------------------------------------------------------------------------

import os
import asyncio
import operator
from typing import Annotated, Sequence, TypedDict
import json
from dotenv import load_dotenv

# AsyncHtmlLoader reads USER_AGENT while it is being imported.
load_dotenv()
os.environ.setdefault("USER_AGENT", "AzerbaijanTravelAssistant/1.0")

from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_chroma import Chroma
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langgraph.graph import StateGraph, END

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

async def build_vectorstore(
    destinations: Sequence[str]) -> Chroma: #B
    """Download WikiVoyage pages and create
    a Chroma vector store."""
    urls = [f"https://en.wikivoyage.org/wiki/{slug}" 
        for slug in destinations] #C
    loader = AsyncHtmlLoader(urls) #C
    print("Downloading destination pages ...") #C
    raw_docs = await loader.aload() #C
    docs = Html2TextTransformer().transform_documents(raw_docs) #C

    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128) #D
    chunks = sum([splitter.split_documents([d]) 
        for d in docs], []) #D

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
# 2. Define the only tool
# ----------------------------------------------------------------------------

@tool #A
def search_travel_info(query: str) -> str: #B
    """Search embedded WikiVoyage content for 
    information about destinations in Azerbaijan."""
    docs = ti_retriever.invoke(query) #C
    top = docs[:4] if isinstance(docs, list) else docs #C
    return "\n---\n".join(
        d.page_content for d in top) #D

#A Define the tool using the @tool decorator
#B Define the tool function, which takes a query, performs a semantic search and returns a string response from the vectorstore
#C Perform a semantic search on the vectorstore and return the top 4 results
#D Joins the top 4 results into a single string

# ----------------------------------------------------------------------------
# 3. Configure LLM with tool awareness
# ----------------------------------------------------------------------------
TOOLS = [search_travel_info] #A

llm_model = ChatOllama(
    model=CHAT_MODEL, #B
    base_url=OLLAMA_BASE_URL,
    temperature=0,
    reasoning=False,
) #B
llm_with_tools = llm_model.bind_tools(TOOLS) #C

#A Define the tools list (in our case, only one tool)
#B Instantiate the local Gemma model through Ollama
#C Bind the tools to the LLM model, which will generate a response with the tool calls

# ----------------------------------------------------------------------------
# 4. Initialize the dependencies for the LangGraph graph
# ----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# AgentState: it only contains LLM messages
# -----------------------------------------------------------------------------
class AgentState(TypedDict): #A
    messages: Annotated[Sequence[BaseMessage], operator.add] #B

#A Define the agent state
#B The agent state only contains LLM messages, which are appended to the list of messages

# -----------------------------------------------------------------------------
# CustomToolNode 
# -----------------------------------------------------------------------------

class ToolsExecutionNode: #A
    """Execute tools requested by the LLM in the last AIMessage."""

    def __init__(self, tools: Sequence): #B
        self._tools_by_name = {t.name: t for t in tools}

    def __call__(self, state: dict): #C
        messages: Sequence[BaseMessage] = state.get("messages", [])  

        last_msg = messages[-1] #D
        tool_messages: list[ToolMessage] = [] #E
        tool_calls = getattr(last_msg, 
            "tool_calls", []) #F
        
        for tool_call in tool_calls: #G
            tool_name = tool_call["name"] #H
            tool_args = tool_call["args"] #I
            tool = self._tools_by_name[tool_name] #J
            result = tool.invoke(tool_args) #K
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(result), #L
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": tool_messages} #M
    
tools_execution_node = ToolsExecutionNode(TOOLS) #N

#A Define the tools execution node
#B Initialize the tools execution node with the tools list
#C Define the __call__ method, which is called when the node is invoked
#D Get the last message from the messages list
#E Initialize the tool messages list, to gather the results of the tool calls
#F Get the tool calls from the last message
#G Iterate over the tool calls
#H Get the tool name from the tool call
#I Get the tool arguments from the tool call
#J Get the tool from the tools list
#K Invoke the tool with the arguments
#L Add the tool result to the tool messages list
#M Return the tool messages list, which contains the results of the tool calls
#N Instantiate the tools execution node, to be used as a node in the LangGraph graph


# ----------------------------------------------------------------------------
# LLM node
# ----------------------------------------------------------------------------

def llm_node(state: AgentState): #A    
    """LLM node that decides whether 
    to call the search tool."""
    current_messages = state["messages"] #B
    respose_message = llm_with_tools.invoke(
        current_messages) #C

    return {"messages": [respose_message]} #D

#A Define the LLM node
#B Get the current messages from the agent state
#C Invoke the LLM model with the current messages. The LLM will decide whether to call the search tool or return an answer.
#D Return the response message, which contains the tool call or the answer


def route_after_llm(state: AgentState) -> str:
    """Route tool requests to the tool node; otherwise finish the run."""
    last_message = state["messages"][-1]
    return "tools" if getattr(last_message, "tool_calls", []) else END

# ----------------------------------------------------------------------------
# 4. Build the LangGraph graph (llm_node + CustomToolNode)
# ----------------------------------------------------------------------------

builder = StateGraph(AgentState) #A
builder.add_node("llm_node", llm_node) #B
builder.add_node("tools", tools_execution_node) #B

builder.add_conditional_edges(
    "llm_node",
    route_after_llm,
    {"tools": "tools", END: END},
) #C

builder.add_edge("tools", "llm_node") #D

builder.set_entry_point("llm_node") #E
travel_info_agent = builder.compile() #F

#A Define the graph builder
#B Add the LLM node and the tools node to the graph
#C Add the conditional edges to the graph, to decide whether to execute the tool calls or return an answer and exit the graph
#D Add the edge from the tools node to the LLM node
#E Set the entry point to the LLM node
#F Compile the graph

# ----------------------------------------------------------------------------
# 5. Simple CLI interface
# ----------------------------------------------------------------------------

def chat_loop(): #A
    print("Azerbaijan Travel Assistant (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip() #B
        if user_input.lower() in \
            {"exit", "quit"}: #C
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


if __name__ == "__main__":
    chat_loop() 

# ----------------------------------------------------------------------------
# Example successful run
# ----------------------------------------------------------------------------
#
# (.venv) PS ...\04-ai-agents\multi_tool_agent_system> python single_tool_agent.py

# C:\Gasym\GitHub Self-Study\AI Agents and Agentic Workflows\.venv\Lib\
# site-packages\langgraph\cache\base\__init__.py:8:
# LangChainPendingDeprecationWarning: The default value of `allowed_objects`
# will change in a future version. Pass an explicit value (for example,
# allowed_objects="messages" or allowed_objects="core") to suppress this warning.
#   from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
# 
# Downloading destination pages ...
# Fetching pages: 100%|########################################| 5/5 [00:01<00:00, 4.33it/s]
# Embedding 294 chunks in batches of 32 ...
# Embedded 294/294 chunks
# Vector store ready.
#
# Azerbaijan Travel Assistant (type 'exit' to quit)
# 
# You: Suggest towns with a nice mountains in Azerbaijan
# Assistant: Azerbaijan offers stunning mountain scenery, particularly in the
# Greater Caucasus range. Here are some of the best towns and villages to visit
# for mountain views and experiences:
#
# 1. Khinalug (Xinaliq)
#
# This is one of the most unique and remote mountain villages in the country.
#
# - Why visit: It is an ancient, scenic village inhabited by an ethnic isolate
#   group. It offers a deep dive into traditional mountain life and is
#   surrounded by dramatic peaks.
# - Vibe: Remote, historical, and culturally rich.
#
# 2. Sheki
#
# Located in the northwest, Sheki is a beautiful city nestled in the Caucasus
# mountains.
#
# - Why visit: It is famous for its rich history (spanning 2,700 years) and
#   cultural monuments. It combines stunning mountain scenery with impressive
#   architecture like the Palace of the Sheki Khans.
# - Vibe: Cultural, historical, and picturesque.
#
# 3. Quba
#
# Quba is a major hub for mountain tourism in Azerbaijan.
#
# - Why visit: It serves as a gateway to the mountains and is known for its lush
#   landscapes. It is a great base for exploring the surrounding highlands and
#   is also home to a significant historical Jewish community.
# - Vibe: Accessible, scenic, and popular for nature lovers.
#
# 4. Lahich
#
# A cozy highland village located on the way to Sheki.
#
# - Why visit: It is a remote and peaceful village famous for its traditional
#   copper work. It offers a quieter, more intimate mountain experience compared
#   to the larger towns.
# - Vibe: Cozy, artisanal, and tranquil.
#
# 5. Goygol National Park
#
# While not a "town" in the urban sense, this is a primary destination for those
# seeking mountain beauty.
#
# - Why visit: It offers some of the most beautiful trekking and hiking trails
#   in Azerbaijan, featuring alpine lakes and dense forests.
# - Vibe: Pure nature, hiking, and outdoor adventure.
#
# Travel Tip: Because many of these mountain locations (especially Khinalug and
# Lahich) are remote, it is highly recommended to have a reliable offline map
# (like OsmAnd or MAPS.ME) and to be well-prepared for the terrain if you plan on
# hiking.
#
# You:
