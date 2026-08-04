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

## Observed local result

Running `python main.py` with the built-in İçərişəhər question completed successfully on the local `gemma4:12b-it-q8_0` model. The workflow generated three bilingual search queries, collected nine results, summarized six usable pages, and rated the evidence as 60% relevant. It therefore accepted the results after the first evaluation and produced a structured Azerbaijani Markdown report with an APA-style list of four cited sources. Fallback search was used for two queries, while inaccessible, insufficient, or invalid pages were skipped without stopping the workflow.

Shortened real console output from that run:

```text
İlkin axtarış sorğuları yaradılır...
3 axtarış sorğusu yaradıldı
  Sorğu 1: İçərişəhər tarixi və qədim dövrlərdəki əhəmiyyəti
  Sorğu 2: History of Icherisheher Old City Baku architecture and cultural heritage
  Sorğu 3: İçərişəhər qədim şəhərinin tarixi abidələri və mədəni xüsusiyyətləri

3 sorğu üzrə veb axtarışları aparılır...
Axtarılır: İçərişəhər tarixi və qədim dövrlərdəki əhəmiyyəti
Sorğu üçün ehtiyat axtarışdan istifadə edildi: İçərişəhər tarixi və qədim dövrlərdəki əhəmiyyəti
Sorğu üçün 3 nəticə tapıldı: İçərişəhər tarixi və qədim dövrlərdəki əhəmiyyəti
...
9 axtarış nəticəsi xülasə edilir...
Məzmun uğurla xülasə edildi: https://icherisheher.gov.az/
Məzmunu əldə etmək mümkün olmadığı və ya yetərsiz olduğu üçün https://en.wikipedia.org/wiki/Old_City_(Baku) ötürülür
...
6 mənbə əsasında tədqiqat xülasəsi yaradıldı
Axtarış nəticələrinin 60%-i uyğundur. Tədqiqat hesabatının yazılmasına keçilir...
İterasiya 1: Axtarış nəticələri uyğundur. Hesabatın yazılmasına keçilir.

# İçərişəhər: Tarixi, Memarlıq Mirası və Müasir İdarəetmə Strategiyaları Haqqında Analitik Hesabat

## Giriş
Azərbaycanın paytaxtı Bakının qədim mərkəzi olan "İçərişəhər", yalnız bir şəhər hissəsi deyil,
həm də Azərbaycanın çoxşaxəli tarixinin, memarlıq sənətinin və mədəniyyətinin canlı şahididir.
...
## Tarixi İnkişaf və Dövrələr
İçərişəhərin tarixi çox qədim dövrlərə dayanır və onun inkişafı Azərbaycanın siyasi-sosial tarixinə paralel şəkildə baş vermişdir.
...
## Memarlıq Mirası və Simvolik Abidələr
İçərişəhər özünəməxsus memarlıq üslubları ilə seçilən bir çox abidələrin cəmidir:
...
## Beynəlxalq Tanınma və UNESCO Statusu
İçərişəhərin dünya mirası daxilindəki yeri 2000-ci ildə rəsmi olaraq təsdiqlənmişdir. O, UNESCO Dünya İrsi Siyahısına daxil edilmişdir. Bu tanınma İçərişəhərin yalnız Azərbaycan üçün deyil, bütöv insanlıq üçün də böyük bir mədəni dəyər olduğunu göstərir.
...
## Müasir İdarəetmə və Qorunma Strategiyaları
İçərişəhərin qorunması müasir dövrdə sistemli və elmi yanaşma ilə həyata keçirilir.
...
## Nəticə
İçərişəhər Azərbaycanın tarixinin "canlı kitabı"dır. Tunc dövründən keçib Şirvanşahlar dövrünün paytaxtına, sonra Rusi imperiyasının sənaye mərkəzinə və nəhayət UNESCO Dünya İrsi obyektinə çevrilən bu qala-şəhər, Azərbaycanın mədəniyyətinin davamlılığını simvolizə edir. Müasir dövrdə tətbiq edilən rəqəmsal xəritələmə, beynəlxalq ekspertlərlə aparılan restavrasiya işləri və sistemli idarəetmə mexanizmləri bu unikal irsin gələcək nəsillərə çatdırılması üçün zəruri addımlardır.
---
### Mənbələr (APA Üslubunda)
* İçərişəhər Dövlət Tarix-Memarlıq Qoruğu İdarəsi. (n.d.). Rəsmi Veb-sayt.
  https://icherisheher.gov.az/
```

> **Terminology clarification:** The complete model output used **“Rusi imperiyası.”** The standard Azerbaijani historical name is **“Rusiya imperiyası,”** as used by the [A.A. Bakikhanov Institute of History and Ethnology](https://www.tarixinstitutu.az/maps/64) and the [Presidential Library](https://www.preslib.az/az/book/BD82FEIOZxnaHVf). The captured output is retained as real generation evidence; its terminology and historical claims should still be reviewed.

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
