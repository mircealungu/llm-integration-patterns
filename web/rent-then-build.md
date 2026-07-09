---
layout: default
title: "Rent, Then Build"
permalink: /rent-then-build/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../managing-change-over-time/">Managing Change Over Time</a>
</nav>


## Context

A feature needs to work in production now, but the efficient, dedicated version of it (a fine-tuned or classical model) needs training data or engineering that does not exist yet. A general-purpose LLM can do the task immediately, if expensively.

## Example

Zeeguu estimates the difficulty level of every article with an LLM, an expensive call it makes constantly. This is also the *bootstrapping* case: those LLM-generated difficulty labels are accumulating as the training set for a cheaper classical classifier that will take the task over once enough have been gathered. The LLM ships the feature and earns its keep today, while quietly producing the data that will one day retire it. 

A plainer instance without the bootstrapping twist: article topic classification runs on an LLM now, to be replaced by a dedicated topic-detection model once the taxonomy of available topics settles.

## Problem

How can a feature ship and start earning its keep before the cheaper, dedicated version that will eventually run it has been built?

## Forces

- **Shipping now captures the feature and its usage immediately.** A general-purpose LLM can do the task the day it is needed, before any dedicated version exists. *(pushes toward renting)*
- **Running the LLM indefinitely is costly and cedes control.** The feature keeps paying per call, and a core capability stays rented from a vendor who prices and deprecates on their own schedule. *(pushes toward building a replacement)*
- **The replacement cannot be built yet.** A fine-tuned or classical version needs training data or engineering that does not exist at the outset; only running the LLM produces it.

## Solution

Use the LLM to perform a task in production while building a more efficient replacement. The arc is rent, then build: the LLM's general capability is *rented* (paid per call, costly but available immediately) to ship the feature now, while a cheaper, dedicated implementation is *built* to eventually own the task. The rented LLM is convincing to users and good for early beta-testing and feedback, but intended to be temporary.

**Bootstrapping variant:** In the strongest form, the LLM *generates the training data for its own replacement* (as with the difficulty labels above): the rented capability directly produces the labeled data the dedicated successor is trained on, so running the stand-in funds and enables the build.

## Consequences

- **The feature is live from day one.** It gathers real usage and feedback immediately, with the LLM standing in for a component that does not exist yet.
- **Running the stand-in funds its successor.** The LLM's inputs and outputs accumulate as the labeled data the dedicated replacement needs, so the temporary solution also produces the training set for the permanent one (the bootstrapping variant).
- **The stand-in is expensive, and "temporary" can stick.** Until the replacement ships, the feature runs at LLM cost and latency, the replacement is a second system to build and validate, and the intended-temporary LLM can quietly become permanent.

## Known Uses

- **[OpenAI Model Distillation](https://openai.com/index/api-model-distillation/)** (Stored Completions) captures a large model's production input–output pairs and fine-tunes a smaller model as a drop-in replacement: the pattern shipped as a product feature.
- **[Self-Instruct / Alpaca](https://github.com/tatsu-lab/stanford_alpaca)** (Wang et al.; Taori et al., 2023) use a strong LLM to generate the instruction data that fine-tunes a small replacement: the bootstrapping variant.
- **[Distilling Step-by-Step](https://arxiv.org/abs/2305.02301)** (Hsieh et al., ACL Findings 2023) trains task-specific models up to 700× smaller from LLM-generated rationales.

These are distillation and self-instruct methods from the literature; we did not find a first-hand account of a production feature completing the full rent-then-build arc, and Zeeguu's own replacement is still in progress.

## Notes

- This pattern has a lifecycle relationship with [Escalate to the LLM](../escalate-to-the-llm/): a system may start with the LLM as primary (renting it), migrate to a specialized tool as primary, and then keep the LLM as the escalation path, completing a full cycle from LLM-first to LLM-on-demand.
- *Depends on LLM Output Provenance* for the bootstrapping variant: because the replacement trains on the rented LLM's own outputs, those labels must be filterable by the prompt and model version that produced them, so labels from a prompt version later found noisy or biased can be excluded from the training set.
- *Composes with LLM Content Validation Tracking* in the bootstrapping variant: gating the training set to validated outputs (confirmed, not merely generated) lets the dedicated successor learn from checked labels rather than the stand-in's unverified guesses.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../soft-invalidation-of-llm-artifacts/">← Soft Invalidation of LLM Artifacts</a><a class="nav-next" href="../centralized-model-selection/">Centralized Model Selection →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BRent%2C+Then+Build%5D+&labels=feedback%2Cmanaging-change-over-time&body=%2A%2ARe%3A%2A%2A+Rent%2C+Then+Build%0A%2A%2ASection%3A%2A%2A+Managing+Change+Over+Time%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Frent-then-build%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
