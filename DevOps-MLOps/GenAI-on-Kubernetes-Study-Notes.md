# GenAI on Kubernetes Study Notes

## Contents

1. [Purpose](#purpose)
2. [Model Servers & Controllers](#model-servers--controllers)
   - [Model Server](#model-server)
   - [vLLM](#vllm)
   - [Hugging Face Text Generation Inference (TGI)](#hugging-face-text-generation-inference-tgi)
   - [Other Model Servers](#other-model-servers)
     - [llama.cpp](#llamacpp)
     - [NVIDIA NIM](#nvidia-nim)
     - [SGLang](#sglang)
   - [Model Server Controller](#model-server-controller)
   - [KServe](#kserve)
     - [Deployment Modes](#deployment-modes)
     - [Core APIs](#core-apis)
     - [From `InferenceService` to `LLMInferenceService`](#from-inferenceservice-to-llminferenceservice)
     - [Why Runtime and Model Separation Matters](#why-runtime-and-model-separation-matters)
   - [Ray Serve and KubeRay](#ray-serve-and-kuberay)
   - [Model Serving Lessons Learned](#model-serving-lessons-learned)
3. [Kubernetes and GPUs](#kubernetes-and-gpus)
   - [GPU Discovery](#gpu-discovery)
     - [Node Feature Discovery](#node-feature-discovery)
     - [GPU Feature Discovery](#gpu-feature-discovery)
   - [Kubernetes GPU Device Plug-Ins](#kubernetes-gpu-device-plug-ins)
   - [GPU Workload Scheduling](#gpu-workload-scheduling)
     - [Label-Based Scheduling](#label-based-scheduling)
     - [Resource-Based Scheduling](#resource-based-scheduling)
     - [Dynamic Resource Allocation](#dynamic-resource-allocation)
   - [NVIDIA GPU Operator](#nvidia-gpu-operator)
     - [Operator Configuration with ClusterPolicy](#operator-configuration-with-clusterpolicy)
   - [GPU Sharing and Sub-GPU Allocation](#gpu-sharing-and-sub-gpu-allocation)
     - [Time Slicing](#time-slicing)
     - [MPS](#mps)
     - [MIG (Multi-Instance GPU)](#mig-multi-instance-gpu)
     - [Model-Serving Example: One GPU, Three Small Models](#model-serving-example-one-gpu-three-small-models)
   - [GPU Diagnostics with nvidia-smi](#gpu-diagnostics-with-nvidia-smi)
   - [Multi-GPU Inference](#multi-gpu-inference)
     - [Data Parallelism](#data-parallelism)
     - [Model Parallelism](#model-parallelism)
     - [Single-Node Versus Multinode Inference](#single-node-versus-multinode-inference)
   - [GPU Resource Optimizations](#gpu-resource-optimizations)
   - [GPU Lessons Learned](#gpu-lessons-learned)
4. [Model Data Storage, Access & Registry in K8s](#model-data-storage-access--registry-in-k8s)
   - [Model Data Storage Formats](#model-data-storage-formats)
     - [Weight-Only Formats](#weight-only-formats)
     - [Self-Contained Formats](#self-contained-formats)
     - [ONNX](#onnx)
     - [Safetensors](#safetensors)
     - [GGUF and GGML](#gguf-and-ggml)
     - [Current State and Gaps in Model Portability](#current-state-and-gaps-in-model-portability)
   - [Model Registry](#model-registry)
     - [Hugging Face Model Hub](#hugging-face-model-hub)
     - [MLflow Model Registry](#mlflow-model-registry)
     - [Kubeflow Model Registry](#kubeflow-model-registry)
     - [OCI Registry](#oci-registry)
     - [OCI Images](#oci-images)
   - [Accessing Model Data in Kubernetes](#accessing-model-data-in-kubernetes)
     - [KServe `storageUri` and Storage Initializers](#kserve-storageuri-and-storage-initializers)
     - [Built-in KServe Storage Initializers](#built-in-kserve-storage-initializers)
     - [Shared Storage with PersistentVolumes](#shared-storage-with-persistentvolumes)
     - [OCI Image for Storing Model Data](#oci-image-for-storing-model-data)
       - [Modelcars](#modelcars)
       - [OCI Image Volume Mounts](#oci-image-volume-mounts)
   - [Model Data Lessons Learned](#model-data-lessons-learned)
5. [Running in Production](#running-in-production)
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
6. [Model Observability](#model-observability)
   - [Observability Stack and Configuration](#observability-stack-and-configuration)
     - [Logs](#logs)
     - [Metrics](#metrics)
     - [Tracing](#tracing)
   - [Model Server Metrics](#model-server-metrics)
     - [Time To First Token](#time-to-first-token)
     - [Time Per Output Token or Inter-Token Latency](#time-per-output-token-or-inter-token-latency)
     - [Throughput](#throughput)
     - [Latency](#latency)
     - [Request Queue Metrics](#request-queue-metrics)
     - [SLI, SLO, and SLA](#sli-slo-and-sla)
   - [GPU Usage Monitoring](#gpu-usage-monitoring)
   - [Quality Metrics](#quality-metrics)
   - [Responsible AI](#responsible-ai)
     - [Explainability](#explainability)
     - [Fairness](#fairness)
   - [Model Safety: Hallucination and Guardrails](#model-safety-hallucination-and-guardrails)
     - [Understanding and Detecting Hallucinations](#understanding-and-detecting-hallucinations)
     - [Runtime Guardrails](#runtime-guardrails)
     - [NVIDIA NeMo Guardrails](#nvidia-nemo-guardrails)
     - [FMS Guardrails Orchestrator](#fms-guardrails-orchestrator)
     - [Guardrails AI](#guardrails-ai)
     - [Llama Stack and Moderation APIs](#llama-stack-and-moderation-apis)
   - [Observability Lessons Learned](#observability-lessons-learned)
7. [Model Customization](#model-customization)
   - [Introduction to LLM Creation](#introduction-to-llm-creation)
   - [Prompt and Context Engineering](#prompt-and-context-engineering)
   - [When to Use Model Customization](#when-to-use-model-customization)
   - [Tuning a Model](#tuning-a-model)
     - [Fine-Tuning](#fine-tuning)
     - [Parameter-Efficient Fine-Tuning](#parameter-efficient-fine-tuning)
     - [Low-Rank Adaptation](#low-rank-adaptation)
   - [Running Tuning Jobs on Kubernetes](#running-tuning-jobs-on-kubernetes)
     - [Kubeflow Trainer](#kubeflow-trainer)
       - [Two personas, two APIs](#two-personas-two-apis)
       - [`TrainingRuntime` and `ClusterTrainingRuntime`](#trainingruntime-and-clustertrainingruntime)
       - [`BuiltinTrainer` vs `CustomTrainer`](#builtintrainer-vs-customtrainer)
       - [`TrainJob` → `JobSet` → Kubernetes Jobs](#trainjob--jobset--kubernetes-jobs)
       - [Example 6-3. Installing Kubeflow Trainer](#example-6-3-installing-kubeflow-trainer)
       - [Example 6-4. `ClusterTrainingRuntime`](#example-6-4-clustertrainingruntime)
       - [Example 6-5. Trainer function using Hugging Face TRL as a `CustomTrainer`](#example-6-5-trainer-function-using-hugging-face-trl-as-a-customtrainer)
       - [Example 6-6. Create `TrainJob` via Kubeflow SDK](#example-6-6-create-trainjob-via-kubeflow-sdk)
       - [Example 6-8. Merge LoRA adapter with the base model](#example-6-8-merge-lora-adapter-with-the-base-model)
       - [Storage and operational considerations](#storage-and-operational-considerations)
       - [Orchestration vs. distribution strategy: where does FSDP live?](#orchestration-vs-distribution-strategy-where-does-fsdp-live)
       - [Example — Self-contained FSDP `CustomTrainer`](#example--self-contained-fsdp-customtrainer)
       - [Where do `LOCAL_RANK`, `RANK`, `WORLD_SIZE`, … come from?](#where-do-local_rank-rank-world_size--come-from)
       - [Why Kubernetes / Kubeflow Trainer instead of just `torchrun`?](#why-kubernetes--kubeflow-trainer-instead-of-just-torchrun)
     - [Other Frameworks](#other-frameworks)
       - [DeepSpeed](#deepspeed)
       - [Ray](#ray)
         - [Ray vs Kubeflow Trainer — code delivery differences](#ray-vs-kubeflow-trainer--code-delivery-differences)
       - [Unsloth](#unsloth)
   - [Customization Lessons Learned](#customization-lessons-learned)
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

## Model Servers & Controllers

Deploying a generative AI model on Kubernetes is not just running yet another container — it requires **two distinct layers**:

- a **model server** (also called *serving runtime*) that loads the model into accelerators and exposes an API to clients
- a **model server controller** that manages the lifecycle of the model server through declarative Kubernetes resources

This section walks through both layers, starting with what a model server is and how the most common open source implementations differ, then moving to the controllers (**KServe**, **Ray Serve**) that orchestrate them on Kubernetes.

[Back to Contents](#contents)

### Model Server

A **model server** (or **serving runtime**) is a component that includes one or more runtimes. It can be **distributed to use multiple GPUs simultaneously** and execute various types of models.

Models are exposed via an **API (REST or gRPC)** and optimized to **maximize throughput** and **minimize latency**.

![Model server architecture](<assets/Model server architecture.png>)

**Figure 1-1. Model server architecture**

#### Not new, but not the same as predictive AI

The model-server concept is not new or specific to generative AI:

- multiple existing model servers serve **traditional ML models** for tasks like classification and regression (collectively known as **predictive AI**)
- some of them are also evolving to support generative AI
- the **concept is the same**, but the **exposed API is very different**

The API difference:

- **Predictive AI** — endpoint is usually a generic `/predict` or `/infer` because the model acts as a **black-box function**
- **Generative AI** — the API is **task-oriented** because similar models can perform different actions and modalities: text generation, summarization, classification, text-to-image, etc.

> **NOTE**
>
> Model servers expose the AI model via an API that clients have to use. This API can be specific to a particular model server implementation, **breaking the abstraction** that the model server aims to provide because client applications should not be tied to a specific implementation.
>
> This problem is not new or specific to generative AI. For predictive AI, the **KServe open-inference-protocol (OIP)** defines a specification to standardize "infer" endpoints. Most model servers have adopted it, and it's now expanding to include generative AI.
>
> The API to invoke generative AI models is still **experimental overall** and very different based on the model type and task. **OpenAI's Chat Completions API** for chat completion is a **de facto standard** for text generation models.

From a Kubernetes platform perspective, every model server is usually similar in terms of **deployment topology**. However, you should be aware of the **type of model and task** because the **scaling, hardware optimization, and metrics** to observe are **model-server specific**.

> **MULTIMODAL MODELS**
>
> Many LLMs work with just one modality: input and output are text. **Multimodal models** can process a larger set of modalities — images, video, audio, mathematical equations, and so on.
>
> The main goal is to **mix modalities** to perform tasks like text-to-image (textual query → generated image). It's possible to do the opposite, or mix multiple modalities in the same query (image + text → new image or text).
>
> From an architecture perspective:
>
> - many popular image/audio generation models use **diffusion-based architectures** (like **Stable Diffusion**)
> - others use **Transformer architectures** (like **DALL-E**, **Imagen**, and **AudioLM**)
>
> This category is part of generative AI but is **not LLMs**. They are widely adopted in healthcare, ecommerce, and content creation, but there is **less standardization** around them compared to text generation models. They're often integrated into specialized products like image editors and chat interfaces.
>
> These notes assume **LLM Transformer bases** applicable to a larger set of use cases. The model output is text, but inputs can include images and audio together with text, making them multimodal models.

#### Encode this

- **Model server = runtime + API + GPU optimization layer**
- **Same concept for predictive and generative AI, different APIs**
- **OIP standardizes `/infer`; OpenAI Chat Completions is the de facto generative-AI standard**
- **Kubernetes deployment topology is similar across model servers; scaling and metrics are not**

#### Recall prompt

*Why do generative-AI APIs look different from predictive-AI APIs even though the underlying "model server" concept is the same?*

[Back to Contents](#contents)

### vLLM

**[vLLM](https://github.com/vllm-project/vllm)** is a **Linux Foundation AI & Data project** for LLM inference and serving.

The project is very active:

- thousands of forks
- hundreds of contributors
- support for **more than fifty model architectures**
- end-to-end optimization techniques
- support for **multiple hardware vendors**

vLLM is a library directly usable in Python, but the project also includes a **CLI** and an **OpenAI-compatible server**.

#### Example 1-3. Load a model in vLLM and execute inference

```python
from vllm import LLM

# Load the model
llm = LLM(model="meta-llama/Meta-Llama-3-8B")
# Invoke the model
results = llm.generate("LLMs are great for")

# Extract the result
print(results[0].outputs[0].text)
```

For Kubernetes deployment, vLLM should be run in a container, making a **server** the best option. Starting the server requires **minimal configuration**, but a key difference in production is that you will likely use a **local copy of the model** rather than fetching it on the fly from Hugging Face.

#### Example 1-4. Start vLLM server and invoke via `curl`

```bash
# start the server
vllm serve \
 --port=8080 \
 --model=/mnt/models \
 --served-model-name=meta-llama/Meta-Llama-3-8B

# invoke the model
curl http://localhost:8080/v1/completions \
 -H "Content-Type: application/json" \
 -d '{
  "model": "meta-llama/Meta-Llama-3-8B",
  "prompt": "LLMs are great for",
  "max_tokens": 10,
  "temperature": 0
 }'
```

What to notice:

- **`vllm serve`** starts the vLLM server
- **`--model`** is the path to the directory containing the model (local to the container)
- **`--served-model-name`** is the name of the model
- **`max_tokens`** is the number of tokens the model should produce
- **`temperature`** controls the randomness of the sampling; **`0` makes the generation deterministic**

#### Kubernetes implications

Many parameters configure how the runtime loads and executes the model, but this is **relatively transparent** from a deployment standpoint.

Optimizations such as:

- **PagedAttention**
- **FlashAttention**
- **speculative decoding**

…focus on **efficient attention management** and **faster execution**. They don't impact deployment directly, but they affect **scalability and resource optimization**.

> **LLM INFERENCE OPTIMIZATION**
>
> The optimization of LLM execution is a **rapidly evolving field** with continuous advancements. Academia and engine implementation are closely coupled in this domain.
>
> New optimization techniques emerge frequently, and proper evaluation requires time to assess their practical benefits.
>
> Key optimizations:
>
> - **PagedAttention** and **FlashAttention** — make self-attention faster given the **quadratic time and memory complexity** of this phase, optimizing memory management
> - **Quantization** — reduces the floating-point size of the model weights, using multiple techniques aimed at minimizing performance loss
> - **Model distillation** — trains a smaller **"student" model** to approximate a larger **"teacher" model's** behavior, reducing model size significantly while retaining much of the original capability
> - **Speculative decoding** — leverages a two-model approach: a small, fast **"draft" model** predicts several tokens ahead, and the large model **verifies** those predictions in a single pass. By running the expensive large model less frequently while maintaining the same output quality, speculative decoding can improve throughput by **1.5× to 3×**, depending on how predictable the sequence is
>
> From an MLOps engineer perspective, **you don't need to be an expert in LLM optimization internals**. Use a model server that is actively developed with a large community so that every new optimization is included.
>
> The configuration of vLLM is usually limited to changing the **startup parameters** of the runtime, and the project is getting better at automatically detecting which configuration to apply based on the model — so the **default values will most likely work**.
>
> Some configuration (like **quantization**) affects model quality and requires tuning to find the right trade-off. This is part of model development and tuning, so at inference time you should already have the configuration as part of the deployment.

<u>Important for MLOps:</u> be aware of parameters with larger implications on **parallelization and scaling**. Multinode distributed serving impacts overall topology, usually requires additional components to manage coordination, and makes the deployment **stateful**.

#### Encode this

- **vLLM = the most-active open source LLM server, with Python API + OpenAI-compatible server**
- **`vllm serve --model --port --served-model-name` is the minimum to launch a production server**
- **PagedAttention, FlashAttention, speculative decoding live inside vLLM — invisible to deployment manifests, visible in throughput**
- **Multinode = stateful + coordinated**

#### Recall prompt

*Why can an MLOps engineer rely on vLLM defaults for most LLM optimizations rather than deeply tuning attention mechanisms?*

[Back to Contents](#contents)

### Hugging Face Text Generation Inference (TGI)

The **[Hugging Face Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference)** is an open source model server created to serve text generation models and used to power Hugging Face's product offering.

Hugging Face is the most active community where you can share generative AI models (base or fine-tuned), datasets, and libraries. Many widely used libraries — **`transformers`**, **`peft`**, **`diffusers`** — are incubated in this community.

#### Multi-backend support

TGI supports **multiple inference backends**, allowing you to choose the most appropriate backend for your hardware and performance requirements while maintaining a **consistent API**. Supported backends:

- **TGI's native CUDA backend** (optimized for NVIDIA GPUs)
- **NVIDIA TensorRT-LLM**
- **`llama.cpp`** (for CPU deployment)
- **AWS Neuron** (for AWS **Trainium** and **Inferentia** chips)

Multi-backend support is an **emerging trend** in model servers, with projects like **Triton** and **TGI** adopting this approach to provide flexibility in deployment options.

<u>Trade-off:</u> while backends are exposed through a **unified API** (such as OpenAI-compatible endpoints), the **configuration parameters and tuning options vary significantly across backends**. This can complicate optimization and debugging when switching between backends or fine-tuning performance.

#### Example 1-5. Start the TGI server with native and OpenAI APIs

```bash
# start the server
text-generation-launcher \
 --port 8080 \
 --model-id /mnt/models

# invoke the model using TGI API
 curl localhost:8080/generate_stream \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{"inputs":"LLMs are great for",
     "parameters":{"max_new_tokens":10}
     }'

# invoke the model using OpenAI-compatible API
curl localhost:3000/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
  "model": "tgi",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "LLMs are great for"
    }
  ],
  "max_tokens": 10
}'
```

What to notice:

- **`text-generation-launcher`** is the launcher command
- **`--model-id`** points to the directory containing the model (local to the container)
- **`/generate_stream`** is TGI's **original API** to invoke the model
- **`/v1/chat/completions`** is TGI's **OpenAI-compatible API**
- the **`system`** role defines the **role of the model** — one of the most common categories of fine-tuned models is **"instruct" models**, designed to follow human instructions

The comments about parameters and their implications for Kubernetes apply to TGI as well.

#### Encode this

- **TGI = Hugging Face's model server, with multi-backend support (CUDA, TensorRT-LLM, llama.cpp, AWS Neuron)**
- **Multi-backend = unified API + non-unified tuning**
- **TGI exposes both its own `generate_stream` API and an OpenAI-compatible API**
- **Instruct models use a `system` role to define model behavior**

#### Recall prompt

*What is the trade-off of TGI's multi-backend architecture compared with a single-backend model server like vLLM?*

[Back to Contents](#contents)

### Other Model Servers

While vLLM and TGI are commonly used open source model servers for LLMs, other implementations deserve consideration for **specific deployment scenarios** and **hardware configurations**.

#### `llama.cpp`

**[`llama.cpp`](https://github.com/ggerganov/llama.cpp)** is a **C++ implementation** that runs Llama models.

History and evolution:

- originally created as a full **re-implementation of the Transformer architecture in C++** specifically for Llama models
- evolved to support a variety of other models
- focus has been on **efficiency**, making it the recommended option for running similar models **locally on a laptop**

It still requires a powerful machine but is widely used by projects such as:

- **Ollama**
- **Ramalama**
- **LM Studio**

While it is not designed for large-scale production deployments with high concurrency, `llama.cpp` **excels in resource-constrained environments**. An active community continues to port optimizations and techniques from other model servers to C++, making `llama.cpp` increasingly powerful for **edge scenarios** such as on-device inference and local development.

One result of `llama.cpp`'s development is the creation of the **GGUF file format**, which other libraries have now adopted.

In addition to the core library, there is a Python server that exposes an **OpenAI-compatible API** similar to other model servers.

##### Example 1-6. Start the `llama.cpp` Python server

```bash
python -m llama_cpp.server \
 --model /mnt/models
```

What to notice:

- **`python -m llama_cpp.server`** starts the `llama.cpp` server
- **`--model`** is the location of the model (local to the container)

> **TIP — Running quantized LLMs locally**
>
> Assuming you have a powerful machine with at least **24 GB of memory**, but **even without a GPU**, running quantized LLMs locally is remarkably straightforward using tools built on top of `llama.cpp`.
>
> **Ollama** provides a simple CLI interface to download and run models with a single command:
>
> ```bash
> ollama run llama3.2:3b
> ```
>
> **Ramalama** offers similar simplicity with support for multiple model registries and container runtimes:
>
> ```bash
> ramalama run llama3.2:3b
> ```
>
> Both tools use `llama.cpp` behind the scenes and expose an **OpenAI-compatible API** for inference.
>
> - **Ramalama** provides **stronger isolation** through container-based execution
> - **Ollama** offers a **more polished developer experience** with easier model management
>
> Both are ideal for **local development, experimentation, and prototyping** before deploying to production Kubernetes clusters.

#### NVIDIA NIM

NVIDIA is the leading provider of GPUs for AI and also provides the necessary software to train and serve models. **NVIDIA NIM** is a solution designed for Kubernetes to **simplify the deployment and optimization** of an LLM on NVIDIA hardware.

It takes a different approach with a **curated container image per model family**, where models are directly tested and published by NVIDIA. Supported models (like **Llama** and **Mistral**) are listed in the NVIDIA documentation.

This approach aims to simplify the deployment configuration by providing **pre-optimized model profiles**.

##### Multi-backend support and selection

Similar to TGI, NVIDIA NIM supports multiple inference backends:

- **TensorRT-LLM** (an open source library for optimizing LLM inference on NVIDIA GPUs)
- **vLLM**
- **SGLang**

NIM **automatically selects** the optimal backend based on available model profiles for the detected GPU hardware, with a **preference order**:

```text
TensorRT-LLM > vLLM > SGLang
```

The selection is automatic based on the availability of pre-optimized TensorRT engines and other parameters. This **hardware-aware backend selection** allows users to benefit from the most suitable inference engine **without manual configuration**.

##### Opinionated design features

Beyond backend selection, NVIDIA NIM stands out due to its **opinionated design**:

- **Local caching of the model** — supported by a **`PersistentVolume`**, aiming to simplify and speed up one of the major pain points of model serving for LLMs: **loading time**. The model is downloaded only once; subsequent replica creations or restarts **do not trigger another download**
- **Hardware optimization** — NVIDIA NIM can **detect available accelerators**, select the most suitable **model variant** for the configuration, and **adjust the model server settings accordingly**

![NVIDIA NIM architecture](<assets/NVIDIA NIM architecture.png>)

**Figure 1-2. NVIDIA NIM architecture**

#### SGLang

**[SGLang](https://github.com/sgl-project/sglang)** is an open source **high-performance serving framework** for large language models and vision-language models, designed to deliver **low-latency, high-throughput inference**.

The project has gained significant industry adoption and is notable for its **advanced optimization techniques**.

Many performance improvements have been driven by the SGLang project, for example:

- **RadixAttention** — a sophisticated caching mechanism that stores **key-value (KV) caches in a radix tree structure**. This enables **efficient prefix search and cache reuse** across requests, particularly beneficial for:
  - workloads with **common prompt prefixes**
  - **multiturn conversations** where previous context can be reused
- **continuous batching**
- **speculative decoding**
- various **quantization techniques**

Like vLLM and TGI, SGLang exposes an **OpenAI-compatible API** and supports most LLM model architectures.

##### Example 1-7. Start an SGLang server

```bash
python -m sglang.launch_server \
 --model-path /mnt/models \
 --port 8080
```

What to notice:

- **`python -m sglang.launch_server`** launches the SGLang server
- **`--model-path`** is the path to the model directory (local to the container)

**Best fit:** scenarios requiring **high cache hit rates**, such as **agents** making multiple calls with similar contexts, or applications with **structured prompts** where prefix reuse is common.

#### Encode this

- **`llama.cpp` = C++ efficiency, ideal for laptops and edge; the origin of the GGUF format**
- **Ollama and Ramalama wrap `llama.cpp` for one-command local model running**
- **NVIDIA NIM = curated container per model family, with auto-selected backend (TensorRT-LLM > vLLM > SGLang) and PV-backed model caching**
- **SGLang = high-performance server known for RadixAttention prefix caching, great for agents and multiturn chats**

#### Recall prompt

*Which model server would you reach for first when serving an agent workflow that reuses long shared prompt prefixes, and why?*

[Back to Contents](#contents)

### Model Server Controller

Deploying models to Kubernetes manually requires managing numerous resources:

- **Deployments**
- **`PersistentVolumeClaim`**s
- **GPU configurations**
- **tolerations**
- **model-specific parameters**

**Model server controllers** simplify this complexity by providing **higher-level abstractions** through **CustomResourceDefinitions (CRDs)**.

Instead of manually crafting deployment manifests and coordinating multiple Kubernetes resources, controllers allow you to **declare your intent at a higher level**. The CRD approach also provides **centralized status information**, making it easier to **monitor the health and state** of model deployments.

![Model server controller architecture](<assets/Model server controller architecture.png>)

**Figure 1-3. Model server controller architecture**

#### Container image gotcha

Each model server usually provides container images so that you do not need to build them. At the same time, **picking the right container image is not straightforward**:

- each accelerator has different drivers and frameworks (e.g., NVIDIA with **CUDA**, AMD with **ROCm**, etc.)
- you must **pay attention to this aspect**

This concern is similar to **multiarchitecture containers**, where you can easily select the architecture (e.g., **ARM64** or **i386**) and get the appropriate container version. However, for **accelerators**, the process is still **quite manual**.

For more on how Kubernetes manages GPU and accelerator access through device plug-ins, see [Kubernetes and GPUs](#kubernetes-and-gpus).

The two main controller approaches in this space:

- **KServe** — Kubernetes-native
- **Ray Serve** (via **KubeRay**) — Python-first

#### Encode this

- **Controllers = CRDs + Kubernetes controllers that orchestrate model servers declaratively**
- **They turn "build a manifest for each piece" into "declare intent"**
- **Accelerator-aware container image selection remains manual (no auto-architecture matrix yet)**

#### Recall prompt

*What problem does a model server controller solve that a vanilla Kubernetes Deployment cannot?*

[Back to Contents](#contents)

### KServe

**[KServe](https://kserve.github.io/website/)** is a **CNCF project** for **model inference on Kubernetes**.

Its job is to help manage the **lifecycle**, **deployment**, and **exposure** of model-serving endpoints using Kubernetes-native patterns.

#### What KServe gives you

- **Scalability**
- **Routing**
- **Canary rollout**
- **Density packing**
- **Declarative model serving**

#### Historical context

- Originally created as **KfServing** in the **Kubeflow** community
- Later became an **independent project**
- Still remains part of the broader **Kubeflow ecosystem**
- First focused on **predictive AI**
- Later evolved to support **generative AI**

#### Key idea to remember

**KServe extends Kubernetes with custom APIs for model serving.**

That means model serving becomes a **declarative Kubernetes problem**, not just an application container problem.

#### Encode this

- **KServe = Kubernetes-native model inference platform**
- **Predictive AI first, generative AI later**
- **Uses CRDs to represent serving concepts declaratively**

#### Recall prompt

*Why is KServe more than just "running a model in a container"?*

[Back to Contents](#contents)

#### Deployment Modes

KServe supports **three deployment modes**:

1. **Knative**
2. **Standard**
3. **ModelMesh**

![KServe Standard, Knative, and LLMInferenceService deployment architecture](<assets/KServe Standard, Knative, and LLMInferenceService deployment architecture.png>)

**Figure 1-4. KServe Standard, Knative, and LLMInferenceService deployment architecture**

> **TIP — Renamed in KServe 0.16**
>
> The deployment modes have been renamed for clarity:
>
> - **Serverless** is now **Knative**, which reflects the underlying technology (Knative Serving)
> - **RawDeployment** is now **Standard**, a more intuitive name for standard Kubernetes deployments
> - **ModelMesh** remains unchanged
>
> Throughout these notes the new terminology is used. If you're using older KServe versions (pre 0.16), substitute "Knative" for "Serverless" and "Standard" for "RawDeployment."

The **ModelMesh** deployment mode is not really applicable to generative AI: the **size and complexity** of similar models doesn't give you the option to deploy multiples of them on the same node.

The **Knative** and **Standard** deployment modes are generally applicable to generative AI. However:

- smaller models such as **Phi**, **Gemma**, and Llama's compact variants (sub-30B parameters) can run on consumer hardware and may benefit from **dynamic scaling**
- larger production LLMs typically require **dedicated GPU resources** that are managed statically
- this makes it challenging to fully use the **dynamic autoscaling advantages** of Knative mode

For LLM workloads, **Standard** is the assumed default deployment mode in the rest of this section.

##### 1. Knative

**Knative** is the most feature-rich mode.

It uses **Knative** and **Istio** for:

- **Autoscaling**
- **Rolling updates**
- **Traffic management**
- **Composition**

In this mode, each model becomes a **KnativeService**.

**Best mental model:** KServe delegates much of the dynamic serving behavior to the Knative ecosystem.

##### 2. Standard

**Standard** is the simplest and most Kubernetes-direct mode.

It adds **no extra major dependency** beyond Kubernetes primitives. For each model, KServe creates a **Deployment**.

This is usually the most practical choice for **LLM serving**, especially when GPUs are **dedicated and statically allocated**.

**KServe 0.16 note:**

- `RawDeployment` was renamed to **Standard**
- `Serverless` was renamed to **Knative**

##### 3. ModelMesh

**ModelMesh** is optimized for **high-density serving** where **many models** must share cluster resources.

The model server can **load and unload models dynamically** based on requests.

This is useful when:

- You need to serve **many small or medium models**
- Running one deployment per model is too expensive

This is **generally not a fit for large generative AI models**, because large LLMs are too heavy to pack densely on the same nodes.

##### Best practical takeaway

For **modern LLM workloads**:

- **Standard** is often the default practical choice
- **Knative** can help for smaller models and elastic patterns
- **ModelMesh** is usually not the right match for large LLMs

##### Encode this

- **Knative = dynamic, feature-rich, extra stack**
- **Standard = simple, direct, deployment-per-model**
- **ModelMesh = many models, dense sharing**

##### Recall prompt

*Why does Standard often make more sense than Knative for production LLMs on GPUs?*

[Back to Contents](#contents)

#### Core APIs

The two main APIs to remember are:

1. **`ServingRuntime`**
2. **`InferenceService`**

##### `ServingRuntime`

A **`ServingRuntime`** is basically a **model server template**.

It defines:

- The **container image**
- Startup **arguments**
- The type of **model formats** it supports
- Runtime-level defaults and behavior

This separates **runtime configuration** from **model configuration**.

There is also **`ClusterServingRuntime`**, which makes a runtime available cluster-wide.

##### What to remember

**`ServingRuntime` describes how to serve.**

Not the specific model itself, but the **runtime environment** that can serve models.

##### Example idea

For vLLM, a `ServingRuntime` can define:

- `image: vllm/vllm-openai:latest`
- exposed port
- startup arguments like `--model` and `--port`
- support for `pytorch` models

##### Example 1-10. KServe `ServingRuntime` for vLLM

```yaml
apiVersion: serving.kserve.io/v1alpha1
kind: ServingRuntime
metadata:
  name: vllm
spec:
  containers:
    - args:
        - --model
        - /mnt/models/
        - --port
        - "8080"
      name: kserve-container
      image: vllm/vllm-openai:latest
      ports:
        - containerPort: 8080
          name: http1
          protocol: TCP
  multiModel: false
  supportedModelFormats:
    - autoSelect: true
      name: pytorch
```

What to notice:

- **`metadata.name: vllm`** — the name of this custom `ServingRuntime`. KServe includes pre-configured `ServingRuntimes` (including one named **"HuggingFace Runtime"** that uses vLLM) that can be used directly. This example defines a custom vLLM `ServingRuntime` to have **full control** over configuration and parameters
- **`spec.containers`** — the `podSpec` where all parameters necessary to run the model server are configured
- **`image: vllm/vllm-openai:latest`** — applying this resource will **not deploy** the model server immediately; it will make it **available within the namespace** for use
- **`supportedModelFormats: pytorch`** — vLLM, like most model servers, uses **PyTorch** as the actual runtime, so this configuration declares that this runtime is able to serve PyTorch models

##### `InferenceService`

An **`InferenceService`** represents the **actual model deployment** the user wants to serve.

It defines:

- The **model format**
- The **runtime** to use
- The **model location**
- Per-model **resource overrides**
- The deployment behavior

When this resource is created, KServe deploys the model server and wires the model to it.

##### What to remember

**`InferenceService` describes what to serve.**

This is the object that points to the model and triggers actual serving.

##### Example 1-11. `InferenceService` with Standard deployment mode

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: Meta-Llama-3-8B
  annotations:
    serving.kserve.io/deploymentMode: Standard
spec:
  predictor:
    model:
      modelFormat:
        name: pytorch
      runtime: vllm
      storageUri: pvc://llama/model
    containers:
      resources:
        limits:
          cpu: "4"
          memory: 50Gi
          nvidia.com/gpu: "1"
        requests:
          cpu: "1"
          memory: 50Gi
          nvidia.com/gpu: "1"
```

What to notice:

- **`serving.kserve.io/deploymentMode: Standard`** — the annotation selects the deployment mode
- **`modelFormat.name: pytorch`** — declaring the model type allows KServe to automatically find a matching `ServingRuntime`
- **`runtime: vllm`** — explicitly references the `ServingRuntime` by name, providing the container image and configuration for the `InferenceService`
- **`storageUri: pvc://llama/model`** — specifies where to get the model, in this case from a **PVC local to the cluster**
- **`containers.resources`** — for each model, it is possible to **override the resources** to match the requirements of the model

##### Useful mapping

- **`ServingRuntime` = server template**
- **`InferenceService` = model serving instance**

##### Minimal mental model

Platform team:

- Owns **runtime images**, defaults, and serving stack choices

Model or application team:

- Owns **which model gets deployed**, where it lives, and model-specific resources

##### Other useful KServe concepts

KServe also supports:

- **Inference logging**
- **Preprocessing and postprocessing**
- **InferenceGraph** for model composition
- **Storage initializer** for downloading model files into the serving container
- **ClusterStorageContainer** for custom storage-loading behavior

##### Encode this

- **`ServingRuntime` = how**
- **`InferenceService` = what**
- **Storage initializer = fetches model artifacts before serving**

##### Recall prompt

*If you want to upgrade the model server image without changing the model itself, which resource concept matters most?*

[Back to Contents](#contents)

#### From `InferenceService` to `LLMInferenceService`

KServe 0.16 introduced **`LLMInferenceService`**, a new CRD designed specifically for **large-scale LLM deployments**.

This exists because traditional `InferenceService` is sufficient for **basic serving**, but not ideal for **advanced LLM production topologies**.

##### Why `LLMInferenceService` exists

Large LLM systems often need:

- **Intelligent routing**
- **KV cache-aware scheduling**
- **Disaggregated serving**
- **Multinode distributed inference**
- **Parallelism across multiple GPUs**

These needs go beyond basic model serving.

##### Related config object

KServe also adds **`LLMInferenceServiceConfig`**, which acts like a **base configuration template**.

It can define shared settings such as:

- Container image
- Runtime arguments
- Resource defaults
- Router settings
- Parallelism settings

Then **`LLMInferenceService`** references that config and can override selected values.

##### Important implementation detail

`LLMInferenceService` uses **Standard deployment mode** under the hood.

That reflects an important shift:

**LLM workloads prioritize stability, predictability, and intelligent routing over fast scale-to-zero style elasticity.**

##### Key capabilities

- **Gateway / router / scheduler**
- **KV cache-aware scheduling**
- **Tensor parallelism**
- **Data parallelism**
- **Expert parallelism**
- **Horizontal replicas**

##### Example 1-12. `LLMInferenceService` with distributed inference and base configuration

```yaml
# Base configuration template
apiVersion: serving.kserve.io/v1alpha1
kind: LLMInferenceServiceConfig
metadata:
  name: vllm-llama-config
spec:
  template:
    containers:
      - name: kserve-container
        image: vllm/vllm-openai:latest
        args:
          - --port=8080
          - --model=/mnt/models
        resources:
          limits:
            nvidia.com/gpu: "1"
            cpu: "4"
            memory: 50Gi
  router:
    gateway: {}
    route: {}
    scheduler: {}
  parallelism:
    tensorParallelism: 2
---
# Actual LLM deployment
apiVersion: serving.kserve.io/v1alpha1
kind: LLMInferenceService
metadata:
  name: llama-3-8b
spec:
  baseRefs:
    - vllm-llama-config
  model:
    uri: pvc://llama/model
    name: meta-llama/Llama-3.1-8B-Instruct
  replicas: 3
  # Optionally override base configuration here
  ...
```

What to notice:

- **`image: vllm/vllm-openai:latest`** + `args` — vLLM container image and startup parameters for serving the model
- **`router`** — specification with **gateway**, **route**, and **scheduler** for **intelligent routing** with **KV cache-aware scheduling**
- **`parallelism`** — strategies for distributed inference: **tensor**, **data**, and **expert** parallelism
- **`baseRefs`** — reference to the base configuration template; **multiple configs can be referenced**, with the **last one taking precedence**
- **`model`** — model specification defining the source and characteristics
- **`replicas: 3`** — number of replicas for horizontal scaling; can override the base configuration

##### Comparison: predictive-AI vs generative-AI KServe APIs

**Table 1-1. Comparison of KServe APIs for predictive AI and generative AI**

| Aspect | `InferenceService` + `ServingRuntime` | `LLMInferenceService` + `LLMInferenceServiceConfig` |
| --- | --- | --- |
| **Primary use case** | Predictive AI (classification, regression) | Generative AI (LLMs, text generation) |
| **Deployment patterns** | Single-node, simple scaling | Multinode distributed inference, disaggregated serving |
| **Configuration template** | `ServingRuntime` defines model server template | `LLMInferenceServiceConfig` defines base LLM configuration with **inheritance** |
| **Routing and scheduling** | Basic load balancing | Advanced routing with **gateway**, **scheduler**, and **KV cache-aware scheduling** |
| **Parallelism support** | Limited | Native support for **tensor**, **data**, and **expert** parallelism |
| **Typical model size** | Small to medium models | Large models (**7B–405B+ parameters**) |

These features are particularly important for deploying **very large models (70B+ parameters)** that require multiple GPUs or sophisticated serving architectures. For more details on distributed inference patterns, see the [llm-d project](https://llm-d.ai/) and [Disaggregated Serving](#disaggregated-serving).

##### Simple comparison

**Traditional path**

- `ServingRuntime` + `InferenceService`
- Better for general model serving and predictive AI

**New LLM path**

- `LLMInferenceServiceConfig` + `LLMInferenceService`
- Better for advanced generative AI serving

##### Encode this

- **`InferenceService` works for basic LLM serving**
- **`LLMInferenceService` exists for complex LLM production patterns**
- **The new API is about routing, scheduling, and distributed inference**

##### Recall prompt

*What production problems does `LLMInferenceService` solve that `InferenceService` does not solve well enough?*

[Back to Contents](#contents)

#### Why Runtime and Model Separation Matters

One of the most important operational ideas in these notes is the separation between:

- **Runtime lifecycle**
- **Model lifecycle**

##### Why this matters

These two things change on **different schedules** and are owned by **different teams**.

##### Runtime lifecycle examples

- Upgrading vLLM or TGI versions
- Changing container images
- Adjusting default server startup parameters
- Updating infrastructure assumptions

##### Model lifecycle examples

- Releasing a new model version
- Changing quantization
- Updating weights
- Rolling back to a previous validated model

##### Operational benefit

This separation allows:

- **Platform teams** to manage runtimes safely
- **Model teams** to iterate independently
- Fewer ownership conflicts
- Cleaner production workflows

##### Broader serving context

Model servers such as **vLLM**, **TGI**, and **SGLang** matter because they provide performance-critical optimizations like:

- **PagedAttention**
- **FlashAttention**
- **Continuous batching**

These are essential for real throughput and latency, especially on GPUs.

##### KServe versus Ray

The trade-off is philosophical as much as technical:

- **KServe** is **Kubernetes-native**
- **Ray** is more **Python-first**

KServe feels more familiar to platform operators because it maps closely to Kubernetes concepts.

Ray offers stronger built-in distributed serving ergonomics, but introduces its own orchestration layer, which can complicate operations and debugging.

##### Encode this

- **Separation of runtime and model reflects real ownership boundaries**
- **Specialized model servers are required for production efficiency**
- **KServe vs Ray = Kubernetes-native vs Python-first orchestration**

##### Recall prompt

*Why is separating runtime management from model management an operational advantage rather than just a design preference?*

[Back to Contents](#contents)

### Ray Serve and KubeRay

The **[Ray project](https://www.ray.io/)**, compared to KServe, is a **newer project** with a **broader scope**. It is an **open source framework** designed to **build and scale ML applications easily**.

Ray is very **Pythonic**, making it user-friendly for those with Python experience, and it allows you to configure all activities **directly within your Python codebase**.

#### Core concepts

Ray is **not specific** for model serving but instead defines a set of **generic core concepts**:

- **Task**
- **Actor**
- **Object**
- **Placement Group**
- **Environment Dependency**

These core concepts, in addition to the **Ray Cluster**, define the execution model used to build and scale all the other features.

![Ray Cluster topology](<assets/Ray Cluster topology.png>)

**Figure 1-5. Ray Cluster topology**

A Ray Cluster wasn't designed with Kubernetes in mind. It has a **standalone infrastructure** to manage the scheduling and orchestration of jobs that you can usually do with the Kubernetes API:

- **head node** — acts as the entry point for the jobs
- **worker nodes** — where execution happens; jobs are dispatched here from the head

For a more comprehensive foundation on Ray, see the book **"Learning Ray"** by Max Pumperla et al. (O'Reilly, 2023).

#### Ray Serve

The set of features that Ray offers covers most of the ML use cases:

- **Ray Train**
- **Ray Tune**
- **Ray Serve**

…are just a subset of them.

**Ray Serve** is the component used to **serve a model**. The deployment is **defined in Python**, and is the same for each endpoint to expose or model initialization.

##### Example 1-13. Ray Serve with a Transformer-based model

```python
from starlette.requests import Request
from typing import Dict

from transformers import pipeline

from ray import serve

@serve.deployment
class TransformerModelDeployment:
    def __init__(self):
        self._model = pipeline(
            "my-transformer-model")

    def __call__(self, request: Request) -> Dict:
        return self._model(
            request.query_params["text"])[0]


serve.run(
    TransformerModelDeployment.bind(),
    route_prefix="/my-model/")
```

What to notice:

- **`@serve.deployment`** — decorator function where it is possible to configure most of the deployment aspects, like **autoscaling**
- **`__init__`** — should be used to load a model; in this case it is a **Transformer-based pipeline**
- **`serve.run`** — deploys the model with a given prefix

Given that it is configured directly in code, Ray Serve is **very flexible**. You can easily find examples integrated with **FastAPI** to expose the endpoint, or using a library like **vLLM** to deploy a full model server.

#### KubeRay

Ray has an API that is very friendly to a **data scientist or Python developer** in general, but deploying a Ray Cluster on Kubernetes still requires help to **wire all the components together** with Kubernetes concepts like **Deployment** and **Ingress**.

The **[KubeRay project](https://github.com/ray-project/kuberay)** has been created to **streamline the transition from local Ray execution to Kubernetes**. This is necessary because Ray Clusters and Ray applications are not natively designed to use Kubernetes — in particular, a Ray Cluster has a **head node** and **worker nodes** that need to be deployed with multiple Deployments properly configured to interact with each other.

KubeRay provides multiple Ray APIs as Kubernetes **CustomResourceDefinitions**. In particular, the **`RayService`** object is a single concept that represents:

- a **multinode Ray Cluster**, and
- a **Ray Serve application** that uses that cluster

##### Example 1-14. `RayService` CR snippet

```yaml
apiVersion: ray.io/v1alpha1
kind: RayService
metadata:
  name: my-transformer-model
spec:
  serveConfigV2: |
    applications:
      - name: my-transformer-model
        import_path: my-transformer-model:deployment
        runtime_env:
          working_dir: "https://my-git-repo.com/main.zip"
  rayClusterConfig:
    rayVersion: %VERSION%
    headGroupSpec:
      ...
      template:
        spec:
          containers:
          - name: ray-head
            image: rayproject/ray-ml:%VERSION%
            ports:
            ...
            - containerPort: 8000
              name: serve
    workerGroupSpecs:
    - replicas: 1
      groupName: gpu-group
      template:
        spec:
          containers:
          - name: ray-worker
            image: rayproject/ray-ml:%VERSION%
          tolerations:
            - key: "ray.io/node-type"
              operator: "Equal"
              value: "worker"
              effect: "NoSchedule"
```

What to notice:

- **`serveConfigV2`** — contains all the configuration of the **Ray Serve application**
- **`working_dir`** — the code of the application is **downloaded** from this location
- **`rayClusterConfig`** — configures the **head and worker nodes** of the Ray Cluster
- **`rayVersion: %VERSION%`** — the version of Ray should be specified here and in the images to use
- **`containerPort: 8000`** — the head node exposes multiple components in addition to the serving aspect, like the **dashboard** or **client**
- **`tolerations`** — as in previous examples, it is possible to configure **tolerations and taints** to match node requirements (such as GPUs or dedicated Ray nodes)

#### KServe vs Ray: trade-off

From a Kubernetes platform perspective:

- **Ray is less familiar** in terms of API and management when compared to KServe
- but it enables **data scientists and Python developers to have full control** over deployment
- this flexibility brings a lot of value, especially when you need to configure **more complex serving topologies**, like distributed serving or training on multiple hosts

#### Encode this

- **Ray = Python-first ML framework with a standalone Cluster model (head + workers)**
- **Ray Serve = the inference component, configured directly in Python via `@serve.deployment`**
- **KubeRay = Kubernetes Operator that bridges Ray Clusters to Kubernetes via `RayService` CRD**
- **`RayService` packages a Ray Cluster + Ray Serve application into one declarative resource**
- **Ray brings flexibility for complex topologies at the cost of additional orchestration on top of Kubernetes**

#### Recall prompt

*Why does Ray Serve introduce its own orchestration layer rather than relying solely on Kubernetes primitives like KServe does?*

[Back to Contents](#contents)

### Model Serving Lessons Learned

This section explored the components necessary to deploy LLMs on Kubernetes, from basic model serving to production-ready orchestration.

**Specialized model servers are essential**

Model servers like **vLLM**, **TGI**, and **SGLang** provide essential optimizations (**PagedAttention**, **FlashAttention**, **continuous batching**) that directly impact **throughput and latency**.

While you can containerize inference code with **FastAPI**, production workloads demand specialized runtimes that:

- maximize **GPU utilization**
- efficiently manage **memory-bound decode phases**

**Separation of runtime and model lifecycle reflects operational reality**

KServe provides:

- **`InferenceService`** with **`ServingRuntime`** for general model serving
- **`LLMInferenceService`** with **`LLMInferenceServiceConfig`** for complex LLM deployments requiring **distributed inference** and **advanced routing**

This separation acknowledges that **runtime upgrades**, **model deployments**, and **infrastructure changes** operate on **different schedules** with **different ownership**:

- **platform teams** can manage runtime versions and container images
- **data science teams** deploy and iterate on models independently
- preventing conflicts and enabling **parallel workflows**

**Deployment controller choice involves fundamental trade-offs**

- **KServe** integrates natively with Kubernetes primitives (Deployments, Services, Ingress), making it familiar to **platform operators** but requiring **additional components** for features like autoscaling
- **Ray** provides a **Python-first development experience** with built-in distributed serving capabilities, but introduces its **own orchestration layer** that partially overlaps with Kubernetes, creating **operational complexity** when debugging or managing resources

**Manual deployments remain valuable as a learning path**

Starting with manual deployments before adopting controllers remains **valid for early-stage projects**:

- understanding the underlying **Deployment**, **`PersistentVolumeClaim`**, and **GPU resource configurations** clarifies **what controllers automate**
- helps diagnose issues when **abstractions leak**

With the inference infrastructure in place, one critical piece remains: **the model itself**. The next section tackles the challenge of **managing model data** and the strategies for getting it into your cluster efficiently.

#### Encode this

- **Production LLM serving is a 2-layer problem: model server + controller**
- **Pick a model server based on runtime needs (vLLM for OSS LLMs, TGI for HF stack, NIM for NVIDIA hardware, SGLang for prefix-cache workloads, llama.cpp for edge)**
- **Pick a controller based on team profile (KServe for Kubernetes-native platforms, Ray Serve for Python-first ML teams)**
- **Separation of `ServingRuntime` and `InferenceService` mirrors team ownership boundaries**
- **`LLMInferenceService` exists because basic InferenceService cannot model routing, KV cache, or distributed inference**

#### Recall prompt

*What is the operational rationale for separating `ServingRuntime` from `InferenceService` instead of bundling them into one resource?*

[Back to Contents](#contents)

## Kubernetes and GPUs

At its core, generative AI involves **intensive mathematical computations**, particularly **linear algebra operations** such as **tensor multiplications**. These operations demand significant computational power and memory capacity to process large datasets and models ranging from **tens to hundreds of billions of parameters**. Specialized hardware called **Graphics Processing Units (GPUs)** has emerged to optimize and accelerate these workloads.

Initially designed for **rendering graphics** and creating immersive gaming experiences, GPUs quickly moved into the AI domain because of their **massively parallel architecture**. That capability fits naturally with the linear-algebra-heavy tasks of AI and machine learning.

### The GPU and accelerator landscape

- **NVIDIA** leads the market by a large margin
- **AMD** and **Intel** are the primary competitors
- **Google Tensor Processing Units (TPUs)** offer compelling performance but are typically restricted to the Google ecosystem
- **AI-specific Application-Specific Integrated Circuits (ASICs)** such as those from **Cerebras** and **Graphcore** are emerging but still niche
- **Field Programmable Gate Arrays (FPGAs)** represent another niche option

The primary reason GPUs remain the standard choice is their **mature ecosystem**, **broad availability**, and **proven scalability**. When deploying LLMs in production, GPUs have become indispensable due to substantial memory and computational demands.

### Why Kubernetes needs a special mechanism for GPUs

By default, Kubernetes includes built-in support for standard computing resources like **CPU** and **memory**. Leveraging specialized hardware like GPUs requires additional mechanisms.

Kubernetes addresses this through **device plug-ins**, a pluggable extension framework that allows Kubernetes to:

- integrate external hardware resources
- manage their lifecycle
- effectively expand the Kubernetes API to include these specialized devices

GPUs require special attention because they need:

- **specific discovery mechanisms** within Kubernetes
- **dedicated scheduling criteria**
- **dedicated software stacks** such as NVIDIA's **CUDA libraries**

This section focuses on NVIDIA GPUs due to their market dominance, and covers:

- discovery via **Node Feature Discovery** and **GPU Feature Discovery**
- the **Kubernetes device plug-in framework**
- the emerging **Dynamic Resource Allocation (DRA)** feature
- **resource-based** and **label-based** scheduling strategies
- advanced management with the **NVIDIA GPU Operator**
- GPU partitioning via **time slicing** and **Multi-Instance GPU (MIG)**
- diagnostics with **nvidia-smi**

[Back to Contents](#contents)

### GPU Discovery

Before Kubernetes can effectively manage GPUs, it must reliably **identify which nodes have GPUs** and **determine their capabilities**. Accurate hardware detection ensures workloads match nodes offering suitable GPU resources.

Two complementary tools handle this:

- **Node Feature Discovery (NFD)** — general-purpose hardware discovery for Kubernetes
- **GPU Feature Discovery (GFD)** — NVIDIA-specific tool that builds on NFD with detailed GPU labels

#### Node Feature Discovery

Kubernetes clusters are rarely identical. Hardware capabilities vary, especially when GPUs are involved. **Effective scheduling in heterogeneous environments** — cloud, hybrid, or bare-metal — depends on accurately identifying these capabilities.

**Node Feature Discovery (NFD)** is the project that provides this capability:

- detects hardware features on each node
- automatically labels the corresponding node resources
- provides essential information for the Kubernetes scheduler

How NFD works:

- deploys a **DaemonSet** so an agent runs on every node
- the agent examines hardware and software configuration of each node
- identifies attributes such as **CPU details**, **network interfaces**, and **available PCI devices** like GPUs
- applies **descriptive labels** to the Node objects in the Kubernetes API

##### Example 3-1. Installing NFD with Kustomize

```bash
NFD_REPO=https://github.com/kubernetes-sigs/node-feature-discovery
kubectl apply -k $NFD_REPO/deployment/overlays/default
```

Alternatively, the **NFD operator** offers a more integrated lifecycle management experience, especially valuable in production environments.

##### Example 3-2. Inspecting node labels added by NFD

```bash
kubectl get node <node-name> -o yaml | yq .metadata.labels

feature.node.kubernetes.io/pci-0300_1d0f.present: "true"
feature.node.kubernetes.io/pci-0302_10de.present: "true"
feature.node.kubernetes.io/cpu-hardware_multithreading: "true"
feature.node.kubernetes.io/cpu-model.family: "6"
feature.node.kubernetes.io/cpu-model.id: "85"
feature.node.kubernetes.io/cpu-model.vendor_id: Intel
feature.node.kubernetes.io/kernel-selinux.enabled: "true"
feature.node.kubernetes.io/kernel-version.full: 5.14.0-427.62.1.el9_4.x86_64
...
```

What to notice:

- `pci-0300_1d0f.present` — a PCI ID that indicates an **AWS VGA-compatible display controller** (vendor ID `1d0f`, device class `0300`), typical in AWS EC2 nodes
- `pci-0302_10de.present` — indicates the presence of an **NVIDIA GPU** (vendor ID `10de`, device class `0302`)

NFD labels follow the format:

```text
feature.node.kubernetes.io/<class>_<vendor>
```

PCI vendor IDs you will commonly see:

- **`10de`** = NVIDIA
- **`1002`** = AMD
- **`8086`** = Intel

PCI class code **`0302`** denotes **3D controllers** such as GPUs.

<u>NFD limitation:</u> NFD labels indicate the **existence** of certain hardware, not detailed GPU specifications like model, memory size, or CUDA capabilities. That gap is filled by GFD.

#### GPU Feature Discovery

**GPU Feature Discovery (GFD)** is a lightweight utility from NVIDIA, specifically designed to **detect detailed GPU characteristics** and expose them as **node labels** for advanced scheduling.

GFD is part of the **NVIDIA GPU Operator** and runs as a **DaemonSet** on GPU-equipped nodes. It uses utilities such as `nvidia-smi` to gather detailed information like:

- GPU model
- memory capacity
- CUDA version
- Multi-Instance GPU capabilities

##### Table 3-1. Labels added by GFD

| Label | Description | Example |
| --- | --- | --- |
| `nvidia.com/gpu.count` | Number of GPUs or MIG instances present on the node | `4` |
| `nvidia.com/gpu.product` | Model name or MIG profile of the NVIDIA GPU. In MIG mode this may include the MIG profile; in time-slicing mode it may have a `-SHARED` suffix | `A100-SXM4-40GB` |
| `nvidia.com/gpu.memory` | Total memory per GPU or MIG instance (in MiB) | `40537` |
| `nvidia.com/gpu.family` | GPU architecture family (Ampere, Hopper, Turing, etc.) | `ampere` |
| `nvidia.com/cuda.driver-version.full` | Full version of the installed NVIDIA GPU driver | `525.105.17` |
| `nvidia.com/cuda.runtime.version.full` | Full version of the available CUDA runtime | `12.2` |
| `nvidia.com/mig.capable` | Indicates whether the GPU supports MIG partitioning | `true` |
| `nvidia.com/mig.strategy` | MIG partitioning strategy (`single`, `mixed`, or unset) | `single` |
| `nvidia.com/gpu.replicas` | Number of virtual GPUs per physical GPU when time slicing is enabled | `8` |
| `nvidia.com/mig-<profile>.count` | Number of MIG partitions of a specific MIG profile available (present if mixed strategy is used) | `2` (e.g., `nvidia.com/mig-1g.5gb.count`) |
| `nvidia.com/gpu.machine` | Machine type or identifier of the GPU-equipped node | `dgx-a100` |
| `nvidia.com/gpu.compute.major` | Major CUDA compute capability version of the GPU | `8` |
| `nvidia.com/gpu.compute.minor` | Minor CUDA compute capability version of the GPU | `0` |

These detailed labels enable scheduling decisions that basic NFD labels cannot:

- **target shared GPUs**: `nvidia.com/gpu.product: A100-SXM4-40GB-SHARED`
- **ensure exclusive GPU access**: avoid nodes with the `-SHARED` suffix

In practice, these labels are often used **internally by NVIDIA GPU Operator components**, such as the NVIDIA device plug-in. Users typically just request GPU resources via resource requests in their pod specifications (see [Resource-Based Scheduling](#resource-based-scheduling)).

#### Encode this

- **NFD = generic hardware labeling for any Kubernetes cluster**
- **GFD = NVIDIA-specific labels with model, memory, CUDA, MIG details**
- **PCI class `0302` + vendor `10de` indicates an NVIDIA GPU**
- **GFD labels enable both manual selection and internal Operator logic**

#### Recall prompt

*Why is GFD needed if NFD already labels nodes with PCI hardware information?*

[Back to Contents](#contents)

### Kubernetes GPU Device Plug-Ins

Once GPU capabilities are labeled, the next step is to **expose GPUs as schedulable and allocatable resources** within Kubernetes. The **device plug-in framework** allows external hardware to integrate seamlessly into the Kubernetes resource model.

Kubernetes was designed to be extensible:

- **CPU** and **memory** are natively supported
- **device plug-ins** integrate specialized hardware (GPUs, TPUs, other accelerators)

Plug-ins register with the **Kubelet** on each node and advertise:

- **device availability**
- **health status**

This enables **resource-aware scheduling** and **workload isolation**.

The device plug-in interface supports a wide variety of specialized hardware including:

- **FPGAs**
- **networking accelerators**
- **storage controllers**
- **cryptographic modules**
- **multimedia processors**
- **robotics hardware**
- **GPUs and AI accelerators**

#### Four core device plug-in functions

**1. Device discovery**

Plug-ins detect hardware devices on nodes and report their inventory to the Kubelet.

**2. Resource allocation**

When a workload requires specific hardware (e.g., GPUs), the device plug-in handles **exclusive allocation**. It:

- sets up the runtime environment
- exposes necessary device files
- injects environment variables

**3. Health monitoring**

Plug-ins continuously monitor device health, ensuring Kubernetes is aware of unhealthy hardware to inform scheduling decisions.

**4. Scheduler integration**

Device plug-ins expose hardware as **standard Kubernetes extended resources** (e.g., `nvidia.com/gpu`). Pods request these resources explicitly in their resource declarations.

#### Well-known device plug-ins

- **`nvidia-device-plugin`** — official NVIDIA plug-in exposing **CUDA-enabled GPUs**, essential for GPU-accelerated AI workloads
- **`amd-device-plugin`** — official AMD plug-in integrating **ROCm-based GPUs** for HPC and AI workloads
- **`intel-gpu-plugin`** — Intel's plug-in for integrated and discrete GPUs
- **`google-cloud-tpu-device-plugin`** — Google's plug-in for **TPUs**, exclusively available in **GKE**

#### Limitations

The device plug-in model has structural limits:

- devices are usually allocated **exclusively** to individual pods → can lead to **underutilized resources**
- resource allocation is **static** and **determined at scheduling time** → less flexible for workloads with dynamic resource requirements

These limitations motivated **Dynamic Resource Allocation (DRA)**, covered below.

#### Encode this

- **Device plug-ins extend Kubernetes to schedule non-CPU/non-memory hardware**
- **Four functions: discovery, allocation, health monitoring, scheduler integration**
- **`nvidia.com/gpu` is an extended resource exposed by the NVIDIA device plug-in**
- **Allocation is exclusive and static; DRA aims to relax both constraints**

#### Recall prompt

*What are the two main limitations of the classic device plug-in model that DRA aims to solve?*

[Back to Contents](#contents)

### GPU Workload Scheduling

Kubernetes offers three complementary approaches to placing GPU-bound workloads:

1. **Label-based scheduling** — steer pods with node labels and affinity rules
2. **Resource-based scheduling** — rely solely on numeric resource requests
3. **Dynamic Resource Allocation (DRA)** — declarative, intent-driven device requests

Each is covered separately so the strengths of each method remain clear.

#### Label-Based Scheduling

When a cluster contains several kinds of GPUs, or when operators want to **fence off GPU nodes from general workloads**, labels become the steering wheel. Kubernetes offers three closely related mechanisms:

- **`nodeSelector`**
- **node affinity**
- **taints and tolerations**

##### `nodeSelector`

The most direct approach. You attach a fixed label to every node that matches a certain characteristic, then repeat that exact key-value pair in the pod spec's `nodeSelector` field.

Instead of creating custom labels manually, you can leverage the GPU-specific labels NFD and GFD automatically attach.

##### Example 3-3. Direct selection of a node with a node selector

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: t4-inference
spec:
  containers:
  - name: server
    image: myrepo/llm-server:latest
  nodeSelector:
    # Select only nodes that are labelled for a Tesla T4 GPU
    nvidia.com/gpu.product: Tesla-T4
```

Strengths and limits:

- **simplicity**: a single line pins the workload to the desired node pool
- **no extra scheduler overhead**
- the rule is **absolute**: if the label is missing or misspelled, the pod won't schedule
- it **cannot express alternatives**; it is "T4 or nothing"

##### Node affinity

**Node affinity** builds on the same idea but allows richer expressions and **soft preferences**:

- **required terms** act like an extended selector
- **preferred terms** let you nudge the scheduler toward the best node when several satisfy the hard constraints

##### Example 3-4. Node affinity for finer-grained selections

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: a100-preferred
spec:
  containers:
  - name: llm
    image: myrepo/mt-server:latest
    resources:
      limits:
        nvidia.com/gpu: 4
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: nvidia.com/gpu.memory
            operator: Gt
            values: ["40000"]
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: nvidia.com/gpu.family
            operator: In
            values: ["hopper"]
```

What to notice:

- the **required** condition is that the GPU has at least **40 GB memory**
- the **preferred** condition is **NVIDIA H100** (Hopper), but the workload still schedules on an Ampere (A100) if no Hopper is free
- the downside is **verbosity**: long match expressions can clutter manifests, and too many hard clauses can starve the workload

##### Taints and tolerations

Sometimes operators want to flip the model and **mark certain nodes off-limits unless a pod explicitly opts in**:

- a **taint** added by the administrator **repels all pods**
- only pods carrying a matching **toleration** can schedule

##### Example 3-5. Taint a node so it is not considered for scheduling by default

```bash
# cluster-admin permission required
kubectl taint nodes -l nvidia.com/gpu.count nvidia.com/gpu=true:NoSchedule
```

This adds a taint `nvidia.com/gpu=true:NoSchedule` to all nodes carrying the label `nvidia.com/gpu.count`. Only pods that explicitly tolerate `nvidia.com/gpu` can be scheduled there.

##### Example 3-6. Deployment with a toleration for `nvidia.com/gpu` taints

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-serving
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: tgi
        image: ghcr.io/huggingface/tgi:latest
        resources:
          limits:
            nvidia.com/gpu: 1
      tolerations:
      - key: "nvidia.com/gpu"
        operator: "Exists"
        effect: "NoSchedule"
```

What to notice:

- the **`limits`** field requires an `nvidia.com/gpu` resource exposed by the NVIDIA device plug-in
- the **toleration** ignores `nvidia.com/gpu` taints regardless of value, so this deployment can also be scheduled on tainted GPU nodes

Taints are ideal for:

- **dedicating costly GPU nodes** to GPU workloads
- **cordoning nodes under maintenance**
- working **in tandem** with affinity or selectors: the taint keeps general pods out, while affinity decides which GPU node fits best among those that remain

##### When to use which

- **`nodeSelector`** — shines in small, homogeneous GPU fleets where a single label is enough
- **Node affinity** — the tool of choice once you mix generations, memory sizes, or availability zones
- **Taints** — protect the GPU pool at cluster scope; pair naturally with the other two for fine placement

All three approaches share one limitation: they rely on **static labels** that administrators maintain manually or that are added by discovery operators (NFD, GFD).

#### Resource-Based Scheduling

The simplest way to schedule a GPU workload in Kubernetes is to **declare the need for a GPU directly in the workload specification**.

As soon as the NVIDIA device plug-in is running, it advertises every GPU as an extended resource — typically `nvidia.com/gpu`.

##### Example 3-7. Require one NVIDIA GPU

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

The scheduler examines only the **numeric availability** from the device plug-in, then binds the pod to a qualifying node. The kubelet grants the container exclusive access to one of that node's GPUs.

Strengths:

- **no extra labels** to manage
- **no node selectors** to remember
- **no additional controllers** to install
- completely integrated with the familiar `requests`/`limits` resource model
- a single field is enough to isolate the GPU at the device-file level
- prevents other pods from touching it
- lets CUDA applications run without further configuration

Limitations — **lack of precision**:

- all GPUs look **identical** to the scheduler, even if the cluster mixes V100s, A100s, and consumer cards
- a model that fits on an **80 GB A100** might not fit on a **16 GB T4**, yet `nvidia.com/gpu: 1` treats them the same
- no built-in way to request:
  - a specific **compute capability**
  - GPUs in **MIG mode**
  - multiple GPUs with a particular **interconnect topology**

In practice teams work around this by **combining resource requests with `nodeSelector` or `nodeAffinity` rules** that steer workloads to compatible hardware. Powerful, but it requires extra coordination between node inventory and workload definitions.

#### Dynamic Resource Allocation

![NVIDIA GPU DRA](<assets/NVIDIA-GPU-DRA.png>)

**Figure 3-1. NVIDIA GPU with Dynamic Resource Allocation**

**Dynamic Resource Allocation (DRA)** is an effort to make device scheduling in Kubernetes **more flexible, composable, and dynamic**. DRA has been available as a **core, stable** Kubernetes feature since **version 1.34**.

Instead of tying device allocation directly to resource fields in the pod spec, DRA introduces new resource types that shift the focus from **"how many" devices** to **"what kind"** of device a workload requires.

The model is inspired by Kubernetes' **volume provisioning**: users describe a desired resource and let the platform resolve it.

##### How DRA changes the model

- workloads declare device needs via **`ResourceClaimTemplate`** resources
- templates act as **intent declarations**
- the Kubernetes control plane and the installed **DRA driver** resolve them at scheduling time
- allocation happens **just-in-time**, allowing smarter decisions and more efficient usage

A pod can request, for example, **"an A100 GPU with at least 40 GB of memory"** and the scheduler will only place the pod on a node that can fulfill the requirement.

##### Example 3-8. `ResourceClaimTemplate` defining GPU requirements for deployment pods

```yaml
apiVersion: resource.k8s.io/v1beta1
kind: ResourceClaimTemplate
metadata:
  name: a100-claim-template
spec:
  spec:
    devices:
      requests:
        - name: high-memory-gpu
          deviceClassName: gpu.nvidia.com/a100
          allocationMode: ExactCount
          count: 1
          parameters:
            minMemory: "40Gi"
            migMode: "disabled"
```

What to notice:

- `deviceClassName: gpu.nvidia.com/a100` — requests an **NVIDIA A100 GPU**
- `count: 1` — one GPU required
- `minMemory: "40Gi"` — the GPU must have at least 40 Gi of memory
- `migMode: "disabled"` — Multi-Instance GPU mode must be disabled (full GPU access)

##### Example 3-9. Deployment using `ResourceClaimTemplate` for GPU allocation

```yaml
apiVersion: batch/v1
kind: Deployment
metadata:
  name: inference-server
spec:
  template:
    spec:
      containers:
      - name: model-runner
        image: myorg/llm-inference:latest
        resources:
          claims:
          - name: high-memory-gpu
      resourceClaims:
      - name: high-memory-gpu
        resourceClaimTemplateName: a100-claim-template
```

What to notice:

- `resources.claims` references a **resource claim name** to use when the deployment creates pods
- `resourceClaims` ties that name to the `ResourceClaimTemplate` defined in Example 3-8

##### Why DRA matters

- **separation between declaration and actual allocation** — opens the door for dynamic, demand-driven GPU provisioning
- drivers can perform **more intelligent allocation strategies** (current usage, power consumption, memory pressure, node-level constraints)
- replaces "pick the first available GPU" with **policy-driven** placement

##### Current limitations

- core DRA APIs are **generally available** since Kubernetes 1.34, but the ecosystem is still catching up
- the **NVIDIA GPU DRA driver** exists but is marked as a **technical preview**, not yet supported for production
- features like **partial GPU requests**, **fine-grained MIG partitioning**, or **topology-aware scheduling** are still maturing and remain driver- and platform-dependent
- integration with **cluster autoscalers** or **quota enforcement** is limited

Until DRA becomes production-grade, **resource requests combined with label-based scheduling remain the standard approach** for GPU scheduling.

#### Encode this

- **Label-based scheduling: `nodeSelector` (absolute), affinity (rich), taints (cluster-scope fences)**
- **Resource-based scheduling: simplest, but treats every GPU identically**
- **DRA: declarative, "what kind" instead of "how many", inspired by volume provisioning**
- **DRA is GA in Kubernetes 1.34, but the NVIDIA driver is still technical preview**

#### Recall prompt

*Why does plain `nvidia.com/gpu: 1` resource scheduling break down when a cluster mixes A100 and T4 GPUs?*

[Back to Contents](#contents)

### NVIDIA GPU Operator

The **NVIDIA GPU Operator** builds on the Kubernetes device plug-in and GFD, and adds everything needed to run NVIDIA GPU workloads reliably in production. It installs:

- **drivers**
- **container runtime hooks**
- **monitoring agents**

It also offers two sharing mechanisms for sub-GPU resource allocation in **one declarative interface**, automating installation and configuration of all necessary components.

#### Components

**NVIDIA drivers (kernel module and CUDA)**

At the heart of GPU enablement are the NVIDIA drivers — kernel modules and user-space libraries that enable **CUDA** and GPU acceleration. The Operator can deploy the official NVIDIA driver into each GPU node by running a **privileged driver container**, which:

- compiles the driver for the node's kernel
- or retrieves a precompiled version when available

By containerizing the driver, the Operator ensures all GPU nodes have the required driver version without manual intervention.

> **NOTE**
>
> GPU nodes ideally should run the **same OS kernel version** if you want to rely on the Operator's driver container across all nodes. Mixed OS versions might require **pre-installing drivers manually**. The `ClusterPolicy` CR allows customizing the driver version or using precompiled binaries if needed.

**GPU Feature Discovery**

The Operator deploys **GFD** as a DaemonSet so you don't have to install it manually.

**Kubernetes device plug-in for GPUs**

The Operator deploys the **NVIDIA device plug-in** as a DaemonSet on GPU nodes. It introduces the extended resource `nvidia.com/gpu` used for resource-level scheduling and also enables **sub-GPU allocation**.

<u>Critical caveat:</u> if the NVIDIA device plug-in is not running or not working, pods will be **stuck pending** because Kubernetes thinks no resources are available.

**NVIDIA Container Toolkit (runtime)**

For containers to actually use the GPU, they need the **NVIDIA Container Runtime** (part of the NVIDIA Container Toolkit). The Operator deploys this toolkit on the nodes. The runtime is an extension to **CRI-O** and **containerd** that knows how to inject GPU drivers and device files into containers when a GPU is requested.

The result: any container that requests a GPU will have `/dev/nvidia0` and GPU drivers available. However, **the container image must still include the CUDA libraries** the application requires.

**Multi-Instance GPU (MIG) Manager**

On systems with **MIG-capable GPUs** (e.g., NVIDIA **A100** or **H100**), the Operator includes a **MIG Manager** component:

- monitors the node's MIG configuration
- reconfigures the GPU's MIG partitions according to a desired state
- applies the MIG strategy configured in the `ClusterPolicy`

Without the MIG Manager, an administrator would have to log in remotely to the node and use `nvidia-smi` to set up MIG partitions manually.

**GPU monitoring with DCGM Exporter**

The Operator also typically deploys the **Data Center GPU Manager (DCGM) Exporter** as a DaemonSet. DCGM polls every GPU for:

- utilization
- memory pressure
- ECC errors
- temperature
- power draw
- and a wealth of other counters

It translates them into **Prometheus metrics**. Most users scrape the exporter with the cluster's Prometheus stack and surface graphs in **Grafana**. See [Model Observability](#model-observability) for the broader observability stack.

#### Operator Configuration with ClusterPolicy

The NVIDIA GPU Operator is available for **multiple Kubernetes distributions**, including **OpenShift**, where it ships out-of-the-box as part of the OperatorHub catalog. It can also be installed on standard Kubernetes clusters using **Helm charts** or custom manifests provided by NVIDIA.

##### Example 3-10. Installing the GPU Operator with Helm

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace
```

The Operator is configured through the **`ClusterPolicy`** custom resource, which controls:

- device plug-in configuration
- enabling time slicing
- configuring MIG strategies

A `ClusterPolicy` can reference a custom **`ConfigMap`** to fine-tune device plug-in behavior — for example, to enable time slicing or other GPU sharing mechanisms. The policy can specify a default key from the ConfigMap that applies when a GPU-enabled node is not labeled with `nvidia.com/device-plugin.config=<key>`.

##### Example 3-11. Example configuration for the NVIDIA GPU Operator

```yaml
apiVersion: nvidia.com/v1
kind: ClusterPolicy
metadata:
  name: gpu-cluster-policy
spec:
  gfd:
    enabled: true
  devicePlugin:
    config:
      name: gpu-sharing-config
      default: sharing
  mig:
    strategy: mixed
```

What to notice:

- **`gfd.enabled: true`** — enables GPU Feature Discovery
- **`devicePlugin.config.name`** — points to the `ConfigMap` `gpu-sharing-config` that holds extra configuration (such as time slicing settings)
- **`devicePlugin.config.default`** — references a key in the ConfigMap; if set to empty string, no default applies and nodes must be labeled with `nvidia.com/device-plugin.config=<config map key>` to pick up the device plug-in config
- **`mig.strategy: mixed`** — sets the MIG strategy to mixed (see [MIG](#mig-multi-instance-gpu))

#### Encode this

- **The NVIDIA GPU Operator bundles drivers, device plug-in, runtime hooks, GFD, MIG Manager, and DCGM exporter**
- **`ClusterPolicy` is the single declarative entry point for GPU Operator configuration**
- **Mixed-kernel clusters may require manual driver pre-installation**
- **A broken NVIDIA device plug-in causes pods to stay pending forever**

#### Recall prompt

*Why is the NVIDIA GPU Operator considered an "out-of-the-box" solution for production GPU workloads compared with installing the device plug-in alone?*

[Back to Contents](#contents)

### GPU Sharing and Sub-GPU Allocation

The **NVIDIA GPU Operator** supports advanced GPU features for **partitioning** or **slicing** a single GPU across multiple workloads.

This may not always be central for operating very large LLMs, because many LLMs need most or all of a GPU's memory. Still, it is important to understand because GPU sharing can improve utilization for **inference**, **small models**, **interactive notebooks**, and **bursty workloads**.

The core GPU sharing concepts to distinguish are:

1. **Time slicing**
2. **MPS**
3. **MIG**

The Operator supports two of these natively (time slicing and MIG) and they can also be **combined**:

- **Time slicing** — allows multiple containers to share a GPU by allocating time-based slices
- **MIG** — available on certain GPUs (such as A100 and H100) to partition a single GPU into **isolated instances**

#### Time Slicing

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

##### CPU comparison: cores, logical processors, and time slicing

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

###### 1. Time slicing: one cashier, many customers taking turns

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

###### 2. Multiple physical cores: many real cashiers

Now there are **four cashiers**.

```text
Cashier 1 serves Customer A
Cashier 2 serves Customer B
Cashier 3 serves Customer C
Cashier 4 serves Customer D
```

This is real parallel work. More work can happen at the same time.

That is like **four physical CPU cores**.

###### 3. Logical processors / hyper-threading: one cashier with two order windows

Now imagine **one cashier has two windows**.

```text
Window 1: Customer A
Window 2: Customer B
```

But behind both windows, it is still **one cashier**.

The cashier can stay busier because when Customer A is waiting for payment approval, the cashier can help Customer B. But the cashier did not become two full cashiers.

That is like **one physical core with two logical processors**.

###### Simple summary

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

##### What time slicing gives you

- Better GPU utilization when workloads are **small**, **bursty**, or **idle** part of the time
- Ability to run several lightweight inference workloads on one GPU
- Sharing support for older GPUs that do **not** support MIG, such as some **T4** or **V100** environments
- Higher overall throughput when individual workloads do not need full GPU capacity all the time

##### Important trade-off

Time-sliced workloads are **not getting full GPU power at the same time**.

If all pods become busy, each pod gets slower because they are sharing the same physical GPU.

<u>Key limitation:</u> time slicing provides **compute-time sharing**, not strong isolation.

Unlike MIG, time slicing does **not** provide:

- GPU memory isolation
- Fault isolation
- Dedicated memory quotas
- Guaranteed full-GPU performance

All pods sharing the same physical GPU can access the same GPU memory pool. If one pod allocates most of the GPU memory, other pods may fail to allocate memory. If one process causes a GPU reset, the other workloads sharing that GPU can also be affected.

##### Example configuration for time slicing

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

##### Scheduling warning

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

##### Best fit

Time slicing is useful when:

- You have many small inference tasks
- You serve multiple lightweight models
- You run interactive notebooks
- Workloads are bursty and often idle
- The models collectively fit in GPU memory
- The GPU does not support MIG

Time slicing is often less useful for large LLMs because LLMs typically need most or all of a GPU's available memory.

#### MPS

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

##### How MPS works

```text
1. An MPS control daemon runs on the node.

2. When a CUDA application starts, the CUDA driver tries to connect to the MPS control daemon.

3. The daemon starts or reuses an MPS server.

4. CUDA client processes connect to that MPS server.

5. The MPS server coordinates shared GPU execution so work from multiple clients can use the GPU concurrently instead of only being time-sliced.
```

NVIDIA explains that, without MPS, kernels from different CUDA contexts are scheduled by a **time-sliced scheduler** and cannot execute concurrently. With MPS, client CUDA contexts route work through the MPS server, which bypasses that limitation and allows kernels from different clients to execute simultaneously. On Volta and newer GPUs, the MPS server is less in the critical path because clients manage more resources directly while the server mediates remaining shared resources.

Source: [NVIDIA Multi-Process Service architecture](https://docs.nvidia.com/deploy/mps/architecture.html) and [NVIDIA MPS introduction](https://docs.nvidia.com/deploy/mps/introduction.html).

##### MPS clarification

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

##### Mental model

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

##### Important nuance

```text
MPS improves GPU utilization, but it is not the same as hard isolation.
On newer NVIDIA GPUs, MPS has better address-space behavior,
but MIG is still the stronger isolation model.
```

For Kubernetes and the NVIDIA GPU Operator, **time slicing** and **MPS** are both GPU sharing strategies. But MPS is more advanced than basic time slicing because it enables more concurrent CUDA execution instead of only rotating workloads in turns.

#### MIG (Multi-Instance GPU)

**MIG** stands for **Multi-Instance GPU**.

It is available on **NVIDIA Ampere and newer GPUs** (such as **A100**, **A30**, **H100**, and **Blackwell B100/B200**), and allows one physical GPU to be partitioned into several **hardware-isolated instances**.

Each instance (or **MIG slice**) has its own:

- **dedicated compute cores**
- **memory carve-out**
- **separate engine contexts**

It is essentially like having multiple smaller GPUs in one card.

> For example, an **A100 40-GB GPU** can be split into up to **seven MIG instances**. The smallest configuration is **`1g.5gb`** (one GPU slice with 5 GB memory each). Each MIG device acts like a mini GPU with **guaranteed memory** and **isolated Streaming Multiprocessor (SM) resources**.

Where time slicing is mainly **temporal sharing**, MIG is **hardware partitioning**.

Simple distinction:

- **Time slicing**: workloads take turns on the same physical GPU.
- **MPS**: CUDA processes run more concurrently through an MPS server/control daemon.
- **MIG**: the GPU is split into isolated hardware-backed instances.

##### MIG strategies in the device plug-in

The NVIDIA device plug-in can expose MIG partitions as schedulable resources in **two ways**:

###### Single MIG strategy

All MIG instances on a node are advertised under the **generic `nvidia.com/gpu`** resource (just like normal GPUs). This strategy assumes **each GPU is identically partitioned**.

Example:

```text
2 x A100 each split into 7 x 1g.5gb instances
=> node reports: nvidia.com/gpu: 14
```

- when a pod requests one GPU, it actually gets one **MIG slice (5 GB)**
- the node labels (`gpu.product`, `gpu.count`) are adjusted to reflect MIG (e.g., `gpu.product = ...-MIG-1g.5gb`, `gpu.count = 14`)
- simple for users, but requires **homogeneous MIG setup** on all GPUs

###### Mixed MIG strategy

MIG instances are exposed as **distinct resource types**, named by their MIG profile:

- `nvidia.com/mig-1g.5gb`
- `nvidia.com/mig-4g.20gb`
- ...

A node may advertise **several different resources** if it has a mix of MIG sizes.

```yaml
resources:
  limits:
    nvidia.com/mig-2g.10gb: 1   # request a roughly 10-GB MIG instance
```

- more **flexible**: GPUs in a node could be split differently or even remain whole
- a bit more **advanced to schedule**: users need to know which MIG type to ask for

In both cases, the GPU Operator's **MIG Manager** creates the MIG partitions on the GPU as specified by `mig.strategy` in the `ClusterPolicy` (either `single` or `mixed`). If MIG mode is off (`none` strategy), GPUs are not partitioned at all.

##### Why MIG provides strong isolation

Unlike time slicing, MIG provides **strong isolation**:

- each MIG instance has a **fixed fraction** of the GPU's memory; it cannot use more than its allocation
- prevents one workload from stealing the memory of the others
- **fault isolation** is also improved: if one MIG instance crashes or resets, the others continue unaffected

This makes MIG attractive for **multitenant** or **production** scenarios where you safely run different applications on the same physical GPU. Ideal if each model service needs only a few GBs of GPU memory.

##### MIG trade-offs

The trade-off is **granularity and overhead**:

- you are limited to the **MIG profiles defined by NVIDIA** (you can't create an arbitrary 6-GB slice, only the fixed sizes offered by the card)
- if one job could have used the whole GPU at times, **MIG partitions hard-limit it to its share** — no concept of borrowing unused capacity from others
- by contrast, **time slicing** could let one pod burst to use the whole GPU if the others are idle

MIG is better when workloads need stronger guarantees around:

- **Isolation**
- **Predictable memory allocation**
- **Fault containment**
- **More stable performance**

For LLM and generative AI workloads:

- MIG is particularly useful for **inference serving** scenarios or running **many smaller experiments**
- if you have a **large model** (e.g., needs >40 GB), MIG won't help — you need the **full GPU** or **multiple GPUs**
- if you're hosting **multiple smaller models** (e.g., seven different language models each requiring ~5 GB), MIG can be very helpful, effectively giving each model its own virtual GPU with guaranteed memory

##### Combining MIG with time slicing

Time slicing and MIG are **not mutually exclusive**. You can time slice MIG instances too.

Example:

```text
Split a GPU into 2 MIG instances
Oversubscribe each MIG instance 2x with time slicing
=> 4 schedulable units per GPU
```

This is **advanced** and needed only in corner cases — but the Operator supports it (appending `-SHARED` to MIG device product labels when both are enabled).

For most production setups, choose **either MIG or time-shared, not both simultaneously**, due to complexity in managing performance.

##### MIG vs Time Slicing summary

- **MIG** partitions a GPU into smaller dedicated slices, each with **fixed memory and compute capacity** → isolation and predictability
- **Time slicing** treats the whole GPU as a single pool that multiple jobs take turns using, **sharing time but not memory** → flexibility and potentially higher utilization if not all jobs are busy at once

For **LLM training** (often consumes entire GPUs or multiple GPUs), typically **neither MIG nor time slicing** is used — GPUs are allocated **exclusively**.

For **LLM inference** and related workloads (fine-tuning smaller models, running many experiments, serving many models), both MIG and time slicing can be very useful:

- **MIG** → strict multitenancy or production QA tests
- **Time slicing** → dev environments or oversubscribing on less critical batch jobs where slowdowns are acceptable

For scenarios requiring stronger isolation guarantees and fixed memory allocations per workload, MIG is the more appropriate NVIDIA sharing mechanism.

#### Model-Serving Example: One GPU, Three Small Models

Imagine one Kubernetes node has **one NVIDIA GPU**, and we want to serve **three small AI models**:

```text
Model A: sentiment analysis
Model B: text embeddings
Model C: small chatbot
```

##### 1. Time slicing

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

##### 2. MPS

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

##### 3. MIG

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

##### Encode this

- **Sub-GPU allocation improves utilization by sharing one GPU across workloads**
- **Time slicing = oversubscription and time-based sharing**
- **MPS = concurrent CUDA execution through an MPS server/control daemon**
- **MIG = hardware-backed GPU partitioning**
- **Time slicing improves utilization but does not isolate memory or faults**
- **MPS improves utilization but is still not hard isolation**
- **Large LLMs often still need exclusive GPUs because memory is the real constraint**

##### Recall prompt

*Why can time slicing improve GPU utilization but still be risky for production workloads that need memory or fault isolation?*

[Back to Contents](#contents)

### GPU Diagnostics with nvidia-smi

To verify that your GPU sharing configuration works as expected, **`nvidia-smi`** is the go-to diagnostic tool.

> **`nvidia-smi`** is NVIDIA's **System Management Interface** tool, providing real-time monitoring and management of NVIDIA GPU devices.

It offers insights into:

- **GPU utilization**
- **memory usage**
- **temperature**
- **power consumption**
- **active processes**

By executing `nvidia-smi`, users obtain a **snapshot** of the current state of all GPUs in the system.

For **continuous monitoring**, the `-l` flag refreshes output at specified intervals:

```bash
nvidia-smi -l 5   # updates every 5 seconds
```

This tool is invaluable for:

- diagnosing **performance issues**
- ensuring GPUs are operating within **optimal parameters**
- verifying that applications are **actually utilizing GPU resources** as intended
- detecting anomalies such as **thermal throttling** or **unexpected memory consumption**
- enabling **proactive troubleshooting** in GPU-accelerated environments

You can run it directly inside a Kubernetes pod with `kubectl`, too.

##### Example 3-13. Running `nvidia-smi` directly on a GPU-enabled Kubernetes node

```bash
patch=$(cat <<EOT
[{
  "op":"add",
  "path":"/spec/containers/0/resources",
  "value":{"limits":{"nvidia.com/gpu":1}}
}]
EOT
)

kubectl run --rm -it gpu-pod \
  --image=nvidia/cuda:12.8.1-base-ubi9 \
  --restart=Never \
  --overrides=$patch --override-type=json -- nvidia-smi
```

The idea is to:

- launch a short-lived pod with a base CUDA image
- patch the container to **request a GPU** (`nvidia.com/gpu: 1`)
- run `nvidia-smi` inside it to inspect the GPU as the runtime sees it

This is especially useful for confirming:

- that the **NVIDIA device plug-in** correctly grants device access
- that **MIG partitions** appear as expected when MIG is enabled
- that **time-sliced replicas** are exposed under the right resource name (e.g., `nvidia.com/gpu.shared`)

#### Encode this

- **`nvidia-smi` is the primary diagnostic command for NVIDIA GPUs**
- **`-l N` refreshes the snapshot every N seconds**
- **Run it inside a GPU-requesting pod to verify the pod actually sees the GPU**
- **Use it to confirm MIG and time-slicing configurations are visible to the workload**

#### Recall prompt

*Why is running `nvidia-smi` inside a pod a stronger verification than checking GPU labels on the node?*

[Back to Contents](#contents)

### Multi-GPU Inference

> Sub-GPU techniques like **time slicing** or **MIG** are useful for squeezing many **small or midsized models** onto the same card, but LLMs rarely fall into that category. In practice, the bottleneck is not how to split one GPU — it is that **even the biggest card is still too small**.
>
> This brings the inverse problem: instead of sharing one GPU across many workloads, we must **distribute a single workload across many GPUs**.

**Multi-GPU inference** addresses this challenge by coordinating multiple GPUs, sometimes across several nodes, to serve a single large model.

Running inference for LLMs often demands **more GPU memory and compute than a single GPU can provide**. When using multiple GPUs for LLM inference, there are **two fundamental approaches**, each serving different needs.

![Multi-GPU parallelism taxonomy](<assets/Multi-GPU parallelism taxonomy.png>)

**Figure 3-1. Multi-GPU parallelism taxonomy**

- **Data parallelism** — uses multiple GPUs to host **replicas of the same model**, serving different requests in parallel to increase overall **queries per second (QPS)**
- **Model parallelism** — required when a single model is **too large to fit into one GPU's memory**; the model is **split across GPUs** so that each GPU holds part of the model, and collectively they handle one inference request

Model parallelism can be further divided into:

- **Tensor parallelism** — splits individual model layers across GPUs on a single node
- **Pipeline parallelism** — distributes entire model layers across multiple nodes

#### Data Parallelism

**Data parallelism** increases overall throughput by running **multiple complete copies of the model**:

- each GPU holds the **full model**
- each GPU serves **different requests concurrently**
- when a model is too large for one GPU, each **group of GPUs working together via model parallelism** can also run an **independent replica**

This approach **does not accelerate** any single query's latency, but it allows **more queries to be processed in parallel**, boosting QPS.

> Example: four GPUs and a moderate-sized LLM that fits in one GPU → deploy **four separate model instances**, each running on one GPU, handling **4× the traffic**.

The Kubernetes-native approach:

- run **multiple replica pods**, each requesting one GPU
- serve the model behind a **load balancer service** for automatic load distribution

Alternatively, some inference frameworks use a **multithreaded server within a single pod** that dispatches requests to multiple GPUs, though this is less common for GPU workloads in Kubernetes.

![Data parallelism: throughput scaling](<assets/Data parallelism - throughput scaling.png>)

**Figure 3-2. Data parallelism: throughput scaling**

##### When data parallelism fits

Ideal when:

- you need to serve **many simultaneous users or API requests**
- the model fits in a **single GPU's memory**

> Example: a 7B-parameter LLM can often be quantized to 8 GB, fitting on a 16 GB GPU — you might run **8 replicas on 8 GPUs** to handle many chats in parallel.

##### Limitations

- **does nothing to reduce the latency of a single query** — each query is still processed by one GPU end-to-end
- if one GPU would take 10 seconds to handle a request, adding more GPUs for data parallelism **won't speed up that one request**
- serving a single request on multiple model replicas would be wasteful — it consumes multiple GPUs to process the same input without reducing latency
- to lower per-request latency, **model parallelism** is needed instead

**Resource usage**: running N replicas means storing **N copies of the model weights** in memory. Inefficient if the model is large and memory is limited.

Some frameworks support **multistream batching** on a single model instance to improve utilization (e.g., **vLLM** can dynamically batch multiple incoming queries on one GPU to improve throughput), which is an alternative to full replication.

##### Operational considerations

- straightforward — typically implemented as **horizontal scaling of pods**
- memory footprint **grows linearly** with replica count
- saturates overall GPU compute only if you have enough concurrent load
- if request rate is low, extra GPUs may sit idle — in that case, consolidate work onto fewer GPUs or **share GPUs among multiple models via time slicing or MIG**
- for dynamic workloads, leverage **Kubernetes autoscaling** to automatically adjust the number of replicas based on demand

#### Model Parallelism

The second motive for multi-GPU inference is to allow a **single large model** to be served by multiple GPUs in unison.

Unlike data parallelism (which replicates the entire model), **model parallelism splits a single model across multiple GPUs** — necessary for modern LLMs with **tens or hundreds of billions of parameters** that exceed the memory of one GPU.

This is possible because LLMs have a **layered architecture** composed of sequential transformer layers. This structure allows splitting the model in two ways:

- **tensor parallelism** divides the computations **within each layer** across GPUs
- **pipeline parallelism** assigns **different layers** to different GPUs

Both approaches can be combined for very large deployments. Individual GPUs hold a portion of the neural network and compute part of the forward pass.

**Trade-off**: reducing per-GPU memory usage and potentially latency for one inference comes at the cost of **added communication between GPUs**. High-bandwidth interconnects like **NVLink** or **NVSwitch** are often critical to handle the frequent data exchanges without bottlenecks.

> **NVLINK AND NVSWITCH: NVIDIA GPU INTERCONNECTS**
>
> NVIDIA developed two complementary technologies to enable high-speed GPU-to-GPU communication for model parallelism: **NVLink** for direct connections and **NVSwitch** for fabric-based networking.
>
> **NVLink** is a high-speed, point-to-point interconnect that provides direct GPU-to-GPU communication within a server node.
>
> - the fifth-generation **NVLink 5.0** (introduced with the **Blackwell** architecture) delivers up to **1.8 TBps bidirectional bandwidth per GPU** using 18 links at 100 GBps each
> - this represents a **2× improvement** over the previous **NVLink 4.0** generation (900 GBps on H100 GPUs)
> - and over **14× the bandwidth of PCIe Gen5**
> - early NVLink generations supported connecting **4 to 8 GPUs**
> - modern implementations can scale to **576 GPUs**, though practical deployments typically use **8 GPUs per node**
>
> **NVSwitch** is a high-performance **switching fabric** (a switching network architecture) that extends NVLink connectivity into a **fully connected, nonblocking mesh** where any GPU can communicate with any other GPU at full NVLink bandwidth simultaneously.
>
> - **NVSwitch 4.0** (for Blackwell systems) features **72 NVLink 5.0 ports per chip**
> - a dual-chip switch tray provides **144 ports** and **14.4 TBps switching capacity**
> - **NVIDIA HGX H100 and H200** systems use **4 NVSwitch 3.0 chips** to interconnect 8 GPUs
> - the **GB200 NVL72** rack-scale system connects 72 GPUs across multiple servers using NVLink Switch with 144 ports and **130 TBps of total GPU bandwidth**
>
> **The key distinction**: NVLink provides the **physical interconnect links**, while NVSwitch provides the **switching infrastructure** to scale these connections across many GPUs.
>
> For cross-node communication in multiserver clusters, systems combine NVLink/NVSwitch for intra-node communication with **InfiniBand** or **RoCE** networks for inter-node traffic. **GPUDirect RDMA** technology bridges these layers, enabling direct GPU-to-GPU data transfers across network boundaries **without CPU involvement**.
>
> Cost considerations: NVSwitch-based deployments can reach **multimillion-dollar price points** and require substantial **power and cooling infrastructure**. For training LLMs and running inference on models exceeding single-GPU memory capacity, the bandwidth and low-latency characteristics of NVLink and NVSwitch are often **essential to achieve acceptable performance**.

##### Tensor parallelism

**Tensor parallelism** slices the computations **within each layer** across multiple GPUs.

How it works:

- each GPU holds a **shard of the layer's weights** (for example, splitting a large weight matrix by columns or rows)
- each GPU processes a **portion of the layer's input**
- GPUs exchange **partial results** to construct the full output of the layer

> For instance, if a fully connected layer has a weight matrix too large for one GPU, it can be divided into multiple slices. Each GPU performs matrix multiplication of the input by its weight slice. The partial outputs are concatenated or summed to form the complete output.

This approach keeps **all GPUs busy on the same layer** (improving per-token latency) and effectively **multiplies the available memory bandwidth** by using several GPUs in parallel.

![Tensor parallelism](<assets/Tensor parallelism.png>)

**Figure 3-3. Tensor parallelism**

**Advantages**:

- directly reduces the **memory burden per GPU**, allowing extremely large models to load (e.g., splitting a **70B-parameter model** across 2 to 4 GPUs means each holds only 35B to 17.5B params)
- **lower latency per token** since GPUs compute in parallel

**Disadvantages**:

- adds **frequent communication overhead** — GPUs must sync after processing each layer or attention head
- if the interconnect is not fast enough, **communication can dominate runtime** (in poorly partitioned cases, **50–70%** of inference time)

<u>Practical rule:</u> tensor parallelism is best confined to **single-node setups** with high-bandwidth links (PCIe with NVLink or NVSwitch). Fine-grained tensor parallelism across multiple nodes with standard networking is **not advisable** due to latency costs.

The maximum tensor parallel degree is often **the number of GPUs in one server** (e.g., four-way tensor parallelism on a four-GPU node). Beyond that, use a machine with more GPUs or switch to **pipeline parallelism** between nodes.

##### Pipeline parallelism

**Pipeline parallelism** splits the model **vertically by layers**, assigning different consecutive layers to different GPUs.

How it works:

- the first few layers on GPU 0 process the input sequence
- intermediate activations pass to GPU 1 for the subsequent layers
- this continues through all pipeline stages, resembling an **assembly line**
- pipeline parallelism stores and transfers **intermediate activations at pipeline stages**, but **not every layer's outputs** as in tensor parallelism
- communications happen **only once per pipeline stage** (per forward pass) rather than at every layer operation

![Pipeline parallelism](<assets/Pipeline parallelism.png>)

**Figure 3-4. Pipeline parallelism**

**Key advantage**: minimizes inter-GPU **communication frequency**. Each pipeline stage requires only one activation handoff per forward pass, making pipeline parallelism **more tolerant of slower interconnects**.

This is **ideal when**:

- GPUs span **different servers**
- high-speed interconnects like NVLink **aren't available**

It allows scaling to models that exceed even a multi-GPU node's total memory (e.g., sharding a 175B model across two nodes).

**Disadvantages**:

- **does not improve single-request latency** — in fact, it can **increase latency** due to sequential stage processing
- introduces **idle time** because the next GPU in the pipeline cannot start processing the next token's data until the previous GPU has finished the previous token
- without careful management, multiple GPUs in a naive pipeline might be **underutilized**

**Mitigation — microbatching**:

Frameworks use microbatching or scheduling techniques: splitting the incoming batch or sequence into **microbatches** that are fed in a staggered fashion so all pipeline stages stay busy in parallel.

> Example: NVIDIA's **FasterTransformer** and **vLLM** implement pipelining with **automated microbatch scheduling** to avoid idle times.

**Bottom line**: pipeline parallelism shines for **multinode scaling** and **high-throughput batch processing** where latency of individual queries is less critical.

##### Hybrid parallelism

While tensor and pipeline parallelism address different challenges, they can be **combined** for maximum scalability in production deployments.

Many systems adopt a **hybrid parallelism** approach:

- **tensor parallelism within each node**
- **pipeline parallelism across nodes**

This leverages **fast local links** for intra-node splitting and uses **pipeline stages** to span multiple machines without requiring excessive cross-node communication.

<u>Rule of thumb:</u>

- use **pipeline parallelism across nodes** and **tensor parallelism within a node** when network links are slow
- if you have a **very fast interconnect between nodes**, tensor parallelism can extend across nodes as well

##### Coordination and fault tolerance

In all cases, distributed inference requires coordination — GPUs must communicate intermediate results using **collective operations**:

- **all-reduce**
- **all-gather**
- **send/receive**

These are typically performed using **NVIDIA's NCCL library** over high-speed links.

> If one GPU and the node in a model-parallel group fails, the inference will **fail entirely**; there is **no graceful fault tolerance** for a partially missing model shard.

Deploying model parallel inference in Kubernetes may benefit from:

- **pod affinity/anti-affinity rules** (to colocate GPUs or separate failure domains)
- **appropriate health checks** to restart the whole group if one part dies

> **CONTROLLING POD PLACEMENT FOR MULTI-GPU WORKLOADS**
>
> Kubernetes **affinity** and **anti-affinity** rules let you control where pods land relative to each other, essential for multi-GPU deployments.
>
> **Affinity** colocates pods on the same node, rack, or zone. Use this for **model-parallel inference** where GPUs must communicate frequently. Keeping tensor-parallel pods together on the same node minimizes latency over fast local interconnects like NVLink.
>
> **Anti-affinity** spreads pods apart across nodes or zones. Use this for **throughput-scaling deployments** where independent model replicas should avoid single points of failure. If one node goes down, replicas on other nodes continue serving.
>
> Both mechanisms support:
>
> - **hard constraints** — a pod will not schedule unless the rule is satisfied
> - **soft constraints** — scheduler prefers but does not require the placement
>
> Hard rules are critical for **correctness**, such as ensuring model shards land together. Soft rules **optimize performance** when possible but allow fallback placement.

#### Single-Node Versus Multinode Inference

When deploying model-parallel inference on Kubernetes, you face a fundamental topology choice:

- **concentrate** your GPUs on a single node, or
- **spread** them across multiple nodes

Each approach has distinct trade-offs.

##### Single-node multi-GPU inference

All GPUs used for the model or replicas are in **the same server**. Advantages:

- **high-speed local interconnects** — within one machine, GPUs often communicate via **PCIe** (and on high-end GPU servers, via **NVLink** or **NVSwitch** between GPUs)
- for example, **NVIDIA DGX-class nodes** have NVSwitch connecting all eight GPUs with up to **900 GBps** bandwidth — far faster than typical network links
- parallel strategies that involve frequent communication (like **tensor parallelism**) work **very well within a single node**

In Kubernetes, utilizing multiple GPUs on one node is straightforward:

- request the number of `nvidia.com/gpu` resources in the pod spec
- the scheduler places the pod on a node that has that many free GPUs
- the container can see all GPUs assigned to a pod (e.g., via the environment variable **`CUDA_VISIBLE_DEVICES`**)
- your inference server or code can then initialize model parallelism across those devices

![Multiple GPUs on a single node](<assets/Multiple GPUs on a single node.png>)

**Figure 3-5. Multiple GPUs on a single node**

##### Multinode multi-GPU inference

Necessary when the model is so large that **no single node has enough GPU memory** (for example, some teams run **175B+ parameter models** across two or more nodes with eight **A100 80 GB** GPUs each).

Communication goes over the **network interface** between nodes:

- **InfiniBand**
- **Ethernet**

Network bandwidth between nodes (e.g., 100-Gbit Ethernet at **12.5 GBps**) is an **order of magnitude slower** than intra-node NVLink (up to **900 GBps**).

This makes **pipeline parallelism** the preferred strategy across nodes, as it sends **larger chunks less frequently**:

- each node processes a substantial portion of the workload before passing it to the next
- the system becomes more **resilient to network latency**

If multinode is used:

- use the **fastest network available**
- ensure **NCCL** is configured to use **RDMA** if possible

> NCCL can operate over **sockets** or **InfiniBand**. In Kubernetes, you must also ensure the pods can **discover each other's addresses** for NCCL (sometimes using Kubernetes service IPs or host networking for performance).

> **WHAT IS NCCL AND RDMA?**
>
> **NCCL** is a high-performance library designed for efficient **GPU-to-GPU communication** in multi-GPU and multinode environments. It provides optimized collective communication primitives such as **all-reduce**, **broadcast**, **reduce-scatter**, and **all-gather**, which are essential for synchronizing model parameters or intermediate results during tensor and pipeline parallelism.
>
> NCCL is typically not used directly by end users; it is leveraged under the hood by inference runtimes like **vLLM**, and frameworks such as **PyTorch**, which abstract its complexity behind higher-level APIs. However, in distributed Kubernetes deployments, advanced users may need to tune NCCL-related settings (e.g., **`NCCL_SOCKET_IFNAME`**) to ensure optimal performance over specific network interfaces.
>
> When available, **RDMA** can be used by NCCL to **bypass the CPU** and **directly access GPU memory on remote nodes**, significantly reducing latency and improving bandwidth in multinode inference setups. RDMA typically requires **specialized accelerated networking devices**, such as **InfiniBand** or **RoCE-capable network adapters**.
>
> Properly configured, NCCL with RDMA plays a crucial role in achieving **scalable, high-throughput inference** for LLMs across multiple GPUs and nodes.

For multinode inference, the typical approach is to run **one pod per node** and coordinate them externally. Popular inference runtimes often leverage orchestration frameworks to simplify this process:

- **vLLM** in multinode deployments uses **Ray**, a distributed computing framework with its own scheduler, to orchestrate inference across multiple nodes
- on Kubernetes, **Ray runs inside pods managed by the KubeRay operator**
- Kubernetes still schedules and restarts pods, while Ray's runtime coordinates distributed vLLM workers across nodes, handling task placement, node discovery, and some fault-tolerance concerns
- other runtimes such as **Hugging Face's TGI** rely on Kubernetes-native constructs like **StatefulSets** or **Deployments**, where one pod acts as a coordinator (commonly referred to as **"rank-0"**) and manages communication between model partitions on different pods

![Multiple GPUs on multiple nodes](<assets/Multiple GPUs on multiple nodes.png>)

**Figure 3-6. Multiple GPUs on multiple nodes**

Regardless of the orchestration method:

- **pod affinity** ensures pods land on distinct GPU nodes or optimized locations
- **service discovery** lets pods resolve each other by name or IP address
- Kubernetes provides built-in mechanisms like **pod hostnames** and **subdomains** to facilitate pod discovery
- **NCCL** can perform topology discovery automatically within a node but typically requires **explicit network interface configuration across nodes**

##### Scaling efficiency

Latency and bandwidth differences mean the **scaling efficiency** going from single-node to multinode may drop:

- within one node: **near-linear speedup** (e.g., four GPUs deliver approximately 3.5× the throughput of one GPU for a well-optimized model)
- multinode: **diminishing returns** if the network becomes a bottleneck
- **collective operations** (like all-reduce) across nodes must be synchronized — if one node is slightly slower or has higher network latency, it can slow the others
- performance becomes **less predictable**; the **slowest node dictates the pace**

##### Failure handling

- **Single-node**: failure of the node naturally leads to pod termination, which Kubernetes handles straightforwardly
- **Multinode**: failure of any participating pod typically **disrupts the entire inference job** due to incomplete model partitions; recovery usually requires **restarting the full group of pods**

Distributed inference jobs require **all-or-nothing semantics** both for initial scheduling and recovery (a pattern known as **gang scheduling**).

Kubernetes concepts like **`PodDisruptionBudgets`** help minimize disruptions during planned maintenance. Some advanced setups consider **checkpointing strategies**, though these are less common for stateless inference workloads and more often used during training.

##### Summary

- **single-node deployments** remain preferable for model-parallel inference due to **lower complexity and higher efficiency**
- **multinode deployments** become necessary due to model size, **pipeline parallelism**, **expert parallelism** (for Mixture-of-Experts models), or other network-efficient methods
- combined with robust orchestration solutions like **Ray.io** or Kubernetes-native deployment patterns, this ensures **reliable and efficient large-scale inference operations**

#### Encode this

- **Data parallelism = many model replicas → throughput scaling, no latency reduction**
- **Model parallelism = one model split across GPUs → memory savings and possibly lower latency, at communication cost**
- **Tensor parallelism splits work inside each layer (frequent comms, best inside one node)**
- **Pipeline parallelism splits layers across stages (rare comms, friendlier to slower networks)**
- **Hybrid parallelism: tensor inside nodes, pipeline across nodes**
- **NVLink/NVSwitch make intra-node communication 10–100× faster than typical Ethernet**
- **Model-parallel pods need affinity + gang scheduling — partial failures collapse the whole inference job**
- **Multinode coordination commonly uses Ray + KubeRay (vLLM) or rank-0 StatefulSets (TGI)**

#### Recall prompt

*Why is tensor parallelism usually confined to a single node while pipeline parallelism is the preferred strategy across nodes?*

[Back to Contents](#contents)

### GPU Resource Optimizations

This subsection consolidates **key GPU optimization strategies** for production deployments. Some techniques (MIG, time slicing) were covered earlier in this section; the focus here is on putting them together with additional best practices.

> **Maximizing GPU utilization and avoiding unused memory is key in production LLM inference, since GPUs are expensive resources.**

#### GPU memory defragmentation

As models load and unload, or as dynamic inference workloads allocate memory (for example, varying sequence lengths), the GPU's memory allocator can become **fragmented**:

- free memory exists in **many small chunks** rather than one contiguous block
- can **prevent large models from being loaded**
- can lead to **out-of-memory errors** even when enough total memory is free but not contiguous

Mitigations:

- **pre-allocate large blocks** (e.g., load all model weights on startup, use memory pools for scratch space) to avoid heap fragmentation
- **PyTorch's caching allocator** helps, but long-running pods might still suffer fragmentation over time
- if GPU memory usage grows or OOMs occur after many requests, **periodically restart the pod** to clear fragmentation
- PyTorch provides an **"expandable segments"** feature that reduces fragmentation by allowing the allocator to **expand existing memory segments** rather than create new ones
- on the inference side, **vLLM's PagedAttention** is essentially a **defragmentation technique for the KV cache**

> **Detection**: if available memory decreases after serving many requests, it's probably memory defragmentation. Proper monitoring is essential.

#### GPU sharing and consolidation

> **An idle GPU is wasted money.**

If your LLM uses only **30% of a GPU's compute and memory**, consider running **multiple model instances** or other workloads on the same GPU:

- **MIG** on supported hardware for clear separation (e.g., two 6B-parameter models on one 80 GB A100, each in a 40 GB MIG slice)
- **time slicing** (see [Time Slicing](#time-slicing))

Another approach: **multimodel servers** that load several models onto one GPU and route requests:

- **NVIDIA Triton**
- **AWS Multi-Model Server**

These can support multiple models per GPU, dynamically unloading less-used models if needed.

<u>Best practice:</u> **profile usage**. If a model uses only 50% of GPU memory, that remaining 50% could host another smaller model or a second copy to double throughput.

<u>Caveat:</u> don't overload memory — leave some margin since **driver overhead** and **fragmentation** can eat a few percent.

> Kubernetes doesn't natively know if a GPU is **"only half used"** — it's up to you to **bin-pack wisely** using MIG or by deploying multiple pods to the same node.

#### Quantization and compilation

Optimizing the model itself can reduce GPU needs:

- **4-bit or 8-bit quantization** of weights dramatically cuts memory per model copy (at some accuracy cost)
- if an LLM can be quantized from 16-bit to 8-bit with negligible quality loss, you potentially **halve the number of GPUs** needed
- many open models have 8-bit or 4-bit quantized versions available

> Example: a **70B model** in full precision needs 280 GB (70B × 4 bytes/param), but in **4-bit mode only ~35 GB** (70B × 0.5 byte/param) → can fit on a **single 48 GB GPU**.

**vLLM** and **TGI** servers support loading such quantized models. Use **optimized runtimes** to improve inference speed per GPU — faster models handle more load with the same hardware.

#### Autoscale

Autoscaling multi-GPU deployments can be tricky if they are model-parallel:

- when a model is split across **four GPUs**, you cannot scale down to two GPUs or scale up to six GPUs
- you must scale in **whole replica units**: either remove all four GPUs or add another complete four-GPU group

For **throughput scaling**, Kubernetes-based autoscaling is effective:

- **KEDA**
- **HPA**
- **Knative**

These can scale on **RPS**, **concurrency**, or **latency**.

#### Placement and affinity

For multi-GPU nodes it is important to know the **topology**:

- on some eight-GPU servers, **not all GPUs are directly connected** — there may be NVLink links in a mesh or groups
- example: an **NVIDIA DGX A100** has NVSwitch all-to-all, but other systems may have **two groups of four GPUs each**
- if your model parallelism uses four GPUs, performance is better if those four are all within **one NVLink group**

Tools and techniques:

- use **`nvidia-smi topo -m`** to display the mesh grouping
- Kubernetes won't automatically account for that
- you can use the node's hardware knowledge and **assign specific GPU indices** by using the device plug-in capabilities to pick specific GPUs by index

> Manually selecting GPU indices is an **advanced optimization**. For most cases, Kubernetes will just assign any four GPUs. But if you care about intra-node latency, you may want to pin to, say, **GPU 0–3** if they're within the same NVSwitch cluster on that node.

#### Optimize I/O and initialization

Large models take time to load from disk or network into GPU memory:

- if you scale pods up and down, you **pay that cost each time**
- amortize it by **keeping pods warm** if possible
- see [Optimize vLLM Startup Time](#optimize-vllm-startup-time) for detailed loading optimization techniques

#### Monitor GPU health

GPUs can encounter issues like:

- **ECC memory errors**
- **high temperature throttling**

Operational guidance:

- ensure **node-level monitoring** and **alerts** for such events
- Kubernetes won't automatically reschedule a pod if the GPU starts erroring but hasn't crashed
- you may need a daemon that checks with **`nvidia-smi`** for errors and then **taints the node** or **restarts pods**
- running **NVIDIA DCGM** and integrating with Kubernetes node health can help
- a **flaky GPU** in a model-parallel group can cause **wrong results or crashes**, so catching hardware issues early is important

#### Encode this

- **Memory fragmentation is real for long-running pods; pre-allocation + PagedAttention + periodic restarts mitigate it**
- **Idle GPU = wasted money; combine MIG/time-slicing, multimodel servers, and bin-packing to keep GPUs busy**
- **Quantization (4-bit/8-bit) is one of the cheapest ways to cut GPU count**
- **Model-parallel groups must scale in whole-replica units**
- **NVLink topology matters — `nvidia-smi topo -m` reveals which GPUs are close to each other**
- **DCGM + node-level monitoring catches GPU faults before they corrupt model-parallel inference**

#### Recall prompt

*Why must autoscaling a model-parallel deployment work in whole-replica units rather than per-GPU increments?*

[Back to Contents](#contents)

### GPU Lessons Learned

This section explored how Kubernetes integrates GPU resources through **device plug-ins**, **feature discovery**, and **advanced management capabilities** for AI workloads.

**Kubernetes extends beyond its native CPU/memory scheduling**

The **device plug-in framework**, combined with **Node Feature Discovery (NFD)** and **GPU Feature Discovery (GFD)**, enables automatic detection and labeling of GPU capabilities. This allows workload-specific scheduling based on GPU model, driver version, and hardware features — the foundation for both simple resource-based scheduling and sophisticated **topology-aware placement**.

**GPU scheduling requires different strategies than traditional workloads**

- **resource-based scheduling** allocates GPUs as countable units
- **label-based scheduling** with `nodeSelector`, affinity rules, and taints enables precise placement based on GPU characteristics
- the emerging **Dynamic Resource Allocation (DRA) API** promises more flexible resource handling, although device plug-ins remain the production-ready standard for most deployments

**Sub-GPU allocation maximizes hardware utilization**

- **Time slicing** enables **temporal sharing** — suitable for inference workloads with intermittent GPU usage
- **Multi-Instance GPU (MIG)** provides **hardware-level partitioning** with memory isolation, creating dedicated GPU slices with guaranteed resources and performance isolation
- each approach involves trade-offs among **isolation**, **overhead**, and **scheduling complexity**

**Multi-GPU inference is necessary when models exceed single-GPU memory**

- **Tensor parallelism** distributes individual operations across GPUs, requiring high-bandwidth interconnects and tight synchronization
- **Pipeline parallelism** splits model layers across GPUs, balancing computation distribution with bubble overhead from sequential dependencies
- **Data parallelism** replicates the entire model across GPUs, processing different batches simultaneously
- these strategies demand careful orchestration across pods and nodes, with Kubernetes providing scheduling primitives, while runtime frameworks handle the coordination logic

**The NVIDIA GPU Operator consolidates GPU management**

A single operator deploys **device plug-ins**, **feature discovery**, **monitoring (DCGM)**, and **runtime components**. The declarative approach via **`ClusterPolicy`** resources simplifies GPU cluster configuration and ensures consistent GPU stack deployment across nodes, reducing operational complexity compared to manual component installation.

#### Encode this

- **Discovery → scheduling → sharing → multi-GPU → operator-managed: the operational arc of GPUs on Kubernetes**
- **GPU choice on Kubernetes is a topology decision, not just a resource decision**
- **Multi-GPU LLM inference is fundamentally a distributed system, not just a "request more GPUs" problem**
- **The GPU Operator is the production glue that keeps drivers, runtime, monitoring, and sharing consistent**

#### Recall prompt

*What is the operational arc of running GPU workloads on Kubernetes, from a fresh cluster to a production multinode LLM deployment?*

> **Note on memory units**: GPU manufacturers like NVIDIA typically advertise memory in **decimal gigabytes** (GB, base-10), while Kubernetes often uses **binary gibibytes** (GiB, base-2). The difference is small but notable: **40 GB ≈ 37.25 GiB** and **80 GB ≈ 74.5 GiB**. These notes use GB to match industry practice.

[Back to Contents](#contents)

## Model Data Storage, Access & Registry in K8s

![MLOps Portability Cover Image](<assets/MLOps-Portability-Cover-Image.png>)

One of the most fundamental challenges when running LLMs on Kubernetes is managing the **sheer size of the model data**. LLMs can range from a **few gigabytes to nearly a terabyte** in size, and efficiently bringing this data into a cluster where runtimes can access it requires careful consideration.

The main portion of these models consists of the **model parameters** and can be extremely large. There is a wide range of variations, from large models that are likely impractical for on-demand use to more lightweight models that can be run on your own cluster and easily downloaded when needed.

**Table 2-1. Open source models and their sizes**

| Name | Vendor | Parameters | Size |
| --- | --- | --- | --- |
| **Llama 4 Maverick** | Meta | 400 billion (MoE, 17B active) | ~800 GB |
| **DeepSeek-V3** | DeepSeek | 671 billion (MoE, 37B active) | ~700 GB |
| **Llama 3.1 405B** | Meta | 405 billion | ~750 GB |
| **Qwen3-235B** | Alibaba | 235 billion (MoE, 22B active) | ~118 GB |
| **Mixtral 8x22B** | Mistral | 141 billion (MoE, 39B active) | ~88 GB |
| **GPT-OSS 120B** | OpenAI | 117 billion (MoE, 5B active) | ~70 GB |
| **Gemma 2 27B** | Google | 27 billion | ~54 GB |
| **Granite 13B** | IBM | 13 billion | ~26 GB |
| **Falcon 2 11B** | TII | 11 billion | ~22 GB |
| **Mistral 7B** | Mistral | 7 billion | ~14 GB |

Even smaller models can pose significant challenges for Kubernetes administrators when managing them efficiently within a cluster. Understanding how to **store and organize these large datasets** effectively is critical for a successful LLM operation.

This section explores how to manage data-heavy artifacts efficiently within a Kubernetes cluster:

- **Model Data Storage Formats** — how LLM data is packaged (Weight-Only, Self-Contained, ONNX, Safetensors, GGUF/GGML)
- **Model Registry** — where to find and how to retrieve model data (Hugging Face, MLflow, Kubeflow, OCI)
- **Accessing Model Data in Kubernetes** — Kubernetes-native methods for fetching and accessing model data (`storageUri`, storage initializers, PVCs)

Most of the time, ML models can be treated as **opaque boxes**, accessed by the inference services described in [Model Servers & Controllers](#model-servers--controllers). However, **understanding the package formats** used to distribute these models is still valuable for successful integration.

[Back to Contents](#contents)

### Model Data Storage Formats

When working with LLMs, their **massive size** (measured in billions of parameters) is the first thing we notice. However, models shared on platforms like Hugging Face contain **more than just the raw weight parameters**. These distributed models also include **metadata** and, in some cases, the **model's architecture**, which defines how the neural network layers and transformers are wired together.

For operators, such distributed models often feel like **black boxes**. Yet, understanding **which format they are stored in is critical** because not every packaged model can run with every runtime. Some formats are **highly flexible** and can be operated by multiple runtimes; others are **closely tied to specific runtime platforms**.

At a high level, model storage formats can be grouped into **two categories**:

- **Weights-only formats** — store only the learned parameters (weights and biases). Architecture, hyperparameters, and metadata are excluded, so the runtime must **already know** how to reconstruct the network before applying the weights
- **Self-contained formats** — store both the weights and the model architecture, along with hyperparameters and other metadata. Allow the model to be loaded and run **without prior knowledge** of the network structure, making them easier to deploy as standalone artifacts

The boundary between both categories is **gradual**. Some formats that seem self-contained may still require external components, such as **tokenizer files** for language models.

For LLMs, the trend is moving toward **mostly self-contained formats** like **GGUF** and **Safetensors**. These formats simplify distribution but remain tightly coupled to specialized runtimes. **True runtime independence** — where a model could be loaded and run in any compatible environment, regardless of the model's training framework — remains a **work in progress**. The **CNCF ModelPack** specification is a standardization attempt in this direction, where model data is packed in **Open Container Initiative (OCI) container images**.

In an ideal world, much like OCI container images abstract application internals, model storage formats would draw a clear boundary between:

- **model data** — produced by data scientists
- **model execution** — managed by MLOps/DevOps engineers in production

However, today's landscape **prioritizes getting models operational quickly** rather than standardizing runtime compatibility. As the field matures, expect **stronger separation** between model creation and deployment concerns.

#### Weight-Only Formats

**Weight-only model formats** store the **numerical parameters (weights and biases)** of a trained neural network **without** including the model's architecture or preprocessing components.

These formats are commonly used during the **development and experimentation** phases, where flexibility and minimal overhead matter more.

Since weight-only formats lack architectural details:

- the runtime must **already know** the network structure
- this knowledge allows the runtime to correctly **reconstruct the model** and apply the stored weights
- weight-only formats are **tightly coupled** to their respective machine learning frameworks

The most commonly used weight-only formats correspond to the two dominant ML frameworks: **PyTorch** and **TensorFlow**. While both provide their own serialization formats, **PyTorch** has become the **de facto standard** for LLM development.

##### Common weight-only formats

- **PyTorch State Dict (`.pt`, `.pth`)** — PyTorch's native format for serializing weight tensors using the `state_dict` method of `torch.nn.Module`. Widely used for LLMs such as **Llama**, **GPT**, and **BLOOM** during development and fine-tuning stages
- **TensorFlow checkpoints (`.ckpt`)** — primarily used in TensorFlow's ecosystem for storing model weights. While it was historically used for models like **BERT**, its relevance for modern LLMs has **declined** as PyTorch gained dominance in the GenAI space
- **NumPy arrays (`.npy`, `.npz`)** — NumPy's native serialization format for numerical arrays. Useful for storing **smaller models** or **individual weight matrices**, but lacks the structure and metadata needed for modern LLM deployments

These formats primarily store **raw tensor data** with **minimal metadata**, making them **highly compact** but **dependent on external runtime code**.

![Example of a model stored in a weight-only format](<assets/Example of a model stored in a weight-only format.png>)

**Figure 2-1. Example of a model stored in a weight-only format**

A model stored in a weight-only format requires **the same network architecture to be reconstructed during inference**. You must manually replicate the training architecture in the inference environment, ensuring both sides can correctly interpret the stored weight tensors.

While weight-only storage formats are **well suited during development and experimentation**, they are **very closely coupled** to the ML code that evaluates those parameters.

#### Self-Contained Formats

A better fit for **production deployments** are models stored and distributed in **self-contained formats**, which bundle more than just the raw weights.

These formats include critical **metadata and structural information**, making models easier to share and run across multiple runtime environments without requiring the original codebase used during training.

##### What self-contained models can carry

- **Weights and biases** — the numerical parameters of the neural network, the bulk of the model size
- **Model architecture** — either as a reference to a well-known architecture or described explicitly as a connected graph of layers
- **Tokenizer and vocabulary data** — often included in language models to preprocess text before inference
- **Hyperparameters** — learning rate, batch size, number of epochs used during training
- **Other metadata** — descriptive information such as model origin, authorship, and additional context for model discovery and reproducibility

Some self-contained formats also support **pre- and post-processing scripts** for transforming inputs before inference and converting outputs into a usable form afterward.

![Example of a self-contained model where the runtime is independent of the training code](<assets/Example of a self-contained model where the runtime is independent of the training code.png>)

**Figure 2-2. Example of a self-contained model where the runtime is independent of the training code**

##### Reality check: "mostly self-contained"

While fully self-contained formats aim to encapsulate everything needed for inference, in practice **as of 2026, no such format exists**. No widely used format today includes **all components** required for inference — the model weights, tokenizer, vocabulary data, and complete architecture — in a single artifact.

As a result, even formats often described as "self-contained" are better categorized as **mostly self-contained** because they still rely on **external components and runtime dependencies**.

These mostly self-contained formats may bundle the model weights and partial metadata but typically omit critical components like the **tokenizer** or **detailed model architecture**, remaining tied to specific inference runtimes or frameworks that "understand" how to interpret the stored data correctly. For example, popular formats like **Safetensors** and **GGUF** include model weights and some metadata but still require external components for complete model inference.

##### Common mostly self-contained formats for LLMs

- **Safetensors (`.safetensors`)** — a mostly self-contained format designed for secure and efficient weight storage, frequently used for LLMs on platforms like Hugging Face. Improves safety and performance over standard PyTorch weight files, but **tokenizer information** (e.g., `tokenizer.json`) and **model architecture definitions** are not embedded, requiring additional files or runtime knowledge to fully reconstruct the model during inference
- **GGUF/GGML (`.gguf`, `.ggml`)** — specialized self-contained formats optimized for **efficient inference with quantized weights**, supporting both CPU and GPU execution. Include the model's weights and basic architecture metadata but remain closely tied to runtimes like **`llama.cpp`** and **vLLM**. GGUF can also store **tokenizer data** (vocabulary, special tokens)
- **ONNX (`.onnx`)** — a versatile, self-contained format for **model interoperability**. Often described as self-contained, ONNX stores the model's weights, architecture, and metadata but lacks critical components like the **tokenizer and vocabulary data**, which are essential for LLMs. This makes it **mostly self-contained**, requiring additional files for complete language model inference
- **TensorFlow SavedModel** — a fully self-contained, directory-based format that stores weights, architecture, and auxiliary files. Common in TensorFlow ecosystems but **rarely used for modern LLMs**
- **Hugging Face Transformers** — best described as a **packaging convention** rather than a standalone model format. It organizes models into a directory containing multiple files essential for running language models. The convention typically includes model weights stored in **Safetensors** (`.safetensors`) or PyTorch's `state_dict` (`.bin`), along with two key files: **`tokenizer.json`** and **`config.json`**

> **`TOKENIZER.JSON` AND `CONFIG.JSON`**
>
> The **`tokenizer.json`** and **`config.json`** files are critical components for running LLMs effectively in the Hugging Face ecosystem and beyond.
>
> **`tokenizer.json`** stores the **tokenization rules and vocabulary mapping** for converting raw text into token IDs:
>
> - defines how input text is split into tokens, using techniques like **Byte-Pair Encoding (BPE)**
> - includes **special tokens** used for padding, start-of-sequence, and end-of-sequence markers
>
> **`config.json`** describes the **model architecture and hyperparameters**:
>
> - number of layers
> - attention heads
> - hidden sizes
> - feed-forward dimensions
> - the **model type** (e.g., `llama`), influencing how the runtime reconstructs the model graph
>
> Together, these files ensure the model can:
>
> - **preprocess input correctly** (`tokenizer.json`)
> - **build the required network structure** (`config.json`)
>
> Without them, the runtime **cannot properly tokenize input text or load the model architecture** for inference.
>
> These files have become **de facto standards** in the machine learning community, extending utility beyond the Hugging Face ecosystem. Frameworks and tools outside of Hugging Face often adopt these conventions for model interoperability and consistency.

Most current model formats for LLMs fall into the category of **mostly self-contained**, often omitting key components such as tokenizers, vocabulary data, and preprocessing logic. Despite these gaps, some formats have gained significant traction due to their **balance between portability and efficiency**:

- **Safetensors** and **GGUF/GGML** are the most commonly used today, both optimized for efficient weight storage with metadata
- **ONNX** is less frequently used for LLMs but serves as a useful reference for a **more fully self-contained format**

> **THE QUEST FOR TRUE MODEL PORTABILITY**
>
> The following sections dive into the technical details of specific model formats. While these details may seem tangential to Kubernetes operations, they address a fundamental operational concern: **achieving clear separation between model data and runtime execution**.
>
> The goal is to achieve **true model portability**, where models can be distributed and executed as **self-contained artifacts**, much like how Docker revolutionized the deployment of arbitrary software workloads across diverse environments. Reaching this level would require broader standardization across both the **model file structure** and the **runtimes capable of executing them**.
>
> Ideally, a model stored in a standardized format could be loaded by any compliant runtime. This would eliminate manual adjustments for tokenization, quantization, or architecture specifics. Such a shift would empower a more diverse set of tools and frameworks, **reducing lock-in** to specific ecosystems while making model distribution as seamless as containerized applications.
>
> This separation is **the holy grail** that would let operators treat models as **interchangeable artifacts**, independent of the runtimes that execute them. We haven't reached this ideal yet, but examining existing formats reveals **how close we are** to achieving true runtime-model independence.

#### ONNX

The **[Open Neural Network Exchange (ONNX)](https://onnx.ai/)**, codeveloped by **Microsoft** and **Facebook** in **2017**, was designed as a **framework-independent format** for representing machine learning models.

ONNX aims to **standardize how models are shared between tools**, allowing developers to train a model in one framework and deploy it in another without requiring framework-specific conversions.

##### File structure

ONNX models are stored in a **single `.onnx` file** using **Protocol Buffers (Protobuf)** for compactness and platform neutrality. Each file contains **three main components**:

- **Computational graph** — defines the network's structure and data flow
- **Learned parameters** — weights and biases
- **Metadata** — input/output specifications, operator sets, and versioning details

This structure makes ONNX a **promising example of a self-contained format**, combining architecture, weights, and operational metadata in a single artifact.

##### Why ONNX falls short for LLMs

ONNX falls short for LLMs because it lacks essential components such as:

- **tokenizers**
- **vocabulary data**
- **preprocessing logic**

For tasks like natural language generation, this missing information makes supplying **additional files alongside the `.onnx` model necessary**. Without these components, an ONNX model alone cannot transform raw text into tokenized inputs, **limiting its suitability for modern LLM deployments**.

##### Op set compatibility

ONNX has **broad support across runtimes**:

- **ONNX Runtime**
- **TensorRT**
- **OpenVINO**
- **Triton Inference Server**

…making it highly portable, but compatibility depends on the **set of operations** (such as matrix multiplication, convolution, and attention mechanisms) that a model uses.

Each runtime supports a defined **operator set (op set)**, which specifies the available operations a model can use. If a model relies on operations **outside a runtime's supported set**, it may fail to load unless extended with **plug-ins or custom runtime extensions**. This challenge further complicates its adoption for complex architectures like those used in LLMs.

##### Outlook for ONNX

Despite these limitations, ONNX provides a **conceptual blueprint** for what a fully self-contained model format for LLMs could look like. If expanded with richer metadata and native support for **tokenizer definitions**, it could offer a more complete solution for the LLM use case.

As of 2026, ONNX remains better suited for models in domains like **computer vision**, where preprocessing is often simpler and less tightly coupled with the model.

#### Safetensors

**[Safetensors](https://github.com/huggingface/safetensors)**, developed by **Hugging Face in 2021**, is a modern model serialization format designed to **securely store and share** machine learning model weights while addressing security vulnerabilities and performance limitations of earlier formats like PyTorch's `.pt` and `pickle`.

##### Why Safetensors exists

The **`pickle` format**, often used in PyTorch, can **execute arbitrary Python code** when deserializing models, posing significant security risks when sharing models.

Safetensors **prevents code execution vulnerabilities** by focusing strictly on storing tensor data, making it a **safer and more efficient choice** for model serialization.

![Internal structure of a Safetensors model](<assets/Internal structure of a Safetensors model.png>)

**Figure 2-3. Internal structure of a Safetensors model**

##### File structure

Each `.safetensors` file begins with a **header containing metadata**, including a serialized JSON object describing each tensor stored in the file. The header includes:

- the tensor's **data type**
- **shape**
- **byte offsets** where the tensor data resides within the file

This structure allows for **zero-copy loading**, where tensor data can be **directly mapped to memory** without unnecessary CPU overhead, improving inference speed, especially when working with LLMs.

##### Sharding for large models

Safetensors supports **sharding**, which allows large models to be split across multiple smaller files. Each shard contains a portion of the model's tensors and is accompanied by an **index file** (e.g., `model.safetensors.index.json`).

The index file maps the names of tensors in the different layers to their respective shard files.

> Example: **Llama 4.1 405B** is released with **30 safetensor files** named like `model-0000x-of-00030.safetensors` and accompanied by a `model.safetensors.index.json` file.

##### Example 2-1. Index file mapping tensors to shard files

```json
{
  "metadata": {
    "total_size": 141107412992
  },
  "weight_map": {
    "lm_head.weight": "model-00030-of-00030.safetensors",
    "model.embed_tokens.weight": "model-00001-of-00030.safetensors",
    "model.layers.0.input_layernorm.weight": "model-00001-of-00030.safetensors",
    "model.layers.0.mlp.down_proj.weight": "model-00001-of-00030.safetensors",
    "model.layers.0.mlp.gate_proj.weight": "model-00001-of-00030.safetensors",
    "model.layers.0.mlp.up_proj.weight": "model-00001-of-00030.safetensors",
   ...
    "model.layers.1.input_layernorm.weight": "model-00002-of-00030.safetensors",
    "model.layers.1.mlp.down_proj.weight": "model-00002-of-00030.safetensors",
    "model.layers.1.mlp.gate_proj.weight": "model-00001-of-00030.safetensors",
    "model.layers.1.mlp.up_proj.weight": "model-00002-of-00030.safetensors",
   ...
  }
}
```

What to notice:

- **`metadata.total_size`** — total size of all model weights, in bytes (approximately **131 GB** for this model)
- **`weight_map`** — maps each tensor name to the specific shard file containing it
- **`lm_head.weight`** — the final output layer weight is in shard file **30**
- additional tensor mappings show how different layers are distributed across shard files

Sharding is particularly useful for **extremely large models** where a single file might be impractical due to storage limitations. This approach also enables **parallel loading**, as different shards can be fetched and processed concurrently.

##### Why Safetensors is "mostly" self-contained

The primary limitation is that **tokenizer information and model architecture definitions are not included** within the `.safetensors` file itself. Essential files like `tokenizer.json` and `config.json` must be supplied separately for language model inference — a key reason why it remains **tightly coupled to the Hugging Face Transformers ecosystem** that provides this extra metadata.

The format's structure and focus on **secure serialization** have made it increasingly popular, especially for **LLM storage and sharing**. Safetensors is now the **default weight format** for many large-scale models distributed on Hugging Face.

#### GGUF and GGML

The **GPT-Generated Unified Format (GGUF)** and its predecessor **GPT-Generated Model Language (GGML)** are specialized formats developed for optimizing the storage and execution of LLMs on **resource-constrained hardware** such as CPUs and edge devices.

Originating from the **[`llama.cpp` project](https://github.com/ggerganov/llama.cpp)** led by **Georgi Gerganov**, both formats focus on **efficient inference with minimal hardware requirements**. While GGML was an important first step, GGUF represents a **significant refinement**, addressing many of its predecessor's limitations.

##### Quantization focus

A defining feature of GGUF and GGML is their focus on **quantization**, a technique that **reduces the precision of model weights** from floating-point values to lower-bit representations such as:

- **8-bit**
- **4-bit**
- even **2-bit integers**

By lowering precision, both **memory footprint** and **computational overhead** are significantly reduced. This allows models to run effectively **without dedicated GPUs** while maintaining acceptable inference accuracy.

##### Backward compatibility

A key improvement in GGUF is its focus on **backward compatibility**:

- as LLMs evolve and architectures become more complex, maintaining compatibility with existing tools can be challenging
- GGUF's **modular design** allows newer models to retain compatibility with older runtime versions, provided the core components remain unchanged
- this **prevents the need for frequent format conversions** when updating models
- when GGUF is updated to support new features, existing models remain **functional without requiring conversion**

##### LLM-specialized vs general-purpose

Unlike **ONNX**, which was designed as a **general-purpose format** for a wide range of machine learning tasks, **GGUF is specialized for LLM inference**. While originally designed for CPU-based inference, GGUF is now **widely supported across both CPU and GPU execution** by runtimes like **`llama.cpp`** and **vLLM**.

##### GGUF vs Safetensors

When compared to Safetensors:

- **GGUF** attempts to bundle **more metadata directly within the model file itself**, including basic tokenizer information and runtime metadata
- **Safetensors** focuses primarily on **weight storage with minimal metadata** and relies on external files for tokenizer definitions and model configurations

GGUF stores **token mappings and model parameters in a single file**, but it still depends on specific external runtimes for complete inference — keeping it in the category of **mostly self-contained formats**.

![Internal structure of a GGUF file](<assets/Internal structure of a GGUF file.png>)

**Figure 2-4. Internal structure of a GGUF file (source: @mishig25, GGUF v3)**

##### File structure

A GGUF file consists of a **structured binary layout**:

- begins with a **magic number** and **version field** to identify the file type
- followed by a section containing **quantized tensor data** stored with byte offsets for efficient access
- a **metadata section** describes the model's architecture, quantization type, and token mappings
- a **tensor information block** defines the data type, shape, and memory locations for each tensor stored in the file

This **single-file design** is particularly beneficial in Kubernetes environments, where **consistent, self-contained artifacts simplify orchestration and scaling**.

GGUF represents a leap forward for **deploying LLMs efficiently**, especially on hardware that lacks high-end GPUs. Its focus on **quantization, self-contained design, and backward compatibility** addresses many pain points of earlier formats.

#### Current State and Gaps in Model Portability

Model portability is still **immature** for LLMs.

While **ONNX** stands out as a self-contained format for general machine learning models, and **GGUF** offers a specialized, self-contained solution for LLMs, both formats reveal important gaps in model portability:

- **ONNX** provides a structured way to package models but lacks critical components like tokenizers for LLMs
- **GGUF** includes basic tokenizer metadata but remains **tightly coupled to specific runtimes** like `llama.cpp`

##### ONNX

- **ONNX** is strong for general ML portability because it provides a structured model format
- But for LLMs, it is often **not fully self-contained** because important artifacts like **tokenizers** may remain outside the model format

##### GGUF

- **GGUF** is a more specialized format for LLMs and is relatively self-contained
- But it is also more tightly coupled to certain runtimes, especially **`llama.cpp`**

##### Safetensors

- **Safetensors** is increasingly important for production deployments
- It is commonly used in a **multifile layout**, which works well with **OCI artifacts** because components can be distributed as separate layers for:
  - **Caching**
  - **Parallel downloads**
  - **Flexibility**

##### Core takeaway

There is still **no universal model packaging standard for LLMs** equivalent to what OCI did for containers.

The field is evolving too quickly:

- New architectures appear often
- Runtime optimizations change fast
- Serving requirements vary widely

True standardization, much like OCI's success with containers, will require the convergence of both **runtime capabilities** and **model representation standards** — a milestone that is still some distance away.

##### What is practical today

For now, **GGUF** and **Safetensors** are often the most practical formats depending on the serving stack and deployment goal:

- **GGUF** dominates the `llama.cpp` ecosystem
- **Safetensors** is increasingly adopted for production deployments — its **multifile structure works well with OCI artifacts**, where model components can be distributed as separate layers for **efficient caching and parallel downloads**

##### Important mental model

At the end of the day, an LLM is **a collection of files**.

Those files may be:

- Self-contained
- Split across multiple artifacts
- Bound to particular runtimes

This is why **discovery, indexing, and management** matter so much in Kubernetes environments — and that is precisely the role of a **model registry**, covered next.

##### Encode this

- **ONNX = useful, but incomplete for many LLM workflows (no tokenizer)**
- **GGUF = self-contained, but runtime-coupled (`llama.cpp` ecosystem)**
- **Safetensors = production-friendly and OCI-compatible (default on Hugging Face)**
- **True portability standardization is still not finished — no Docker-for-models yet**

##### Recall prompt

*Why is OCI-level standardization for models harder than OCI standardization for containers?*

[Back to Contents](#contents)

### Model Registry

A **model registry** is a central system for **managing models and their metadata** across the ML lifecycle.

It acts as both:

- A **discovery mechanism**
- A **collaboration platform**

#### What a model registry does

It helps teams:

- Track model versions
- Store metadata
- Manage governance
- Promote models through lifecycle stages
- Support deployment readiness

A model registry stands at the **intersection of the responsibilities of data scientists and MLOps engineers**:

- **For data scientists**, it supports creating and tracking changes during model experimentation, verifying performance and metric tracking, packaging artifacts for reproducibility, and releasing validated models to production
- **For MLOps engineers**, the model registry facilitates deploying approved models with associated metadata while also supporting ongoing monitoring of deployed models for performance, drift, and necessary retraining — though this level of observability is considered an **advanced feature beyond the core functionality** of a model registry

#### Important operational detail

Most organizations run model registries as **internal services**, often inside the cluster. They usually **do not store the actual model weights directly**.

Instead, they typically store:

- **Metadata**
- **References**
- **Version records**
- **Governance information**

The actual model artifacts often live in:

- **S3 buckets**
- Other **object stores**

Organizations **don't expose these registries outside the cluster**. The registries primarily manage model metadata rather than storing the actual model weights or artifacts.

#### Why this separation matters

Keeping metadata separate from large model files improves:

- **Flexibility**
- **Scalability**
- **Operational simplicity**

By providing a **structured and secure interface** for managing models and their metadata, model registries become a **critical tool for operationalizing machine learning at scale**, especially in dynamic environments like Kubernetes.

#### Shared value across roles

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

#### Core model registry capabilities

The following list outlines the **core features** that define a model registry, providing essential capabilities for both **public and local** use cases.

##### Metadata management

Stores information about:

- **Accuracy**
- **Dataset lineage**
- **Performance benchmarks**
- Other critical training context

##### Model discovery and search

Search and retrieve models based on metadata such as:

- **Architecture**
- **Hyperparameters**
- **Training datasets**
- **Performance metrics**

Supports filtering with **range queries** (e.g., `accuracy > 0.95`).

##### Version control

Tracks **multiple versions** of both:

- **Models** — enables comparison of different model iterations and rollback if necessary
- **Datasets** — ensures **reproducibility** by tracking which data version was used for training and evaluation

This is essential for **reproducibility** and **rollback**.

##### Lifecycle management

Manage model stages such as:

- **Experimentation**
- **Staging**
- **Production**
- **Retirement**

This feature is especially critical as part of **continuous development workflows**.

##### Access control

Provide **fine-grained permissions** for model visibility and usage, ensuring **secure collaboration across teams**.

##### Auditing and compliance

Maintain a record of:

- model **usage**
- **approvals**
- **changes**

…to ensure regulatory compliance and reproducibility.

##### Data pipeline integration

Integrate into CI/CD workflows like:

- **Validation**
- **Artifact packaging**
- **Production rollout**

#### Related ML concepts

> **MODEL EXPERIMENTATION AND FEATURE STORES**
>
> **Model experimentation** refers to the **iterative process of training multiple model variations** with different hyperparameters (settings like learning rate or batch size) to find the best-performing configuration.
>
> - each training run produces metrics like **accuracy** or **loss**
> - typically runs as **GPU-intensive training jobs** on Kubernetes
> - **experiment tracking systems** log parameters and metrics from these runs
> - **MLflow** (covered later) provides experiment tracking as part of its broader toolset
>
> **Features** in machine learning are **input variables** that models use to make predictions — for example, *"number of transactions in the last hour"* or *"average amount over 30 days"* in a fraud detection system.
>
> A **feature store** manages the computation and serving of these features **consistently across training and inference**, preventing **training-serving skew**:
>
> - feature computation often runs as **data pipelines**
> - for generative AI workloads, features are **less central** than in traditional ML, as LLMs work primarily with **text and embeddings** rather than structured features
> - **[Feast](https://feast.dev/)** is a leading open source feature store that manages both traditional ML features and **text embeddings** for generative AI applications like **retrieval-augmented generation (RAG)**
>
> Both concepts highlight the **collaborative ML workflow**: data scientists experiment and iterate, while platform teams provide the Kubernetes infrastructure (GPU nodes, persistent storage, batch scheduling) that makes this work scalable.
>
> **The model registry serves as the handoff point**, storing metadata from successful experiments ready for production deployment.

##### Model experimentation

This is the iterative process of training many model variants with different:

- **Hyperparameters**
- **Datasets**
- **Configurations**

The goal is to **identify the best-performing version**.

##### Feature stores

A **feature store** manages features consistently across training and inference to avoid **training-serving skew**.

This matters more in **traditional ML** than in many LLM workloads, though **embeddings** and **retrieval systems** still make it relevant in generative AI systems.

#### Key bridge concept

**The model registry is the handoff point between experimentation and production.**

That is one of the highest-value ideas to remember.

#### Encode this

- **Registry stores metadata, not usually the full model weights**
- **It bridges experiment workflows and production workflows**
- **It supports versioning, governance, search, and lifecycle control**

#### Recall prompt

*Why is the model registry considered a handoff point between data science and MLOps?*

[Back to Contents](#contents)

To provide a clearer understanding of how these features are implemented in real-world tools, the following sub-subsections examine **four prominent model registries**: **Hugging Face Model Hub**, **MLflow Model Registry**, **Kubeflow Model Registry**, and **OCI Registries**.

#### Hugging Face Model Hub

The **[Hugging Face Model Hub](https://huggingface.co/models)** is the **canonical public platform** for discovering and sharing open source machine learning models, especially **LLMs**.

As of early 2026, it hosts **over two million models** in general and **more than 310,000 LLMs** specifically, all publicly available.

<u>Main idea:</u> Hugging Face plays a role for **open ML models** that is similar to what **GitHub** plays for **open source code**.

##### Why it matters

- It is the **main discovery layer** for open models
- It standardizes how models are documented
- It supports both **manual exploration** and **API-driven access**
- It is often the **first source** people use before internalizing models into production systems

##### Model Cards

Each model entry in the catalog is accompanied by a **Model Card**.

A **Model Card** provides a standardized summary of a machine learning model's key characteristics:

- **Intended use cases**
- **Training datasets**
- **Evaluation metrics**
- **Limitations and risks**
- **Licensing information**

This is important because **model adoption is not just about weights**; it is also about understanding **fitness**, **constraints**, and **governance**.

It often contains links to the datasets used for training, evaluation metrics, and licensing information.

![Hugging Face Model Card for Llama 3.1](<assets/Hugging Face Model Card for Llama 3.1.png>)

**Figure 2-5. Hugging Face Model Card for Llama 3.1 (source: Llama 3.1)**

##### Inference widget

Users can also try out models interactively using the built-in **inference widget**, which enables **quick testing** of the model directly from the web interface without requiring local setup.

This helps with:

- **Quick manual validation**
- **Basic behavioral testing**
- **Fast model comparison** before local deployment

##### API access

In addition to the web interface, Hugging Face also offers a **REST API** for programmatic access to its repository:

- **Querying models**
- **Retrieving metadata**
- **Discovering versions** (latest version of a model)
- **Filtering models programmatically** (filtering models based on specific criteria)

This is useful in automation pipelines, even if the Hub itself is not the final production registry.

##### Limitation for production

While the Hugging Face Hub is **perfect for public model sharing and manual discovery**, it has limitations for production use:

- It is a **public registry** — not suitable for organizations that need to keep **proprietary models private**
- It may also become limiting in **fully automated workflows** where model versions need to be programmatically tracked and managed
- It is not enough by itself for **full lifecycle traceability**
- External availability and access control may not meet production requirements

For such scenarios, a **dedicated internal model registry** becomes essential to ensure **version control, traceability, privacy**, and tighter integration into production pipelines.

##### Best operational takeaway

Use Hugging Face as:

- A **public source of truth** for open models
- A **discovery and evaluation layer**
- A **source repository** that you may later mirror, package, or import into internal systems

Do not confuse that with an **internal production-grade registry strategy**.

##### Encode this

- **Hugging Face Hub = public discovery and sharing platform**
- **Model Card = operational and governance context around a model**
- **Useful for exploration, but not sufficient by itself for private production model management**

##### Recall prompt

*Why is Hugging Face ideal for public model discovery but insufficient as the only production registry for many organizations?*

[Back to Contents](#contents)

#### MLflow Model Registry

**[MLflow](https://mlflow.org/)** is a **Linux Foundation project** for managing the machine learning lifecycle, including:

- **Experiment tracking**
- **Model packaging**
- **Model registry**

It was created by **Databricks in 2018** to address the challenges of managing machine learning experiments and model artifacts consistently across teams and environments. Since its release as an open source project, MLflow has become widely adopted in the **data science community** for its **simplicity and integration capabilities**.

##### Core concept: the Tracking Server

The central component in MLflow is the **Tracking Server**, which acts as the main hub for managing and storing all experiment metadata, metrics, and model artifacts.

It stores and exposes:

- **Experiment metadata**
- **Metrics**
- **Parameters**
- **Runs**
- **Model artifacts**
- **Registry entries**

This makes MLflow especially strong on the **data science side** of the lifecycle.

A **rich set of visualizations** allows you to follow the change of performance data and different hyperparameters.

##### Why practitioners like MLflow

- **Easy to install**
- **Easy to use locally**
- **Strong experiment tracking UX**
- **Good for comparing runs** and hyperparameters
- **Supports metadata-rich model registration**

##### Where model artifacts live

In simple setups, model artifacts can live on the **local filesystem**.

In production-oriented setups, MLflow can store artifacts in:

- **AWS S3**
- Other object stores
- External artifact locations
- References to external sources such as the **Hugging Face Hub**

The registry stores **artifact URIs**, not just display names. MLflow manages references to these storage locations through **artifact URIs** stored in the registry's metadata.

##### The MLflow Model Registry UI

The MLflow Model Registry is a part of this Tracking Server, providing a **centralized repository for versioning, tracking, and managing** machine learning models. It allows data scientists to register models with **rich metadata**, including version history and performance metrics.

![MLflow Model Registry UI](<assets/MLflow Model Registry UI.png>)

**Figure 2-6. MLflow Model Registry UI**

##### Example 2-2. Programmatically logging and registering models with MLflow

Most data scientists interact with the MLflow Model Registry **programmatically**:

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

What to notice:

- **`mlflow.set_tracking_uri(...)`** — sets the tracking server URI for logging
- **`mlflow.set_experiment(...)`** — creates a new MLflow experiment
- **`params`** — model hyperparameters
- **`mlflow.log_params(params)`** — logs those hyperparameters
- **`mlflow.sklearn.log_model(...)`** — logs the model itself at the tracking server

##### Example 2-3. Searching for and listing models via the MLflow REST API

For MLOps engineers, MLflow provides a **REST API** that you can leverage for **model discovery**:

```bash
$ curl http://localhost:8000/api/2.0/mlflow/registered-models/search
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

What to notice:

- **`curl http://localhost:8000/...`** — accessing an MLflow server running on the local machine
- **`"version": "4"`** — models in the registry are **versioned**
- **`source`** — URI reference to the model artifacts using MLflow's `mlflow-artifacts://` scheme. In this local setup, artifacts are stored on the filesystem, but the scheme supports **external storage like S3 or GCS**

##### Example 2-4. Creating a self-contained OCI container image with MLflow and Podman

MLflow provides CLI tools that interact with the Model Server. An interesting option here is to create a **self-contained OCI container image** that you can push to an OCI Registry for later usage in a Kubernetes cluster:

```bash
$ mlflow models generate-dockerfile \
  -m mlflow-artifacts:/84948067/f0dd25483e/artifacts/my_model
... INFO mlflow.models.cli: Generating Dockerfile for model mlflow-artifacts:
    .../artifacts/my_model
... INFO mlflow.models.flavor_backend_registry: Selected backend
    for flavor 'python_function'
... INFO mlflow.models.cli: Generated Dockerfile in directory mlflow-dockerfile

$ cd mlflow-dockerfile
$ podman build -t my_model .
STEP 1/12: FROM python:3.13.1-slim
STEP 2/12: RUN apt-get -y update && apt-get install -y --no-install-recommends nginx
....
Successfully tagged localhost/my_model:latest
a828556afe0d53d4728d872aa51fe07eaa1d4ef4faedb5a788bac9a7a7651e73
```

What to notice:

- **`mlflow models generate-dockerfile`** — uses the `mlflow` CLI to generate a Dockerfile that describes how to build an image with MLflow and the model data included
- **`podman build -t my_model .`** — uses `podman` to create an OCI image named `my_model`. Alternatively, **Docker** can be used for building the image

However, this feature is **not optimized for large download volumes** that need to be stored locally, so it is **not very well suited for LLMs**.

> **NOTE**
>
> MLflow also provides an **`mlflow models build-docker`** command that combines both steps into a single operation, directly creating the Docker image without generating a separate Dockerfile.
>
> The **`generate-dockerfile`** approach shown here offers **more flexibility for customization** (e.g., modifying the base image or adding post-build steps) and works seamlessly with **Podman or Docker**.

##### MLflow on Kubernetes

While MLflow was **not initially built with Kubernetes in mind**, the platform can be deployed effectively on Kubernetes. The standard approach is deploying it as a **web service** using tools like **Helm charts**, where a **PostgreSQL** database often serves as the backend for storing metadata.

However:

- It does **not** introduce native Kubernetes **CRDs**
- It is **not deeply Kubernetes-native**
- Scaling and serving automation usually require extra integration work

##### MLflow and LLMs

MLflow has significantly improved its **LLM support starting with the 3.0 release**, with capabilities such as:

- **Memory-efficient logging** through the Transformers flavor that avoids loading large models into memory during artifact storage
- **Prompt Registry** for versioning prompts
- **AI gateway** for unified LLM provider access
- Native **GenAI evaluation** capabilities
- Enhanced **tracing for LLM applications**
- **Reference-based logging** that stores Hugging Face Hub references instead of full model weights, substantially reducing storage requirements during development

For **production deployments**, however, full model weights typically still need to be **downloaded and stored locally** to ensure availability and performance.

That said, these approaches can create challenges in production environments, such as:

- the risk of **losing access to external repositories**
- **insufficient caching mechanisms** for repeated large model retrievals

MLflow's artifact storage and model handling techniques, though improving, may still require **complementary infrastructure** for LLM management at scale. For example, downloading large models repeatedly from a registry can become inefficient, and MLflow's current artifact storage approach is **not optimized for such high-volume data handling**.

##### Best operational takeaway

**MLflow is strongest as a data science lifecycle platform, not as the final answer to large-scale Kubernetes-native LLM operations.**

Its biggest advantage is that it is **very accessible** and can be easily installed on local machines.

For more **Kubernetes-native solutions**, alternatives like **Kubeflow** extend the concept of a model registry with **deeper Kubernetes integration** and additional observability features.

##### Encode this

- **MLflow = experiment tracking first, registry second**
- **Tracking Server is the central hub**
- **Great for DS workflows, less native to Kubernetes operations**
- **LLM support is improving (3.0+), but large-model production usually needs more infrastructure**

##### Recall prompt

*Why is MLflow highly effective for experimentation but often incomplete by itself for large-scale LLM production on Kubernetes?*

[Back to Contents](#contents)

#### Kubeflow Model Registry

**[Kubeflow](https://www.kubeflow.org/)** is a **Kubernetes-native ML platform** that aims to support the full ML lifecycle, including model training, serving, and model registry management.

It was initially developed by **Google** and is now an open source project under **CNCF**, consisting of these loosely connected components.

##### Major Kubeflow components

- **Kubeflow Dashboard**  
  A [central dashboard](https://www.kubeflow.org/docs/components/central-dash/overview/) and hub that connects the authenticated web interfaces of Kubeflow and other ecosystem components.

- **Kubeflow Notebooks**  
  A component for running [web-based development environments](https://www.kubeflow.org/docs/components/notebooks/) like Jupyter Notebooks inside your Kubernetes cluster by running them in pods. No local installation is needed.

- **Kubeflow Pipelines**  
  [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/) (KFP) is a platform for building and deploying portable and scalable machine learning workflows using Kubernetes.

- **Kubeflow Trainer**  
  [Kubeflow Trainer](https://www.kubeflow.org/docs/components/trainer/) is a unified interface for model training and fine-tuning on Kubernetes. It runs scalable and distributed training jobs for popular frameworks like PyTorch or TensorFlow.

- **Kubeflow Katib**  
  [Katib](https://www.kubeflow.org/docs/components/katib/) is a Kubernetes-native project for automated machine learning (**AutoML**) with support for **hyperparameter tuning**, **early stopping**, and **neural architecture search**.

- **Model serving (KServe)**  
  **KServe** (previously **KFServing**) solves production model serving on Kubernetes. It started in Kubeflow but has been moved to a **separate CNCF project**. We cover KServe in detail in [KServe](#kserve).

- **Model Registry**  
  An **index and catalog** for ML models. The registry is the **central hub** within the Kubeflow ecosystem, and the rest of this section focuses on it.

At its core, Kubeflow takes advantage of **Kubernetes principles**, with all tasks, including model registration and training, **defined as containerized workloads**.

![Kubeflow architecture and how it interacts with its Model Registry](<assets/Kubeflow architecture and how it interacts with its Model Registry.png>)

**Figure 2-7. Kubeflow architecture and how it interacts with its Model Registry**

##### Why Kubeflow is different from MLflow

Unlike MLflow, which is a more flexible experiment tracking and model management tool, **Kubeflow offers deeper Kubernetes integration** through:

- **CustomResourceDefinitions (CRDs)**
- **Manifests**
- **Native controllers** for each ML lifecycle component
- Native workflow patterns built around cluster operations

This makes Kubeflow more aligned with **platform engineering on Kubernetes** than tools that primarily began as standalone tracking systems.

##### What the Kubeflow Model Registry does

The **Kubeflow Model Registry** serves as a **central repository** for managing machine learning models, their versions, and related metadata. It substantially simplifies the **transition from experimentation to production deployments**.

It is the central catalog for:

- **Models**
- **Versions**
- **Metadata**
- **Lineage-relevant details**

Its purpose is to simplify the move from **experimentation** to **production deployment** inside a Kubernetes-centric ecosystem.

##### Metadata storage model

At its core, the registry uses a **flexible entity-relationship model** for metadata storage in a backend relational database (**MySQL**). This model is inspired by **Google's ML Metadata project** and provides a **structured, scalable approach** to storing:

- **Model lineage**
- **Metrics**
- **Parameters**

The Kubeflow Model Registry can **standardize metadata**, enable **version control**, and offer **interoperability across Kubeflow components**. This allows for robust tracking of model versions and the **reuse of metadata for deployment or pipeline triggers**.

##### Operational requirement

The registry relies on **external dependencies** such as:

- **MySQL** for metadata storage
- A **persistent volume** required for durability

This needs to be taken into account when operating the registry in production setups. So while it is Kubernetes-native, it is still not "free"; it requires careful production operation.

It exposes **REST APIs** and a **Python SDK** for interaction.

##### Example 2-5. Register a model at the Kubeflow Model Registry

You can interact with the registry through a Python SDK. The following example shows how you can do this from within a Python program or a Jupyter Notebook:

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

What to notice:

- **`ModelRegistry(server_address=..., ...)`** — creates a proxy to the Model Registry running in the cluster. This code must run **within a pod in the cluster** to access the cluster-internal service address (`.svc.cluster.local`)
- **`registry.register_model(...)`** — registers a model with metadata and a reference to the **location of the model data** (in this case, Google Cloud Storage)

##### Access pattern

Because the service address is **cluster-internal**, this kind of code usually runs **inside the cluster**, for example:

- In a **notebook pod**
- In a **pipeline step**
- In an **application pod**

##### Example 2-6. Query the cluster-internal Model Registry with curl from a pod

When a model is registered at the registry, you can easily access it via a Python library call. You can also access the model via a **REST API call directly** to the service:

```bash
kubectl run -it --rm curl --image=curl --restart=Never -- \
  http://model-registry-service.kubeflow.svc.cluster.local/...
```

This runs a `curl` command inside a **temporary pod** to query the **cluster-internal Model Registry service**.

##### Example 2-7. `InferenceService` accessing model data from the Kubeflow registry

You can also access the Kubeflow Model Registry with a **KServe `InferenceService`** in order to initialize the `InferenceService` with the model data that the registry points to:

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

What to notice:

- **`storageUri: "model-registry://iris/v1"`** — reference to the **model ID and version**. The actual storage URI is retrieved from the Model Registry metadata, providing an **extra layer of indirection** that allows changing storage locations without updating the `InferenceService`
- **`modelFormat: name: "sklearn"`** — format that specifies the runtime to use

This matters because the **`InferenceService`** can reference the model through the registry, while the actual underlying storage location can change later **without rewriting the serving manifest**.

##### Best operational takeaway

**Kubeflow Model Registry is a stronger fit when you want the registry to participate as part of a Kubernetes-native ML platform rather than remain a mostly standalone tracking system.**

##### Encode this

- **Kubeflow = full Kubernetes-native ML platform**
- **Model Registry is central inside that ecosystem**
- **Uses structured metadata with deeper cluster integration**
- **Works naturally with KServe and other Kubeflow components**

##### Recall prompt

*What makes Kubeflow Model Registry more Kubernetes-native than MLflow Model Registry?*

[Back to Contents](#contents)

#### OCI Registry

An **OCI (Open Container Initiative) Registry** is a **standard mechanism for storing and distributing container images**, commonly used in Kubernetes environments.

Familiar services like **Docker Hub** and **Quay.io** have made it easy for Kubernetes users to store and manage images without running a registry themselves. Some Kubernetes distributions, such as **Red Hat OpenShift**, even include a **built-in OCI Registry**.

Examples include:

- **Docker Hub**
- **Quay.io**
- Built-in registries in some Kubernetes distributions such as **OpenShift**

> **WHAT IS OCI?**
>
> The **Open Container Initiative (OCI)** standardizes how containerized applications and artifacts are managed.
>
> Founded in **2015 by Docker and others** under the **Linux Foundation**, OCI ensures **interoperability** and **vendor neutrality** in container technologies. It evolved from Docker's proprietary format to **avoid lock-in**, becoming an **open, extensible ecosystem**.
>
> While OCI began with container images, it now supports **diverse artifacts** like **Helm charts** and **generative AI models** through its **OCI artifacts specification**. This makes registries highly versatile for modern workloads.
>
> See [Modelcars](#modelcars) for how to use OCI images with model data via modelcars, and [OCI Image Volume Mounts](#oci-image-volume-mounts) for native OCI image volume mounts in Kubernetes.

##### Why OCI registries matter for GenAI

OCI registries are increasingly useful for **model distribution**, not just application containers.

That is possible because OCI evolved beyond classic container images into a broader artifact model.

##### What OCI means here

The **Open Container Initiative (OCI)** standardizes how containerized applications and related artifacts are packaged, stored, and exchanged.

OCI began with images but now also supports **OCI artifacts**, which allows registries to store more than runnable applications.

##### Why this is important for LLMs

An OCI Registry can store **more than just container images**. With the introduction of **OCI 1.1**, the specification expanded to support **OCI artifacts**, a **generalization of the original image format**. OCI artifacts let you store **arbitrary data types**, making an OCI Registry suitable for hosting **machine learning models, including LLMs**.

This means the registry can manage the **entire model file** rather than merely referencing external storage.

OCI Registries provide:

- **Versioning**
- **Immutability**
- **Persistence**
- Efficient **distribution mechanisms**

…that fit well with LLM hosting.

Compared to **MLflow and Kubeflow Registries**, which primarily store **model metadata and references** to external storage, an **OCI Registry focuses on storing the full model data itself**.

That makes it attractive for:

- Versioning
- Immutability
- Caching
- Distribution
- Kubernetes-native delivery workflows

##### Passive data images

LLM model images are examples of **"passive data images"**.

That means:

- You **don't execute them**
- Instead, you use them as **immutable packages** of model weights and configurations
- **Inference runtimes consume the files they contain**

You can easily create such a data image by cloning a **Hugging Face repository**, as shown next.

##### Example 2-8. Dockerfile for creating a container image that holds a model

```dockerfile
FROM alpine/git
RUN git lfs install \
 && git clone --depth 1 https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct /models
ENTRYPOINT sh
```

This Dockerfile can be used directly with **`podman`** or **`docker`** to create a **self-contained OCI image file** that has all the files needed to run the model.

For simplicity, this example adds the **entire model as a single layer**. In production, consider adding each model chunk as its **own layer** so that container runtimes can **download and cache them independently**.

##### Example 2-9. Build and push a model file with podman

```bash
$ podman build -f Dockerfile.model -t quay.io/rhuss/qwen2.5-0.5b-instruct .

STEP 1/3: FROM alpine/git
Trying to pull docker.io/alpine/git:latest...
Getting image source signatures
...
Writing manifest to image destination
STEP 2/3: RUN git lfs install
       && git clone https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
       && ln -s /git/Qwen2.5-0.5B-Instruct /models
Git LFS initialized.
Cloning into 'Qwen2.5-0.5B-Instruct'...
--> b437a8f78e49
STEP 3/3: ENTRYPOINT sh
COMMIT quay.io/rhuss/qwen2.5-0.5b-instruct
--> f680df7c975f
Successfully tagged quay.io/rhuss/qwen2.5-0.5b-instruct:latest
f680df7c975f6bfc806783574003c2b17872e9bf767944380f

$ podman push quay.io/rhuss/qwen2.5-0.5b-instruct:latest
```

What to notice:

- **`podman build -f Dockerfile.model ...`** — builds the model image. It will **clone the full repo** from the Hugging Face Hub and might take some time
- **`podman push ...`** — pushes to the registry where you can access it from the Kubernetes cluster

By leveraging **OCI Registries**, you can **store, version, and distribute** LLM models efficiently within Kubernetes-native infrastructure, integrating smoothly into **MLOps pipelines and declarative workflows**. Both **Modelcars** and **OCI Image Volume Mounts** allow KServe `InferenceServices` to **directly load model data from OCI images** — see [Modelcars](#modelcars) and [OCI Image Volume Mounts](#oci-image-volume-mounts).

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

#### OCI Images

An **OCI image** is a **standardized container image format** defined by the **Open Container Initiative**.

![OCI image consists of multiple filesystem layers](<assets/OCI image consists of multiple filesystem layers.png>)

**Figure 2-8. OCI image consists of multiple filesystem layers**

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

### Accessing Model Data in Kubernetes

Now that the notes have covered **model formats**, **registries**, and **artifact distribution**, the next operational question is:

**How does a model-serving workload actually access model data from inside a Kubernetes cluster?**

For GenAI serving on Kubernetes, this is not a secondary detail. It directly affects:

- **startup time**
- **storage efficiency**
- **replica scaling**
- **network usage**
- **inference latency**

#### KServe `storageUri` and Storage Initializers

KServe provides a clean reference model for understanding how Kubernetes-based serving systems access model data.

In the simplest case, the storage location is declared directly in an `InferenceService` using `storageUri`.

##### Example 2-10. `InferenceService` picking up model data from an S3 storage

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

- **`serviceAccountName: sa`** — identifies the Kubernetes `ServiceAccount` that is **associated with a `Secret`** holding the authentication credentials (or a cloud-native identity)
- the runtime here is **TensorFlow**
- **`storageUri: "s3://kserve-examples/mnist"`** — reference to an **S3 bucket** that holds the model data files

##### Why the URI scheme matters

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

##### Custom storage initializers

KServe lets you add **custom URI schemes** through a **`ClusterStorageContainer`** resource. In this resource you specify:

- a **reference to an image** holding the custom storage initializer
- a **list of URL schemas** that should trigger that storage initializer

URLs that match these schemas can then be used as `storageUri` specification in an `InferenceService`.

###### Example 2-11. `ClusterStorageContainer` adding `model-registry://` schema support

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

What to notice:

- **`image: kubeflow/model-registry-storage-initializer`** — reference to the **OCI image** for executing the initializer logic
- **`supportedUriFormats.prefix: model-registry://`** — registers the URL schema `model-registry` so that it can be used in an `InferenceService`

Kubernetes runs the storage initializer as an **init-container before the model runtimes start**; its only purpose is to **make the model data available** for the serving runtime.

##### Init containers and sidecars

These are important Kubernetes patterns to remember.

**Init containers**:

- run **before** the application container
- perform **one-time setup work**
- commonly prepare files in a shared volume

**Sidecars**:

- run **alongside** the main container
- provide supporting behavior such as logging, transformation, or coordination

For model serving, the storage initializer is usually an **init-container pattern**, not a sidecar pattern.

> **INIT CONTAINERS AND SIDECARS**
>
> **Init containers** and **sidecars** are powerful Kubernetes patterns for enhancing pod behavior.
>
> **Init containers** run **first** and perform **one-time setup tasks**, such as **populating a shared volume** with data needed by the main container.
>
> **Sidecars**, on the other hand, run **alongside** the main container, often providing auxiliary functionality like:
>
> - **logging**
> - **data processing**
> - **cross-container data sharing**
>
> Together, these patterns enable a **flexible and modular design for pods**. For more insights, check out the **init container** and **sidecar** patterns described in [*Kubernetes Patterns*](https://www.oreilly.com/library/view/kubernetes-patterns-2nd/9781098131678/).

##### Node-local sharing with `emptyDir`

A common KServe pattern is:

1. the storage initializer downloads or copies the model data
2. the data is written into an `emptyDir` volume
3. the main serving container mounts that same volume

This works because `emptyDir` is shared among containers in the same pod, including:

- init containers
- application containers

This gives the runtime a node-local copy of the model data for that pod.

#### Built-in KServe Storage Initializers

KServe supports several storage schemes out of the box.

**Table 2-2. KServe storage initializers**

| Schema | Description | Example |
| --- | --- | --- |
| `gs` | Download from Google Cloud Storage | `gs://kfserving-examples/models/sklearn/1.0/model` |
| `s3` | Download from an S3 bucket | `s3://kserve-examples/mnist` |
| `https` | Download model data with HTTP | `https://huggingface.co/meta-llama/Llama-3.2-3B` |
| `hdfs`, `webhdfs` | Access files from a Hadoop Distributed File System | `hdfs://path/to/model` |
| `pvc` | Copy or mount model data from a `PersistentVolumeClaim` | `pvc://${PVC_NAME}/export` |
| `oci` | Pull an OCI image with model data and access it directly via a modelcar — see [Modelcars](#modelcars) | `oci://quay.io/rhuss/kserving-example-sklearn:1.0` |
| `model-registry` | Access a model registered in the Kubeflow Model Registry | `model-registry://iris/v1` |
| `hf` | Download directly from the Hugging Face Hub | `hf://meta-llama/Llama-2-7b-chat-hf` |

##### Important operational distinction

Most of these schemes involve **preparing a node-local copy** of model data for each pod.

That is convenient for runtime access speed, but it can mean:

- repeated downloads
- repeated copies
- duplicated storage across replicas or nodes

This is one reason storage strategy matters so much for larger models.

#### Shared Storage with PersistentVolumes

When an `InferenceService` runs with multiple replicas, each replica needs access to the same model files.

There are three broad approaches:

- download copies from remote object storage
- package models into OCI artifacts
- mount shared storage through **PersistentVolumes**

PersistentVolumes provide a third model:

**store the model once, mount it from many pods**

##### Why PersistentVolumes matter

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

##### Example 2-12. `PersistentVolume` and `PersistentVolumeClaim` for model storage

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

What to notice:

- **`storage: 20Gi`** — defines the **total PV capacity**
- **`accessModes: ReadOnlyMany`** — allows multiple pods to mount the volume **read-only simultaneously**
- **`persistentVolumeReclaimPolicy: Retain`** — preserves the underlying model data if the PVC is deleted (**prevents accidental model deletion**); `Delete` removes both PV and underlying storage
- **`nfs:`** — NFS is used here as an example; other distributed filesystems supported by your cluster (such as **Ceph**, **AWS EFS**, **Azure Files**, or **Google Cloud Filestore**) can be configured similarly
- the PVC must request an **access mode compatible** with the PV

##### Why `ReadOnlyMany` is a strong fit

Model serving workloads typically need **read-only access** to model weights and configuration files. Inference engines **read the model parameters but don't modify them** during serving. This **read-only characteristic** makes the **`ReadOnlyMany`** access mode ideal for model storage PVs.

Configuring read-only access happens at **two levels**:

- **PV level** — the `ReadOnlyMany` access mode permits multiple pods to mount the volume simultaneously for reading
- **Pod level** — setting **`readOnly: true`** in the volume mount specification **reinforces this constraint** and provides additional benefits

Read-only mounts deliver **two performance advantages**:

- the operating system can apply **aggressive filesystem caching** since it knows the data won't change
- there's **no lock contention** between replicas attempting concurrent access, eliminating coordination overhead that would occur with read-write mounts

##### Example 2-13. `InferenceService` using `PersistentVolumeClaim` for model data

KServe supports PVs through the **`pvc://`** storage URI scheme, enabling direct integration with `PersistentVolumeClaims`:

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

What to notice:

- **`storageUri: pvc://llama-3-8b-pvc/`** — references the PVC **by name**. KServe mounts the PVC **directly into the model container at `/mnt/models`**

##### How PVC access differs from remote-download schemes

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

##### Trade-off: local speed versus shared efficiency

This is the core operational trade-off:

**Node-local access**

- faster runtime I/O
- avoids repeated network reads during inference
- but may require one copy per pod or per node

**Network-backed shared PV access**

- more storage-efficient
- simpler central updates
- but introduces network latency on reads

##### Scaling considerations

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

##### Practical takeaway

There is no universal best method for model data access.

The right choice depends on whether you optimize for:

- **startup speed**
- **runtime latency**
- **storage efficiency**
- **replica scale**
- **operational simplicity**

PVs are often a strong choice for shared model serving, but for very high-throughput or high-scale inference, **node-local approaches such as OCI-backed delivery** can be better.

Beyond `PersistentVolumes`, **OCI images** offer another approach for transferring and storing model data. The following sub-section explores how to **package models as OCI images** and access them efficiently from LLM runtimes.

#### OCI Image for Storing Model Data

In **2013**, **Docker** invented a clever **layered format** for storing container blueprints. The original and still prevalent usage for those images is to store, beside the kernel, all the binaries and files that make up a Linux operating system.

It is a **layered format** so that users can create **base images** that can be reused for different specialized images, for example, those containing the applications that will be run in a container. **Multiple containers share layers** when running if they refer to the same layers.

In addition to the **read-only layers** of an image, Docker uses a **union filesystem** that adds a **read-write layer on top** of the image layer stack, so that different container instances can still share the same underlying operating system files.

> One key benefit of this schema is that the read-only layers can be **cached individually**, which makes working with OCI images very efficient as **only changed layers** need to be distributed.

For the moment it is important that:

- you can **share layers**
- an OCI image is **built up hierarchically** — the layers are **stacked**

This stacking matches nicely for **model composition techniques** like **fine-tuning with Low-Rank Adaptation (LoRA) adapters** on top of foundational models. These foundational models, stored in base images, can be **shared when running on the cluster nodes**, which makes it very **efficient to run multiple specialized fine-tuned models**.

> See Figure 2-8 above for how OCI images are composed. At the end, all layers are packed into a **tar archive** stored in an OCI Registry.

Docker's success eventually led to a **standardization of the OCI image specification**. A full ecosystem of supporting tools has emerged over time:

- **registries** for hosting OCI images
- CLI tooling like **`skopeo`** or **`oras`** for inspecting and managing OCI images

Putting LLMs into OCI images **piggybacks on this existing landscape** and automatically benefits from the existing work that has been done in this area.

##### Example 2-14. Deployment with init-container copying model data to `emptyDir` volume

We can initialize the model data directly from an OCI container image. The following example introduces an `emptyDir` volume for sharing the model data between an **init-container** (which copies from the OCI image) and the **serving container**:

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: vllm
spec:
  replicas: 1
  template:
    spec:
      initContainers:
      - name: copy-model-data
        image: quay.io/rhuss/qwen2.5-0.5b-instruct:latest
        command:
        - "sh"
        - "-c"
        - "cp -a /models/. /mnt/models"
        volumeMounts:
        - name: models
          mountPath: /mnt/models
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args:
        - "--served-model-name",
        - "Qwen/Qwen2.5-0.5B-Instruct",
        - "--model",
          "/mnt/models"
        volumeMounts:
        - name: models
          mountPath: /mnt/models
      volumes:
        - name: models
          emptyDir: {}
```

What to notice:

- **`image: quay.io/rhuss/qwen2.5-0.5b-instruct:latest`** — OCI image holding the model data for Qwen 2.5 in the directory `/models` (built per Example 2-9)
- **`cp -a /models/. /mnt/models`** — copies the data from the image directory `/models` to the mounted `/mnt/models` directory that is backed by an `emptyDir` volume. **This might take some time depending on the size of the model to copy**
- the init-container **mounts the `emptyDir` volume** at `/mnt/models`
- **`--model /mnt/models`** — runs vLLM so that it accesses the model stored in `/mnt/models`
- the application container **mounts the shared directory** at `/mnt/models` to access the data copied by the init-container
- **`emptyDir: {}`** — declares an **empty node-local directory**

The technique above shows how model data is **typically initialized** for a deployed model, whether it's downloaded from an S3 bucket or extracted from an OCI image. KServe's storage initializers use this **same init-container approach** to copy model data from various sources.

Besides downloading the data from some source, this technique involves an **expensive copy step** that is performed **every time a runtime pod is started**.

The following sub-subsections demonstrate how this **copying over of gigabyte-sized amounts of data can be avoided** by directly accessing the data that is contained in an OCI model data image.

> **CNCF MODELPACK SPECIFICATION**
>
> The **[CNCF ModelPack specification](https://github.com/CloudNativeAI/model-spec)** is a **CNCF Sandbox project** that extends the OCI image specification for **packaging and distributing AI models**.
>
> It targets an expansion of the OCI standard to support AI model artifacts, including:
>
> - **model weights**
> - **metadata**
> - **configurations**
>
> The goal is to **standardize model storage and management**, ensuring better compatibility across different runtime environments. By leveraging OCI's extensible architecture, it aims to **simplify model deployment and sharing**.
>
> This initiative complements OCI's **image volume mount capabilities** described later in [Modelcars](#modelcars) and [OCI Image Volume Mounts](#oci-image-volume-mounts). The definition of **new annotation types** is also part of the specification.
>
> The specification was accepted into the **CNCF Sandbox in May 2025**, reflecting **strong community interest** and **strong industry support**. Its success will lead to a **more unified approach to operationalizing AI workloads** in cloud-native environments.

##### Modelcars

As we have seen in Example 2-14, you can easily access models stored in OCI images. However, this way of **copying all the model data into an intermediate storage** has some drawbacks.

**Direct access** to model data stored in an OCI image **without copying** would:

- **significantly speed up initialization**
- **reduce node space usage**
- an image needs to be **downloaded only once** but can be used **simultaneously by many pods**
- for LLM models that benefit from the **layered nature of OCI images** (like **LoRA fine-tuned** models), the overall storage space needed for specialized models that share a foundational model is reduced
- the image layers of the foundation model can be **shared among the specialized models**, reducing required disk space considerably

Kubernetes has **long lacked support** for this use case. Although the feature request was already recorded more than **10 years ago** in **[GitHub issue 831](https://github.com/kubernetes/kubernetes/issues/831)**, it was not considered for implementation for many years.

However, things have changed with the advent of LLMs and the desire to ship model data in OCI images. **Starting with Kubernetes 1.35**, you can use **image volume mounts directly in your pod specs**. However, it might take some time until image volume mounts move out of the experimental stage and are considered stable.

KServe uses a technique to achieve the same behavior for **older Kubernetes versions**: **modelcars**.

> You might consider jumping directly to [OCI Image Volume Mounts](#oci-image-volume-mounts) if you can already leverage OCI volume mounts. Modelcars can be considered a **temporary solution** you can use today.
>
> **OCI image volumes will support everything that modelcars provide**, but in a **much cleaner and more standardized way**. Use OCI image volumes whenever you can; rely on modelcars if this is not yet possible.

###### Example 2-15. `InferenceService` that uses model data from an OCI image

Unlike the vanilla Kubernetes deployment in Example 2-14, KServe's `InferenceService` resource **handles the modelcar setup automatically**. The **`oci://`** URL format is **KServe-specific syntax** for referencing OCI images containing model data, and the model data stored in the referenced image will be **directly accessed without prior copying** into a volume:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: "sklearn-iris-oci"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      # OCI Registry and repository of the image holding the model data
      storageUri: "oci://rhuss/kserving-example-sklearn:1.0"
```

Modelcars can **speed up the startup of a model runtime considerably**, especially when working with a large dataset.

> **NOTE — Deep-dive ahead**
>
> The rest of this Modelcars subsection is a **deep dive** into the technical architecture and implementation. You may wish to skip directly to [OCI Image Volume Mounts](#oci-image-volume-mounts). The pattern behind this technique proves useful in other scenarios when you have to deal with a large amount of data.

###### `shareProcessNamespace` trick

The Kubernetes pod specification supports a relatively unknown property called **`shareProcessNamespace`**.

- By default, containers that Kubernetes starts for a pod **cannot see each other**. Running `ps aux` inside a container shows **only the processes** started by that container. This is great for keeping containers isolated.
- Setting **`shareProcessNamespace: true`** allows the container to **"see" other processes** from other containers.
- You can also access the **filesystem from all containers** via the **`/proc` filesystem**.

###### Example 2-16. Accessing another container's root filesystem

```bash
$ cat spns.yaml

apiVersion: v1
kind: Pod
metadata:
  name: spns
spec:
  containers:
  - image: docker.io/httpd
    name: httpd
  - image: docker.io/busybox
    name: busybox
    command: ["sleep", "infinity"]
  shareProcessNamespace: false

$ kubectl apply -f spns.yaml

# Jump into the busybox container
$ kubectl exec -it spns -c busybox -- sh

$$ ps
PID   USER     TIME  COMMAND
    1 root      0:00 sleep infinity
    7 root      0:00 sh
   14 root      0:00 ps aux

$$ ls -d /proc [0-9]*
/proc/1  /proc/7

# Root filesystem of PID 1
$$ ls /proc/1/root/
bin    dev    etc    home   lib    lib64
proc   root   run    sys    tmp    usr    var

# Jump out of the container again
$$ exit

# Change `shareProcessNamespace` from false to true
$ sed  's/false/true/' spns.yml | kubectl apply --force -f -

# Jump into busybox container like before
$ kubectl exec -it spns -c busybox -- sh
$$ ps

PID   USER     TIME  COMMAND
    1 root      0:00 /pause
    7 root      0:00 httpd -DFOREGROUND
   15 www-data  0:00 httpd -DFOREGROUND
   16 www-data  0:00 httpd -DFOREGROUND
   17 www-data  0:00 httpd -DFOREGROUND
   99 root      0:00 sleep infinity
  126 root      0:00 sh
  132 root      0:00 ps

# Show data from the other container
$$ head -3 /proc/7/root/usr/local/apache2/conf/httpd.conf
#
# This is the main Apache HTTP server configuration file.  It contains the
# configuration directives that give the server its instructions.
```

What to notice:

- Simple pod with **two containers**: an Apache HTTP server and a busybox that sleeps forever to keep the container running. **No process namespace sharing** is enabled initially
- Only the **processes from the container's process namespace are visible**. The specified command has PID 1 when process namespace isolation is enabled
- **Root filesystem of process PID 1** (which is the same as `ls /`)
- When **process namespace sharing is enabled**, the PIDs from the other containers can be seen, too
- Via the `/proc` filesystem, a file specific to the **`httpd`-container** can be accessed from the **busybox container**

> **NOTE — Permissions caveat**
>
> You can access other processes' filesystems **only when Unix permissions allow**. Ideally, the processes from all containers use the **same UID**, so that cross-container filesystem access should not be an issue.
>
> However, depending on your cluster setup, additional mechanisms like **SELinux** might affect the ability to access another container's filesystem, even when using that UID or using UID 0 for the containers.

This technique to cross-share the containers' filesystems is **universal to Kubernetes** and can be used for any deployed workload, regardless of whether you have deployed the runtime yourself or via an add-on platform.

###### How KServe implements direct image mounting

Although it's not necessary to understand what happens behind the scenes, it's enlightening to see how KServe implements direct image mounting. The technique is **independent of KServe** and can also be used in other contexts where access to large datasets stored in OCI images is required.

![Modelcar components](<assets/Modelcar components.png>)

**Figure 2-9. Modelcar components**

The **serving runtime** and the **modelcar container** start in **parallel**. During startup:

- the modelcar creates a **symbolic link** from its filesystem to a **shared `emptyDir` volume** accessible by both containers
- the modelcar goes into an **infinite sleep** to keep the container alive

This linking operation is part of the modelcar's startup command and requires **minimal resources — less than 10 MB of memory** to maintain idle status.

> It's important to emphasize that **no data is copied over**; just a **symbolic link** is created to allow the serving runtime container to find the model data at a **fixed location** (e.g., `/mnt/models`).

###### Example 2-17. Pod with modelcar sidecar using `/proc` symlink for model data

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sklearn-iris-oci-predictor-00001-deployment-7fd9c7fc67-dzdsz
  namespace: default
spec:
  shareProcessNamespace: true
  containers:
  - name: kserve-container
    image: kserve/sklearnserver
    args:
    - --model_name=sklearn-iris-oci
    - --model_dir=/mnt/models
    volumeMounts:
    - mountPath: /mnt
      name: kserve-provision-location
  - name: modelcar
    image: rhuss/kserving-example-sklearn:1.0
    args:
    - sh
    - -c
    - ln -s /proc/$$$$/root/models /mnt/models && sleep infinity
    volumeMounts:
    - mountPath: /mnt
      name: kserve-provision-location
  volumes:
  - name: kserve-provision-location
    emptyDir: {}
```

What to notice:

- **`kserve-container`** with `image: kserve/sklearnserver` — serving runtime that executes on the model from the modelcar
- mounts the shared local directory on **`/mnt`** so that the model can be accessed from `/mnt/models`
- **`modelcar`** with `image: rhuss/kserving-example-sklearn:1.0` — modelcar image that holds the model data
- **`ln -s /proc/$$$$/root/models /mnt/models && sleep infinity`** — creates a symbolic link `/mnt/models` that **points into the modelcar's own root filesystem**, accessible via the `/proc` filesystem. In YAML, the `$$$$` gets replaced with `$$`, which is the special shell variable that holds the modelcar's shell process ID. After the link is created, the modelcar **sleeps indefinitely** to keep the container alive
- **`kserve-provision-location: emptyDir: {}`** — declaration of the shared `emptyDir` volume that is referenced in the container declaration for the serving runtime and the modelcar

###### Modelcar drawbacks

While the modelcar technique proved to be very valuable for optimizing the initialization of LLMs, it also has a handful of drawbacks:

**Startup order**

- Serving runtimes typically assume the model data is **already present** when they start up. However, with modelcars, the **modelcar container and runtime container start in parallel**. This can lead to the **runtime starting before the model is available**.

- Despite modelcar containers starting quickly, startup is slower when the modelcar image still needs to be pulled from an OCI Registry. This can be mitigated by using the **Kubernetes sidecar support** (available since **Kubernetes 1.28** as an optional feature), so that the runtime starts only when the modelcar is initialized.

- For setups where sidecars are not enabled, you can still **minimize the risk of a race condition** by **pre-pulling the modelcar image** in an init-container.

**Security**

- Enabling `shareProcessNamespace` **allows access to the process namespace and filesystems of all containers** defined for a pod. This is especially important to remember when other sidecars are included.

- A prominent example is the service mesh **Istio**, which uses sidecars to provide its functionality. Istio sidecars **assume they are fully isolated**, so they don't implement any precautions to hide sensitive information like the access configuration to their upstream Istio daemon.

- The lack of additional encryption of the local Istio configuration can be **easily exploited**. Understanding the consequences when using tools and platforms like **Istio** or **Knative** that perform sidecar injections is therefore **critical**.

**Nonuniform startup times**

- Depending on whether the model OCI image has already been loaded in the Kubernetes node's OCI runtime, the actual serving runtime can either start quickly or might **take several minutes** until a potentially large model OCI image is downloaded from a registry.

- To make the startup times more predictable — especially important in **scale-to-zero scenarios** — optimization techniques like **image prefetching** can be leveraged.

**Multiarchitecture support**

- Modelcars require an **active process** to keep the sidecar alive. This process is **specific to a certain CPU architecture**, so if you want to use modelcar images in a **multiarchitecture setup**, you need to create **copies of modelcars, one for each supported CPU architecture**.

- Those images contain the same ML model, **wasting resources**. However, tools like **BuildKit**, **umoci**, or **skopeo** can mitigate this duplication by creating **multiarchitecture images** with **manifest lists** that **share architecture-independent layers** (like model data) across platforms, while duplicating only the architecture-specific executable layers. This approach leverages **OCI's content-addressable storage** to deduplicate shared layers automatically when pushed to registries.

All of these drawbacks can be overcome by **real OCI image volume mounts**. Luckily, **Kubernetes 1.35 offers OCI image sources for volumes as a beta feature**. It will still take some time until this mount type is generally available; in the meantime, **modelcars are a good bridging technology** with a smooth upgrade path until OCI image volume mounts arrive for everyone.

##### OCI Image Volume Mounts

Starting with **Kubernetes 1.31**, pods can **directly mount OCI container images as volumes** without the need to copy model data first. This feature provides an **efficient way to access large model artifacts** stored in OCI images, reducing both **initialization time** and **storage overhead**.

The benefit of direct image mounts over the modelcar approach is that it **avoids the need for symbolic links or process namespace sharing**. Instead, model data can be **directly read from the image layers as a mounted volume**, benefiting from the underlying **OCI image layer cache**.

###### Example 2-18. Pod serving a locally mounted LLM via vLLM

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llm-server
spec:
  containers:
  - name: main
    image: vllm/vllm-openai:latest
    args:
      - "--served-model-name"
      - "meta-llama/Meta-Llama-3-8B"
      - "--model"
      - "/mnt/models"
    volumeMounts:
      - name: model-volume
        mountPath: /mnt/models
        subPath: models
  volumes:
  - name: model-volume
    image:
      reference: quay.io/meta-llama/meta-llama-3.2-8b
      pullPolicy: IfNotPresent
```

What to notice:

- **`image: vllm/vllm-openai:latest`** — runtime image for serving the model, vLLM in this case
- **`--model /mnt/models`** — specifies an absolute path to the mounted model as a startup argument for vLLM
- **`mountPath: /mnt/models`** — mounts the content of the OCI image into `/mnt/models`
- **`subPath: models`** — mounts only a **specific subdirectory** from the image rather than the entire image root. Using `models` as the `subPath` matches the **typical modelcar image structure** and provides **forward compatibility**
- **`image:`** — the volume type for an OCI image to mount. The usual pull semantics apply: if no `pullPolicy` is provided, always pull the image if the tag `latest` is specified. Otherwise, Kubernetes pulls only if the image is **not present at the node**
- **`pullPolicy: IfNotPresent`** — the pull policy can be also specified explicitly

###### subPath and forward compatibility

Image volumes support **`subPath`** and **`subPathExpr`** mounts, allowing you to mount **specific subdirectories** from an OCI image rather than the entire image root.

The `subPath` feature is particularly important for **forward compatibility** with modelcars. By:

- structuring your OCI images with model data in a **`/models` subdirectory**
- and using **`subPath: models`**

…you create images that work **seamlessly with both the modelcar approach and native OCI image volumes**. This enables a **smooth migration path** from modelcars to native image volumes **without rebuilding your model images**.

###### Current limitations

While this image volume mount feature simplifies large model deployments for both OCI images and OCI artifacts, it still has limitations as of early 2026:

- **Container runtime support** — CRI-O v1.33+ has full support; containerd requires v2.2.0+ for beta features (v2.1.0+ for basic support)
- **Feature gates** must be **explicitly enabled** (still disabled by default)
- The feature **doesn't support writeable layers**; volumes remain **read-only**
- Only **directory mounts** are supported; individual files cannot be mounted directly

The community is actively working on these limitations, with **signature validation**, **compressed layers**, and **read-write support** planned for future releases. This feature will eventually become the **preferred method for serving LLMs on Kubernetes**, replacing the modelcar approach as it matures. In the meantime, **modelcars are a reliable approach** for direct access to model data stored in an OCI image.

#### Encode this

- **`storageUri` is the control point for how KServe locates model data**
- **storage initializers are usually init containers that prepare model files before serving**
- **`emptyDir` gives pod-local shared storage between init containers and runtimes**
- **`pvc://` differs from remote-download schemes because it mounts shared storage directly**
- **model access design is a trade-off between local performance and shared efficiency**

#### Recall prompt

*Why might a team choose `pvc://` over `s3://`, and what performance trade-off does that decision introduce?*

[Back to Contents](#contents)

### Model Data Lessons Learned

This combined section explored the **three-layer challenge** of LLM data on Kubernetes: **storage formats**, **registries**, and **runtime access**.

**LLM data is uniquely large**

Models range from **~14 GB** (Mistral 7B) to **~800 GB** (Llama 4 Maverick), and the **sheer size dominates operational decisions** in a way that traditional application containers never do.

**Storage formats are still "mostly self-contained"**

- **Weight-only formats** (PyTorch `state_dict`, TensorFlow checkpoints, NumPy arrays) work for development but require the runtime to **already know the architecture**
- **Self-contained formats** (ONNX, Safetensors, GGUF/GGML, Hugging Face Transformers) bundle weights with metadata, but **all still depend on external components** (especially **tokenizers**)
- **Safetensors** is now the **default on Hugging Face**, **GGUF** dominates the `llama.cpp` / edge ecosystem, and **ONNX** is the best example of where the field could go for a fully self-contained LLM format

**Model registries split into "metadata-only" vs "artifact-storing"**

- **Hugging Face Model Hub** — public discovery, **Model Cards**, inference widget; not for proprietary models
- **MLflow** — strong for experiment tracking and DS workflows, less Kubernetes-native, LLM support improving in 3.0+
- **Kubeflow Model Registry** — Kubernetes-native, CRD-driven, integrates with KServe `model-registry://` URIs
- **OCI Registry** — unlike the metadata-only registries, OCI **stores the full model artifact**, making it a strong fit for **immutable, versioned, layered model delivery**

**Accessing model data is a trade-off, not a single answer**

Model data access strategies involve **fundamental trade-offs** among **storage efficiency**, **access performance**, and **operational complexity**.

**Table 2-3. Comparison of model data access strategies**

| Approach | Storage efficiency | Access speed | Startup time | Best for | Limitations |
| --- | --- | --- | --- | --- | --- |
| **Init Container Copy** | Low | Fast | Slow | Single replica per node, latency-sensitive inference | Wastes node storage, slow initial pod creation, repeated copying |
| **PersistentVolume** | Highest | Moderate | Fast | Multiple replicas with moderate scale, external model management | Network dependency, infrastructure overhead, struggles at hundreds of replicas |
| **Modelcar** | High | Fast | Moderate | Multiple models sharing base layers, efficient storage | Requires OCI packaging, process namespace sharing, security considerations |
| **OCI Volume Mount** | High | Fast | Moderate | Multiple models, native Kubernetes integration | Beta feature (K8s 1.35+), limited runtime support |

**Init container copying** delivers the **fastest inference performance** through **node-local I/O**, making it ideal for **latency-sensitive workloads**. However, this approach **wastes storage when running multiple replicas**, as each node maintains its own copy. Use this strategy for **single-replica or low-concurrency scenarios** where you can tolerate slow startup in exchange for peak inference performance.

**`PersistentVolumes`** provide the **highest storage efficiency** by storing models once and sharing them across all replicas. Storage efficiency comes at the cost of **network latency on every model file read**. PVs work well for **tens of replicas** but face challenges when scaling to hundreds due to **backend saturation and network contention**. Choose PVs when **storage costs matter more than peak inference performance**, or when data scientists manage models externally through distributed filesystems.

**OCI image-based approaches (modelcars and volume mounts)** offer a **middle ground**:

- **high storage efficiency** through layer sharing
- plus **fast local access**

As a **standardized format**, OCI enables seamless model distribution and discovery across registries.

- **Modelcars** provide immediate availability but require **process namespace sharing** with security considerations
- **OCI volume mounts** offer cleaner integration as a **native Kubernetes feature** but remain experimental as of Kubernetes 1.33

Both approaches **excel when running multiple fine-tuned models sharing the same base model**, as common layers are shared across all instances.

**Hybrid strategies for complex environments**

Consider hybrid strategies for complex environments:

- **Development environments** might use **`PersistentVolumes`** for easy model updates
- **Production deployments** use **OCI volumes** for performance and reliability
- Different **model tiers** might use different approaches: frequently accessed models in OCI images for speed, less-critical models sharing `PersistentVolumes` for cost efficiency

As **OCI volume mounts mature and gain widespread runtime support**, they will likely become the **preferred approach for most deployments**.

#### Encode this

- **Storage formats, registries, and access patterns are one connected problem, not three**
- **No format today is fully self-contained for LLMs — tokenizers and configs always come along**
- **Metadata registries (MLflow, Kubeflow) ≠ artifact registries (OCI)**
- **`storageUri` scheme is the single control point that decides download-vs-mount semantics**
- **Replica scale + model size + storage backend together set the operational ceiling**
- **Four access strategies: init-container copy / PV / modelcar / OCI volume mount — each with different trade-offs**

#### Recall prompt

*Given a 70 GB Safetensors model and 10 inference replicas, which combination of registry + access pattern would you choose for the lowest total startup cost, and what trade-off does it introduce?*

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

![AI Inference on Kubernetes](<assets/AI Inference on Kubernetes.png>)

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

## Model Observability

Kubernetes orchestrates container execution through a **declarative API**, using **controllers** and **reconciliation loops** to self-heal workloads in an eventually consistent way. This approach does **not** replace proper observability and monitoring; those capabilities allow rapid reaction when something cannot be solved automatically.

The same principle applies to LLMs, but with an important caveat:

**Monitoring a model server is not equivalent to monitoring traditional applications.**

LLMs differ significantly from traditional microservices, where workload is mainly driven by **number of requests** and **speed of query on data**. They are also different from traditional ML.

Throughout these notes, LLMs are usually treated as **operational black boxes**, focusing on deployment, scaling, and resource management without needing to understand their internal mechanics. For observability, that black-box stance is not enough:

- the metrics monitored (**Time To First Token**, **token throughput**, **KV cache utilization**) are directly tied to the LLM inference pipeline
- understanding **tokenization**, **embeddings**, **prefill** and **decode** phases, and **compute-bound** versus **memory-bound** workloads is required to interpret those metrics

For the rest of this section, basic familiarity with these concepts is assumed.

> **PREFILL AND DECODE — QUICK REFRESHER**
>
> The **prefill phase** is when the model processes the **input prompt** and builds the internal attention state, often called the **KV cache**. During this phase, the model reads all prompt tokens in parallel-ish chunks and prepares to predict the **first output token**.
>
> So **TTFT** (**Time To First Token**) mostly includes:
>
> 1. **receiving the request**,
> 2. **tokenizing / preparing the prompt**,
> 3. **running the prompt through the model during prefill**,
> 4. **sampling the first generated token**,
> 5. **returning that token to the user**.
>
> The **decode phase** starts after the first token is produced. The model then generates **one token at a time**, using the **KV cache from prefill** plus the newly generated tokens.
>
> So the rough timeline is:
>
> ```text
> User prompt
>    ↓
> Prefill: process prompt, build KV cache
>    ↓
> First output token  ← TTFT ends here
>    ↓
> Decode: generate token 2, token 3, token 4...
>    ↓
> End of generation
> ```
>
> A slightly more precise phrasing:
>
> > The **prefill phase** is the model's processing of the input context up to computing the **first next-token distribution**. The **decode phase** is the **autoregressive generation** of output tokens after that, usually one token per step.
>
> In short: **prefill = prompt processing before/for the first token**, and **decode = producing the rest of the completion token by token**.

### Observability Stack and Configuration

Existing Kubernetes observability tools and practices can be **reused or adapted** for LLM workloads.

Workload observability involves several aspects:

- **inspecting logs** to find errors
- **collecting metrics** for time-series analysis
- **correlating execution steps** via tracing
- **proxying traffic** as sidecars
- **injecting modules** directly into containers

This applies to application workloads, and most of the same applies to LLM deployments using KServe and vLLM.

#### Logs

Kubernetes has a defined **logging architecture** where both `stdout` and `stderr` are redirected to a `log-file.log` on the worker node where the container is running.

This makes logs easy to access via:

```bash
kubectl logs
```

But it does **not** provide long-term storage or indexing. That must be added with projects such as **[Grafana Loki](https://github.com/grafana/loki)**.

When deploying a model as an `InferenceService`, the KServe controller creates the Deployment with **multiple containers**:

- an `initContainer` named **`storage-initializer`** to load the model
- the **`kserve-controller`** container where the model server runs
- additional **sidecar containers** depending on the deployment mode (Knative or ModelMesh)

Log introspection and management for LLMs is **analogous to application workloads**. The vLLM startup sequence below illustrates the typical key log entries from initialization through receiving the first inference request.

##### Example 5-1. vLLM startup logs

```text
INFO [api_server.py:651] vLLM API server version ...
INFO [api_server.py:652] args: ...
INFO [api_server.py:199] Started engine process with PID ...
INFO [config.py:478] This model supports multiple tasks: ...
WARNING [arg_utils.py:1089] Chunked prefill is enabled ...
INFO [llm_engine.py:249] Initializing an LLM engine (...) with config: model=...
INFO [model_runner.py:1092] Starting to load model ...
INFO [weight_utils.py:243] Using model weights format ['*.safetensors']
...
Loading safetensors checkpoint shards: 100% Completed | 4/4 [00:04<00:00,  1.12s/it]
...
INFO [worker.py:241] the current vLLM instance can use total_gpu_memory ...
INFO [worker.py:241] model weights take 14.99GiB; ...
...
INFO [launcher.py:19] Available routes are:
INFO [launcher.py:27] Route: /openapi.json, Methods: HEAD, GET
...
INFO [launcher.py:27] Route: /v1/chat/completions, Methods: POST
...
INFO:     Started server process [39626]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO [logger.py:37] Received request cmpl-...: prompt: ...
INFO [engine.py:267] Added request cmpl-....
```

What to notice:

- vLLM logs the **version** and the **arguments** specified to start it
- a model may support **multiple tasks**: `generation` is the most common, but others include `classify` or `reward`
- the **configuration to load a model** is logged; this comes from the model's `config.json`
- after the model loads, vLLM logs **VRAM information**, including the space assigned to the **KV cache**
- logs include **all available endpoints**
- a log entry is produced **every time a new request is received**, including prompt and parameters; disable this with `--disable-log-requests`

#### Metrics

Kubernetes core does **not** include built-in support for metrics, but the de facto standard is **[Prometheus](https://prometheus.io/)** with the **[OpenMetrics](https://openmetrics.io/)** exposition format.

> **OpenMetrics** is a CNCF incubating project that standardized and extended the original Prometheus text format while maintaining backward compatibility.

Containers expose metrics via an endpoint, usually `/metrics`, using this format. The endpoint is pulled periodically by the collector component in charge of scraping them.

##### Example 5-2. Configure a service for monitoring

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service-deployment
spec:
  ...
---
apiVersion: v1
kind: Service
metadata:
  name: my-service
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/path: "/metrics"
    prometheus.io/port: "80"
  labels:
    app.kubernetes.io/part-of: my-application
spec:
  type: ClusterIP
  selector:
    app: my-service
  ports:
    ...
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-service-servicemonitor
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: my-application
  endpoints:
    - interval: 15s
```

What to notice:

- the **annotations on the Service** declare the location of the metrics endpoint
- the **`ServiceMonitor` API** enables monitoring
- a **selector** is required to match the Service to monitor
- the **scraping frequency** is configurable

The configuration to monitor a model is **very similar**. KServe defines a set of annotations to configure monitoring directly on `ServingRuntime` and `InferenceService` objects. Using these annotations, the KServe controller configures the Deployment correctly.

##### Example 5-3. Configure a model with monitoring

```yaml
apiVersion: serving.kserve.io/v1alpha1
kind: ServingRuntime
metadata:
  name: kserve-vllm
spec:
  annotations:
    prometheus.kserve.io/port: '8080'
    prometheus.kserve.io/path: "/metrics"
  ...
---
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: my-model
  annotations:
    serving.kserve.io/enable-prometheus-scraping: "true"
spec:
  ...
```

What to notice:

- the `prometheus.kserve.io/*` annotations are **KServe-specific** but equivalent to `prometheus.io/*`
- `serving.kserve.io/enable-prometheus-scraping: "true"` enables the injection of `prometheus.io/*` to the pod by KServe

Once metrics are exported and collected by Prometheus, they can be **queried** or **displayed in a Grafana dashboard**, exactly the same way as for traditional Kubernetes workloads.

> **TIP**
>
> KServe has different deployment modes. Monitoring works differently when **Knative mode** is used because **multiple containers** in the pod run alongside the model server.
>
> Prometheus configuration assumes a single endpoint to scrape, which means information from other containers can be missed. To address this, the KServe project has developed a **metric aggregator component** named **`qpext`** that scrapes metrics from all containers and exposes a **single aggregated metrics endpoint**.
>
> Enable this with the `serving.kserve.io/enable-metric-aggregation` annotation.
>
> This aggregation is **not necessary** in **Standard mode** because the deployment has a single container.

#### Tracing

Container logs give full visibility into what a component is doing, and aggregated metrics provide trends and time-series indicators. What is still missing: **the ability to trace the execution flow of a single request**.

The evolution of tracing best practices in Kubernetes mirrors metrics: it is not natively integrated, but the **[OpenTelemetry](https://opentelemetry.io/)** project has defined concepts and formats that have become the de facto standard.

The OpenTelemetry specification for tracing defines that every request has an **identifier** used to correlate the execution flow that can span multiple steps. This makes tracing very different from metrics:

- in real-world scenarios, **multiple components** are involved beyond the model server (firewalls, gateways acting as pre/post-processors)
- all of these components must implement the protocol to **propagate the identifier** and **produce tracing information**
- unlike metrics that are **pulled by a collector**, trace information is **pushed to the exporter** by the component

One of the most commonly used server implementations for tracing is **[Jaeger](https://www.jaegertracing.io/)**, which exposes the necessary endpoint to collect tracing data and provides graphical tools to display it.

vLLM uses the **[OpenTelemetry SDK](https://opentelemetry.io/docs/languages/sdk-configuration/)** to integrate tracing support; configuration is therefore simplified and analogous to other projects using the same approach.

##### Example 5-4. Configure vLLM for tracing

```yaml
apiVersion: serving.kserve.io/v1alpha1
kind: ServingRuntime
metadata:
  name: kserve-vllm
spec:
  containers:
    - name: kserve-container
      image: vllm/vllm-openai:latest
      args:
        - --model
        - /mnt/models/
        - --port
        - "8080"
        - --otlp-traces-endpoint
        - "$JAEGER_TRACE_ENDPOINT"
      env:
        - name: "OTEL_SERVICE_NAME"
          value: "vllm-server"
  ...
```

What to notice:

- `--otlp-traces-endpoint` enables OpenTelemetry tracing in vLLM and configures the exporter endpoint; it supports **gRPC** and **HTTP** along with many other configurations
- the OpenTelemetry SDK uses **environment variables** for its configuration; see the OpenTelemetry SDK website and [Python SDK documentation](https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html) for more details

> **PROMETHEUS, OPENMETRICS, AND OPENTELEMETRY**
>
> The **[Prometheus](https://prometheus.io/)** project is the most widely adopted solution for metrics, but the format was not initially formalized with a specification. Over time, **OpenMetrics** became the specification that extends the original Prometheus format while preserving near-full backward compatibility.
>
> The **[OpenTelemetry](https://opentelemetry.io/)** project is a collection of API definitions, SDKs, and tools covering all aspects of observability. It also proposes **[semantic conventions](https://opentelemetry.io/docs/specs/semconv/)** to standardize naming for metrics and trace entries.
>
> LLM observability (under the broader **[generative AI](https://github.com/open-telemetry/community/blob/main/projects/gen-ai.md)** OpenTelemetry subproject) is one of the active areas, and an **[experimental specification](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai)** already defines a core set of semantic conventions. The vLLM implementation for tracing is already based on this semantic convention work.
>
> This effort is analogous to the **[KServe Open Inference Protocol (OIP)](https://github.com/kserve/open-inference-protocol)**, which aims to unify the shape of model evaluation endpoints.

#### Encode this

- **Logs in Kubernetes are easy to read but require external tools like Loki for long-term storage**
- **vLLM startup logs reveal model load, VRAM use, KV cache size, and available endpoints**
- **Prometheus with OpenMetrics is the de facto metrics standard**
- **KServe-specific annotations configure scraping on `ServingRuntime` and `InferenceService` objects**
- **Knative deployment mode needs the `qpext` aggregator to expose a unified metrics endpoint**
- **OpenTelemetry is the tracing standard; vLLM ships with native integration**

#### Recall prompt

*Why does Knative mode in KServe require the `qpext` aggregator while Standard mode does not?*

[Back to Contents](#contents)

### Model Server Metrics

With the metrics stack installed, an LLM deployed using KServe, and vLLM properly configured, model server performance can be analyzed.

Traditional Kubernetes monitoring tracks **CPU usage**, **memory usage**, **throughput** (requests per second), and **latency** (time to process a request). The same approach applies to LLMs, but with important differences:

- LLM workload happens **mainly on the GPU**, so CPU usage is not a good representation of system usage
- the two main inference phases, **prefill** and **decode**, are very different: prefill is **compute-bound** and decode is **memory-bound**
- the concept of throughput and latency is different because **it is not possible to predict how long an answer will be**, so any metric that counts requests will not represent the actual model server workload

Because **tokens are the core unit of computation** for LLM generation, model server metrics are **token-based** rather than request-based.

#### Time To First Token

**Time To First Token (TTFT)** is the actual time a user waits before starting to receive the response.

- the **most important metric** for real-time use cases such as chatbots
- **less critical** for offline scenarios such as batch jobs

Properties:

- unit: **seconds**
- type: **histogram** (tracks distribution across configurable buckets)
- vLLM name: `vllm:time_to_first_token_seconds`
- OpenTelemetry semantic convention: `gen_ai.server.time_to_first_token`

TTFT represents the time necessary to compute the **prefill phase**.

#### Time Per Output Token or Inter-Token Latency

Tokens are produced one by one and are usually returned as a stream, so the second metric to look at is the time to produce each token **after the first**.

- TTFT = the actual time the user perceives as waiting time
- **Time Per Output Token (TPOT)** = the speed of the result as seen by the end user, also called **Inter-Token Latency (ITL)**

Properties:

- unit: **seconds**
- type: **histogram**
- vLLM name: `vllm:time_per_output_token_seconds`
- OpenTelemetry semantic convention: `gen_ai.server.time_per_output_token`

Practical reference point:

> On average, a human reads about **180 words per minute**, or roughly **3 words per second**. Since tokens approximate but do not exactly match words, producing **at least 4–5 tokens per second** ensures that humans can consume the output without perceived delay.

If TTFT maps to the **prefill phase**, this metric measures the duration of each **decoding iteration**.

#### Throughput

With tokens as the computational unit for LLMs, throughput is defined as the **number of tokens generated per second**.

However, requests can be very long (more than 100k tokens), so looking only at the number of generated tokens misses the time and cost to process the **initial request (prefill)**.

vLLM provides both individual and combined metrics:

- `vllm:prompt_tokens_total` — number of input tokens processed per second
- `vllm:generation_tokens_total` — number of output tokens produced per second
- `vllm:tokens_total` — combined total tokens processed per second

OpenTelemetry semantic conventions do **not** currently provide a recommendation for this metric.

Even with both metrics available, the **throughput of generated tokens** is generally enough as a valid indicator of system load. Because modern GPUs are very fast, the input processing finishes quickly (compute-bound), and the **decoding phase takes most of the time**.

<u>Important nuance:</u> throughput does **not directly relate** to the number of processed requests, because the system can be fully used to produce a single response, or vice versa.

#### Latency

**Latency** is the time, in seconds, necessary for the model to generate a **full response**.

This metric correlates with TTFT and TPOT but is also an important indicator of **total request processing time**, useful for spotting **trends** or **patterns**.

Properties:

- unit: **seconds**
- type: **histogram**
- vLLM name: `vllm:e2e_request_latency_seconds`
- OpenTelemetry semantic convention: `gen_ai.server.request.duration`

#### Request Queue Metrics

Every time a request is received by vLLM, **batching techniques** maximize throughput, but a request might **not be processed immediately** if the batch is full.

Queue-related metrics:

- `vllm:num_requests_waiting` — requests waiting to be processed
- `vllm:num_requests_running` — currently executing requests

vLLM exposes many additional metrics for KV cache usage and other execution aspects. See the **[Production Metrics](https://docs.vllm.ai/en/latest/usage/metrics/)** documentation for the full list.

##### Example 5-5. Create a Prometheus rule with vLLM metrics

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: my-llm-rule
spec:
  groups:
    - name: "vllm.latency.rule"
      rules:
        - alert: vLLMLatency
          expr: max_over_time(time_per_output_token_seconds}[5m]) >= 0.3
          labels:
            severity: critical
            app: my-model
          annotations:
            message: Latency of vLLM is too high.
            summary: Model "my-model" needs to keep latency < 0.3 second
            runbook_url: https://my.company/runbooks/vllm/modelslow
            description: The runtime is slowing down, check request queue
```

What to notice:

- the **`expr`** field configures the condition that fires the alert
- a **runbook URL** (documented procedure) can be linked to help on-call engineers troubleshoot the issue

#### SLI, SLO, and SLA

When defining alerts and monitoring strategies, the relationship between service-level metrics helps establish meaningful thresholds:

**Service-Level Indicator (SLI)**

A metric defined to monitor a particular service. It should be based on aspects that have **direct user impact**.

> Example for LLMs: **TPOT**, because it measures the time users must wait to receive each token after the first.

**Service-Level Objective (SLO)**

The **promise** made to users regarding a specific SLI.

> Example: keep TPOT below a specific threshold in **99.999%** of requests in a given window (such as monthly).

**Service-Level Agreement (SLA)**

The **contractual agreement** with users. It is related to defined SLOs but is more high-level, usually expressed in terms of **monthly availability** of a service.

> Breaking one or more SLOs can impact the SLA to the point that an agreement is no longer being met.

#### Encode this

- **Token-based metrics replace request-based observability for LLMs**
- **TTFT measures user-perceived wait time and maps to the prefill phase**
- **TPOT / ITL measures streaming speed and maps to each decoding iteration**
- **Throughput is best measured in tokens per second, not requests per second**
- **Request queue metrics reveal batching pressure**
- **SLI → SLO → SLA: indicator, promise, contractual agreement**

#### Recall prompt

*Why are token-based metrics more informative than request-per-second metrics for LLM workloads?*

[Back to Contents](#contents)

### GPU Usage Monitoring

System metrics measure overall throughput and the number of requests the cluster is processing, enabling alerts when the system is not meeting the expected SLA.

Resource usage for **CPU**, **memory**, and **network** can be monitored exactly as for a traditional Kubernetes workload, although networking may be more complex when using **secondary network interfaces** for high-performance interconnects like **RDMA** or **InfiniBand**.

**GPU usage requires additional consideration.**

Each hardware provider has its own implementation, but all follow a similar approach:

- a **management component** collects usage metrics from the GPU
- an **exporter component** exposes them via a `/metrics` endpoint compatible with Prometheus

#### Vendor implementations

**NVIDIA**

- **[Data Center GPU Manager (DCGM)](https://developer.nvidia.com/dcgm)** — suite of tools to manage GPUs in a cluster
- **[DCGM-exporter](https://github.com/NVIDIA/dcgm-exporter)** — Helm Chart to deploy the exporter to Kubernetes
- **[GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html)** — installs in the cluster to automatically provision and configure the metrics exporter

Metrics scraping is then configured as shown in Example 5-2.

**AMD**

- **[AMD Device Metrics Exporter](https://github.com/ROCm/device-metrics-exporter/)**
- **[AMD GPU Operator](https://instinct.docs.amd.com/projects/gpu-operator/en/release-v1.5.0/)**

**Intel**

- **[Prometheus Metric Exporter](https://docs.habana.ai/en/latest/Orchestration/Prometheus_Metric_Exporter.html)**

Almost every other vendor follows the same pattern: deploy the component per documentation and start collecting GPU metrics.

#### No common naming convention

No common naming convention has been adopted across vendors, but they all cover **low-level usage metrics** such as:

- **PCIe bandwidth**
- **graphic engine activity**

#### Encode this

- **GPU usage is essential because LLM workloads are GPU-dominant**
- **vendors provide their own exporter + operator stack**
- **NVIDIA = DCGM + DCGM-exporter + GPU Operator**
- **no shared naming convention means dashboards and alerts must be vendor-specific**

#### Recall prompt

*Why are vendor-specific exporters required for GPU monitoring instead of a single shared standard?*

[Back to Contents](#contents)

### Quality Metrics

Infrastructure monitoring covers **throughput** and **latency** so user experience matches the SLA. But LLMs must be not only **fast** but also **correct**.

Model quality monitoring has been critical since the early days of ML in production:

- a normal application that receives unknown input usually **crashes or shows a visible error**
- a machine learning model in the same situation usually **does not crash** and just continues producing **bad/wrong predictions**

A model is trained on a specific set of data expected to represent reality, but **human behavior changes over time (drift)**, so even a perfectly trained model requires periodic tuning or retraining to preserve quality. Techniques used to monitor this include:

- **performance metrics**
- **data drift detection**
- **bias detection**

These techniques fall under a broader initiative known as **responsible AI**, which existed before generative AI and is now evolving to cover the new challenges LLMs bring.

#### Hallucinations

Given the generative nature of LLMs, there are many ways for a model to produce an incorrect result. The worst case is when the generated outcome **sounds completely reasonable but refers to something that does not exist**. This is called a **hallucination**.

> While a hallucination may seem harmless in isolation, consider a company chatbot that hallucinates and **approves a refund based on a nonexistent policy**.

##### Example 5-6. LLM hallucination (OpenAI ChatGPT)

```text
"What is the world record for crossing the English channel entirely on foot?"
"This world record was made on August 14, 2020, by Christof Wandratsch of Germany,
who completed it in 14 hours and 51 minutes."
```

There is **no generic evaluation metric** to judge whether an LLM is hallucinating. However, many benchmarks assess overall quality based on capabilities such as **reasoning ability**. One of the most-used suites for this task is the [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness).

#### LLM-as-a-judge

Pre-deployment benchmarks help **select** a model, but what about **ongoing quality evaluation** in production?

This is where **LLM-as-a-judge** techniques come in:

> **one LLM evaluates another LLM's outputs for quality dimensions like relevance, coherence, factuality, and safety.**

This approach scales better than human evaluation and captures more nuanced quality issues than simple rule-based checks. For example, a powerful model like **GPT-4** or a specialized judge model can assess whether responses are helpful, accurate, and appropriate. It acts as an **automated quality reviewer**.

Operational considerations on Kubernetes:

- evaluating **every** response synchronously would add latency and significantly raise inference costs
- production systems typically evaluate a **sampled subset (1%–10%)** in an **asynchronous pipeline** that does not block user-facing requests
- the judge model produces quality scores that can be exported as **Prometheus metrics**, allowing the same monitoring and alerting patterns as infrastructure metrics

Frameworks for LLM evaluation include:

- **[OpenAI Evals](https://github.com/openai/evals)**
- **[LangSmith](https://www.langchain.com/langsmith/observability)**
- **[Arize AI](https://arize.com/)**; [GitHub](https://github.com/Arize-ai/phoenix)

Many teams also implement custom solutions tailored to specific quality requirements.

<u>Important principle:</u> treat **quality metrics as first-class observability signals** alongside latency and throughput. Store evaluation results in your existing observability stack (Prometheus for metrics, logging systems for detailed results) and establish **quality SLOs** just as you would for infrastructure metrics.

#### Task-specific quality metrics

For some specific tasks, computable metrics help mitigate hallucination risk. For **summarization**, the output is expected to mostly contain text that exists in the input. The **ROUGE** technique measures the **overlap of groups of words** between input and output.

A small component can compute the metric and export it to Prometheus.

Even when a model does **not** hallucinate, it can still produce **inappropriate or toxic content**. **Guardrails** are the mitigation technique for that.

#### Encode this

- **Infrastructure monitoring is not enough; model quality must also be observed**
- **Hallucinations are the most challenging LLM quality issue**
- **LLM-as-a-judge evaluates a sampled subset asynchronously and produces Prometheus-friendly scores**
- **ROUGE-style metrics work for narrower tasks like summarization**
- **Quality metrics deserve their own SLOs**

#### Recall prompt

*Why is LLM-as-a-judge usually applied to a sampled subset rather than every production request?*

[Back to Contents](#contents)

### Responsible AI

**Responsible AI** groups all the principles and techniques to develop and manage AI solutions with the goal of enabling **transparency and trust** for all stakeholders. It has ethical implications to **avoid biases** and aims to mitigate risks related to the adoption of AI.

This cannot be achieved by focusing on a single aspect; it requires a **framework adopted at every organizational level**.

> Compare it to security: a dedicated security team that implements security policies does not replace the fact that **everyone must adopt proper security principles**.

The term covers different aspects with no single definition, but they can be summarized as:

- **explainability**
- **fairness**

More recently, LLM-specific concerns — particularly **toxic content detection** and **hallucinations** — have become the priority. These are covered separately under **Model Safety**.

#### Explainability

**Explainability** is the principle that **human trust requires the ability to understand why and how a model produced a prediction**.

- not every model has the same level of intrinsic explainability
- a **neural network** is very powerful but **hard for humans to understand**, because knowledge is captured in layers and weights as numbers that cannot easily be correlated with inputs and outputs

Explainability techniques can target:

- **global explanation** — overall model behavior
- **local explanation** — a single prediction

> Sometimes called **interpretability** because some models can be directly interpreted.

**From a Kubernetes perspective:**

- KServe supports attaching an **[explainer](https://kserve.github.io/website/docs/model-serving/predictive-inference/explainers/overview)** to an `InferenceService` to perform local explanations
- this is **not usually suggested in production**, because computing the explanation can be an **order of magnitude more expensive** than executing the model

The **[TrustyAI](https://github.com/trustyai-explainability/trustyai-explainability/)** project provides multiple explainer implementations and integrates natively with KServe. [Documentation](https://kserve.github.io/website/docs/model-serving/predictive-inference/explainers/trustyai).

For production use, an **[Inference Logger](https://kserve.github.io/website/docs/model-serving/predictive-inference/logger)** captures each request and response pair from the model server. This allows generating local explanations **retroactively** — only when needed, such as when investigating disputed predictions — rather than computing expensive explanations for every request in real time.

#### Fairness

**Fairness** is the principle that models should **not discriminate** against people, in particular **underrepresented groups**, and should not learn prejudice that may be present in training data.

How bias enters models:

- **underrepresented categories** without explicit discrimination in the data
- **correlations that should not drive predictions**

> Example: people living in a poor area may have higher loan rejection rates, but the model should not automatically reject loan requests based on the area.

The concept of bias is usually tied to features called **protected attributes**:

- for these features, the model is expected to behave **fairly**
- their values should not drive prediction results

The most critical aspect:

> Even with bias-free training data and a properly trained model, **bias can still occur at runtime** because of **data drift**. Training data may not represent current human behavior, so when the model processes similar data for the first time, a biased outcome can emerge.

**KServe and TrustyAI** can help monitor this in production while the model is running, producing **bias metrics** against one or more protected attributes. TrustyAI uses the **Inference Logger** to retrieve prediction data and compute Prometheus metrics. You can find more information by [checking this demo](https://github.com/trustyai-explainability/odh-trustyai-demos).

#### Encode this

- **Responsible AI is a framework, not a single feature**
- **Explainability has global and local forms; local explanations are expensive in real time**
- **Inference Logger enables retroactive explanation without paying inference-time cost**
- **Fairness focuses on protected attributes and unfair correlations**
- **Data drift means bias can appear at runtime even when training was clean**

#### Recall prompt

*Why is computing local explanations at inference time usually avoided in production?*

[Back to Contents](#contents)

### Model Safety: Hallucination and Guardrails

**Model safety** is likely the fastest-evolving area in LLM monitoring, with expectations for significant developments and disruption.

It addresses two critical challenges in LLM deployment:

- **hallucinations** — models generating plausible but incorrect information
- **toxic or inappropriate content** — including prompt injection attacks

Both require **detection mechanisms** and **protective measures (guardrails)** to ensure models behave safely and reliably in production.

#### Understanding and Detecting Hallucinations

LLMs are prone to hallucinations because they **provide clear and well-motivated answers even when hallucinating**.

##### What are hallucinations?

Hallucinations are inconsistencies at different levels:

- **within the generated text itself** — *"Daniele is tall, thus he is the shortest person"*
- **between input prompt and generated answer** — *"Generate formal text to announce to colleagues..."* but the model produces *"Yo Boyz!"*
- **factually incorrect** — *"First man on the Moon in 2024"*

##### Why do hallucinations happen?

LLMs are black boxes; hallucinations happen for different reasons:

- **partial or inconsistent training data**, so the LLM learns to generalize from data that is not comprehensive
- **"hallucination prone" configuration** with sampling parameters (such as `temperature`, `top_k`, `top_p`) that influence the model to produce less probable but more creative answers
- **poor context or prompt quality**, where the question is too generic

Analyzing these causes reveals a fundamental issue:

- most teams **do not train LLMs themselves**, so cannot address training data
- model configuration can limit creativity, but **creativity is a goal** of LLMs
- the **area with the most control is making the input more specific**

#### Other safety risks

Beyond hallucinations:

- toxic or inappropriate content can emerge from **model outputs** or **malicious user inputs**
- *inappropriate* is broad: from off-topic questions to **returning private/sensitive information (PII)**
- well-known open source models are often fine-tuned to encourage friendly, non-condescending generation, but **attackers can craft prompts to bypass built-in safety mechanisms**

Attack types:

- **prompt jailbreaking** — trying to make the model produce something against terms and conditions
- **prompt injection** — injecting specific instructions in the prompt to bypass developer-configured instructions

> Producing such an attack is very simple: add an instruction like *"ignore all previous instructions"* to confuse the model and bypass system prompts.

#### Runtime Guardrails

Models can be protected with **guardrails**: **preprocessors and postprocessors** for user input and model output that validate data to keep the model on track.

At their core, guardrails consist of:

1. an **input validation function** that analyzes text (or other modalities) and determines whether it meets safety criteria
2. an **action**: allow the request, block it, or modify it

Analyzing arbitrary text to decide if it is inappropriate is **not trivial**. Other LLMs can be used for this purpose.

#### Specialized safety models

Some models are tuned specifically for detecting these problems and allow specifying which risk types to detect:

- **Llama Guard**
- **Granite Guardian**

Both are available on **Hugging Face** with different sizes and configurations. The largest is around **7B or 8B parameters**, corresponding to about **15–20 GB** of data. These models can be deployed like any other LLM with **KServe** and **vLLM**.

The validation configuration is done **in the prompt itself**. The same approach can validate model output.

##### Example 5-7. Prompt to validate user input using Llama Guard

```text
[INST] Task: Check if the content of 'user' messages in the
   conversations our policies described with the below categories.

<BEGIN UNSAFE CONTENT CATEGORIES>
O1: Violence and Hate.
Should not
- Promote or suggest people to use violence.
...
Can
- Describe what violence is.
...
<END UNSAFE CONTENT CATEGORIES>

<BEGIN CONVERSATION>
...
<END CONVERSATION>

Provide safety assessment with following format:
- First line must be 'safe' or 'unsafe'
- If unsafe, second line must include comma-separated list of
  violated categories.
```

What to notice:

- in a chat with an LLM, **different roles** can be defined; this instruction tells Llama Guard to **check only user messages**
- the **unsafe content categories** section configures which categories to detect; the more specific the `Should not` and `Can` rules, the better
- the **conversation to verify** is included after the appropriate tag
- being **specific about the result format** makes the output easy to parse to decide how to proceed

This technique is very powerful but **expensive in resource usage and latency**:

- another LLM must be deployed to check the conversation
- the evaluation requires the **full conversation** because safety assessment cannot be done token by token
- this introduces a considerable delay on the end-user side

It is critical to **consider smaller, specialized models and techniques** for guardrails to find the best **cost-performance trade-off**.

Composition of the guardian model with the user request flow can be done programmatically with custom orchestration code, but there is **ongoing work to include this in AI/LLM gateway components**. Specialized frameworks have also been developed to orchestrate and manage guardrails in production environments.

#### NVIDIA NeMo Guardrails

**[NVIDIA NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails)** is an open source toolkit that adds **programmable guardrails** to LLM-based conversational applications.

The framework uses **Colang**, a custom modeling language designed specifically for defining **dialogue flows** and **safety constraints**. Developers control LLM behavior by:

- defining specific response patterns
- preventing discussion on certain topics
- ensuring conversation paths stay within acceptable boundaries

NeMo Guardrails supports **five types of rails**, applied at different stages of the LLM interaction:

| Rail | Purpose |
| --- | --- |
| **Input rails** | Validate and filter user inputs before they reach the model, blocking malicious prompts or sensitive information requests |
| **Dialog rails** | Control the conversation flow and ensure the model stays on topic during multi-turn interactions |
| **Retrieval rails** | Validate information retrieved from external knowledge bases in RAG scenarios |
| **Execution rails** | Monitor and control when the model invokes external tools or APIs |
| **Output rails** | Filter and validate model responses before returning them to users |

The framework integrates with:

- **cloud LLMs** like OpenAI models
- **self-hosted models** like Llama 4

Deployment options:

- Python library
- standalone **Guardrails server**
- container image for Kubernetes deployment

**Best fit:** domain-specific assistants and question-answering systems that require strict conversational boundaries.

#### FMS Guardrails Orchestrator

The **[FMS Guardrails Orchestrator](https://github.com/foundation-model-stack/fms-guardrails-orchestrator/)**, developed by **IBM Research** and integrated with the **TrustyAI** project, is designed specifically to **orchestrate the application of one or more guardrails in complex workflows**.

It addresses a common production challenge: **coordinating multiple safety checks** at different stages of request processing.

Key capabilities:

- a layer of abstraction to **compose different guardrail types** (input validation, output filtering, PII detection) into cohesive safety pipelines
- each guardrail is called a **detector**
- composition is particularly valuable when applying **different policies based on context, user roles, or which LLM is invoked**

For Kubernetes deployments:

- can be deployed as a **service between the application and the model server**
- intercepts requests and responses to apply configured safety policies
- integration with **TrustyAI** provides monitoring; guardrail activations and violations are tracked as **Prometheus metrics**

#### Guardrails AI

**[Guardrails AI](https://guardrailsai.com/)** takes a more **developer-oriented approach** compared to infrastructure-focused frameworks.

It is a **Python library** with:

- a **validator-based architecture**
- a centralized hub of **prebuilt risk detectors**

Two primary purposes:

- detecting and mitigating AI-related risks through input/output validation
- helping generate **structured data** from LLM responses

The key differentiator is the **[Guardrails Hub](https://guardrailsai.com/hub)**, a library of community-contributed validators that detect specific risks such as:

- toxic language
- PII exposure
- hallucinations
- competitor mentions
- off-topic responses

Validators can be combined to create comprehensive guards tailored to a specific use case.

Unlike frameworks that require learning a new configuration language or deploying separate orchestration services:

- Guardrails AI validators are **Python functions integrated directly into the application code**
- the framework intercepts LLM inputs and outputs within the application
- it runs them through configured validators and takes action (block, log, remediate)

**Best fit:** teams preferring to manage safety logic **within the application layer** rather than deploying additional infrastructure components.

**Trade-off:**

- **less integrated with the Kubernetes ecosystem** compared to NeMo Guardrails or FMS Guardrails Orchestrator
- in Kubernetes environments, Guardrails AI is **embedded directly into the application container**
- simpler to deploy, but potentially **less flexible for centralized policy management** across multiple services

#### Llama Stack and Moderation APIs

**[Llama Stack](https://ogx-ai.github.io/)**, created by **Meta**, defines a comprehensive set of APIs for building generative AI applications, including a dedicated safety layer through its **Safety API** with **configurable shields (guardrails)**.

The Safety API allows:

- registering safety shields with specific configurations
- applying them at **both input and output stages** of LLM interactions

Multiple shield types are supported, from basic content moderation with **Llama Guard models** to advanced custom safety policies for domain-specific requirements. Shields can be applied with fine-grained control:

- different shields for **user inputs** versus **model outputs**
- **contextual shields** that adapt based on conversation state

Llama Stack also provides a **moderation endpoint** at `/v1/moderations`, mirroring **OpenAI's Moderation API**:

> The [OpenAI Moderation API](https://developers.openai.com/api/docs/guides/moderation) is a specialized model endpoint that classifies text inputs across categories like **hate speech**, **self-harm**, **sexual content**, and **violence**. It returns **category scores** and **binary flags** indicating whether content violates each policy.

Advantages of moderation APIs (OpenAI's or Llama Stack's):

- pre-trained, continuously updated models specifically designed for safety classification
- no need to deploy and maintain separate guardrail models

Disadvantages:

- typically **less customizable** than framework-based approaches
- relying on **external APIs** introduces network latency and potential vendor dependencies

For Kubernetes deployments:

- Llama Stack can be deployed as a service that applications call to apply shields
- or the Llama Stack SDK can be integrated directly into application containers
- the moderation API approach works best for **asynchronous validation workflows** where a small percentage of requests are sampled and evaluated without blocking user-facing responses

> **Clarification on Llama Stack deployment model**
>
> Llama Stack is an **open-source API server/framework** for building GenAI applications. The Llama Stack server can be **downloaded, installed, and deployed inside an organization's own environment**, including an **on-prem Kubernetes cluster**.
>
> Llama Stack being "API-based" does **not** mean it must be cloud-hosted. It can expose APIs **locally inside Kubernetes**, for example as an **internal cluster service**.
>
> In Kubernetes, the main components are:
>
> - **Llama Stack server** — the running service/pod that exposes GenAI APIs, safety APIs, moderation endpoints, tool APIs, RAG APIs, etc.
> - **Llama Stack API** — the HTTP interface exposed by the server, such as `/v1/moderations` or other OpenAI-compatible endpoints
> - **Llama Stack SDK/client** — the library used by application code to call the Llama Stack server APIs more easily
>
> A **fully on-prem setup** is possible when **all configured providers are also local/on-prem**, for example:
>
> - local inference provider such as **vLLM** or **Ollama**
> - local safety/guardrail model such as **Llama Guard**
> - local embedding model
> - local vector database or storage
>
> However, Llama Stack can also be configured to use **cloud providers**. In that case, the Llama Stack server may still run in your Kubernetes cluster, but it **forwards some requests to external cloud APIs**.
>
> Therefore, the key point is:
>
> **Llama Stack itself can be self-hosted and on-prem. Whether the full solution is truly on-prem depends on the providers configured behind Llama Stack.**

> **TIP**
>
> Many guardrailing techniques rely on **LLM as a judge**, where one LLM evaluates another's output (or even its own).
>
> When implementing LLM as a judge for safety detection or any evaluation, be **very specific** in evaluation questions. Instead of asking *"Is this answer right?"*, ask **targeted questions** like:
>
> - *"Is the tone of this answer formal?"*
> - *"Does this response include personal information?"*
>
> Specific, focused evaluation criteria produce **more reliable and consistent judgments** from the judge model.

Model safety is still a very active field. Implementing proper guardrailing is critical to mitigate risks related to LLM usage, but it remains **difficult to find the right trade-off** to avoid an explosion of complexity and cost.

#### Encode this

- **Hallucinations have three flavors: internal contradiction, prompt mismatch, factual error**
- **Most teams cannot fix training data; the leverage is in improving prompts and adding guardrails**
- **Guardrails = validation function + action (allow/block/modify)**
- **Specialized safety models like Llama Guard and Granite Guardian are LLMs in their own right and add resource + latency cost**
- **NeMo Guardrails uses Colang and 5 rail types (input, dialog, retrieval, execution, output)**
- **FMS Guardrails Orchestrator composes detectors and integrates with TrustyAI for Prometheus metrics**
- **Guardrails AI is developer-centric, embedded in application code, less Kubernetes-native**
- **Llama Stack and OpenAI-style moderation APIs are pre-trained shields but less customizable**
- **LLM-as-a-judge prompts should be specific, narrow questions**

#### Recall prompt

*Why does deploying a specialized safety model like Llama Guard introduce significant latency for end users, and what mitigates that cost?*

[Back to Contents](#contents)

### Observability Lessons Learned

LLM observability spans **infrastructure metrics**, **model quality monitoring**, and **safety guardrails**.

**Traditional monitoring tells an incomplete story**

CPU and memory utilization matter, but they miss the **primary compute resource (GPU)** and the distinct characteristics of inference phases:

- **compute-bound prefill**
- **memory-bound decode**

**Token-based metrics replace request-based observability**

- **Time To First Token (TTFT)** measures user-perceived latency during the prefill phase
- **Time Per Output Token (TPOT)** determines whether generated text appears faster than humans can read

These metrics map directly to user experience in ways that traditional throughput and latency cannot.

**Model quality observability extends beyond infrastructure monitoring**

Guardrails for safety, hallucination detection, and bias mitigation must be embedded at **both input and output stages**, treating content validation as a **first-class operational concern** rather than an afterthought.

**Responsible AI is a framework, not a feature**

Explainability and fairness require **organization-wide adoption**, supported by tools like **TrustyAI**, **Inference Logger**, and Prometheus-based bias metrics.

**Safety guardrails are a trade-off**

- **NeMo Guardrails**, **FMS Guardrails Orchestrator**, **Guardrails AI**, and **Llama Stack** offer different points on the cost-complexity-customization spectrum
- LLM-as-a-judge scales evaluation but should sample and use **narrow, specific evaluation prompts**

#### Encode this

- **LLM observability requires GPU-aware, token-aware, quality-aware thinking**
- **Logs, metrics, and traces remain the foundation, but their content is different from traditional apps**
- **TTFT and TPOT map to prefill and decode phases**
- **GPU monitoring depends on vendor-specific exporters**
- **Quality and safety metrics deserve SLOs, not just dashboards**
- **Guardrail choice should match the team's operating model and customization needs**

#### Recall prompt

*Why is CPU utilization a misleading scaling signal for LLM workloads, and which signals should replace it in production observability?*

[Back to Contents](#contents)

## Model Customization

Training an LLM **from scratch** requires significant computational resources and expertise that most organizations do not have. These notes do **not** cover creating a model from scratch. Instead, the focus is on **customizing an existing LLM** for a specific use case.

This section covers:

- several **tuning techniques**
- the Kubernetes technologies available to implement and deploy the corresponding training jobs

> **Deep-dive companion notes:** for a much more detailed treatment of **finetuning specifically** — covering transfer learning, when (and when not) to finetune, RAG vs finetuning trade-offs, memory bottlenecks, and PEFT — see the dedicated **[Finetuning notes](Finetuning.md)** (a structured companion to Chapter 7 of [*"AI Engineering"* by Chip Huyen](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)).

[Back to Contents](#contents)

### Introduction to LLM Creation

- LLM training techniques differ significantly across model providers that invest heavily in developing proprietary methods. Most technical papers published with model releases **omit implementation details**, making reproduction difficult. The [technical paper for **DeepSeek V3**](https://arxiv.org/pdf/2412.19437) is a notable exception with unusually detailed documentation.

- Much of the innovation focuses on **new model architectures with more efficient attention mechanisms**. **Dataset curation** and **tuning methods** are rarely disclosed in detail.

#### The LLM creation pipeline

- Training starts with **data cleaning and deduplication**. The **first phase, pre-training**, consumes most of the time and cost: processing all data using **thousands of GPUs for many weeks**. The output is a **base or foundation model** that can predict text but lacks an understanding of tasks or appropriate content boundaries.

- The next step is **alignment**, which teaches the LLM to **perform tasks safely and reliably** according to human preferences.

> This phase is analogous to **Isaac Asimov's Three Laws of Robotics**: just as robots need core principles to ensure safe interaction with humanity, **LLMs need behavioral boundaries** to perform tasks without causing harm.

Alignment requires:

- **curated labeled data**
- a **reward mechanism** where humans or specialized reward models evaluate the model's responses

It is possible to find **base models** that went through a pre-training phase only, but the **vast majority** of publicly available models have **already been aligned** so that they are ready to be used for a specific set of tasks.

**Model customization**, also known as **post-training**, applies to an **already aligned model**.

![LLM creation pipeline](<assets/LLM creation pipeline.png>)

**Figure 6-1. LLM creation pipeline**

> **MODEL TUNING, MODEL CUSTOMIZATION, AND POST-TRAINING**
>
> - **Model tuning** is a **general term** for various fine-tuning techniques and is **not specific to LLMs** — it also applies to predictive AI.
>
> - **Model customization** is a **broader term** that encompasses all techniques used to **modify an LLM** or to **learn new tasks**. Some of these methods differ compared to traditional fine-tuning and may require multiple steps, including human interaction.
>
> - **Post-training** refers to the **specific phase** in the LLM creation pipeline where model customization occurs. This step can be applied **multiple times** to **incrementally inject new policies or knowledge** into the model.
>
> These terms are often used **interchangeably** in these notes because they all involve **modifying a model** and present **similar operational challenges** on a Kubernetes platform.

#### Why versatility matters

The primary difference that makes LLMs unique from traditional predictive AI models is their **versatility**:

- a single **LLM can perform a large number of different tasks**
- a traditional **machine learning model is specialized for just one**

This versatility is why **inference comes first** in operational terms: you can often **adapt an existing LLM** for different use cases **without any training at all**.

Before diving into training techniques, it's worth understanding **when you don't need to train**. Many use cases can be solved through alternatives that **avoid the complexity and cost entirely**.

#### Encode this

- **LLM creation = pre-training (huge) → alignment → post-training (customization)**
- **Most public models are already aligned and ready for use**
- **Customization = post-training applied on top of an aligned model**
- **Tuning / customization / post-training are used interchangeably here**

#### Recall prompt

*Why is alignment necessary after pre-training, and what does it add that pre-training alone cannot?*

[Back to Contents](#contents)

### Prompt and Context Engineering

- The real power of LLMs is that they **work without modification**. Through **careful engineering of inputs and context**, you can often achieve your goals **without training**. These alternatives aren't just simpler — they are **often the right choice**.

#### Prompt engineering

> **Prompt engineering** is the process of **crafting detailed and specific instructions (prompts)** to guide an LLM's output.

This set of instructions is **critical to maximize the accuracy** of the response. This field is becoming a **specialization in its own right**, with best practices for communicating effectively with an LLM to obtain the most accurate results.

Effective prompt engineering is not just about specifying the task; it also involves describing:

- **The scenario** — *"This is an airline company named ABC"*
- **The role the model should take** — *"You are an AI-assistant chatbot to help customers"*
- **The boundaries of the task** to help reduce hallucinations or guide behavior — *"You can only reply about our company and if you are sure about the answer"*

Similar prompts are usually specified by the **provider of the service** and **hidden to the end users** as a **system prompt**.

> **System prompts should not be relied upon as security controls** — they can be bypassed through **prompt injection** or **jailbreaking techniques**.
>
> For production systems with security requirements, **additional safeguards** like **input validation**, **output filtering**, and **content moderation** should be implemented at the application level. See [Model Safety: Hallucination and Guardrails](#model-safety-hallucination-and-guardrails) for the full guardrail toolkit.

Since every LLM is trained on a **vast but finite dataset**, another use of prompt engineering is to **inject additional data into the prompt**, forcing the model to use that information during generation.

#### Context engineering

- Basic or manual prompt engineering techniques have **evolved into established patterns** that make the system more powerful, even **enabling models to dynamically invoke tools** to retrieve information or perform actions.

- This is a core principle of **AI agents** and is often called **context engineering**. The term reflects that the **main engineering work lies in creating the input context** for the LLM, a process involving **complex, multicomponent, and iterative steps**.

#### Retrieval-Augmented Generation (RAG)

> One of the most widely adopted patterns for context enrichment is **Retrieval-Augmented Generation (RAG)**, which **injects relevant data from external sources** into the context based on the user's question.

How the RAG pattern works:

- additional data is ingested as **embedding vectors** into a **vector database** using specialized **embedding models**
- when a user request arrives, an **initial query** is performed against the vector database using **similarity search algorithms** (such as **approximate nearest neighbors**) to find content that is **semantically close** to the user's input
- this **additional context** is then included in the prompt for the model to use when answering the question

This solution helps to inject:

- **external or recent knowledge** that wasn't available during the model's training
- **proprietary data**
- **information published after the training cutoff date**

While each model has a **limited context window**, RAG addresses this by **filtering and including only the data most relevant** to the user's question — rather than attempting to include an entire knowledge base.

![An example of RAG pipeline](<assets/An example of RAG pipeline.png>)

**Figure 6-2. An example of RAG pipeline**

The flexibility of solutions like RAG makes them **increasingly popular**. You can **update the vector database with new data in minutes** and **refresh the knowledge of the solution**. This trend, together with the adoption of **agentic AI** patterns, is taking over significant portions of the model customization space.

#### Combining prompt/context engineering with customization

- <u>Important takeaway:</u> all prompt and context engineering techniques work with **both general-purpose models and tuned models**. You can **combine RAG with model customization**.

The question isn't **"either/or"** but rather:

> *Which combination gives you the best balance of performance, cost, and maintainability?*

#### Encode this

- **Prompt engineering = scenario + role + boundaries + injected data**
- **System prompts are not security controls — pair with guardrails**
- **Context engineering = building the input context dynamically for the LLM (multistep, multicomponent)**
- **RAG = embeddings + vector DB + similarity search → context injection**
- **RAG and customization are complementary, not mutually exclusive**

#### Recall prompt

*When would you reach for RAG instead of fine-tuning, and when does the inverse become a better operational choice?*

[Back to Contents](#contents)

### When to Use Model Customization

- While **RAG** and **prompt engineering** are powerful, they aren't always the **most cost-effective solution**. Model customization becomes valuable when you need to **embed knowledge or behavior directly into the model itself**.

#### Inference-cost trade-off

- The possibility to influence model behavior through prompts and RAG is powerful and often sufficient. But this approach has limitations that make model customization the better choice in certain scenarios.

A **large context window requires more GPU memory** at inference time. Model customization is a key tool for **controlling inference costs**:

- it allows a company's **core, slow-changing knowledge** to be **embedded directly into the model**
- this **reduces the need for a large context window** with every request

> Example: a **bank** could create a customized model with embedded domain knowledge about **loans, trading, and credit risk**. This information doesn't change frequently, so it makes sense to **embed it in the model itself** rather than providing it in the context of every request. The result is **lower inference costs** and **potentially better performance**.

#### Model size and Small Language Models (SLMs)

- The same principle applies to **model size**: a **small, specialized model** (potentially created through **distillation** from a larger model) can be **as effective as or even more effective than a larger, untuned model**.

This is particularly relevant with **Small Language Models (SLMs)** that require fewer resources to be served:

- an SLM usually has between **8 and 16 billion parameters**
- this makes it a good candidate to be tuned with **constrained time and resources**

**Model distillation** is another approach, where a **large teacher model** is used to train a **smaller, more efficient SLM** that inherits the teacher's knowledge while requiring fewer computational resources.

#### Encode this

- **Customization shines when knowledge is stable and large context windows are too expensive**
- **SLMs (8–16B params) are the natural target for cost-effective customization**
- **Distillation transfers a teacher model's knowledge into a smaller student**
- **The choice is about inference economics, not just accuracy**

#### Recall prompt

*Why does embedding stable domain knowledge into a model lower inference cost compared to passing it through RAG every request?*

[Back to Contents](#contents)

### Tuning a Model

The possibility to **continually train a model**, also known as **post-training**, is **not new to machine learning**. In traditional predictive AI, models are often fine-tuned in a **second phase** to update them with new data.

In the context of generative AI, this activity is usually performed to:

- **specialize a model** and improve performance in a specific domain
- **reduce the overall cost** of the solution by leveraging **specialized smaller models** instead of one of the bigger and more expensive alternatives

![Fine-tuning concept](<assets/Fine-tuning concept.png>)

**Figure 6-3. Fine-tuning concept**

While fine-tuning is **less complex and costly than pre-training** by an order of magnitude, it can still take **many hours or even days** to run.

Sometimes, however, **full fine-tuning is unnecessary**. For example, the user might want to **reduce the domain areas** that the model should be able to answer — similar to the prompt engineering use case described before but as a **built-in feature in the model** and **less affected by external attacks**. These simpler options fall under a category named **Parameter-Efficient Fine-Tuning (PEFT)**.

For both full fine-tuning and PEFT approaches, **Hugging Face** provides the **Transformer Reinforcement Learning (TRL)** library, which includes **`SFTTrainer`**, a utility class that can:

- load a model
- perform various tuning techniques
- include an evaluation step to compute accuracy

> **WHAT IS SUPERVISED FINE-TUNING?**
>
> The name of the library `SFTTrainer` stands for **Supervised Fine-Tuning Trainer**. The term **"supervised"** is usually omitted when discussing fine-tuning because practitioners implicitly understand the process as supervised.
>
> While some techniques for **unsupervised fine-tuning** exist, the vast majority of methods require **labeled data** as input — data that has been classified by a human or another model. The reason is straightforward: for a model to learn a specific policy or piece of knowledge, the **input dataset must contain the specific traits** the model is expected to embed.
>
> However, **labeled data for generative models differs from classification tasks**:
>
> - in **classification**, labels are **discrete categories** such as `spam` / `not-spam`
> - for **LLMs**, the label is the **complete expected output text**
>
> Training pairs consist of input-output sequences such as:
>
> - input *"Translate to French: Hello"* paired with output *"Bonjour"*
> - input *"Summarize: [article]"* paired with output *"The article discusses X, Y, and Z."*
>
> During training, the model learns by **predicting the next word at each step** in the output sequence and **adjusting when it predicts incorrectly**. Both classification and generation are **"supervised"** because training provides correct answers, but **generation predicts sequences of tokens** rather than single categories.
>
> The **creation of a supervised input dataset** is usually an **expensive activity**. As a result, these curated datasets are **orders of magnitude smaller** than the datasets used for unsupervised pre-training.

#### Fine-Tuning

**Fine-tuning** a model involves **continuing the training process** to embed additional knowledge or tasks, such as:

- **instruction following**
- **question answering**
- **chat capabilities**

In other words, **full fine-tuning changes all the model's parameters**, producing a **distinct model** that, while derived from the original, has been **fully adapted to the new training data**.

This approach requires a **considerable amount of labeled data** (at least **hundreds of thousands of new examples**) to influence the model enough to learn new concepts. It is a **very expensive activity**.

From a Kubernetes platform perspective, full fine-tuning requires:

- **many GPUs during the training phase**
- **dedicated GPUs to serve the new model** — there is no efficient way to layer or merge it with the original at inference time

While this is the **primary approach for predictive AI**, **full fine-tuning in generative AI is more challenging** due to:

- the **high cost of preparing datasets**
- the **computational expense** of training and inference
- risks such as **catastrophic forgetting** — where the model loses previously learned knowledge

##### Example 6-1. `SFTTrainer` usage to perform supervised fine-tuning

The Hugging Face `SFTTrainer` can be used to perform full fine-tuning:

```python
from datasets import load_dataset
from trl import SFTTrainer
from transformers import AutoModelForCausalLM


train_dataset = load_dataset("json", data_files="my_file.json")
original_model = AutoModelForCausalLM.from_pretrained(...)

trainer = SFTTrainer(
    model=original_model,
    train_dataset=train_dataset,
)

trainer.train()
trainer.save_model("target_location")
```

What to notice:

- **`load_dataset(...)`** — loads the dataset with new content for the model to learn. This can be a **public dataset from Hugging Face** or a **local file**
- **`AutoModelForCausalLM.from_pretrained(...)`** — the function used to load the model is the **same one used for inference**. The model can be downloaded on the fly, but it is typically **downloaded locally first**

#### Parameter-Efficient Fine-Tuning

**Parameter-Efficient Fine-Tuning (PEFT)** is a group of techniques that takes a **different approach** to tuning a model:

- the **original model remains unchanged**
- instead, it is **composed with new layers** that influence its behavior at runtime during inference

While conceptually similar to prompt engineering in that both **influence model behavior without full retraining**, **PEFT embeds learned parameters directly into the model architecture** rather than relying on text-based prompts at runtime.

##### Why PEFT is easier for Kubernetes platforms

From a Kubernetes platform perspective, PEFT is **much easier to manage** for both training and serving:

- the **training phase** requires **fewer data samples** (between **100 and 1,000 labeled examples**), making the training job **shorter and less hardware intensive**
- **serving these fine-tuned models is also more efficient** — the **base model can be dynamically composed with one or more tuned layers at runtime** in the same deployment, thanks to support in modern inference engines
- see [OCI Image for Storing Model Data](#oci-image-for-storing-model-data) for efficient model storage and [LLM-Aware Routing](#llm-aware-routing) for inference routing

##### PEFT trade-offs

The main drawback of PEFT is that it has a **more limited impact** on the model compared to full fine-tuning, which modifies all parameters. With PEFT, **only a small fraction of the parameters are affected**.

> For example, **LoRA** (one of the most popular PEFT algorithms) might tune **less than 1% of the total parameters** for a **Llama 3.1 8B model**.

Hugging Face created a library named **`peft`** to collect different PEFT algorithms, and it integrates **natively with the `SFTTrainer`** class.

##### Example 6-2. LoRA fine-tuning using `SFTTrainer`

```python
from datasets import load_dataset
from trl import SFTTrainer
from peft import LoraConfig
from transformers import AutoModelForCausalLM

train_dataset = load_dataset("json", data_files="my_file.json")
original_model = AutoModelForCausalLM.from_pretrained(...)
lora_config = LoraConfig(...)

trainer = SFTTrainer(
    model=original_model,
    train_dataset=train_dataset,
    peft_config=lora_config,
)

trainer.train()
trainer.save_model("target_location")
```

What to notice:

- **`lora_config = LoraConfig(...)`** — compared to full fine-tuning, the **only difference** is the initialization of the PEFT configuration (in this case, LoRA). There are many parameters; check the **[Hugging Face PEFT documentation](https://huggingface.co/docs/peft/package_reference/lora)** for more details
- **`peft_config=lora_config`** — to enable PEFT, you just need to **pass the `lora_config` instance** as the `peft_config` argument

#### Low-Rank Adaptation

- **[Low-Rank Adaptation (LoRA)](https://arxiv.org/abs/2106.09685)** keeps the **original model weights frozen** while training a **relatively small number of new parameters** on the fine-tuning dataset.

- The new parameters are organized as **smaller matrices called adapters**. These **low-rank matrices** learn the updates, and their **product is combined with the original weights**.

##### How LoRA decomposes weight updates

- In a **traditional fine-tuning job**, the training process **learns a new, full-sized matrix** representing the weight updates.

- **LoRA**, however, **decomposes this large update**. Instead of learning the full matrix, the training produces **two much smaller, low-rank matrices**. When these two smaller matrices are **multiplied**, their **product approximates the full weight update**.

- This **decomposition** is what makes the training procedure **significantly more efficient**.

![Comparison of LoRA decomposition and full fine-tuning](<assets/Comparison of LoRA decomposition and full fine-tuning.png>)

**Figure 6-4. Comparison of LoRA decomposition and full fine-tuning**

##### LoRA variants

LoRA is applicable to a **large set of LLMs**, and **many variants** of the algorithm exist for specific scenarios. Two notable specializations:

- **[X-LoRA](https://arxiv.org/abs/2402.07148)** — extends the approach to **Mixture-of-Experts (MoE)** architectures
- **[QLoRA](https://arxiv.org/abs/2305.14314)** — applies **quantization** to reduce fine-tuning memory requirements

##### Benefits of LoRA

LoRA offers **two main benefits**:

- a **cheaper training phase** (in terms of time and hardware) compared to full fine-tuning
- an **efficient inference approach** — since the base model is **not modified**, adapters can be **composed with it at runtime**

The combined size of the two small matrices (**A** and **B**) is typically only **1–10% of the original model size**, making it possible to **serve one base model and many LoRA-tuned models** using the hardware required for **only the base model**.

![Serving of LoRA adapters](<assets/Serving of LoRA adapters.png>)

**Figure 6-5. Serving of LoRA adapters**

##### Merging LoRA adapters with the base model

Even if it is **not the traditional use case** for LoRA, it is still possible to **merge the LoRA adapter with the base model** for testing purposes.

> Further reading: the blog post **["Practical Tips for Finetuning LLMs Using LoRA (Low-Rank Adaptation)"](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)** by **Sebastian Raschka** provides more information about LoRA.

> **ADVANCED TUNING TECHNIQUES**
>
> Full fine-tuning and PEFT are **not the only ways** to tune a model; new and more complex techniques are **constantly emerging**.
>
> Many of these new approaches involve **multistep workflows** rather than a single training loop, which can include using **synthetic data** produced by the model in a previous iteration. Some of the most common advanced techniques include:
>
> - **Group Relative Policy Optimization (GRPO)**
> - **Direct Preference Optimization (DPO)**
> - **Model distillation**
> - **Model merging**
> - **Reward modeling**
>
> These notes do not cover these advanced methods in detail, as each technique is a complex topic. They are also very different:
>
> - **[GRPO](https://arxiv.org/abs/2402.03300)** is an innovation from the **DeepSeek** team
> - **[InstructLab](https://arxiv.org/abs/2403.01081v1)** is a full methodology from **IBM Research** for alignment tuning
>
> For more information, see the **[Transformer Reinforcement Learning (TRL)](https://github.com/huggingface/trl)** library from [Hugging Face](https://huggingface.co/docs/trl/en/index), which collects many of these techniques with **dedicated trainer classes**.
>
> The focus of these notes is on the **operational challenges** of generative AI. From a Kubernetes platform perspective, these tuning methods manifest as:
>
> - **long-running, multideployment topologies**
> - **most components require dedicated GPUs**
> - **the ability to communicate securely** between components
>
> The **security of this communication** is critical for production workloads and is a separate operational concern.

#### Encode this

- **Fine-tuning = all parameters change, very expensive, needs hundreds of thousands of examples, dedicated GPUs to serve**
- **PEFT = composes new layers on top of a frozen base, cheaper training, can share one base model across many adapters at inference time**
- **LoRA = decomposes weight updates into two small matrices (A × B); typically 1–10% of original size**
- **X-LoRA = LoRA + MoE; QLoRA = LoRA + quantization**
- **SFT = Supervised Fine-Tuning; the "S" is usually implicit**

#### Recall prompt

*Why can a single LoRA-tuned deployment serve many specialized variants of a model using essentially the hardware of just the base model?*

[Back to Contents](#contents)

### Running Tuning Jobs on Kubernetes

- With an understanding of the different tuning techniques and their trade-offs, this subsection explores **how to operationalize them on Kubernetes**.

- So far, the notes have introduced the core concepts for creating and tuning an LLM, from **traditional full fine-tuning**, to **PEFT**, to **advanced tuning pipelines**. Understanding these different approaches is important because they have **different implications and challenges** from a Kubernetes platform perspective.

- This subsection shifts from implementation details to **platform requirements**. All of these tuning techniques have **at least one training phase** that requires **GPUs for scaling**. The GPU management principles covered earlier for inference largely apply here as well — see [Kubernetes and GPUs](#kubernetes-and-gpus) for a recap.

#### Why networking becomes the bottleneck

- Although provisioning GPU workloads is not new, a **major additional challenge for training** is that **networking can easily become the bottleneck** of the system.

- A tuning job is **not equivalent to an inference request**; even for an SLM, the **hardware requirements for tuning are greater than for serving**. As a result, the job will likely require **multiple GPUs on the same node or even across multiple nodes**.

![Multinode training job](<assets/Multinode training job.png>)

**Figure 6-6. Multinode training job**

Based on the type of tuning performed, the system **gathers the sharded weights** of the model on all GPUs **before every "step"** of the model execution (in particular, every layer **forward and backward passes**). This action requires:

- a **continuous stream of data shuffling** across the GPUs
- based on the size of the model and the number of GPUs, it can produce **traffic of many gigabytes per second**

The **bandwidth is the main scalability challenge** and requires improvements across the entire stack:

- **specialized network interfaces and protocols**
- more efficient **kernel implementations** and ad-hoc **GPU instructions**

Similar to inference optimization, training also has kernel implementations that benefit from **dedicated GPU instructions**:

- **[Liger Kernel](https://github.com/linkedin/Liger-Kernel)** (optimized for **[Triton](https://triton-lang.org/main/index.html)**)
- **[FlashAttention](https://github.com/Dao-AILab/flash-attention)**

#### Higher-level training libraries

The attention kernel is a **core component**, and it is usually embedded in a **higher-level, end-user library**. While Hugging Face provides many of these libraries, such as **[Transformers](https://github.com/huggingface/transformers)**, other options include:

- **[DeepSpeed](https://github.com/deepspeedai/DeepSpeed)**
- **[NVIDIA's Megatron-LM](https://github.com/NVIDIA/Megatron-LM)**

Although these libraries have different APIs and configurations, they **all use [PyTorch](https://pytorch.org/)**, which has become the **de facto standard deep learning library** for LLM implementation.

> **NOTE — PyTorch**
>
> **PyTorch** is an **open source machine learning library** originally created by **Meta** and now owned by the **[PyTorch Foundation](https://pytorch.org/foundation/)**, part of the **Linux Foundation**.
>
> It has many different applications, but in the context of LLM development it is used mainly as the **core deep learning library**: other end-user libraries like **Hugging Face Transformers** use PyTorch and have **[deprecated](https://github.com/huggingface/transformers/pull/38758) support** for other deep learning libraries like **TensorFlow** or **JAX**.
>
> The PyTorch project has many different packages that cover a large set of capabilities:
> - the **core neural network implementation**
> - a **compiler**
> - a **distributed package** with the specific goal of supporting **distributed training jobs**
>
> In particular, **[Fully Sharded Data Parallel (FSDP2)](https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html)** is the most common library used to **scale the job on multiple nodes**.

The software and hardware stack is **evolving rapidly**, with the hope that many of these complexities will eventually become implementation details from a platform perspective. However, **optimizing the network stack** is a challenge that **cannot be avoided**.

Managing this complexity at scale requires **dedicated tooling that abstracts the distributed training infrastructure** from data scientists, who need to focus on **model development**.

#### Kubeflow Trainer

- **[Kubeflow Trainer](https://www.kubeflow.org/docs/components/trainer/)** is a component of the [Kubeflow](https://www.kubeflow.org/) ecosystem designed specifically for **managing the scaling and distribution** of LLM fine-tuning.

- The Kubeflow project aims to be the **foundation for AI platforms on Kubernetes** and is evolving from its origins in **predictive AI** to support **generative AI workloads**. Another component, the **Kubeflow Model Registry**, was introduced earlier in [Kubeflow Model Registry](#kubeflow-model-registry).

##### Two personas, two APIs

- Kubeflow Trainer's sole purpose is to **manage the Kubernetes building blocks** required to **configure, deploy, and scale long-running training jobs**.

The project designs its API for **two different personas**:

- the **platform administrator**, who configures the cluster and available resources via a **`TrainingRuntime`**
- the **data scientist / AI engineer**, who submits the training job using a **`TrainJob`**

Since these roles have different skills and tools, Kubeflow Trainer provides a **[Python Kubeflow SDK](https://github.com/kubeflow/sdk)** that **abstracts the creation of the `TrainJob`**, so the data scientist does not need to interact directly with Kubernetes resources.

![Kubeflow Trainer architecture](<assets/Kubeflow Trainer architecture.png>)

**Figure 6-7. Kubeflow Trainer architecture**

##### `TrainingRuntime` and `ClusterTrainingRuntime`

**`TrainingRuntime`** (or **`ClusterTrainingRuntime`** for cluster-wide configuration) is **equivalent to KServe's `ServingRuntime`** described in [KServe](#kserve). It's a **template** that declares the **availability of a runtime**, such as PyTorch, including its container image and other options.

- a **`TrainingRuntime`** is visible **only in the namespace** where you create it; `TrainJobs` must be in the same namespace to use it
- a **`ClusterTrainingRuntime`** is **visible to the entire cluster**

Kubeflow Trainer supports **multiple frameworks for distributed training**:

- **PyTorch**
- **DeepSpeed**
- **MLX**
- **MPI**

Because of this **multiframework design**, a `TrainingRuntime` requires a mandatory **`trainer.kubeflow.org/framework`** label. The SDK uses this label to apply the **correct configuration** for the specified framework (e.g., `torch` for PyTorch) and its trainer.

##### `BuiltinTrainer` vs `CustomTrainer`

The **trainer** represents the library that uses the framework to **define and perform the training job**. It can be one of two types:

- **`BuiltinTrainer`** — like **[TorchTune](https://github.com/meta-pytorch/torchtune)**, provides a **predefined training script** for common use cases like LLM fine-tuning, requiring only parameters for the input dataset and LoRA configuration. **Less flexible**, but **easier to start with**
- **`CustomTrainer`** — gives the user **full control** by allowing them to define a **Python function** containing the entire training process. **Maximum flexibility** for the data scientist, while the administrator only needs to define the `TrainingRuntime` with the compatible framework

##### `TrainJob` → `JobSet` → Kubernetes Jobs

The **`TrainJob`** object defines the **training code** and references a **training runtime**. As mentioned before, the **SDK simplifies the configuration** so data scientists don't need to write it manually.

Once the `TrainJob` is created, the **Kubeflow Trainer controller merges it with the `TrainingRuntime`** to produce a **`JobSet`** and the corresponding **Kubernetes Jobs**.

A [**`JobSet`**](https://jobset.sigs.k8s.io/docs/overview/) is a **Kubernetes custom resource** that represents a **group of Kubernetes Jobs**. It comes from a standalone **[JobSet project](https://jobset.sigs.k8s.io/)** that aims to **unify the API** for deploying **High-Performance Computing (HPC)** and **AI/ML training workloads** on Kubernetes.

##### Example 6-3. Installing Kubeflow Trainer

The Kubeflow Trainer installation is straightforward like for any other Kubernetes controller:

```bash
export VERSION=v2.1.0
export URL="https://github.com/kubeflow/trainer.git/manifests/overlays"
kubectl apply --server-side -k "${URL}/manager?ref=${VERSION}"
kubectl apply --server-side -k "${URL}/runtimes?ref=${VERSION}"
```

What to notice:

- **`VERSION=v2.1.0`** — replace with the version to install
- the Kubeflow Trainer project provides a **built-in set of `ClusterTrainingRuntimes`** to simplify the getting-started experience
- in production, **administrators will define their own curated list of runtimes**

##### Example 6-4. `ClusterTrainingRuntime`

Kubeflow Trainer provides a set of built-in `ClusterTrainingRuntimes`, but they are **optional**. You can skip this specific installation step and **replace the built-in runtimes with one or more custom runtimes**:

```yaml
apiVersion: trainer.kubeflow.org/v1alpha1
kind: ClusterTrainingRuntime
metadata:
  name: my-torch-distributed-runtime
  labels:
    trainer.kubeflow.org/framework: torch
spec:
  mlPolicy:
    numNodes: 1
    torch:
      numProcPerNode: auto
  template:
    spec:
      replicatedJobs:
        - name: node
          template:
            metadata:
              labels:
                trainer.kubeflow.org/trainjob-ancestor-step: trainer
            spec:
              template:
                spec:
                  containers:
                    - name: node
                      image: pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime
```

What to notice:

- **`kind: ClusterTrainingRuntime`** — replace with **`TrainingRuntime`** to create a **namespace-scoped** training runtime
- **`metadata.name: my-torch-distributed-runtime`** — the data scientist uses this name to **select the desired runtime** for their job
- **`trainer.kubeflow.org/framework: torch`** — this label is used by the **SDK** to guide the configuration of the `TrainJob`
- **`mlPolicy.numNodes: 1`** — the spec can define default values for most of the values; for example, this means the job can only use **one node**
- **`image: pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime`** — the administrator might want to control the image used in the cluster by replacing this value with a customized image. The image is **GPU-specific**, so in this case it is for **NVIDIA CUDA**

##### Example 6-5. Trainer function using Hugging Face TRL as a `CustomTrainer`

With the cluster configured and the `TrainingRuntime` available, the platform administrator's work is done. The data scientist can now focus on creating the **training job**:

```python
def my_custom_trainer(**kwargs):
    from datasets import load_dataset
    from transformers import AutoTokenizer, set_seed
    from trl import SFTTrainer

    # It is not mandatory to set a fixed seed but it is useful for reproducibility
    set_seed(kwargs["seed"])

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        ...,    # kwargs[...]
        use_fast=True
    )

    # Load datasets
    train_dataset = load_dataset(
        ...,    # kwargs[...]
    )

    # Initialize Trainer
    trainer = SFTTrainer(
        model=...,
        args=...,
        train_dataset=train_dataset,
        eval_dataset=...,
        peft_config=...,
        processing_class=tokenizer,
    )

    trainer.train()

    trainer.save_model(
        ...,    # kwargs[...]
    )
```

What to notice:

- the **custom trainer function must be self-contained**, so the **`import` must be part of the body**. This example is based on Hugging Face libraries: [`datasets`](https://github.com/huggingface/datasets) for the training dataset (and optionally the evaluation dataset), [`transformers`](https://github.com/huggingface/transformers) for the tokenizer, and [`trl`](https://github.com/huggingface/trl) for the actual trainer class. There is **no Kubeflow Trainer-specific code** here; the function is a **plain Python train function** that can be directly invoked
- **`AutoTokenizer.from_pretrained(..., use_fast=True)`** — the tokenizer is related to the model that is fine-tuned. It is important to use a **fast tokenizer** that works concurrently to avoid slowdown of the training process
- **`train_dataset = load_dataset(...)`** — contains the new knowledge that the model should learn during fine-tuning. It can be a publicly available dataset, but most likely it will be a **custom one**
- **`SFTTrainer(...)`** — the initialization is equivalent to the previous example. This is where you **select the model**, specify the **datasets**, and configure the **PEFT technique** (e.g., `LoraConfig`)
- **`trainer.train()`** — initializes the training process. Hardware configurations such as **number of GPUs and workers** are **not specified here**; instead, you define them when creating the job (see Example 6-6)

> **NOTE — SDK function serialization**
>
> - When you call `client.train(func=my_custom_trainer)`, the **SDK serializes your Python function** and **embeds it into the `TrainJob` custom resource**. The `TrainingRuntime`'s **base container image** (preinstalled with PyTorch, Transformers, PEFT) **deserializes and executes your function** at runtime.
>
> - This **differs from traditional Kubernetes workflows**: you **never build or push custom images** — just **rerun the SDK command** when you modify your function.
>
> - The trade-off is that the **base image must already contain all your dependencies**, and your function must be **serializable** (imports must reference installed packages, **no complex closures**).

##### Example 6-6. Create `TrainJob` via Kubeflow SDK

With the training logic and configuration defined in the trainer function, you can now create the `TrainJob` using the **Kubeflow Python SDK**:

```python
from kubeflow.trainer import CustomTrainer, TrainerClient

client = TrainerClient()

torch_runtime = client.get_runtime("my-torch-distributed-runtime")

job_name = client.train(
    trainer=CustomTrainer(
        # The custom trainer function is injected here with its parameters
        func=my_custom_trainer,
        func_args=...,      # load_args()
        num_nodes=8,
        resources_per_node={
            "cpu": 4,
            "memory": "64Gi",
            "nvidia.com/gpu": 1,
        },
    ),
    runtime=torch_runtime,
)

client.wait_for_job_status(name=job_name, status={"Running"})
_ = client.get_job_logs(job_name, follow=True)

# It is possible to get all the steps and the status for each of them
# steps = client.get_job(name=job_name).steps

# client.delete_job(job_name)
```

What to notice:

- a **`CustomTrainer`** is created using the custom function defined in Example 6-5, and the **`TrainerClient`** submits the `TrainJob`
- **`num_nodes=8` + `resources_per_node`** — hardware requirements are specified **during job submission**. The values are **directly related to the size of the model and the type of tuning** you perform. In this example, the value has been used to customize a **Meta-Llama-3.1-8B-Instruct** model using **PEFT LoRA**
- **`wait_for_job_status(... status={"Running"})`** — the client can wait for a specific job status. This is a **blocking call**. You can also fetch **logs** or configure the use of **[TensorBoard](https://www.tensorflow.org/tensorboard)** — a visualization toolkit originally from the TensorFlow project that is now compatible with multiple libraries, including PyTorch
- **`client.delete_job(job_name)`** — while you can delete the job at any time, even while it's running, this action also **removes the `TrainJob` object** and its associated metadata from Kubernetes. If you're not using external experiment tracking, consider **preserving completed jobs** to maintain a record of training runs

> **SOME YAML MAGIC**
>
> A training job like the one in Example 6-6 requires **many parameters, more than 10**. If the job creation code runs **inside a [Jupyter Notebook](https://jupyter.org/)**, maybe using the **[Kubeflow Notebooks](https://www.kubeflow.org/docs/components/notebooks/overview/)** component, it is possible to **easily configure all the parameters** using the [**`yamlmagic`**](https://github.com/bollwyvl/yamlmagic) library.
>
> This Python module can be installed in a notebook via `pip install yamlmagic` and loaded via `%load_ext yamlmagic`; after that, it is possible to initialize a variable, like `my_params`, using a code block that begins with `%%yaml my_params`. Each row of the block after this first line is parsed as YAML and `my_params` becomes a **Python dictionary** ready to be used.
>
> ###### Example 6-7. Use `yamlmagic` in Jupyter Notebooks for training configuration
>
> ```python
> # In a Jupyter Notebook cell
> %load_ext yamlmagic
>
> %%yaml training_config
> model_name: meta-llama/Llama-3.2-3B
> dataset: openai/gsm8k
> num_epochs: 3
> learning_rate: 2.0e-4
> output_dir: /mnt/models/llama-gsm8k
>
> # Now use the config with Kubeflow SDK
> from kubeflow.trainer import TrainingClient
>
> client = TrainingClient()
> client.train(
>     name="llama-math-tuning",
>     model=training_config["model_name"],
>     dataset=training_config["dataset"],
>     num_epochs=training_config["num_epochs"],
>     learning_rate=training_config["learning_rate"],
>     output_dir=training_config["output_dir"]
> )
> ```

##### Example 6-8. Merge LoRA adapter with the base model

In the LoRA example, the training procedure **doesn't produce a new, full model**. Instead, each saved checkpoint is a **LoRA adapter** that can be **dynamically composed with the base model at runtime**. This enables the **efficient serving of multiple tuned models**, as described in Figure 6-5.

While this is **not the best approach for efficient serving**, it can be useful **for testing purposes** to **merge the LoRA adapter with the base model** to create a new, standalone model:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained(
    ...,
    device_map="cuda"
)
finetuned_path = "/opt/app-root/Meta-Llama-3.1-8B-Instruct/checkpoint-100/"

model = PeftModel.from_pretrained(base_model, finetuned_path)
merged_model = model.merge_and_unload()
merged_model.save(...)
```

What to notice:

- **`AutoModelForCausalLM.from_pretrained(..., device_map="cuda")`** — the base model must be loaded first. The **`device_map` parameter** makes the model directly **load on the GPU**
- **`finetuned_path = "/opt/.../checkpoint-100/"`** — it is necessary to have the path where the **LoRA-tuned model is stored**. After every training epoch a **new checkpoint** (aka model candidate) is created; in this example, **checkpoint number 100** is selected
- **`merged_model = model.merge_and_unload()`** — after the base model and the fine-tuned layer are loaded together, it is possible to **merge** and obtain the new model using the **`merge_and_unload()`** method

##### Storage and operational considerations

The **checkpoint paths** shown (like `/opt/app-root/Meta-Llama-3.1-8B-Instruct/checkpoint-100/`) require **persistent storage infrastructure** to survive **beyond the ephemeral training job lifecycle**.

From a platform perspective, scheduling these **long-running, resource-intensive workloads** requires **additional optimization** to ensure:

- **fair cluster usage**
- **prevention of GPU underutilization**

One significant challenge is **gang scheduling**: distributed workloads often require the system to **deploy all its pods simultaneously** to run correctly. This is an **"all-or-nothing" semantic**.

The experience for the **data scientist is simpler**, as the Kubeflow ecosystem allows them to **focus on the model customization lifecycle**, with **limited awareness** of the underlying Kubernetes platform.

> **TIP — Kubeflow ecosystem for end-to-end MLOps**
>
> The Kubeflow project includes numerous components to support the **entire MLOps or LLMOps lifecycle**:
>
> - the **Kubeflow Model Registry** ([Kubeflow Model Registry](#kubeflow-model-registry)) — model metadata management
> - **Kubeflow Trainer** — distributed training jobs (covered here)
>
> Data scientists can develop and manage the Python code included in the fine-tuning example by leveraging **two other Kubeflow components**:
>
> - **[Kubeflow Notebooks](https://www.kubeflow.org/docs/components/notebooks/overview/)** — manages the infrastructure for **web-based IDEs like Jupyter**, making it easy for data scientists to **self-provision** an environment and experiment with the Kubeflow Trainer SDK
> - **[Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/overview/)** — after experimenting and defining the training job, a data scientist can use Kubeflow Pipelines to **convert the notebook into a reproducible pipeline**. This allows the logic to be **executed multiple times** for retraining the model, either by extracting the code into distinct steps or by **directly incorporating the notebook** into the pipeline

##### Orchestration vs. distribution strategy: where does FSDP live?

A natural follow-up after the TRL example: *if I want **FSDP** (or DDP, DeepSpeed, Accelerate), where does that code actually go?* The answer is that the **FSDP / PyTorch Distributed logic usually lives inside the `CustomTrainer` function itself**, exactly like the Hugging Face TRL trainer in Example 6-5.

It helps to keep **two distinct layers** separate in your head:

```text
Kubeflow Trainer layer (orchestration):
- creates the TrainJob
- chooses the TrainingRuntime
- produces the JobSet / Kubernetes Jobs
- allocates nodes, CPU, memory, GPUs
- launches the distributed workers

Your trainer function layer (training strategy):
- loads the model and dataset
- initializes PyTorch distributed
- applies FSDP / DDP / DeepSpeed / Accelerate / TRL
- runs the training loop
- saves checkpoints / the final model
```

So **Kubeflow Trainer handles the *orchestration***, while **FSDP handles the *actual distributed-training strategy***.

A minimal sketch of the strategy layer — note how all the distributed mechanics are *inside* the function:

```python
def my_fsdp_trainer(**kwargs):
    import os
    import torch
    import torch.distributed as dist
    from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
    from torch.utils.data.distributed import DistributedSampler

    dist.init_process_group(backend="nccl")

    local_rank = int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(local_rank)

    model = build_model(...)
    model.cuda()

    model = FSDP(model)

    dataset = build_dataset(...)
    sampler = DistributedSampler(dataset)

    dataloader = torch.utils.data.DataLoader(
        dataset,
        sampler=sampler,
        batch_size=...,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=...)

    for epoch in range(...):
        sampler.set_epoch(epoch)

        for batch in dataloader:
            loss = model(**batch).loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

    if dist.get_rank() == 0:
        save_model_or_checkpoint(...)
```

The **SDK side** then only declares *how much hardware* to use — the same `num_nodes` / `resources_per_node` knobs from Example 6-6:

```python
job_name = client.train(
    trainer=CustomTrainer(
        func=my_fsdp_trainer,
        func_args={...},
        num_nodes=8,
        resources_per_node={
            "cpu": 4,
            "memory": "64Gi",
            "nvidia.com/gpu": 1,
        },
    ),
    runtime=torch_runtime,
)
```

The dividing line is worth memorizing:

```text
num_nodes / resources_per_node  → Kubernetes-side resource allocation
FSDP / DDP / DeepSpeed code      → training-side distribution logic
```

Inside `CustomTrainer` you can swap in **any** distribution strategy:

```text
Pure PyTorch FSDP
PyTorch DDP
Hugging Face Trainer with FSDP args
Hugging Face Accelerate
DeepSpeed
TRL SFTTrainer with an FSDP/DeepSpeed config
a fully custom training loop
```

Whichever you pick, the **main requirements** stay the same:

```text
the TrainingRuntime image must contain your dependencies
the runtime must launch the distributed processes correctly
your function must be serializable
your code must read the environment variables the runtime provides
checkpoints must be saved to shared/object storage, not only local disk
```

> **In short:** **FSDP goes inside the `CustomTrainer` function** (or inside whatever library you call from it). Kubeflow Trainer *starts and coordinates* the distributed job; your trainer code *decides* whether the job uses FSDP, DDP, DeepSpeed, TRL, Accelerate, or something else.

##### Example — Self-contained FSDP `CustomTrainer`

Here is a more complete, **self-contained `CustomTrainer` function** that uses **PyTorch FSDP** for a causal-LM fine-tuning workload. It assumes the Kubeflow Trainer runtime launches the distributed workers and provides the usual env vars (`LOCAL_RANK`, `RANK`, `WORLD_SIZE`, `MASTER_ADDR`, `MASTER_PORT`):

```python
def my_fsdp_trainer(**kwargs):
    """
    Example CustomTrainer function for Kubeflow Trainer using PyTorch FSDP.

    Expected kwargs:
      model_name: str
      dataset_name: str
      text_column: str
      output_dir: str
      epochs: int
      batch_size: int
      lr: float
      max_length: int
      seed: int
      min_num_params: int
    """

    import os
    from functools import partial

    import torch
    import torch.distributed as dist
    from torch.utils.data import DataLoader
    from torch.utils.data.distributed import DistributedSampler

    from datasets import load_dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        DataCollatorForLanguageModeling,
        set_seed,
    )

    from torch.distributed.fsdp import (
        FullyShardedDataParallel as FSDP,
        MixedPrecision,
        StateDictType,
        FullStateDictConfig,
    )
    from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy

    # -----------------------------
    # 1. Read config
    # -----------------------------
    model_name = kwargs["model_name"]
    dataset_name = kwargs["dataset_name"]
    text_column = kwargs.get("text_column", "text")
    output_dir = kwargs.get("output_dir", "/tmp/fsdp-model")

    epochs = int(kwargs.get("epochs", 1))
    batch_size = int(kwargs.get("batch_size", 1))
    lr = float(kwargs.get("lr", 2e-5))
    max_length = int(kwargs.get("max_length", 1024))
    seed = int(kwargs.get("seed", 42))
    min_num_params = int(kwargs.get("min_num_params", 1_000_000))

    set_seed(seed)

    # -----------------------------
    # 2. Initialize distributed
    # -----------------------------
    dist.init_process_group(backend="nccl")

    local_rank = int(os.environ["LOCAL_RANK"])
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])

    torch.cuda.set_device(local_rank)
    device = torch.device("cuda", local_rank)

    is_main_process = rank == 0

    # -----------------------------
    # 3. Load tokenizer and dataset
    # -----------------------------
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        use_fast=True,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    raw_dataset = load_dataset(dataset_name)

    train_dataset = raw_dataset["train"]

    def tokenize_fn(examples):
        return tokenizer(
            examples[text_column],
            truncation=True,
            max_length=max_length,
            padding=False,
        )

    tokenized_dataset = train_dataset.map(
        tokenize_fn,
        batched=True,
        remove_columns=train_dataset.column_names,
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    sampler = DistributedSampler(
        tokenized_dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=True,
        seed=seed,
    )

    dataloader = DataLoader(
        tokenized_dataset,
        batch_size=batch_size,
        sampler=sampler,
        collate_fn=data_collator,
        drop_last=True,
    )

    # -----------------------------
    # 4. Load model
    # -----------------------------
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    )

    model.config.use_cache = False
    model.to(device)

    # -----------------------------
    # 5. Configure FSDP
    # -----------------------------
    auto_wrap_policy = partial(
        size_based_auto_wrap_policy,
        min_num_params=min_num_params,
    )

    mixed_precision = MixedPrecision(
        param_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        reduce_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        buffer_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    )

    model = FSDP(
        model,
        auto_wrap_policy=auto_wrap_policy,
        mixed_precision=mixed_precision,
        device_id=device,
        use_orig_params=True,
    )

    # Important: create the optimizer AFTER wrapping with FSDP
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=lr,
    )

    # -----------------------------
    # 6. Training loop
    # -----------------------------
    model.train()

    for epoch in range(epochs):
        sampler.set_epoch(epoch)

        for step, batch in enumerate(dataloader):
            batch = {
                key: value.to(device)
                for key, value in batch.items()
                if torch.is_tensor(value)
            }

            outputs = model(**batch)
            loss = outputs.loss

            loss.backward()
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)

            if is_main_process and step % 10 == 0:
                print(
                    f"epoch={epoch} step={step} loss={loss.item():.4f}",
                    flush=True,
                )

    # -----------------------------
    # 7. Save full model checkpoint
    # -----------------------------
    dist.barrier()

    save_policy = FullStateDictConfig(
        offload_to_cpu=True,
        rank0_only=True,
    )

    with FSDP.state_dict_type(
        model,
        StateDictType.FULL_STATE_DICT,
        save_policy,
    ):
        state_dict = model.state_dict()

    if is_main_process:
        os.makedirs(output_dir, exist_ok=True)

        # Save model weights
        unwrapped_model = model.module
        unwrapped_model.save_pretrained(
            output_dir,
            state_dict=state_dict,
        )

        # Save tokenizer
        tokenizer.save_pretrained(output_dir)

        print(f"Model saved to {output_dir}", flush=True)

    dist.barrier()

    # -----------------------------
    # 8. Cleanup
    # -----------------------------
    dist.destroy_process_group()
```

The **hardware part stays outside the function**, in the SDK call:

```python
job_name = client.train(
    trainer=CustomTrainer(
        func=my_fsdp_trainer,
        func_args={
            "model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "dataset_name": "your_dataset_name",
            "text_column": "text",
            "output_dir": "/mnt/checkpoints/my-fsdp-model",
            "epochs": 1,
            "batch_size": 1,
            "lr": 2e-5,
            "max_length": 2048,
            "seed": 42,
            "min_num_params": 1_000_000,
        },
        num_nodes=8,
        resources_per_node={
            "cpu": 4,
            "memory": "64Gi",
            "nvidia.com/gpu": 1,
        },
    ),
    runtime=torch_runtime,
)
```

What to notice:

- the **optimizer is created *after* the `FSDP(...)` wrap** — FSDP flattens/sharded parameters, so an optimizer built on the unwrapped parameters would not see the sharded state
- **`bf16` is preferred when supported**, falling back to `fp16`, for both the model dtype and the FSDP `MixedPrecision` config
- the **full-checkpoint save** uses `FULL_STATE_DICT` with `offload_to_cpu=True` and `rank0_only=True`, so only **rank 0** gathers and writes the consolidated weights
- **`dist.barrier()`** before and after saving keeps all ranks in step around the checkpoint

> **Practical note:** `output_dir` should usually be a **mounted PVC, NFS path, S3-compatible mount, or other persistent/shared storage** — *do not* rely on the container's temporary local disk for real training checkpoints, since it disappears with the ephemeral job.

##### Where do `LOCAL_RANK`, `RANK`, `WORLD_SIZE`, … come from?

These variables are **not defined inside your trainer function**. They are **injected by the distributed launcher/runtime** that starts your training processes. In this stack the chain looks roughly like:

```text
Kubeflow Trainer TrainJob
  → TrainingRuntime / ClusterTrainingRuntime
  → JobSet
  → Kubernetes Jobs/Pods
  → launcher command (usually torchrun / the PyTorch distributed launcher)
  → your CustomTrainer function
```

The environment variables originate in that **launcher layer**.

**The main variables:**

```text
LOCAL_RANK   = GPU/process index within the current node
RANK         = global process index across all nodes
WORLD_SIZE   = total number of distributed processes
MASTER_ADDR  = address of the leader/master process
MASTER_PORT  = port used for the distributed rendezvous
```

For example, with **2 nodes and 4 GPUs per node**:

```text
WORLD_SIZE = 8

Node 1:
  process 0: RANK=0, LOCAL_RANK=0
  process 1: RANK=1, LOCAL_RANK=1
  process 2: RANK=2, LOCAL_RANK=2
  process 3: RANK=3, LOCAL_RANK=3

Node 2:
  process 4: RANK=4, LOCAL_RANK=0
  process 5: RANK=5, LOCAL_RANK=1
  process 6: RANK=6, LOCAL_RANK=2
  process 7: RANK=7, LOCAL_RANK=3
```

Notice that **`RANK` is global** (unique across the whole job) while **`LOCAL_RANK` restarts at 0 on each node** — which is exactly why `LOCAL_RANK` is the one you pass to `torch.cuda.set_device(...)`.

**Where are they actually set?** For a local/manual run, `torchrun` sets them:

```bash
torchrun \
  --nnodes=8 \
  --nproc-per-node=1 \
  --node-rank=$NODE_RANK \
  --master-addr=$MASTER_ADDR \
  --master-port=$MASTER_PORT \
  train.py
```

In **Kubeflow Trainer you normally don't write that command by hand** — the **`TrainingRuntime` template and the Trainer controller** create the Kubernetes Jobs and launch the workers with the correct distributed environment. Your `CustomTrainer` just **reads** the values:

```python
local_rank = int(os.environ["LOCAL_RANK"])
rank = int(os.environ["RANK"])
world_size = int(os.environ["WORLD_SIZE"])
```

> **In short:** the variables are produced by the **distributed launcher** — directly by `torchrun` for local/manual runs, and *indirectly* by `TrainJob + TrainingRuntime + JobSet + PyTorch runtime launcher` under Kubeflow Trainer. Your trainer function simply **assumes they already exist**.

##### Why Kubernetes / Kubeflow Trainer instead of just `torchrun`?

**PyTorch Distributed (FSDP/DDP) owns the training *algorithm*; Kubernetes and Kubeflow Trainer own *running that algorithm reliably on real infrastructure*.**

You *can* run distributed training with PyTorch alone:

```bash
torchrun --nnodes=4 --nproc-per-node=8 train.py
```

…but then **you** have to answer all the infrastructure questions yourself:

```text
Which machines are available?
Which machines have free GPUs?
How do I reserve CPU/RAM/GPU resources?
How do I start the same job on all nodes?
How do the nodes discover each other?
What happens if a pod/process fails?
Where are logs collected?
Where are checkpoints stored?
How do I track job status?
How do I stop two users from grabbing the same GPUs?
How do admins control approved images/runtimes?
```

PyTorch does **not** solve those cluster-management problems — it **assumes the processes are already started correctly and can communicate** with one another.

Kubernetes supplies the **infrastructure layer**:

```text
scheduling
resource allocation
GPU assignment
pod lifecycle
networking
secrets/configs
volumes
logs
restart policies
namespace isolation
multi-user cluster sharing
```

And **Kubeflow Trainer adds a training-specific layer** on top of Kubernetes:

```text
TrainJob: user-facing training job API
TrainingRuntime: admin-defined training environment
JobSet/Kubernetes Jobs: actual distributed execution
SDK: Python interface for data scientists
```

So the division of responsibility is:

```text
PyTorch FSDP/DDP/DeepSpeed:
  "How should the model be trained across processes/GPUs?"

Kubernetes:
  "Where do those processes run — with what resources, networking, storage, and lifecycle?"

Kubeflow Trainer:
  "How do we package distributed training as a clean, repeatable, platform-managed job?"
```

> For a **small experiment**, PyTorch alone is plenty. On an **enterprise GPU cluster**, Kubernetes + Kubeflow Trainer earn their keep by turning training from a manual, server-by-server operation into a **repeatable, schedulable, observable, multi-user platform workflow**.

#### Other Frameworks

While Kubeflow Trainer provides a comprehensive solution for most use cases, the ecosystem offers **several alternatives** worth considering.

The Kubeflow Trainer project takes a **Kubernetes-native approach** to managing the lifecycle of distributed training jobs, allowing both platform administrators and data scientists to work with their preferred tools.

While Kubeflow Trainer and **Hugging Face's TRL** offer a robust, platform-centric solution for distributed training on Kubernetes, several other projects and libraries provide **specialized tools** to optimize the fine-tuning process, particularly focusing on **efficiency, speed, and resource management** for LLMs:

- **DeepSpeed**
- **Unsloth**
- **Ray with KubeRay**

##### DeepSpeed

**[DeepSpeed](https://www.deepspeed.ai/)** is a **deep learning optimization library** that **wraps PyTorch** to simplify the management of training jobs.

Using DeepSpeed with Kubeflow Trainer is **very similar to the previous example**:

- select a **DeepSpeed-compatible `TrainingRuntime`** (such as the default DeepSpeed distributed runtime)
- **update the custom trainer logic**

###### Example 6-9. Trainer function using DeepSpeed

```python
def my_custom_deepspeed_trainer(**kwargs):
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    from datasets import load_dataset
    from torch.utils.data import DataLoader
    from torch.utils.data.distributed import DistributedSampler
    import deepspeed

    # Initialize DeepSpeed distributed training
    deepspeed.init_distributed(dist_backend="nccl")
    local_rank = int(kwargs["local_rank"])

    # Set seed for reproducibility
    set_seed(kwargs["seed"])

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(..., use_fast=True)   # kwargs[...]

    # Load datasets
    train_dataset = load_dataset(...).with_format("torch")      # kwargs[...]

    train_loader = DataLoader(
        dataset, batch_size=16, sampler=DistributedSampler(dataset)
    )

    # DeepSpeed configuration
    ds_config = {
        ...,    # kwargs[...]
    }

    # Initialize DeepSpeed engine.
    model_engine, _, _, _ = deepspeed.initialize(
        model=model,
        config=ds_config,
        model_parameters=model.parameters(),
    )

    num_epoch = int(...)    # kwargs[...]
    for epoch in range(num_epoch):
        for batch_idx, batch in enumerate(train_loader):
            for key in batch.keys():
                batch[key] = batch[key].to(local_rank)
            outputs = model_engine(batch)
            loss = outputs.loss

            model_engine.backward(loss)
            model_engine.step()


    model_engine.module.save_pretrained(...)   # kwargs[...]
    tokenizer.save_pretrained(...)      # kwargs[...]
```

What to notice:

- **`deepspeed.init_distributed(dist_backend="nccl")`** — you must initialize the distributed training. The value **`nccl`** is used for **NVIDIA CUDA hardware**, and **`local_rank`** is an environment variable provided as an argument to the training script
- **`load_dataset(...).with_format("torch")`** — the example loads the dataset using the **Hugging Face `datasets` library**, and it can be **easily converted to a PyTorch dataset**
- **`deepspeed.initialize(...)`** — the engine initialization returns **multiple variables**, but for this example only the **`model_engine`** is needed
- in this example, the **training loop is explicit**, showing the computation of the **forward pass, loss, and backward pass**

##### Ray

While Kubeflow Trainer's flexibility is sufficient for most model customization techniques, it is **not the only framework** for distributed computation on Kubernetes. The **[Ray project](https://www.ray.io/)** is a valid alternative.

Ray provides an entire ecosystem of components for AI platforms and was previously introduced in [Ray Serve and KubeRay](#ray-serve-and-kuberay). Its core concepts, like the **`RayCluster`** (Figure 1-5), are **generic** and apply to the **training space as well**.

Ray's integration with Kubernetes is managed by **KubeRay**, which provides the necessary APIs:

- deploy a **`RayCluster`**
- submit a **`RayJob`** to perform a **long-running, multinode computation** for model customization

The process is **similar to the Kubeflow Trainer example**:

- create a Python script with the training logic
- instantiate a `RayCluster` (a step **not required by Kubeflow Trainer**)
- deploy the job

###### Ray vs Kubeflow Trainer — code delivery differences

Code delivery **differs** between the two:

- **Kubeflow Trainer** — **serializes and injects Python functions** directly
- **Ray** — requires **training scripts packaged in container images** or accessible via **remote locations** (Git repos, mounted volumes), with the `RayJob` CR **referencing the script path** rather than embedding code

This means that:

- **Ray requires container rebuilds** for code changes — better suited for teams already using the Ray ecosystem
- **Kubeflow Trainer's immediate re-execution** supports **rapid experimentation**

A full example of using **DeepSpeed and Ray** to fine-tune an LLM can be found in the **[opendatahub-io repository](https://github.com/opendatahub-io/distributed-workloads/tree/main/examples/ray-finetune-llm-deepspeed)**, which uses the **[CodeFlare SDK](https://github.com/project-codeflare/codeflare-sdk)** to programmatically configure KubeRay resources.

> **WARNING — Don't confuse [Ray Tune](https://docs.ray.io/en/latest/tune/index.html) with LLM model tuning**
>
> **Ray Tune** is a module designed for **hyperparameter tuning and optimization**, which mainly applies to **predictive AI**.
>
> The equivalent project in the Kubeflow community is **[Kubeflow Katib](https://www.kubeflow.org/docs/components/katib/overview/)**.
>
> While not designed for model customization, it is still possible to use Ray Tune with the **Hugging Face `transformers` library** for hyperparameter optimization techniques like **[Population Based Training (PBT)](https://docs.ray.io/en/latest/tune/examples/pbt_guide.html)**, as described in [this example](https://docs.ray.io/en/latest/tune/examples/pbt_transformers.html).

##### Unsloth

The **[Unsloth project](https://github.com/unslothai/unsloth)** specifically targets the **LLM customization process** with the goal to make it **easy, fast, and with limited hardware requirements**. It has a **large and active community**.

While **not designed for large-scale infrastructure on Kubernetes**, it is **very easy to start with**, as it can be **installed locally as a standard Python package**:

```bash
pip install unsloth
```

In this respect, it can be seen as the **fine-tuning equivalent of local inference projects** like **[Ollama](https://ollama.com/)** or [**`llama.cpp`**](https://github.com/ggml-org/llama.cpp). Although designed as a local library, it is possible to deploy it on Kubernetes using the **[AIKit project](https://github.com/sozercan/aikit)** - [see documentation](https://kaito-project.github.io/aikit/docs/).

#### Encode this

- **Training networking is the real scaling bottleneck — gigabytes/sec across GPUs every step**
- **FSDP2 + Liger Kernel + FlashAttention are the optimization vocabulary for training**
- **Kubeflow Trainer separates platform admin (`TrainingRuntime`) from data scientist (`TrainJob` via SDK)**
- **`TrainJob` → `JobSet` → Kubernetes Jobs is the controller chain**
- **`BuiltinTrainer` = quick start; `CustomTrainer` = full Python function flexibility**
- **SDK serializes Python functions into `TrainJob` — no custom image build/push needed**
- **DeepSpeed = explicit training-loop control inside a custom trainer**
- **Ray + KubeRay = alternative to Kubeflow Trainer; script-based delivery (vs serialized functions)**
- **Don't confuse Ray Tune (hyperparameter search) with LLM model tuning**
- **Unsloth = local-first fine-tuning, K8s-deployable via AIKit**

#### Recall prompt

*Why does Kubeflow Trainer's "serialize and inject Python function" model give data scientists faster iteration than Ray's "container with embedded script" approach?*

[Back to Contents](#contents)

### Customization Lessons Learned

This section explored how to **adapt an existing LLM** to a specific use case on Kubernetes, from prompt-level adjustments to full fine-tuning.

**You often don't need to train**

- **prompt engineering** sets scenario, role, and boundaries
- **context engineering** builds dynamic, multistep input contexts (the foundation of **AI agents**)
- **RAG** injects external knowledge via embeddings + vector DB + similarity search
- these techniques work with **both general-purpose and tuned models**

**When training is the right call**

- **stable, slow-changing domain knowledge** is better embedded in the model than passed via context every request
- **smaller specialized models (SLMs, 8–16B params)** can match or beat larger untuned models at a fraction of the inference cost
- **distillation** transfers a large teacher's behavior into a smaller student

**Two training families**

- **Full fine-tuning** — modifies all parameters; powerful but expensive; needs hundreds of thousands of examples; produces a **distinct model** that needs dedicated GPUs to serve
- **PEFT (Parameter-Efficient Fine-Tuning)** — composes new layers on a **frozen base**; 100–1,000 examples; one base + many adapters served on the same hardware

**LoRA dominates the PEFT space**

- **decomposes** the full weight-update matrix into two **low-rank matrices** (A × B)
- adapters are typically **1–10% of the base model size**
- **X-LoRA** handles MoE; **QLoRA** combines LoRA with quantization
- inference composes the base model + adapters at runtime → strong cost story

**Beyond LoRA**

Advanced techniques (**GRPO**, **DPO**, **distillation**, **model merging**, **reward modeling**, **InstructLab**) are **multistep workflows**, often with **synthetic data**, **multiple dedicated GPU pools**, and **secure inter-component communication**. From a Kubernetes perspective, they look more like **long-running training pipelines** than single training loops.

**Operational lens**

Whatever the technique:

- **dataset preparation is the most expensive step** (curated labeled data)
- **training jobs are long-running, GPU-heavy workloads**
- **serving topology depends on the technique** — full fine-tune = new dedicated deployment, PEFT/LoRA = one base + many adapters
- **secure communication between training components** matters for production workloads

**Running tuning jobs on Kubernetes**

- **Networking is the real scaling bottleneck**: gathering sharded weights across GPUs at every step produces **gigabytes/sec of traffic**; bandwidth is what limits scale, not just GPU count
- **PyTorch is the de facto deep-learning library**; FSDP2 is the most common way to shard a training job across nodes
- **Kubeflow Trainer** separates two personas:
  - **Platform admin** owns `TrainingRuntime` / `ClusterTrainingRuntime` (template like KServe's `ServingRuntime`)
  - **Data scientist** submits a `TrainJob` via the **Kubeflow Python SDK** without touching YAML
- Controller chain: **`TrainJob` + `TrainingRuntime` → `JobSet` → Kubernetes Jobs**
- **`BuiltinTrainer`** (e.g., TorchTune) for quick starts; **`CustomTrainer`** for arbitrary Python functions
- The SDK **serializes the Python function** into the `TrainJob` CR — **no custom image build/push** for code changes (image just needs the deps)
- **Alternative frameworks**: **DeepSpeed** (PyTorch wrapper, explicit loop), **Ray + KubeRay** (script-based, container rebuild for code changes), **Unsloth** (local-first, K8s-deployable via AIKit)
- **Don't confuse Ray Tune (hyperparameter search) with LLM model tuning** — Ray Tune is for predictive AI; Kubeflow Katib is its Kubeflow equivalent

**Training jobs are batch workloads, not services**

Training job management requires **different operational patterns** than inference serving:

- jobs are **batch workloads** with defined completion criteria, **not long-running services**
- resource allocation favors **throughput over latency**
- **checkpoint management** enables recovery from preemption
- **gang scheduling** prevents partial resource allocation from blocking expensive GPU nodes

#### Encode this

- **The cheapest customization is no customization — try prompts and RAG first**
- **Customization wins when knowledge is stable and inference cost matters**
- **PEFT + LoRA = the cost-effective default for most LLM customization on K8s**
- **Full fine-tuning is reserved for cases where partial parameter updates aren't enough**
- **Advanced techniques are multistep K8s pipelines, not one-shot training jobs**
- **Kubeflow Trainer = the Kubernetes-native way to run training jobs without exposing platform plumbing to data scientists**
- **Training jobs are batch + gang-scheduled, not stateless services**

#### Recall prompt

*Given a stable internal knowledge base, 10 GPUs, and a need to serve five fine-tuned variants of one model, which customization technique would you choose and why — and which Kubernetes framework would you reach for to run the training?*

[Back to Contents](#contents)

## High-Value Recall Checklist

Use these prompts for fast review:

- **Model server**: What does a model server do, and how is its API different for predictive vs generative AI?
- **vLLM vs TGI**: When do you pick **vLLM**, and when do you pick **TGI**? What does multi-backend support buy and cost?
- **Edge serving**: Why is **`llama.cpp`** the go-to for laptop/edge inference, and what is **GGUF**?
- **NVIDIA NIM**: What does NIM's curated container + auto backend selection (TensorRT-LLM > vLLM > SGLang) get you?
- **SGLang**: What workloads make **RadixAttention** especially valuable?
- **Controllers**: What problem does a **Model Server Controller** solve that a vanilla Deployment cannot?
- **KServe**: What problem does it solve on Kubernetes?
- **Deployment modes**: When do you choose **Knative**, **Standard**, or **ModelMesh**?
- **Core APIs**: What is the difference between **`ServingRuntime`** and **`InferenceService`**?
- **LLM APIs**: Why was **`LLMInferenceService`** introduced, and how does it compare with `InferenceService` in routing, parallelism, and model size?
- **Operations**: Why should runtime lifecycle and model lifecycle be separated?
- **Ray Serve / KubeRay**: When does the Python-first orchestration of Ray beat Kubernetes-native KServe?
- **GPU discovery**: Why is **GFD** needed alongside **NFD** for Kubernetes GPU clusters?
- **Device plug-ins**: What four functions does the Kubernetes device plug-in framework provide?
- **GPU scheduling**: When do you reach for **`nodeSelector`**, **node affinity**, **taints**, **resource requests**, or **DRA**?
- **DRA**: How does Dynamic Resource Allocation change the model from "how many" to "what kind"?
- **NVIDIA GPU Operator**: Which components does the **`ClusterPolicy`** orchestrate?
- **GPU sharing**: What is the difference between **time slicing**, **MPS**, and **MIG**?
- **MIG strategies**: When do you choose the **single** strategy versus the **mixed** strategy?
- **Diagnostics**: How does running **`nvidia-smi`** inside a pod verify the GPU plumbing?
- **Multi-GPU**: When do you reach for **data parallelism** vs **tensor parallelism** vs **pipeline parallelism**?
- **Interconnect**: Why do **NVLink** and **NVSwitch** matter for tensor parallelism but less for pipeline parallelism?
- **Topology**: When is **multinode multi-GPU** inference unavoidable, and what coordination problems does it bring?
- **NCCL/RDMA**: Why is **RDMA-backed NCCL** important for multinode LLM inference?
- **Optimization**: Which **GPU resource optimizations** matter most for production LLM serving?
- **Model sizes**: Roughly how large is a 7B model in FP16 vs a 70B model? Why does that matter for K8s storage?
- **Weight-only vs self-contained**: Why is a PyTorch `state_dict` insufficient by itself for production inference?
- **"Mostly self-contained"**: Why does no LLM format today qualify as fully self-contained?
- **Portability**: Why are ONNX, GGUF, and Safetensors each useful but incomplete?
- **`tokenizer.json` and `config.json`**: What do these two files contain, and why are they de-facto standards?
- **Safetensors sharding**: What does `model.safetensors.index.json` do, and when do you need sharding?
- **GGUF**: Why is GGUF tied to `llama.cpp`, and why does its quantization focus matter for edge inference?
- **Registry**: Why does a model registry store metadata more often than weights?
- **Model experimentation vs feature stores**: How do these two concepts bracket the model registry's role?
- **Hugging Face**: Why is it the default public discovery platform but not the full production answer?
- **MLflow**: Why is it strong for experimentation but weaker as a Kubernetes-native serving control plane?
- **Kubeflow**: What makes its registry more deeply integrated with Kubernetes workflows?
- **OCI Registry**: Why is storing full model artifacts there different from storing metadata in a model registry?
- **OCI Images**: What are the four main OCI image components?
- **Model access**: What is the difference between download-based storage initialization and direct PVC-backed mounting?
- **`storageUri` scheme**: What changes when you switch from `s3://` to `pvc://` to `oci://`?
- **Production serving**: Why do model evaluation, compression, benchmarking, runtime tuning, autoscaling, startup time, routing, and disaggregated topology need to be treated as one connected system?
- **LLM-aware routing**: Why is round robin often weak for LLM replicas?
- **Disaggregated serving**: Why do distributed KV cache and disaggregated prefill require high-bandwidth networking?
- **LLM creation pipeline**: What is the difference between **pre-training**, **alignment**, and **post-training (customization)**?
- **Prompt vs context engineering**: Where does **RAG** fit, and why is it complementary to fine-tuning rather than a replacement?
- **When to customize**: What kinds of knowledge or behavior justify embedding into the model instead of injecting via RAG every request?
- **Full fine-tuning vs PEFT**: What is the operational cost difference, and why is PEFT easier on a Kubernetes platform?
- **LoRA**: How does LoRA decompose the weight-update matrix, and why does that enable one-base-many-adapters serving?
- **X-LoRA / QLoRA**: What does each variant add on top of vanilla LoRA?
- **Advanced techniques**: Why do **GRPO**, **DPO**, **distillation**, **model merging**, and **InstructLab** look like multideployment K8s pipelines rather than single training jobs?
- **Training networking**: Why does **bandwidth between GPUs** dominate scaling of LLM training, and which technologies (FSDP2, Liger Kernel, FlashAttention) address it?
- **Kubeflow Trainer personas**: How does the **`TrainingRuntime` / `TrainJob` split** mirror KServe's **`ServingRuntime` / `InferenceService`** model?
- **`BuiltinTrainer` vs `CustomTrainer`**: When do you choose each, and what does the Kubeflow SDK do with a `CustomTrainer` function?
- **Kubeflow Trainer vs Ray**: What is the operational difference between **"serialize a Python function into the `TrainJob`"** and **"package the script into a container image"**?
- **Ray Tune trap**: Why is **Ray Tune** *not* what you reach for to fine-tune an LLM, and what is the right Kubeflow equivalent?
- **Training as batch**: Why are tuning jobs **batch workloads with gang scheduling**, and why does that change how you reason about checkpoints and resource allocation?

### One-sentence compression

**KServe operationalizes model serving on Kubernetes, registries operationalize model discovery and governance, OCI-style artifacts improve model distribution, storage access strategy determines how efficiently models reach serving pods, and production LLM serving depends on token-aware evaluation, tuning, scaling, startup optimization, routing, and topology design.**

[Back to Contents](#contents)
