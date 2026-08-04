# Azerbaijani Agentic Research with LangGraph

This application accepts an Azerbaijani research question, searches the web, evaluates the collected information, and produces a structured Azerbaijani report. It runs locally with Ollama using `gemma4:12b-it-q8_0`.

## Application flow

```text
Question
   ↓
Select a specialized assistant
   ↓
Generate three search queries
   ↓
Search → scrape pages → summarize sources
   ↓
Evaluate relevance
   ├─ Below 50% → generate new queries (up to three iterations)
   └─ At least 50% or final iteration → write the report
```

DuckDuckGo provides the normal search results. If it is unavailable or rate-limited, the workflow uses fallback sources, including Azerbaijani Wikipedia.

## Architecture

- `main.py` — builds the LangGraph state machine, handles conditional routing, and runs the workflow.
- `models.py` — configures `ChatOllama` and defines the shared `ResearchState` types.
- `prompts.py` — contains the Azerbaijani prompts for assistant selection, searching, summarization, and report writing.
- `agents/assistant_selector.py` — selects a research-specialist role for the question.
- `agents/web_researcher.py` — generates queries, searches, summarizes sources, and evaluates relevance.
- `agents/report_writer.py` — produces the final Azerbaijani Markdown report.
- `utils/` — contains DuckDuckGo search/fallback logic and webpage scraping.

## Run the application

Prerequisites:

- An activated Python virtual environment with the repository requirements installed
- The Ollama Windows application running
- `gemma4:12b-it-q8_0` downloaded locally
- Internet access for search and webpage retrieval

From the repository root:

```powershell
ollama pull gemma4:12b-it-q8_0
cd "02-summarization\agentic_workflows_with_langgraph"
python main.py
```

The built-in example researches the history of İçərişəhər. To submit another question without editing the source code:

```powershell
python -c "from main import run_research; print(run_research('Şuşanın tarixi və mədəni əhəmiyyəti nədir?'))"
```

Install dependencies from the repository root using:

```powershell
python -m pip install -r requirements.txt
```

To release the model's VRAM after the run:

```powershell
ollama stop gemma4:12b-it-q8_0
```
