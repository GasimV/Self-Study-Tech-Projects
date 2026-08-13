# Common Issues in Naive RAG Architecture and Recommended Solutions

| Issue | Recommended solution |
|---|---|
| Retrieval returning the wrong content chunks | Advanced document indexing techniques |
| Poor question formulation | Question transformations |
| Ineffective question for retrieval | Question transformations |
| Limited data relevance in the content store | Routing to multiple content stores |
| Limited querying capabilities for structured data | Content store query generation |
| Irrelevant retrieved results fed to the LLM | Retrieval postprocessing |


## Table of Contents
* [`ParentDocumentRetriever` — simple concept](#parentdocumentretriever--simple-concept)
* [`MultiVectorRetriever`](#multivectorretriever)
  * [Key concept of `MultiVectorRetriever`](#key-concept-of-multivectorretriever)
  * [Main difference from `ParentDocumentRetriever`](#main-difference-from-parentdocumentretriever)
* [Embedding document summaries `MultiVectorRetriever`](#embedding-document-summaries-multivectorretriever)
* [Why these techniques are called **multi-vector embedding approach**?](#why-these-techniques-are-called-multi-vector-embedding-approach)
* [**Hypothetical-question embeddings — simple concept**](#hypothetical-question-embeddings--simple-concept)
* [Can we combine all these techniques in our RAG solution (and is this good) or not?](#can-we-combine-all-these-techniques-in-our-rag-solution-and-is-this-good-or-not)

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

## **Hypothetical-question embeddings — simple concept**

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

