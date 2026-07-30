# Agentic AI Systems: Study Notes

These notes explain reusable Agentic AI concepts, architectural patterns, and implementation building blocks. Financial assistance and IT support are included as contrasting examples; neither use case defines the architecture.

<a id="contents"></a>

## Contents

- [Agentic Workflows vs AI Agents](#agentic-workflows-vs-ai-agents)
  - [Agentic Workflow](#agentic-workflow)
  - [AI Agent](#ai-agent)
    - [Practical distinction](#practical-distinction)
- [Common Agentic Workflow Patterns](#common-agentic-workflow-patterns)
  - [Router Workflow](#router-workflow)
    - [Router examples](#router-examples)
  - [Controller–Worker Workflow](#controllerworker-workflow)
    - [Controller–Worker examples](#controllerworker-examples)
- [Architectural Patterns for Agents and Multi-Agent Systems](#architectural-patterns-for-agents-and-multi-agent-systems)
  - [Agent Reasoning and Execution Patterns](#agent-reasoning-and-execution-patterns)
    - [Chain-of-Thought and Tree-of-Thoughts](#chain-of-thought-and-tree-of-thoughts)
    - [ReAct](#react)
    - [Plan-and-Execute](#plan-and-execute)
    - [ReWOO](#rewoo)
    - [LLMCompiler](#llmcompiler)
  - [Multi-Agent Systems](#multi-agent-systems)
    - [When One Agent Is Not Enough](#when-one-agent-is-not-enough)
    - [Hierarchical or Supervisor Architecture](#hierarchical-or-supervisor-architecture)
    - [Network Multi-Agent Architecture](#network-multi-agent-architecture)
- [LangChain vs LangGraph](#langchain-vs-langgraph)
  - [LangChain](#langchain)
  - [LangGraph](#langgraph)
- [Why Move from Chains to Graphs?](#why-move-from-chains-to-graphs)
- [LangGraph Core Components](#langgraph-core-components)
  - [1. State](#1-state)
  - [TypedDict vs Pydantic](#typeddict-vs-pydantic)
    - [`TypedDict`](#typeddict)
    - [Pydantic](#pydantic)
  - [Redis is different](#redis-is-different)
- [Nodes](#nodes)
- [Edges](#edges)
  - [Normal edge](#normal-edge)
  - [Conditional edge](#conditional-edge)
- [Entry and End](#entry-and-end)
- [State Updates](#state-updates)
- [Graph State vs LLM/Tool Schema Validation](#graph-state-vs-llmtool-schema-validation)
  - [Graph State Schema](#graph-state-schema)
  - [LLM Structured Output Schema](#llm-structured-output-schema)
  - [Tool Input Schema](#tool-input-schema)
- [Typed MCP Tools](#typed-mcp-tools)
- [Reference Agentic System Architecture](#reference-agentic-system-architecture)
  - [Core principle](#core-principle)

---

## Agentic Workflows vs AI Agents

### Agentic Workflow

A workflow follows a **controlled graph of predefined steps and branches**.

The LLM may decide **which allowed path to take**, but the possible paths already exist.

```text
Input
  ↓
LLM Router
 ├─ Knowledge Search
 ├─ Data Analysis
 └─ External Action
```

Characteristics:

* predictable
* auditable
* constrained
* easier to test
* well suited to regulated processes, customer support, and operational automation

### AI Agent

An agent has more freedom to determine **what to do next**, often repeatedly selecting and combining tools based on intermediate results.

```text
Goal
 ↓
LLM
 ↓
choose tool
 ↓
observe result
 ↓
decide next action
 ↺
```

The path is determined dynamically rather than being fully encoded beforehand.

#### Practical distinction

> **Workflow:** LLM chooses among predefined paths.
> **Agent:** LLM dynamically constructs the next sequence of actions.

The appropriate level of autonomy depends on the task and its risk. For example:

* a financial assistant should normally use a **controlled agentic workflow** for payments, investments, and account changes,
* an IT support assistant may have more freedom to investigate logs and documentation, while production changes remain constrained by approval steps,
* an ambient DevOps, MLOps, or Kubernetes agent may continuously investigate alerts, logs, metrics, deployment state, and model drift.

The ***ambient agent*** can autonomously diagnose problems and propose remediation. Production-changing actions, such as restarting workloads, modifying configuration, rolling back deployments, changing access controls, or promoting models, should pass through policy validation and **human-in-the-loop (HITL)** approval.

This illustrates **action-dependent autonomy**: the same agent can operate autonomously while observing, remain constrained while planning, and require explicit human approval before high-impact execution. An ambient agent describes a continuously running or event-driven operating model; it does not imply unrestricted autonomy.

Continuous oversight, where an operator can inspect or interrupt background work, is often described as **human-on-the-loop**. A mandatory approval gate before a sensitive action is **human-in-the-loop**.

[Back to contents](#contents)

---

## Common Agentic Workflow Patterns

### Router Workflow

An LLM classifies the request and chooses **one predefined branch**.

```text
               Router
          ┌──────┼───────┐
          ▼      ▼       ▼
      Search  Analysis  Action
```

Best for requests that naturally belong to one domain.

Examples:

* Financial assistant: “Show my last five ride-share payments.”

```text
Router → TransactionSearchWorker
```

* IT support assistant: “Check whether the email service is currently degraded.”

```text
Router → ServiceStatusWorker
```

#### Router examples

A router is often the main top-level pattern when requests fall into clear domains. A financial assistant might route between transaction search, spending analysis, and account actions. An IT support assistant might route between documentation search, incident diagnosis, and service operations.

---

### Controller–Worker Workflow

A controller decomposes a more complex task and coordinates several predefined workers.

```text
             Controller
        ┌──────┼──────┐
        ▼      ▼      ▼
     Worker A Worker B Worker C
        └──────┼──────┘
               ▼
           Synthesis
```

Workers may run:

* sequentially,
* conditionally,
* or in parallel.

The controller does **not necessarily choose tools directly**. Workers may themselves call typed tools through MCP.

#### Controller–Worker examples

Use Controller–Worker only when a request requires **multiple analyses or domains**.

Financial assistant example:

> “Analyze my spending and suggest suitable investment options.”

```text
Router
  ↓
Composite
  ↓
Controller
 ├─ AnalyticsWorker
 └─ InvestmentWorker
  ↓
Cross-domain synthesis
```

IT support assistant example:

> “Investigate the recurring checkout failures and prepare an incident summary.”

```text
Router
  ↓
Composite
  ↓
Controller
 ├─ LogAnalysisWorker
 └─ KnowledgeBaseWorker
  ↓
Incident synthesis
```

So:

> **Simple request → Router → one worker**
> **Composite request → Router → Controller → multiple predefined workers**

[Back to contents](#contents)

---

## Architectural Patterns for Agents and Multi-Agent Systems

### Agent Reasoning and Execution Patterns

#### Chain-of-Thought and Tree-of-Thoughts

**Chain-of-Thought (CoT)** is a prompting approach that encourages an LLM to reason through intermediate steps before producing an answer. It is most useful for requests that require complex logic, planning, or mathematical operations.

CoT can be elicited by:

* including examples that demonstrate a reasoning process,
* or adding an instruction that encourages step-by-step reasoning, known as **Zero-Shot CoT**.

**Tree-of-Thoughts (ToT)** extends this idea by exploring and evaluating multiple reasoning paths instead of following only one linear path.

Tool use is either unavailable or very limited in a basic CoT or ToT prompt because these are primarily reasoning and prompting techniques rather than complete agent architectures.

**Advantages:**

* simple to apply through prompting,
* can improve performance on logical and mathematical tasks,
* can reduce some reasoning errors and hallucinations,
* provides a more understandable path to the result.

**Disadvantages:**

* does not support rich interaction with external tools,
* does not eliminate hallucinations,
* has limited flexibility when the environment changes during execution,
* may increase token usage when reasoning traces are long or multiple paths are explored.

**When to use it:**

* the task requires no external tools, or at most one simple tool call,
* the task primarily involves logical or mathematical reasoning,
* a lightweight prompting approach is sufficient.

#### ReAct

**ReAct** is an agent architecture that interleaves reasoning with actions:

```text
Thought → Action → Observation → Thought → ... → Answer
```

After each action, the agent observes the result and updates its understanding of the current state before deciding what to do next. This makes ReAct effective for interacting with external tools and adapting to intermediate results.

Tool calls are generally made sequentially as the reasoning progresses.

**Advantages:**

* supports full interaction with external tools,
* maintains good answer quality through continuous state evaluation,
* can use a less capable model because it only needs to plan the next step at each iteration,
* adapts naturally when a tool returns unexpected information.

**Disadvantages:**

* repeated LLM calls lead to high token consumption and latency,
* sequential execution limits opportunities for parallelism,
* using different specialized models for different stages can be difficult,
* long action loops require explicit limits and failure handling.

**When to use it:**

* sequential execution is natural to the task,
* later actions depend heavily on earlier observations,
* examples include web research, troubleshooting, and interactive user workflows.

#### Plan-and-Execute

**Plan-and-Execute** separates planning from execution. A planner first identifies the steps expected to achieve the goal, and an executor then performs those steps. If execution does not achieve the goal, the system can generate a revised plan.

```text
Goal → Plan → Execute steps → Evaluate → Replan if needed
```

Steps are often executed sequentially, although independent steps can be parallelized when the orchestration layer supports it.

**Advantages:**

* supports full interaction with external tools,
* can reduce token consumption and latency compared with repeated ReAct loops,
* allows less expensive or specialized models to execute individual tasks,
* provides a clear plan for tasks with a long execution horizon.

**Disadvantages:**

* performs poorly when the initial plan is incomplete or inefficient,
* requires a capable planning model,
* may waste work when early assumptions become invalid,
* replanning adds complexity and additional model calls.

**When to use it:**

* the task has a long planning horizon,
* the required steps can be identified before execution begins,
* execution benefits from separating a capable planner from cheaper workers.

#### ReWOO

**ReWOO**, or **Reasoning Without Observation**, separates planning, tool execution, and result synthesis. The planner creates the expected steps and their dependencies before tools are called. Workers then execute the planned commands, often with full or partial parallelism, without repeatedly returning each observation to the planner.

```text
Plan → Execute tools → Aggregate evidence → Final answer
```

**Advantages:**

* supports full interaction with external tools,
* reduces LLM calls because the planner does not observe every intermediate result,
* can reduce latency through parallel execution,
* allows less expensive models or deterministic workers to execute tasks.

**Disadvantages:**

* depends heavily on the quality and completeness of the initial plan,
* adapts less naturally than ReAct when tools return unexpected results,
* requires explicit dependency and result-reference handling,
* may still require replanning when execution fails.

**When to use it:**

* several task steps can run independently or in parallel,
* the task is predictable enough to plan before observing tool results,
* examples include content-generation pipelines and multi-source data collection.

#### LLMCompiler

**LLMCompiler** is a more advanced planning and execution architecture related to ReWOO. It represents tasks as a **directed acyclic graph (DAG)** and schedules each task as soon as its prerequisites are complete.

```text
Plan as DAG → Schedule ready tasks → Execute → Join results → Final answer
```

A separate aggregation stage combines the tool results before the response is returned to the user.

**Advantages:**

* supports full interaction with external tools,
* maximizes parallelism while respecting dependencies,
* can reduce latency and repeated LLM calls,
* allows task execution to use cheaper models or deterministic tools.

**Disadvantages:**

* requires a high-quality planner that can construct valid task dependencies,
* inefficient plans lead to unnecessary work or blocked execution,
* scheduling, dependency resolution, and error recovery increase implementation complexity,
* dynamic replanning is required when assumptions or dependencies change.

**When to use it:**

* the task contains many dependent and independent steps,
* substantial portions of the work can execute in parallel,
* latency reduction justifies more complex orchestration.

### Multi-Agent Systems

#### When One Agent Is Not Enough

A multi-agent system becomes useful when one general-purpose agent cannot handle the workflow reliably or efficiently. Common reasons include:

* a complex process uses many tools, making tool selection less reliable as the tool set grows,
* the domain requires specialized models, prompts, permissions, or context,
* different tasks benefit from different agent architectures,
* the system needs graceful degradation when one capability is unavailable,
* new functionality should be added without continually expanding one agent,
* independent tasks can run in parallel.

Multi-agent architecture adds coordination, observability, and state-management costs, so it should address a concrete limitation rather than being the default for every application.

#### Hierarchical or Supervisor Architecture

A dedicated supervisor agent coordinates the other agents.

```text
              Supervisor
          ┌──────┼──────┐
          ▼      ▼      ▼
       Agent A Agent B Agent C
          └──────┼──────┘
                 ▼
             Synthesis
```

Characteristics:

* the supervisor routes tasks, manages dependencies, and combines results,
* the supervisor usually owns the complete context,
* worker agents receive only the context required for their assigned tasks,
* centralized coordination makes execution easier to control and audit,
* it works well for medium and large systems but can be excessive for small applications,
* the supervisor can become a bottleneck or single point of failure.

#### Network Multi-Agent Architecture

Agents operate as peers and dynamically decide whether another agent is needed.

```text
Agent A ↔ Agent B
   ↕         ↕
Agent C ↔ Agent D
```

Characteristics:

* agents are peers rather than being controlled by one permanent supervisor,
* a user may interact with any suitable agent,
* agents can transfer work directly to other agents,
* context is often shared across agents, although scoped context is safer for sensitive data,
* the topology can work well for small systems with clear handoff rules,
* larger systems face agent-discovery, routing, shared-state, and debugging complexity.

[Back to contents](#contents)

---

## LangChain vs LangGraph

### LangChain

Provides reusable AI building blocks:

* LLM interfaces
* prompt templates
* tools
* retrievers
* embeddings
* structured outputs
* MCP adapters

Simple applications may use a linear chain:

```python
prompt | llm | parser
```

This works well when execution is essentially:

```text
A → B → C
```

---

### LangGraph

LangGraph organizes those components into a **stateful graph**.

It becomes useful when you need:

* conditional branches
* multiple execution paths
* parallel work
* cycles/retries
* human approval
* persistent state
* long multi-step workflows

Think of it as:

> **LangChain = components**
> **LangGraph = orchestration and runtime structure connecting them**

[Back to contents](#contents)

---

## Why Move from Chains to Graphs?

A linear chain becomes awkward when the application needs:

```text
        ┌→ B
A → decision
        └→ C
```

or:

```text
       ┌→ B ─┐
A ─────┤     ├→ D
       └→ C ─┘
```

or:

```text
A → B → evaluate
    ↑       │
    └───────┘
```

LangGraph explicitly models these cases. A domain-neutral routing graph might look like this:

```text
request
  ↓
router
 ├─ knowledge search
 ├─ data analysis
 ├─ recommendations
 └─ external actions
```

For example, a financial assistant can map these branches to transaction search, spending analysis, investment information, and account actions. An IT support assistant can map the same structure to documentation search, log analysis, remediation advice, and service operations.

Sensitive actions can pause for approval in either domain, such as submitting a payment or restarting a production service:

```text
propose
  ↓
interrupt
  ↓
user confirmation
  ↓
resume
```

[Back to contents](#contents)

---

## LangGraph Core Components

### 1. State

The **shared evolving runtime context** of the graph.

Example:

```python
class AssistantState(TypedDict):
    messages: list
    route: str | None
    tool_results: list
    pending_action: dict | None
    final_answer: str | None
```

Each node reads from this state and returns updates.

```text
Node A
 ↓
State
 ↓
Node B
 ↓
State
 ↓
Node C
```

State is **not merely input/output validation**. It is the central data/context passed through the workflow.

---

### TypedDict vs Pydantic

#### `TypedDict`

Useful for:

* state structure
* static type checking
* lightweight graph schemas

#### Pydantic

Adds:

* runtime validation
* coercion/parsing
* constraints
* structured error handling

Either can define LangGraph state depending on requirements.

---

### Redis is different

Redis does not replace the state schema.

```text
TypedDict / Pydantic
        ↓
defines what State looks like

LangGraph State
        ↓
current runtime context

Redis Checkpointer
        ↓
persists/restores that state
```

This distinction applies to any domain:

> **TypedDict/Pydantic = state definition**
> **Redis = short-term persistence/checkpoint storage**

Redis enables:

* multi-turn conversations
* session restoration
* interrupt/resume
* cross-process persistence

For example, it can restore a paused financial-assistant approval flow or a paused IT-support troubleshooting session.

[Back to contents](#contents)

---

## Nodes

A node is a processing step, usually a Python function.

```python
def route_request(state):
    ...
    return {"route": route}
```

Nodes may contain:

* deterministic Python
* LLM calls
* MCP/tool calls
* API calls
* validation
* synthesis
* authorization logic

A node does **not automatically mean an LLM call**.

Example:

```text
authentication node     → deterministic
router node             → LLM
MCP execution node      → deterministic
answer synthesis node   → LLM
```

[Back to contents](#contents)

---

## Edges

Edges define valid transitions.

### Normal edge

```text
A → B
```

### Conditional edge

The next node depends on state:

```text
             ┌→ KnowledgeSearchWorker
Router ──────┼→ DataAnalysisWorker
             └→ ExternalActionWorker
```

Conceptually:

```python
graph.add_conditional_edges(
    "router",
    choose_route,
)
```

Conditional edges are what make workflows dynamic while still controlled.

[Back to contents](#contents)

---

## Entry and End

Every graph has a defined start and termination.

Conceptually:

```text
START
  ↓
prepare
  ↓
...
  ↓
final_response
  ↓
END
```

This makes the execution lifecycle explicit and testable.

[Back to contents](#contents)

---

## State Updates

Nodes normally return only the state fields they changed.

```python
def research_worker(state):
    result = search_sources(...)
    return {
        "tool_results": [result]
    }
```

LangGraph merges these updates into the graph state.

So you generally do not manually pass every parameter from function to function as with traditional application code.

[Back to contents](#contents)

---

## Graph State vs LLM/Tool Schema Validation

These are related but different concepts.

### Graph State Schema

Defines workflow context:

```python
class AssistantState(TypedDict):
    route: str
    tool_results: list
    final_answer: str
```

### LLM Structured Output Schema

Defines what an LLM must return:

```python
class RouteDecision(BaseModel):
    route: Literal[
        "knowledge_search",
        "data_analysis",
        "external_action"
    ]
```

### Tool Input Schema

Defines arguments accepted by a tool:

The schema is specific to the selected tool. For example:

```python
class SpendingQuery(BaseModel):  # Financial assistant
    start_date: date
    end_date: date
    category: str | None


class IncidentQuery(BaseModel):  # IT support assistant
    service: str
    start_time: datetime
    severity: str | None
```

The flow becomes:

```text
LLM
 ↓
structured JSON/tool call
 ↓
Pydantic / JSON Schema validation
 ↓
validated arguments
 ↓
MCP tool
 ↓
typed result
```

So Pydantic can appear in several places, but for **different purposes**.

[Back to contents](#contents)

---

## Typed MCP Tools

A typed MCP tool has an explicit contract.

Instead of exposing a low-level operation such as:

```text
execute_sql("...")
```

expose domain-level tools with explicit contracts. For example:

```python
# Financial assistant
get_spending_summary(
    start_date: date,
    end_date: date,
    category: str | None
)

# IT support assistant
search_incidents(
    service: str,
    start_time: datetime,
    severity: str | None
)
```

The LLM produces structured arguments appropriate to the selected tool:

```json
{
  "start_date": "2026-07-01",
  "end_date": "2026-07-31",
  "category": "Restaurants"
}
```

or:

```json
{
  "service": "checkout-api",
  "start_time": "2026-07-30T08:00:00Z",
  "severity": "critical"
}
```

Then:

```text
LLM tool call
 → JSON Schema / Pydantic validation
 → validated Python arguments
 → FastMCP tool
 → domain service
 → database or external API
 → typed result
```

The LLM therefore **does not write Python or SQL**.

[Back to contents](#contents)

---

## Reference Agentic System Architecture

A general controlled agentic architecture can be summarized as:

```text
User
 ↓
Identity + Checkpoint State
 ↓
Input Guard
 ↓
LangGraph LLM Router
 │
 ├─ KnowledgeSearchWorker
 ├─ DataAnalysisWorker
 ├─ RecommendationWorker
 ├─ ExternalActionWorker
 └─ Composite
        ↓
     Controller
       ├─ Worker A
       └─ Worker B
        ↓
     Synthesis
 ↓
 Typed MCP tools / domain APIs
 ↓
Grounded Answer Synthesis
 ↓
Output Guard
 ↓
User
```

The architecture is domain-independent. Worker names and tool contracts change with the application:

* **Financial assistant:** transaction search, spending analysis, investment information, and approved account actions.
* **IT support assistant:** documentation search, log analysis, remediation recommendations, and approved service operations.

### Core principle

> **Use deterministic graph structure wherever possible, and use the LLM only where semantic understanding, routing, tool selection, or natural-language synthesis actually requires it.**

[Back to contents](#contents)
