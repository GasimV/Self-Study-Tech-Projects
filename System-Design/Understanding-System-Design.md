# Understanding System Design

## Table of Contents

- [Overview](#overview)
- [Core Terminology](#core-terminology)
- [Functional and Non-Functional Requirements](#functional-and-non-functional-requirements)
- [Design Process](#design-process)
- [High-Level System Design](#high-level-system-design)
  - [Data Flow](#data-flow)
  - [Scalability](#scalability)
  - [Fault Tolerance](#fault-tolerance)
- [Low-Level System Design](#low-level-system-design)
  - [Algorithms](#algorithms)
  - [Data Structures](#data-structures)
  - [API Design](#api-design)
  - [Code Optimization](#code-optimization)
- [Design Challenges and Trade-Offs](#design-challenges-and-trade-offs)
  - [Common Challenges](#common-challenges)
  - [Evaluating Trade-Offs](#evaluating-trade-offs)
- [Key Takeaway](#key-takeaway)
- [System Design vs. Software Architecture](#system-design-vs-software-architecture)
- [System Design & Deployment Infra, Ops, Networking](#system-design--deployment-infra-ops-networking)
- [System Design vs. Solution Architecture](#system-design-vs-solution-architecture)
  - [Example: E-commerce platform](#example-e-commerce-platform)
  - [Key takeaway](#key-takeaway-1)
- [Levels of Architecture: System Design vs. Solution Architecture vs. Enterprise Architecture](#levels-of-architecture-system-design-vs-solution-architecture-vs-enterprise-architecture)
  - [1. Abstraction levels of architecture](#1-abstraction-levels-of-architecture)
  - [2. Recommended learning progression](#2-recommended-learning-progression)
- [AI Architect Knowledge Map](#ai-architect-knowledge-map)
  - [Complete Knowledge Map](#complete-knowledge-map)
  - [Required Depth of Knowledge](#required-depth-of-knowledge)
  - [Recommended Learning Order](#recommended-learning-order)
  - [AI Architect's Defining Capability](#ai-architects-defining-capability)

## Overview

**System design** turns requirements into a practical blueprint for building and operating software. It defines the system's structure, components, responsibilities, interfaces, data flow, and interactions.

Design connects user needs with technical decisions. For an online store, this includes how customers search, how orders are saved, what happens when payment is unavailable, and how the service handles a traffic spike.

The goal is to meet today's requirements while making future changes manageable. Good design anticipates bottlenecks and failures, supports expected growth, and balances infrastructure cost with the team's ability to build and operate the system.

> Start with the required behavior and operating conditions. These determine which architecture and mechanisms are useful.

## Core Terminology

| Term | Plain meaning | Example |
| --- | --- | --- |
| **Latency** | How long one operation takes | Time from submitting a search to receiving results |
| **Throughput** | How much work completes per unit of time | Orders processed per second |
| **Availability** | Whether users can access a usable service when needed | The proportion of checkout requests served successfully within an agreed deadline |
| **Scalability** | Ability to handle more work while meeting performance targets | Adding instances as traffic grows |
| **Consistency** | How and when copies of data agree, and what users can read after updates | Whether a profile read can still show the old name after an update |
| **Reliability** | Ability to perform the intended function correctly over time | Orders are recorded correctly despite component failures |
| **Resilience** | Ability to withstand disruption and recover | Restoring service after a region becomes unavailable |
| **Fault tolerance** | Ability to keep providing service when components fail | Remaining instances serve requests after one crashes |
| **Load balancing** | Distributing work across eligible backends | Sending requests to healthy application instances |
| **Caching** | Reusing a stored result to avoid repeating expensive work | Serving a product description from memory |
| **Sharding** | Splitting a dataset across storage nodes using a partition key | Assigning customers to shards by customer ID |
| **Microservices** | Organizing an application into independently deployable services | Separate order, inventory, and notification services |

Latency and throughput measure different things: a system can process many requests per second while individual requests still take a long time. Likewise, a reachable service can return incorrect results, so availability alone does not establish reliability.

See [Distributed System Attributes](Distributed-System-Attributes.md) for deeper explanations, and [Load Balancing and Traffic Distribution](Load-Balancing-and-Traffic-Distribution.md) for routing and backend selection.

## Functional and Non-Functional Requirements

**Functional requirements** describe what the system must do. **Non-functional requirements (NFRs)** describe the quality and operating conditions it must satisfy.

| Aspect | Functional requirements | Non-functional requirements |
| --- | --- | --- |
| Main question | What behavior must the system support? | Under what conditions, and how well must it work? |
| E-commerce examples | Register users, search products, manage a cart, accept payment, track orders | Search latency, peak capacity, availability, access restrictions, recovery targets |
| Verification | Exercise workflows and check their results | Measure behavior under specified load, failures, and security conditions |

Some requirements combine both. Supporting login is a feature; specifying who can access each account's data adds a security constraint. An order workflow also needs explicit correctness rules, such as preventing duplicate charges when a request is retried.

Replace vague statements such as “the system should be fast” with measurable targets. The following are **illustrative requirements**, not universal defaults:

- **Performance:** At 1,000 search requests per second with an agreed dataset and request mix, 95% of responses complete within 200 ms.
- **Availability:** At least 99.9% of valid search requests succeed within the agreed deadline over a calendar month.
- **Security:** A customer can access only their own private order records.
- **Recovery:** After losing an application instance, new requests are routed to healthy instances within 30 seconds.

> Record the target, workload, measurement method, and acceptable failure behavior. Also record constraints such as budget, delivery date, existing integrations, and permitted data locations.

## Design Process

A typical design process includes:

1. **Clarify requirements and constraints** — Define workflows, correctness rules, quality targets, budget, and dependencies.
2. **Estimate the workload** — Estimate normal and peak traffic, concurrent users, data growth, payload sizes, and read/write patterns. Record assumptions.
3. **Sketch the high-level architecture** — Identify components, service boundaries, communication paths, and external integrations.
4. **Design data storage** — Choose data models and access patterns; decide where replication, caching, or partitioning is needed.
5. **Define APIs and user interactions** — Specify contracts, authentication, errors, retries, and how clients receive results.
6. **Work through component details** — Choose algorithms, data structures, concurrency controls, and failure handling.
7. **Evaluate bottlenecks and trade-offs** — Examine slow dependencies, shared resources, single points of failure, cost, and operating complexity.
8. **Validate and revise** — Use prototypes, load tests, failure tests, and production measurements to check the assumptions and targets.

The result includes architecture diagrams, API contracts, data models, and decision records explaining the choices and alternatives considered.

> Design is iterative. A failed load test or a changed requirement can send you back to an earlier decision; revisit assumptions as evidence improves.

## High-Level System Design

High-level design describes the system as a whole. It focuses on major building blocks, how they communicate, how data moves, and how the system handles growth and failures.

Common architecture styles include:

- **Monolithic architecture:** All major functionality is packaged in one application.
- **Client-server architecture:** Clients request data or services from one or more centralized servers.
- **Microservices architecture:** The system is divided into independently deployable (modular) services.
- **Event-driven architecture:** Components communicate through events or asynchronous messages.

Choosing an architecture requires balancing several concerns:

- **Scalability:** Can the system support more users, traffic, data, and features?
- **Maintainability:** Can teams easily understand, test, debug, modify, improve, and operate it safely?
- **Reliability:** Does it keep performing its intended functions correctly, including during specified failures?
- **Performance:** Can it meet latency and throughput expectations?
- **Complexity:** Are the operational and development costs justified?

### Data Flow

Data flow describes how information moves through a system:

- **Ingestion:** Identify the sources of data and the mechanisms of how the data enters into the system - through APIs, events, files, streams, or batch jobs.
- **Processing:** Define how data is validated, transformed, aggregated, or analyzed.
- **Storage:** Data is saved in a storage system suited to its structure, query performance and access patterns.
- **Retrieval:** Clients and services access data through suitable queries, indexes, caches, and routing strategies.

Good data-flow design reduces bottlenecks and supports the required performance, consistency, and user experience.

### Scalability

Scalability is the ability to handle increasing demand without unacceptable performance loss.

- **Vertical scaling** adds CPU/GPU, memory, or storage to an existing machine.
- **Horizontal scaling** spreads work across additional machines or service instances.

> Horizontal scaling usually offers greater long-term capacity and fault isolation, but it also introduces distributed-system complexity. Load balancing, stateless services, caching, replication, and data partitioning are common scaling techniques.

Measure which resource limits capacity before adding instances. A shared database, hot shard, or external API can remain the bottleneck. See [Scalability](Distributed-System-Attributes.md#scalability) and [Autoscaling with Load Balancing](Load-Balancing-and-Traffic-Distribution.md#autoscaling-with-load-balancing).

### Fault Tolerance

Fault tolerance allows a system to continue providing useful service when components fail. Common techniques include:

- Replication and redundancy
- Graceful degradation
- Health checks and monitoring
- Automatic failover and recovery
- Isolation of failing components

Failures are normal in production systems, so recovery behavior should be part of the design rather than an afterthought.

Specify what happens to in-flight work, whether retries are safe, and how recovery is tested. See [Fault Tolerance](Distributed-System-Attributes.md#fault-tolerance) for the detection, containment, and recovery process.

## Low-Level System Design

Low-level design focuses on how individual components are implemented. It covers classes, modules, algorithms, data structures, APIs, and internal control flow.

### Algorithms

> Algorithms are the step-by-step procedures for performing calculations, data processing, and problem-solving.

Algorithm choice affects execution time, memory use, and scalability. Important considerations include:

- **Time complexity**: The relationship between the input size and the number of operations the algorithm performs - `O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2ⁿ), O(n!)`.
- **Space complexity**: The relationship between the input size and the amount of memory the algorithm consumes - `O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2ⁿ), O(n!)`.
- **Trade-offs**: The balance between time and space complexity, depending on the system’s requirements and constraints *(between speed, memory, and implementation complexity)*.

> Efficient algorithms can often improve performance more effectively than simply adding hardware. 

Examples of common algorithms are *binary search, sorting, shortest path, hashing, caching algorithms*.

### Data Structures

Data structures determine how efficiently data can be stored and accessed. The right choice depends on:

- Read, write, and update patterns
- Search, insertion, and deletion costs (time complexity)
- Ordering requirements
- Memory usage

Common options include arrays, linked lists, hash tables, trees, graphs, queues, and heaps.

### API Design

APIs define how components communicate and help keep modularity by separating responsibilities. A well-designed API should be:

- **Consistent:** Similar operations follow predictable conventions.
- **Clear:** Inputs, outputs, errors, and behavior are easy to understand.
- **Flexible:** The interface can evolve without unnecessarily breaking existing functionality.
- **Secure:** Authentication, authorization, and input validation are built in.
- **Efficient:** Requests use resources carefully and meet performance needs (e.g., optimized for low latency).

Stable API contracts make systems easier to integrate and evolve while preserving backward compatibility. Define how clients handle timeouts and retries, especially for operations that change data.

### Code Optimization

Optimization should target measured bottlenecks while preserving correctness and readability. Useful techniques include:

- **Refactoring** unclear or inefficient code by restructuring it to improve its readability and maintainability without changing its functionality
- **Memoization:** Reuse stored results of repeated computations when their inputs and relevant state have not changed
- **Parallelizing** independent work where appropriate by breaking down tasks into smaller, independent subtasks that can be executed concurrently, reducing overall processing time
- **Loop unrolling** by replacing repetitive loop structures with a series of statements, reducing loop overhead and improving performance
- Reducing unnecessary allocations, queries, and network calls
- Selecting better algorithms and data structures

Optimization can add complexity or memory use, so changes should be guided by profiling and real system requirements.

## Design Challenges and Trade-Offs

### Common Challenges

- **Partial failures:** One service may fail while others remain healthy. A timeout does not tell the caller whether a remote write completed.
- **Data synchronization:** Replicas can lag and concurrent writes can conflict. Define which operations require fresh data and which can tolerate stale reads.
- **Bottlenecks:** Slow queries, overloaded queues, hot keys, and network calls can limit the whole request path.
- **Security and data handling:** Enforce identity, authorization, encryption, retention, and applicable data-location requirements across services.
- **Operating cost and complexity:** Extra services, replicas, and regions require money, monitoring, deployment work, and recovery procedures.

Use the consistency model that matches each operation. With **strong consistency**, a read started after a successful write sees that write or a newer one. With **eventual consistency**, replicas may temporarily differ and converge when updates stop and replication completes.

**Partition tolerance** concerns behavior when groups of nodes cannot communicate; it is not another consistency model. See [Partition Tolerance](Distributed-System-Attributes.md#partition-tolerance) for the consistency and availability choices during a partition.

### Evaluating Trade-Offs

| Decision | Benefit | Cost or risk | Example |
| --- | --- | --- | --- |
| Serve reads from a cache | Lower latency and less database work | Stale data and invalidation complexity | Cache product descriptions; recheck price and stock at checkout |
| Wait for replica acknowledgements before confirming a write | More copies have the update when success is returned | More coordination and write latency; unreachable replicas may block progress | Confirm a reservation only after the required persistence and coordination steps |
| Add redundant instances or regions | Survive more component failures | Infrastructure cost, replication, and operational work | Keep spare capacity to absorb an instance failure |
| Shard a growing dataset | Distribute storage and processing | Rebalancing, hot shards, and cross-shard operations | Partition customer records by a suitable key |
| Move work to a queue | Absorb bursts and shorten the initial response | Delayed completion and retry/deduplication logic | Send confirmation emails after an order commits |
| Run close to full capacity | Reduce idle-resource cost | Less room for bursts or failures | Choose a utilization target with recovery headroom |

These outcomes depend on the implementation and workload. Replication or caching can sometimes improve both speed and resilience; scalability does not automatically require weaker consistency.

> For each major decision, record the requirement it satisfies, the alternatives considered, the cost it introduces, and the evidence that would justify revisiting it.

## Key Takeaway

- **Requirements define success:** Specify features, correctness rules, and measurable operating targets.
- **HLD organizes the system:** Choose components, data flow, communication, and deployment boundaries.
- **LLD makes components concrete:** Define APIs, schemas, algorithms, and behavior under concurrency and failure.
- **Trade-offs need a reason:** Relate each choice to the workload, cost, risk, and team constraints.
- **Validation closes the loop:** Measure the design against its targets and revise it when assumptions change.

## System Design vs. Software Architecture

They overlap heavily, but **system design is broader**.

- **Software architecture** = the system’s **high-level structure and major technical decisions**.
- **System design** = the **full design process**, including architecture plus lower-level details such as APIs, databases, caching, queues, algorithms, failure handling, etc.

**Example — e-commerce system:**

Architecture might decide:

> Web app → API Gateway → Order Service / Payment Service / Inventory Service → databases

System design goes further:

> How does `Order Service` work? What API does it expose? Which DB schema? How are transactions handled? What happens if payment succeeds but inventory fails? How is caching implemented?

A useful mental model:

**System Design**  
→ **High-Level Design / Software Architecture**  
→ **Low-Level Design / Implementation details**

So, **software architecture is largely the high-level part of system design**, not a completely separate discipline.

## System Design & Deployment Infra, Ops, Networking

**System design includes deployment infrastructure, networking, reliability, observability, and operational concerns** at the architectural level.

DevOps/network engineers usually handle the **deeper implementation and operation**.

So:

- **System designer/architect:** decides what infrastructure/networking is needed and why.
- **DevOps/network engineer:** implements, configures, automates, and operates it.

## System Design vs. Solution Architecture

System design and solution architecture overlap significantly, but they are not exactly the same. The main difference is their scope and level of abstraction.

| Aspect | System Design | Solution Architecture |
| --- | --- | --- |
| Focus | How a system is designed and implemented | How multiple systems and technologies work together to solve a business problem |
| Scope | Individual systems and their internal components | End-to-end solution across systems and services |
| Key decisions | APIs, databases, algorithms, caching, scalability, and reliability | Technology selection, integrations, security, infrastructure, and architectural trade-offs |
| Output | System architecture, component designs, API specifications | Solution architecture diagrams, technology choices, integration strategies |

### Example: E-commerce platform

Solution architecture defines how the entire solution works together: the storefront, payment gateway, inventory system, CRM, cloud infrastructure, and external integrations.

System design defines how individual systems work internally: order processing, database schemas, APIs, caching strategies, and communication between services.

> By "individual systems," here I mean the subsystems or components that make up the overall e-commerce solution, such as the storefront, order management, inventory management, and payment processing systems.

The distinction depends on their scope and implementation:

* **Solution architecture**: Defines how these subsystems fit together, their responsibilities, integrations, and technology choices.

* **System design**: Defines how each subsystem is designed internally, including its components, APIs, data models, algorithms, and internal workflows.

> **Important distinction**: If a subsystem is developed internally, its internal architecture and implementation must be designed. If it is a third-party product (e.g., an external payment gateway or CRM), the focus is typically on selecting, configuring, and integrating it rather than designing its internals.

Therefore, system design can be performed at the subsystem level, while solution architecture addresses the end-to-end solution. However, both disciplines can operate at multiple levels of abstraction.


### Key takeaway

* **Solution architecture**: What systems and technologies are needed, how they integrate, and why.

* **System design**: How those systems and their components should be designed and implemented.

> In practice, the responsibilities often overlap. A solution architect may perform system design, and a system designer may make solution-level architectural decisions.


## Levels of Architecture: System Design vs. Solution Architecture vs. Enterprise Architecture

There is a natural progression from system design to solution architecture and then enterprise architecture. However, these disciplines overlap, and the distinction is primarily about scope and responsibilities, not strictly technical depth.

### 1. Abstraction levels of architecture

**Highest abstraction - Enterprise Architecture**

- Aligns business strategy, processes, applications, data, and technology across the entire organization.  

**Higher abstraction - Solution Architecture**

- Designs an end-to-end solution to a business problem, defining the required systems, technologies, integrations, and architectural decisions.

**More detailed design - System Design**

- Designs individual systems and their internal components, including APIs, databases, algorithms, data structures, and communication patterns.
  
This is a useful conceptual hierarchy, although real-world responsibilities often overlap.

### 2. Recommended learning progression

1. System Design (HLD + LLD)

    - Understand how to design, implement, scale, and maintain software systems.

2. Solution Architecture

    - Learn how to combine systems, technologies, infrastructure, and integrations into complete business solutions.

3. Enterprise Architecture

    - Learn how to align the organization's overall technology landscape with its business capabilities, strategy, and long-term objectives.

**Important**: System design is not exclusively lower-level. High-Level Design (HLD) involves architectural decisions that overlap significantly with solution architecture. Also, solution architecture is not necessarily less technical. It often requires deep expertise in distributed systems, cloud infrastructure, security, integration, and scalability.

**Bottom line**: Studying system design first is a sensible path for a software engineer. Solution architecture builds on those technical foundations while expanding the scope to business requirements and end-to-end solutions. Enterprise architecture extends that scope to the organization as a whole.

## AI Architect Knowledge Map

An **AI Architect** needs deep system design and solution architecture skills, combined with AI expertise and working knowledge of the engineering disciplines that support production AI systems.

> The objective is not to become an expert in every discipline. It is to understand how the disciplines fit together, identify the important trade-offs, and make sound architectural decisions.

### Complete Knowledge Map

<div style="border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; margin: 1rem 0;">
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/1-core-foundation.png" alt="1. Core foundation"><br>
    <strong>Software Engineering &amp; System Design</strong><br><br>
    Algorithms, data structures, APIs, databases, networking, LLD, HLD, distributed systems, scalability, reliability, security, and software design patterns.
  </div><br>
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/2-core-architecture.png" alt="2. Core architecture"><br>
    <strong>Solution Architecture</strong><br><br>
    Requirements analysis, architectural patterns, technology selection, system integration, cloud architecture, cost optimization, and architectural trade-offs.
  </div><br>
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/3-ai-expertise.png" alt="3. AI expertise"><br>
    <strong>AI &amp; Machine Learning</strong><br><br>
    Machine learning, deep learning, model architectures and internals, transformers, LLMs, training, fine-tuning, RAG, agentic AI, multimodal AI, and model evaluation.
  </div><br>
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/4-data-foundation.png" alt="4. Data foundation"><br>
    <strong>Data Architecture &amp; Data Engineering</strong><br><br>
    Data modeling, data pipelines, ETL/ELT, data warehouses, data lakes, lakehouses, streaming, vector databases, data quality, governance, and data lifecycle management.
  </div><br>
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/5-infrastructure-and-operations.png" alt="5. Infrastructure and operations"><br>
    <strong>Cloud, DevOps, MLOps &amp; LLMOps</strong><br><br>
    Cloud infrastructure, containers, Kubernetes, CI/CD, infrastructure as code, model deployment, model registries, monitoring, observability, experiment tracking, and automated evaluation.
  </div><br>
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/6-ai-production-systems.png" alt="6. AI production systems"><br>
    <strong>Inference Engineering</strong><br><br>
    Model serving, inference optimization, batching, quantization, caching, GPU resource management, throughput, latency, and inference cost optimization.
  </div><br>
  <div style="padding: 14px 12px; border-bottom: 1px solid #e5e7eb;">
    <img src="assets/ai-architect-knowledge-map/7-cross-cutting-responsibilities.png" alt="7. Cross-cutting responsibilities"><br>
    <strong>Security, Governance &amp; Responsible AI</strong><br><br>
    Data privacy, access control, threat modeling, prompt-injection defense, model and data security, AI safety, regulatory requirements, and AI governance.
  </div><br>
  <div style="padding: 14px 12px;">
    <img src="assets/ai-architect-knowledge-map/8-business-and-leadership.png" alt="8. Business and leadership"><br>
    <strong>Business &amp; Architectural Decision-Making</strong><br><br>
    Business requirements, stakeholder communication, feasibility assessment, build-versus-buy decisions, cost-benefit analysis, technical leadership, documentation, and architectural decision records.
  </div>
</div>

### Required Depth of Knowledge

Not every subject requires the same level of expertise.

| Discipline | Expected proficiency |
| --- | --- |
| **System Design & Solution Architecture** | **Deep** |
| **AI/ML, LLMs, RAG & Agents** | **Deep** |
| Data Architecture & Engineering | Strong working knowledge |
| Cloud, DevOps, MLOps & LLMOps | Strong working knowledge |
| Inference Engineering | Strong working knowledge; deeper for model-serving roles |
| Security, Governance & Responsible AI | Strong working knowledge |
| **Business & Architectural Decision-Making** | **Deep** |

For example:

- An AI Architect should understand how to design a scalable data pipeline without necessarily implementing every data-engineering component.
- Understanding model training and fine-tuning trade-offs is essential, but most AI Architect roles do not require building foundation models from scratch.

### Recommended Learning Order

For someone who already has an AI or data-science background:

1. **System Design — LLD and HLD**
   - Build foundations in software architecture, distributed systems, scalability, reliability, and security.
2. **Data Architecture and Cloud Engineering**
   - Understand data platforms, pipelines, cloud services, infrastructure, and system integration.
3. **DevOps, MLOps, and LLMOps**
   - Learn how AI systems are deployed, monitored, evaluated, and maintained in production.
4. **Inference Engineering and AI System Architecture**
   - Design end-to-end AI systems involving model serving, orchestration, retrieval, evaluation, and performance optimization.
5. **Solution Architecture**
   - Expand from individual AI systems to complete business solutions involving requirements, integrations, technology selection, cost, and architectural trade-offs.

> Solution architecture can be studied alongside system design; these disciplines are complementary rather than strictly sequential.

### AI Architect's Defining Capability

The knowledge areas above form a comprehensive technical foundation. The additional competencies that must remain explicit are **security**, **AI governance**, **business requirements**, **architectural decision-making**, and **stakeholder communication**.

> **Bottom line:** An AI Architect is defined not by knowing every technology in depth, but by the ability to translate business requirements into secure, reliable, scalable, and cost-effective AI solutions—and to justify the architectural decisions behind them.
