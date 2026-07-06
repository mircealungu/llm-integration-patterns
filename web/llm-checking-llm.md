---
layout: default
title: "LLM-Checking-LLM"
permalink: /llm-checking-llm/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../quality-assurance/">Quality Assurance</a>
</nav>


## Context

An LLM generates content that will be used or stored, and its output is sometimes wrong in ways a targeted check could catch. Verifying a specific property (grammaticality, factual match, difficulty level) is a narrower task than the open-ended generation that produced it.

## Example

After generating contextual example sentences for vocabulary words, a second LLM call reviews the examples for accuracy, naturalness, and appropriate difficulty level.

## Problem

How can an unreliable generator's mistakes be caught, when a second generator would be just as unreliable?

## Forces

LLMs are imprecise generators, but verification of specific properties (e.g., grammatical correctness) is a more constrained task than open-ended generation (e.g., text simplification). A second, focused LLM call can catch errors that the first, more complex call introduced.

## Solution

Use one LLM call to generate a result, then use a separate LLM call to check or refine it. The verification prompt can be simpler and more focused than the generation prompt.

## Consequences

- **A focused check is more reliable than the generation.** Verifying one property is easier than producing the whole output, so the second call catches errors the first introduced, for the price of one extra call.
- **It narrows the error rate, it does not remove it.** The checker is itself an LLM and can return its own false verdicts, and it adds cost and latency.
- **It pays off only when checking is genuinely narrower than generating.** A check as open-ended as the generation buys little. The verdict composes with [LLM Content Validation Tracking](../llm-content-validation-tracking/) (record it) and [Hybrid Classical+LLM Pipeline](../hybrid-classical-llm-pipeline/) (a classical check is cheaper still, where one exists).

## Note

This is distinct from ensemble methods or chain-of-thought: the key insight is that checking is a fundamentally easier task than generating, and this asymmetry can be exploited architecturally.

## Known Uses

- **[LLM-as-a-judge](https://arxiv.org/abs/2306.05685)** (Zheng et al., NeurIPS 2023) uses a separate strong LLM to score another model's open-ended outputs.
- **[Self-Refine](https://arxiv.org/abs/2303.17651)** (Madaan et al., NeurIPS 2023): a separate pass critiques and refines the first output.
- **[G-Eval](https://arxiv.org/abs/2303.16634)** (Liu et al., 2023), shipped in eval frameworks such as **[DeepEval](https://deepeval.com/docs/metrics-llm-evals)**, uses a separate chain-of-thought judge call to grade generated output.
- *Contrast.* Unlike self-critique on the same reasoning, this pattern uses a differently-prompted call to check a *different property* (see [Related Work](../related-work/) on Stechly et al.).



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../soft-invalidation-of-llm-artifacts/">← Soft Invalidation of LLM Artifacts</a><a class="nav-next" href="../llm-content-validation-tracking/">LLM Content Validation Tracking →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM-Checking-LLM%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+LLM-Checking-LLM%0A%2A%2ASection%3A%2A%2A+Quality+Assurance%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-checking-llm%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
