# AI Agents & Agentic Workflows

My hands-on learning journey into building AI agents and agentic systems.

This repo is where I work through books, tutorials, and my own experiments while
studying the modern agent stack. All examples are adapted to run against a **local
LLM** instead of paid cloud APIs, so everything here runs offline and free.

## Local Ollama configuration

The local development machine uses Ollama `0.32.5` with an NVIDIA GeForce RTX
5090 Laptop GPU (24 GB dedicated VRAM). The default `gemma4:e4b` tag currently
resolves to this configuration:

| Property | Value |
| --- | --- |
| Architecture | Gemma 4 E4B |
| Parameters | 4.5B effective, 8B including embeddings |
| Weight quantization | `Q4_K_M` |
| Maximum model context | 131,072 tokens (128K) |
| Default allocated context on this GPU | 32,768 tokens (32K) |
| Processor allocation | 100% GPU |

The relatively small VRAM footprint is expected. Gemma 4 E4B uses per-layer
embeddings, and the default Ollama tag stores most model weights at 4-bit
precision. Low VRAM use does not mean layers are being offloaded: the
`PROCESSOR` column from `ollama ps` is the authoritative check.

### Verified default Q4 runtime evidence

The original `gemma4:e4b` run used the default `Q4_K_M` weights and a 32K
context. While the model was loaded, `ollama ps` reported:

```text
NAME          ID              SIZE      PROCESSOR    CONTEXT    UNTIL
gemma4:e4b    c6eb396dbd59    3.4 GB    100% GPU     32768      14 seconds from now
```

The same run produced these Windows Task Manager readings after generation:

| Measurement | Observed value |
| --- | --- |
| Dedicated GPU memory | 6.1 GB / 24.0 GB |
| Shared GPU memory | 6.0 GB / 47.4 GB |
| Total GPU memory | 12.1 GB / 71.4 GB |
| GPU utilization while idle | 0% |
| GPU temperature | 42 C |

This is direct evidence that the quantized model ran with all layers assigned
to the GPU while using substantially less dedicated VRAM than the BF16
variant. The 3.4 GB value is Ollama's loaded runtime allocation, whereas the
6.1 GB Task Manager value is total dedicated GPU memory in use by the system at
that moment. Shared and total GPU-memory readings are also system-wide and
should not be interpreted as Ollama CPU offload.

### Inspect a model and its runtime allocation

Show the stored model's parameter count, maximum context, and weight
quantization:

```cmd
ollama show gemma4:e4b
```

While the model is loaded, run the following in a second terminal to see the
allocated context and CPU/GPU split:

```cmd
ollama ps
```

The three size readings are not directly comparable:

- `ollama list` shows the downloaded model package size.
- `ollama ps` shows the loaded runtime allocation.
- Windows Task Manager shows GPU memory used by Ollama, Windows, and other
  applications.

### Use higher-precision E4B weights

Ollama publishes three useful E4B variants:

| Model tag | Weight precision | Download size |
| --- | --- | --- |
| `gemma4:e4b-it-q4_K_M` | Q4_K_M | 9.6 GB |
| `gemma4:e4b-it-q8_0` | Q8_0 | 12 GB |
| `gemma4:e4b-it-bf16` | BF16 | 16 GB |

Run the BF16 variant to use the same E4B model without 4-bit or 8-bit weight
quantization:

```cmd
ollama run gemma4:e4b-it-bf16
ollama show gemma4:e4b-it-bf16
```

The 24 GB GPU can hold the E4B BF16 weights, but the weights and the complete
128K context may not fit in VRAM simultaneously. BF16 requires roughly 17.9 GB
for weights and loading overhead before allocating the KV context cache.

### Verified BF16 runtime evidence

The BF16 model was downloaded successfully, passed Ollama's SHA-256
verification, and generated a valid Azerbaijani response locally. With the
context setting increased to 64K, `ollama ps` reported:

```text
NAME                  ID              SIZE      PROCESSOR    CONTEXT    UNTIL
gemma4:e4b-it-bf16    d0d10a1b1ddb    9.7 GB    100% GPU     65536      4 minutes from now
```

This provides direct evidence that:

- the BF16 model loaded and ran successfully;
- the configured 65,536-token context was applied;
- all model layers were assigned to the GPU, with no CPU layer offload;
- Ollama reported a 9.7 GB loaded runtime allocation for this configuration.

The qualitative language smoke test also showed good Azerbaijani generation.
Given this prompt:

```text
Salam. Necəsən? Azərbaycanda danışa bilərik?
```

the model correctly inferred that the user wanted to continue in Azerbaijani
and replied naturally:

```text
Salam! Mən yaxşıyam, təşəkkürlər. 😊 Siz necəsiniz?

Bəli, əlbəttəki! Azərbaycanca danışa bilərik. Hansı mövzuda söhbət etmək istərdiniz?
```

The response used Azerbaijani vocabulary and characters correctly, maintained
an appropriate conversational tone, and handled the intended meaning despite
the prompt using `Azərbaycanda` where `Azərbaycanca` would be more precise. It
was a strong practical result, although `əlbəttəki` should conventionally be
written as two words: `əlbəttə ki`.

*Windows Task Manager showed ***12.5 GB of 24 GB dedicated GPU memory*** in use after
generation.* The GPU activity graph rose to nearly 100% while tokens were being
generated and returned to 0% when the model became idle. This is expected: the
weights can remain loaded in VRAM during Ollama's keep-alive period even though
the GPU is not performing inference between requests.

> **Why an 8B BF16 model used less than 16 GB of dedicated VRAM:** The
> calculation `8B parameters x 2 bytes = 16 GB` correctly estimates total BF16
> weight storage, but it does not imply that every weight is stored in
> dedicated VRAM. Gemma 4 E4B has 4.5B effective transformer parameters and 8B
> total parameters after including its unusually large Per-Layer Embedding
> (PLE) lookup tables.
>
> The Ollama load log recorded `8,964.66 MiB` of model tensors in the CUDA GPU
> buffer and `6,656.00 MiB` in the CUDA host model buffer. The host allocation
> matches the model's embedding tables:
>
> ```text
> Normal token embeddings:
> 262,144 vocabulary x 2,560 dimensions x 2 bytes = 1,280 MiB
>
> Per-layer embeddings:
> 262,144 vocabulary x 42 layers x 256 dimensions x 2 bytes = 5,376 MiB
>
> Total embedding lookup tables:
> 1,280 MiB + 5,376 MiB = 6,656 MiB
> ```
>
> Its approximate GPU-side allocation was `8,964.66 MiB` for model tensors,
> `1,064 MiB` for the 64K KV caches, and `166.02 MiB` for the compute buffer.
> Task Manager's 12.5 GB reading additionally included Windows, display-driver,
> application, and other GPU allocations. The log confirmed that all `43/43`
> computational layers were offloaded to the GPU. Thus, `100% GPU` describes
> layer offload; it does not mean every auxiliary lookup tensor resides in
> dedicated VRAM. The full BF16 weight footprint still exists, split between
> GPU memory and CUDA host memory.

Task Manager also displayed 6.7 GB of shared GPU memory, but that number is
system-wide and includes Windows and other applications. By itself, it is not
evidence of transformer-layer CPU offloading; `ollama ps` reporting `100% GPU`
is the relevant layer-offload measurement.

### Configure the context window

Inside an `ollama run` session, set the context before sending the prompt:

```text
/set parameter num_ctx 65536
```

The full native E4B context can be requested with:

```text
/set parameter num_ctx 131072
```

Afterward, use `ollama ps` in another terminal and confirm that `PROCESSOR`
remains `100% GPU`. If the BF16 model is offloaded or runs out of memory at
128K, use 64K.

To make 64K the persistent Windows default:

```cmd
setx OLLAMA_CONTEXT_LENGTH 65536
```

Completely quit the Ollama system-tray application and relaunch it after
changing an environment variable. The context can alternatively be changed
with the Ollama application's **Settings > Context length** control.

For this 24 GB GPU, the practical choices are:

- `gemma4:e4b-it-bf16` with 32K or 64K context for maximum E4B weight
  precision.
- `gemma4:e4b-it-q8_0` when a longer context and near-full weight precision
  are both important.
- `gemma4:12b-it-q8_0` (about 13 GB) when improving model capability matters
  more than preserving the E4B architecture.

Do not increase context merely to fill unused VRAM. Context capacity only
helps when the prompt, conversation, retrieved documents, and generated output
actually need those tokens. GPU utilization also falls to zero between
requests even when the model remains loaded in VRAM.

References: [Ollama context length documentation](https://docs.ollama.com/context-length),
[Ollama Gemma 4 tags](https://ollama.com/library/gemma4/tags), and
[Google's Gemma 4 model overview](https://ai.google.dev/gemma/docs/core).
