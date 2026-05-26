# Finetuning

> These notes are a structured study companion to **Chapter 7 ("Finetuning")** of the book **["AI Engineering" by Chip Huyen](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)**. They consolidate the chapter's core ideas with the same elaborative-encoding / active-recall style used in the [main `GenAI-on-Kubernetes-Study-Notes.md`](GenAI-on-Kubernetes-Study-Notes.md).

## Contents

1. [Chapter Introduction](#chapter-introduction)
2. [Finetuning Overview](#finetuning-overview)
3. [When to Finetune](#when-to-finetune)
   - [Reasons to Finetune](#reasons-to-finetune)
   - [Reasons Not to Finetune](#reasons-not-to-finetune)
   - [Finetuning Domain-Specific Tasks](#finetuning-domain-specific-tasks)
4. [Finetuning and RAG](#finetuning-and-rag)
5. [Memory Bottlenecks](#memory-bottlenecks)
   - [Backpropagation and Trainable Parameters](#backpropagation-and-trainable-parameters)
   - [Memory Math](#memory-math)
     - [Memory needed for inference](#memory-needed-for-inference)
     - [Memory needed for training](#memory-needed-for-training)
   - [Numerical Representations](#numerical-representations)
   - [Quantization](#quantization)
     - [Inference quantization](#inference-quantization)
     - [Training quantization](#training-quantization)
6. [Finetuning Techniques](#finetuning-techniques)
   - [Parameter-Efficient Finetuning](#parameter-efficient-finetuning)
     - [PEFT techniques](#peft-techniques)
     - [LoRA](#lora)
       - [Why does LoRA work?](#why-does-lora-work)
       - [LoRA configurations](#lora-configurations)
       - [Serving LoRA adapters](#serving-lora-adapters)
     - [Quantized LoRA](#quantized-lora)
   - [Model Merging and Multi-Task Finetuning](#model-merging-and-multi-task-finetuning)
     - [Summing](#summing)
     - [Pruning redundant task-specific parameters](#pruning-redundant-task-specific-parameters)
     - [Layer stacking](#layer-stacking)
     - [Concatenation](#concatenation)
   - [Finetuning Tactics](#finetuning-tactics)
     - [Finetuning frameworks and base models](#finetuning-frameworks-and-base-models)
     - [Finetuning hyperparameters](#finetuning-hyperparameters)
7. [Summary](#summary)
8. [Notes](#notes)

## Chapter Introduction

**Finetuning** is the process of **adapting a model to a specific task** by further training the **whole model or part of the model**.

While **prompt-based methods** adapt a model by giving it **instructions, context, and tools**, **finetuning adapts a model by adjusting its weights**.

### What finetuning can improve

Finetuning can enhance various aspects of a model:

- **domain-specific capabilities**, such as **coding** or **medical question answering**
- **safety**
- most often: **instruction-following ability**, particularly adherence to specific **output styles and formats**

### The cost trade-off

While finetuning can help create models that are more customized to your needs, it also requires **more up-front investment**.

> A question heard very often is: **when to finetune** and **when to do RAG?**

This chapter discusses:

- the **reasons for finetuning**
- the **reasons for not finetuning**
- a **simple framework** for choosing between finetuning and alternate methods

### Memory: the dominant constraint

Compared to prompt-based methods, finetuning incurs a **much higher memory footprint**:

- at the scale of today's foundation models, **naive finetuning often requires more memory than what's available on a single GPU**
- this makes finetuning **expensive and challenging** to do
- **reducing memory requirements is a primary motivation** for many finetuning techniques

A memory-efficient approach that has become **dominant in the finetuning space** is **PEFT (Parameter-Efficient Finetuning)**. The chapter explores PEFT and how it differs from traditional finetuning, with a focus on **adapter-based techniques**.

### Prerequisites

With **prompt-based methods**, knowledge about how ML models operate under the hood is **recommended but not strictly necessary**.

However, **finetuning brings you to the realm of model training**, where **ML knowledge is required**.

> This chapter is the most technically challenging — not because of the complexity of the concepts, but because of the **broad scope** these concepts cover. If, at any point, you feel like you're diving too deep into details that aren't relevant to your work, **feel free to skip**.

[Back to Contents](#contents)

## Finetuning Overview

To finetune, you start with a **base model** that has **some, but not all, of the capabilities you need**. The goal of finetuning is to get this model to perform well enough for your **specific task**.

### Finetuning as transfer learning

Finetuning is one way to do **transfer learning**, a concept first introduced by **Bozinovski and Fulgosi in 1976**. Transfer learning focuses on **how to transfer the knowledge gained from one task to accelerate learning for a new, related task**.

> Conceptually similar to how humans transfer skills: for example, knowing how to play the piano can make it easier to learn another musical instrument.

An early large-scale success in transfer learning was **Google's multilingual translation system** (Johnson et al., 2016). The model transferred its knowledge of Portuguese–English and English–Spanish translation to **directly translate Portuguese to Spanish, even though there were no Portuguese–Spanish examples in the training data**.

#### Why transfer learning matters for LLMs

Since the early days of deep learning, transfer learning has offered a solution for tasks with **limited or expensive training data**:

- by training a **base model** on tasks with **abundant data**, you can **transfer that knowledge** to a **target task**
- for LLMs, knowledge gained from **pre-training on text completion** (a task with abundant data) is transferred to **more specialized tasks** like **legal question answering** or **text-to-SQL** — which often have **less available data**

This capability for transfer learning makes **foundation models particularly valuable**.

### Sample efficiency

Transfer learning **improves sample efficiency**, allowing a model to learn the **same behavior with fewer examples**. A **sample-efficient model** learns effectively from fewer samples.

> Example: while training a model **from scratch** for legal question answering may need **millions of examples**, **finetuning a good base model** might only require **a few hundred**.

Ideally, much of what the model needs to learn is **already present in the base model**, and finetuning just **refines the model's behavior**.

> **OpenAI's InstructGPT paper (2022)** suggested viewing finetuning as **unlocking the capabilities a model already has** but that are difficult for users to access via prompting alone.

> **NOTE — Finetuning is not the only form of transfer learning**
>
> Another approach is **feature-based transfer**. In this approach, a model is trained to **extract features from the data**, usually as **embedding vectors**, which are then used by **another model**.
>
> Feature-based transfer is **very common in computer vision**. For instance, in the second half of the 2010s, many people used models trained on the **ImageNet dataset** to extract features from images and use these features in other computer vision tasks such as **object detection** or **image segmentation**.

### Finetuning as a phase of training

Finetuning is part of a model's **training process**. It's an **extension of model pre-training**. Because any training that happens **after pre-training** is finetuning, finetuning can take **many different forms**.

Two main types covered earlier in the book:

- **supervised finetuning**
- **preference finetuning**

#### Self-supervised continued pre-training

A model's training process starts with **pre-training**, which is usually done with **self-supervision**. Self-supervision allows the model to learn from a **large amount of unlabeled data**:

- for language models, self-supervised data is typically just **sequences of text** that don't need annotations

Before finetuning this pre-trained model with **expensive task-specific data**, you can finetune it with **self-supervision using cheap task-related data**:

- to finetune a model for **legal question answering**, before finetuning it on expensive annotated `(question, answer)` data, you can **finetune it on raw legal documents**
- to finetune a model to do **book summarization in Vietnamese**, you can first finetune it on a **large collection of Vietnamese text**

Self-supervised finetuning is also called **continued pre-training**.

#### Autoregressive vs masked models / infilling finetuning

Language models can be **autoregressive** or **masked**:

- an **autoregressive model** predicts the **next token in a sequence** using the **previous tokens** as the context
- a **masked model** fills in the blank using the tokens **both before and after** it

Similarly, with supervised finetuning, you can also finetune a model to:

- **predict the next token**, or
- **fill in the blank** — also known as **infilling finetuning**

> **Infilling finetuning** is especially useful for tasks such as **text editing** and **code debugging**. You can finetune a model for infilling **even if it was pre-trained autoregressively**.

#### Why supervised finetuning matters

The massive amount of data a model can learn from during self-supervised learning **outfits the model with a rich understanding of the world**, but:

- it might be **hard for users to extract that knowledge** for their tasks
- the way the model behaves might be **misaligned with human preference**

**Supervised finetuning** uses **high-quality annotated data** to refine the model to **align with human usage and preference**.

During supervised finetuning, the model is trained using **`(input, output)` pairs**:

- the **input** can be an **instruction** and the **output** can be a **response**
- a response can be **open-ended**, such as for the task of **book summarization**
- a response can be **close-ended**, such as for a **classification task**

> **High-quality instruction data can be challenging and expensive to create**, especially for instructions that require **factual consistency, domain expertise, or political correctness**.

#### Preference finetuning

A model can also be finetuned with **reinforcement learning** to generate responses that **maximize human preference**.

**Preference finetuning** requires **comparative data** that typically follows the format:

```text
(instruction, winning response, losing response)
```

#### Long-context finetuning

It's possible to finetune a model to **extend its context length**:

- **long-context finetuning** typically requires **modifying the model's architecture**, such as **adjusting the positional embeddings**
- a longer sequence means **more possible positions for tokens**, and positional embeddings should be able to **handle them**
- compared to other finetuning techniques, **long-context finetuning is harder to do**
- the resulting model **might also degrade on shorter sequences**

### A real-world example: Code Llama

Different finetuning techniques can be combined to make different specialized models from the same base model.

![Different finetuning techniques used to make different Code Llama models](<assets/Different finetuning techniques used to make different Code Llama models.png>)

**Figure 7-1. Different finetuning techniques used to make different Code Llama models.** *(Image from Rozière et al., 2024. Adapted from an original image licensed under CC BY 4.0.)*

The figure shows the making of different **Code Llama** models (Rozière et al., 2024), from the **base model Llama 2**, using **different finetuning techniques**:

- using **long-context finetuning**, they were able to increase the model's maximum context length **from 4,096 tokens to 16,384 tokens** to accommodate longer code files
- in the image, **instruction finetuning** refers to **supervised finetuning**

### Who does the finetuning

Finetuning can be done by **both model developers and application developers**:

- **Model developers** typically **post-train a model with different finetuning techniques** before releasing it. They might release **different model versions**, each finetuned to a different extent, so that application developers can choose the version that works best for them
- As an **application developer**, you might finetune a **pre-trained model**, but most likely, you'll **finetune a model that has been post-trained**

> The **more refined a model is** and the **more relevant its knowledge is** to your task, the **less work you'll have to do** to adapt it.

### Encode this

- **Finetuning = adjust the weights**, prompting = adjust the inputs
- **Foundation models work because of transfer learning** — pre-training on abundant data transfers to scarce-data tasks
- **Sample efficiency** is the key win: hundreds of examples vs millions when starting from scratch
- **Many "types" of finetuning**: supervised (next-token or infilling), preference, self-supervised continued pre-training, long-context
- **Code Llama** shows how stacking finetuning techniques produces a family of specialized models from one base

### Recall prompt

*Why does pre-training on abundant data make finetuning more sample-efficient on specialized tasks?*

[Back to Contents](#contents)

## When to Finetune

Before jumping into different finetuning techniques, it's necessary to consider **whether finetuning is the right option for you**.

Compared to **prompt-based methods**, finetuning requires significantly more resources:

- **data**
- **hardware**
- **ML talent**

> Finetuning is generally attempted **after extensive experiments with prompt-based methods**.
>
> However, finetuning and prompting are **not mutually exclusive**. Real-world problems often require **both approaches**.

### Reasons to Finetune

The primary reason for finetuning is to **improve a model's quality**, in terms of:

- **general capabilities**
- **task-specific capabilities**

Finetuning is commonly used to **improve a model's ability to generate outputs following specific structures**, such as **JSON** or **YAML** formats.

#### Task specialization

A general-purpose model that performs well on a wide range of benchmarks **might not perform well on your specific task**. If the model you want to use **wasn't sufficiently trained on your task**, finetuning it with your data can be especially useful.

> Example: an out-of-the-box model might be good at converting from text to **standard SQL dialect** but might fail with a **less common SQL dialect**. Finetuning this model on data containing this SQL dialect will help.
>
> Similarly, if the model works well on standard SQL for common queries but often fails for **customer-specific queries**, finetuning the model on customer-specific queries might help.

#### Bias mitigation

One especially interesting use case of finetuning is **bias mitigation**:

- if the base model **perpetuates certain biases** from its training data, exposing it to **carefully curated data during finetuning can counteract these biases** (Wang and Russakovsky, 2023)

> Examples:
>
> - if a model consistently assigns CEOs **male-sounding names**, finetuning it on a dataset with **many female CEOs** can mitigate this bias
> - Garimella et al. (2022) found that finetuning **BERT-like language models** on text **authored by women** can **reduce gender biases**, while finetuning them on **texts by African authors** can **reduce racial biases**

#### Finetuning small models

You can finetune a big model to make it even better, but **finetuning smaller models is much more common**:

- smaller models require **less memory**, so they are **easier to finetune**
- they are also **cheaper and faster** to use in production

A common approach is to **finetune a small model to imitate the behavior of a larger model** using data generated by this large model:

- because this approach **distills the larger model's knowledge** into the smaller model, it's called **distillation**

> Example: **Grammarly** found that their finetuned **Flan-T5 models** (Chung et al., 2022) **outperformed a GPT-3 variant** specialized in text editing across a wide range of writing assistant tasks **despite being 60 times smaller**. The finetuning process used only **82,000 `(instruction, output)` pairs**, which is smaller than the data typically needed to train a text-editing model from scratch.

#### Open source models make finetuning attractive

In the early days of foundation models, when the strongest models were **commercial with limited finetuning access**, there weren't many competitive models available for finetuning. However, as the **open source community proliferates** with high-quality models of all sizes, tailored for a wide variety of domains, **finetuning has become a lot more viable and attractive**.

### Reasons Not to Finetune

While finetuning can improve a model in many ways, many of these improvements can also be **achieved, to a certain extent, without finetuning**:

- finetuning can improve a model's performance, but so do **carefully crafted prompts and context**
- finetuning can help with **structured outputs**, but many other techniques can also do that

#### Risk: degradation on other tasks

While finetuning a model for a specific task can improve its performance for that task, **it can degrade its performance for other tasks**. This can be frustrating when you intend this model for an application that expects **diverse prompts**.

> Imagine you need a model for **three types of queries**: product recommendations, changing orders, and general feedback. Originally, the model works well for **product recommendations and general feedback** but **poorly for changing orders**.
>
> To fix this, you finetune the model on a dataset of `(query, response)` pairs about changing orders. The finetuned model might indeed perform better for this type of query, **but worse for the two other tasks**.

What do you do in this situation?

- finetune the model on **all the queries you care about**, not just changing orders
- if you can't seem to get a model to perform well on all your tasks, consider **using separate models** for different tasks
- if you wish to combine these separate models into one to make serving them easier, you can also consider **merging them together**

#### High up-front investment

If you're just starting to experiment with a project, **finetuning is rarely the first thing you should attempt**. Finetuning requires **high up-front investments** and **continual maintenance**.

##### Data

- **annotated data can be slow and expensive to acquire manually**, especially for tasks that demand **critical thinking** and **domain expertise**
- **open source data** and **AI-generated data** can mitigate the cost, but their **effectiveness is highly variable**

##### ML knowledge

You need the knowledge of **how to train models**:

- **evaluate base models** to choose one to finetune (options might be limited depending on needs and resources)
- understand the **training knobs** you can tweak
- **monitor the learning process** and **debug** when something is wrong
- understand:
  - how an **optimizer** works
  - what **learning rate** to use
  - how much **training data** is needed
  - how to address **overfitting / underfitting**
  - how to **evaluate** your models throughout the process

##### Serving

Once you have a finetuned model, you'll need to figure out **how to serve it**:

- host it **yourself** or use an **API service**?
- **inference optimization** for large models, especially LLMs, isn't trivial
- finetuning requires **less of a technical leap** if you're already hosting your models in-house

#### Continual maintenance

You need to establish a policy and budget for:

- **monitoring**
- **maintaining**
- **updating**

…your model. As you iterate, **new base models are being developed at a rapid pace**. These base models may **improve faster than you can enhance your finetuned model**.

Key questions:

- if a new base model outperforms your finetuned model on your specific task, **how significant does the performance improvement have to be before you switch**?
- what if a new base model **doesn't immediately outperform** your existing model but **has the potential to do so after finetuning** — would you experiment with it?

In many cases, switching to a better model would provide only a **small incremental improvement**, and your task might be given a **lower priority** than projects with larger returns, like enabling new use cases.

#### Start with prompting, not finetuning

> **AI engineering experiments should start with prompting**, following prompt engineering best practices. Explore more advanced solutions **only if prompting alone proves inadequate**.

Ensure you have **thoroughly tested various prompts**, as a model's performance can **vary greatly with different prompts**.

Many practitioners share a similar story:

> Someone complains that prompting is ineffective and **insists on finetuning**. Upon investigation, it turns out that **prompt experiments were minimal and unsystematic**. Instructions were unclear, examples didn't represent actual data, and metrics were poorly defined. **After refining the prompt experiment process, the prompt quality improved enough** to be sufficient for their application.

### Finetuning Domain-Specific Tasks

> **FINETUNING DOMAIN-SPECIFIC TASKS — sidebar**
>
> Beware of the argument that **general-purpose models don't work well for domain-specific tasks** and, therefore, you **must finetune** or train models for your specific tasks. As **general-purpose models become more capable**, they also become **better at domain-specific tasks** and can **outperform the domain-specific models**.
>
> #### BloombergGPT — a cautionary example
>
> An interesting early specialized model is **BloombergGPT**, introduced by Bloomberg in **March 2023**:
>
> - the strongest models on the market then were all **proprietary**
> - Bloomberg wanted a **mid-size model** that performed well on **financial tasks** and could be **hosted in-house** for use cases with sensitive data
> - **50 billion parameters**, required **1.3 million A100 GPU hours** for training
> - estimated compute cost: **between $1.3 million and $2.6 million**, excluding data costs (Wu et al., 2023)
>
> #### GPT-4-0314 outperformed it within the same month
>
> In the same month, OpenAI released **GPT-4-0314**. Research by Li et al. (2023) demonstrated that **GPT-4-0314 significantly outperformed BloombergGPT** across various financial benchmarks.
>
> **Table 7-1. General-purpose models like GPT-4 can outperform financial models in financial domains.**
>
> | Model | FiQA sentiment analysis (weighted F1) | ConvFinQA (accuracy) |
> | --- | --- | --- |
> | **GPT-4-0314 (zero-shot)** | **87.15** | **76.48** |
> | BloombergGPT | 75.07 | 43.41 |
>
> Since then, several mid-size models with performance comparable to GPT-4 have been released, including:
>
> - **Claude 3.5 Sonnet** (~70B parameters)
> - **Llama 3-70B-Instruct**
> - **Qwen2-72B-Instruct**
>
> The latter two are **open-weight** and can be **self-hosted**.
>
> Because **benchmarks are insufficient to capture real-world performance**, it's possible that BloombergGPT works well for Bloomberg for their specific use cases. The Bloomberg team certainly gained **invaluable experience** through training this model, which might enable them to better develop and operate future models.

Both finetuning and prompting experiments require **systematic processes**. Doing prompt experiments enables developers to build:

- an **evaluation pipeline**
- a **data annotation guideline**
- **experiment tracking practices**

…that will be **stepping stones for finetuning**.

#### Finetuning as token-usage optimization

One benefit of finetuning, before **prompt caching** was introduced, was that it can help **optimize token usage**:

- the **more examples** you add to a prompt, the **more input tokens** the model will use, which **increases both latency and cost**
- instead of including your examples in **each prompt**, you can **finetune a model on these examples**
- this allows you to use **shorter prompts** with the finetuned model

![Instead of including examples in each prompt, you finetune a model on these examples](<assets/Instead of including examples in each prompt.png>)

**Figure 7-2. Instead of including examples in each prompt, which increases cost and latency, you finetune a model on these examples.**

With **prompt caching**, where repetitive prompt segments can be cached for reuse, this is **no longer a strong benefit**. However, the **number of examples you can use with a prompt is still limited by the maximum context length**. With finetuning, there's **no limit to how many examples you can use**.

### Encode this

- **Try prompting first; finetune only after prompt experiments have been systematic, not anecdotal**
- **Finetuning has three costs**: data acquisition, ML knowledge, serving + maintenance
- **Risk**: a model finetuned for task A can get *worse* at tasks B and C
- **Small finetuned model > large general model** is a common pattern (Grammarly Flan-T5, distillation)
- **BloombergGPT lesson**: domain-specific training can be outperformed by a stronger general-purpose model released weeks later
- **Prompt caching reduced the token-saving incentive for finetuning, but context length is still a hard cap**

### Recall prompt

*What three categories of investment must you budget for before deciding to finetune, and why does "we just need to finetune" often signal under-investment in prompt experimentation?*

[Back to Contents](#contents)

## Finetuning and RAG

Once you've maximized the performance gains from prompting, you might wonder whether to do **RAG** or **finetuning** next.

> The answer depends on whether your model's failures are **information-based** or **behavior-based**.

### Information-based failures → RAG

If the model **fails because it lacks information**, a **RAG system** that gives the model access to the relevant sources of information can help. Information-based failures happen when the **outputs are factually wrong or outdated**.

Two example scenarios:

#### The model doesn't have the information

- **Public models** are unlikely to have information **private to you or your organization**
- when a model doesn't have the information, it **either tells you so** or **hallucinates an answer**

#### The model has outdated information

> If you ask: *"How many studio albums has Taylor Swift released?"* and the correct answer is 11, but the model answers 10, it can be because the model's **cut-off date was before the release of the latest album**.

#### Evidence from "Fine-Tuning or Retrieval?" (Ovadia et al., 2024)

The paper **"Fine-Tuning or Retrieval?"** by Ovadia et al. (2024) demonstrated that for tasks that require **up-to-date information**, such as questions about **current events**:

- **RAG outperformed finetuned models**
- **RAG with the base model outperformed RAG with finetuned models**

This finding indicates that while finetuning can enhance a model's performance on a specific task, it may also lead to a **decline in performance in other areas**.

**Table 7-2. RAG outperforms finetuning on a question-answering task about current events** *(curated by Ovadia et al., 2024). `FT-reg` and `FT-par` refer to two different finetuning approaches the authors used.*

| Base model | Base model + RAG | FT-reg | FT-par | FT-reg + RAG | FT-par + RAG |
| --- | --- | --- | --- | --- | --- |
| **Mistral-7B** — `0.481` | `0.875` | `0.504` | `0.588` | `0.810` | `0.830` |
| **Llama 2-7B** — `0.353` | `0.585` | `0.219` | `0.392` | `0.326` | `0.520` |
| **Orca 2-7B** — `0.456` | `0.876` | `0.511` | `0.566` | `0.820` | `0.826` |

### Behavior-based failures → finetuning

On the other hand, if the model has **behavioral issues**, finetuning might help.

#### Outputs correct but irrelevant

> Example: you ask the model to generate **technical specifications** for a software project to provide to your engineering teams. While accurate, the generated specs **lack the details your teams need**.

Finetuning the model with **well-defined technical specifications** can make the outputs **more relevant**.

#### Outputs fail format expectations

> Example: if you asked the model to write **HTML code**, but the generated code **didn't compile**, it might be because the model **wasn't sufficiently exposed to HTML** in its training data.

You can correct this by **exposing the model to more HTML code during finetuning**.

#### Semantic parsing

**Semantic parsing** is a category of tasks whose success hinges on the model's **ability to generate outputs in the expected format** and, therefore, **often requires finetuning**:

- semantic parsing = converting **natural language into a structured format** like JSON
- **strong off-the-shelf models** are generally good for **common, less complex syntaxes** like **JSON, YAML, and regex**
- they might **not be as good** for syntaxes with **fewer available examples on the internet**, such as a **domain-specific language** for a less popular tool or a **complex syntax**

### Form vs facts

> **In short: finetuning is for form, and RAG is for facts.**

- A **RAG system** gives your model **external knowledge** to construct **more accurate and informative answers**. A RAG system can help **mitigate your model's hallucinations**
- **Finetuning** helps your model **understand and follow syntaxes and styles**
- While finetuning can potentially **reduce hallucinations** if done with **enough high-quality data**, it can also **worsen hallucinations** if the data quality is low

### If your model has both issues, start with RAG

If your model has **both information and behavior issues**, **start with RAG**:

- RAG is typically **easier** since you won't have to worry about **curating training data** or **hosting the finetuned models**
- when doing RAG, start with **simple term-based solutions** such as **BM25** instead of jumping straight into something that requires vector databases

RAG can also introduce a **more significant performance boost** than finetuning. Ovadia et al. (2024) showed that for **almost all question categories** in the **MMLU benchmark**, **RAG outperforms finetuning** for three different models: **Mistral 7B**, **Llama 2-7B**, and **Orca 2-7B**.

### RAG and finetuning are not mutually exclusive

However, RAG and finetuning **aren't mutually exclusive**. They can sometimes be used **together** to maximize your application's performance.

In the same experiment, Ovadia et al. (2024) showed that:

- incorporating **RAG on top of a finetuned model** can **boost its performance on the MMLU benchmark 43% of the time**
- but using **RAG with finetuned models doesn't improve the performance 57% of the time**, compared to using **RAG alone**

### Example application development workflow

There's **no universal workflow** for all applications.

![Example application development flows](<assets/Example application development flows.png>)

**Figure 7-3. Example application development flows.** *After simple retrieval (such as term-based retrieval), whether to experiment with more complex retrieval (such as hybrid search) or finetuning depends on each application and its failure modes. Inspired by an example workflow shown by OpenAI (2023).*

#### A practical adaptation workflow

> **Before any of the adaptation steps**, you should **define your evaluation criteria** and **design your evaluation pipeline**. Evaluation **does not happen only in the beginning** — it should be **present during every step of the process**.

1. **Try to get a model to perform your task with prompting alone.** Use prompt engineering best practices, including **systematically versioning your prompts**
2. **Add more examples to the prompt.** Depending on the use case, the number of examples needed might be **between 1 and 50**
3. **If your model frequently fails due to missing information**, connect it to **data sources** that can supply relevant information. When starting with RAG, begin by using **basic retrieval methods like term-based search**. Even with simple retrieval, adding **relevant and accurate knowledge** should lead to some improvement in your model's performance
4. **Depending on your model's failure modes**, you might explore one of these next steps:
   - **If the model continues having information-based failures**, try even more advanced RAG methods, such as **embedding-based retrieval**
   - **If the model continues having behavioral issues** — irrelevant, malformatted, or unsafe responses — opt for **finetuning**
     - **Embedding-based retrieval** increases **inference complexity** by introducing additional components into the pipeline
     - **Finetuning** increases the complexity of **model development** but **leaves inference unchanged**
5. **Combine both RAG and finetuning** for even more performance boost

If, after considering all the pros and cons of finetuning and other alternate techniques, you decide to **finetune your model**, the rest of the chapter (covered in continuation) will address the **number one challenge of finetuning: its memory bottleneck**.

### Encode this

- **Finetuning is for form (style/syntax); RAG is for facts (knowledge)**
- **Information-based failures → RAG**; **behavior-based failures → finetuning**
- **Start with RAG** when in doubt — easier to iterate on, no training data curation, no extra inference complexity for the base model itself
- **Begin retrieval with BM25**, escalate to embedding-based retrieval only if needed
- **Embedding retrieval complicates inference**; **finetuning complicates training but keeps inference simple**
- **RAG + finetuning can stack**, but only ~43% of the time does that beat RAG alone (Ovadia et al., 2024)

### Recall prompt

*Given a model that produces factually outdated answers AND fails to follow your required JSON schema, in which order would you apply RAG and finetuning — and why?*

[Back to Contents](#contents)

## Memory Bottlenecks

Because finetuning is **memory-intensive**, many finetuning techniques aim to **minimize their memory footprint**. Understanding what causes this memory bottleneck is necessary to understand **why and how these techniques work**. This understanding, in turn, can help you **select a finetuning method** that works best for you.

Besides explaining finetuning's memory bottleneck, this section also introduces **formulas for back-of-the-napkin calculation** of the memory usage of each model. This calculation is useful in **estimating what hardware you'd need** to serve or finetune a model.

> Because memory calculation requires a breakdown of **low-level ML and computing concepts**, this section is **technically dense**. If you're already familiar with these concepts, feel free to skip them.

> **KEY TAKEAWAYS FOR UNDERSTANDING MEMORY BOTTLENECKS**
>
> If you decide to skip this section, here are a few key takeaways. If you find any of these takeaways unfamiliar, the concepts in this section should help explain them:
>
> - Because of the scale of foundation models, **memory is a bottleneck** for working with them, both for **inference** and for **finetuning**. The memory needed for finetuning is typically **much higher** than the memory needed for inference because of the way neural networks are trained
> - The **key contributors** to a model's memory footprint during finetuning are its **number of parameters**, its **number of trainable parameters**, and its **numerical representations**
> - The more trainable parameters, the higher the memory footprint. You can **reduce memory requirement for finetuning by reducing the number of trainable parameters** — this is the motivation for **PEFT** (parameter-efficient finetuning)
> - **Quantization** refers to the practice of converting a model from a format with **more bits to a format with fewer bits**. Quantization is a **straightforward and efficient** way to reduce a model's memory footprint. For a model of 13 billion parameters, using **FP32** means **4 bytes per weight** or **52 GB for the whole weights**. If you can reduce each value to only **2 bytes**, the memory needed for the model's weights decreases to **26 GB**
> - **Inference** is typically done using as **few bits as possible**, such as 16 bits, 8 bits, and even 4 bits
> - **Training** is more sensitive to numerical precision, so it's **harder to train a model in lower precision**. Training is typically done in **mixed precision**, with some operations done in higher precision (e.g., 32-bit) and some in lower precision (e.g., 16-bit or 8-bit)

### Backpropagation and Trainable Parameters

A key factor that determines a model's memory footprint during finetuning is its **number of trainable parameters**.

A **trainable parameter** is a parameter that **can be updated during finetuning**:

- During **pre-training**, **all model parameters** are updated
- During **inference**, **no model parameters** are updated
- During **finetuning**, **some or all** model parameters may be updated

The parameters that are kept unchanged are **frozen parameters**.

#### How backpropagation drives memory cost

The memory needed for each trainable parameter results from the way a model is trained. As of this writing, neural networks are typically trained using a mechanism called **backpropagation**. With backpropagation, each training step consists of **two phases**:

- **Forward pass** — the process of **computing the output from the input**
- **Backward pass** — the process of **updating the model's weights** using the aggregated signals from the forward pass

> During **inference**, only the **forward pass** is executed.
> During **training**, **both passes** are executed.

#### What happens in the backward pass

At a high level, the backward pass works as follows:

1. **Compare** the computed output from the forward pass against the **expected output (ground truth)**. If they are different, the model made a mistake, and the parameters need to be adjusted. The difference is called the **loss**
2. **Compute how much each trainable parameter contributes to the mistake.** This value is called the **gradient**. Mathematically, gradients are computed by taking the **derivative of the loss** with respect to each trainable parameter. There's **one gradient value per trainable parameter**. If a parameter has a **high gradient**, it **significantly contributes to the loss** and should be **adjusted more**
3. **Adjust trainable parameter values** using their corresponding gradient. **How much** each parameter should be readjusted, given its gradient value, is determined by the **optimizer**. Common optimizers include:
   - **SGD** (stochastic gradient descent)
   - **Adam** — for transformer-based models, **by far** the most widely used optimizer

![The forward and backward pass of a simple neural network](<assets/The forward and backward pass of a simple neural network..png>)

**Figure 7-4. The forward and backward pass of a simple neural network.**

#### Why trainable parameters cost memory

During the backward pass, **each trainable parameter** comes with **additional values**:

- its **gradient**
- its **optimizer states**

Therefore, the **more trainable parameters there are**, the **more memory is needed** to store these additional values.

#### Encode this

- **Trainable parameters drive finetuning memory cost — frozen parameters do not**
- **Backpropagation = forward pass (compute output) + backward pass (compute gradients, update weights)**
- **Each trainable parameter needs storage for its value + gradient + optimizer states**
- **Adam is the de facto LLM optimizer; it stores 2 extra values per trainable parameter**
- **PEFT works precisely because it shrinks the trainable-parameter count**

#### Recall prompt

*Why does shrinking the set of trainable parameters dramatically reduce finetuning memory even when the model itself stays the same size?*

[Back to Contents](#contents)

### Memory Math

It's useful to know **how much memory a model needs** so that you can use the **right hardware** for it.

Often, you might already have the hardware and need to calculate **whether you can afford to run a certain model**. If a model requires **30 GB** of memory to do inference, a chip with **24 GB of memory won't be sufficient**.

A model's memory footprint depends on:

- the **model**
- the **workload**
- the **different optimization techniques** used to reduce its memory usage

Because it's impossible to account for all optimization techniques and workloads, this section outlines only **formulas for approximate calculations** — enough to give a rough idea of how much memory you need to operate a model, both during **inference** and **training**.

> **NOTE — Why training and inference chips diverge**
>
> Inference and training having **distinct memory profiles** is one of the reasons for the **divergence in chips for training and inference**.

#### Memory needed for inference

During inference, **only the forward pass** is executed. The forward pass requires memory for the model's **weights**.

Let:

- `N` = the model's **parameter count**
- `M` = the **memory needed for each parameter**

Then the memory needed to load the model's parameters is:

```text
N × M
```

The forward pass also requires memory for **activation values**. Transformer models need memory for **key-value vectors** for the **attention mechanism**. The memory for both activation values and key-value vectors **grows linearly with sequence length and batch size**.

For many applications, the memory for activation and key-value vectors can be assumed to be **20% of the memory for the model's weights**. If your application uses a **longer context** or **larger batch size**, the actual memory needed will be higher.

This assumption brings the model's memory footprint to:

```text
N × M × 1.2
```

##### Example: a 13B-parameter model

Consider a **13B-parameter model**. If each parameter requires **2 bytes**, the model's weights will require:

```text
13B × 2 bytes = 26 GB
```

The total memory for inference will be:

```text
26 GB × 1.2 = 31.2 GB
```

A model's memory footprint **grows rapidly with its size**. As models become bigger, **memory becomes a bottleneck** for operating them.

> A **70B-parameter model** with **2 bytes per parameter** will require a whopping **140 GB of memory just for its weights**.

#### Memory needed for training

To train a model, you need memory for:

- the model's **weights**
- **activations**
- **gradients**
- **optimizer states**

The latter two scale with the **number of trainable parameters**.

Overall, the memory needed for training is calculated as:

```text
Training memory = model weights + activations + gradients + optimizer states
```

> **TIP — Optimizer state cost**
>
> During the backward pass, each trainable parameter requires **one value for gradient** plus **zero to two values for optimizer states**, depending on the optimizer:
>
> - **vanilla SGD** — no state
> - **momentum optimizer** — stores **one value** per trainable parameter
> - **Adam optimizer** — stores **two values** per trainable parameter

##### Example: 13B model, full finetune with Adam

Imagine you're updating **all parameters** in a **13B-parameter model** using the **Adam optimizer**. Each trainable parameter has **three values** for its gradient and optimizer states. If it takes **2 bytes** to store each value, the memory needed for gradients and optimizer states will be:

```text
13 billion × 3 × 2 bytes = 78 GB
```

##### Example: 13B model, only 1B trainable parameters

However, if you only have **1B trainable parameters**, the memory needed for gradients and optimizer states will be only:

```text
1 billion × 3 × 2 bytes = 6 GB
```

##### Activation memory can dwarf weight memory

One important thing to note: the formula above **assumed that the memory needed for activations is less than the memory needed for the model's weights**. However, **in reality, the activation memory can be much larger**.

If activations are **stored for gradient computation**, the memory needed for activations can **dwarf the memory needed for the model's weights**.

![The memory needed for activations can dwarf the memory needed for the model's weights](<assets/The memory needed for activations can dwarf the memory needed for the model’s weights.png>)

**Figure 7-5. The memory needed for activations can dwarf the memory needed for the model's weights.** *(Image from Korthikanti et al., 2022.)*

The figure shows memory needed for activations compared to memory needed for the model's weights for different **Megatron** models at different scales, according to **"Reducing Activation Recomputation in Large Transformer Models"** by Korthikanti et al. (2022).

##### Gradient checkpointing / activation recomputation

One way to reduce the memory needed for activations is to **not store them**:

- instead of storing activations for reuse, you **recompute activations when necessary**
- this technique is called **gradient checkpointing** or **activation recomputation**

While this **reduces memory requirements**, it **increases the time needed for training** due to the recomputation.

#### Encode this

- **Inference memory** ≈ `N × M × 1.2` (weights + ~20% for activations and KV cache)
- **Training memory** = weights + activations + gradients + optimizer states
- **Adam adds 3× the trainable-parameter memory** (gradient + 2 optimizer values per parameter)
- **A 13B Adam full finetune** needs ~78 GB just for gradients + optimizer state (on top of weights and activations)
- **Activation memory can exceed weight memory** at scale — gradient checkpointing trades compute for memory to fix this
- **KV cache + long contexts + bigger batches all blow up the 20% assumption**

#### Recall prompt

*Why is the memory needed to finetune a 13B model with full Adam several times larger than the memory needed just to do inference on the same model?*

[Back to Contents](#contents)

### Numerical Representations

In the memory calculation so far, each value was assumed to take up **two bytes** of memory. The **memory required to represent each value** in a model **contributes directly to the model's overall memory footprint**.

> If you **reduce the memory needed for each value by half**, the memory needed for the model's weights is **also reduced by half**.

#### Floating point formats (the FP family)

Numerical values in neural networks are traditionally represented as **float numbers**. The most common family of floating point formats is the **FP family**, adhering to the **IEEE 754 standard** for Floating-Point Arithmetic:

- **FP32** — uses **32 bits (4 bytes)** to represent a float. Called **single precision**
- **FP64** — uses **64 bits (8 bytes)**. Called **double precision**
- **FP16** — uses **16 bits (2 bytes)**. Called **half precision**

While **FP64** is still used in many computations (it's the default format for **NumPy** and **pandas**), it's **rarely used in neural networks** because of its memory footprint. **FP32** and **FP16** are more common.

Other popular floating point formats in AI workloads:

- **BF16 (BFloat16)** — designed by **Google** to optimize AI performance on **TPUs**
- **TF32 (TensorFloat-32)** — designed by **NVIDIA** for **GPUs**

#### Integer formats

Numbers can also be represented as **integers**. Even though not yet as common as floating formats, integer representations are becoming **increasingly popular**. Common integer formats:

- **INT8** (8-bit integers)
- **INT4** (4-bit integers)

#### Range vs precision

Each float format usually has **1 bit** to represent the **sign** (negative or positive). The rest of the bits are split between **range** and **precision**:

- **Range** — the number of range bits determines the **range of values the format can represent**. More bits → wider range. Similar to how having more digits lets you represent a wider range of numbers
- **Precision** — the number of precision bits determines **how precisely a number can be represented**. Reducing precision bits makes a number **less precise**

> Example: if you convert `10.1234` to a format that can support only two decimal digits, this value becomes `10.12`, which is **less precise** than the original value.

![Different numerical formats with their range and precision](<assets/Different numerical formats with their range and precision.png>)

**Figure 7-6. Different numerical formats with their range and precision.**

#### Reducing precision causes errors

Formats with **more bits** are considered **higher precision**. Converting from a high-precision format into a low-precision format (e.g., from FP32 to FP16) **reduces precision** and can cause a value to **change** or result in **errors**.

**Table 7-3. Convert from FP32 values to lower-precision formats.** *Resultant inaccuracies are in italics.*

| FP32 | FP16 | BF16 | TF32 |
| --- | --- | --- | --- |
| `0.0123456789` | *`0.0123443603515625`* | *`0.0123291`* | *`0.0123443603515625`* |
| `0.123456789` | *`0.12347412109375`* | *`0.123535`* | *`0.1234130859375`* |
| `1.23456789` | *`1.234375`* | *`1.23438`* | *`1.234375`* |
| `12.3456789` | *`12.34375`* | *`12.375`* | *`12.34375`* |
| `123.456789` | *`123.4375`* | *`123.5`* | *`123.4375`* |
| `1234.56789` | *`1235.0`* | *`1232.0`* | *`1234.0`* |
| `12345.6789` | *`12344.0`* | *`12352.0`* | *`12344.0`* |
| `123456.789` | ***`INF`*** ¹ | *`123392.0`* | *`123456.0`* |
| `1234567.89` | ***`INF`*** | *`1236990.0`* | *`1233920.0`* |

> ¹ Values out of bound in FP16 are **rounded to infinity**.

##### BF16 vs FP16 trade-off

Note in Table 7-3 that even though **BF16 and FP16 have the same number of bits**, **BF16 has more bits for range** and **fewer bits for precision**:

- this allows BF16 to represent **large values that are out-of-bound for FP16**
- however, this makes BF16 **less precise than FP16**

> Example: `1234.56789` is:
>
> - `1235.0` in **FP16** (**0.035%** value change)
> - `1232.0` in **BF16** (**0.208%** value change)

> **WARNING — Load models in the format they were intended for**
>
> When using a model, make sure to load the model in the **format it's intended for**. Loading a model into the **wrong numerical format** can cause the model to **change significantly**.
>
> Example: **Llama 2 had its weights set to BF16** when it came out. However, many teams **loaded the model in FP16** and were subsequently frustrated to find the model's **quality much worse than advertised**.
>
> While this misunderstanding wasted a lot of people's time, the upside is that it **forced many people to learn about numerical representations**.

The **right format** for you depends on:

- the **distribution of numerical values** of your workload (such as the range of values you need)
- **how sensitive** your workload is to small numerical changes
- the **underlying hardware**

#### Encode this

- **Each parameter's bit-width directly scales the model's memory footprint**
- **FP32 / FP16 dominate; BF16 (TPU-friendly) and TF32 (GPU-friendly) are common AI variants**
- **BF16 vs FP16**: same bit count, different range/precision trade — BF16 handles larger values, FP16 is more precise
- **INT8 / INT4** are increasingly used, especially for inference
- **Loading a model in the wrong format silently degrades quality** — Llama 2 BF16-as-FP16 is the canonical cautionary tale

#### Recall prompt

*Why does BF16 sometimes outperform FP16 on training workloads even though both use 16 bits, and what kind of workload would prefer FP16's higher precision over BF16's wider range?*

[Back to Contents](#contents)

### Quantization

The fewer bits needed to represent a model's values, the **lower the model's memory footprint** will be:

- a **10B-parameter model in a 32-bit format** requires **40 GB** for its weights
- the same model in a **16-bit format** will require only **20 GB**

**Reducing precision**, also known as **quantization**, is a **cheap and extremely effective** way to reduce a model's memory footprint. It's straightforward to do and **generalizes over tasks and architectures**.

> In the context of ML, **low precision** generally refers to any format with **fewer bits than the standard FP32**.

> **QUANTIZATION VERSUS REDUCED PRECISION**
>
> Strictly speaking, it's **"quantization"** only if the **target format is integer**.
>
> However, in practice, **"quantization" is used to refer to all techniques** that convert values to a **lower-precision format**. These notes use **"quantization" to mean precision reduction**, to keep it consistent with the literature.

#### What to quantize and when to quantize

To do quantization, you need to decide **what to quantize** and **when**:

##### What to quantize

Ideally, you want to quantize whatever is **consuming most of your memory**, but it also depends on **what you can quantize without hurting performance too much**.

Major contributors to a model's memory footprint during inference are the model's **weights and activations**:

- **weight quantization** is **more common than activation quantization**
- weight quantization tends to have a **more stable impact on performance with less accuracy loss**

##### When to quantize

Quantization can happen **during training** or **post-training**:

- **Post-training quantization (PTQ)** — means quantizing a model **after it's been fully trained**. PTQ is **by far the most common**. It's also **more relevant to AI application developers** who don't usually train models

#### Inference quantization

In the early days of deep learning, it was standard to **train and serve models using 32 bits with FP32**. Since the late 2010s, it has become increasingly common to serve models in **16 bits** and in even **lower precision**.

For example:

- **Dettmers et al. (2022)** quantized LLMs into **8 bits** with **LLM.int8()**
- **QLoRA (Dettmers et al., 2023)** quantized into **4 bits**

##### Mixed precision serving

A model can also be served in **mixed precision**, where values are **reduced in precision when possible** and **maintained in higher precision when necessary**:

- to serve models on devices, **Apple (2024)** leveraged a quantization scheme that uses a **mixture of 2-bit and 4-bit formats**, averaging **3.5 bits-per-weight**
- in 2024, in anticipation of 4-bit neural networks, **NVIDIA announced their new GPU architecture, Blackwell**, supporting model **inference in 4-bit float**

##### Sub-8-bit gets tricky

Once you get to **8 bits and under**, numerical representations get more tricky. You can:

- keep parameter values as **floats** using one of the **minifloat formats**, such as **FP8** (8 bits) and **FP4** (4 bits)
- more commonly, convert parameter values into an **integer format**, such as **INT8** or **INT4**

##### How low can quantization go?

Quantization is effective, but there's a limit to how far it can go. You can't have fewer than **1 bit per value**, and some have attempted the **1-bit representation**:

- **BinaryConnect** (Courbariaux et al., 2015)
- **Xnor-Net** (Rastegari et al., 2016)
- **BitNet** (Wang et al., 2023)

##### The era of 1-bit LLMs

In 2024, **Microsoft researchers (Ma et al.)** declared that we're entering the **era of 1-bit LLMs** by introducing **BitNet b1.58**:

- a **transformer-based language model** that requires only **1.58 bits per parameter**
- performance comparable to **16-bit Llama 2** (Touvron et al., 2023) up to **3.9B parameters**

**Table 7-4. BitNet b1.58's performance compared to that of Llama 2 16-bit** on different benchmarks and at different model sizes, up to 3.9B parameters. *Results from Ma et al. (2024).*

| Model | Size | ARCe | ARCc | HS | BQ | OQ | PQ | WGe | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Llama LLM** | 700M | 54.7 | 23.0 | 37.0 | 60.0 | 20.2 | 68.9 | 54.8 | **45.5** |
| **BitNet b1.58** | 700M | 51.8 | 21.4 | 35.1 | 58.2 | 20.0 | 68.1 | 55.2 | **44.3** |
| **Llama LLM** | 1.3B | 56.9 | 23.5 | 38.5 | 59.1 | 21.6 | 70.0 | 53.9 | **46.2** |
| **BitNet b1.58** | 1.3B | 54.9 | 24.2 | 37.7 | 56.7 | 19.6 | 68.8 | 55.8 | **45.4** |
| **Llama LLM** | 3B | 62.1 | 25.6 | 43.3 | 61.8 | 24.6 | 72.1 | 58.2 | **49.7** |
| **BitNet b1.58** | 3B | 61.4 | 28.3 | 42.9 | 61.5 | 26.6 | 71.5 | 59.3 | **50.2** |
| **BitNet b1.58** | 3.9B | 64.2 | 28.7 | 44.2 | 63.5 | 24.2 | 73.2 | 60.5 | **51.2** |

##### Beyond memory: speed gains

Reduced precision not only **reduces the memory footprint** but also often **improves computation speed**:

- it allows a **larger batch size**, enabling the model to **process more inputs in parallel**
- reduced precision **speeds up computation**, which further reduces inference latency and training time

> To illustrate: consider the addition of two numbers. If we perform the addition bit by bit, and each takes `t` nanoseconds, it'll take **`32t` nanoseconds for 32 bits** but only **`16t` nanoseconds for 16 bits**.

However, reducing precision **doesn't always reduce latency** due to the **added computation needed for format conversion**.

##### Downsides

There are downsides to reduced precision:

- each conversion often causes a **small value change**, and many small changes can cause a **big performance change**
- if a value is **outside the range** the reduced precision format can represent, it might be **converted to infinity or an arbitrary value**, causing the model's quality to further degrade

> **How to reduce precision with minimal impact on model performance is an active area of research**, pursued by model developers, hardware makers, and application developers.

##### PTQ has become a standard

Inference in lower precision has become a **standard**:

- a model is **trained using a higher-precision format** to maximize performance
- then its **precision is reduced for inference**

Major ML frameworks offer PTQ for free with a few lines of code:

- **PyTorch**
- **TensorFlow**
- **Hugging Face's `transformers`**

Some **edge devices only support quantized inference**, so frameworks for **on-device inference** — such as **TensorFlow Lite** and **PyTorch Mobile** — **also offer PTQ**.

#### Training quantization

Quantization during training is **not yet as common as PTQ**, but it's **gaining traction**. There are **two distinct goals** for training quantization:

1. **Produce a model that can perform well in low precision during inference.** This addresses the challenge that a model's quality might degrade during PTQ
2. **Reduce training time and cost.** Quantization reduces a model's memory footprint, allowing a model to be trained on **cheaper hardware** or allowing the training of a **larger model on the same hardware**. Quantization also **speeds up computation**, further reducing costs

A quantization technique might help achieve **one or both** of these goals.

##### Quantization-aware training (QAT)

**Quantization-aware training (QAT)** aims to create a model with **high quality in low precision for inference**:

- the model **simulates low-precision (e.g., 8-bit) behavior during training**
- this allows the model to **learn to produce high-quality outputs in low precision**
- however, **QAT doesn't reduce a model's training time** since its computations are still performed in high precision
- QAT can even **increase training time** due to the extra work of simulating low-precision behavior

##### Training directly in low precision

Training a model **directly in lower precision** can help with **both goals**. People attempted to train models in reduced precision as early as **2016** (Hubara et al., 2016; Jacob et al., 2017).

> **Character.AI (2024)** shared that they were able to **train their models entirely in INT8**, which helped eliminate the **training/serving precision mismatch** while also **significantly improving training efficiency**.

However, **training in lower precision is harder to do**, as **backpropagation is more sensitive to lower precision**.

##### Mixed-precision training

Lower-precision training is often done in **mixed precision**, where:

- a **copy of the weights** is kept in **higher precision**
- **other values**, such as **gradients and activations**, are kept in **lower precision**

You can also have:

- **less-sensitive weight values** computed in **lower precision**
- **more-sensitive weight values** computed in **higher precision**

> Example: **LLM-QAT (Liu et al., 2023)** quantizes weights and activations into **4 bits** but keeps **embeddings in 16 bits**.

The portions of the model that should be in lower precision can be set automatically using the **automatic mixed precision (AMP)** functionality offered by many ML frameworks.

##### Different precisions across training phases

It's also possible to have **different phases of training in different precision levels**. For example:

- a model can be **trained in higher precision** but **finetuned in lower precision**
- this is especially common with **foundation models**:
  - the team training a model from scratch might be an **organization with sufficient compute for higher-precision training**
  - once the model is published, **developers with less compute access** can **finetune that model in lower precision**

#### Encode this

- **Quantization = convert values to a lower-precision format** (in literature, includes float→float reductions too)
- **Weight quantization is more common and safer than activation quantization**
- **PTQ (Post-Training Quantization)** is the dominant pattern for inference today
- **Below 8 bits**, formats split into **minifloat** (FP8, FP4) and **integer** (INT8, INT4) families
- **BitNet b1.58 (1.58 bits)** showed that **near-1-bit LLMs can match 16-bit Llama 2** up to ~3.9B parameters
- **Reduced precision also speeds up computation** (more bits = more nanoseconds per op)
- **Training is more precision-sensitive than inference**, so training quantization is dominated by **QAT** and **mixed-precision** strategies
- **AMP** automates mixed-precision decisions in PyTorch/TF/HF

#### Recall prompt

*If you have a 13B Adam-finetuned model that won't fit on a single 80 GB GPU, which two levers (other than buying more GPUs) would you pull first, and in what order?*

[Back to Contents](#contents)

## Finetuning Techniques

The previous section made clear **why finetuning large-scale models is so memory-intensive**. The more memory finetuning requires, the **fewer people who can afford to do it**. Techniques that **reduce a model's memory footprint** make finetuning more accessible, allowing more people to **adapt models to their applications**.

This section focuses on **memory-efficient finetuning techniques**, centered on **parameter-efficient finetuning (PEFT)**.

It also covers **model merging** — an **exciting but more experimental** approach to creating custom models. While model merging is generally **not considered finetuning**, it is included here because it is **complementary to finetuning**:

- **finetuning** tailors *one* model to specific needs
- **model merging** combines *multiple* models, often finetuned models, for the same purpose

While combining multiple models isn't a new concept, **new types of models and finetuning techniques** have inspired many creative model-merging techniques.

[Back to Contents](#contents)

### Parameter-Efficient Finetuning

#### Full finetuning: the starting point

In the early days of finetuning, models were small enough that people could finetune **entire models**. This is called **full finetuning**. In full finetuning, the **number of trainable parameters is exactly the same as the number of parameters**.

Full finetuning can look similar to training. The main difference is:

- **training** starts with **randomized model weights**
- **finetuning** starts with model weights that have been **previously trained**

##### Why full finetuning gets expensive fast

The more trainable parameters there are, the more memory is needed. Consider a **7B-parameter model**:

- using a **16-bit format** like FP16, loading the model's weights alone requires **14 GB** for memory
- **full finetuning** this model with the **Adam optimizer**, also in a 16-bit format, requires an additional `7B × 3 × 2 bytes = 42 GB` of memory
- the **total memory** needed for the model's weights, gradients, and optimizer states is then `14 GB + 42 GB = 56 GB`

**56 GB exceeds the memory capacity of most consumer GPUs**, which typically come with **12–24 GB** of memory, with higher-end GPUs offering up to **48 GB**. And this estimation **doesn't yet take into account the memory required for activations**.

> **NOTE — Two levers to fit a model on given hardware**
>
> To fit a model on a given hardware, you can either:
>
> - **reduce the model's memory footprint** — techniques like **quantization** and **PEFT** help here
> - **find ways to use the hardware's memory more efficiently** — techniques include **CPU offloading**: instead of trying to fit the whole model on GPUs, you can **offload excess memory onto CPUs**, as demonstrated by **DeepSpeed** (Rasley et al., 2020)

#### Partial finetuning: not enough

Full finetuning, especially **supervised** and **preference** finetuning, also typically requires a lot of **high-quality annotated data** that most people can't afford.

Due to the high memory and data requirements, people started doing **partial finetuning** — only **some of the model's parameters** are updated:

> Example: if a model has ten layers, you might **freeze the first nine layers** and finetune only the **last layer**, reducing trainable parameters to **10% of full finetuning**.

While partial finetuning can reduce the memory footprint, it's **parameter-inefficient**. It requires **many trainable parameters** to achieve performance close to that of full finetuning.

> A study by **Houlsby et al. (2019)** shows that with **BERT large** (Devlin et al., 2018), you'd need to update approximately **25% of the parameters** to achieve performance comparable to full finetuning on the **GLUE benchmark**.

![The blue line shows that partial finetuning requires many trainable parameters](<assets/The blue line shows that partial finetuning requires many trainable parameters.png>)

**Figure 7-7. The blue line shows that partial finetuning requires many trainable parameters to achieve a performance comparable to full finetuning.** *(Image from Houlsby et al., 2019.)*

#### PEFT: parameter-efficient finetuning

This brings up the question:

> **How to achieve performance close to that of full finetuning while using significantly fewer trainable parameters?**

Finetuning techniques resulting from this quest are **parameter-efficient**.

> There's no clear threshold a finetuning method has to pass to be considered parameter-efficient. In general, a technique is considered parameter-efficient if it can achieve performance **close to that of full finetuning** while using **several orders of magnitude fewer trainable parameters**.

The idea of **PEFT (parameter-efficient finetuning)** was introduced by **Houlsby et al. (2019)**. The authors showed that by **inserting additional parameters into the model in the right places**, you can achieve strong finetuning performance using a **small number of trainable parameters**.

They inserted **two adapter modules** into each **transformer block** of a BERT model:

![By inserting two adapter modules into each transformer layer for a BERT model](<assets/By inserting two adapter modules into each transformer layer for a BERT model.png>)

**Figure 7-8. By inserting two adapter modules into each transformer layer for a BERT model and updating only the adapters, Houlsby et al. (2019) were able to achieve strong finetuning performance using a small number of trainable parameters.**

During finetuning:

- they **kept the model's original parameters unchanged**
- they only **updated the adapters**
- the **number of trainable parameters** is the number of parameters in the **adapters**

On the GLUE benchmark, they achieved a performance **within 0.4% of full finetuning** using only **3% of the number of trainable parameters**. The **orange line** in Figure 7-7 shows the performance delta between full finetuning and finetuning using different adapter sizes.

However, the **downside** of this approach is that it **increases the inference latency** of the finetuned model. The adapters introduce **additional layers**, which add more computational steps to the forward pass.

##### Why PEFT is so attractive

PEFT enables finetuning on **more affordable hardware**, making it accessible to many more developers.

PEFT methods are generally **not only parameter-efficient but also sample-efficient**:

- **full finetuning** may need **tens of thousands to millions** of examples to achieve notable quality improvements
- some **PEFT methods** can deliver strong performance with **just a few thousand examples**

#### PEFT techniques

The existing prolific world of PEFT generally falls into **two buckets**:

- **adapter-based methods**
- **soft prompt-based methods**

> It's likely that newer buckets will be introduced in the future.

##### Adapter-based methods (additive)

**Adapter-based methods** refer to all methods that involve **additional modules to the model weights**, such as the one developed by Houlsby et al. (2019). Because adapter-based methods **involve adding parameters**, they are also called **additive methods**.

The landscape:

- **LoRA** (Hu et al., 2021) — **by far the most popular** adapter-based method, and the topic of the next sub-subsection
- **BitFit** (Zaken et al., 2021) — came out around the same time as LoRA
- **IA³** (Liu et al., 2022) — **efficient mixed-task batching** strategy makes it particularly attractive for **multi-task finetuning**. Has been shown to **outperform LoRA and even full finetuning** in some cases
- **LongLoRA** (Chen et al., 2023) — a LoRA variant that incorporates attention-modification techniques to **expand context length**

##### Soft prompt-based methods

If adapter-based methods **add trainable parameters to the model's architecture**, **soft prompt-based methods modify how the model processes the input** by introducing **special trainable tokens**.

These additional tokens are fed into the model **alongside the input tokens**. They are called **soft prompts** because, like the inputs (**hard prompts**), soft prompts also **guide the model's behaviors**.

However, soft prompts differ from hard prompts in **two ways**:

- **Hard prompts are human-readable.** They typically contain discrete tokens such as *"I"*, *"write"*, *"a"*, and *"lot"*. In contrast, **soft prompts are continuous vectors**, resembling **embedding vectors**, and are **not human-readable**
- **Hard prompts are static and not trainable**, whereas **soft prompts can be optimized through backpropagation** during the tuning process, allowing them to be adjusted for specific tasks

> Some people describe soft prompting as a **crossover between prompt engineering and finetuning**.

![Hard prompts and soft prompts can be combined to change a model's behaviors](<assets/Hard prompts and soft prompts can be combined to change a model’s behaviors.png>)

**Figure 7-9. Hard prompts and soft prompts can be combined to change a model's behaviors.**

##### Soft prompt tuning variants (confusing names)

Soft prompt tuning as a subfield is characterized by a series of **similar-sounding techniques** that can be confusing:

- **prefix-tuning** (Li and Liang, 2021)
- **P-Tuning** (Liu et al., 2021)
- **prompt tuning** (Lester et al., 2021)

They differ mainly on the **locations where the soft prompts are inserted**:

- **prefix tuning** prepends soft prompt tokens to the input at **every transformer layer**
- **prompt tuning** prepends soft prompt tokens to **only the embedded input**

Many PEFT frameworks implement them **out of the box**.

##### Popularity by GitHub issue count

To get a sense of what PEFT methods are being used, an analysis of over **1,000 open issues** on the GitHub repository `huggingface/peft` in October 2024 was conducted. The assumption is: **if someone uses a technique, they are more likely to report issues or ask questions about it**.

![The number of issues corresponding to different finetuning techniques](<assets/The number of issues corresponding to different finetuning techniques.png>)

**Figure 7-10. The number of issues corresponding to different finetuning techniques from the GitHub repository `huggingface/peft`.** *This is a proxy to estimate the popularity of each technique.*

From this analysis:

- **LoRA dominates**
- **soft prompts are less common**, but there's **growing interest** from those who want more customization than prompt engineering but who don't want to invest in full finetuning

Because of LoRA's popularity, the next sub-subsection focuses on **how LoRA works** and how it solves the challenge posed by early adapter-based methods.

#### LoRA

Unlike the original adapter method by Houlsby et al. (2019), **LoRA (Low-Rank Adaptation)** (Hu et al., 2021) incorporates additional parameters in a way that **doesn't incur extra inference latency**.

Instead of introducing **additional layers** to the base model, LoRA uses **modules that can be merged back to the original layers**.

##### How LoRA works on a weight matrix

You can apply LoRA to **individual weight matrices**. Given a weight matrix, LoRA:

- **decomposes this matrix** into the **product of two smaller matrices**
- then **updates these two smaller matrices** before merging them back to the original matrix

Consider the weight matrix **W** of dimension **`n × m`**. LoRA works as follows:

1. **First**, choose the dimension of the smaller matrices. Let **`r`** be the chosen value. Construct two matrices:
   - **A** (dimension **`n × r`**)
   - **B** (dimension **`r × m`**)
   - their product is **W_AB**, which is of the **same dimension as W**
   - **`r`** is the **LoRA rank**
2. **Add W_AB** to the original weight matrix **W** to create a new weight matrix **W′**. Use **W′** in place of W as part of the model. You can use a hyperparameter **α** to determine how much W_AB should contribute to the new matrix:

```text
W′ = W + (α / r) · W_AB
```

3. **During finetuning, update only the parameters in A and B.** W is kept intact.

![To apply LoRA to a weight matrix W, decompose it into the product of two matrices A and B](<assets/To apply LoRA to a weight matrix W, decompose it into the product of two matrices A and B.png>)

**Figure 7-11. To apply LoRA to a weight matrix W, decompose it into the product of two matrices A and B. During finetuning, only A and B are updated. W is kept intact.**

> **NOTE — Low-rank factorization**
>
> **LoRA (Low-Rank Adaptation)** is built on the concept of **low-rank factorization**, a long-standing **dimensionality reduction** technique.
>
> The key idea: **you can factorize a large matrix into a product of two smaller matrices** to reduce the number of parameters, which **reduces both the computation and memory requirements**.
>
> Example: a **9 × 9 matrix** can be factorized into the product of two matrices of dimensions **9 × 1 and 1 × 9**. The original matrix has **81 parameters**, but the two product matrices have only **18 parameters combined**.
>
> The number of columns in the first factorized matrix and the number of columns in the second factorized matrix correspond to the **rank of the factorization**. The original matrix is **full-rank**, while the two smaller matrices represent a **low-rank approximation**.
>
> While factorization can significantly reduce the number of parameters, it's **lossy** because it only **approximates** the original matrix. **The higher the rank, the more information from the original matrix the factorization can preserve.**

Like the original adapter method, LoRA is **parameter-efficient and sample-efficient**. The factorization enables LoRA to use **even fewer trainable parameters**.

> The LoRA paper showed that, for **GPT-3**, LoRA achieves **comparable or better performance with full finetuning** on several tasks while using only **~4.7M trainable parameters — 0.0027% of full finetuning**.

##### Why does LoRA work?

Parameter-efficient methods like LoRA have become so popular that many people **take them for granted**. But **why is parameter efficiency possible at all?**

> If a model requires a lot of parameters to learn certain behaviors during pre-training, shouldn't it also require a lot of parameters to change its behaviors during finetuning?

The same question can be raised for data: if a model requires a lot of data to learn a behavior, shouldn't it also require a lot of data to meaningfully change this behavior?

###### The intrinsic dimension argument

Many papers have argued that while LLMs have many parameters, they have **very low intrinsic dimensions**:

- Li et al. (2018)
- Aghajanyan et al. (2020)
- Hu et al. (2021)

They showed that **pre-training implicitly minimizes the model's intrinsic dimension**. Surprisingly, **larger models tend to have lower intrinsic dimensions after pre-training**. This suggests that **pre-training acts as a compression framework** for downstream tasks.

> In other words, **the better trained an LLM is, the easier it is to finetune the model** using a **small number of trainable parameters and a small amount of data**.

###### Why don't we use LoRA for pre-training?

You might wonder: **if low-rank factorization works so well, why don't we use LoRA for pre-training as well?**

Throughout the 2010s, many people tried training **low-rank neural networks**:

- "Low-Rank Matrix Factorization for Deep Neural Network Training with High-Dimensional Output Targets" (Sainath et al., 2013)
- "Semi-Orthogonal Low-Rank Matrix Factorization for Deep Neural Networks" (Povey et al., 2018)
- "Speeding up Convolutional Neural Networks with Low Rank Expansions" (Jaderberg et al., 2014)

**Low-rank factorization has proven to be effective at smaller scales.** Example: by applying various factorization strategies, including replacing **3 × 3 convolution with 1 × 1 convolution**, **SqueezeNet** (Iandola et al., 2016) achieves **AlexNet-level accuracy** on ImageNet using **50× fewer parameters**.

More recent attempts at **low-rank LLMs**:

- **ReLoRA** (Lialin et al., 2023) — works for transformer-based models of up to **1.3B parameters**
- **GaLore** (Zhao et al., 2024) — achieves performance comparable to a full-rank model at **1B parameters** and promising performance at **7B parameters**

> If Aghajanyan et al.'s argument is correct — that pre-training implicitly compresses a model's intrinsic dimension — **full-rank pre-training is still necessary** to sufficiently reduce the model's intrinsic dimension to a point where low-rank factorization can work.

##### LoRA configurations

To apply LoRA, you need to decide:

- **what weight matrices to apply LoRA to**
- the **rank of each factorization**

LoRA's efficiency depends not only on **what matrices** LoRA is applied to but also on the **model's architecture**, as different architectures have different weight matrices.

###### Where LoRA is most commonly applied

LoRA has been primarily used for **transformer models**. It is most commonly applied to the **four weight matrices in the attention modules**:

- **W_q** — query
- **W_k** — key
- **W_v** — value
- **W_o** — output projection

Typically, LoRA is applied **uniformly to all matrices of the same type** within a model.

###### Trade-off study from the LoRA paper

When finetuning **GPT-3 175B**, Hu et al. (2021) set their **trainable parameter budget at 18M** (0.01% of the model's total). This budget allows them to apply LoRA to:

- **one matrix** with rank **8**
- **two matrices** with rank **4**
- **all four matrices** with rank **2**

> **NOTE — Trainable parameter math**
>
> GPT-3 175B has **96 transformer layers** with a model dimension of **12,288**. Applying LoRA with `rank = 2` to all four matrices would yield `(12,288 × 2 × 2) × 4 = 196,608` trainable parameters per layer, or **18,874,368** for the whole model.

They found that **applying LoRA to all four matrices with `rank = 2` yields the best performance** on the **WikiSQL** and **MultiNLI** benchmarks.

**Table 7-5. LoRA performance with the budget of 18M trainable parameters.** *Results from LoRA (Hu et al., 2021).*

| Weight type | W_q | W_k | W_v | W_o | W_q, W_k | W_q, W_v | W_q, W_k, W_v, W_o |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Rank `r`** | 8 | 8 | 8 | 8 | 4 | 4 | 2 |
| **WikiSQL (± 0.5%)** | 70.4 | 70.0 | 73.0 | 73.2 | 71.4 | 73.7 | **73.7** |
| **MultiNLI (± 0.1%)** | 91.0 | 90.8 | 91.0 | 91.3 | 91.3 | 91.3 | **91.7** |

> If you can choose only **two attention matrices**, the **query and value matrices** generally yield the best results.

###### Beyond attention matrices

Empirical observations suggest that applying LoRA to **more weight matrices**, including the **feedforward matrices**, yields better results:

- **Databricks** showed that the **biggest performance boost** they got was from applying LoRA to **all feedforward layers** (Sooriyarachchi, 2023)
- **Fomenko et al. (2024)** noted that **feedforward-based LoRA can be complementary** to attention-based LoRA, though attention-based LoRA typically offers **greater efficacy within memory constraints**

###### Choosing the rank `r`

The beauty of LoRA is that while its performance depends on its rank, studies have shown that **a small `r`, such as between 4 and 64, is usually sufficient** for many use cases.

- a **smaller `r`** → **fewer LoRA parameters** → **lower memory footprint**
- the LoRA authors observed that, to their surprise, **increasing the value of `r` doesn't increase finetuning performance**
- Databricks reported that **increasing `r` beyond a certain value may not yield any discernible increase in quality**
- some argue that a **higher `r` might even hurt** as it can lead to **overfitting**
- however, in some cases a **higher rank might be necessary** — **Raschka (2023)** found that **`r = 256`** achieved the best performance on his tasks

###### The hyperparameter `α`

Another LoRA hyperparameter you can configure is the value **`α`** that determines how much the product **W_AB** should contribute to the new matrix during merging:

```text
W′ = W + (α / r) · W_AB
```

In practice, **`α` is often chosen so that the ratio `α / r` is typically between 1:8 and 8:1**, but the optimal ratio varies:

- if **`r` is small**, you might want **`α` to be larger**
- if **`r` is large**, you might want **`α` to be smaller**

> Experimentation is needed to determine the best **`α` / `r` combination** for your use case.

##### Serving LoRA adapters

LoRA not only lets you finetune models using **less memory and data**, but it also **simplifies serving multiple models** due to its **modularity**.

###### Two ways to serve a LoRA-finetuned model

- **Option 1 — Merge before serving:** merge the LoRA weights **A** and **B** into the original model to create the new matrix **W′** prior to serving the finetuned model. Since **no extra computation** is done during inference, **no extra latency** is added
- **Option 2 — Keep separate, merge at inference:** keep **W**, **A**, and **B** separate during serving. The process of merging A and B back to W happens **during inference**, which **adds extra latency**

> **Option 1** is generally better if you have **only one LoRA model** to serve.
> **Option 2** is generally better for **multi-LoRA serving** — serving multiple LoRA models that share the same base model.

![Keeping LoRA adapters separate allows reuse of the same full-rank matrix W in multi-LoRA serving](<assets/Keeping LoRA adapters separate allows reuse of the same full-rank matrix W in multi-LoRA serving.png>)

**Figure 7-12. Keeping LoRA adapters separate allows reuse of the same full-rank matrix W in multi-LoRA serving.**

###### Storage savings for multi-LoRA serving

Consider the scenario in which you **finetune a model for each of your customers** using LoRA. With **100 customers**, you end up with **100 finetuned models**, all sharing the **same base model**.

- with **Option 1**, you have to store **100 full-rank matrices W′**
- with **Option 2**, you only have to store **one full-rank matrix W** and **100 sets of smaller matrices (A, B)**

To put this in perspective, suppose the original matrix **W** is `4096 × 4096` (**16.8M parameters**). If LoRA's rank is **8**, the number of parameters in A and B is `4096 × 8 × 2 = 65,536`:

- **Option 1**: `16.8M × 100 = 1.68B parameters`
- **Option 2**: `16.8M + 65,536 × 100 = 23.3M parameters`

###### Fast task-switching

**Option 2 also makes it faster to switch between tasks.** Let's say you're currently serving customer X. To switch to customer Y, instead of loading this customer's full weight matrix, you only need to **load Y's LoRA adapter**, which can **significantly reduce the loading time**.

> While keeping A and B separate incurs additional latency, there are **optimization techniques** to minimize the added latency.

###### Combining multiple specialized models

Multi-LoRA serving makes it easy to **combine multiple specialized models**. Instead of having one big powerful model for multiple tasks, you can have **one LoRA adapter for each task**.

> Example: **Apple** used multiple LoRA adapters to adapt the same **3B-parameter base model** to different **iPhone features** (2024). They utilized **quantization techniques** to further reduce memory footprint, allowing **all of them on-device**.

###### LoRA adapters can be shared

The modularity of LoRA adapters means that LoRA adapters can be **shared and reused**. There are publicly available finetuned LoRA adapters that you can use the way you'd use pre-trained models. You can find them on **[Hugging Face](https://huggingface.co/)** or initiatives like **[AdapterHub](https://adapterhub.ml/)**.

###### LoRA's main drawback

The main drawback of LoRA: it **doesn't offer performance as strong as full finetuning**. It's also more challenging to do than full finetuning, as it involves **modifying the model's implementation** — requires an understanding of the model's architecture and coding skills.

However, this is usually only an issue for **less popular base models**. PEFT frameworks likely support LoRA for popular base models **right out of the box**:

- **Hugging Face's PEFT**
- **Axolotl**
- **unsloth**
- **LitGPT**

#### Quantized LoRA

The rapid rise of LoRA has led to many LoRA variations. Some aim to **reduce the number of trainable parameters even further**. However, the memory of a **LoRA adapter is minimal** compared to the memory of the model's weights. Reducing the number of LoRA parameters decreases the overall memory footprint **by only a small percentage**.

**Table 7-6. The memory needed by LoRA weights compared to that needed by the model's weights.**

| | Model's weights memory (16 bits) | LoRA trainable params (r=2, query & key matrices) | LoRA adapter memory (16 bits) |
| --- | --- | --- | --- |
| **Llama 2 (13B)** | 26 GB | 3.28M | 6.55 MB |
| **GPT-3 (175B)** | 350 GB | 18.87M | 37.7 MB |

##### QLoRA — quantize the model, not the adapter

Rather than trying to reduce LoRA's number of parameters, you can reduce memory usage more effectively by **quantizing the model's weights, activations, and/or gradients during finetuning**.

An early promising quantized version of LoRA is **QLoRA (Dettmers et al., 2023)**:

- in the original LoRA paper, during finetuning, the model's weights are stored using **16 bits**
- **QLoRA stores the model's weights in 4 bits** but **dequantizes them back into BF16** when computing the forward and backward pass

##### NF4 + paged optimizers

The **4-bit format that QLoRA uses is NF4 (NormalFloat-4)**, which quantizes values based on the insight that **pre-trained weights usually follow a normal distribution with a median of zero**.

On top of 4-bit quantization, QLoRA also uses **paged optimizers** to automatically **transfer data between the CPU and GPU** when the GPU runs out of memory — especially with **long sequence lengths**.

> These techniques allow a **65B-parameter model** to be finetuned on a **single 48 GB GPU**.

##### Guanaco results

The authors finetuned a variety of models, including **Llama 7B to 65B**, in 4-bit mode. The resulting family, **Guanaco**, showed competitive performance on both public benchmarks and comparative evaluation.

**Table 7-7. Elo ratings of Guanaco models compared to popular models in May 2023 using GPT-4 as a judge.** *Experiment from QLoRA (Dettmers et al., 2023).*

| Model | Size | Elo |
| --- | --- | --- |
| **GPT-4** | – | **1348 ± 1** |
| Guanaco 65B | 41 GB | 1022 ± 1 |
| Guanaco 33B | 21 GB | 992 ± 1 |
| Vicuna 13B | 26 GB | 974 ± 1 |
| ChatGPT | – | 966 ± 1 |
| Guanaco 13B | 10 GB | 916 ± 1 |
| Bard | – | 902 ± 1 |
| Guanaco 7B | 6 GB | 879 ± 1 |

> While **Guanaco 65B didn't outperform GPT-4**, it was often **preferred to ChatGPT**.

##### QLoRA trade-off

The main limitation of QLoRA: **NF4 quantization is expensive**. While QLoRA can reduce the memory footprint, it might **increase training time** due to the extra time required by quantization and dequantization steps.

Other quantized LoRA works:

- **QA-LoRA** (Xu et al., 2023)
- **ModuLoRA** (Yin et al., 2023)
- **IR-QLoRA** (Qin et al., 2024)

#### Encode this

- **Full finetuning** of a 7B FP16 model needs **~56 GB** just for weights + gradients + Adam state — exceeds most consumer GPUs
- **Partial finetuning** (freezing layers) still needs **~25%** of params to match full finetuning → parameter-inefficient
- **PEFT = adapter-based + soft-prompt-based** families
- **LoRA dominates**; it decomposes weight updates into **A × B** (rank `r`), updates only A and B
- **Apply LoRA to all four attention matrices with small `r`** (LoRA paper) — query+value are the best 2-matrix choice
- **Feedforward LoRA can boost quality** beyond attention-only LoRA
- **Two LoRA serving modes**: merge-into-base (one model, lowest latency) vs keep-separate (multi-LoRA serving, fast task switching, huge storage win)
- **QLoRA** = 4-bit base + BF16 dequantize on the fly + NF4 + paged optimizers → finetune **65B on a single 48 GB GPU**
- **Trade-off**: QLoRA saves memory but adds training time (quantize/dequantize overhead)

#### Recall prompt

*Why does keeping LoRA adapters separate (Option 2) become dramatically more storage-efficient than merging them in (Option 1) once you serve dozens or hundreds of customer-specific finetunes from the same base model?*

[Back to Contents](#contents)

### Model Merging and Multi-Task Finetuning

If **finetuning** lets you create a custom model by **altering a single model**, **model merging** lets you create a custom model by **combining multiple models**.

Model merging offers **greater flexibility** than finetuning alone:

- you can take **two available models** and merge them to create a new, **hopefully more useful, model**
- you can also **finetune any or all of the constituent models** before merging them

> While you don't have to further finetune the merged model, its performance can often be **improved by finetuning**. Without finetuning, **model merging can be done without GPUs**, making merging particularly attractive to **indie model developers** that don't have access to a lot of compute.

#### What model merging gives you

The goal: a single model that provides **more value than using all the constituent models separately**.

##### Added value from improved performance

If two models are good at different things on the **same task**, you can merge them into a single model that is **better than both** of them on that task.

> Imagine **one model that can answer the first 60% of the questions** and **another model that can answer the last 60% of the questions**. Combined, perhaps they can answer **80% of the questions**.

##### Added value from reduced memory footprint

If two models can do **different tasks**, they can be merged into one model that can do **both tasks but with fewer parameters**. This is particularly attractive for **adapter-based** models — given two models that were finetuned on top of the **same base model**, you can combine their **adapters into a single adapter**.

#### Use case: multi-task finetuning

One important use case of model merging is **multi-task finetuning**. Without model merging, if you want to finetune a model for multiple tasks, you generally have to follow one of these approaches:

- **Simultaneous finetuning** — create a dataset with examples for **all the tasks** and finetune the model on this dataset to make the model learn all the tasks simultaneously. However, because it's generally harder to learn multiple skills at the same time, this approach typically requires **more data and more training**
- **Sequential finetuning** — finetune the model on each task **separately but sequentially**. The assumption: it's easier for models to learn one task at a time. Unfortunately, neural networks are prone to **catastrophic forgetting** (Kirkpatrick et al., 2016) — a model can **forget how to do an old task** when it's trained on a new task

**Model merging offers another method for multi-task finetuning:**

- finetune the model on different tasks **separately but in parallel**
- once done, **merge** the different models together
- finetuning on each task separately allows the model to **learn that task better**
- because there's **no sequential learning**, there's **less risk of catastrophic forgetting**

#### Use case: on-device deployment

Model merging is also appealing when you have to deploy models to **devices** such as phones, laptops, cars, smartwatches, and warehouse robots.

On-device deployment is often challenging because of **limited on-device memory capacity**:

- instead of squeezing **multiple models** for different tasks onto a device
- you can **merge these models together into one model** that can perform multiple tasks while requiring **much less memory**

On-device deployment is necessary for use cases where:

- **data can't leave the device** (often due to privacy)
- there's **limited or unreliable internet access**

On-device deployment can also **significantly reduce inference costs**. The more computation you can offload to user devices, the less you have to pay to data centers.

#### Use case: federated learning

Model merging is one way to do **federated learning** (McMahan et al., 2016), in which **multiple devices train the same model using separate data**:

- if you deploy model X to multiple devices, each copy of X can **continue learning separately from the on-device data**
- after a while, you have **multiple copies of X**, all trained on **different data**
- you can **merge these copies together** into one new base model that contains the learning of all constituent models

#### Ensembling vs model merging

The idea of combining models together to obtain better performance started with **model ensemble methods**. **Ensembling** combines *"multiple learning algorithms to obtain better predictive performance than could be obtained from any of the constituent learning algorithms alone"*.

The difference:

- **model merging** typically involves **mixing parameters of constituent models together**
- **ensembling** typically combines **only model outputs** while keeping each constituent model intact

> Example: in ensembling, given a query, you might use **three models to generate three different answers**. Then, a **final answer** is generated based on these three answers, using a **simple majority vote** or another trainable ML module.

While ensembling can generally improve performance, it has a **higher inference cost** since it requires **multiple inference calls per request**.

![How ensembling and model merging work](<assets/How ensembling and model merging work.png>)

**Figure 7-13. How ensembling and model merging work.**

> Just like model ensembles used to dominate leaderboards, many models on top of **Hugging Face's Open LLM Leaderboard** are **merged models**.

#### High-level approaches to model merging

Many model-merging techniques are **experimental** and might become outdated as the community gains a better understanding of the underlying theory. This section focuses on the **high-level merging approaches** instead of any individual technique.

Model merging approaches differ in **how the constituent parameters are combined**. Three approaches covered here:

- **summing**
- **layer stacking**
- **concatenation**

![Three main approaches to model merging — summing, layer stacking, and concatenation](<assets/Three main approaches to model merging - summing, layer stacking, and concatenation.png>)

**Figure 7-14. Three main approaches to model merging: summing, layer stacking, and concatenation.**

> You can **mix these approaches** when merging models, e.g., summing some layers and stacking others.

#### Summing

This approach involves **adding the weight values** of constituent models together. Two summing methods are covered: **linear combination** and **spherical linear interpolation (SLERP)**.

> If the parameters in two models are in **different scales** (e.g., one model's parameter values are much larger than the other's), you can **rescale the models before summing** so that their parameter values are in the same range.

##### Linear combination

Linear combination includes both an **average** and a **weighted average**. Given two models **A** and **B**, their **weighted average** is:

```text
merged = (w_A · A + w_B · B) / (w_A + w_B)
```

![Merging parameters by averaging them](<assets/Merging parameters by averaging them.png>)

**Figure 7-15. Merging parameters by averaging them.** *(Shown when `w_A = w_B = 1`.)*

Linear combination works **surprisingly well**, given how simple it is. The idea that multiple models can be linearly combined was studied as early as the **early 1990s** (Perrone, 1993). Linear combination is often used in **federated learning** (Wang et al., 2020).

###### Combining entire models or parts of models

You can linearly combine entire models or parts of models:

- **Model soups** (Wortsman et al., 2022) showed how **averaging the entire weights** of multiple finetuned models can **improve accuracy without increasing inference time**
- More common: **linearly combining specific components**, such as their adapters

###### Most effective: same base model

Linear combination is the most effective for **models finetuned on top of the same base model**. In this case, linear combination can be viewed through the concept of **task vectors**:

- once you've finetuned a model for a specific task, **subtracting the base model from it** should give you a **vector that captures the essence of the task**
- task vectors are also called **delta parameters**
- if you finetune using LoRA, you can construct the task vector **from the LoRA weights**

###### Task arithmetic

Task vectors allow us to do **task arithmetic** (Ilharco et al., 2022):

- **adding two task vectors** to combine task capabilities
- **subtracting a task vector** to reduce specific capabilities

> Task subtraction can be useful for **removing undesirable model behaviors**, such as invasive capabilities like **facial recognition** or **biases obtained during pre-training**.

###### Combining heterogeneous models

Linear combination is straightforward when components are of the same architecture and size. However, it can also work for models that **don't share the same architecture or size**:

- if one model's layer is larger than the other, you can **project one or both layers** into the same dimension

Some people proposed **aligning models before averaging** to ensure that functionally related parameters are averaged together:

- "Model Fusion via Optimal Transport" (Singh and Jaggi, 2020)
- "Git Re-Basin: Merging Models Modulo Permutation Symmetries" (Ainsworth et al., 2022)
- "Merging by Matching Models in Task Parameter Subspaces" (Tam et al., 2023)

> While it makes sense to combine aligned parameters, **aligning parameters can be challenging to do**, so this approach is less common than naive linear combinations.

##### Spherical linear interpolation (SLERP)

Another common model summing method is **SLERP**, which is based on the mathematical operator of the same name: **Spherical LinEar inteRPolation**.

> **NOTE — Interpolation**
>
> **Interpolation** means estimating unknown values based on known values. In the case of model merging, the **unknown value is the merged model**, and the **known values are the constituent models**.
>
> **Linear combination** is one interpolation technique. **SLERP** is another.

Intuitively, you can think of each component (vector) to be merged as a **point on a sphere**:

- to merge two vectors, you first draw the **shortest path between these two points along the sphere's surface** (similar to drawing the shortest path between two cities along the Earth's surface)
- the **merged vector** of these two vectors is a **point along their shortest path**
- where exactly the point falls along the path depends on the **interpolation factor**, which you can set to be **between 0 and 1**:
  - factor values **less than 0.5** bring the merged vector **closer to the first vector**
  - a factor of **0.5** means you pick a point **exactly halfway** — the blue point in Figure 7-16

![How SLERP works for two vectors t1 and t2](<assets/How SLERP works for two vectors t1 and t2.png>)

**Figure 7-16. How SLERP works for two vectors t1 and t2.** *The red line is their shortest path on the spherical surface. Depending on the interpolation, the merged vector can be any point along this path. The blue vector is the resulting merged vector when the interpolation factor is 0.5.*

> SLERP, as a mathematical operation, is defined with **only two vectors**, which means that you can merge **only two vectors at a time**. If you want to merge more than two vectors, you can potentially do SLERP **sequentially** — e.g., merging A with B, and then merging that result with C.

#### Pruning redundant task-specific parameters

During finetuning, **many model parameters are adjusted**. However, **most of these adjustments are minor** and **don't significantly contribute to the model's performance** on the task. Adjustments that don't contribute are considered **redundant**.

In the paper **"TIES-Merging: Resolving Interference When Merging Models"**, Yadav et al. (2023) showed that you can **reset a large portion of task vector parameters with minimal performance degradation**.

> **Resetting** means changing the finetuned parameter to its original value in the base model, **effectively setting the corresponding task vector parameter to zero**.

![In Yadav et al experiments, keeping the top 20% of the task vector parameters](<assets/In Yadav et al experiments, keeping the top 20% of the task vector parameters.png>)

**Figure 7-17. In Yadav et al.'s experiments, keeping the top 20% of the task vector parameters gives comparable performance to keeping 100% of the parameters.**

These redundant parameters, **while not harmful to one model**, might be **harmful to the merged model**. Merging techniques such as **TIES** (Yadav et al., 2023) and **DARE** (Yu et al., 2023) **first prune the redundant parameters from task vectors before merging them**.

> Both papers showed that this practice can **significantly improve the quality** of the final merged models. The **more models there are to merge, the more important pruning is** because there are more opportunities for redundant parameters in one task to interfere with other tasks.

#### Layer stacking

In this approach, you take **different layers from one or more models** and **stack them on top of each other**.

> Example: you might take the **first layer from model 1** and the **second layer from model 2**.

This approach is also called **passthrough** or **frankenmerging**. It can create models with **unique architectures and numbers of parameters**.

> Unlike the merging-by-summing approach, the merged models resulting from layer stacking **typically require further finetuning** to achieve good performance.

##### Early success: Goliath-120B

One early success of frankenmerging is **Goliath-120B** (alpindale, 2023), which was merged from **two finetuned Llama 2-70B models — Xwin and Euryale**. It took **72 out of 80 layers** from each model and merged them together.

##### Layer stacking for Mixture-of-Experts (MoE)

Layer stacking can be used to train **mixture-of-experts (MoE)** models, as introduced in **"Sparse Upcycling: Training Mixture-of-Experts from Dense Checkpoints"** (Komatsuzaki et al., 2022):

- rather than training an MoE from scratch
- take a **pre-trained model** and **make multiple copies of certain layers** or modules
- a **router** is then added to send each input to the **most suitable copy**
- you then **further train the merged model along with the router** to refine their performance

![You can create an MoE model from a pre-trained model](<assets/You can create an MoE model from a pre-trained model.png>)

**Figure 7-18. You can create an MoE model from a pre-trained model.** *Image adapted from Komatsuzaki et al. (2022).*

> Komatsuzaki et al. showed that layer stacking can produce models that **outperform MoE models trained from scratch**.
>
> Using this approach, **Together AI** mixed **six weaker open source models** together to create **Mixture-of-Agents**, which achieved **comparable performance to OpenAI's GPT-4o** in some benchmarks (Wang et al., 2024).

##### Model upscaling

An interesting use case of layer stacking is **model upscaling** — the study of how to **create larger models using fewer resources**.

> Example: your team might have originally trained a model to fit on your **40 GB GPU**. However, you obtained a new machine with **80 GB**, which allows you to **serve a bigger model**. Instead of training a new model from scratch, you can use **layer stacking** to create a larger model from the existing model.

One approach is **depthwise scaling**. Kim et al. (2023) used this to create **SOLAR 10.7B** from one 7B-parameter model with 32 layers. The procedure:

1. **Make a copy** of the original pre-trained model
2. **Merge these two copies** by **summing certain layers** (summing two layers and turning them into one layer) and **stacking the rest**. The layers to be summed are carefully selected to match the target model size. For **SOLAR 10.7B**, **16 layers are summed**, leaving the final model with `32 × 2 − 16 = 48 layers`
3. **Further train** this upscaled model toward the target performance

![Use depthwise scaling to create a 48-layer model from a 32-layer model](<assets/Use depthwise scaling to create a 48-layer model from a 32-layer model.png>)

**Figure 7-19. Use depthwise scaling to create a 48-layer model from a 32-layer model.** *Image licensed under CC BY 4.0, slightly modified for readability.*

#### Concatenation

Instead of adding the parameters of the constituent models together in different manners, you can also **concatenate** them.

- the merged component's number of parameters will be the **sum of the number of parameters from all constituent components**
- if you merge **two LoRA adapters** of ranks **r₁** and **r₂**, the **merged adapter's rank will be `r₁ + r₂`**

![If you merge two LoRA adapters using concatenation](<assets/If you merge two LoRA adapters using concatenation.png>)

**Figure 7-20. If you merge two LoRA adapters using concatenation, the rank of the merged adapter will be the sum of both adapters' ranks.**

> **Concatenation isn't recommended** because it **doesn't reduce the memory footprint** compared to serving different models separately. Concatenation might give better performance, but the **incremental performance might not be worth the number of extra parameters**.

#### Encode this

- **Model merging combines models; ensembling combines outputs** — merging trades inference cost for compactness
- Three high-level merging approaches: **summing**, **layer stacking**, **concatenation** (mix-and-match allowed)
- **Linear combination** is shockingly effective, especially across models sharing a base; **task vectors** = `finetuned − base`, enabling **task arithmetic** (add capability, subtract bias)
- **SLERP** treats vectors as points on a sphere; takes only **2 vectors at a time** but works well when models are far apart
- **TIES / DARE prune redundant task vectors before merging** — critical when merging many models
- **Layer stacking** can build MoE models (sparse upcycling) and upscale dense models (SOLAR 10.7B from a 7B base)
- **Concatenation is the weakest of the three** — keeps full memory cost

#### Recall prompt

*Why can two models finetuned in parallel on different tasks, then merged, avoid the catastrophic forgetting that sequential finetuning would cause?*

[Back to Contents](#contents)

### Finetuning Tactics

This last section focuses on **more practical finetuning tactics**.

#### Finetuning frameworks and base models

While many things around finetuning — **deciding whether to finetune, acquiring data, and maintaining finetuned models** — are hard, the **actual process of finetuning is more straightforward**.

There are **three things** you need to choose:

- a **base model**
- a **finetuning method**
- a **framework for finetuning**

##### Base models

At the beginning of an AI project, when you're still exploring feasibility, it's useful to **start with the most powerful model you can afford**:

- if this model **struggles to produce good results**, weaker models are likely to perform **even worse**
- if the strongest model **meets your needs**, you can then explore weaker models, using the initial model as a **benchmark for comparison**

For finetuning, the starting models vary for different projects. OpenAI's **finetuning best practices** document gives examples of **two development paths**: the **progression path** and the **distillation path**.

###### The progression path

1. **Test your finetuning code** using the **cheapest and fastest** model to make sure the code works as expected
2. **Test your data** by finetuning a **middling** model. If the training loss doesn't go down with more data, something might be wrong
3. **Run a few more experiments with the best model** to see how far you can push performance
4. Once you have good results, do a **training run with all models** to map out the **price/performance frontier** and select the model that makes the most sense for your use case

###### The distillation path

1. **Start with a small dataset and the strongest model you can afford.** Train the best possible model with this small dataset. Because the base model is already strong, it requires **less data to achieve good performance**
2. Use this finetuned model to **generate more training data**
3. Use this new dataset to **train a cheaper model**

> Because finetuning usually comes **after experiments with prompt engineering**, by the time you start to finetune, you should already have a pretty **good understanding of different models' behaviors**.

##### Finetuning methods

- **adapter techniques like LoRA** are **cost-effective** but typically **don't deliver the same level of performance** as full finetuning
- if you're just starting with finetuning, **try something like LoRA**, and attempt full finetuning later

The finetuning methods to use also depend on your **data volume**:

- **full finetuning** typically requires **at least thousands of examples** and often many more
- **PEFT methods** can show good performance with a **much smaller dataset**
- if you have a small dataset (say, a few hundred examples), **full finetuning might not outperform LoRA**

Take into account how many finetuned models you need and how you want to serve them:

- **adapter-based methods like LoRA** allow you to **more efficiently serve multiple models** that share the same base model
- with LoRA, you only need to serve a **single full model**
- **full finetuning** requires **serving multiple full models**

##### Finetuning frameworks

The easiest way to finetune is to use a **finetuning API** where you can upload data, select a base model, and get back a finetuned model. Like model inference APIs, finetuning APIs can be provided by **model providers**, **cloud service providers**, and **third-party providers**.

Limitations:

- you're **limited to the base models that the API supports**
- the API might **not expose all the knobs** you can use for optimal finetuning performance

> Finetuning APIs are suitable for those who want something **quick and easy**, but they might be frustrating for those who want **more customization**.

You can also finetune using one of many great finetuning frameworks:

- **LLaMA-Factory**
- **unsloth**
- **PEFT**
- **Axolotl**
- **LitGPT**

They support a wide range of finetuning methods, especially **adapter-based techniques**. If you want to do **full finetuning**, many base models provide their **open source training code on GitHub** that you can clone and run with your own data.

> Doing your own finetuning gives you **more flexibility**, but you'll have to **provision the necessary compute**. If you do only adapter-based techniques, a **mid-tier GPU** might suffice for most models.

To finetune a model using **more than one machine**, you'll need a framework that helps you do **distributed training**:

- **DeepSpeed**
- **PyTorch Distributed**
- **ColossalAI**

#### Finetuning hyperparameters

Depending on the base model and the finetuning method, there are many **hyperparameters you can tune** to improve finetuning efficiency. For specific hyperparameters for your use case, check the **documentation of the base model or the finetuning framework** you use.

This section covers a few **important hyperparameters** that frequently appear.

##### Learning rate

The **learning rate** determines **how fast the model's parameters should change** with each learning step.

> If you think of learning as **finding a path toward a goal**, the learning rate is the **step size**:
>
> - if the step size is **too small**, it might take **too long** to get to the goal
> - if the step size is **too big**, you might **overstep the goal**, and the model might **never converge**

###### How to pick a learning rate

A **universal optimal learning rate doesn't exist**. You'll have to **experiment** with different learning rates, typically **between the range of `1e-7` to `1e-3`**, to see which one works best.

> A common practice: take the learning rate at the **end of the pre-training phase** and **multiply it with a constant between 0.1 and 1**.

###### Reading the loss curve

The **loss curve** can give you hints about the learning rate:

- if the loss curve **fluctuates a lot** → learning rate is likely **too big**
- if the loss curve is **stable but takes a long time to decrease** → learning rate is likely **too small**
- **increase the learning rate as high as the loss curve remains stable**

###### Varying learning rates during training

You can **vary learning rates during the training process**:

- use **larger learning rates in the beginning**
- use **smaller learning rates near the end**

Algorithms that determine how learning rates should change throughout the training process are called **learning rate schedules**.

##### Batch size

The **batch size** determines **how many examples a model learns from in each step** to update its weights:

- a batch size that is **too small** (such as fewer than **8**) can lead to **unstable training**
- a **larger batch size** helps **aggregate the signals** from different examples, resulting in **more stable and reliable updates**

###### Speed vs memory trade-off

In general:

- the **larger the batch size**, the **faster the model can go through training examples**
- the **larger the batch size**, the **more memory is needed** to run your model
- thus, **batch size is limited by the hardware** you use

> This is where you see the **cost-versus-efficiency trade-off**. More expensive compute allows faster finetuning.

###### Gradient accumulation

As of this writing, **compute is still a bottleneck** for finetuning. Often, models are so large, and memory is so constrained, that **only small batch sizes can be used**, which can lead to **unstable model weight updates**.

To address this, instead of updating the model weights **after each batch**, you can **accumulate gradients across several batches** and update the model weights **once enough reliable gradients are accumulated**.

> This technique is called **gradient accumulation**.

###### When compute isn't the bottleneck

When compute cost isn't the most important factor, you can **experiment with different batch sizes** to see which gives the best model performance.

##### Number of epochs

An **epoch** is a **pass over the training data**. The number of epochs determines **how many times each training example is trained on**.

###### Sizing epochs to dataset size

- **small datasets** may need **more epochs** than large datasets
- for a dataset with **millions of examples**, **1–2 epochs** might be sufficient
- a dataset with **thousands of examples** might still see performance improvement after **4–10 epochs**

###### Reading training vs validation loss

The difference between the **training loss** and the **validation loss** can give you hints about epochs:

- if **both** training loss and validation loss **still steadily decrease** → the model can benefit from **more epochs (and more data)**
- if the **training loss still decreases** but the **validation loss increases** → the model is **overfitting** to the training data, and you might try **lowering the number of epochs**

##### Prompt loss weight

For **instruction finetuning**, each example consists of a **prompt** and a **response**, both of which can contribute to the model's loss during training.

During inference, however:

- **prompts are usually provided by users**
- the **model only needs to generate responses**

Therefore, **response tokens should contribute more to the model's loss during training than prompt tokens**.

###### How the weight works

The **prompt loss weight** determines **how much prompts should contribute to this loss** compared to responses:

- if this weight is **100%** → prompts contribute to the loss **as much as responses**, meaning the model learns **equally from both**
- if this weight is **0%** → the model learns **only from responses**
- typically, this weight is set to **10% by default**, meaning the model learns **some from prompts but mostly from responses**

#### Encode this

- **Three choices to make**: base model, finetuning method, framework
- **OpenAI's two paths**: progression (cheap → middling → best → all) vs distillation (best → generate data → cheaper)
- **Start with LoRA** if new to finetuning; **switch to full finetuning** if data and budget justify it
- **Finetuning APIs** = easy but limited; **frameworks** (LLaMA-Factory, unsloth, PEFT, Axolotl, LitGPT) = flexible but require compute
- **Multi-machine training** = DeepSpeed / PyTorch Distributed / ColossalAI
- **Learning rate** is the most important hyperparameter — typical range `1e-7` to `1e-3`; tune by reading the loss curve; vary across training via **learning rate schedules** (warm at the start, cool at the end)
- **Batch size**: too-small (< 8) is unstable, large eats memory; **gradient accumulation** simulates large batches under tight memory budgets
- **Number of epochs**: smaller datasets need more epochs; **rising validation loss with falling training loss = overfitting**, cut epochs
- **Prompt loss weight ≈ 10% by default**: model should learn mostly from the response, not the prompt

#### Recall prompt

*Given a fixed budget and a small training set (a few hundred examples), which finetuning method and framework choice would you start with, and how would you decide when to switch to full finetuning?*

[Back to Contents](#contents)

## Summary

Outside of the evaluation chapters, **finetuning has been the most challenging chapter** in *AI Engineering*. It touched on a wide range of concepts:

- **old (transfer learning)** and **new (PEFT)**
- **fundamental (low-rank factorization)** and **experimental (model merging)**
- **mathematical (memory calculation)** and **tactical (hyperparameter tuning)**

### The process of finetuning vs the context around it

The **process of finetuning itself isn't hard**. Many finetuning frameworks handle the training process for you. These frameworks can even **suggest common finetuning methods with sensible default hyperparameters**.

However, the **context surrounding finetuning is complex**. It starts with whether you **should even finetune a model**.

The chapter covered:

- the **reasons for finetuning** and the **reasons for not finetuning**
- one question asked many times: **when to finetune** and **when to do RAG**

### Why finetuning got so much more complicated than it used to be

In its early days, **finetuning was similar to pre-training** — both involved updating the model's entire weights. However, as models increased in size:

- **full finetuning became impractical** for most practitioners
- the **more parameters to update**, the **more memory finetuning needs**
- most practitioners **don't have access to sufficient resources** (hardware, time, and data) to do full finetuning with foundation models

### Two memory-reduction strategies

Many finetuning techniques have been developed with the **same motivation**: to achieve strong performance on a minimal memory footprint:

- **PEFT** reduces finetuning's memory requirements by **reducing the number of trainable parameters**
- **Quantized training** mitigates this memory bottleneck by **reducing the number of bits needed to represent each value**

### LoRA, in particular

After giving an overview of PEFT, the chapter zoomed into **LoRA — why and how it works**. LoRA has many properties that make it popular among practitioners:

- **parameter-efficient**
- **data-efficient**
- **modular** — making it much easier to **serve and combine multiple LoRA models**

### Model merging

The idea of combining finetuned models brought the chapter to **model merging**; its goal is to **combine multiple models into one model** that works better than these models separately. The chapter discussed:

- many **use cases** of model merging — from **on-device deployment** to **model upscaling**
- general **approaches** to model merging (summing, layer stacking, concatenation)

### Closing observation

> A comment often heard from practitioners is that **finetuning is easy, but getting data for finetuning is hard**. Obtaining **high-quality annotated data**, especially **instruction data**, is challenging — and is the topic of the chapter following this one in the book.

[Back to Contents](#contents)

## Notes

The original chapter contains numerous footnotes that add color, asides, and references. They are gathered here as supplementary material rather than interspersed inline.

1. Some people call this phenomenon an **alignment tax** (Bai et al., 2020), but this term can be confused with penalties against human preference alignment.
2. Many businesses **resist changing technologies** they consider *"good enough"*. If all companies were quick to adopt more optimal solutions, **fax machines would have become obsolete by now**.
3. The author has noticed a few cases when engineers **know that finetuning isn't strictly necessary but still insist on doing it** because they want to learn how to finetune. As an engineer who likes learning new skills, the author appreciates this mindset. However, if you're in a leadership position, **it can be hard to differentiate whether finetuning is needed or wanted**.
4. **`0314`** denotes the date the GPT-4 version came out — **March 14, 2023**. The specific date stamp matters because different versions vary significantly in performance.
5. Some people (such as the authors of the **Llama 3.1 paper**, Dubey et al., 2024) adhere to *"the principle that post-training should align the model to 'know what it knows' rather than add knowledge."*
6. Other than backpropagation, a promising approach to training neural networks is **evolutionary strategy**. One example, described by **Maheswaranathan et al.**, combines **random search with surrogate gradients**, instead of using real gradients, to update model weights. Another interesting approach is **direct feedback alignment** (Arild Nøkland, 2016).
7. If a parameter is **not trainable**, it doesn't need to be updated — therefore, there's **no need to compute its gradient**.
8. Some might say that *"you're not doing AI until you've seen a `RuntimeError: CUDA out of memory` error."*
9. For inference memory calculation, see **Carol Chen's *Transformer Inference Arithmetic*** on `kipply's blog` (March 2022).
10. For training memory calculation, see **EleutherAI's *Transformer Math 101*** (Anthony et al., April 2023).
11. Google introduced **BFloat16** as *"the secret to high performance on Cloud TPUs"*.
12. **Integer formats** are also called **fixed point formats**.
13. **Range bits** are called **exponents**. **Precision bits** are called **significands**.
14. Usually the number at the end of a format's name signifies how many bits it occupies, but **TF32 actually has 19 bits, not 32 bits**. The author believes it was named so to suggest its **functional compatibility with FP32**.
15. The **FP16 and BF16 confusion continued with Llama 3.1**. See discussions on X / Threads, `llama.cpp`'s benchmark between BF16 and FP16, TheBloke's writeup, and Raschka's writeup.
16. Designing numerical formats is a **fascinating discipline**. Being able to create a **lower-precision format that doesn't compromise a system's quality** can make that system much **cheaper and faster**, enabling new use cases.
17. Another major contributor to the memory footprint of transformer-based models is the **KV cache**.
18. The **smallest possible float size** that follows all IEEE principles is **4-bit**.
19. The authors of the **Xnor-Net** paper spun off **Xnor.ai**, a startup focused on **model compression**. In early 2020, it was **acquired by Apple for a reported $200M**.
20. During training, the model's weights are updated via multiple steps. **Small rounding changes can compound** during the training process, making it difficult for the model to achieve the desirable performance. **Loss values require precise computation**: small changes in the loss value can point parameter updates in the wrong direction.
21. *Personal anecdote (the author):* much of her team's work at NVIDIA was on mixed-precision training. See *"Mixed Precision Training for NLP and Speech Recognition with OpenSeq2Seq"* (Huyen et al., NVIDIA Developer Technical Blog, October 2018).
22. In partial finetuning, it's common to **finetune the layers closest to the output layer** because those layers are usually **more task-specific**, whereas **earlier layers tend to capture more general features**.
23. The author has *"never met a single person who could explain to me, on the spot, the differences between these techniques."* (prefix-tuning vs P-Tuning vs prompt tuning)
24. To effectively use LoRA for a model, **it's necessary to understand that model's architecture**. For the exact weight composition of a model, refer to its paper.
25. As of this writing, some finetuning frameworks like **Fireworks** only allow a **maximum LoRA rank of 32**. However, this constraint is **unlikely due to performance** and **more likely due to their hardware's memory constraint**.
26. On Hugging Face, search for these adapters by tags **`adapter`**, **`peft`**, or **`LoRA`**.
27. **QLoRA isn't the only quantized LoRA work**. Many research labs have been working on quantized LoRA without publicly discussing it.
28. The author's earlier book — ***Designing Machine Learning Systems*** — has a section on *"ML on the Cloud and on the Edge."*
29. More on **ensemble methods** in *Designing Machine Learning Systems*.
30. **Averaging works** not just with weights but also with **embeddings**. Given a sentence, you can use a word embedding algorithm to generate an embedding vector for each word, then average all these word embeddings into a **sentence embedding**.
31. The assumption is that the parameters that undergo the most substantial changes during finetuning are the ones most crucial for the target task.
32. **TIES** is abbreviated from *"**T**r**I**m, **E**lect **S**ign, and merge"*; **DARE** is from *"**D**rop **A**nd **RE**scale"*. *("I know, these abbreviations pain me too." — the author)*
33. When task vectors are pruned, **they become more sparse, but the finetuned model doesn't**. Pruning, in this case, isn't to **reduce the memory footprint or inference latency**, but to **improve performance**.
34. The author debated for a long time whether to include the **concatenation technique** and decided to include it **for completeness**.
35. *Painful college anecdote (the author):* training a model overnight, only to have it crash after eight hours because she tried to save the checkpoint in a **nonexistent folder**.
36. While it's commonly acknowledged that **small batch sizes lead to unstable training**, the author wasn't able to find good explanations for **why** that's the case.
37. The first paper introducing **gradient accumulation** is hard to pin down. Its use in deep learning was mentioned as early as **2016** in *"Ako: Decentralised Deep Learning with Partial Gradient Exchange"* (Watcharapichat et al., *Proceedings of the Seventh ACM Symposium on Cloud Computing*, 2016). The concept seems to come from **distributed training**, where gradients computed on different machines need to be **accumulated and used to update the model's weights**.

[Back to Contents](#contents)

---

> *End of the Chapter 7 ("Finetuning") study companion. These notes consolidate the chapter's core ideas; the original chapter and its full citations live in **["AI Engineering" by Chip Huyen](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)**.*
