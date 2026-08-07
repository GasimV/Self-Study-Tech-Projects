# Agentic Workflows with LangGraph

## Agentic workflows

Agentic workflows execute predefined steps in sequence. Agents dynamically select tools and adjust their paths based on intermediate results or errors.

LangGraph builds workflows as directed graphs:

- **Nodes** represent processing functions.
- **Edges** define transitions between nodes.
- **Conditional edges** route execution based on the runtime state.

A research assistant demonstrates this pattern by deciding whether to search for more sources or compile the results based on the quality of content returned by previous searches.

LangGraph extends LangChain rather than replacing it. LangChain components such as LLMs, retrievers, and embeddings can be used as building blocks inside LangGraph nodes.

## State management

State management tracks data across workflow steps through typed state objects that nodes read from and write to. State is immutable within each node, while updates accumulate as data moves through the graph.

Define state with Python's `TypedDict` for strong typing:

```python
from typing import TypedDict


class ResearchState(TypedDict):
    question: str
    search_queries: list[str]
    results: list[dict]
```

This ensures that the data flowing between nodes is type-checked. Create a graph with the typed state definition:

```python
from langgraph.graph import StateGraph

graph = StateGraph(ResearchState)
```

All nodes must receive and return updates compatible with this state structure.

## Nodes and edges

Node functions perform discrete tasks such as searching, parsing, or summarizing. They should be pure functions when possible. A node receives the current state and returns only the fields it needs to update (return partial updates such as ```{"search_queries": queries}```), not a complete replacement state:

```python
def generate_queries(state: ResearchState) -> dict:
    queries = create_search_queries(state["question"])
    return {"search_queries": queries}

# graph.add_node("node_name", node_function)
graph.add_node("generate_queries", generate_queries)
```

Connect nodes with directed edges to establish execution order:

```python
# graph.add_edge("source_node", "destination_node")
graph.add_edge("generate_queries", "search")
graph.add_edge("search", "evaluate_results")
```

Define where execution begins with either the `START` constant or `set_entry_point()`:

```python
from langgraph.graph import START, END

# graph.set_entry_point("first_node") or
graph.add_edge(START, "generate_queries")
```

Mark the endpoint by connecting the final node to `END`:

```python
graph.add_edge("write_report", END)
```

## Conditional routing

Conditional edges choose the next node from runtime conditions. For example, a research workflow can return to search when the retrieved content is insufficient or proceed to synthesis when enough sources have been found.

Router functions for conditional edges must return a string that matches (the next node names) one of the configured route keys:

```python
def route_after_evaluation(state: ResearchState) -> str:
    if len(state["results"]) < 3:
        return "search_more"
    return "write_report"

# graph.add_conditional_edges("source_node", router_function, {"option1": "node1", "option2": "node2"})
graph.add_conditional_edges(
    "evaluate_results",
    route_after_evaluation,
    {
        "search_more": "search",
        "write_report": "write_report",
    },
)
```

This makes loops and branches explicit in the graph structure.

## Compilation and execution

Compile the graph before running it:

```python
app = graph.compile()
```

Compilation validates the graph structure and creates an executable application.

## Benefits over linear chains

Converting a linear chain into a LangGraph graph separates concerns into discrete nodes. This makes workflows easier to debug, test, and extend with new capabilities.

LangGraph workflows can also preserve execution history and intermediate states. This makes it possible to inspect reasoning paths, replay workflows from checkpoints, or branch from previous decisions. These capabilities are difficult to implement with simple LangChain chains.
