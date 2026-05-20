# GenAI on Kubernetes Study Notes

## Contents

1. [Purpose](#purpose)
2. [KServe](#kserve)
   - [Deployment Modes](#deployment-modes)
   - [Core APIs](#core-apis)
   - [From `InferenceService` to `LLMInferenceService`](#from-inferenceservice-to-llminferenceservice)
   - [Why Runtime and Model Separation Matters](#why-runtime-and-model-separation-matters)
3. [GPU Sharing and Sub-GPU Allocation](#gpu-sharing-and-sub-gpu-allocation)
   - [Time Slicing](#time-slicing)
   - [MPS](#mps)
   - [MIG](#mig)
4. [Current State and Gaps in Model Portability](#current-state-and-gaps-in-model-portability)
5. [Model Registry](#model-registry)
   - [Hugging Face Model Hub](#hugging-face-model-hub)
   - [MLflow Model Registry](#mlflow-model-registry)
   - [Kubeflow Model Registry](#kubeflow-model-registry)
   - [OCI](#oci)
     - [Registry](#registry)
     - [Images](#images)
6. [Accessing Model Data in Kubernetes](#accessing-model-data-in-kubernetes)
   - [KServe `storageUri` and Storage Initializers](#kserve-storageuri-and-storage-initializers)
   - [Built-in KServe Storage Initializers](#built-in-kserve-storage-initializers)
   - [Shared Storage with PersistentVolumes](#shared-storage-with-persistentvolumes)
7. [Running in Production](#running-in-production)
   - [Model and Runtime Tuning](#model-and-runtime-tuning)
   - [Language Model Evaluation](#language-model-evaluation)
   - [Language Model Compression](#language-model-compression)
   - [Model Performance Benchmark](#model-performance-benchmark)
   - [vLLM Runtime Parameters Tuning](#vllm-runtime-parameters-tuning)
   - [Autoscaling](#autoscaling)
   - [Optimize vLLM Startup Time](#optimize-vllm-startup-time)
   - [LLM-Aware Routing](#llm-aware-routing)
   - [Disaggregated Serving](#disaggregated-serving)
   - [Lessons Learned](#lessons-learned)
8. [High-Value Recall Checklist](#high-value-recall-checklist)

## Purpose

These notes are structured for **elaborative encoding**, **active recall**, and **future reuse**.

Focus on:

- **What each concept is**
- **Why it exists**
- **When to use it**
- **How it connects to Kubernetes, MLOps, and production AI systems**

<u>Core rule:</u> do not just memorize definitions; **remember the operational reason behind each tool or API**.

[Back to Contents](#contents)

## KServe

**KServe** is a **CNCF project** for **model inference on Kubernetes**.

Its job is to help manage the **lifecycle**, **deployment**, and **exposure** of model-serving endpoints using Kubernetes-native patterns.

### What KServe gives you

- **Scalability**
- **Routing**
- **Canary rollout**
- **Density packing**
- **Declarative model serving**

### Historical context

- Originally created as **KfServing** in the **Kubeflow** community
- Later became an **independent project**
- Still remains part of the broader **Kubeflow ecosystem**
- First focused on **predictive AI**
- Later evolved to support **generative AI**

### Key idea to remember

**KServe extends Kubernetes with custom APIs for model serving.**

That means model serving becomes a **declarative Kubernetes problem**, not just an application container problem.

### Encode this

- **KServe = Kubernetes-native model inference platform**
- **Predictive AI first, generative AI later**
- **Uses CRDs to represent serving concepts declaratively**

### Recall prompt

*Why is KServe more than just "running a model in a container"?*

[Back to Contents](#contents)

### Deployment Modes

KServe supports **three deployment modes**:

1. **Knative**
2. **Standard**
3. **ModelMesh**

#### 1. Knative

**Knative** is the most feature-rich mode.

It uses **Knative** and **Istio** for:

- **Autoscaling**
- **Rolling updates**
- **Traffic management**
- **Composition**

In this mode, each model becomes a **KnativeService**.

**Best mental model:** KServe delegates much of the dynamic serving behavior to the Knative ecosystem.

#### 2. Standard

**Standard** is the simplest and most Kubernetes-direct mode.

It adds **no extra major dependency** beyond Kubernetes primitives. For each model, KServe creates a **Deployment**.

This is usually the most practical choice for **LLM serving**, especially when GPUs are **dedicated and statically allocated**.

**KServe 0.16 note:**

- `RawDeployment` was renamed to **Standard**
- `Serverless` was renamed to **Knative**

#### 3. ModelMesh

**ModelMesh** is optimized for **high-density serving** where **many models** must share cluster resources.

The model server can **load and unload models dynamically** based on requests.

This is useful when:

- You need to serve **many small or medium models**
- Running one deployment per model is too expensive

This is **generally not a fit for large generative AI models**, because large LLMs are too heavy to pack densely on the same nodes.

#### Best practical takeaway

For **modern LLM workloads**:

- **Standard** is often the default practical choice
- **Knative** can help for smaller models and elastic patterns
- **ModelMesh** is usually not the right match for large LLMs

#### Encode this

- **Knative = dynamic, feature-rich, extra stack**
- **Standard = simple, direct, deployment-per-model**
- **ModelMesh = many models, dense sharing**

#### Recall prompt

*Why does Standard often make more sense than Knative for production LLMs on GPUs?*

[Back to Contents](#contents)

### Core APIs

The two main APIs to remember are:

1. **`ServingRuntime`**
2. **`InferenceService`**

#### `ServingRuntime`

A **`ServingRuntime`** is basically a **model server template**.

It defines:

- The **container image**
- Startup **arguments**
- The type of **model formats** it supports
- Runtime-level defaults and behavior

This separates **runtime configuration** from **model configuration**.

There is also **`ClusterServingRuntime`**, which makes a runtime available cluster-wide.

#### What to remember

**`ServingRuntime` describes how to serve.**

Not the specific model itself, but the **runtime environment** that can serve models.

#### Example idea

For vLLM, a `ServingRuntime` can define:

- `image: vllm/vllm-openai:latest`
- exposed port
- startup arguments like `--model` and `--port`
- support for `pytorch` models

#### `InferenceService`

An **`InferenceService`** represents the **actual model deployment** the user wants to serve.

It defines:

- The **model format**
- The **runtime** to use
- The **model location**
- Per-model **resource overrides**
- The deployment behavior

When this resource is created, KServe deploys the model server and wires the model to it.

#### What to remember

**`InferenceService` describes what to serve.**

This is the object that points to the model and triggers actual serving.

#### Useful mapping

- **`ServingRuntime` = server template**
- **`InferenceService` = model serving instance**

#### Minimal mental model

Platform team:

- Owns **runtime images**, defaults, and serving stack choices

Model or application team:

- Owns **which model gets deployed**, where it lives, and model-specific resources

#### Other useful KServe concepts

KServe also supports:

- **Inference logging**
- **Preprocessing and postprocessing**
- **InferenceGraph** for model composition
- **Storage initializer** for downloading model files into the serving container
- **ClusterStorageContainer** for custom storage-loading behavior

#### Encode this

- **`ServingRuntime` = how**
- **`InferenceService` = what**
- **Storage initializer = fetches model artifacts before serving**

#### Recall prompt

*If you want to upgrade the model server image without changing the model itself, which resource concept matters most?*

[Back to Contents](#contents)

### From `InferenceService` to `LLMInferenceService`

KServe 0.16 introduced **`LLMInferenceService`**, a new CRD designed specifically for **large-scale LLM deployments**.

This exists because traditional `InferenceService` is sufficient for **basic serving**, but not ideal for **advanced LLM production topologies**.

#### Why `LLMInferenceService` exists

Large LLM systems often need:

- **Intelligent routing**
- **KV cache-aware scheduling**
- **Disaggregated serving**
- **Multinode distributed inference**
- **Parallelism across multiple GPUs**

These needs go beyond basic model serving.

#### Related config object

KServe also adds **`LLMInferenceServiceConfig`**, which acts like a **base configuration template**.

It can define shared settings such as:

- Container image
- Runtime arguments
- Resource defaults
- Router settings
- Parallelism settings

Then **`LLMInferenceService`** references that config and can override selected values.

#### Important implementation detail

`LLMInferenceService` uses **Standard deployment mode** under the hood.

That reflects an important shift:

**LLM workloads prioritize stability, predictability, and intelligent routing over fast scale-to-zero style elasticity.**

#### Key capabilities

- **Gateway / router / scheduler**
- **KV cache-aware scheduling**
- **Tensor parallelism**
- **Data parallelism**
- **Expert parallelism**
- **Horizontal replicas**

#### Simple comparison

**Traditional path**

- `ServingRuntime` + `InferenceService`
- Better for general model serving and predictive AI

**New LLM path**

- `LLMInferenceServiceConfig` + `LLMInferenceService`
- Better for advanced generative AI serving

#### Encode this

- **`InferenceService` works for basic LLM serving**
- **`LLMInferenceService` exists for complex LLM production patterns**
- **The new API is about routing, scheduling, and distributed inference**

#### Recall prompt

*What production problems does `LLMInferenceService` solve that `InferenceService` does not solve well enough?*

[Back to Contents](#contents)

### Why Runtime and Model Separation Matters

One of the most important operational ideas in these notes is the separation between:

- **Runtime lifecycle**
- **Model lifecycle**

#### Why this matters

These two things change on **different schedules** and are owned by **different teams**.

#### Runtime lifecycle examples

- Upgrading vLLM or TGI versions
- Changing container images
- Adjusting default server startup parameters
- Updating infrastructure assumptions

#### Model lifecycle examples

- Releasing a new model version
- Changing quantization
- Updating weights
- Rolling back to a previous validated model

#### Operational benefit

This separation allows:

- **Platform teams** to manage runtimes safely
- **Model teams** to iterate independently
- Fewer ownership conflicts
- Cleaner production workflows

#### Broader serving context

Model servers such as **vLLM**, **TGI**, and **SGLang** matter because they provide performance-critical optimizations like:

- **PagedAttention**
- **FlashAttention**
- **Continuous batching**

These are essential for real throughput and latency, especially on GPUs.

#### KServe versus Ray

The trade-off is philosophical as much as technical:

- **KServe** is **Kubernetes-native**
- **Ray** is more **Python-first**

KServe feels more familiar to platform operators because it maps closely to Kubernetes concepts.

Ray offers stronger built-in distributed serving ergonomics, but introduces its own orchestration layer, which can complicate operations and debugging.

#### Encode this

- **Separation of runtime and model reflects real ownership boundaries**
- **Specialized model servers are required for production efficiency**
- **KServe vs Ray = Kubernetes-native vs Python-first orchestration**

#### Recall prompt

*Why is separating runtime management from model management an operational advantage rather than just a design preference?*

[Back to Contents](#contents)

## GPU Sharing and Sub-GPU Allocation

The **NVIDIA GPU Operator** supports advanced GPU features for **partitioning** or **slicing** a single GPU across multiple workloads.

This may not always be central for operating very large LLMs, because many LLMs need most or all of a GPU's memory. Still, it is important to understand because GPU sharing can improve utilization for **inference**, **small models**, **interactive notebooks**, and **bursty workloads**.

The core GPU sharing concepts to distinguish are:

1. **Time slicing**
2. **MPS**
3. **MIG**

### Time Slicing

**Time slicing** allows multiple containers to share one physical GPU by allocating **time-based slices**.

By default, if a pod requests:

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

Kubernetes grants that pod **exclusive access** to one physical GPU.

Time slicing changes the scheduling model by allowing **GPU oversubscription**. The NVIDIA device plug-in can advertise multiple virtual GPU replicas for each real GPU. For example, one physical GPU can be represented as four or eight schedulable GPU devices.

That means several pods can each request what looks like one GPU, while actually sharing the same hardware.

**Time slicing** means several workloads **take turns using the same hardware**.

Imagine one GPU as a single classroom projector.

Without time slicing:

```text
Pod A gets the projector.
Pod B must wait.
Pod C must wait.
```

With time slicing:

```text
Pod A uses the GPU for a tiny moment
then Pod B uses it
then Pod C uses it
then back to Pod A
```

It happens very fast, so it looks like they are sharing the GPU at the same time.

CPU time slicing is similar:

```text
One CPU core
-> runs browser for a moment
-> runs music app for a moment
-> runs terminal for a moment
-> repeats quickly
```

GPU time slicing:

```text
One physical GPU
-> serves model A request
-> serves model B request
-> serves model C request
-> repeats quickly
```

#### CPU comparison: cores, logical processors, and time slicing

CPU scheduling is a related concept, but **CPU logical processors** and **time slicing** are not exactly the same thing.

A CPU has **physical cores** and may also expose **logical processors** through **hyper-threading** or **Simultaneous Multithreading (SMT)**.

Example:

```text
CPU: 8 physical cores
Hyper-threading: 2 logical processors per core
OS sees: 16 logical CPUs
```

The OS scheduler can place work on those 16 logical CPUs. But two logical CPUs on the same physical core still share the same execution resources, so they are **not equal to two full physical cores**.

Time slicing is slightly different:

```text
Logical CPU / hyper-threading:
two hardware threads share one physical core at the same time

Time slicing:
many processes take turns using a CPU core over time
```

The analogy:

```text
Physical core = real hardware
Logical CPU = hardware-exposed shared execution slot
Time slicing = scheduler rapidly switches workloads on the hardware
```

For GPUs, time slicing is closer to saying:

```text
One real GPU is advertised as multiple schedulable "GPU slots,"
but those slots still share the same physical GPU.
```

Think of a **physical CPU core** like **one cashier**.

##### 1. Time slicing: one cashier, many customers taking turns

There is **one cashier** and **five customers**.

The cashier serves:

```text
Customer A for 10 seconds
Customer B for 10 seconds
Customer C for 10 seconds
Customer D for 10 seconds
Customer E for 10 seconds
then back to Customer A
```

Each customer feels like they are "being served," but actually they are **taking turns**.

That is **time slicing**.

##### 2. Multiple physical cores: many real cashiers

Now there are **four cashiers**.

```text
Cashier 1 serves Customer A
Cashier 2 serves Customer B
Cashier 3 serves Customer C
Cashier 4 serves Customer D
```

This is real parallel work. More work can happen at the same time.

That is like **four physical CPU cores**.

##### 3. Logical processors / hyper-threading: one cashier with two order windows

Now imagine **one cashier has two windows**.

```text
Window 1: Customer A
Window 2: Customer B
```

But behind both windows, it is still **one cashier**.

The cashier can stay busier because when Customer A is waiting for payment approval, the cashier can help Customer B. But the cashier did not become two full cashiers.

That is like **one physical core with two logical processors**.

##### Simple summary

```text
Physical core:
a real worker

Logical processor:
an extra lane/window into the same worker

Time slicing:
many tasks taking turns with the worker
```

For GPU time slicing, imagine:

```text
1 physical GPU = 1 big machine

Kubernetes advertises it as:
gpu-slot-1
gpu-slot-2
gpu-slot-3
gpu-slot-4
```

But underneath, all four slots still use the **same physical GPU**, taking turns.

#### What time slicing gives you

- Better GPU utilization when workloads are **small**, **bursty**, or **idle** part of the time
- Ability to run several lightweight inference workloads on one GPU
- Sharing support for older GPUs that do **not** support MIG, such as some **T4** or **V100** environments
- Higher overall throughput when individual workloads do not need full GPU capacity all the time

#### Important trade-off

Time-sliced workloads are **not getting full GPU power at the same time**.

If all pods become busy, each pod gets slower because they are sharing the same physical GPU.

<u>Key limitation:</u> time slicing provides **compute-time sharing**, not strong isolation.

Unlike MIG, time slicing does **not** provide:

- GPU memory isolation
- Fault isolation
- Dedicated memory quotas
- Guaranteed full-GPU performance

All pods sharing the same physical GPU can access the same GPU memory pool. If one pod allocates most of the GPU memory, other pods may fail to allocate memory. If one process causes a GPU reset, the other workloads sharing that GPU can also be affected.

#### Example configuration for time slicing

To enable GPU time slicing, configure the NVIDIA device plug-in through a `ConfigMap` referenced by the GPU Operator configuration.

Example configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gpu-sharing-config
  namespace: gpu-operator-resources
data:
  sharing: |
    version: v1
    sharing:
      timeslicing:
        renameByDefault: true
        resources:
        - name: nvidia.com/gpu
          replicas: 8
```

Important fields:

- **`renameByDefault: true`** renames the shared resource from `nvidia.com/gpu` to `nvidia.com/gpu.shared`.
- **`replicas: 8`** exposes eight schedulable GPU units for each physical GPU.
- **`resources.name`** controls which GPU resource is oversubscribed.

For one physical GPU, `replicas: 8` exposes eight virtual GPU units. For ten physical GPUs, the node can advertise eighty virtual GPU units.

The node may also receive a label such as:

```text
gpu.replicas=8
```

This marks the oversubscription level.

#### Scheduling warning

A pod requesting multiple time-sliced GPUs does **not** get twice the performance of a single shared GPU.

For example:

```yaml
resources:
  limits:
    nvidia.com/gpu: 2
```

In shared mode, this usually gives the pod shares on two separate physical GPUs, each still shared with other workloads. That is rarely useful and can confuse users into thinking they received two full GPUs.

For this reason, the device plug-in can be configured to reject requests for more than one GPU in shared mode.

<u>Practical rule:</u> time slicing is intended for pods that request exactly **one** GPU, where that "one GPU" really means **one shared slice** of a physical GPU.

For multi-GPU workloads, keep GPUs **exclusive** or use **MIG** where appropriate.

#### Best fit

Time slicing is useful when:

- You have many small inference tasks
- You serve multiple lightweight models
- You run interactive notebooks
- Workloads are bursty and often idle
- The models collectively fit in GPU memory
- The GPU does not support MIG

Time slicing is often less useful for large LLMs because LLMs typically need most or all of a GPU's available memory.

### MPS

**NVIDIA Multi-Process Service (MPS)** is **not the same as simple time slicing**.

Both allow multiple workloads to share one GPU, but they work differently.

```text
Time slicing:
Multiple pods/processes are placed on the same GPU.
They take turns using GPU execution resources over time.
Work from different CUDA contexts is scheduled in time slices.
This is simple oversubscription, but it does not provide strong isolation.

MPS:
Multiple CUDA processes can submit work to the GPU more concurrently.
Instead of each process being isolated behind its own separately time-sliced CUDA context,
MPS coordinates their GPU work through an MPS server/control daemon.
This allows kernels from different client processes to run concurrently when the GPU has available capacity.
```

#### How MPS works

```text
1. An MPS control daemon runs on the node.

2. When a CUDA application starts, the CUDA driver tries to connect to the MPS control daemon.

3. The daemon starts or reuses an MPS server.

4. CUDA client processes connect to that MPS server.

5. The MPS server coordinates shared GPU execution so work from multiple clients can use the GPU concurrently instead of only being time-sliced.
```

NVIDIA explains that, without MPS, kernels from different CUDA contexts are scheduled by a **time-sliced scheduler** and cannot execute concurrently. With MPS, client CUDA contexts route work through the MPS server, which bypasses that limitation and allows kernels from different clients to execute simultaneously. On Volta and newer GPUs, the MPS server is less in the critical path because clients manage more resources directly while the server mediates remaining shared resources.

Source: [NVIDIA Multi-Process Service architecture](https://docs.nvidia.com/deploy/mps/architecture.html) and [NVIDIA MPS introduction](https://docs.nvidia.com/deploy/mps/introduction.html).

#### MPS clarification

**MPS does not manually assign each tiny job to individual CUDA cores like a traffic officer.**

Instead, it lets work from different processes enter the GPU in a way that the GPU hardware scheduler can run them **concurrently** when resources are available.

Simple example:

```text
Without MPS:

Model A has its own CUDA context.
Model B has its own CUDA context.

GPU runs work from Model A.
Then switches context.
GPU runs work from Model B.
Then switches back.
```

This can leave GPU capacity unused if Model A's kernel is small and does not occupy the whole GPU.

With MPS:

```text
Model A sends CUDA work.
Model B sends CUDA work.
Model C sends CUDA work.

MPS makes these clients share a common execution path/context,
so the GPU can see more work at the same time.
```

Then the GPU can do something like:

```text
Model A uses part of the GPU
Model B uses another available part
Model C uses remaining available capacity
```

The mental model is close:

```text
MPS helps prevent GPU resources from sitting idle
when one model alone cannot fully occupy the GPU.
```

But more precisely:

```text
MPS exposes work from multiple CUDA processes concurrently,
and the GPU hardware scheduler fills available compute capacity.
```

So MPS is less like:

```text
daemon assigns every task to every CUDA core
```

And more like:

```text
daemon opens a shared highway so multiple CUDA applications can feed work to the GPU together
```

#### Mental model

```text
Time slicing = one cashier serving customers one by one very quickly.

MPS = one shared kitchen where several cooks prepare different orders at the same time,
while a kitchen manager coordinates access to shared equipment.
```

Simple distinction:

```text
MIG = split one physical GPU into hard isolated GPU instances.

Time slicing = share one GPU by letting workloads take turns.

MPS = share one GPU by allowing CUDA processes to run more concurrently through an MPS server/control daemon.
```

#### Important nuance

```text
MPS improves GPU utilization, but it is not the same as hard isolation.
On newer NVIDIA GPUs, MPS has better address-space behavior,
but MIG is still the stronger isolation model.
```

For Kubernetes and the NVIDIA GPU Operator, **time slicing** and **MPS** are both GPU sharing strategies. But MPS is more advanced than basic time slicing because it enables more concurrent CUDA execution instead of only rotating workloads in turns.

### MIG

**MIG** stands for **Multi-Instance GPU**.

It is available on certain NVIDIA GPUs, such as **A100** and **H100**, and allows one physical GPU to be partitioned into multiple **isolated GPU instances**.

Where time slicing is mainly **temporal sharing**, MIG is **hardware partitioning**.

Simple distinction:

- **Time slicing**: workloads take turns on the same physical GPU.
- **MPS**: CUDA processes run more concurrently through an MPS server/control daemon.
- **MIG**: the GPU is split into isolated hardware-backed instances.

MIG is better when workloads need stronger guarantees around:

- **Isolation**
- **Predictable memory allocation**
- **Fault containment**
- **More stable performance**

For scenarios requiring stronger isolation guarantees and fixed memory allocations per workload, MIG is the more appropriate NVIDIA sharing mechanism.

### Model-Serving Example: One GPU, Three Small Models

Imagine one Kubernetes node has **one NVIDIA GPU**, and we want to serve **three small AI models**:

```text
Model A: sentiment analysis
Model B: text embeddings
Model C: small chatbot
```

#### 1. Time slicing

Kubernetes pretends the single GPU is several shareable GPU slots.

```text
Pod A -> Model A -> GPU slot 1
Pod B -> Model B -> GPU slot 2
Pod C -> Model C -> GPU slot 3
```

But physically, there is still only **one GPU**.

The GPU serves them like this:

```text
Model A runs for a tiny slice of time
Model B runs for a tiny slice of time
Model C runs for a tiny slice of time
then repeats
```

This is good for light workloads, but if all three get busy, they slow each other down.

#### 2. MPS

The three model servers still share the same GPU, but instead of only taking turns, their CUDA work can run more concurrently.

```text
Model A sends small GPU jobs
Model B sends small GPU jobs
Model C sends small GPU jobs

MPS coordinates them so the GPU can execute work from multiple models more efficiently.
```

This is useful when each model alone does not fully use the GPU. MPS helps **fill the gaps**.

Mental image:

```text
Time slicing:
one model at a time, very fast switching

MPS:
multiple small model jobs sharing the GPU more concurrently
```

#### 3. MIG

The physical GPU is split into real isolated GPU partitions.

```text
GPU partition 1 -> Pod A -> Model A
GPU partition 2 -> Pod B -> Model B
GPU partition 3 -> Pod C -> Model C
```

Each model gets its own dedicated slice of GPU memory and compute.

This is stronger isolation than time slicing or MPS. Model A cannot easily interfere with Model B's GPU memory.

Simple comparison:

```text
Time slicing:
three models take turns on one GPU

MPS:
three models share one GPU more concurrently

MIG:
one GPU is carved into separate mini-GPUs
```

For AI model serving:

```text
Use time slicing when workloads are light and occasional.

Use MPS when workloads are small but active, and you want better utilization.

Use MIG when you need stronger isolation and predictable GPU slices.
```

#### Encode this

- **Sub-GPU allocation improves utilization by sharing one GPU across workloads**
- **Time slicing = oversubscription and time-based sharing**
- **MPS = concurrent CUDA execution through an MPS server/control daemon**
- **MIG = hardware-backed GPU partitioning**
- **Time slicing improves utilization but does not isolate memory or faults**
- **MPS improves utilization but is still not hard isolation**
- **Large LLMs often still need exclusive GPUs because memory is the real constraint**

#### Recall prompt

*Why can time slicing improve GPU utilization but still be risky for production workloads that need memory or fault isolation?*

[Back to Contents](#contents)

## Current State and Gaps in Model Portability

![MLOps Portability Cover Image](assets\MLOps-Portability-Cover-Image.png)

Model portability is still **immature** for LLMs.

### ONNX

- **ONNX** is strong for general ML portability because it provides a structured model format.
- But for LLMs, it is often **not fully self-contained** because important artifacts like **tokenizers** may remain outside the model format.

### GGUF

- **GGUF** is a more specialized format for LLMs and is relatively self-contained.
- But it is also more tightly coupled to certain runtimes, especially **`llama.cpp`**.

### Safetensors

- **Safetensors** is increasingly important for production deployments.
- It is commonly used in a **multifile layout**, which works well with **OCI artifacts** because components can be distributed as separate layers for:
  - **Caching**
  - **Parallel downloads**
  - **Flexibility**

### Core takeaway

There is still **no universal model packaging standard for LLMs** equivalent to what OCI did for containers.

The field is evolving too quickly:

- New architectures appear often
- Runtime optimizations change fast
- Serving requirements vary widely

### What is practical today

- For now, **GGUF** and **Safetensors** are often the most practical formats depending on the serving stack and deployment goal.

### Important mental model

At the end of the day, an LLM is **a collection of files**.

Those files may be:

- Self-contained
- Split across multiple artifacts
- Bound to particular runtimes

This is why discovery, indexing, and management matter so much in Kubernetes environments.

### Encode this

- **ONNX = useful, but incomplete for many LLM workflows**
- **GGUF = self-contained, but runtime-coupled**
- **Safetensors = production-friendly and OCI-compatible**
- **True portability standardization is still not finished**

### Recall prompt

- *Why is OCI-level standardization for models harder than OCI standardization for containers?*

[Back to Contents](#contents)

## Model Registry

A **model registry** is a central system for **managing models and their metadata** across the ML lifecycle.

It acts as both:

- A **discovery mechanism**
- A **collaboration platform**

### What a model registry does

It helps teams:

- Track model versions
- Store metadata
- Manage governance
- Promote models through lifecycle stages
- Support deployment readiness

### Important operational detail

Most organizations run model registries as **internal services**, often inside the cluster.

They usually **do not store the actual model weights directly**.

Instead, they typically store:

- **Metadata**
- **References**
- **Version records**
- **Governance information**

The actual model artifacts often live in:

- **S3 buckets**
- Other **object stores**

### Why this separation matters

Keeping metadata separate from large model files improves:

- **Flexibility**
- **Scalability**
- **Operational simplicity**

### Shared value across roles

For **data scientists**, the registry supports:

- Experiment tracking linkage
- Performance verification
- Reproducibility
- Release preparation

For **MLOps engineers**, the registry supports:

- Controlled deployment of approved models
- Metadata-driven automation
- Governance and auditability
- Monitoring hooks for later lifecycle steps

### Core model registry capabilities

#### Metadata management

Stores:

- Accuracy
- Lineage
- Benchmarks
- Training context

#### Model discovery and search

Allows search by:

- Architecture
- Hyperparameters
- Dataset
- Performance metrics

#### Version control

Tracks:

- Model versions
- Dataset versions

This is essential for **reproducibility** and **rollback**.

#### Lifecycle management

Supports stages such as:

- Experimentation
- Staging
- Production
- Retirement

#### Access control

Supports secure collaboration with permissions and visibility rules.

#### Auditing and compliance

Tracks approvals, changes, and usage history.

#### Data pipeline integration

Supports CI/CD workflows like:

- Validation
- Packaging
- Promotion
- Rollout

### Related ML concepts

#### Model experimentation

This is the iterative process of training many model variants with different:

- Hyperparameters
- Datasets
- configurations

The goal is to identify the best-performing version.

#### Feature stores

A **feature store** manages features consistently across training and inference to avoid **training-serving skew**.

This matters more in traditional ML than in many LLM workloads, though embeddings and retrieval systems still make it relevant in generative AI systems.

### Key bridge concept

**The model registry is the handoff point between experimentation and production.**

That is one of the highest-value ideas to remember.

### Encode this

- **Registry stores metadata, not usually the full model weights**
- **It bridges experiment workflows and production workflows**
- **It supports versioning, governance, search, and lifecycle control**

### Recall prompt

*Why is the model registry considered a handoff point between data science and MLOps?*

[Back to Contents](#contents)

### Hugging Face Model Hub

The **Hugging Face Model Hub** is the **canonical public platform** for discovering and sharing open source machine learning models, especially **LLMs**.

<u>Main idea:</u> Hugging Face plays a role for **open ML models** that is similar to what **GitHub** plays for **open source code**.

#### Why it matters

- It is the main discovery layer for open models
- It standardizes how models are documented
- It supports both manual exploration and API-driven access
- It is often the first source people use before internalizing models into production systems

#### Model Cards

Each model entry typically includes a **Model Card**.

A Model Card summarizes:

- Intended use cases
- Training datasets
- Evaluation metrics
- Limitations and risks
- Licensing information

This is important because **model adoption is not just about weights**; it is also about understanding **fitness**, **constraints**, and **governance**.

#### Inference widget

Many models also expose an **interactive inference widget** in the web UI.

This helps with:

- Quick manual validation
- Basic behavioral testing
- Fast model comparison before local deployment

#### API access

Hugging Face also provides a **REST API** for:

- Querying models
- Retrieving metadata
- Discovering versions
- Filtering models programmatically

This is useful in automation pipelines, even if the Hub itself is not the final production registry.

#### Limitation for production

The Hub is excellent for **public discovery**, but it has important limitations for enterprise production use:

- It is not ideal for **proprietary private models**
- It may be too loose for **strict internal governance**
- It is not enough by itself for **full lifecycle traceability**
- External availability and access control may not meet production requirements

#### Best operational takeaway

Use Hugging Face as:

- A **public source of truth** for open models
- A **discovery and evaluation layer**
- A **source repository** that you may later mirror, package, or import into internal systems

Do not confuse that with an **internal production-grade registry strategy**.

#### Encode this

- **Hugging Face Hub = public discovery and sharing platform**
- **Model Card = operational and governance context around a model**
- **Useful for exploration, but not sufficient by itself for private production model management**

#### Recall prompt

*Why is Hugging Face ideal for public model discovery but insufficient as the only production registry for many organizations?*

[Back to Contents](#contents)

### MLflow Model Registry

**MLflow** is a **Linux Foundation project** for managing the machine learning lifecycle, including:

- **Experiment tracking**
- **Model packaging**
- **Model registry**

It was created by **Databricks in 2018** and became widely adopted because it is relatively simple and integrates well with data science workflows.

#### Core concept: the Tracking Server

The central component in MLflow is the **Tracking Server**.

It stores and exposes:

- Experiment metadata
- Metrics
- Parameters
- Runs
- Model artifacts
- Registry entries

This makes MLflow especially strong on the **data science side** of the lifecycle.

#### Why practitioners like MLflow

- Easy to install
- Easy to use locally
- Strong experiment tracking UX
- Good for comparing runs and hyperparameters
- Supports metadata-rich model registration

#### Where model artifacts live

In simple setups, model artifacts can live on the **local filesystem**.

In production-oriented setups, MLflow can store artifacts in:

- **S3**
- Other object stores
- External artifact locations
- References to external sources such as the Hugging Face Hub

The registry stores **artifact URIs**, not just display names.

#### Programmatic logging and registration

Most data scientists use MLflow programmatically:

```python
import mlflow

mlflow.set_tracking_uri(uri="http://localhost:8000")
mlflow.set_experiment("MLflow Demo")

params = {
    "solver": "lbfgs",
    "multi_class": "auto",
    "max_iter": 2500,
}

with mlflow.start_run():
    mlflow.log_params(params)
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="my_model",
        input_example=X_train,
        registered_model_name="my-model",
    )
```

#### Registry access through the REST API

MLOps workflows often interact with MLflow through its HTTP API:

```bash
curl http://localhost:8000/api/2.0/mlflow/registered-models/search
```

Example response shape:

```json
{
  "registered_models": [
    {
      "name": "my-model",
      "creation_timestamp": 1736523034148,
      "last_updated_timestamp": 1736524822538,
      "latest_versions": [
        {
          "name": "my-model",
          "version": "4",
          "creation_timestamp": 1736524822538,
          "last_updated_timestamp": 1736524822538,
          "current_stage": "None",
          "description": "",
          "source": "mlflow-artifacts:/84948067/f0dd25483e/artifacts/my_model",
          "run_id": "f0dd25483e234400b7",
          "status": "READY",
          "run_link": ""
        }
      ]
    }
  ]
}
```

#### OCI image generation

MLflow can also generate a Dockerfile and package a model into a self-contained container image:

```bash
mlflow models generate-dockerfile \
  -m mlflow-artifacts:/84948067/f0dd25483e/artifacts/my_model

cd mlflow-dockerfile
podman build -t my_model .
```

This is useful for smaller or traditional ML packaging flows, but it is **not ideal for very large LLM artifacts** that require heavy downloads and more efficient caching patterns.

#### MLflow on Kubernetes

MLflow can be deployed on Kubernetes, usually as a web service backed by a database such as **PostgreSQL**.

However:

- It does **not** introduce native Kubernetes CRDs
- It is **not deeply Kubernetes-native**
- Scaling and serving automation usually require extra integration work

#### MLflow and LLMs

MLflow has improved its GenAI and LLM support significantly, especially from the **3.0** line onward, with capabilities such as:

- Memory-efficient Transformers logging
- Prompt Registry
- AI gateway
- GenAI evaluation
- Tracing for LLM applications
- Reference-based logging for Hub-backed models

Still, large-scale LLM operations often need complementary infrastructure because:

- Full weights usually still need local or nearby storage in production
- Repeated large downloads are expensive
- Artifact storage patterns may not be optimized for very large model payloads

#### Best operational takeaway

**MLflow is strongest as a data science lifecycle platform, not as the final answer to large-scale Kubernetes-native LLM operations.**

#### Encode this

- **MLflow = experiment tracking first, registry second**
- **Tracking Server is the central hub**
- **Great for DS workflows, less native to Kubernetes operations**
- **LLM support is improving, but large-model production usually needs more infrastructure**

#### Recall prompt

*Why is MLflow highly effective for experimentation but often incomplete by itself for large-scale LLM production on Kubernetes?*

[Back to Contents](#contents)

### Kubeflow Model Registry

**Kubeflow** is a **Kubernetes-native ML platform** that aims to support the full ML lifecycle.

It was initially developed by **Google** and is now part of the broader **CNCF ecosystem**.

#### Major Kubeflow components

- **Kubeflow Dashboard**  
  A central dashboard and hub that connects the authenticated web interfaces of Kubeflow and other ecosystem components.

- **Kubeflow Notebooks**  
  A component for running web-based development environments like Jupyter Notebooks inside your Kubernetes cluster by running them in pods. No local installation is needed.

- **Kubeflow Pipelines**  
  Kubeflow Pipelines (KFP) is a platform for building and deploying portable and scalable machine learning workflows using Kubernetes.

- **Kubeflow Trainer**  
  Kubeflow Trainer is a unified interface for model training and fine-tuning on Kubernetes. It runs scalable and distributed training jobs for popular frameworks like PyTorch or TensorFlow.

- **Kubeflow Katib**  
  Katib is a Kubernetes-native project for automated machine learning (AutoML) with support for hyperparameter tuning, early stopping, and neural architecture search.

- **KServe** for model serving  
  KServe, previously KFServing, solves production model serving on Kubernetes. It started in Kubeflow but later became a separate CNCF project. We cover KServe in detail in the KServe section.

- **Model Registry**  
  An index and catalog for ML models. The registry is the central hub within the Kubeflow ecosystem, and the rest of this section focuses on it.

#### Why Kubeflow is different from MLflow

Kubeflow goes deeper into **Kubernetes-native control-plane integration**.

It uses:

- **CRDs**
- **Controllers**
- **Kubernetes manifests**
- Native workflow patterns built around cluster operations

This makes Kubeflow more aligned with platform engineering on Kubernetes than tools that primarily began as standalone tracking systems.

#### What the Kubeflow Model Registry does

The **Kubeflow Model Registry** is the central catalog for:

- Models
- Versions
- Metadata
- Lineage-relevant details

Its purpose is to simplify the move from **experimentation** to **production deployment** inside a Kubernetes-centric ecosystem.

#### Metadata storage model

The registry uses a backend relational database, commonly **MySQL**, and follows a flexible **entity-relationship model** inspired by **Google ML Metadata**.

This helps with:

- Structured lineage tracking
- Parameter storage
- Metric storage
- Version reuse across Kubeflow components
- Triggering downstream workflows

#### Operational requirement

The registry depends on external stateful infrastructure such as:

- **MySQL**
- **Persistent volumes**

So while it is Kubernetes-native, it is still not "free"; it requires careful production operation.

#### Registering a model

You can interact with the registry through a Python SDK:

```python
from model_registry import ModelRegistry

registry = ModelRegistry(
    server_address="http://model-registry-service.kubeflow.svc.cluster.local",
    port=8080,
    author="your name",
    is_secure=False,
)

rm = registry.register_model(
    "iris",
    "gs://kfserving-examples/models/sklearn/1.0/model",
    model_format_name="sklearn",
    model_format_version="1",
    version="v1",
    description="Iris scikit-learn model",
    metadata={
        "accuracy": 3.14,
        "license": "BSD 3-Clause License",
    },
)
```

#### Access pattern

Because the service address is cluster-internal, this kind of code usually runs **inside the cluster**, for example:

- In a notebook pod
- In a pipeline step
- In an application pod

#### Querying the registry from inside the cluster

You can also access it from a temporary pod:

```bash
kubectl run -it --rm curl --image=curl --restart=Never -- \
  http://model-registry-service.kubeflow.svc.cluster.local/...
```

#### Integration with KServe

Kubeflow Model Registry can act as an indirection layer for KServe:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: iris-model
spec:
  predictor:
    model:
      storageUri: "model-registry://iris/v1"
      modelFormat:
        name: "sklearn"
        version: "1"
```

This matters because the **InferenceService** can reference the model through the registry, while the actual underlying storage location can change later without rewriting the serving manifest.

#### Best operational takeaway

**Kubeflow Model Registry is a stronger fit when you want the registry to participate as part of a Kubernetes-native ML platform rather than remain a mostly standalone tracking system.**

#### Encode this

- **Kubeflow = full Kubernetes-native ML platform**
- **Model Registry is central inside that ecosystem**
- **Uses structured metadata with deeper cluster integration**
- **Works naturally with KServe and other Kubeflow components**

#### Recall prompt

*What makes Kubeflow Model Registry more Kubernetes-native than MLflow Model Registry?*

[Back to Contents](#contents)

### OCI

#### Registry

An **OCI Registry** is a standard system for **storing and distributing OCI-compliant artifacts**, most famously container images.

Examples include:

- **Docker Hub**
- **Quay.io**
- Built-in registries in some Kubernetes distributions such as **OpenShift**

##### Why OCI registries matter for GenAI

OCI registries are increasingly useful for **model distribution**, not just application containers.

That is possible because OCI evolved beyond classic container images into a broader artifact model.

##### What OCI means here

The **Open Container Initiative (OCI)** standardizes how containerized applications and related artifacts are packaged, stored, and exchanged.

OCI began with images but now also supports **OCI artifacts**, which allows registries to store more than runnable applications.

##### Why this is important for LLMs

Unlike many model registries that store mostly **metadata and references**, an OCI Registry can store the **full model data itself**.

That makes it attractive for:

- Versioning
- Immutability
- Caching
- Distribution
- Kubernetes-native delivery workflows

##### Passive data images

LLM model images are often **passive data images**.

That means:

- They are **not executed** like applications
- They are used as **immutable packages** of model files
- Inference runtimes consume the files they contain

##### Building a model image from Hugging Face

Example Dockerfile:

```dockerfile
FROM alpine/git

RUN git lfs install \
 && git clone --depth 1 https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct /models

ENTRYPOINT sh
```

##### Building and pushing with Podman

```bash
podman build -f Dockerfile.model -t quay.io/rhuss/qwen2.5-0.5b-instruct .
podman push quay.io/rhuss/qwen2.5-0.5b-instruct:latest
```

##### Important production note

For simplicity, a model might be added as a **single layer**, but in production it is often better to structure large artifacts into multiple layers so runtimes can:

- Cache efficiently
- Reuse unchanged chunks
- Download pieces independently

##### Relationship to KServe

OCI-backed model artifacts can integrate well with Kubernetes-native serving workflows.

They are especially relevant when combined with patterns such as:

- **Modelcars**
- **OCI image volume mounts**
- KServe loading model data from OCI-managed artifacts

##### Prominent OCI-compliant registries

The following are prominent **OCI-compliant registries**, grouped by deployment model and primary use case.

###### Major cloud-managed registries

- **Amazon Elastic Container Registry (ECR)**  
  A highly scalable managed registry that integrates with AWS IAM and provides built-in vulnerability scanning.

- **Azure Container Registry (ACR)**  
  Provides geo-replication for high availability and supports OCI artifacts such as Helm charts.

- **Google Artifact Registry (GAR)**  
  Google’s successor to GCR, supporting both container images and language-specific packages such as `npm` and `Maven`.

- **Oracle Cloud Infrastructure Registry (OCIR)**  
  Tailored for Oracle Cloud services and integrated with Oracle Container Engine for Kubernetes (OKE).

- **DigitalOcean Container Registry (DOCR)**  
  A simplified managed registry designed for easy integration with DigitalOcean Kubernetes.

###### Popular public and SaaS registries

- **Docker Hub**  
  The default registry for Docker and the largest public marketplace for container images.

- **GitHub Container Registry (GHCR)**  
  Integrated with GitHub Actions and repositories, with fine-grained permissions tied to GitHub identities.

- **Quay.io**  
  A Red Hat-hosted registry known for strong security scanning and repository mirroring features.

- **GitLab Container Registry**  
  A built-in registry for GitLab users, supporting seamless image management inside GitLab CI/CD workflows.

###### Open source and self-hosted solutions

- **Harbor**  
  A CNCF-graduated registry project with RBAC, image signing through Notary, and vulnerability scanning.

- **Zot**  
  A vendor-neutral, OCI-native registry distributed as a single statically linked binary, designed for simplicity and performance.

- **Distribution**  
  The reference implementation of the OCI Distribution Specification, previously known as Docker Distribution.

- **Sonatype Nexus Repository OSS**  
  A universal repository manager that supports OCI-compliant Docker registries alongside `Maven`, `npm`, and other package formats.

- **JFrog Artifactory**  
  An enterprise-grade universal repository manager with OCI artifact support and extended security capabilities through JFrog Xray.

##### Best operational takeaway

**OCI Registry is not just another metadata registry. It can be the actual distribution system for the full model artifact.**

That is a fundamental distinction from many classic model registry designs.

##### Encode this

- **OCI Registry can store the full model artifact, not just metadata**
- **Useful for immutable, versioned model delivery**
- **Strong fit for Kubernetes-native distribution of large model files**

##### Recall prompt

*Why is an OCI Registry conceptually different from MLflow or Kubeflow registries when handling model data?*

[Back to Contents](#contents)

#### Images

An **OCI image** is a **standardized container image format** defined by the **Open Container Initiative**.

Its purpose is **interoperability**:

**build with one tool, run with another, without changing the artifact**.

##### Why OCI matters

OCI makes container artifacts portable across:

- Build tools
- Registries
- Runtimes
- Kubernetes environments

##### Core components of an OCI image

###### 1. Filesystem layers

Ordered, content-addressed blobs representing filesystem changes.

###### 2. Image configuration

A JSON document describing runtime details such as:

- Environment variables
- Entrypoint
- Default command

###### 3. Image manifest

A JSON document that pins:

- Specific layers
- Specific config
- Cryptographic digests

This acts like a **bill of materials** for the image.

###### 4. Image index

An optional higher-level manifest that points to platform-specific variants, such as:

- `amd64`
- `arm64`

##### Standard pull workflow

When a runtime pulls an OCI image, it generally:

1. **Downloads** the manifest
2. **Verifies** layer digests
3. **Unpacks** the filesystem layers
4. **Executes** the image through the runtime stack

##### OCI versus Docker

They are closely related, but not identical:

- **OCI image** = open standard
- **Docker image** = Docker-oriented conventions, now largely OCI-compatible

##### Why this matters in AI systems

OCI ideas influence how people think about **packaging and distributing model artifacts**, especially when models are broken into multiple files or layers.

This is one reason **Safetensors + OCI artifacts** is a practical pattern for production delivery.

##### Encode this

- **OCI = standard for interoperable container packaging**
- **Manifest = cryptographic description of the image**
- **Image index = multi-architecture selector**
- **OCI thinking influences model artifact packaging too**

##### Recall prompt

*Why is OCI a strong analogy for where model packaging standards may eventually go?*

[Back to Contents](#contents)

## Accessing Model Data in Kubernetes

Now that the notes have covered **model formats**, **registries**, and **artifact distribution**, the next operational question is:

**How does a model-serving workload actually access model data from inside a Kubernetes cluster?**

For GenAI serving on Kubernetes, this is not a secondary detail. It directly affects:

- **startup time**
- **storage efficiency**
- **replica scaling**
- **network usage**
- **inference latency**

### KServe `storageUri` and Storage Initializers

KServe provides a clean reference model for understanding how Kubernetes-based serving systems access model data.

In the simplest case, the storage location is declared directly in an `InferenceService` using `storageUri`.

Example using S3-backed model storage:

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "mnist"
spec:
  predictor:
    serviceAccountName: sa
    tensorflow:
      storageUri: "s3://kserve-examples/mnist"
```

What to notice:

- `serviceAccountName` identifies the Kubernetes `ServiceAccount`
- that service account is typically associated with a `Secret` or cloud-native identity
- the runtime here is **TensorFlow**
- `storageUri` points to the model’s storage location

#### Why the URI scheme matters

The **scheme** in `storageUri` determines which storage backend KServe will use and how the model data is prepared.

Examples:

- `s3://`
- `gs://`
- `https://`
- `pvc://`
- `oci://`
- `hf://`

This scheme triggers a **storage initializer**, which KServe runs as an **init container** before the main serving runtime starts.

Its purpose is simple:

**make model data available to the runtime container before inference begins**

#### Custom storage initializers

KServe lets you add custom URI schemes through `ClusterStorageContainer`.

Example:

```yaml
apiVersion: serving.kserve.io/v1alpha1
kind: ClusterStorageContainer
metadata:
  name: model-registry-storage
spec:
  container:
    name: storage-initializer
    image: kubeflow/model-registry-storage-initializer
  supportedUriFormats:
    - prefix: model-registry://
```

What this does:

- declares a custom initializer image
- registers `model-registry://` as a supported URI prefix
- allows `InferenceService` resources to refer to models through that scheme

#### Init containers and sidecars

These are important Kubernetes patterns to remember.

**Init containers**:

- run **before** the application container
- perform **one-time setup work**
- commonly prepare files in a shared volume

**Sidecars**:

- run **alongside** the main container
- provide supporting behavior such as logging, transformation, or coordination

For model serving, the storage initializer is usually an **init-container pattern**, not a sidecar pattern.

#### Node-local sharing with `emptyDir`

A common KServe pattern is:

1. the storage initializer downloads or copies the model data
2. the data is written into an `emptyDir` volume
3. the main serving container mounts that same volume

This works because `emptyDir` is shared among containers in the same pod, including:

- init containers
- application containers

This gives the runtime a node-local copy of the model data for that pod.

### Built-in KServe Storage Initializers

KServe supports several storage schemes out of the box:

| Scheme | Description | Example |
| --- | --- | --- |
| `gs` | Download from Google Cloud Storage | `gs://kfserving-examples/models/sklearn/1.0/model` |
| `s3` | Download from an S3 bucket | `s3://kserve-examples/mnist` |
| `https` | Download model data with HTTP | `https://huggingface.co/meta-llama/Llama-3.2-3B` |
| `hdfs`, `webhdfs` | Access files from Hadoop Distributed File System | `hdfs://path/to/model` |
| `pvc` | Copy or mount model data from a PersistentVolumeClaim | `pvc://${PVC_NAME}/export` |
| `oci` | Pull an OCI image with model data and access it directly via a modelcar | `oci://quay.io/rhuss/kserving-example-sklearn:1.0` |
| `model-registry` | Access a model registered in the Kubeflow Model Registry | `model-registry://iris/v1` |
| `hf` | Download directly from the Hugging Face Hub | `hf://meta-llama/Llama-2-7b-chat-hf` |

#### Important operational distinction

Most of these schemes involve **preparing a node-local copy** of model data for each pod.

That is convenient for runtime access speed, but it can mean:

- repeated downloads
- repeated copies
- duplicated storage across replicas or nodes

This is one reason storage strategy matters so much for larger models.

### Shared Storage with PersistentVolumes

When an `InferenceService` runs with multiple replicas, each replica needs access to the same model files.

There are three broad approaches:

- download copies from remote object storage
- package models into OCI artifacts
- mount shared storage through **PersistentVolumes**

PersistentVolumes provide a third model:

**store the model once, mount it from many pods**

#### Why PersistentVolumes matter

PVs are useful when you want:

- **storage efficiency** across replicas
- **centralized model management**
- **fast startup without redownloading model data**
- clearer separation between infrastructure and model ownership

Typical backends include:

- **NFS**
- **Ceph**
- **AWS EFS**
- **Azure Files**
- **Google Cloud Filestore**

#### Example PV and PVC for model storage

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: llama-3-8b-pv
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadOnlyMany
  persistentVolumeReclaimPolicy: Retain
  nfs:
    server: nfs-server.example.com
    path: /exports/models/llama-3-8b
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: llama-3-8b-pvc
  namespace: default
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 20Gi
```

Key points:

- `storage: 20Gi` defines the total PV capacity
- `ReadOnlyMany` allows multiple pods to mount the volume read-only at the same time
- `Retain` preserves the underlying model data if the PVC is deleted
- the PVC must request an access mode compatible with the PV

#### Why `ReadOnlyMany` is a strong fit

Serving workloads usually need to **read** model weights, not modify them.

That makes **read-only shared mounts** a natural fit.

This also helps with:

- safer sharing across replicas
- less coordination overhead
- more aggressive filesystem caching

#### Using a PVC with KServe

KServe supports PVC-backed access through the `pvc://` storage scheme:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: llama-pvc
spec:
  predictor:
    model:
      modelFormat:
        name: pytorch
      storageUri: pvc://llama-3-8b-pvc/
```

The PVC name is referenced directly in the URI.

KServe then mounts the PVC into the model container, typically under `/mnt/models`.

#### How PVC access differs from remote-download schemes

This is a crucial distinction.

For schemes like:

- `s3://`
- `gs://`
- `https://`
- `hf://`

the storage initializer usually **downloads and copies** data into pod-local storage.

For `pvc://`, KServe generally **mounts the volume directly**.

That means:

- no large data copy step is needed
- startup can be faster
- the runtime reads directly from the mounted shared filesystem

The storage initializer may still exist in the flow, but for PVC-backed access it effectively becomes a **near no-op** compared with remote download schemes.

#### Trade-off: local speed versus shared efficiency

This is the core operational trade-off:

**Node-local access**

- faster runtime I/O
- avoids repeated network reads during inference
- but may require one copy per pod or per node

**Network-backed shared PV access**

- more storage-efficient
- simpler central updates
- but introduces network latency on reads

#### Scaling considerations

PersistentVolumes work well for many common serving deployments, especially when:

- replica counts are moderate
- model files are large
- startup efficiency matters
- centralized storage management is preferred

But performance depends on:

- backend storage throughput
- storage server load
- available network bandwidth
- number of concurrent readers

Warning signs include:

- increasing I/O wait
- higher latency variance
- storage backend pressure
- network saturation

High-performance distributed storage systems usually scale better than simple NFS setups.

#### Practical takeaway

There is no universal best method for model data access.

The right choice depends on whether you optimize for:

- **startup speed**
- **runtime latency**
- **storage efficiency**
- **replica scale**
- **operational simplicity**

PVs are often a strong choice for shared model serving, but for very high-throughput or high-scale inference, node-local approaches such as OCI-backed delivery can be better.

### Encode this

- **`storageUri` is the control point for how KServe locates model data**
- **storage initializers are usually init containers that prepare model files before serving**
- **`emptyDir` gives pod-local shared storage between init containers and runtimes**
- **`pvc://` differs from remote-download schemes because it mounts shared storage directly**
- **model access design is a trade-off between local performance and shared efficiency**

### Recall prompt

*Why might a team choose `pvc://` over `s3://`, and what performance trade-off does that decision introduce?*

[Back to Contents](#contents)

## Running in Production

Once an LLM is deployed on Kubernetes, the real production question changes from **"does it respond?"** to **"does it respond consistently, efficiently, and under load?"**

Production LLM serving is not the same as running a normal stateless web container. GenAI workloads have several unusual properties:

- **large model artifacts**
- **high GPU memory pressure**
- **variable request cost based on token count**
- **runtime state such as KV cache**
- **long startup and warmup phases**
- **network-sensitive distributed serving patterns**

The trap is treating a model server like any other container:

```text
set resource limits
expose a Service
ship it
```

That misses the operational reality. LLM inference needs careful tuning around model choice, runtime memory, autoscaling, request routing, model loading, and sometimes distributed serving topology.

This chapter focuses on five production areas:

| Area | Core question |
| --- | --- |
| **Model and runtime tuning** | Which model/runtime settings meet the use case without wasting GPU budget? |
| **Autoscaling** | How should replicas change when LLM request cost is token-dependent? |
| **Optimizing vLLM startup time** | How do we reduce deployment and scale-up latency? |
| **LLM-aware routing** | How do we route requests to replicas that can serve them efficiently? |
| **Disaggregated serving** | When do prefill/decode or multi-node topologies become necessary? |

The most fundamental decision is still the first one: **pick and tune a model that matches the workload before spending effort scaling it.**

### Model and Runtime Tuning

For many teams, the first GenAI application starts with a managed API such as **OpenAI ChatGPT**, where configuration options are intentionally limited.

On-premise or self-managed Kubernetes serving is different. You must choose the model yourself, and that choice depends on:

- **task type**
- **latency requirements**
- **real-time versus batch inference**
- **expected concurrency**
- **accuracy requirements**
- **GPU memory and cost constraints**

Model size matters, but it is not enough. Two models with the same parameter count can behave very differently because of:

- architecture
- training data
- training method
- instruction tuning
- context length
- tokenizer behavior
- quantization or compression state

**Key idea:** model selection should be based on measured task performance, not manual prompt testing alone.

Traditional predictive AI models are usually trained for one specific problem. LLMs are broader: they can summarize, reason, answer questions, classify text, generate code, and more. So the first evaluation step is to decide which ability actually matters for the application.

Examples:

- A chatbot may care about **truthfulness**, **latency**, and **safety**
- A RAG system may care about **faithfulness to retrieved context**
- A coding assistant may care about **program correctness**
- A summarizer may care about **coverage** and **low hallucination**

[Back to Contents](#contents)

### Language Model Evaluation

**Language model evaluation** measures a model's ability against specific tasks or risks.

Evaluation can target:

- **knowledge**
- **reasoning**
- **truthfulness**
- **toxicity**
- **robustness**
- **domain-specific correctness**
- **RAG faithfulness**
- **security resistance**

One widely used project is [EleutherAI's `lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness), which provides many out-of-the-box benchmark tasks.

Each benchmark generally contains:

- a **dataset** of prompts/questions
- expected **answers or labels**
- an **evaluation function**
- one or more **metrics**

Many tasks are structured as multiple-choice questions because that makes scoring easier and less subjective.

#### Evaluation flow

The evaluation process is usually asynchronous because benchmark runs can take many minutes or hours.

![Language model evaluation execution flow](<assets/Language model evaluation execution flow.png>)

**Figure 4-1. Language model evaluation execution flow**

High-level flow:

```text
benchmark task
  -> prompt/query generation
  -> deployed model endpoint
  -> model response
  -> scoring function
  -> metrics and report
```

Tools such as **TrustyAI** can wrap `lm-evaluation-harness` with Kubernetes-native resources such as an `LMEvalJob` CRD.

#### Leaderboards

Leaderboards help create an initial shortlist of models.

Useful examples include:

- [Hugging Face Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
- benchmark-specific leaderboards for **math**, **reasoning**, **safety**, or **coding**

Important caveat:

> Leaderboards are useful for narrowing the search, but they are not a substitute for local evaluation. Published benchmark scores still have trust and reproducibility implications.

The practical workflow is:

1. Use leaderboards to identify candidate models
2. Evaluate the candidates locally on application-relevant tasks
3. Benchmark runtime performance on production-like hardware
4. Re-evaluate after compression or fine-tuning

#### Common benchmark families

**MMLU**

**Massive Multitask Language Understanding** tests knowledge across many multiple-choice topics, including science, history, government, law, mathematics, and more.

**MMMU**

**Massive Multi-discipline Multimodal Understanding** extends the idea to multimodal models.

**RAG evaluation**

RAG systems need metrics that evaluate both retrieval and generation. [Ragas](https://github.com/explodinggradients/ragas) is commonly used to measure:

- context relevance
- answer faithfulness
- retrieval quality
- answer correctness

**Security evaluation**

[NVIDIA garak](https://github.com/NVIDIA/garak) is a vulnerability scanner for LLMs. It can probe for:

- prompt injection weakness
- jailbreak susceptibility
- harmful output generation
- other model security risks

#### Why evaluation matters after model selection

Evaluation is not only a model-picking activity.

It is also required after production optimization because techniques like **quantization** and **distillation** change model behavior.

Compression can reduce model size dramatically and improve throughput on the same hardware, but it can also reduce accuracy. A well-compressed model may recover more than **99%** of the original model's accuracy, but that needs to be measured.

#### Encode this

- **Model selection starts with the application task, not the leaderboard**
- **Leaderboards create a shortlist; local evaluation validates the choice**
- **RAG and security workloads need specialized evaluation**
- **Compression requires re-evaluation because model weights change**

#### Recall prompt

*Why is manual prompt testing not enough for choosing a production LLM?*

[Back to Contents](#contents)

### Language Model Compression

An LLM such as **Meta-Llama-3.1-8B-Instruct** has roughly **8 billion parameters**.

If each parameter is stored as a 16-bit floating point value:

```text
8 billion parameters x 16 bits = about 16 GB
```

That is only the model weights. GPU memory also needs space for:

- **activations**
- **KV cache**
- **intermediate tensors**
- **runtime/kernel overhead**
- **output tensors**

The main family of model compression techniques is **quantization**.

> **QUANTIZATION**
>
> Quantization reduces the memory footprint by representing values with lower precision, such as **FP8**, **INT8**, or other compressed formats.
>
> This is not just rounding numbers. Good quantization uses calibration and error-compensation techniques so the compressed model remains useful.

#### Why runtime support matters

Compression alone is not enough.

If the runtime cannot process quantized data efficiently, it may need to convert values back to 16-bit precision during execution. That reduces or eliminates the benefit.

The ideal setup is:

```text
compressed model
  + runtime-native quantization support
  + optimized GPU kernels
  = better throughput and lower memory pressure
```

vLLM has native support for many quantization techniques and can enable optimized kernels when it detects a quantized model.

#### Risks

Quantization is powerful, but not free.

Main risks:

- accuracy loss
- degraded reasoning quality
- hallucination increase
- hardware-specific kernel limitations
- unexpected behavior on long-context or domain-specific tasks

The mitigation is straightforward but non-negotiable:

**evaluate before and after compression.**

#### Example 4-1. Compress an LLM using `llmcompressor`

```python
from llmcompressor.modifiers.quantization import GPTQModifier
from llmcompressor.modifiers.smoothquant import SmoothQuantModifier
from llmcompressor.transformers import oneshot

# Select quantization algorithm. In this case, we:
#   * apply SmoothQuant to make the activations easier to quantize
#   * quantize the weights to int8 with GPTQ (static per channel)
#   * quantize the activations to int8 (dynamic per token)
recipe = [
    SmoothQuantModifier(smoothing_strength=0.8),
    GPTQModifier(scheme="W8A8", targets="Linear", ignore=["lm_head"]),
]

# Apply quantization using the built-in open_platypus dataset.
oneshot(
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    dataset="open_platypus",
    recipe=recipe,
    output_dir="TinyLlama-1.1B-Chat-v1.0-INT8",
    max_seq_length=2048,
    num_calibration_samples=512,
)
```

What to notice:

- `recipe` defines the quantization pipeline
- `SmoothQuantModifier` prepares activations for easier quantization
- `GPTQModifier(scheme="W8A8")` quantizes both **weights** and **activations** to 8-bit
- `dataset` is used for calibration
- `output_dir` contains the compressed model and config files needed for serving

> **TIP**
>
> Compression can make LLM serving dramatically more efficient, but improper quantization can break model quality.
>
> When possible, consider professionally compressed and validated models from trusted publishers, then still evaluate them against your own workload.

#### Encode this

- **Quantization reduces memory pressure by lowering numeric precision**
- **Runtime kernel support determines whether compression improves throughput**
- **Compression changes model behavior, so evaluation must be repeated**
- **A compressed model is an optimization artifact, not automatically a production-ready artifact**

#### Recall prompt

*Why can a quantized model fail to improve performance if the runtime does not support quantized execution natively?*

[Back to Contents](#contents)

### Model Performance Benchmark

Production tuning requires measurement under realistic load.

Important LLM-serving metrics include:

- **Time To First Token (TTFT)**
- **Inter-Token Latency (ITL)**
- **tokens per second**
- **request throughput**
- **latency distribution**
- **GPU memory utilization**
- **KV cache pressure**
- **queue depth**

Traditional HTTP load generators can call an LLM endpoint, but they usually do not understand LLM-specific metrics like TTFT and ITL. Specialized tools are better.

#### GuideLLM

[GuideLLM](https://github.com/neuralmagic/guidellm) is built to benchmark and tune LLM deployments under realistic inference patterns.

It can simulate different workload modes:

- synchronous request chains
- fixed concurrency
- constant request rates
- sweep scenarios
- Poisson-style traffic patterns

#### Example 4-2. Run a benchmark with GuideLLM

```bash
guidellm benchmark \
  --target http://127.0.0.1:8000 \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --output-path output_file.json \
  --rate-type sweep \
  --data 'prompt_tokens=256,output_tokens=128' \
  --max-seconds 400 \
  --warmup-percent 0.2
```

What to notice:

- `--target` points to the already deployed model endpoint
- `--output-path` stores the benchmark report
- `--rate-type sweep` tests multiple request-rate scenarios
- `--data` should match expected production input/output token sizes
- `--warmup-percent` gives the runtime warmup time before measured results matter

![Example output of a GuideLLM run](<assets/Example output of a GuideLLM run.png>)

**Figure 4-2. Example output of a GuideLLM run**

#### MLPerf Inference

[MLPerf Inference](https://mlcommons.org/benchmarks/inference-datacenter/) comes from **MLCommons**, an AI engineering consortium focused on open collaboration and reproducible AI system benchmarks.

It publishes results for:

- data center configurations
- edge/device configurations
- multiple model and hardware combinations

#### Inference Perf

**Inference Perf** is a GenAI inference benchmarking effort from the Kubernetes serving community.

It can:

- run locally
- run in a cluster
- target OpenAI-compatible endpoints
- use custom datasets that resemble production scenarios

#### vLLM benchmark suite

vLLM also provides benchmark scripts and nightly benchmark jobs.

These are useful when validating:

- model/runtime combinations
- GPU configurations
- vLLM tuning changes
- regression risk after upgrades

#### CI/CD integration

Performance tests should be part of the release pipeline.

The useful pattern is:

```text
deploy model to production-like environment
  -> run benchmark workload
  -> store benchmark output
  -> compare against previous release
  -> update capacity/rate-limit assumptions
```

**Important:** benchmark numbers are only useful when the environment resembles production, especially in:

- GPU type
- GPU count
- model artifact
- quantization format
- runtime version
- storage path
- network topology

#### Encode this

- **LLM benchmarking needs token-aware metrics**
- **TTFT and ITL matter more than generic HTTP latency alone**
- **Benchmarks feed capacity planning, rate limits, and autoscaling thresholds**
- **Production-like hardware is part of the benchmark, not an implementation detail**

#### Recall prompt

*Why is requests-per-second alone a weak metric for LLM-serving capacity?*

[Back to Contents](#contents)

### vLLM Runtime Parameters Tuning

vLLM usually starts from strong defaults, but it cannot automatically know everything about:

- workload shape
- expected concurrency
- maximum context size
- GPU memory budget
- latency objective

The key memory fact:

**vLLM greedily uses available GPU memory to maximize throughput.**

The ideal situation is:

```text
model weights fit in VRAM
  + activation memory fits in VRAM
  + KV cache has enough room
  = stable throughput and low latency variance
```

When KV cache space is too small, vLLM may need to evict or swap data. That usually shows up as higher **inter-token latency** and lower throughput.

> **HOW TO CALCULATE MODEL MEMORY REQUIREMENTS**
>
> Start with the model parameters:
>
> ```text
> parameter count x bytes per parameter = baseline weight memory
> ```
>
> A full-size model commonly uses **2 bytes per parameter** with FP16 or BF16.
>
> An 8B model therefore needs roughly:
>
> ```text
> 8 billion x 2 bytes = about 16 GB
> ```
>
> Then add memory for runtime overhead, activations, KV cache, and output tensors.
>
> For an 8B FP16 model with a 2048 context and batch size 1, a simplified estimate may land around **17.3 GB**. Increasing batch size to 10 can push the requirement above **28 GB**.
>
> The practical lesson: **batch size and sequence length can change memory requirements dramatically.**

#### Example 4-3. vLLM logs information about memory

```text
...
INFO [model_runner.py:1097] Loading model weights took 14.9888 GB
INFO [worker.py:241] Memory profiling takes 0.67 seconds
INFO [worker.py:241] the current vLLM instance can use total_gpu_memory (79.14GiB)
        x gpu_memory_utilization (0.90) = 71.22GiB
INFO [worker.py:241] model weights take 14.99GiB; non_torch_memory takes 0.12GiB;
        PyTorch activation peak memory takes 1.19GiB; the rest of the memory
        reserved for KV Cache is 54.93GiB.
...
WARNING [scheduler.py:1057] Sequence group 0 is preempted by PreemptionMode.SWAP
        mode because there is not enough KV cache space. This can affect the
        end-to-end performance. Increase gpu_memory_utilization or
        tensor_parallel_size to provide more KV cache memory.
        total_cumulative_preemption_cnt=1
```

What to notice:

- vLLM reports model weight size during startup
- it calculates usable GPU memory from `gpu_memory_utilization`
- it reports activation peak memory
- it reserves the remaining memory for KV cache
- preemption warnings indicate KV cache pressure

#### Important parameters

**`gpu-memory-utilization`**

Default is commonly `0.9`.

This controls how much available GPU memory vLLM can use. Raising it closer to `1.0` can make more space available for KV cache, but it also reduces safety margin.

**`max-model-len`**

Controls maximum context length.

This is crucial because KV cache size tracks context size. Set it based on the real application need.

Examples:

- Short chat prompts can use smaller values
- RAG workloads often need larger context
- long-document analysis needs larger context again

**`max-num-seqs` / `max-num-batched-tokens`**

Controls batching behavior.

Larger batches improve throughput but consume more KV cache memory. Reducing these values can reduce memory pressure at the cost of throughput.

**`tensor-parallel-size`**

Splits tensors across multiple GPUs.

This can free more per-GPU memory for KV cache, but requires multiple GPUs and fast cross-GPU communication.

**`pipeline-parallel-size`**

Distributes model layers across GPUs.

This is compatible with tensor parallelism, but tensor parallelism is more common for multi-GPU inference on one node.

**`data-parallel-size`**

Splits serving across parallel groups, including multi-node setups.

This can increase serving capacity but introduces distributed networking and scheduling complexity.

**`cpu-offload-gb`**

Allows part of the model to live in CPU memory.

This can make oversized models load, but it usually causes a large throughput penalty and is strongly discouraged for production serving unless there is no better option.

#### Practical tuning loop

```text
benchmark workload
  -> inspect vLLM logs and metrics
  -> adjust memory/concurrency parameters
  -> benchmark again
  -> lock production defaults
```

The goal is not to maximize one metric. The goal is to satisfy the service-level objective with the lowest stable GPU cost.

#### Encode this

- **KV cache is often the real runtime bottleneck**
- **context length and batch size drive memory pressure**
- **vLLM logs expose useful memory allocation details**
- **tuning should be guided by benchmark data, not guesses**

#### Recall prompt

*Why can increasing context length reduce serving throughput even when the model weights already fit in GPU memory?*

[Back to Contents](#contents)

### Autoscaling

After tuning one replica, production introduces a harder question:

**How many replicas should be running right now?**

For real-time inference, the most important signals usually include:

- **TTFT**
- **ITL**
- **queue depth**
- **running requests**
- **waiting requests**
- **KV cache pressure**

For offline inference, the focus often shifts toward:

- batch size
- total throughput
- job completion time
- GPU utilization

The challenge is that LLM request cost varies dramatically:

```text
short prompt + short answer  -> cheap request
long prompt + long answer    -> expensive request
```

So simple request counts can be misleading.

#### Horizontal Pod Autoscaler (HPA)

Kubernetes **HPA** is the native option.

It works well for many workloads but is limited for LLM serving because its common signals are:

- CPU
- memory
- custom metrics if configured

LLM inference pressure is usually dominated by **GPU**, **tokens**, and **KV cache**, not CPU alone.

#### Knative Pod Autoscaler (KPA)

**KPA** is part of Knative Serving and can scale based on request concurrency.

It has:

- **stable mode** using a longer observation window
- **panic mode** using a shorter window for rapid changes

KPA is a better fit than basic CPU-based HPA for some inference workloads, and it integrates naturally with KServe in Knative deployment mode.

But there are two LLM-specific problems:

- LLM pods can take minutes to become ready because the model must load
- request count does not equal token cost

#### Kubernetes Event-driven Autoscaling (KEDA)

[KEDA](https://keda.sh/) is often a better fit because it can scale from flexible metric queries.

For vLLM, useful metrics include:

- `vllm:num_requests_running`
- `vllm:num_requests_waiting`
- `vllm:time_to_first_token_seconds`
- `vllm:time_per_output_token_seconds`

KServe supports KEDA in **Standard** deployment mode.

Metrics can come from:

- **PodMetric**, querying the pod directly
- **External**, querying systems such as Prometheus

Direct pod metrics can reduce autoscaler latency. External metrics are more flexible because they can combine multiple sources and replicas.

#### Example 4-4. Example of KServe and KEDA

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: Meta-Llama-3-8B
  annotations:
    serving.kserve.io/deploymentMode: Standard
    serving.kserve.io/autoscalerClass: "keda"
    sidecar.opentelemetry.io/inject: "Meta-Llama-3-8B"
spec:
  predictor:
    model:
      modelFormat:
        name: huggingface
      args:
        - --model_name=llama3
        - --model_id=meta-llama/meta-llama-3-8b
    minReplicas: 1
    maxReplicas: 5
    autoScaling:
      metrics:
        - type: PodMetric
          podmetric:
            metric:
              backend: "opentelemetry"
              metricNames:
                - vllm:num_requests_running
              query: "vllm:num_requests_running"
            target:
              type: Value
              value: "4"
#        - type: External
#          external:
#            metric:
#              backend: "prometheus"
#              serverAddress: "http://prometheus.url:9092"
#              query: "vllm:num_requests_running"
```

What to notice:

- `serving.kserve.io/deploymentMode: Standard` is required for KEDA in this pattern
- `serving.kserve.io/autoscalerClass: "keda"` enables KEDA autoscaling
- OpenTelemetry sidecar injection can expose pod-local metrics
- `PodMetric` queries metrics directly from the pod
- the query can be a single metric or a PromQL-style expression
- target value `4` means scaling should react when roughly four requests are already running
- the commented `External` block shows how to query Prometheus instead

#### Emerging LLM-specific autoscaling

LLM serving is moving beyond generic autoscaling.

Disaggregated serving and prefill/decode separation require controllers that understand runtime roles, not just pod count.

[llm-d](https://llm-d.ai/) includes the **Workload Variant Autoscaler (WVA)**, which is designed for LLM workloads. WVA considers:

- what each pod can handle
- request shape and token cost
- latency objectives
- recent traffic mix
- hardware capacity

The goal is to run clusters at higher utilization while still meeting latency targets.

#### Encode this

- **LLM autoscaling should be token-aware, not only request-aware**
- **HPA is simple but usually too generic**
- **KPA helps with concurrency but startup time and token cost remain difficult**
- **KEDA can scale from vLLM-specific metrics**
- **WVA-style autoscaling is emerging for richer LLM-serving topologies**

#### Recall prompt

*Why can an autoscaler based only on request count make poor decisions for LLM inference?*

[Back to Contents](#contents)

### Optimize vLLM Startup Time

Autoscaling is only useful if new replicas become ready quickly enough.

LLMs make this hard because model artifacts can be huge. Some large models require hundreds of gigabytes or close to a terabyte of storage.

The scale-up path has several phases:

1. Runtime image provisioning
2. Model retrieval and mounting
3. Starting the runtime
4. Loading the model
5. Warming up the inference engine
6. Exposing the model

#### 1. Runtime image provisioning

The vLLM runtime image can be several gigabytes because it includes GPU framework dependencies such as CUDA.

Production guidance:

- avoid `imagePullPolicy: Always`
- prefer `IfNotPresent` when images can be cached on nodes
- use `Never` only when images are deliberately pre-pulled
- use specific image tags instead of `latest`
- prefer digest pinning for fully reproducible deployments

Example:

```text
vllm/vllm-openai:v0.12.0
vllm/vllm-openai@sha256:...
```

#### 2. Model retrieval and mounting

Model storage strategy has a major effect on startup time.

Common options:

- download from Hugging Face at startup
- download from S3-compatible storage
- copy into a PersistentVolumeClaim
- mount a PVC directly
- package the model as an OCI artifact/image

Slowest pattern:

```text
remote download -> local copy -> runtime load
```

Faster patterns avoid repeated copying:

- PVC direct mount
- OCI-style delivery
- node-local cache
- KServe local model cache

For Hugging Face or S3-backed models, KServe local model cache can reduce repeated download cost by caching based on `storageUri`.

Fast local storage such as **NVMe SSDs** is especially valuable.

#### 3. Starting the runtime

The vLLM process itself usually starts quickly.

This phase is rarely the bottleneck compared with:

- image pull
- model transfer
- GPU weight loading
- warmup

#### 4. Loading the model

Once the model files are available, vLLM must copy model weights into GPU memory.

This is often one of the most expensive startup phases.

There is a physical limit: the I/O bandwidth into GPU memory. But default loading can still be far from that limit.

Infrastructure acceleration can help. For example, **NVIDIA GPUDirect Storage** can create a more direct path between NVMe storage and GPU memory.

vLLM supports model-loading extensions such as:

- **Run:ai Model Streamer**
- **CoreWeave Tensorizer**
- **fastsafetensor**

> **OPTIMIZE MODEL LOADING**
>
> **Run:ai Model Streamer** is often the easiest to try because it can load common formats such as safetensors without requiring a different serialized model format.
>
> **Tensorizer** and **fastsafetensor** can be powerful, but usually require model preparation or a specific storage/loading setup.

#### Example 4-5. vLLM usage of Run:ai Model Streamer

```bash
vllm serve \
 --port=8080 \
 --model=/mnt/models \
 --served-model-name=meta-llama/Meta-Llama-3-8B \
 --load-format runai_streamer \
 --model-loader-extra-config '{"concurrency":16}'
```

What to notice:

- `--load-format runai_streamer` enables Run:ai Model Streamer
- `--model-loader-extra-config '{"concurrency":16}'` loads model data with 16 concurrent workers
- `tensorizer` is another possible load format, but requires Tensorizer serialization

#### 5. Warming up the inference engine

After weights are in GPU memory, the runtime still performs warmup work:

- pre-allocating KV cache memory
- profiling operations
- preparing optimized execution paths
- capturing reusable CUDA or HIP graph sequences

This warmup matters because repeatedly launching thousands of GPU kernels individually would create CPU overhead during inference.

CUDA/HIP graphs reduce that overhead by reusing captured kernel launch sequences.

#### 6. Exposing the model

After the model is loaded and the runtime is warmed up, vLLM exposes an OpenAI-compatible API and health endpoints.

The `/health` endpoint can be used for a Kubernetes readiness probe.

#### Practical startup optimization summary

The biggest startup wins usually come from:

- keeping runtime images cached on nodes
- avoiding remote model download during pod startup
- using PVC, OCI, or local model cache strategies
- using fast storage such as NVMe
- optimizing model loading with Model Streamer, Tensorizer, or similar extensions
- configuring readiness probes around actual runtime readiness

Applied together, these techniques can reduce vLLM scale-up time from many minutes to tens of seconds, depending on model size and hardware.

#### Encode this

- **Autoscaling is limited by startup time**
- **image pulls and model downloads should be removed from the hot path**
- **loading weights into GPU memory is often the main bottleneck**
- **fast storage and optimized loaders can materially reduce time-to-ready**
- **readiness should mean the model is actually ready to serve**

#### Recall prompt

*Why does model startup time make naive autoscaling less effective for LLM deployments?*

[Back to Contents](#contents)

### LLM-Aware Routing

![AI Inference on Kubernetes](<assets\AI Inference on Kubernetes.png>)

After scaling to multiple replicas, the next production question is:

**Which replica should receive each request?**

Kubernetes Services usually distribute traffic with a simple load-balancing strategy such as round robin. That works reasonably well for many stateless microservices because each request has roughly similar cost and CPU/memory are often enough to estimate load.

LLM serving breaks those assumptions.

An LLM request can vary by:

- prompt token count
- generated token count
- current queue depth
- KV cache reuse opportunity
- LoRA adapter availability
- real-time versus batch priority
- prefill/decode cost profile

So the router should understand inference-specific signals, not only endpoint availability.

#### Why ordinary round robin is weak for LLMs

Kubernetes has already needed smarter routing in other scenarios. In multi-zone cloud deployments, **topology-aware routing** helps keep traffic inside the zone where it originated.

LLM serving stretches the routing problem further. The router may need to consider:

**Each request is different**

There is no reliable correlation between input prompt size and generated output size. A short prompt can generate a long answer, and a long prompt can generate a short one.

Useful runtime signal:

```text
vllm:num_requests_waiting
```

This vLLM metric helps identify replicas that already have queued work.

**Batching**

vLLM batches requests to use GPU resources efficiently.

An LLM-aware router can improve utilization by mixing workloads, such as using offline inference requests to fill unused batch capacity while still protecting real-time traffic.

**Prefill and decode workload**

The **prefill** phase is related to prompt size and is compute-heavy. The **decode** phase generates tokens one by one and is more memory-bandwidth-sensitive.

This makes it possible to design specialized pools for large-prompt prefill and separate decode workers.

**KV cache reuse**

The model itself has no memory. Chatbots and agents often send the whole previous conversation back to the model with each new request.

If a router knows which replica already has useful KV cache blocks, it can route related requests to that replica. This is often called **prefix-aware routing** or **cache-aware routing**.

**Different service-level requirements**

Real-time traffic usually deserves higher priority than batch traffic.

A smarter scheduler can:

- prefer high-priority requests
- delay low-priority requests
- reject noncritical requests when capacity is constrained
- protect latency objectives during overload

**LoRA adapters**

**Low-Rank Adaptation (LoRA)** fine-tuning stores a small adapter layer that composes with a base model.

This is efficient because multiple fine-tuned variants can share one base model runtime. But it breaks the simple idea that one model maps to one endpoint.

The router needs to know:

```text
requested model or adapter -> runtime replica where that adapter is available
```

#### LLM-aware gateway

The common goal is a gateway that understands LLM traffic and can optimize request placement.

![LLM-aware Gateway API](<assets/LLM-aware Gateway API.png>)

**Figure 4-3. LLM-aware Gateway API**

At a high level, the gateway should be able to consider:

- model name
- adapter name
- queue depth
- runtime metrics
- token cost
- request priority
- cache locality
- rollout policy

#### Example 4-6. Serving LoRA adapters with vLLM

```bash
vllm serve meta-llama/Meta-Llama-3-8B \
    --enable-lora \
    --lora-modules my-lora-model=$HOME/.cache/huggingface/

curl localhost:8080/v1/models | jq
{
    "object": "list",
    "data": [
        {
            "id": "meta-llama/Meta-Llama-3-8B",
            "object": "model"
        },
        {
            "id": "my-lora-model",
            "object": "model"
        }
    ]
}

curl localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "my-lora-model",
        "prompt": "LoRA is a",
        "max_tokens": 10,
        "temperature": 0
    }' | jq
```

What to notice:

- the base model is served by vLLM
- `--enable-lora` enables LoRA support
- `--lora-modules` maps an adapter name to the adapter path inside the container
- the base model and LoRA adapter both appear in `/v1/models`
- the client selects the adapter by setting `"model": "my-lora-model"`

From the user perspective, the LoRA adapter behaves like another model. From the platform perspective, it is a routing and service discovery problem.

#### Gateway API

> **GATEWAY API**
>
> [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/) is the next-generation Kubernetes API for L4 and L7 routing, ingress, load balancing, and service mesh-style traffic management.
>
> It is role-oriented. Infrastructure providers, platform teams, and application teams can each own different parts of the network configuration.
>
> A route, such as an `HTTPRoute`, attaches to a `Gateway` and defines how traffic should be forwarded to services inside the cluster.

Gateway API defines routing intent. Gateway implementations, such as Envoy-based systems, perform the actual traffic handling.

#### From API Gateway to AI Gateway

Traditional API gateways were designed for mostly stateless APIs where the request is the natural accounting unit.

LLM gateways need different capabilities because the real compute unit is usually the **token**.

AI gateways support **Model as a Service (MaaS)** patterns where many teams or users consume model inference through managed APIs.

Important AI gateway capabilities include:

**Token-based rate limiting and user management**

A single LLM request may generate 10 tokens or 10,000 tokens. Request-count rate limits do not reflect GPU cost.

Projects such as [Envoy AI Gateway](https://aigateway.envoyproxy.io/) and [Kuadrant](https://kuadrant.io/) can help enforce quota and rate-limit policies closer to token consumption.
- [Envoy AI Gateway - Usage-based Rate Limiting](https://aigateway.envoyproxy.io/docs/capabilities/traffic/usage-based-ratelimiting/)
- [Kuadrant Token Rate Limiting](https://docs.kuadrant.io/1.3.x/kuadrant-operator/doc/overviews/token-rate-limiting/)

**Semantic routing**

Semantic routing sends requests to models based on the meaning of the request.

Examples:

- code requests to a code-specialized model
- general chat to a general-purpose model
- safety-sensitive requests to a stricter model or policy path

**Hybrid routing**

Hybrid routing can choose between local and remote models based on:

- current cluster load
- model availability
- latency objective
- cost
- data residency requirements

Example:

```text
normal load -> local GPU cluster
peak overflow -> cloud-hosted inference endpoint
```

**Model composition**

Some gateways are evolving toward model orchestration, where several models or services are chained together.

RAG is a common example:

```text
retriever -> reranker -> LLM -> response
```

This turns the gateway from a simple router into an inference orchestration layer.

#### Gateway API Inference Extension

[Gateway API Inference Extension](https://gateway-api-inference-extension.sigs.k8s.io/) extends Kubernetes Gateway API for AI inference workloads.

It adds inference-aware concepts such as:

- model-aware routing
- serving priorities
- incremental model rollout
- traffic splitting
- endpoint picking based on inference metrics

The key resources are:

**`InferencePool`**

Represents a group of pods serving AI models with similar compute configuration, accelerator type, or base model.

**`InferenceObjective`**

Defines serving objectives and priorities for routing decisions.

This resource is alpha and may evolve.

**Endpoint Picker**

An Endpoint Picker chooses the best endpoint from an `InferencePool`.

It can use metrics such as:

- queue length
- KV cache state
- adapter availability
- latency
- request priority

#### Example 4-7. Example of Gateway API Inference Extension usage

```yaml
apiVersion: inference.networking.k8s.io/v1
kind: InferencePool
metadata:
  name: vllm-llama3-8b-instruct
spec:
  targetPorts:
    - number: 8000
  selector:
    app: vllm-llama3-8b-instruct
  endpointPickerRef:
    name: vllm-llama3-8b-epp
    port: 9002
    failureMode: FailClose
---
apiVersion: inference.networking.x-k8s.io/v1alpha2
kind: InferenceObjective
metadata:
  name: high-priority-inference
spec:
  priority: 1
  poolRef:
    group: inference.networking.k8s.io
    name: vllm-llama3-8b-instruct
---
apiVersion: inference.networking.x-k8s.io/v1alpha2
kind: InferenceObjective
metadata:
  name: standard-inference
spec:
  priority: 2
  poolRef:
    group: inference.networking.k8s.io
    name: vllm-llama3-8b-instruct
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-llama3-8b-epp
spec:
  selector:
    app: vllm-llama3-8b-epp
  ports:
    - port: 9002
      targetPort: 9002
```

What to notice:

- `InferencePool` uses the stable `inference.networking.k8s.io/v1` API group
- `targetPorts` lists ports exposed by the model-server pods
- `selector` chooses the pods that belong to the pool
- `endpointPickerRef` references the Endpoint Picker service
- `InferenceObjective` defines serving priority
- the Endpoint Picker is exposed as a Kubernetes `Service`

#### Envoy External Processing and EPP

Gateway API Inference Extension commonly uses **Envoy** as the proxy foundation.

Envoy supports an **External Processing** filter, often called `ext_proc`, that lets an external gRPC service inspect or modify HTTP headers and request bodies.

Gateway API Inference Extension uses this idea for the **Endpoint Picker Protocol (EPP)**.

The flow is:

```text
client request
  -> Envoy gateway
  -> external processing / Endpoint Picker
  -> selected model-server endpoint
  -> vLLM replica
```

An Endpoint Picker can be deployed as its own Kubernetes Deployment, usually near the model-serving namespace. It must be reachable from the gateway and must be able to collect the metrics it needs from the vLLM pods.

The communication path can be secured with mTLS or certificate-based controls.

#### Related projects

The inference gateway space is active.

Important projects and patterns include:

- [Gateway API Inference Extension](https://github.com/kubernetes-sigs/gateway-api-inference-extension) for inference-aware Kubernetes routing APIs
- [Envoy AI Gateway](https://github.com/envoyproxy/ai-gateway) for AI gateway capabilities built on Envoy Gateway
- [vLLM Production Stack](https://github.com/vllm-project/production-stack) for production-serving patterns around vLLM
- [llm-d](https://llm-d.ai/) for large-scale LLM serving with routing, KV cache, and disaggregated serving integrations
- KServe `LLMInferenceService` for a higher-level abstraction over lower-level gateway and serving components

KServe can hide much of this low-level gateway complexity through `LLMInferenceService` and `LLMInferenceServiceConfig`, while still allowing platform teams to customize advanced routing behavior when needed.

#### Encode this

- **LLM routing should consider runtime state, not only pod availability**
- **round robin ignores token cost, queue depth, KV cache locality, and adapter placement**
- **LoRA adapters make model-to-endpoint mapping more complex**
- **Gateway API Inference Extension introduces inference-aware routing primitives**
- **Endpoint Pickers can use vLLM metrics to select better replicas**

#### Recall prompt

*Why can cache-aware or prefix-aware routing reduce LLM serving cost and latency?*

[Back to Contents](#contents)

### Disaggregated Serving

LLM-aware routing is one optimization. At very large scale, the serving architecture itself can be split into specialized parts.

**Disaggregated serving** separates LLM serving responsibilities across multiple pools and components, usually combining:

- LLM-aware routing
- distributed KV cache
- disaggregated prefill
- high-bandwidth networking
- specialized GPU placement

This is no longer a simple stateless Kubernetes Deployment. It behaves more like a production appliance built from Kubernetes resources and high-performance infrastructure.

Use it when:

- model serving scale is very high
- latency objectives are strict
- prompt lengths are large
- KV cache reuse is valuable
- the cluster has fast interconnects and careful topology design

#### Why networking becomes critical

Once runtime state such as KV cache moves between replicas, network bandwidth becomes part of the serving path.

Ordinary pod networking may be backed by Ethernet in the range of 10 to 20 Gbps.

Distributed KV cache and disaggregated prefill can require much more, often hundreds of Gbps.

Relevant technologies include:

- **NVLink**
- **NVSwitch**
- **RDMA**
- **RoCE**
- **InfiniBand**

The operational lesson is simple:

**Disaggregated serving is not just a software setting. It requires infrastructure topology planning.**

#### Distributed KV cache

The KV cache makes repeated token generation efficient.

The distributed KV cache idea is:

```text
store reusable KV blocks outside one runtime instance
  -> share them across replicas
  -> avoid repeated prefill work
```

Benefits:

- KV cache capacity is no longer limited to one replica's GPU memory
- cache blocks can be reused across replicas
- long-prompt workloads can avoid repeated compute
- RAG and agent workflows may improve significantly

The hard requirement:

**cache transfer must be extremely fast.**

Otherwise, the time saved by avoiding prefill can be lost moving cache blocks around.

Relevant projects:

- [LMCache](https://github.com/LMCache/LMCache), which provides a KV cache layer for LLM inference
- [NIXL](https://github.com/ai-dynamo/nixl), NVIDIA Inference Xfer Library, for accelerating point-to-point transfer across memory and storage types

LMCache and NIXL can be used together. For example, LMCache can manage reusable KV blocks while NIXL accelerates transfer across GPU, CPU, or storage-backed memory.

Routing still matters. Even if every replica can access distributed cache blocks, it is better to route a request to a replica that already has the needed blocks nearby.

#### Disaggregated prefill

LLM request processing has two major phases:

**Prefill**

- processes the input prompt
- produces the first token
- compute-bound
- strongly affects **Time To First Token (TTFT)**

**Decode**

- produces tokens one by one
- memory-bandwidth-sensitive
- strongly affects **Inter-Token Latency (ITL)**

Disaggregated prefill separates these into different pools:

```text
prefill pool -> KV cache transfer -> decode pool
```

This lets each phase scale independently.

Example:

- long-prompt workload -> add more prefill capacity
- long-generation workload -> add more decode capacity

The main challenge is that prefill initializes the KV cache. The decode worker needs that cache state to continue generation, so distributed KV cache or very fast transfer is required.

#### llm-d architecture

The following diagram shows an end-to-end disaggregated serving design using Gateway API, KServe `LLMInferenceService`, llm-d components, and vLLM.

![llm-d disaggregated serving architecture](<assets/llm-d disaggregated serving architecture.png>)

**Figure 4-4. llm-d disaggregated serving architecture**

Projects in this space include:

- **NVIDIA Dynamo**, focused on NVIDIA-optimized serving infrastructure
- **llm-d**, focused on integrating open source components across the Kubernetes ecosystem
- **[Mooncake](https://kvcache-ai.github.io/Mooncake/)**, which helped popularize the disaggregated prefill topology
- **LMCache** and **NIXL**, focused on KV cache and transfer acceleration

#### Operational trade-off

Disaggregated serving can improve:

- throughput
- cache reuse
- TTFT for long prompts
- hardware utilization
- independent scaling of prefill and decode

But it increases:

- platform complexity
- network requirements
- scheduler requirements
- observability needs
- component coupling
- failure-mode complexity

This pattern belongs to large-scale deployments where the savings and latency gains justify the operational cost.

#### Encode this

- **Disaggregated serving separates runtime responsibilities across specialized pools**
- **distributed KV cache helps reuse expensive prefill work**
- **prefill is compute-bound; decode is memory-bandwidth-sensitive**
- **cache movement makes high-bandwidth networking critical**
- **advanced serving topologies look more like distributed systems than ordinary Deployments**

#### Recall prompt

*Why does disaggregated prefill require fast KV cache transfer between prefill and decode workers?*

[Back to Contents](#contents)

### Lessons Learned

Production LLM inference is continuous optimization across model, runtime, and infrastructure.

**Model selection**

Model choice cannot rely only on parameter count or generic leaderboard position. Use task-specific evaluation with domain-relevant datasets.

**Compression**

Quantization and related compression techniques can reduce memory footprint and improve throughput, but they can also reduce quality. Benchmark and evaluate the compressed model before committing to it.

**Autoscaling**

LLM autoscaling differs from traditional application scaling. Token-aware metrics, TTFT, ITL, queue depth, and KV cache utilization are better signals than CPU or request rate alone.

**Startup optimization**

Scale-to-zero is often impractical for large LLMs because model loading time is measured in minutes, not milliseconds. Pre-warmed replicas and conservative minimum replica counts can protect user experience.

**Routing**

Routing affects both latency and cost. Cache-aware routing can reduce duplicate prefill work, and LoRA-aware routing can place requests where the requested adapter is already available.

**Advanced topologies**

Disaggregated serving introduces infrastructure requirements that look closer to distributed training than ordinary stateless web serving. GPU topology, network bandwidth, and scheduler behavior become first-class design concerns.

With these optimizations in place, the next operational question becomes:

**How do we know the system is actually behaving as expected?**

That leads naturally into LLM observability: metrics, logs, traces, and alerts that reveal whether the production setup is meeting its latency, reliability, and cost goals.

#### Encode this

- **Production LLM serving is a system problem, not just a model problem**
- **evaluation, compression, benchmarking, scaling, routing, and topology are connected**
- **token-aware signals are more useful than generic request metrics**
- **startup time and cache locality shape both autoscaling and routing**
- **advanced serving gains usually come with advanced operational complexity**

#### Recall prompt

*Which production signal would you trust more for LLM scaling: CPU utilization, request count, or token/queue/cache metrics, and why?*

### Production Mental Model

A production LLM serving stack is a chain:

```text
model choice
  -> evaluation
  -> compression
  -> benchmark
  -> runtime tuning
  -> autoscaling
  -> routing
  -> startup optimization
  -> distributed topology
```

Weakness in any link can waste GPU budget or degrade latency.

The Kubernetes lesson is:

**GenAI serving is still Kubernetes, but the workload semantics are different enough that ordinary container defaults are rarely sufficient.**

### Encode this

- **Production is consistency under load, not a successful first response**
- **LLM workloads need token-aware, GPU-aware operational thinking**
- **model selection, compression, tuning, benchmarking, and autoscaling are connected**
- **startup optimization is part of scalability**
- **Kubernetes provides the control plane, but LLM semantics must guide the configuration**

### Recall prompt

*What makes production LLM serving different from running a normal stateless application container on Kubernetes?*

[Back to Contents](#contents)

## High-Value Recall Checklist

Use these prompts for fast review:

- **KServe**: What problem does it solve on Kubernetes?
- **Deployment modes**: When do you choose **Knative**, **Standard**, or **ModelMesh**?
- **Core APIs**: What is the difference between **`ServingRuntime`** and **`InferenceService`**?
- **LLM APIs**: Why was **`LLMInferenceService`** introduced?
- **Operations**: Why should runtime lifecycle and model lifecycle be separated?
- **GPU sharing**: What is the difference between **time slicing**, **MPS**, and **MIG**?
- **Portability**: Why are ONNX, GGUF, and Safetensors each useful but incomplete?
- **Registry**: Why does a model registry store metadata more often than weights?
- **Hugging Face**: Why is it the default public discovery platform but not the full production answer?
- **MLflow**: Why is it strong for experimentation but weaker as a Kubernetes-native serving control plane?
- **Kubeflow**: What makes its registry more deeply integrated with Kubernetes workflows?
- **OCI Registry**: Why is storing full model artifacts there different from storing metadata in a model registry?
- **OCI**: What are the four main OCI image components?
- **Model access**: What is the difference between download-based storage initialization and direct PVC-backed mounting?
- **Production serving**: Why do model evaluation, compression, benchmarking, runtime tuning, autoscaling, startup time, routing, and disaggregated topology need to be treated as one connected system?
- **LLM-aware routing**: Why is round robin often weak for LLM replicas?
- **Disaggregated serving**: Why do distributed KV cache and disaggregated prefill require high-bandwidth networking?

### One-sentence compression

**KServe operationalizes model serving on Kubernetes, registries operationalize model discovery and governance, OCI-style artifacts improve model distribution, storage access strategy determines how efficiently models reach serving pods, and production LLM serving depends on token-aware evaluation, tuning, scaling, startup optimization, routing, and topology design.**

[Back to Contents](#contents)
