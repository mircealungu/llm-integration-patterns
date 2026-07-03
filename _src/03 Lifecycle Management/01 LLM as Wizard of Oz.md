# LLM as Wizard of Oz

## Example

Topic classification of articles is currently performed by pasting the abstract into an LLM and askint it to clasify the topic. This works but is expensive. Once we are satisfied with the topic taxonomy and have accumulated enough labeled data, we will switch to a dedicated topic detection framework.

## Forces

LLMs are general-purpose machines that can attempt almost any text-based task. Building dedicated, efficient solutions requires upfront investment and training data that may not yet exist.

## Solution

Use the LLM to perform a task in production while building a more efficient replacement. The LLM serves as the "wizard behind the curtain": convincing to users, allowing early beta-testing and feedback, but intended to be temporary.

**Bootstrapping variant:** In a more subtle variant, the LLM *generates the training data for its own replacement.* For example, Zeeguu uses an LLM to estimate text difficulty levels. These LLM-generated difficulty labels are being accumulated as training data for a classical classifier that will eventually take over the task.

## Note

This pattern has a lifecycle relationship with *Escalate to the LLM*: a system may start with the LLM as primary (Wizard of Oz), migrate to a specialized tool as primary, and then keep the LLM as the escalation path, completing a full cycle from LLM-first to LLM-on-demand.

## Known Uses

- **[OpenAI Model Distillation](https://openai.com/index/api-model-distillation/)** (Stored Completions) captures a large model's production input–output pairs and fine-tunes a smaller model as a drop-in replacement — the pattern shipped as a product feature.
- **[Self-Instruct / Alpaca](https://github.com/tatsu-lab/stanford_alpaca)** (Wang et al.; Taori et al., 2023) use a strong LLM to generate the instruction data that fine-tunes a small replacement — the bootstrapping variant.
- **[Distilling Step-by-Step](https://arxiv.org/abs/2305.02301)** (Hsieh et al., ACL Findings 2023) trains task-specific models up to 700× smaller from LLM-generated rationales.

> [!draft]- Notes after the focus group
> - it's not exactcly as wizard of oz prototyping
