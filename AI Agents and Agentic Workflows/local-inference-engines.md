# Local LLM Inference Engines

Local inference engines load and run open-weight models on hardware you control. They usually provide a CLI, native library, local HTTP API, or a combination of these interfaces.

```text
Application / LangChain / LangGraph
                 |
          SDK or HTTP API
                 |
          Inference engine
                 |
       Model weights + CPU/GPU
```

## Why run models locally?

- **Privacy and offline use:** prompts and retrieved documents can remain on the machine.
- **Control:** choose the model, quantization, context length, CPU/GPU allocation, and generation settings.
- **Predictable marginal cost:** no per-token API charge after hardware and operating costs.
- **Trade-offs:** limited RAM/VRAM, slower or lower-quality models, setup effort, and responsibility for updates, security, and monitoring.

## Engine comparison

| Engine | Best suited for | Main interfaces | Key trade-off |
|---|---|---|---|
| **llama.cpp** | Maximum low-level control, GGUF models, and efficient CPU/GPU or hybrid inference | CLI, C/C++ library, bindings, web UI, OpenAI-compatible server | Flexible and portable, but exposes more build and tuning complexity |
| **Ollama** | Simple local development and model management | CLI, native REST API, Python/JavaScript libraries, supported OpenAI-compatible endpoints | Excellent usability, but abstracts some low-level runtime choices |
| **vLLM** | High-throughput, multi-user GPU serving | Python and OpenAI-compatible HTTP server | Production-oriented performance, but heavier deployment and hardware requirements |
| **llamafile** | Portable distribution with minimal installation | Single executable, CLI, web UI, OpenAI-compatible server | Very easy to distribute; less suitable for managing a large serving fleet |
| **LM Studio** | Desktop model discovery, testing, and local app development | GUI, CLI, Python/TypeScript SDKs, REST, OpenAI- and Anthropic-compatible endpoints | Convenient for exploration; desktop-first unless its headless service is used |
| **LocalAI** | A self-hosted, multi-backend and multimodal API platform | OpenAI-/Anthropic-compatible APIs, web UI, containers | Broad and extensible, but operationally more complex than a single-model runner |
| **GPT4All** | Private desktop chat, local-document Q&A, and lightweight experimentation | Desktop UI, Python SDK, local API | Easy for personal use; not primarily designed for high-throughput production serving |

> **Compatibility is not identity.** “OpenAI-compatible” means that selected request and response shapes are implemented. Endpoint coverage, tool calling, multimodality, sampling parameters, and error behavior still vary by engine and model; test the exact features an application needs.

## Selection guide

- Choose **Ollama** for the simplest CLI-driven local workflow and straightforward LangChain/LangGraph integration.
- Choose **llama.cpp** for direct GGUF control, broad consumer-hardware support, and detailed runtime tuning.
- Choose **vLLM** when concurrent GPU throughput and production serving matter most.
- Choose **LM Studio** or **GPT4All** for a desktop-first graphical experience.
- Choose **llamafile** when a portable, nearly self-contained executable is the priority.
- Choose **LocalAI** when one self-hosted gateway must expose several engines or modalities through familiar APIs.

## What to evaluate before choosing

1. **Model and format support:** architecture, GGUF or native weights, embedding/vision/tool-use support.
2. **Memory:** weight precision or quantization plus KV cache, context length, runtime buffers, and concurrent requests.
3. **Hardware and OS:** CPU instruction set, NVIDIA/AMD/Intel/Apple acceleration, drivers, and platform support.
4. **Workload:** interactive latency versus batch throughput, concurrency, streaming, and model switching.
5. **Integration:** native SDK versus HTTP, API compatibility, structured output, tools, embeddings, and observability.
6. **Operations:** authentication, network binding, isolation, upgrades, monitoring, and model licensing.

## Repository default: Ollama

This repository uses Ollama with the local `gemma4:12b-it-q8_0` model:

```powershell
ollama pull gemma4:12b-it-q8_0
ollama run gemma4:12b-it-q8_0
ollama ps
```

Minimal LangChain configuration:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gemma4:12b-it-q8_0",
    num_ctx=8192,
    num_predict=192,
    temperature=0,
    reasoning=False,
)

print(llm.invoke("Salam! Azərbaycanca qısa cavab ver.").content)
```

## Key takeaway

The engine and model solve different problems: the **model** determines learned capabilities, while the **engine** determines how those weights are loaded, accelerated, configured, and served. Start with Ollama for local development, then move to a lower-level or production-oriented engine only when control, compatibility, or throughput requirements justify it.

## Official references

- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Ollama API and OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)
- [vLLM OpenAI-compatible server](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/)
- [llamafile](https://github.com/mozilla-ai/llamafile)
- [LM Studio local server](https://lmstudio.ai/docs/developer/core/server)
- [LocalAI](https://localai.io/docs/)
- [GPT4All](https://docs.gpt4all.io/)
