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
