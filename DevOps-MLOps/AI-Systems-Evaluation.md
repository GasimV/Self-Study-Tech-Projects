# AI Systems Evaluation

> These notes are a structured study companion to **Chapter 3 ("Evaluation Methodology")** of the book **["AI Engineering" by Chip Huyen](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)**. They consolidate the chapter's core ideas with the same elaborative-encoding / active-recall style used in the [main `GenAI-on-Kubernetes-Study-Notes.md`](GenAI-on-Kubernetes-Study-Notes.md) and the [`Finetuning.md`](Finetuning.md) notes.

## Contents

1. [Evaluation Methodology](#evaluation-methodology)
2. [Challenges of Evaluating Foundation Models](#challenges-of-evaluating-foundation-models)
3. [Understanding Language Modeling Metrics](#understanding-language-modeling-metrics)
   - [Entropy](#entropy)
   - [Cross Entropy](#cross-entropy)
   - [Bits-per-Character and Bits-per-Byte](#bits-per-character-and-bits-per-byte)
   - [Perplexity](#perplexity)
   - [Perplexity Interpretation and Use Cases](#perplexity-interpretation-and-use-cases)
   - [How to Use a Language Model to Compute a Text's Perplexity](#how-to-use-a-language-model-to-compute-a-texts-perplexity)
4. [Exact Evaluation](#exact-evaluation)
   - [Functional Correctness](#functional-correctness)
   - [Similarity Measurements Against Reference Data](#similarity-measurements-against-reference-data)
     - [Exact Match](#exact-match)
     - [Lexical Similarity](#lexical-similarity)
     - [Semantic Similarity](#semantic-similarity)
   - [Introduction to Embedding](#introduction-to-embedding)
5. [Notes](#notes)

## Evaluation Methodology

The **more AI is used, the more opportunity there is for catastrophic failure**. We've already seen many failures in the short time that foundation models have been around:

- A man **committed suicide** after being encouraged by a chatbot.
- Lawyers submitted **false evidence hallucinated by AI**.
- **Air Canada** was ordered to pay damages when its AI chatbot gave a passenger false information.

> Without a way to **quality control AI outputs**, the risk of AI might **outweigh its benefits** for many applications.

As teams rush to adopt AI, many quickly realize that the **biggest hurdle** to bringing AI applications to reality is **evaluation**. For some applications, figuring out evaluation can take up the **majority of the development effort**.[^1]

Because evaluation is so important and so complex, the original book devotes **two chapters** to it:

- **This chapter** covers the different **evaluation methods** used to evaluate open-ended models, how these methods work, and their **limitations**.
- The **next chapter** focuses on how to use these methods to **select models** for your application and to **build an evaluation pipeline** to evaluate your application.

### Evaluation in the context of a whole system

While evaluation is discussed in its own chapters, **evaluation has to be considered in the context of a whole system, not in isolation**. Evaluation aims to:

- **mitigate risks**, and
- **uncover opportunities**.

To mitigate risks, you first need to **identify the places where your system is likely to fail** and design your evaluation around them. Often, this may require **redesigning your system to enhance visibility into its failures**.

> Without a clear understanding of **where your system fails**, no amount of evaluation metrics or tools can make the system robust.

### Why systematic evaluation matters

Before diving into evaluation methods, it's important to acknowledge the **challenges** of evaluating foundation models. Because evaluation is difficult, many people settle for:

- **word of mouth**[^2] — e.g., *"someone says that model X is good,"* or
- **eyeballing the results**.[^3]

This creates **even more risk** and **slows application iteration**. Instead, we need to invest in **systematic evaluation** to make results more reliable.

Since many foundation models have a **language model component**, this chapter gives a quick overview of the metrics used to evaluate language models — including **cross entropy** and **perplexity**. These metrics are essential for **guiding training and finetuning** and are frequently reused in many evaluation methods.

### Open-endedness, human evaluators, and automation

Evaluating foundation models is especially challenging because they are **open-ended**. Key best practices:

- **Human evaluators** remain a necessary option for many applications.
- Because human annotations are **slow and expensive**, the goal is to **automate** the process.
- This book focuses on **automatic evaluation**, which includes both **exact** and **subjective** evaluation.

> The **rising star of subjective evaluation** is **AI as a judge** — the approach of using AI to evaluate AI responses. It's *subjective* because the score depends on **what model and prompt the AI judge uses**. While this approach is gaining rapid traction in industry, it also invites **intense opposition** from those who believe that AI isn't trustworthy enough for this important task.

[Back to Contents](#contents)

## Challenges of Evaluating Foundation Models

Evaluating ML models has **always been difficult**. With the introduction of foundation models, evaluation has become **even more so**. There are multiple reasons why evaluating foundation models is more challenging than evaluating traditional ML models.

### 1. The smarter the model, the harder it is to evaluate

The more intelligent AI models become, the **harder it is to evaluate them**:

- Most people can tell if a **first grader's** math solution is wrong. **Few** can do the same for a **PhD-level** math solution.[^4]
- It's easy to tell a book summary is bad if it's **gibberish**, but much harder if the summary is **coherent**. To validate quality, you might need to **read the book first**.

> **Corollary:** evaluation can be **much more time-consuming** for sophisticated tasks. You can no longer evaluate a response based on **how it sounds** — you'll also need to **fact-check, reason, and incorporate domain expertise**.

### 2. Open-endedness undermines evaluation against ground truths

The open-ended nature of foundation models undermines the traditional approach of **evaluating a model against ground truths**:

- With **traditional ML**, most tasks are **close-ended**. A classification model can only output among the expected categories. If the expected output is category **X** but the model outputs category **Y**, the model is **wrong**.
- For an **open-ended task**, a given input can have **so many possible correct responses**. It's **impossible** to curate a comprehensive list of correct outputs to compare against.

### 3. Foundation models are black boxes

Most foundation models are treated as **black boxes**, either because:

- model providers **choose not to expose** model details, or
- application developers **lack the expertise** to understand them.

Details such as the **model architecture**, **training data**, and **training process** can reveal a lot about a model's strengths and weaknesses. Without those details, you can evaluate a model **only by observing its outputs**.

### 4. Public benchmarks saturate quickly

Publicly available evaluation benchmarks have proven **inadequate** for evaluating foundation models. Ideally, benchmarks should **capture the full range** of model capabilities and **evolve** as AI progresses.

> A benchmark becomes **saturated** for a model once the model achieves a **perfect score**. With foundation models, benchmarks are becoming saturated **fast**.

| Original benchmark | Year | Saturated / replaced by | Year |
| --- | --- | --- | --- |
| **GLUE** (General Language Understanding Evaluation) | 2018 | **SuperGLUE** | 2019 |
| **NaturalInstructions** | 2021 | **Super-NaturalInstructions** | 2022 |
| **MMLU** | 2020 | **MMLU-Pro** | 2024 |

GLUE became saturated in **just a year**, necessitating SuperGLUE. MMLU — a strong benchmark that many early foundation models relied on — was largely replaced by **MMLU-Pro**.

### 5. The scope of evaluation has expanded for general-purpose models

- With **task-specific models**, evaluation means measuring a model's performance on its **trained task**.
- With **general-purpose models**, evaluation is not only about assessing performance on **known tasks** but also about **discovering new tasks** the model can do — including tasks that **extend beyond human capabilities**.

> Evaluation takes on the **added responsibility** of exploring the **potential and limitations** of AI.

### The good news, and the bad news

**The good news:** the new challenges of evaluation have prompted **many new methods and benchmarks**. The number of published papers on **LLM evaluation grew exponentially** every month in the first half of 2023 — from **2 papers a month** to almost **35 papers a month**.

![The trend of LLMs evaluation papers over time](<assets/The trend of LLMs evaluation papers over time.png>)

**Figure 3-1. The trend of LLM evaluation papers over time.** *(Image from Chang et al., 2023.)*

In the author's own analysis of the **top 1,000 AI-related GitHub repositories** (ranked by stars), she found **over 50 repositories dedicated to evaluation** (as of May 2024).[^5] Plotting evaluation repositories by their creation date, the growth curve also looks **exponential**.

![Number of open source evaluation repositories among the 1,000 most popular AI repositories on GitHub](<assets/Number of open source evaluation repositories.png>)

**Figure 3-2. Number of open source evaluation repositories among the 1,000 most popular AI repositories on GitHub.**

**The bad news:** despite the increased interest, **evaluation lags behind** the rest of the AI engineering pipeline:

> **Balduzzi et al. (DeepMind)** noted that *"developing evaluations has received little systematic attention compared to developing algorithms."* Experiment results are **almost exclusively** used to improve algorithms and are **rarely** used to improve evaluation.

Recognizing the lack of investment, **Anthropic** called on policymakers to **increase government funding and grants** both for developing new evaluation methodologies and for analyzing the robustness of existing evaluations.

The number of **tools for evaluation** is also small compared to the number of tools for **modeling and training** and **AI orchestration**.

![Evaluation lags behind other aspects of AI engineering in terms of open source tools](<assets/evaluation lags behind other aspects of AI engineering.png>)

**Figure 3-3. According to data sourced from the author's list of the 1,000 most popular AI repositories on GitHub, evaluation lags behind other aspects of AI engineering in terms of open source tools.**

> **Inadequate investment leads to inadequate infrastructure**, making it hard for people to carry out systematic evaluations.

When asked how they evaluate their AI applications, many people said they just **eyeballed the results**. Many keep a **small set of go-to prompts** curated **ad hoc** — based on the curator's personal experience instead of the application's needs. You might get away with this when getting a project off the ground, but it **won't be sufficient for application iteration**. This book focuses on a **systematic approach** to evaluation.

[Back to Contents](#contents)

## Understanding Language Modeling Metrics

Foundation models **evolved out of language models**, and many still have language models as their main components. For these models, the **performance of the language model component** tends to be **well correlated** with the foundation model's performance on **downstream applications** ([Liu et al., 2023](https://arxiv.org/abs/2305.14342)). Therefore, a rough understanding of language modeling metrics can be **quite helpful** for understanding downstream performance.[^6]

As discussed in Chapter 1, language modeling has been around for decades, popularized by **Claude Shannon** in his 1951 paper **["Prediction and Entropy of Printed English"](https://archive.org/details/bstj30-1-50)**. The metrics used to guide language model development **haven't changed much** since then:

- Most **autoregressive** language models are trained using **cross entropy** or its relative, **perplexity**.
- In papers and model reports, you'll also see **bits-per-character (BPC)** and **bits-per-byte (BPB)** — both variations of cross entropy.

> All four metrics — **cross entropy, perplexity, BPC, and BPB** — are **closely related**. If you know the value of one, you can compute the other three, given the necessary information. While called *language modeling metrics*, they apply to **any model that generates sequences of tokens**, including **non-text tokens**.

Recall that a language model **encodes statistical information** about languages (how likely a token is to appear in a given context). Statistically, given the context **"I like drinking ___"**, the next word is more likely to be **"tea"** than **"charcoal"**. The more statistical information a model captures, the **better it predicts the next token**.

In ML lingo, a language model **learns the distribution of its training data**. The better it learns:

- the better it predicts what comes next in the training data, and
- the **lower its training cross entropy**.

> As with any ML model, you care about performance not just on the **training data** but also on your **production data**. In general, the **closer your data is to a model's training data**, the better the model can perform on your data.

> **NOTE — This section is math-heavy**
>
> Compared to the rest of the book, this section is math-heavy. If you find it confusing, feel free to **skip the math** and focus on **how to interpret these metrics**. Even if you're not training or finetuning models, understanding these metrics helps with **choosing which models to use** for your application, and they occasionally power certain **evaluation** and **data deduplication** techniques.

### Entropy

**Entropy** measures **how much information, on average, a token carries**. The higher the entropy, the **more information each token carries**, and the **more bits** are needed to represent a token.[^7]

Imagine you want to create a language to describe **positions within a square**:

- **(a)** If your language has only **two tokens**, each can tell you whether a position is **upper** or **lower**. Since there are only two tokens, **one bit** is sufficient. The entropy of this language is **1**.
- **(b)** If your language has **four tokens**, each gives a more specific position — **upper-left, upper-right, lower-left, lower-right**. Since there are now four tokens, you need **two bits**. The entropy of this language is **2**.

![Two languages describe positions within a square](<assets/Two languages describe positions within a square.png>)

**Figure 3-4. Two languages describe positions within a square. Compared to the language on the left (a), the tokens on the right (b) carry more information, but they need more bits to represent them.**

> Intuitively, **entropy measures how difficult it is to predict what comes next** in a language. The **lower** a language's entropy (the less information each token carries), the **more predictable** that language.

In the example, the language with **two tokens** is easier to predict than the one with four (you choose among two options instead of four). This is similar to how, if you can **perfectly predict** what someone will say next, what they say carries **no new information**.

### Cross Entropy

When you train a language model on a dataset, your goal is to get the model to **learn the distribution of the training data** — in other words, to **predict what comes next** in the training data. A language model's **cross entropy on a dataset** measures **how difficult it is for the model to predict what comes next** in that dataset.

A model's cross entropy on the training data depends on **two qualities**:

1. The training data's **predictability**, measured by the **training data's entropy**.
2. How the **distribution captured by the model** diverges from the **true distribution** of the training data.

Entropy and cross entropy share the same notation, $H$. Let **$P$** be the **true distribution** of the training data, and **$Q$** be the **distribution learned by the language model**. Accordingly:

- The training data's **entropy** is:

$$H(P) = -\sum_{x} P(x) \log_2 P(x)$$

- The divergence of $Q$ with respect to $P$ is measured using the **Kullback–Leibler (KL) divergence**:

$$D_{KL}(P \parallel Q) = \sum_{x} P(x) \log_2 \frac{P(x)}{Q(x)}$$

- The model's **cross entropy** with respect to the training data is therefore:

$$H(P, Q) = H(P) + D_{KL}(P \parallel Q) = -\sum_{x} P(x) \log_2 Q(x)$$

> **Cross entropy isn't symmetric.** The cross entropy of $Q$ with respect to $P$ — $H(P, Q)$ — is **different** from the cross entropy of $P$ with respect to $Q$ — $H(Q, P)$.

A language model is trained to **minimize its cross entropy** with respect to the training data. If the model learns **perfectly**:

- the model's cross entropy will be **exactly the same** as the **entropy of the training data**, and
- the KL divergence $D_{KL}(P \parallel Q)$ will be **0**.

> You can think of a model's **cross entropy** as its **approximation of the entropy** of its training data.

### Bits-per-Character and Bits-per-Byte

One **unit** of entropy and cross entropy is **bits**. If the cross entropy of a language model is **6 bits**, the model needs **6 bits to represent each token**.

Since different models use **different tokenization methods** (one uses words as tokens, another uses characters), the **number of bits per token isn't comparable** across models. Some use **bits-per-character (BPC)** instead:

$$\text{BPC} = \frac{\text{bits per token}}{\text{characters per token}}$$

> If the number of bits per token is **6** and, on average, each token consists of **2 characters**, the BPC is $6 / 2 = 3$.

One complication with BPC arises from **different character encoding schemes**:

- With **ASCII**, each character is encoded using **7 bits**.
- With **UTF-8**, a character can be encoded using **anywhere between 8 and 32 bits**.

A more standardized metric is **bits-per-byte (BPB)** — the number of bits a model needs to represent **one byte** of the original training data. If the BPC is **3** and each character is **7 bits** (i.e., $\tfrac{7}{8}$ of a byte), then:

$$\text{BPB} = \frac{\text{BPC}}{\text{bytes per character}} = \frac{3}{7/8} = 3.43$$

> Cross entropy tells us **how efficient a language model will be at compressing text**. If the BPB of a model is **3.43** — meaning it can represent each original byte (8 bits) using **3.43 bits** — this model can compress the original training text to **less than half** its original size.

### Perplexity

**Perplexity** is the **exponential** of entropy and cross entropy. It is often shortened to **PPL**.

- Given a dataset with the true distribution $P$, its **perplexity** is:

$$\text{PPL}(P) = 2^{H(P)}$$

- The **perplexity of a language model** (with learned distribution $Q$) on this dataset is:

$$\text{PPL}(P, Q) = 2^{H(P, Q)}$$

> If **cross entropy** measures how difficult it is for a model to predict the next token, **perplexity** measures the **amount of uncertainty** it has when predicting the next token. **Higher uncertainty** means **more possible options** for the next token.

Consider a language model trained to encode the **4 position tokens** from Figure 3-4 (b) **perfectly**. Its cross entropy is **2 bits**. When predicting a position in the square, it must choose among $2^2 = 4$ possible options. Thus, this model has a **perplexity of 4**.

So far we've used **bit** as the unit, where each bit represents **2 unique values** — hence the **base of 2** in the equation above. Popular ML frameworks, including **TensorFlow** and **PyTorch**, use **nat (natural log)** as the unit. Nat uses the base of **$e$**, the base of the natural logarithm.[^8] With nat as the unit, perplexity is the exponential of $e$:

$$\text{PPL}(P, Q) = e^{H(P, Q)}$$

> Due to the **confusion around bit and nat**, many people report **perplexity**, instead of cross entropy, when reporting their language models' performance.

### Perplexity Interpretation and Use Cases

Cross entropy, perplexity, BPC, and BPB are all **variations of a language model's predictive accuracy**. The **more accurately** a model predicts a text, the **lower** these metrics are. In this book, **perplexity** is the default language modeling metric.

> Remember: the **more uncertainty** the model has in predicting what comes next in a given dataset, the **higher** the perplexity.

What counts as a **good perplexity value** depends on the **data itself** and **how perplexity is computed** (such as how many previous tokens the model has access to). Some general rules:

- **More structured data gives lower expected perplexity.** More structured data is more predictable. For example, **HTML code** is more predictable than everyday text — if you see an opening tag like `<head>`, you can predict a closing `</head>` nearby. So the expected perplexity on HTML should be **lower** than on everyday text.
- **The bigger the vocabulary, the higher the perplexity.** The more possible tokens, the harder it is to predict the next one. A model's perplexity on a **children's book** will likely be lower than on **War and Peace**. For the same English dataset, **character-based** perplexity will be lower than **word-based** perplexity, because there are fewer possible characters than words.
- **The longer the context length, the lower the perplexity.** More context means less uncertainty. In **1951, Claude Shannon** evaluated his model's cross entropy by predicting the next token conditioned on **up to 10 previous tokens**. As of this writing, perplexity is typically computed conditioned on **500–10,000 previous tokens** (and possibly more), upper-bounded by the model's **maximum context length**.

> For reference, it's not uncommon to see perplexity values **as low as 3 or even lower**. If all tokens in a hypothetical language were equally likely, a perplexity of **3** means the model has a **1 in 3 chance** of predicting the next token correctly. Given that a model's vocabulary is in the order of **10,000s and 100,000s**, these odds are **incredible**.

#### Perplexity as a proxy for capability

Other than guiding training, perplexity is useful in many parts of an AI engineering workflow. First, **perplexity is a good proxy for a model's capabilities**. If a model is bad at predicting the next token, its **downstream performance** will likely be bad too.

**OpenAI's GPT-2 report** shows that **larger (more powerful) models consistently give lower perplexity** across a range of datasets.

**Table 3-1. Larger GPT-2 models consistently give lower perplexity on different datasets.** *(Source: OpenAI, 2019.)*

| Model | LAMBADA (PPL) ↓ | LAMBADA (ACC) ↑ | CBT-CN (ACC) ↑ | CBT-NE (ACC) ↑ | WikiText2 (PPL) ↓ | PTB (PPL) ↓ | enwik8 (BPB) ↓ | text8 (BPC) ↓ | WikiText103 (PPL) ↓ | 1BW (PPL) ↓ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **SOTA** | 99.8 | 59.23 | 85.7 | 82.3 | 39.14 | 46.54 | 0.99 | 1.08 | 18.3 | **21.8** |
| **117M** | 35.13 | 45.99 | 87.65 | 83.4 | 29.41 | 65.85 | 1.16 | 1.17 | 37.50 | 75.20 |
| **345M** | 15.60 | 55.48 | 92.35 | 87.1 | 22.76 | 47.33 | 1.01 | 1.06 | 26.37 | 55.72 |
| **762M** | 10.87 | 60.12 | 93.45 | 88.0 | 19.93 | 40.31 | 0.97 | 1.02 | 22.05 | 44.575 |
| **1542M** | **8.63** | **63.24** | 93.30 | **89.05** | **18.34** | **35.76** | **0.93** | **0.98** | **17.48** | 42.16 |

> Sadly, following the trend of companies being increasingly **secretive about their models**, many have **stopped reporting** their models' perplexity.

#### Detecting contamination, deduplicating, and spotting abnormal text

Recall that perplexity measures how difficult it is for a model to predict a given text. For a given model, perplexity is **lowest for texts the model has seen and memorized during training**. This makes perplexity useful for:

- **Detecting data contamination** — if a model's perplexity on a **benchmark's data is low**, that benchmark was **likely included in the model's training data**, making the model's performance on it **less trustworthy**.
- **Deduplicating training data** — e.g., add new data to an existing training dataset **only if its perplexity is high** (i.e., it's genuinely new).
- **Detecting abnormal text** — perplexity is **highest** for unpredictable texts, such as unusual ideas (*"my dog teaches quantum physics in his free time"*) or gibberish (*"home cat go eye"*).

> **WARNING — Perplexity is a weak proxy after post-training**
>
> Perplexity might **not** be a great proxy for evaluating models that have been **post-trained** using techniques like **SFT** and **RLHF**.[^9] Post-training teaches models **how to complete tasks**. As a model gets better at completing tasks, it might get **worse at predicting the next token**, so a model's perplexity **typically increases after post-training** — some say *post-training collapses entropy*. Similarly, **quantization** (reducing a model's numerical precision and memory footprint) can change perplexity in **unexpected ways**.[^10]

> Perplexity and its related metrics help us understand the performance of the **underlying language model**, which is a **proxy** for downstream performance. The rest of the chapter discusses how to measure a model's **downstream performance directly**.

### How to Use a Language Model to Compute a Text's Perplexity

A model's perplexity with respect to a text measures **how difficult it is for the model to predict that text**. Given a language model $X$ and a sequence of tokens $[x_1, x_2, \ldots, x_n]$, $X$'s perplexity for this sequence is:

$$P(x_1, x_2, \ldots, x_n)^{-\frac{1}{n}} = \left( \frac{1}{P(x_1, x_2, \ldots, x_n)} \right)^{\frac{1}{n}} = \left( \prod_{i=1}^{n} \frac{1}{P(x_i \mid x_1, \ldots, x_{i-1})} \right)^{\frac{1}{n}}$$

where $P(x_i \mid x_1, \ldots, x_{i-1})$ denotes the **probability** that $X$ assigns to the token $x_i$ given the previous tokens $x_1, \ldots, x_{i-1}$.

> To compute perplexity, you need access to the **probabilities (or logprobs)** the language model assigns to each next token. Unfortunately, **not all commercial models expose their logprobs**, as discussed in Chapter 2.

[Back to Contents](#contents)

## Exact Evaluation

When evaluating models' performance, it's important to differentiate between **exact** and **subjective** evaluation.

- **Exact evaluation** produces judgment **without ambiguity**. If the answer to a multiple-choice question is **A** and you pick **B**, your answer is **wrong** — no ambiguity.
- **Subjective evaluation** depends on **who grades**. Essay grading is subjective: an essay's score depends on who grades it, and the same grader, asked twice some time apart, can give the **same essay different scores**. Grading can become *more* exact with **clear guidelines**.

> As you'll see in the next section, **AI as a judge** is **subjective** — the result can change based on the **judge model** and the **prompt**.

This section covers **two evaluation approaches that produce exact scores**:

1. **Functional correctness**
2. **Similarity measurements against reference data**

> **NOTE — Why focus on open-ended responses?**
>
> This section focuses on evaluating **open-ended responses** (arbitrary text generation), not **close-ended responses** (such as classification). This is **not** because foundation models aren't used for close-ended tasks — in fact, many foundation model systems have at least a **classification component**, typically for **intent classification or scoring**. The focus is on open-ended evaluation because **close-ended evaluation is already well understood**.

### Functional Correctness

**Functional correctness** evaluation means evaluating a system based on **whether it performs the intended functionality**:

- If you ask a model to **create a website**, does the generated website **meet your requirements**?
- If you ask a model to **make a reservation** at a certain restaurant, does the model **succeed**?

> Functional correctness is the **ultimate metric** for evaluating any application — it measures whether your application **does what it's intended to do**. However, it **isn't always straightforward to measure**, and its measurement **can't always be automated**.

#### Code generation: execution accuracy

**Code generation** is an example of a task where functional correctness measurement **can** be automated — sometimes called **execution accuracy**. Say you ask a model to write a Python function, `gcd(num1, num2)`, to find the greatest common denominator of two numbers. The generated code can be fed into a **Python interpreter** to check whether it's valid and, if so, whether it produces the correct result:

```python
# Given the pair (num1=15, num2=20):
gcd(15, 20)  # must return 5 — the correct answer
# If it returns anything else, the function is wrong.
```

Long before AI was used for writing code, **automatically verifying code's functional correctness** was standard practice in software engineering. Code is typically validated with **unit tests**, where it is executed in different scenarios to ensure it generates the expected outputs. This is how coding platforms like **LeetCode** and **HackerRank** validate submitted solutions.

Popular benchmarks that use functional correctness as their metric include:

- **Code generation** — OpenAI's **HumanEval** and Google's **MBPP** (Mostly Basic Python Problems Dataset).
- **Text-to-SQL** (generating SQL from natural language) — **Spider** (Yu et al., 2018), **BIRD-SQL** (Li et al., 2023), and **WikiSQL** (Zhong et al., 2017).

A benchmark problem comes with a set of **test cases**. Each test case consists of a **scenario** the code should run and the **expected output** for that scenario. Here's an example of a problem and its test cases in **HumanEval**:

**Problem**

```python
from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each
    other than given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
```

**Test cases** (each `assert` statement represents a test case)

```python
def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 1.0) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 0.5) == False
```

#### The pass@k metric

When evaluating a model, for each problem a number of code samples — denoted as **$k$** — are generated. A model **solves a problem** if **any** of the $k$ samples it generated **pass all** of that problem's test cases. The final score, called **`pass@k`**, is the **fraction of solved problems** out of all problems.

> If there are **10 problems** and a model solves **5** with $k = 3$, then that model's **`pass@3`** score is **50%**.

The **more code samples** a model generates, the **more chance** it has at solving each problem, hence the **greater** the final score. So, in expectation:

$$\text{pass@1} \leq \text{pass@3} \leq \text{pass@10}$$

#### Beyond code: measurable objectives

Another category of tasks whose functional correctness can be automatically evaluated is **game bots**. If you create a bot to play **Tetris**, you can tell how good it is by **the score it gets**.

> Tasks with **measurable objectives** can typically be evaluated using functional correctness. For example, if you ask AI to **schedule your workloads to optimize energy consumption**, the AI's performance can be measured by **how much energy it saves**.[^11]

### Similarity Measurements Against Reference Data

If the task you care about **can't** be automatically evaluated using functional correctness, a common approach is to evaluate AI's outputs **against reference data**. For example, to evaluate a French→English translation, you compare the generated English translation against the **correct** English translation.

Each example in the reference data follows the format:

```text
(input, reference responses)
```

- An input can have **multiple reference responses** — e.g., multiple valid English translations of a French sentence.
- Reference responses are also called **ground truths** or **canonical responses**.
- Metrics that **require** references are **reference-based**; metrics that **don't** are **reference-free**.

> Because this approach requires reference data, it's **bottlenecked** by how much and how fast reference data can be generated. Reference data is typically generated by **humans** and increasingly by **AIs**.

Using **human-generated** data as the reference means we treat **human performance as the gold standard**, and AI is measured against it. Human-generated data can be **expensive and time-consuming**, leading many to use **AI** to generate reference data instead. AI-generated data might still need **human review**, but reviewing is **far less labor** than generating from scratch.

Generated responses that are **more similar** to the reference responses are considered **better**. There are **four ways** to measure the similarity between two open-ended texts:

1. **Asking an evaluator** (human or AI) to judge whether two texts are the same.
2. **Exact match** — whether the generated response matches one of the reference responses **exactly**.
3. **Lexical similarity** — how similar the generated response **looks** to the reference responses.
4. **Semantic similarity** — how close the generated response is to the reference responses in **meaning**.

> Two responses can be compared by **human** or **AI** evaluators. AI evaluators are increasingly common and are the focus of the next section.

This section focuses on **hand-designed metrics**: exact match, lexical similarity, and semantic similarity. Scores by **exact matching are binary** (match or not), whereas the other two are on a **sliding scale** (e.g., between 0 and 1, or between –1 and 1). Despite the ease and flexibility of AI as a judge, hand-designed similarity measurements are **still widely used** in industry for their **exact nature**.

> **NOTE — Similarity measurements have many uses beyond evaluation**
>
> You can also use similarity measurements for many other use cases, including:
>
> - **Retrieval and search** — find items similar to a query.
> - **Ranking** — rank items by how similar they are to a query.
> - **Clustering** — cluster items by how similar they are to each other.
> - **Anomaly detection** — detect items that are the **least** similar to the rest.
> - **Data deduplication** — remove items that are **too similar** to other items.
>
> These techniques come up again throughout the book.

#### Exact Match

It's considered an **exact match** if the generated response matches one of the reference responses **exactly**. Exact matching works for tasks that expect **short, exact responses** — simple math problems, common-knowledge queries, and trivia-style questions:

- *"What's 2 + 3?"*
- *"Who was the first woman to win a Nobel Prize?"*
- *"What's my current account balance?"*
- *"Fill in the blank: Paris to France is like ___ to England."*

One **variation** accepts any output that **contains** the reference response as a match. For *"What's 2 + 3?"* with reference `"5"`, this variation accepts `"The answer is 5"` and `"2 + 3 is 5"`.

> **However**, this variation can accept the **wrong** solution. For *"What year was Anne Frank born?"* the correct response is **1929** (she was born June 12, 1929). If the model outputs **"September 12, 1929"**, the correct year is included, but the output is **factually wrong**.

Beyond simple tasks, exact match **rarely works**. Given the French sentence **"Comment ça va?"**, there are multiple valid English translations — *"How are you?"*, *"How is everything?"*, *"How are you doing?"* If the reference set contains only those three and the model generates **"How is it going?"**, it's marked **wrong**. The longer and more complex the original text, the more possible translations there are. It's **impossible to enumerate** all valid responses, so for complex tasks **lexical** and **semantic similarity** work better.

#### Lexical Similarity

**Lexical similarity** measures **how much two texts overlap**. You first break each text into smaller **tokens**.

In its simplest form, lexical similarity counts **how many tokens two texts have in common**. Consider the reference response **"My cats scare the mice"** and two generated responses (assume each token is a word):

| Generated response | Overlapping words | Similarity score |
| --- | --- | --- |
| **A.** "My cats eat the mice" | 4 of 5 | **80%** |
| **B.** "Cats and mice fight all the time" | 3 of 5 | **60%** |

Response **A** is therefore considered **more similar** to the reference.

**Approximate string matching** (colloquially **fuzzy matching**) measures similarity by counting how many **edits** are needed to convert one text into another — a number called **edit distance**. The usual three edit operations are:

- **Deletion:** `"brad"` → `"bad"`
- **Insertion:** `"bad"` → `"bard"`
- **Substitution:** `"bad"` → `"bed"`

Some fuzzy matchers also treat **transposition** — swapping two letters (`"mats"` → `"mast"`) — as an edit; others count each transposition as **two** operations (one deletion + one insertion).

> For example, `"bad"` is **one** edit to `"bard"` and **three** edits to `"cash"`, so `"bad"` is considered **more similar** to `"bard"` than to `"cash"`.

**N-gram similarity** measures overlap based on **sequences of tokens (n-grams)** instead of single tokens. A **1-gram (unigram)** is a token; a **2-gram (bigram)** is a set of two tokens. **"My cats scare the mice"** consists of four bigrams: *"my cats"*, *"cats scare"*, *"scare the"*, *"the mice"*. You measure what percentage of n-grams in the reference responses also appear in the generated response.[^12]

Common lexical-similarity metrics are **BLEU**, **ROUGE**, **METEOR++**, **TER**, and **CIDEr** — they differ in exactly how overlap is calculated. Before foundation models, **BLEU** and **ROUGE** were common, especially for translation. Since the rise of foundation models, **fewer benchmarks use lexical similarity**; examples that still do include **WMT**, **COCO Captions**, and **GEMv2**.

**Drawbacks of lexical similarity:**

- It requires curating a **comprehensive set of reference responses**. A good response can get a **low score** if the reference set contains nothing similar. On some benchmark examples, **Adept** found that its model **Fuyu** performed poorly **not because its outputs were wrong**, but because **correct answers were missing** in the reference data.
- **References can be wrong.** The organizers of the **WMT 2023 Metrics shared task** reported finding **many bad reference translations**. Low-quality reference data is one reason **reference-free metrics** were strong contenders against reference-based metrics in correlation to human judgment (Freitag et al., 2023).
- **Higher lexical similarity doesn't always mean a better response.** On **HumanEval**, OpenAI found that **BLEU scores for incorrect and correct solutions were similar** — optimizing for BLEU isn't the same as optimizing for **functional correctness** (Chen et al., 2021).

![An example where Fuyu generated a correct caption but was given a low score because of the limitation of reference captions](<assets/An example where Fuyu generated a correct option but.png>)

**Figure 3-5. An example where Fuyu generated a correct caption but was given a low score because of the limitation of reference captions.**

#### Semantic Similarity

Lexical similarity measures whether two texts **look** similar, **not** whether they **mean** the same thing:

- *"What's up?"* and *"How are you?"* — **lexically different** (little word overlap), but **semantically close**.
- *"Let's eat, grandma"* and *"Let's eat grandma"* — **lexically similar**, but mean **two completely different things**.

**Semantic similarity** aims to compute similarity **in meaning**. This first requires transforming a text into a numerical representation — an **embedding**. For example, *"the cat sits on a mat"* might be represented as `[0.11, 0.02, 0.54]`. Semantic similarity is therefore also called **embedding similarity**.

> The similarity between two embeddings can be computed using metrics such as **cosine similarity**. Two **identical** embeddings have a similarity of **1**; two **opposite** embeddings have a similarity of **–1**.

Semantic similarity can be computed for embeddings of **any data modality**, including images and audio. For text it's sometimes called **semantic textual similarity**.

> **WARNING — Is semantic similarity exact or subjective?**
>
> While semantic similarity is placed in the **exact** category here, it can be considered **subjective**, since **different embedding algorithms produce different embeddings**. However, given **two fixed embeddings**, the similarity score between them is computed **exactly**.

Mathematically, let **$A$** be an embedding of the generated response and **$B$** be an embedding of a reference response. The **cosine similarity** between $A$ and $B$ is:

$$\cos(A, B) = \frac{A \cdot B}{\lVert A \rVert \, \lVert B \rVert}$$

with:

- $A \cdot B$ — the **dot product** of $A$ and $B$.
- $\lVert A \rVert$ — the **Euclidean norm** (also known as the **$L^2$ norm**) of $A$. If $A = [0.11, 0.02, 0.54]$, then $\lVert A \rVert = \sqrt{0.11^2 + 0.02^2 + 0.54^2}$.

Metrics for semantic textual similarity include **BERTScore** (embeddings generated by BERT) and **MoverScore** (embeddings generated by a mixture of algorithms).

> Semantic textual similarity **doesn't require** a reference set as comprehensive as lexical similarity does. However, its reliability depends on the **quality of the underlying embedding algorithm** — two texts with the same meaning can still score low if their embeddings are bad. Another drawback: the embedding algorithm might require **nontrivial compute and time** to run.

### Introduction to Embedding

The concept of embedding lies at the heart of **semantic similarity** and is the backbone of many topics explored throughout the book — including **vector search** (Chapter 6) and **data deduplication** (Chapter 8).

Since computers work with numbers, a model must convert its input into **numerical representations** it can process. An **embedding** is a numerical representation that aims to **capture the meaning** of the original data.

An embedding is a **vector**. For example, *"the cat sits on a mat"* might be represented as `[0.11, 0.02, 0.54]`. In reality, the size of an embedding vector (the number of elements) is typically between **100 and 10,000**.[^13]

Models trained especially to produce embeddings include the open source **BERT**, **CLIP** (Contrastive Language–Image Pre-training), and **Sentence Transformers**. There are also **proprietary embedding models** provided as APIs.[^14]

**Table 3-2. Embedding sizes used by common models.**

| Model | Variant | Embedding size |
| --- | --- | --- |
| **Google's BERT** | BERT base | 768 |
| | BERT large | 1024 |
| **OpenAI's CLIP** | Image | 512 |
| | Text | 512 |
| **OpenAI Embeddings API** | `text-embedding-3-small` | 1536 |
| | `text-embedding-3-large` | 3072 |
| **Cohere's Embed v3** | `embed-english-v3.0` | 1024 |
| | `embed-english-light-3.0` | 384 |

Because models typically require their inputs to first be transformed into vector representations, many ML models — including **GPTs** and **Llamas** — also involve a step to **generate embeddings**. If you have access to the **intermediate layers** of these models, you can use them to extract embeddings. However, their quality **might not be as good** as embeddings from **specialized** embedding models.

#### What makes an embedding "good"?

The goal of an embedding algorithm is to produce embeddings that **capture the essence** of the original data. The vector `[0.11, 0.02, 0.54]` looks **nothing like** the text *"the cat sits on a mat"* — so how do we verify quality?

> At a high level, an embedding algorithm is **good** if **more-similar texts have closer embeddings** (measured by cosine similarity or related metrics). The embedding of *"the cat sits on a mat"* should be **closer** to *"the dog plays on the grass"* than to *"AI research is super fun"*.

You can also evaluate embedding quality based on its **utility for your task** — embeddings are used in **classification, topic modeling, recommender systems, and RAG**. A benchmark that measures embedding quality across multiple tasks is **MTEB** (Massive Text Embedding Benchmark, Muennighoff et al., 2023).

Any data can have embedding representations: ecommerce solutions like **Criteo** and **Coveo** have embeddings for **products**; **Pinterest** has embeddings for images, graphs, queries, and even **users**.

#### Joint (multimodal) embeddings

A new frontier is creating **joint embeddings** for data of **different modalities**:

- **CLIP** (Radford et al., 2021) — one of the first major models to map **text and images** into a joint embedding space.
- **ULIP** (Xue et al., 2022) — unified representations of **text, images, and 3D point clouds**.
- **ImageBind** (Girdhar et al., 2023) — a joint embedding across **six modalities**, including text, images, and audio.

**CLIP** is trained using **(image, text) pairs** (the text can be a caption or comment). For each pair, a **text encoder** converts the text to a text embedding and an **image encoder** converts the image to an image embedding; both are then **projected into a joint embedding space**. The training goal is to get an image's embedding **close** to the embedding of its **corresponding text**.

![CLIP architecture](<assets/CLIP architecture.png>)

**Figure 3-6. CLIP's architecture (Radford et al., 2021).**

> A joint embedding space that can represent data of different modalities is a **multimodal embedding space**. In a text–image joint space, the embedding of an image of a man fishing should be **closer** to the text *"a fisherman"* than to *"fashion show"*. This enables embeddings of different modalities to be **compared and combined** — for example, **text-based image search**: given a text, find the images closest to it.

[Back to Contents](#contents)

## Notes

The original chapter contains numerous footnotes that add color, asides, and references. They are gathered here as supplementary material rather than interspersed inline.

[^1]: For some applications, evaluation is the **single largest bucket of work** in shipping an AI product — in practice it can consume the **majority of the development effort**.
[^2]: *Word of mouth* — relying on someone else's verdict (e.g., *"model X is good"*) rather than measuring the model against your own application's needs.
[^3]: *Eyeballing the results* — manually skimming a handful of outputs and judging by feel, instead of running a repeatable, systematic evaluation.
[^4]: As model capability rises, **evaluating the output requires comparable expertise** to producing it — a dynamic that makes scalable oversight of advanced models an open research problem.
[^5]: Based on the author's analysis of the **top 1,000 AI-related GitHub repositories** by star count, as of **May 2024**.
[^6]: A model's language modeling quality is only a **proxy** for downstream task performance — strongly correlated, but not a guarantee (see Liu et al., 2023).
[^7]: Entropy is reported in **bits** when the logarithm uses base 2, i.e., the average number of bits needed to encode each token.
[^8]: A **nat** is the unit of entropy measured with the **natural logarithm** (base $e$). $1 \text{ nat} = \tfrac{1}{\ln 2} \approx 1.44$ bits.
[^9]: **SFT** = Supervised Fine-Tuning; **RLHF** = Reinforcement Learning from Human Feedback. Both are **post-training** techniques that align a model to complete tasks rather than to minimize next-token loss.
[^10]: **Quantization** lowers a model's numerical precision (e.g., from 16-bit to 4-bit) to shrink its memory footprint, which can shift perplexity **upward or downward** in ways that are hard to predict.
[^11]: Any task with a **measurable objective** — energy saved, score achieved, latency reduced — admits functional-correctness evaluation, because success can be **read directly off the objective** rather than judged subjectively.
[^12]: N-gram overlap is **directional**: you typically measure the fraction of the **reference's** n-grams that appear in the generated response (recall-oriented, as in ROUGE) or vice versa (precision-oriented, as in BLEU).
[^13]: Larger embedding vectors can capture **more nuance** but cost **more storage and compute** at search time; the right size is a trade-off between **representational quality** and **efficiency**.
[^14]: Proprietary embedding APIs (e.g., **OpenAI Embeddings**, **Cohere Embed**) trade the control of self-hosting for **convenience**, but send your data to a **third party** and can change model versions underneath you.
