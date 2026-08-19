# Common Issues in Naive RAG Architecture and Recommended Solutions

| Issue | Recommended solution |
|---|---|
| Retrieval returning the wrong content chunks | [Advanced document indexing techniques](#advanced-document-indexing-techniques) |
| Poor question formulation | [Question transformations](#question-transformations) |
| Ineffective question for retrieval | [Question transformations](#question-transformations) |
| Limited querying capabilities for structured data | [Content store query generation](#content-store-query-generation) |
| Limited data relevance in the content store | Routing to multiple content stores |
| Irrelevant retrieved results fed to the LLM | Retrieval postprocessing |


## Table of Contents
* [Advanced document indexing techniques](#advanced-document-indexing-techniques)
  * [`ParentDocumentRetriever` — simple concept](#parentdocumentretriever--simple-concept)
  * [`MultiVectorRetriever`](#multivectorretriever)
    * [Key concept of `MultiVectorRetriever`](#key-concept-of-multivectorretriever)
    * [Main difference from `ParentDocumentRetriever`](#main-difference-from-parentdocumentretriever)
  * [Embedding document summaries `MultiVectorRetriever`](#embedding-document-summaries-multivectorretriever)
  * [Why these techniques are called **multi-vector embedding approach**?](#why-these-techniques-are-called-multi-vector-embedding-approach)
  * [Hypothetical-question embeddings — simple concept](#hypothetical-question-embeddings--simple-concept)
  * [Can we combine all these techniques in our RAG solution (and is this good) or not?](#can-we-combine-all-these-techniques-in-our-rag-solution-and-is-this-good-or-not)
  * [Granular chunk expansion — simple concept](#granular-chunk-expansion--simple-concept)
  * [Semi-structured RAG](#semi-structured-rag)
  * [Multimodal RAG](#multimodal-rag)
  * [Advanced Document Indexing for RAG — Summary](#advanced-document-indexing-for-rag--summary)
* [Question transformations](#question-transformations)  
  * [Rewrite–Retrieve–Read — simple concept](#rewriteretrieveread--simple-concept)
  * [Multi-query retrieval — simple concept](#multi-query-retrieval--simple-concept)
  * [Step-back question — simple concept](#step-back-question--simple-concept)
  * [HyDE — simple concept](#hyde--simple-concept)
  * [Single-step vs multi-step decomposition — simple concept](#single-step-vs-multi-step-decomposition--simple-concept)
  * [Question Transformations — summary](#question-transformations--summary)
* [Content store query generation](#content-store-query-generation)  
  * [LangChain: **`SelfQueryRetriever`** - Simple concept](#langchain-selfqueryretriever---simple-concept)
  * [Self-querying / metadata query enrichment — simple concept](#self-querying--metadata-query-enrichment--simple-concept)
  * [Natural language → SQL — simple concept](#natural-language--sql--simple-concept)
  * [Semantic SQL search — simple concept](#semantic-sql-search--simple-concept)
  * [Graph database / KG-RAG / GraphRAG — simple concept](#graph-database--kg-rag--graphrag--simple-concept)

# Advanced document indexing techniques

## `ParentDocumentRetriever` — simple concept

* Split each document into **large parent chunks**.
* Split each parent into **small child chunks**.
* Store:

  * **parent chunks** in a normal document/key-value store
  * **child chunks + embeddings** in the vector database
* A query does **semantic search only over the child chunks**.
* When a child matches, it carries a **parent ID**.
* The retriever uses that ID to fetch the **corresponding parent chunk**.
* The **parent chunk is returned to the LLM**, giving more surrounding context for synthesis.

In one line:

> Search small chunks for precision → return their larger parent chunks for context.**

## `MultiVectorRetriever`

### Key concept of `MultiVectorRetriever`

**Search using multiple small/vector representations → return the larger parent document.**

Mechanics:

> query → semantic search over child chunks → matching child → read doc_id → fetch parent chunk → return parent to LLM

So again:

- **small child chunks = retrieval units**
- **large parent chunks = synthesis/context units**

### Main difference from `ParentDocumentRetriever`

`ParentDocumentRetriever` is basically a **specialized convenience version** of this pattern.

With `ParentDocumentRetriever`:

* you give it `parent_splitter` and `child_splitter`
* `add_documents()` automatically:

  * creates parents
  * creates children
  * assigns parent IDs
  * stores children in vector store
  * stores parents in document store

With `MultiVectorRetriever`, **you manage those steps yourself** in the code:

* create parents
* create children
* generate IDs
* attach `doc_id`
* store children
* store parents

The advantage is that `MultiVectorRetriever` is **more general**. The vectors representing one parent do not have to be only child chunks. Later you could have:

`Parent document`
→ child-chunk embeddings
→ LLM-generated summary embedding
→ hypothetical questions / generated-question embeddings
→ other representations

> and **any of those vectors can lead back to the same parent document**.

So the easiest way to remember it is:

**`ParentDocumentRetriever` = convenient parent/child retriever.**
**`MultiVectorRetriever` = more general framework where many vector representations can point to the same parent.**

## Embedding document summaries `MultiVectorRetriever`

In [**this specific implementation**](advanced_indexing.ipynb), the idea is even simpler:

**Search using summary embeddings → return the original large/coarse chunk.**

- There are **no child chunks at all** in this version.

Mechanically:

> `coarse chunk → LLM creates summary → summary is embedded → vector store`

while:

> `coarse chunk → document store`

At query time:

> `query → similarity search over SUMMARY embeddings only → matched summary → doc_id → fetch original coarse chunk → return coarse chunk to LLM`

So for the code in the notebook:

* **Coarse/original chunk:** stored in `docstore`, **not embedded**
* **Summary:** stored + embedded in the vector store
* **Child chunks:** **not created or used**
* **Similarity search:** searches **only summary embeddings**
* **Final retrieved document:** the **original coarse chunk**

Summary embeddings could be stored “alongside the original chunk embeddings,” but **the notenook's code only embeds the summaries**.

So compare the two strategies:

**Previous strategy:**
> `query → child embeddings → parent/coarse chunk`

**Summary strategy:**
> `query → summary embeddings → parent/coarse chunk`

Same final goal, but a different representation is used for searching.

## Why these techniques are called **multi-vector embedding approach**?

Because **one parent document/chunk can be represented by multiple vectors** for retrieval.

For example, one parent chunk can be represented by vectors from:

* several **child chunks**, or
* its **summary**, generated questions, etc.

All those vectors point back to the **same parent chunk**.

> So: **multiple vectors for one document → MultiVector retrieval.**

## Hypothetical-question embeddings — simple concept

* Split content into **large/coarse chunks**.
* For each chunk, use an LLM to generate several **questions that this chunk could answer**.
* Embed and store those **hypothetical questions** in the vector store.
* Store the original **coarse chunk** in the document store.
* At query time, compare the user’s question against the **hypothetical-question embeddings**.
* When one matches, use its `doc_id` to fetch and return the **original coarse chunk** to the LLM. 

In one line:

**Search question-like embeddings → return the full source chunk.**

> Why it helps: a user query is often more semantically similar to another **question** than to the wording of the answer/document itself.


## Can we combine all these techniques in our RAG solution (and is this good) or not?

Yes, you **can combine them** in one RAG system.

For the same parent chunk, you could store vectors from:

* child chunks
* summaries
* hypothetical questions
* optionally the parent itself

Then any matching vector points back to the same parent chunk.

This can improve recall and robustness, but **more is not always better**: it increases storage, ingestion cost, latency, and can add noisy matches. Usually, test combinations and keep only the ones that measurably improve retrieval quality.


## Granular chunk expansion — simple concept

* Split the document into **small granular chunks**.
* For each chunk, create an **expanded version** containing:
  **previous chunk + current chunk + next chunk**.
* Store:

  * **small granular chunks + embeddings** in the vector store
  * **expanded chunks** in the document store
* Query searches the **small chunk embeddings**.
* When a small chunk matches, use its `doc_id` to return the **expanded chunk** instead.
* Send that richer expanded context to the LLM.

**Key idea:**
**Search small chunks for precision → return the matched chunk plus its neighbors for more context.**


## Semi-structured RAG

For content containing **text + tables**:

* Store the **full text chunks / full tables** in the document store.
* Create **summaries** of them.
* Embed the summaries in the vector store.
* User query searches the **summary embeddings**.
* Matching summary → retrieve the **original full text/table**.
* Send **user query + retrieved original content + optionally its summary** to the LLM.

**Key idea:**
**Search compact summaries → answer using the full original content.**

## Multimodal RAG

Same pattern for **images** and **audio**:

* Image → generate a textual description/summary.
* Audio → generate a transcript and/or summary.
* Embed those text representations.
* Store the **original image/audio** separately.
* User query searches the summary/transcript embeddings.
* Matching representation → retrieve the **original image/audio**.
* Send **user query + original image/audio + optionally summary/transcript** to a multimodal LLM.

**Key idea:**
**Search using textual representations → return and reason over the original media.**

## Advanced Document Indexing for RAG — Summary

Advanced Document Indexing for RAG improves **what is searched** and **what is finally given to the LLM**.

* **Better chunking** → split content at meaningful semantic or structural boundaries.
* **SemanticChunker** → uses **embedding similarity** to detect natural breakpoints instead of fixed sizes; this requires extra embedding API calls during ingestion.
* **Parent-child retrieval** → search small child chunks → return larger parent chunks with more context.
* **Multi-vector retrieval** → one source can have several searchable vector representations.
* **Summary embeddings** → search summaries → return full chunks.
* **Hypothetical-question embeddings** → search question-like representations → return full chunks.
* **Context window retrieval / context expansion** → after a chunk matches, also fetch **N chunks before and after it**, usually using document ID and chunk-position metadata.
* **Metadata filtering** → narrow retrieval by date, type, category, source, etc. Support and syntax depend on the vector database; for example, ChromaDB provides filtering, but implementations vary across platforms.
* **Hybrid search** → combine keyword/sparse retrieval with vector/semantic retrieval.
* **Semi-structured RAG** → search summaries of text/tables → return the full originals.
* **Multimodal RAG** → search image descriptions or audio transcripts/summaries → return the original media.

### Important tradeoff

Parent-child retrieval stores **both parent and child chunks**, and combining several retrieval approaches can increase:

> **storage + ingestion cost + embedding/LLM calls + computation + latency + system complexity**

So:

> **Benchmark the quality improvement against storage and computational costs before deploying.**

### Core principle to remember

> **Use the representation that is best for retrieval, but give the LLM the richer original content for answering.**

Or even shorter:

**Optimize search for precision → retrieve rich context for synthesis.**

# Question transformations

## Rewrite–Retrieve–Read — simple concept

* User asks a question.
* An LLM **rewrites the question into a clearer search query**.
* The retriever uses the **rewritten query** to search the vector store.
* The original user question is still kept for the final answer generation. 

**Key idea:**
> **Rewrite for better retrieval → retrieve relevant context → answer the original question.**

### Example

User asks:

> “Tell me some fun things I can enjoy in Cornwall.”

LLM rewrites it as:

> “fun activities to do in Cornwall”

The vector store searches using the **rewritten query**, retrieves chunks about surfing, cycling, festivals, etc., and then the LLM answers the **original question** using those retrieved chunks. 

In one line:

> **Original question → optimized search query → retrieval → original question + retrieved context → final answer.**


## Multi-query retrieval — simple concept

* Start with **one user question**.
* An LLM generates **several alternative versions/sub-questions** of it.
* Run **each query separately** against the vector store.
* Combine/deduplicate the retrieved documents.
* Send the **original user question + combined retrieved context** to the LLM for the final answer.

LangChain provides **`MultiQueryRetriever`** for this.

**Key idea:**
> **One question → multiple search queries → broader retrieval → one final answer.**

### Example

Original question:

> “Is LA warmer than Miami in April?”

Possible generated queries:

* “What is the average April temperature in Los Angeles?”
* “What is the average April temperature in Miami?”
* “How do April temperatures in LA and Miami compare?”

Each query retrieves relevant chunks separately. Then the LLM combines those chunks and answers the **original comparison question**.

So compared with simple query rewriting:

* **Rewrite-Retrieve-Read** → usually **one improved query**
* **MultiQueryRetriever** → **multiple alternative queries** for the same original question


## Step-back question — simple concept

* Start with the **original detailed question**.
* Retrieve context for that detailed question.
* Ask an LLM to generate a **broader, more abstract version** of the question.
* Retrieve additional context using that broader question.
* Give the final LLM the **original question + detailed context + broader context**.

**Key idea:**
> **Retrieve both specific details and the bigger picture, then combine them for a fuller answer.**

### Example

Original question:

> “Can you give me some tips for a trip to Brighton?”

Step-back question:

> “What are some general tips for planning a successful trip to a coastal city?”

Then retrieve:

* **Detailed context** about Brighton specifically
* **Broader context** about coastal-trip planning

Finally:

> **original question + both contexts → final answer**

In one line:

> **Detailed query + broader step-back query → combine both retrieval results → better contextual answer.**


## HyDE — simple concept

* User asks a question.
* An LLM first generates a **hypothetical answer/document** that could answer it.
* Embed/search using that hypothetical document instead of the raw question.
* Retrieve the real document chunks whose embeddings are semantically closest.
* Send **original user question + retrieved real context** to the LLM for the final answer.

**Key idea:**
> **Transform the question into answer-like text → use that for retrieval → answer from real retrieved documents.**

Difference from **hypothetical-question embeddings**:

* **Hypothetical questions** → generated at **ingestion time** for each document chunk.
* **HyDE** → hypothetical document generated at **query time** for each user question.

**Simple HyDE example:**

User asks:

> “What are the best beaches in Cornwall?”

Instead of embedding that question directly, HyDE first asks an LLM to generate something like:

> “Some of the best beaches in Cornwall include Fistral Beach, Porthcurno Beach, and St Ives Bay.”

Then:

1. Embed this hypothetical answer.
2. Search the vector store with that embedding.
3. Retrieve real chunks about Cornwall beaches.
4. Give the LLM:
   **original question + real retrieved chunks**
5. Generate the final grounded answer.

Why it helps: **answer-like text is often closer in embedding space to real document text than the original question is.**


## Single-step vs multi-step decomposition — simple concept

**Single-step decomposition**

* Break one complex question into several **independent subquestions**.
* Each can be retrieved **separately or in parallel**.
* Combine all retrieved information for the final answer.

Example:

> “Compare PostgreSQL and MongoDB for time-series data.”

Becomes:

* “How does PostgreSQL handle time-series data?”
* “How does MongoDB handle time-series data?”

Both can be answered independently.

**Multi-step decomposition**

* Break a question into **dependent subquestions**.
* The answer from step 1 becomes an input to step 2, and so on.
* Execute them **sequentially**, then synthesize the final answer.

Example:

> “What is the average August temperature at the most popular sandy beach in Cornwall?”

1. “What is the most popular sandy beach in Cornwall?”
   → **Fistral Beach**
2. “What are the August temperatures at **Fistral Beach**?”
   → temperature data
3. “What is the average of **those temperatures**?”
   → final value

**Key idea:**

> **Independent subquestions → parallel retrieval.**  
> **Dependent subquestions → sequential retrieval where each answer feeds the next step.**

> While LangChain doesn’t offer a dedicated class for multi-step question decomposition, you may find inspiration in **LlamaIndex**’s `MultiStepQueryEngine` class. Explore this class for further ideas.

---

## Question Transformations — summary

These techniques improve RAG by **transforming the user's question before or during retrieval**, rather than only changing document indexing.

* **Rewrite–Retrieve–Read** → rewrite a vague/poor query into **one clearer search query**; keep the original question for final synthesis.
* **Multi-query retrieval** → generate **multiple alternative queries**, retrieve for each, then merge the results for broader coverage using Reciprocal Rank Fusion (RRF). This captures diverse phrasings of the same intent.
* **RRF (Reciprocal Rank Fusion)** → combine several ranked retrieval lists; documents ranking highly across multiple queries receive higher overall scores.
* **Reciprocal Rank Fusion (RRF)** scores documents by summing 1 / (rank + k) across all query result lists, with k typically set to 60. Documents appearing in multiple lists score higher.
* **Step-back prompting** → create a **broader question** and retrieve both broad + specific context.
* **HyDE** → generate a **hypothetical answer/document**, search using that answer-like text, then retrieve real documents.
* **Single-step decomposition** → split a complex question into **independent subquestions** that can be searched separately/parallel.
* **Multi-step decomposition** → split into **dependent sequential questions**, where each answer determines the next query.
* **Coarse-to-fine retrieval** → first retrieve a broad/relevant section using coarse representations (high-level summaries; e.g., 500-word chunks), then re-search more precisely inside that section using fine-grained chunks (e.g., 100-word chunks). This narrows the scope progressively.

### Easy way to remember them

- **Rewrite** → make the query clearer.
- **Multi-query** → ask it several ways.
- **Step-back** → ask a broader version too.
- **HyDE** → search with a hypothetical answer.
- **Decomposition** → break the problem into smaller questions.
- **Coarse-to-fine** → search broad first, then narrow down.

### Overall principle

> **Transform the query into a form that makes retrieval easier and more accurate, while keeping the original user question for final answer synthesis.**

And, as with indexing techniques, **benchmark these approaches on your own data**—extra LLM calls and retrievals can improve quality but also add latency, cost, and complexity. For example, `MultiQueryRetriever` works well for ambiguous questions; `HyDE` excels when queries are conceptually different from document phrasing.

# Content store query generation

## LangChain: **`SelfQueryRetriever`** - Simple concept

The `SelfQueryRetriever` is a powerful tool in the LangChain ecosystem designed to enhance document retrieval by ***combining semantic search with structured filtering***. It takes a natural-language query and lets an LLM turn it into:

**semantic search text + structured metadata filters**

Unlike traditional retrieval methods that rely solely on semantic similarity, the SelfQueryRetriever leverages a large language model (LLM) to generate structured queries that can *filter documents based on metadata fields* such as *genre, year, rating, or any other custom attributes*. This hybrid approach allows users to perform more precise and context-aware searches, making it an invaluable tool for applications like movie recommendations, product searches, or any domain where **metadata** plays a crucial role.

Example:

User asks:

> “Find sci-fi movies after 2015 with rating above 8.”

The retriever may interpret that roughly as:

`semantic query: "sci-fi movies"`
`filters: year > 2015 AND rating > 8`

> Filtered Retrieval: Applies the structured filter to the database first, then runs vector similarity only on the filtered subset.

## Self-querying / metadata query enrichment — simple concept

Self-querying turns a natural-language question into:

> **semantic search text + metadata filters**

Then the vector store narrows the search using metadata and performs semantic similarity search on the filtered subset. 

### Main methods

* **Explicit metadata filter** → your app/user directly specifies filters.
* **`SelfQueryRetriever`** → an LLM automatically infers the semantic query and metadata filters.
* **Structured LLM function call** → the LLM returns a typed structured query, and your code converts it into a vector-store-specific filter. 

Metadata can be added manually, extracted with **TF-IDF/BM25**, or generated by an LLM during ingestion. 

### `lark` dependency

LangChain’s **`SelfQueryRetriever` requires the `lark` parsing package**. Lark parses the structured query language generated by the LLM and turns it into metadata-filter expressions the retriever can apply. If `lark` is not installed, `SelfQueryRetriever` initialization can fail with an `ImportError`.

### Example

User asks:

> “Tell me about festivals in Newquay.”

The system may derive:

* semantic query: **`"events festivals"`**
* metadata filter: **`destination = Newquay`**, **`region = Cornwall`**

Then it searches only the relevant Newquay/Cornwall chunks for festival-related content. 

**Key idea:**

> **Use metadata to narrow the search space, then use embeddings to find the best matches inside it.**


## Natural language → SQL — simple concept

Use an LLM to turn a user’s natural-language question into a **SQL query**, run that query on a relational database, then use the returned rows as context for the final answer.

Typical flow:

> **User question → LLM generates SQL → clean/validate SQL → execute on DB → return rows → LLM synthesizes answer**

A good prompt should include the **database schema** and ideally a few sample rows, because this reduces hallucinated table/column names.

### Example

User asks:

> “Give me some offers for Cardiff, including the hotel name.”

The LLM may generate SQL like:

```sql
SELECT Offer.OfferDescription,
       Offer.DiscountRate,
       Accommodation.Name
FROM Offer
JOIN Accommodation
  ON Offer.AccommodationId = Accommodation.AccommodationId
JOIN Destination
  ON Accommodation.DestinationId = Destination.DestinationId
WHERE Destination.Name = 'Cardiff'
LIMIT 5;
```

The database returns something like:

> `Early Bird Discount, 20%, Cardiff Camping`

Then the LLM turns that into a natural-language answer.

**Key idea:**
> **Translate natural language into structured SQL so RAG can retrieve precise facts from relational databases.**


## Semantic SQL search — simple concept

Traditional SQL searches by **exact values or patterns**. Semantic SQL adds **embeddings** so SQL can search by **meaning/similarity**.

Typical flow:

> **Database value → create embedding → store embedding in vector column → embed user query → compare vectors → return nearest rows**

With PostgreSQL, this is commonly done using **pgvector**.

### Example

Suppose the database contains names:

`Roberto, Robert, Bob, Bobby, Bert`

Traditional SQL:

```sql
WHERE first_name = 'Roberto'
```

returns only **Roberto**.

Semantic SQL:

* embed `"Roberto"`
* compare it with stored name embeddings
* rank rows by vector similarity

This can also return semantically/linguistically related names such as **Robert, Bob, Bobby, Bert**, depending on the embedding model.

### Key idea

> **Use SQL for relational structure + vector embeddings for semantic similarity.**

You can also combine both:

> **exact SQL filters + semantic vector search + joins**

So semantic SQL is essentially:

> **Traditional SQL enriched with vector similarity search.**


## Graph database / KG-RAG / GraphRAG — simple concept

A **graph database** stores information as:

- **nodes = entities**
- **edges = relationships**

Example:

- `Roberto → isFanOf → InterMilan`
- `InterMilan → playsIn → SerieA`

For RAG, an LLM can turn a natural-language question into a graph query such as **Cypher** or **SPARQL**, run it against the graph database, then use the returned graph data to answer the user.

Typical flow:

> **User question → LLM generates Cypher/SPARQL → graph DB executes it → graph results → LLM synthesizes answer**

### Illustrative example

User asks:

> “Which league does Roberto’s favorite team play in?”

The LLM may generate a graph query that follows:

`Roberto → isFanOf → InterMilan → playsIn → SerieA`

The graph database returns:

> `SerieA`

Then the LLM answers:

> “Roberto’s favorite team, InterMilan, plays in Serie A.”

### Key idea

> **Use graph relationships for retrieval when the answer depends on how entities are connected.**

LLMs can also help by:

* extracting **entities and relationships** from text to build the graph
* generating **Cypher/SPARQL** from natural language
* converting graph query results into a natural-language answer

In one line:

> **Natural-language question → graph query → relationship traversal → answer from connected facts.**
