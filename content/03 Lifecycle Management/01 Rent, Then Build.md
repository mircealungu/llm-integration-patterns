# Rent, Then Build

## Context

A specific feature has not been implemented yet. An LLM exists which can be immediately used to implement the feature for a price which is expensive but still affordable.

## Example

Topic classification of articles is currently performed by pasting the abstract into an LLM and asking it to classify the topic. This works but is expensive. Once we are satisfied with the topic taxonomy and have accumulated enough labeled data, we will switch to a dedicated topic detection framework.

## Problem

How can a feature ship and start earning its keep before the cheaper, dedicated version that will eventually run it has been built?

## Forces

- **Generality**. LLMs are general-purpose machines that can attempt almost any text-based task. Specific solutions may provide deterministic results which can be guaranteed to be correct within a concrete domain.

- **Cost**. LLMs are readily available for a pay-per-use fee. Building dedicated, efficient solutions requires upfront investment and training data that may not yet exist.

- **Time to Market**. A feature needs to work in production now, but the efficient, dedicated version of it (a fine-tuned or classical model) needs training data or engineering that does not exist yet. A general-purpose LLM can do the task immediately, if expensively.


## Solution

Use the LLM to perform a task in production while building a more efficient replacement. The arc is rent, then build: the LLM's general capability is *rented* (paid per call, costly but available immediately) to ship the feature now, while a cheaper, dedicated implementation is *built* to eventually own the task. The rented LLM is convincing to users and good for early beta-testing and feedback, but intended to be temporary.

**Bootstrapping variant:** In a more subtle variant, the LLM *generates the training data for its own replacement.* For example, Zeeguu uses an LLM to estimate text difficulty levels. These LLM-generated difficulty labels are being accumulated as training data for a classical classifier that will eventually take over the task.

## Consequences

- **The feature is live from day one.** It gathers real usage and feedback immediately, with the LLM standing in for a component that does not exist yet.
- **Running the stand-in funds its successor.** The LLM's inputs and outputs accumulate as the labeled data the dedicated replacement needs, so the temporary solution also produces the training set for the permanent one (the bootstrapping variant).
- **The stand-in is expensive, and "temporary" can stick.** Until the replacement ships, the feature runs at LLM cost and latency, the replacement is a second system to build and validate, and the intended-temporary LLM can quietly become permanent.
- **User feedback**. The feature is validated by gathering user feedback before making the investment to build and optimize a specific implementation for it.

## Note

This pattern has a lifecycle relationship with *Escalate to the LLM*: a system may start with the LLM as primary (renting it), migrate to a specialized tool as primary, and then keep the LLM as the escalation path, completing a full cycle from LLM-first to LLM-on-demand.

## Known Uses

- **[OpenAI Model Distillation](https://openai.com/index/api-model-distillation/)** (Stored Completions) captures a large model's production input–output pairs and fine-tunes a smaller model as a drop-in replacement: the pattern shipped as a product feature.
- **[Self-Instruct / Alpaca](https://github.com/tatsu-lab/stanford_alpaca)** (Wang et al.; Taori et al., 2023) use a strong LLM to generate the instruction data that fine-tunes a small replacement: the bootstrapping variant.
- **[Distilling Step-by-Step](https://arxiv.org/abs/2305.02301)** (Hsieh et al., ACL Findings 2023) trains task-specific models up to 700× smaller from LLM-generated rationales.
