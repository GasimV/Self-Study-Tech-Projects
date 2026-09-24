# Understanding System Design

## Table of Contents

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
- [Key Takeaway](#key-takeaway)
- [System Design vs. Solution Architecture](#system-design-vs-solution-architecture)
  - [Example: E-commerce platform](#example-e-commerce-platform)
  - [Key takeaway](#key-takeaway-1)

System design is the process of turning requirements into a practical blueprint for building and operating software. It defines the system's structure, major components, responsibilities, interfaces, data flow, and interactions.

A strong design should satisfy both:

- **Functional requirements:** what the system must do.
- **Non-functional requirements:** how well it must perform, including scalability, reliability, security, latency, and maintainability.

The goal is not only to make a system work today. The design should also be understandable, adaptable, and able to support future changes in traffic, data, features, and infrastructure.

## Design Process

A typical system design process includes:

1. **Analyze requirements** — Clarify features, constraints, expected traffic, data volume, and read/write patterns.
2. **Design the high-level system architecture** — Identify the main components, services, interfaces, and communication paths.
3. **Design the low-level component details** — Decide how each component behaves internally and how components coordinate.
4. **Design APIs** — Define clear contracts between clients, services, and external systems.
5. **Design data storage** — Choose suitable data models and storage technologies based on access patterns, consistency, and scale.
6. **Consider the user interaction** — Outline how the frontend communicates with backend services.

The result is a set of architectural design documents consisting of architecture diagrams, API contracts, data models, and design decisions that serve as a blueprint for implementation.

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
- **Reliability:** Can it remain available and recover from failures (fault tolerance, resilience, etc.)?
- **Performance:** Can it meet latency and throughput expectations?
- **Complexity:** Are the operational and development costs justified?

### Data Flow

Data flow describes how information moves through a system:

- **Ingestion:** Identify the sources of data and the mechanisms of how the data enters into the system - through APIs, events, files, streams, or batch jobs.
- **Processing:** Deigning the processes that validate, transform, aggregate, or analyze the data.
- **Storage:** Data is saved in a storage system suited to its structure, query performance and access patterns.
- **Retrieval:** Clients and services access the processed data with suitable caching, latency, and routing/load balancing strategies.

Good data-flow design reduces bottlenecks and supports the required performance, consistency, and user experience.

### Scalability

Scalability is the ability to handle increasing demand without unacceptable performance loss.

- **Vertical scaling** adds CPU/GPU, memory, or storage to an existing machine.
- **Horizontal scaling** spreads work across additional machines or service instances.

> Horizontal scaling usually offers greater long-term capacity and fault isolation, but it also introduces distributed-system complexity. Load balancing, stateless services, caching, replication, and data partitioning are common scaling techniques.

### Fault Tolerance

Fault tolerance allows a system to continue providing useful service when components fail. Common techniques include:

- Replication and redundancy
- Graceful degradation
- Health checks and monitoring
- Automatic failover and recovery
- Isolation of failing components

Failures are normal in production systems, so recovery behavior should be part of the design rather than an afterthought.

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

Stable API contracts make systems easier to integrate, maintain, and evolve by enabling building the backward-compatible systems.

### Code Optimization

Optimization should target measured bottlenecks while preserving correctness and readability. Useful techniques include:

- **Refactoring** unclear or inefficient code by restructuring it to improve its readability and maintainability without changing its functionality
- **Memorizing** expensive repeated computations by storing the results of previous calls
- **Parallelizing** independent work where appropriate by breaking down tasks into smaller, independent subtasks that can be executed concurrently, reducing overall processing time
- **Loop unrolling** by replacing repetitive loop structures with a series of statements, reducing loop overhead and improving performance
- Reducing unnecessary allocations, queries, and network calls
- Selecting better algorithms and data structures

Optimization always involves trade-offs. More performance may add complexity, so changes should be guided by profiling and real system requirements. This is the *broad topic* which has dedicated books to it.

## Key Takeaway

High-level and low-level design solve different parts of the same problem. High-level design explains how the system is organized and operates at scale, while low-level design explains how its individual components are implemented. Effective system design connects both views and makes deliberate trade-offs based on requirements, constraints, and expected change.


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

### Key takeaway

* Solution architecture: What systems and technologies are needed, how they integrate, and why.

* System design: How those systems and their components should be designed and implemented.

In practice, the responsibilities often overlap. A solution architect may perform system design, and a system designer may make solution-level architectural decisions.
