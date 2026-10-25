---
layout: default
title: "Rent, Then Build"
permalink: /rent-then-build/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../managing-change-over-time/">Managing Change Over Time</a>
</nav>


*Ship a feature on an LLM now, while building the cheaper component that will replace it.*

## Context

A feature needs a task done on every item that flows through the system, such as labeling each article or each message. A small dedicated model could do the task cheaply, but it would have to be trained on labeled examples, and there are none yet. A general-purpose LLM can do the task today, from a prompt.

## Problem

How can a feature ship and start earning its keep before the cheaper, dedicated version that will eventually run it has been built?

## Problem in Zeeguu

Zeeguu recommends news articles at the learner's level, so every article it crawls needs a level, from A1 (beginner) to C2 (near native). That is tens of thousands of articles a month, in more than ten languages. No collection of articles labeled with their level existed for most of these languages. The readability formula Zeeguu used before, which counts words and syllables per sentence, could not tell the levels apart. An LLM could estimate the level of an article, but at the price of a call, and several seconds, per article.

## Forces

- **Shipping now gets the feature, and its usage, immediately.** A general-purpose LLM can do the task the day it is needed, before any replacement exists. *(pushes toward renting)*
- **Running the LLM indefinitely is costly and cedes control.** The feature keeps paying per call, and a core capability stays rented from a vendor who prices and deprecates on their own schedule. *(pushes toward building a replacement)*
- **The replacement cannot be built yet.** A dedicated model needs training data that does not exist at the outset. *(pushes toward relying on the LLM for now)*

## Solution

Use the LLM to perform the task in production while building a more efficient replacement. The LLM's general capability is *rented*: paid per call, costly, but available immediately. A cheaper replacement is *built* to take the task over later. The rented LLM is good enough for users and for early feedback, but it is meant to be temporary.

Switch once the replacement agrees well enough with the LLM. Measure the agreement on the kind of inputs the replacement will judge in production, not only on those it was trained from.

**Bootstrapping variant:** in the strongest form, the LLM *generates the training data for its own replacement*. Every answer it gives in production is a labeled example, so running the LLM also produces what the replacement is trained on.

<figure class="img">
  <a href="/images/rent-then-build-diagram.svg"><img src="/images/rent-then-build-diagram.svg" alt="Now, a rented LLM serves the feature, paid per call. Later, a cheaper dedicated model owned by the system takes the task over. In the bootstrapping variant drawn here, the LLM&#x27;s answers become the training data for the model that replaces it."></a>
  <figcaption>Now, a rented LLM serves the feature, paid per call. Later, a cheaper dedicated model owned by the system takes the task over. In the bootstrapping variant drawn here, the LLM&#x27;s answers become the training data for the model that replaces it.</figcaption>
</figure>

## Solution in Zeeguu

Zeeguu built the replacement and uses it where a fast estimate is critical.

From the start, an LLM estimated the level of every crawled article, and Zeeguu stored the level with the article. By October 2025 these stored levels were enough to train a replacement. Zeeguu trained one small classifier per language (a random forest), on twelve features of the text that are cheap to compute, such as sentence length, word length and how varied the vocabulary is.[^rtb-ml]

The classifier answers in milliseconds and costs nothing per call. That makes it the right tool where the level is needed in real time. When a teacher edits a text for a class, Zeeguu shows the text's level and updates it as the teacher types. An LLM call would take seconds for every change. The crawler, which has no one waiting, still asks the LLM.

[^rtb-ml]: `zeeguu/core/language/ml_cefr_classifier.py` and the evaluation in `zeeguu/core/language/EVALUATION_SUMMARY.md`, in the `zeeguu/api` repository.

## Consequences

- **The feature is live from day one.** It gathers real usage and feedback immediately, with the LLM doing the work of a component that does not exist yet.
- **The replacement learns the LLM's mistakes.** A replacement trained on the LLM's labels is measured against those same labels. Its accuracy says how well it copies the LLM, not how often it is right.
- **"Temporary" can stick.** Until the replacement takes over, the feature runs at LLM cost and latency.
- **There are two systems to maintain.** The replacement has to be built, validated and kept up to date next to the LLM.

## War Story: The Rent That Never Ended

The replacement was built, but the LLM was not retired. The crawler still asks the LLM for the level of every article. The same call also writes the article's summaries and flags paywalled and disturbing articles: one call does several tasks ([Prompt Amortization](../prompt-amortization/)), so the level costs almost nothing extra. Moving it to the classifier would save little, and the call would run anyway.

## Known Uses

- **[OpenAI Model Distillation](https://openai.com/index/api-model-distillation/)** (Stored Completions) captures a large model's production input and output pairs and fine-tunes a smaller model as a drop-in replacement: the pattern shipped as a product feature.
- **[Self-Instruct / Alpaca](https://github.com/tatsu-lab/stanford_alpaca)** (Wang et al.; Taori et al., 2023) use a strong LLM to generate the instruction data that fine-tunes a small replacement: the bootstrapping variant.
- **[Distilling Step-by-Step](https://arxiv.org/abs/2305.02301)** (Hsieh et al., ACL Findings 2023) trains task-specific models up to 700× smaller from LLM-generated rationales.

These are distillation methods from the literature. We did not find a first-hand account of a production feature that completed the full arc.

## Related Patterns

[Escalate to the LLM](../escalate-to-the-llm/) is where this pattern often ends. A system starts with the LLM as the only path, builds a dedicated model, and then keeps the LLM for the inputs the dedicated model cannot handle.

[LLM Output Provenance](../llm-output-provenance/) lets the bootstrapping variant choose its training data. Labels from a prompt or model version later found to be noisy can be left out.

[LLM Content Validation Tracking](../llm-content-validation-tracking/) lets the replacement train only on labels that were checked, not on every guess of the LLM.

[Prompt Amortization](../prompt-amortization/) can keep the rent going. When one call already does several tasks, moving one of them to a dedicated model saves little.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../llm-output-provenance/">← LLM Output Provenance</a><a class="nav-next" href="../centralized-model-selection/">Centralized Model Selection →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BRent%2C+Then+Build%5D+&labels=feedback%2Cmanaging-change-over-time&body=%2A%2ARe%3A%2A%2A+Rent%2C+Then+Build%0A%2A%2ASection%3A%2A%2A+Managing+Change+Over+Time%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Frent-then-build%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
