# Parallelization with LCEL

> **LangChain Expression Language (LCEL)** organizes LLM components—such as *web search*, *scraping*, and *summarization*—into efficient, composable pipelines.

## Why LCEL?

- Uses a unified **Runnable protocol** to compose simple components into complex workflows.
- Improves <u>performance and scalability</u> through **parallel execution**.
- Supports multiple execution modes: *synchronous*, *streaming*, *batch*, and *asynchronous*.
- Provides **fallbacks** for error handling.
- Enables **LangSmith tracing** for automatic logging, debugging, and monitoring.
- Standardizes methods such as `invoke()`, `stream()`, and `batch()`, including asynchronous variants.

> LCEL may take practice to master, but its flexibility and performance benefits make it highly valuable for LLM applications.

## Web Research Chain

The solution builds a **mini-chain** for each processing step and combines them into one master **Web Research chain**:

- **Assistant Instructions chain**
  - Selects the most suitable research assistant.
  - Creates the system prompt defining its *purpose and skills*.
- **Web Searches chain**
  - Generates multiple searches from the user’s question.
  - Adds different perspectives or divides complex questions into simpler queries.
- **Search and Summarization chain**
  - Searches the web, extracts result URLs, scrapes pages, and summarizes each source.
- **Research Report chain**
  - Synthesizes the original question and collected summaries into the final answer.

## Search and Summarization Subchains

- **Search Results URL chain** — retrieves URLs from search results.
- **Search Results Text and Summary chain** — scrapes and summarizes each page.
- **Joined Summaries chain** — merges individual summaries into one text block.

## Parallelization Strategy

LCEL applies parallel execution at <u>two key levels</u>:

1. **Across searches:** a separate **Search and Summarization chain** runs simultaneously for every generated web query.
2. **Across search results:** a separate **Text and Summary chain** runs simultaneously for every result URL.

> **Key outcome:** independent searches and page summaries run concurrently, making the research engine significantly faster than a sequential workflow.
