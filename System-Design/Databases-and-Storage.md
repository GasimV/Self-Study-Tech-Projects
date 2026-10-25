# Databases and Storage

## Table of Contents

- [Overview](#overview)
- [Databases](#databases)
  - [Why Applications Use Databases](#why-applications-use-databases)
  - [Types of Databases](#types-of-databases)
  - [Relational Databases](#relational-databases)
    - [Customers and Orders Example](#customers-and-orders-example)
    - [Normalization and Indexes](#normalization-and-indexes)
    - [Greenplum: Relational Analytics with MPP](#greenplum-relational-analytics-with-mpp)
      - [Parallelism: Business-Card Analogy](#parallelism-business-card-analogy)
      - [Cluster Components and Shared-Nothing Architecture](#cluster-components-and-shared-nothing-architecture)
      - [Query Walkthrough](#query-walkthrough)
      - [Availability and Practical Limits](#availability-and-practical-limits)
  - [Transactions and ACID](#transactions-and-acid)
    - [Account Transfer Example](#account-transfer-example)
    - [What ACID Does Not Promise](#what-acid-does-not-promise)
  - [NoSQL Databases](#nosql-databases)
    - [Schemas, Transactions, and Consistency](#schemas-transactions-and-consistency)
    - [Wide-Column vs. Analytical Columnar Storage](#wide-column-vs-analytical-columnar-storage)
  - [Relational and NoSQL Trade-Offs](#relational-and-nosql-trade-offs)
    - [Database Selection Checklist](#database-selection-checklist)
- [Key-Value Stores](#key-value-stores)
  - [What Is a Key-Value Store?](#what-is-a-key-value-store)
  - [Why Use Key-Value Stores in Distributed Systems?](#why-use-key-value-stores-in-distributed-systems)
  - [Functional Requirements and a Simple API](#functional-requirements-and-a-simple-api)
  - [Non-Functional Requirements and Trade-Offs](#non-functional-requirements-and-trade-offs)
  - [Design Topics to Study Next](#design-topics-to-study-next)
  - [Scalability: Partitioning and Consistent Hashing](#scalability-partitioning-and-consistent-hashing)
  - [Replication Models and Replica Placement](#replication-models-and-replica-placement)
  - [Coordinating Reads and Writes](#coordinating-reads-and-writes)
  - [Temporary Failures: Sloppy Quorums and Hinted Handoff](#temporary-failures-sloppy-quorums-and-hinted-handoff)
  - [Replica Repair and Merkle Trees](#replica-repair-and-merkle-trees)
  - [Membership, Gossip, and Failure Detection](#membership-gossip-and-failure-detection)
  - [Design Review and Interview Checklist](#design-review-and-interview-checklist)
- [Amazon DynamoDB](#amazon-dynamodb)
- [Column-Family Databases](#column-family-databases)
- [Apache HBase](#apache-hbase)
- [Graph Databases](#graph-databases)
- [Neo4j](#neo4j)
- [Summary](#summary)
- [Related Notes](#related-notes)
- [Further Reading](#further-reading)

## Overview

Applications need to retain information, find it efficiently, and modify it without violating required rules. **Databases and storage support these needs at different levels.**

| Term | Meaning | Example |
| --- | --- | --- |
| **Database** | An organized collection of application data | Customers, orders, and payment records |
| **Database management system (DBMS)** | Software that manages data, queries, concurrency, and supported guarantees | PostgreSQL or MongoDB |
| **Storage infrastructure** | Resources and services used to retain bytes | Local SSDs, network-attached block volumes, or object storage used by a system |

A DBMS can run within an application process, on one server, or across multiple nodes. Its data model is separate from its physical deployment. Different engines use different storage resources; an object-storage service is not automatically a transactional application database.

Choose from **access patterns, correctness requirements, workload, growth, and operating constraints**, not simply the labels “SQL” and “NoSQL.” A small application and a globally distributed service can need different architectures while both using relational data.

> **Mental model:** The data model organizes information; the DBMS implements operations and guarantees; storage infrastructure retains the underlying bytes. Correct application behavior requires all three to fit the workload.

## Databases

### Why Applications Use Databases

| Need | What a DBMS can contribute | Design responsibility |
| --- | --- | --- |
| **Organization and retrieval** | Data structures, indexes, query processing, and aggregation | Model actual queries and measure their cost |
| **Integrity and concurrency** | Constraints, atomic operations, transactions, and isolation | Define invariants and select adequate guarantees |
| **Security and sharing** | Authentication, authorization, and supported encryption controls | Configure least privilege, network access, key handling, and application authorization |
| **Growth** | Vertical scaling, replication, partitioning, or distributed execution | Account for hot keys, data movement, coordination, and cost |
| **Recovery** | Logging, backups, restore tools, and replication | Define acceptable loss/downtime and test recovery |
| **Analysis and history** | Reporting queries and optional audit, temporal, or change-tracking features | Decide what history to record and how long to retain it |

These are **capabilities, not automatic promises made by every database**. Constraints, encryption, audit features, backup coverage, and scaling behavior depend on the product and configuration. Not all database models organize application data as relational tables.

**Replication is not backup.** Replicas can improve availability or read capacity, but may also copy an accidental deletion or bad update. Backups retain recoverable data under a separate retention strategy; their usefulness still depends on completeness, accessibility, and successful restores. Neither replication nor merely creating backup files establishes recoverability without a tested recovery process. See the [PostgreSQL backup overview](https://www.postgresql.org/docs/current/backup.html).

### Types of Databases

A useful introductory classification separates **relational databases** from common **NoSQL families**:

```mermaid
flowchart TB
    DB["Database families"] --> REL["Relational"]
    DB --> NOSQL["Common NoSQL families"]
    NOSQL --> KV["Key-value"]
    NOSQL --> DOC["Document"]
    NOSQL --> WIDE["Column-family / wide-column"]
    NOSQL --> GRAPH["Graph"]
```

This is **not an exhaustive or mutually exclusive taxonomy**. Products can support several models, and query language does not uniquely determine storage architecture. For example, a relational database can store and query JSON; [PostgreSQL's JSON types](https://www.postgresql.org/docs/current/datatype-json.html) illustrate that overlap.

### Relational Databases

Relational databases organize data into **relations**, commonly represented as tables. SQL implementations offer schemas, queries, constraints, and transactions with product-specific details.

| Concept | Meaning |
| --- | --- |
| **Table** | A named structure representing an entity or relationship, such as Customers or Orders |
| **Row / record** | One entry in that table; a suitable key identifies it |
| **Column / attribute** | A named field with a declared type and applicable rules |
| **Primary key** | Column or columns chosen to uniquely identify rows; values cannot be null |
| **Foreign key** | A constraint requiring non-null reference values to match an eligible referenced key |
| **SQL** | A language for defining structures and querying/modifying data; dialects and extensions differ |
| **Transaction** | A group of operations managed as one transaction boundary |

Foreign keys can reference **suitable unique keys, not only primary keys**. Null handling and eligible referenced keys follow the engine's rules. A table name or column ending in `_id` does not create referential integrity by itself: the constraint must be declared and enforced. See [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html).

#### Customers and Orders Example

**Customers** — `customer_id` is the primary key:

| customer_id | name |
| --- | --- |
| 1 | Mina |
| 2 | Rashad |

**Orders** — `order_id` is the primary key; `customer_id` is a non-null foreign key to Customers:

| order_id | customer_id | total | status |
| --- | --- | --- | --- |
| 101 | 1 | 20.00 | paid |
| 102 | 1 | 5.00 | pending |
| 103 | 2 | 15.00 | paid |

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    CUSTOMERS {
        int customer_id PK
        string name
    }
    ORDERS {
        int order_id PK
        int customer_id FK
        decimal total
        string status
    }
```

Each order belongs to **exactly one existing customer** in this example; a customer can have **zero or many orders**. Mina has two orders, connected by `customer_id = 1`. Joining the tables can retrieve her name alongside each order without copying her current name into every order. Diagram types are illustrative, not an executable schema.

#### Normalization and Indexes

**Normalization** organizes relations to reduce avoidable duplication and update anomalies. Keeping customer details separately can avoid having to change the same current address in many order rows. It does not eliminate every repeated value: foreign-key values intentionally repeat, and historical order details may need deliberate snapshots.

**Denormalization** deliberately duplicates or precomputes information for a requirement such as read performance or historical accuracy. It introduces an explicit maintenance or freshness responsibility.

**Indexes** provide additional access paths. They can accelerate suitable lookups and joins but consume storage and add write/maintenance work. Joins are **not inherently slow**: cost depends on query shape, indexes, cardinality estimates, data size/distribution, and the execution plan. Inspect and measure actual plans rather than assuming one data model is faster. See [PostgreSQL query-plan documentation](https://www.postgresql.org/docs/current/using-explain.html).

Examples of relational DBMSs include **MySQL, PostgreSQL, Oracle Database, Microsoft SQL Server, SQLite, and IBM Db2**. These differ in deployment, concurrency, extensions, and operational characteristics; the list is not a ranking.

#### Greenplum: Relational Analytics with MPP

**Greenplum is a PostgreSQL-based relational/SQL DBMS designed for distributed analytics**, including data warehousing, reporting, and large aggregations. Its **MPP (massively parallel processing)** architecture illustrates why relational databases need not run on one server. It is not a NoSQL column-family database. See the [Greenplum project repository (archived historical material)](https://github.com/greenplum-db/gpdb-archive).

| Workload | Typical pattern and example |
| --- | --- |
| **OLTP — online transaction processing** | Many short operational transactions, such as recording individual purchases |
| **OLAP — online analytical processing** | Larger scans and aggregations, such as annual sales totals by region |

These are **workload categories, not rigid product boundaries**. PostgreSQL also supports analytical queries; a system's suitability depends on its architecture and workload.

**MPP mental model:** The coordinator accepts SQL and plans/distributes work. Segment instances process their data portions in parallel; results are combined and returned through the coordinator. See the [archived Greenplum architecture documentation](https://github.com/greenplum-db/gpdb-archive/blob/main/gpdb-doc/markdown/admin_guide/intro/arch_overview.html.md).

##### Parallelism: Business-Card Analogy

Suppose you must inspect **1,200 business cards** and find everyone working for one company. At one card per second, one worker needs **1,200 seconds = 20 minutes**. Divide the cards into ten equal piles and let ten workers inspect them simultaneously:

| Workers | Cards per worker | Ideal inspection time |
| --- | --- | --- |
| 1 | 1,200 | 1,200 seconds = 20 minutes |
| 10 | 120 | 120 seconds = 2 minutes |

This is an **ideal tenfold speedup**, assuming independent work at the same rate and ignoring the time to distribute cards, coordinate workers, and collect matches. Unequal piles or slower workers change the result.

In the regional-sales example, primary segments similarly process different portions of the orders dataset. Their partial results must then be combined; real queries also incur storage, network, and coordination costs.

##### Cluster Components and Shared-Nothing Architecture

These notes use **coordinator**; older Greenplum material calls it the **master**. A cluster combines PostgreSQL-derived database instances with Greenplum's distributed planning and execution.

| Component | Responsibility |
| --- | --- |
| **Coordinator** | Client entry point; authenticates connections, handles SQL planning, coordinates execution, and returns results. Its global catalog contains metadata; user-table data resides on segments. |
| **Standby coordinator** | Optional coordinator redundancy, maintained through log replication and activated through the deployment's recovery procedure. It is distinct from a segment mirror. |
| **Segment host** | A server or VM running segment instances. Several instances can use the same host's operating system, memory, and disks. |
| **Primary segment** | A database instance that stores and processes its assigned user-data portion. Different primaries normally work on different portions of a distributed table. |
| **Mirror segment** | A redundant copy of a corresponding primary segment, placed on another host and eligible to take over under the supported failover conditions. |
| **Interconnect** | The networking/communication layer used by the distributed execution system, including intermediate data exchange between segments. |

**Shared-nothing** describes separate host resources and distributed data ownership. It does not require a separate physical computer, operating system, or disk for every segment instance. A host contributes execution, memory, and storage resources that its segment instances share. The number of instances per host is a configuration decision based on resources and workload.

The following **illustrative layout** has two primary data portions and cross-host mirrors:

```mermaid
flowchart TB
    CLIENT["Analyst / BI client"] --> COORD["Coordinator"]
    COORD --> NET["Logical interconnect"]
    COORD -.->|"Logs"| STANDBY["Optional standby coordinator"]

    subgraph HOST_A["Segment host A"]
        direction TB
        P1["Primary S1<br/>Data portion 1"]
        M2["Mirror S2<br/>Copy of portion 2"]
    end

    subgraph HOST_B["Segment host B"]
        direction TB
        P2["Primary S2<br/>Data portion 2"]
        M1["Mirror S1<br/>Copy of portion 1"]
    end

    NET --> P1
    NET --> P2
    P1 -.-> M1
    P2 -.-> M2

    classDef coordinator fill:#fff3cd,stroke:#111,color:#111
    classDef primary fill:#dbeafe,stroke:#111,color:#111
    classDef mirror fill:#dcfce7,stroke:#111,color:#111
    class COORD,STANDBY,NET coordinator
    class P1,P2 primary
    class M1,M2 mirror
```

Solid arrows show the client/query-work path; dotted arrows show coordinator-log or segment-data replication. **Primary S1 and Primary S2 process different data portions; Mirror S1 and Mirror S2 hold redundant copies.** The standby is shown separately from the segment hosts; an actual deployment must choose its host and failure domain.

The interconnect box represents a communication layer, not necessarily one dedicated switch. Segment-to-segment exchanges and replication also use networking; the diagram simplifies those paths. Network capacity and isolation affect performance, but there is no single Ethernet speed appropriate to every deployment. See the [archived Greenplum architecture documentation (historical)](https://github.com/greenplum-db/gpdb-archive/blob/main/gpdb-doc/markdown/admin_guide/intro/arch_overview.html.md).

##### Query Walkthrough

1. **Connect:** An application or BI tool connects to the coordinator using a supported interface, such as JDBC, ODBC, or the `psql` client.
2. **Authenticate and plan:** The coordinator authenticates the connection, processes the SQL, and handles planning and distribution of query work. Its global catalog describes the database; it does not replace the user-table data on segments.
3. **Process in parallel:** Primary segments scan and compute over their assigned portions. The plan may require intermediate data exchange between segments, such as redistributing rows for a join or aggregation.
4. **Combine and return:** Intermediate results are combined according to the plan, and the coordinator presents the final result to the client. Not every computation must happen on the coordinator.

**Example:** To calculate annual sales totals by region across a large orders dataset, each segment filters its portion to the requested year and computes partial totals. Combining those totals produces the final regional totals. Depending on data distribution and the query plan, intermediate results may move between segments.

##### Availability and Practical Limits

Coordinator redundancy and segment redundancy protect different roles:

| Failure | Recovery role and condition |
| --- | --- |
| **Coordinator failure** | A configured, suitably synchronized standby can be activated through the supported recovery procedure. Activation and client reconnection are deployment-dependent; they are not universally automatic. |
| **Primary-segment or segment-host failure** | A healthy, eligible mirror on another host can take over the affected data portion through segment failover. Continued service requires the needed data portions, coordinator, and communication paths to remain available. |

In the diagram, if **Host A fails**, Mirror S1 on Host B can become the active copy of portion 1, while Primary S2 still holds portion 2. Host B then carries more active work and redundancy is reduced until recovery restores the missing copies. This assumes the remaining infrastructure and capacity support continued operation. Losing both copies of a required portion prevents normal access to that portion.

Mirrors must reside on different hosts from their corresponding primaries. A standby coordinator protects the coordinator role; it does not hold backup copies of every segment's user data. Treat standby capacity as part of the recovery design rather than assuming it is spare ETL capacity. See [Broadcom's coordinator-activation guidance](https://knowledge.broadcom.com/external/article/296354/failover-to-standby.html) for a vendor example of an explicit activation procedure.

**Storage layout is a separate choice:** Greenplum supports row-oriented heap tables and append-optimized tables with row or column orientation. Columnar storage does not make a database NoSQL. See the [provider's Greenplum storage explanation](https://yandex.cloud/en/docs/managed-greenplum/concepts/tables).

Greenplum can participate in a larger data platform and process data used for reporting or analytical models. That participation does not make the relational DBMS a data lake by itself. Capacity depends on the deployment, data layout, and workload; a fixed “hundreds of TB” ceiling is not a general definition.

**Trade-offs:** Distribution-key choices affect balance and data movement. Skew can leave one segment doing much more work; joins and aggregations may require inter-segment transfers. Network costs and cluster operations also matter, so adding nodes does not guarantee linear speedup. See the [provider's data-distribution explanation](https://yandex.cloud/en/docs/managed-greenplum/concepts/sharding).

> **Relational describes the data model; columnar describes a storage layout; MPP describes parallel processing across instances.**

### Transactions and ACID

A transaction groups related database operations so the application can commit them or abandon their uncommitted effects. ACID describes four important properties:

| Property | Meaning | Transfer example |
| --- | --- | --- |
| **Atomicity** | The transaction's changes take effect together or not at all | Do not retain only the debit without the corresponding credit |
| **Consistency** | Correct transaction logic and enforced rules preserve defined invariants | Preserve the combined balance and any required balance constraints |
| **Isolation** | Controls how concurrent transactions interact and what they can observe | Concurrent transfers must not produce forbidden outcomes under the chosen isolation strategy |
| **Durability** | Committed changes survive the failures covered by the configured guarantee | Retain the committed transfer through the covered crash/recovery scenario |

#### Account Transfer Example

For a simplified transfer of **20 units from A to B**, with no fees or other balance changes:

| Account | Before | After a successful commit |
| --- | --- | --- |
| A | 100 | 80 |
| B | 50 | 70 |
| **Combined** | **150** | **150** |

The application checks the relevant rules and groups the debit and credit within one transaction. On rollback, those uncommitted changes do not become the completed transfer. A database transaction does not automatically make unrelated external API calls atomic. See the [transaction introduction](https://www.postgresql.org/docs/current/tutorial-transactions.html).

#### What ACID Does Not Promise

- **ACID consistency is not distributed read consistency.** Preserving business/data invariants differs from whether a replica read reflects the latest write. See [Consistency](Distributed-System-Attributes.md#consistency).
- **ACID does not invent correct business logic.** A transaction can commit the wrong amount if neither its logic nor the enforced constraints prevent it.
- **Isolation levels matter.** Weaker levels permit outcomes that serializable execution rules out. Even serializable transactions may need safe retries after conflicts; a default isolation level is not automatically sufficient. See [PostgreSQL isolation levels](https://www.postgresql.org/docs/current/transaction-iso.html).
- **Durability has a failure scope.** Logging, flush/acknowledgment settings, replication, and recovery procedures determine what a deployment actually promises.
- **Error handling is engine-specific.** A failing statement, deadlock, explicit rollback, and disconnected client need not have identical effects. Do not assume every SQL error automatically rolls back the whole transaction. For example, [MySQL InnoDB documents different rollback scopes](https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html).

> **Recall:** Transactions are a tool for enforcing specified rules. Choose transaction boundaries, isolation, and durability deliberately; “supports ACID” is not a complete application-correctness design.

### NoSQL Databases

**NoSQL**, often expanded as *Not Only SQL*, is an umbrella label for several non-relational approaches. It does not mean “no structure,” “no relationships,” or “no transactions.” A database may store structured and semi-structured records or binary values depending on its model; not every engine is equally suited to every data shape.

| Family | Main organization | Simple access-pattern example | Representative systems |
| --- | --- | --- | --- |
| **Key-value** | Look up a value using a key; values may have rich supported types | Retrieve a session by its ID | Redis, Amazon DynamoDB |
| **Document** | Store records as documents with fields and nested structures | Read a product's description and variable attributes together | MongoDB, Apache CouchDB |
| **Column-family / wide-column** | Organize records around row/partition keys and related columns | Fetch device measurements within a modeled key/time range | Apache Cassandra, Apache HBase |
| **Graph** | Represent entities and explicit relationships for traversal | Follow account-to-device connections in a fraud investigation | Neo4j, Amazon Neptune |

These examples describe common use patterns, not exclusive product capabilities. Redis supports multiple [data types](https://redis.io/docs/latest/develop/data-types/); DynamoDB supports key-value and document patterns. See [CouchDB's document overview](https://docs.couchdb.org/en/stable/intro/overview.html), [Cassandra's architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html), and [Neo4j graph concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/).

#### Schemas, Transactions, and Consistency

**Flexible schema is not absence of schema.** Applications still rely on field meanings, types, indexes, and relationships. Existing readers may not understand a new field format; mixed versions, backfills, validation, and index changes need planning. See [MongoDB data-modeling guidance](https://www.mongodb.com/docs/manual/data-modeling/).

NoSQL does **not inherently mean weak consistency or absent transactions**. [MongoDB supports multi-document transactions](https://www.mongodb.com/docs/manual/core/transactions/), including supported distributed deployments; [DynamoDB provides transactional APIs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html). Scope, limits, isolation, deployment, and cost must be checked for the specific operation.

Read guarantees can also differ within one product: for example, DynamoDB documents [strongly consistent and eventually consistent read options](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html), with differences between tables and index types. A family name alone does not identify the consistency of every read.

#### Wide-Column vs. Analytical Columnar Storage

The terms sound similar but describe different ideas:

- **Wide-column / column-family model:** A logical organization around keyed rows and column families, with product-specific rules. HBase is an example; row-key design strongly affects access patterns.
- **Analytical columnar storage:** Physically stores values by column to support workloads such as scanning and aggregating selected columns.

Do not infer an analytical columnar layout merely from the label “column-family.” These model and storage-layout concepts can overlap in some systems, but are not synonyms. Compare [HBase's data model](https://hbase.apache.org/docs/datamodel/) with the [ClickHouse column-oriented overview](https://clickhouse.com/docs/get-started/about/intro).

The relational [Greenplum example](#greenplum-relational-analytics-with-mpp) shows the distinction: its append-optimized tables can use columnar storage while retaining the relational/SQL model.

### Relational and NoSQL Trade-Offs

| Dimension | Relational approaches | NoSQL approaches | Question to ask |
| --- | --- | --- | --- |
| **Queries and relationships** | SQL, joins, and constraints suit many interconnected workloads | Key, document, wide-column, or graph operations fit different access patterns | Which queries, traversals, and aggregations must be efficient? |
| **Transactions** | Commonly support multi-statement transactions; guarantees vary | Atomic/transaction scope varies; some support multi-record ACID transactions | Which changes must commit together? |
| **Schema evolution** | Explicit schemas and migrations; JSON support is possible | Often flexible records, but compatibility and indexes still matter | Can old and new application versions coexist? |
| **Scaling** | Vertical scaling, replicas, partitioning, sharding, or distributed relational designs | Many systems offer distributed partitioning, with model-specific restrictions | Where are the hot spots and cross-node coordination costs? |
| **Consistency** | Depends on isolation, replication, read routing, and settings | Depends on product, operation, topology, and settings | What may each read observe during concurrency or failure? |
| **Storage** | Normalization can reduce duplication; indexes and row layout affect size | Embedding/denormalization may reduce lookups but duplicate data | What are the actual memory, disk, and write-amplification costs? |
| **Security and operations** | Engine/deployment controls require correct configuration | Same responsibility, with different features and service boundaries | Who handles access, keys, upgrades, backups, and recovery? |
| **Portability** | SQL provides common foundations, but dialects and extensions differ | APIs and models vary significantly; some expose SQL-like query languages | What migration or interoperability constraints matter? |

**Relational does not mean “cannot scale horizontally.”** Distributed relational systems exist; [Spanner's schema and data-model documentation](https://docs.cloud.google.com/spanner/docs/schema-and-data-model) describes relational tables and distribution. Conventional deployments can also use read replicas or application sharding, with different coordination and maintenance costs. Conversely, distributing a NoSQL system is not automatically seamless or appropriate.

For distributed analytical workloads, [Greenplum's MPP architecture](#greenplum-relational-analytics-with-mpp) provides another relational scaling example.

**Null storage is implementation-dependent.** Do not assume every null reserves a full column value or makes relational databases inherently memory-intensive. PostgreSQL, for example, documents a [null bitmap in its row layout](https://www.postgresql.org/docs/current/storage-page-layout.html). Measure the chosen engine and schema.

**Schema changes are not automatically disruption-free in either category.** Security, availability, and scalability likewise require deliberate design and operation, rather than following automatically from a database label.

#### Database Selection Checklist

1. What are the main reads, writes, searches, traversals, and aggregations?
2. Which invariants and multi-record transaction boundaries must hold?
3. What freshness and concurrency guarantees does each operation require?
4. What are the data size, growth, throughput, latency, and geographic requirements?
5. Which partition keys, indexes, or joins could become bottlenecks?
6. How will schema changes, backups, restores, and failures be handled?
7. Which security controls, operational skills, and costs can the team support?

Use [CAP](Distributed-Systems-Theorems-and-Data-Structures.md#cap-theorem) and [PACELC](Distributed-Systems-Theorems-and-Data-Structures.md#pacelc-theorem) to reason about relevant distributed trade-offs—not to assign every product a permanent SQL/NoSQL consistency category. For a small workload, a simpler deployment can be a sound design.

> **Choose the data model and guarantees for the workload, then validate the engine and deployment. Neither “relational” nor “NoSQL” is a universal winner.**

## Key-Value Stores

### What Is a Key-Value Store?

A **key-value store** associates a unique **key** with a **value** within a defined namespace. The key identifies what to retrieve or change, much like a dictionary:

| Key | Value | Meaning |
| --- | --- | --- |
| `cart:42` | `book` | A simplified shopping-cart value |
| `theme:42` | `dark` | A user's display preference |
| `product:7` | `{"name":"Notebook","price":5}` | A serialized product record |

The key is the lookup identifier; the value may be text, bytes, a serialized document, or a product-supported data structure. The application must still define formats, validation, and compatibility. Flexible values do not remove the need for a data model.

**A key-value store is not necessarily distributed.** It can be embedded, run on one server, or span several servers. A **distributed hash table (DHT)** distributes key-based lookup and ownership using hashing; it is one approach to building a distributed key-value system, not a synonym for every key-value database.

The basic mental model exposes one current value per key. Replication and concurrent updates can introduce internal copies or competing versions; the store's consistency and conflict rules determine what a read returns. [Redis strings](https://redis.io/docs/latest/develop/data-types/strings/) illustrate basic key-based storage and retrieval, while Redis also supports richer types.

> **Mental model:** You know the key and ask for its value. How the system locates, stores, replicates, and protects that value is a separate design problem.

### Why Use Key-Value Stores in Distributed Systems?

| Benefit | How it can help | Important limit |
| --- | --- | --- |
| **Scalability** | Partition different keys across nodes to spread storage and traffic | Hot keys, skew, and rebalancing can still limit scaling |
| **Performance** | Direct key access can avoid unnecessary scans or joins | Network hops, value size, storage, load, and coordination affect latency |
| **Flexible values** | Store records with different payload shapes | Readers and writers must agree on their meaning and format |
| **Fault tolerance** | Keep replicas so another node may serve a key after a failure | Partitioning alone does not create a backup copy; failover needs adequate replicas and a defined protocol |

Typical uses include sessions, preferences, shopping carts, and cached objects. Suitability depends on required durability, consistency, expiry, and access controls. Key lookup alone does not provide arbitrary searches, joins, or multi-key transactions; additional capabilities depend on the engine.

```mermaid
flowchart TB
    APP["Application"] --> ROUTE["Key-based routing"]
    ROUTE --> A["Partition A<br/>Some keys"]
    ROUTE --> B["Partition B<br/>Other keys"]
    A -.-> AR["Replica of A"]
    B -.-> BR["Replica of B"]

    classDef client fill:#fff3cd,stroke:#111,color:#111
    classDef data fill:#dbeafe,stroke:#111,color:#111
    class APP,ROUTE client
    class A,B,AR,BR data
```

The routing arrows show alternative destinations for a key, not a broadcast to every partition. Dotted arrows show replication relationships; they do not prescribe synchronous or asynchronous acknowledgments. Routing can reside in a client or service. **Partitioning divides data; replication copies it.** The diagram does not define a complete failover protocol.

### Functional Requirements and a Simple API

For an illustrative design, define these operations explicitly:

| Operation | Intended behavior | Illustrative result |
| --- | --- | --- |
| **`Put(key, value)`** | Insert a new key or replace its current value | Success under the chosen write-acknowledgment policy, or an operation error |
| **`Get(key)`** | Retrieve the value visible under the selected read guarantee | Value, `NotFound`, or an operation error |
| **`Delete(key)`** | Remove the key's logical value | `Deleted`, `NotFound`, or an operation error |

These names describe a conceptual API, not commands shared by every database. Here a put replaces the whole value; field updates, conditional writes, and multi-key operations need separate contracts. Missing-key deletion behavior varies: an API may report `NotFound` or treat an already-absent key as successful deletion.

**Sequential walkthrough**, with no concurrent writers and reads that observe completed writes:

| Request | Result |
| --- | --- |
| `Put("cart:42", "book")` | Success; create the key |
| `Get("cart:42")` | `"book"` |
| `Put("cart:42", "book, pen")` | Success; replace the value |
| `Get("cart:42")` | `"book, pen"` |
| `Delete("cart:42")` | `Deleted` |
| `Get("cart:42")` | `NotFound` |

`NotFound` is distinct from a stored empty value, a timeout, or an authorization failure. A timeout does not prove that the key is absent or that a write failed; the request may have completed before its reply was lost. Define safe retry behavior accordingly.

### Non-Functional Requirements and Trade-Offs

| Requirement | What to specify | Design implication |
| --- | --- | --- |
| **Scalability** | Data size, growth, key distribution, and peak traffic | Plan capacity, partitioning, hot-key handling, and rebalancing |
| **Performance** | Read/write latency percentiles at a stated load and value size | Measure routing, storage, network, and coordination costs; do not promise constant latency as the system grows |
| **Durability** | Which acknowledged writes survive which failures | Define persistence, replication acknowledgments, recovery, and backup procedures |
| **Consistency** | What each read may observe and how concurrent writes are ordered or reconciled | Choose a read/write protocol and explicit conflict semantics |
| **Availability** | Which operations must complete during covered failures | Provide healthy capacity and replicas; some failures can still prevent progress |
| **Partition behavior** | How each side behaves when nodes cannot communicate | Decide which operations wait, fail, or proceed with weaker coordination |

If a per-key operation is **linearizable**, a read observes the latest write in a single order consistent with real-time completion; concurrent operations can be ordered within their overlap. This is a possible requirement, not an inherent key-value-store property. Eventually consistent reads may return an older value; [DynamoDB documents different read options and their scope](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html).

**These requirements cannot all be unconditional.** During a network partition, a system cannot guarantee both linearizable behavior and successful completion of every request at every reachable node. It may reject or delay operations that cannot coordinate, or allow operations under weaker consistency rules. See [CAP](Distributed-Systems-Theorems-and-Data-Structures.md#cap-theorem) and [PACELC](Distributed-Systems-Theorems-and-Data-Structures.md#pacelc-theorem).

Replication does not automatically establish durable storage or consistent reads, and it is not a substitute for backup. Likewise, “low latency” is a workload target, not a guarantee under arbitrary network delays and failures.

### Design Topics to Study Next

The introductory requirements lead to these design questions:

| Topic | Question to resolve |
| --- | --- |
| **Partitioning and scalability** | [Place keys and handle membership changes](#scalability-partitioning-and-consistent-hashing). |
| **Replication** | [Choose copies, physical owners, and replication behavior](#replication-models-and-replica-placement). |
| **Versioning and conflicts** | [Interpret concurrent versions](#coordinating-reads-and-writes); detailed reconciliation algorithms remain further study. |
| **Configurability** | [Specify R/W thresholds and their limits](#coordinating-reads-and-writes). |
| **Fault tolerance and failure detection** | [Handle temporary failures](#temporary-failures-sloppy-quorums-and-hinted-handoff), [repair replicas](#replica-repair-and-merkle-trees), and [manage membership](#membership-gossip-and-failure-detection). |

The original [Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) is a concrete example combining partitioning, replication, versioning, and application-assisted conflict handling. **Dynamo is the historical system described in that paper; Amazon DynamoDB is a separate managed product.** These techniques and their guarantees must be evaluated together rather than assumed from the key-value model.

> **Recall:** A simple key-based API can hide a complex distributed design. Specify what success, missing data, concurrent updates, and failures mean before choosing the mechanisms.

### Scalability: Partitioning and Consistent Hashing

**Partitioning assigns different keys to different storage nodes.** Hash-based placement can spread keys, but the mapping must remain understandable to clients and coordinators when membership changes.

**Modulo routing:** For `m` nodes with zero-based indexes `0` through `m - 1`, select `index = hash(key) % m`:

| Hash result | Node count | Calculation | Selected index |
| --- | --- | --- | --- |
| 10 | 4 | `10 % 4 = 2` | 2 |
| 10 | 5 | `10 % 5 = 0` | 0 |

```mermaid
flowchart TB
    KEY["Key"] --> HASH["Hash = 10"]
    HASH --> M4["Modulo 4"]
    HASH --> M5["Modulo 5"]
    M4 --> I2["Node index 2"]
    M5 --> I0["Node index 0"]

    classDef step fill:#fff3cd,stroke:#111,color:#111
    classDef node fill:#dbeafe,stroke:#111,color:#111
    class KEY,HASH,M4,M5 step
    class I2,I0 node
```

The hash stays the same; changing the divisor changes placement. Many other keys can also move, including keys whose old owners remain healthy. A uniform hash can spread **keys** approximately evenly, but does not make four nodes receive exactly 25% of requests each: some keys may be much more popular or larger than others.

**Consistent hashing:** Place node tokens and key hashes in the same circular hash space. Select the first eligible token clockwise, wrapping around when necessary. In this illustrative ring, the key hash `60` belongs to N3 at token `70`:

```mermaid
flowchart LR
    N1["N1: token 20"] --> N2["N2: token 45"]
    N2 --> N3["N3: token 70"]
    N3 --> N4["N4: token 90"]
    N4 --> N1
    KEY["Key hash 60"] -.-> N3

    classDef node fill:#dbeafe,stroke:#111,color:#111
    classDef selected fill:#fff3cd,stroke:#111,stroke-width:2px,color:#111
    class N1,N2,N4 node
    class KEY,N3 selected
```

The arrows represent logical clockwise token order, not a network topology or a required circular rendering. If N5 joins at token `65`, keys in `(45, 65]` move from N3 to N5 in this **single-token, primary-placement example**. Other primary ranges remain unchanged. Virtual nodes and replication can involve additional ranges and replica transfers; do not generalize this example into “only one physical neighbor is ever affected.”

**Virtual nodes** give a physical server several token positions. One hash function is sufficient: `h("nodeA#0")`, `h("nodeA#1")`, and `h("nodeA#2")` identify different tokens for the same machine. A placement policy can assign more tokens or weight to greater capacity. Multiple tokens can improve range balance and spread reassignment among neighbors, but also add metadata and maintenance work.

Virtual nodes do not add hardware, create independent replicas, or distribute a single hot key across multiple owners by themselves. Membership changes also need data transfer and a safe routing transition; a new owner cannot recreate data if no copy survives.

See [Consistent Hashing](Distributed-Systems-Theorems-and-Data-Structures.md#consistent-hashing), [Virtual Nodes](Distributed-Systems-Theorems-and-Data-Structures.md#virtual-nodes-multiple-tokens-per-server), and the existing [C++ teaching example](examples/consistent_hashing/README.md). [Cassandra's architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html) illustrates token-based placement; its implementation is not a universal specification for every key-value store.

### Replication Models and Replica Placement

**Replication keeps copies of the same data.** A distributed store can partition data first and then replicate each partition; it need not copy every key to every server.

| Model | Where client writes are handled | Main design questions |
| --- | --- | --- |
| **Primary-secondary / single-leader** | The current primary for that partition orders writes; secondaries apply replicated changes | Replication lag, acknowledgment rules, promotion, and preventing competing primaries |
| **Leaderless** | A coordinator sends operations to the key's replica set without a permanent per-key write leader | Response thresholds, concurrent versions, reconciliation, and replica repair |

**Primary-secondary example:**

```mermaid
flowchart TB
    CLIENT["Client writes"] --> PRIMARY["Primary"]
    PRIMARY --> S1["Secondary 1"]
    PRIMARY --> S2["Secondary 2"]
    READ["Optional replica reads"] --> S2

    classDef primary fill:#fff3cd,stroke:#111,color:#111
    classDef replica fill:#dbeafe,stroke:#111,color:#111
    class PRIMARY primary
    class S1,S2 replica
```

The primary-to-secondary arrows carry replication updates. A secondary applies those updates but does not normally accept independent client writes in this single-leader model. The primary can also serve reads; secondary reads depend on product capabilities and can be stale when replication lags.

With **asynchronous replication**, the primary may acknowledge before secondaries have the update. A failure can therefore lose acknowledged updates not yet protected elsewhere. **Synchronous replication** waits for the configured replica acknowledgment condition; whether that means received, persisted, or applied must be specified. Waiting improves the covered guarantee but introduces coordination costs and can block progress.

A failed primary can be replaced through a designed failover process; primary-secondary replication is not inherently limited to permanent loss of write service. Promotion must select an eligible replica, redirect clients, and prevent the old primary from continuing as a writer—often through **fencing**, which blocks an obsolete writer. See [PostgreSQL replication](https://www.postgresql.org/docs/current/warm-standby.html) and [failover guidance](https://www.postgresql.org/docs/current/warm-standby-failover.html). Consensus-based designs such as [Raft](Distributed-Systems-Theorems-and-Data-Structures.md#raft) provide another context for safe leadership and replicated history.

**Leaderless example for one key:**

```mermaid
flowchart TB
    CLIENT["Client"] --> COORD["Request coordinator"]
    COORD <--> A["Replica A"]
    COORD <--> B["Replica B"]
    COORD <--> C["Replica C"]

    classDef coordinator fill:#fff3cd,stroke:#111,color:#111
    classDef replica fill:#dbeafe,stroke:#111,color:#111
    class COORD coordinator
    class A,B,C replica
```

The coordinator is a **request-handling role**, not necessarily a permanent leader or a separate machine. A storage node can coordinate a request and hold a replica. Different requests may use different coordinators. The diagram shows request/reply paths; it does not require all cluster nodes to exchange every write.

Let **N** be the total intended replicas of a key, including its first owner. It differs from **m**, the total physical-node count used in the modulo example. For `N = 3`, a clockwise preference scan such as `A#0 → A#1 → B#0 → C#0 → D#0` selects intended physical owners **A, B, C**: A's second token does not count as another copy. Later candidates such as D can be considered by a fallback policy.

Place replicas across suitable failure domains, such as racks or availability zones, where the deployment supports it. Three copies in one rack do not protect against loss of that rack. Neither replication model automatically provides unlimited availability or durability; persistence, routing, failure assumptions, and recovery remain necessary.

### Coordinating Reads and Writes

Clients can reach the storage system through different paths:

| Approach | Benefit | Responsibility |
| --- | --- | --- |
| **Generic router / load balancer** | Keeps placement knowledge out of the client | The selected node may need to forward to the key's replicas |
| **Partition-aware client** | Can avoid an unnecessary forwarding hop | Must refresh placement information and handle stale routes and failures |

For this **Dynamo-style teaching model**, the coordinator contacts intended replicas in parallel and waits for configured response thresholds. These are conceptual operations, not a complete implementation protocol.

- **N:** Intended replica count for the key.
- **W:** Distinct replica acknowledgments required for write success.
- **R:** Distinct valid replica responses required for a read.

For ordinary fixed-set operations, assume `1 <= R, W <= N`. Count physical replicas once, not repeated replies or multiple virtual nodes on one host. A read must interpret returned versions according to the protocol; receiving R responses alone does not establish which value to return.

**Example: N = 3, R = 2, W = 2, intended replicas A/B/C.**

1. A coordinator sends a versioned put to A, B, and C.
2. A and B acknowledge under the configured persistence policy. The coordinator can report write success after those two acknowledgments; C may complete later or require repair.
3. A subsequent read requests the replicas in parallel. Suppose B and C provide the first two valid responses.
4. B can report the completed write even if C is stale. The coordinator must select or reconcile versions correctly rather than return an arbitrary response.
5. Outstanding propagation and repair are separate from the client's completed response.

For subsets of the **same fixed N-replica set**, `R + W > N` guarantees that every qualifying read set intersects every qualifying write set:

| N | R | W | Read/write overlap guaranteed? | Completion requirement and trade-off |
| --- | --- | --- | --- | --- |
| 3 | 2 | 1 | **No:** `2 + 1 = 3` | A read can miss the sole acknowledged writer; smaller write threshold |
| 3 | 2 | 2 | **Yes:** `2 + 2 = 4` | Both operations need two responses; one unreachable replica need not prevent completion |
| 3 | 3 | 1 | **Yes:** `3 + 1 = 4` | Reads need all three; writes need one |
| 3 | 1 | 3 | **Yes:** `1 + 3 = 4` | Writes need all three; reads need one |

“Guaranteed overlap” is a set-intersection property, **not a standalone guarantee of linearizability**. Correct version selection, concurrent-write handling, incomplete-operation behavior, and operation ordering still matter. Even overlapping write sets do not resolve concurrent updates by arithmetic alone. Compare [Quorum Reads and Writes](Distributed-System-Attributes.md#quorum-reads-and-writes), including its consistency caveat.

**Latency and availability:** With parallel fan-out to all N eligible replicas, the waiting component is typically determined by the R-th valid read response or W-th qualifying write acknowledgment, plus coordination and processing. It is not necessarily the slowest of all replicas contacted. Increasing R or W generally requires more reachable responses and can increase latency or reduce operation availability; there is no configuration that tolerates arbitrary failures.

**Conflict example:** Two writers read the same cart version, then independently add `book` and `pen`. Returning one later-timestamped replacement could discard the other addition. The system needs an explicit ordering, conditional-update, or reconciliation policy. Version metadata can identify relevant relationships, but automatic merging is application-dependent. Replica counts alone do not solve this problem.

### Temporary Failures: Sloppy Quorums and Hinted Handoff

A **strict replica-set quorum** requires qualifying responses from a key's designated replicas. In a **sloppy quorum**, a Dynamo-style system may substitute other eligible healthy nodes from its preference list when intended replicas are unreachable. This can allow more operations to complete, but changes the participating sets.

**Example:** Intended replicas are **A, B, C**, with `N = 3` and `W = 2`. A is unreachable, C is slow, and D is an eligible fallback. Q is the request coordinator, shown separately for clarity.

```mermaid
sequenceDiagram
    participant Q as Coordinator Q
    participant A as Intended A
    participant B as Intended B
    participant C as Intended C
    participant D as Fallback D

    Note over Q,D: Stage 1 - A unreachable, C slow
    Q->>B: Put v2
    Q->>C: Put v2
    Q->>D: Store v2 with hint for A
    B-->>Q: Stored
    D-->>Q: Stored
    Note over Q: W = 2 satisfied by B and D
    Note over Q,D: Stage 2 - A recovers
    D->>A: Deliver hinted update v2
    A-->>D: Update durably handled
    Note over D: Remove temporary hinted copy
```

D stores the **key, value/update, version metadata, and intended destination A** under the fallback policy—not merely a request ID. After A recovers, D delivers the update. Once A has safely handled it, D removes the corresponding temporary copy. D must not discard unrelated data it owns. The request to C may still be pending; the diagram does not assume C has stored v2.

**Why overlap can fail:** Before handoff completes, A could return with its old value while C is still stale. A read receiving replies from **A and C** can miss the successful write acknowledged by **B and D**. Although `R + W = 4 > 3` numerically, those two sets are disjoint because D lies outside the intended A/B/C set.

Hints require safe replay so retries do not duplicate logical effects or overwrite newer versions incorrectly. Deletion/version information must survive the required recovery window. Hint storage, retention, and reachability are finite; D can also fail. Hinted handoff therefore **does not guarantee that every read/write succeeds or that every missed update is repaired**. Additional replica synchronization is needed when hints cannot finish.

This example follows the **historical Dynamo-style fallback placement** described in the [Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf). [Cassandra's documented hints](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/hints.html) are stored by coordinators for unavailable replicas; they are not an identical implementation of temporary replica substitution. Cassandra describes hints as best effort and not a replacement for repair.

### Replica Repair and Merkle Trees

**Anti-entropy repair** compares replica state and transfers missing or differing data. It is useful after prolonged outages, incomplete propagation, or replacement; it is not limited to permanently failed nodes. A replacement needs data from surviving replicas or a suitable backup.

A **Merkle tree** summarizes a dataset through hashes: leaves summarize records or ranges, and each parent summarizes its children. Compare equivalent key ranges using compatible ordering, encoding, and version/snapshot rules. Conceptually, record hashes must cover the **key, value, and relevant version/deletion state**, not only the key name; equal names with different values must be distinguishable.

| Comparison for keys k1–k4 | Observation | Next action |
| --- | --- | --- |
| Whole-range roots | Different | Compare the two subranges |
| Left subtree: k1–k2 | Equal | Skip this subtree under the hash assumptions |
| Right subtree: k3–k4 | Different | Compare its children |
| Record k3 | Different | Exchange state and apply reconciliation rules |
| Record k4 | Equal | No repair needed for that record |

With suitable collision-resistant hashes and equivalent tree construction, matching roots indicate matching summarized state with the usual negligible collision risk. Different roots tell us **where to investigate**, not which replica has the correct version. Reconciliation rules determine the retained state; a newer deletion marker may need to suppress an older value.

Comparing only differing branches can reduce transferred data. Building and maintaining trees still costs storage/CPU/I/O, and extensive differences can require substantial transfer. Changed ownership ranges may require rebuilding affected trees, depending on the implementation.

Merkle trees cannot recover a value whose every copy is gone, establish business correctness, or replace version handling. See [Cassandra's repair explanation](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/repair.html) for an implementation using range comparisons and Merkle trees.

### Membership, Gossip, and Failure Detection

Keep these concepts separate:

| Concept | What it describes |
| --- | --- |
| **Token ownership** | Which physical nodes own particular hash ranges and their replicas |
| **Membership** | Which nodes belong to the cluster, including controlled additions and removals |
| **Reachability / liveness estimate** | Which peers a node currently believes it can contact |

**Gossip** spreads selected cluster information through repeated peer exchanges. For example, A exchanges membership information with B; B later exchanges with C, allowing C to learn about A. Bootstrap contacts or seed nodes help a joining node discover the existing cluster. Token assignment and ownership policy are distinct from merely choosing peers to contact.

This is control information, **not automatic replication of every application write**. Message contents, persisted membership records, and liveness detectors depend on the system. The Dynamo paper, for example, separates explicit membership changes from local reachability judgments. Do not assume every gossip design has one globally agreed failure view.

A timeout means “no acceptable response arrived in time.” The node could be slow, partitioned, or unreachable only from one observer. Two healthy nodes can therefore disagree about a third node's liveness. During a partition, gossip cannot instantly reconcile views across the broken link.

A brief outage need not trigger permanent removal and full redistribution. Define when to keep placement stable and route around a suspected failure, when to rebuild replicas, and when to change membership. Planned joins/removals need controlled data movement, routing updates, and adequate copies throughout the transition. Returning nodes may need repair before their stale data can safely participate in particular operations.

> **Failure detection guides a response; it does not prove a node is permanently dead. Membership changes and data recovery require their own rules.**

### Design Review and Interview Checklist

1. **Requirements:** Define key/value sizes, operations, growth, workload skew, latency targets, and required failure behavior.
2. **Placement:** Explain routing, partition ownership, membership changes, and hot-key handling.
3. **Replication:** Choose N, distinct physical owners, failure domains, and persistence/acknowledgment semantics.
4. **Consistency:** Define what reads may observe, how R/W are used, and which operations must stop when coordination is unavailable.
5. **Concurrency:** Explain version handling and what happens to competing writes; do not claim quorum overlap supplies a complete protocol.
6. **Temporary failures:** Describe routing, fallback policy, hint limits, retry safety, and client-visible uncertainty.
7. **Recovery:** Explain anti-entropy, replacement, deletion handling, backup, and what happens if no copy survives.
8. **Membership and operations:** Cover discovery, suspicion, controlled changes, safe rejoining, and monitoring of lag, hints, capacity, and repair.
9. **Justification:** State why this design fits the workload, what it cannot guarantee, and how requirements or configuration may evolve.

> **Recall:** Hashing places keys; replication preserves copies; response thresholds control participation; version rules interpret writes; hints and repair restore missed state; membership and failure detection guide routing and recovery. The guarantees come from the complete design.

## Amazon DynamoDB

> Study notes to be added.

## Column-Family Databases

> Study notes to be added.

## Apache HBase

> Study notes to be added.

## Graph Databases

> Study notes to be added.

## Neo4j

> Study notes to be added.

## Summary

Databases organize application information; DBMSs supply operations and configurable guarantees; storage resources retain the underlying bytes. Relational, key-value, document, column-family, and graph models emphasize different ways to represent and access data.

Transactions, constraints, indexes, partitioning, and recovery mechanisms must be selected for the actual workload. Relational systems can scale beyond one node and store semi-structured data; NoSQL systems can provide strong consistency and transactions within documented boundaries. Neither category removes the need for modeling, compatibility planning, access control, and tested recovery.

The later sections above reserve space for deeper study of particular families and implementations; their internals are not covered by this introduction.

> **Recall:** Start with the queries and invariants. Then choose the model, guarantees, engine, and operating strategy—not the other way around.

## Related Notes

- [Data engineering pipelines and analytical architectures](Data-Engineering-for-Solution-Architecture.md)
- [System design at different scales](Understanding-System-Design.md#system-design-at-different-scales)
- [Distributed consistency](Distributed-System-Attributes.md#consistency)
- [CAP theorem](Distributed-Systems-Theorems-and-Data-Structures.md#cap-theorem)
- [PACELC theorem](Distributed-Systems-Theorems-and-Data-Structures.md#pacelc-theorem)
- [IAM and authorization](Identity-and-Access-Management.md#authorization-in-practice)

## Further Reading

- [PostgreSQL: Constraints and Keys](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL: Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [PostgreSQL: Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL: JSON Types](https://www.postgresql.org/docs/current/datatype-json.html)
- [PostgreSQL: Query Plans](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL: Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL: Physical Row Layout and Null Bitmap](https://www.postgresql.org/docs/current/storage-page-layout.html)
- [MySQL: InnoDB Error Handling and Rollback Scope](https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html)
- [MongoDB: Data Modeling](https://www.mongodb.com/docs/manual/data-modeling/)
- [MongoDB: Transactions](https://www.mongodb.com/docs/manual/core/transactions/)
- [DynamoDB: Transactions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html)
- [DynamoDB: Read Consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
- [Redis: Data Types](https://redis.io/docs/latest/develop/data-types/)
- [Redis: String Values and Key-Based Operations](https://redis.io/docs/latest/develop/data-types/strings/)
- [Dynamo: Amazon's Highly Available Key-Value Store — Original 2007 Paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Apache CouchDB: Technical Overview](https://docs.couchdb.org/en/stable/intro/overview.html)
- [Apache Cassandra: Architecture Overview](https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html)
- [Apache Cassandra: Token Placement, Replication, and Membership](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Apache Cassandra: Hints and Hinted Handoff](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/hints.html)
- [Apache Cassandra: Replica Repair and Merkle Trees](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/repair.html)
- [PostgreSQL: Primary-Standby and Synchronous Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [PostgreSQL: Failover and Preventing Competing Primaries](https://www.postgresql.org/docs/current/warm-standby-failover.html)
- [Apache HBase: Data Model](https://hbase.apache.org/docs/datamodel/)
- [ClickHouse: Column-Oriented Database Overview](https://clickhouse.com/docs/get-started/about/intro)
- [Neo4j: Graph Database Concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/)
- [Spanner: Schemas and Data Distribution](https://docs.cloud.google.com/spanner/docs/schema-and-data-model)
- [Greenplum Project Repository — Archived Historical Material](https://github.com/greenplum-db/gpdb-archive)
- [Greenplum Architecture — Archived Historical Documentation](https://github.com/greenplum-db/gpdb-archive/blob/main/gpdb-doc/markdown/admin_guide/intro/arch_overview.html.md)
- [Broadcom: Greenplum Standby Coordinator Activation](https://knowledge.broadcom.com/external/article/296354/failover-to-standby.html)
- [Yandex Cloud: Greenplum Storage Layouts](https://yandex.cloud/en/docs/managed-greenplum/concepts/tables)
- [Yandex Cloud: Greenplum Data Distribution](https://yandex.cloud/en/docs/managed-greenplum/concepts/sharding)
