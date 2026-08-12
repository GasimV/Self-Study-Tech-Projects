# Common Issues in Naive RAG Architecture and Recommended Solutions

| Issue | Recommended solution |
|---|---|
| Retrieval returning the wrong content chunks | Advanced document indexing techniques |
| Poor question formulation | Question transformations |
| Ineffective question for retrieval | Question transformations |
| Limited data relevance in the content store | Routing to multiple content stores |
| Limited querying capabilities for structured data | Content store query generation |
| Irrelevant retrieved results fed to the LLM | Retrieval postprocessing |


## ParentDocumentRetriever — simple concept

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

# MultiVectorRetriever

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
→ hypothetical questions
→ generated-question embeddings
→ other representations

> and **any of those vectors can lead back to the same parent document**.

So the easiest way to remember it is:

**`ParentDocumentRetriever` = convenient parent/child retriever.**
**`MultiVectorRetriever` = more general framework where many vector representations can point to the same parent.**
