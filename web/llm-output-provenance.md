---
layout: default
title: "LLM Output Provenance"
permalink: /llm-output-provenance/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../data-management/">Data Management</a>
</nav>


## Context

LLM-generated artifacts (example sentences, summaries, labels) are written to persistent storage and reused for a long time, while the models and prompts that produce them keep improving. The prompt changes more often, and often matters more to output quality, than the model.

## Example

When the system generates example sentences with a given word to be used in exercises, it stores which model and prompt version produced each result. When a prompt is improved, the system can identify and regenerate stale outputs without reprocessing everything.

## Problem

When a prompt or model improves, how can exactly the stale artifacts be found and regenerated, without reprocessing the entire store?

## Forces

LLM-generated data that enters persistent storage becomes a long-lived asset, but models and prompts improve over time. Without knowing how a piece of data was generated, it cannot be selectively regenerated when better models or prompts become available. Prompts evolve more frequently than model versions and can have a larger impact on output quality.

## Solution

Store the full provenance tuple alongside every LLM-generated artifact: (model version, prompt version, generated output, timestamp). This enables selective regeneration (e.g., *"re-run everything produced by prompt v2 with the improved prompt v3"*) and quality auditing.

## Consequences

- **Selective regeneration becomes a query.** Re-run everything a given prompt or model produced and leave the rest, and the same record doubles as a quality-audit trail.
- **The stamp must be present and precise.** Every write has to record the provenance, and it is only as useful as the granularity it captures: a field that does not bump when the prompt is edited in place silently goes stale and drives nothing.
- **One identifier, shared with selection and validation.** The stamped model identifier and the one used to select the model at call time should be the same central constant (composes with [Centralized Model Selection](../centralized-model-selection/)), and provenance pairs with [LLM Content Validation Tracking](../llm-content-validation-tracking/): how an artifact was made, and whether it has been confirmed.

## Notes

- The key insight is that the prompt is at least as important to version as the model: a prompt change can completely alter output format, quality, or behavior even with the same model.   
- This is also critical for the Wizard of Oz pattern: when accumulating LLM-generated labels as training data for a classical replacement, provenance tracking lets one exclude data produced by a prompt version that was later found to be noisy or biased.  
- The identifier stamped for provenance should be the *same* constant the code uses to select the model, kept in one place ([Centralized Model Selection](../centralized-model-selection/)). When the two are separate literals, the selection can move to a new model while the provenance field keeps naming the old one. A field that names a model no longer in the pipeline is worse than no field at all.
- Implicit provenance: Keep model names and prompt versions as constants in code. When one needs to know what generated a piece of data, correlate its `created_at` timestamp with git history to determine which model/prompt was deployed at that time. However, this works for simpler systems where there is a single model/prompt active at any time. A system using alternative prompts, e.g. for A/B testing, will have to track provenance explicitly. Also, explicit tracking makes data analysis faster, and ensures that data is self-describable.

## Known Uses

- *Better attested in tooling than in production self-reports.* The capability is productized: [MLflow Prompt Registry](https://mlflow.org/docs/latest/genai/prompt-registry/) and [LangSmith](https://docs.langchain.com/langsmith/prompt-engineering-concepts) version prompts and record which prompt/model produced each output, confirming the pattern's core claim that the *prompt* deserves versioning as much as the model, but these are tools, not documented in-app deployments.
- *Adjacent production pipelines.* [DoorDash](https://careersatdoordash.com/blog/doordash-profile-generation-llms-understanding-consumers-merchants-and-items/) stores versioned LLM-generated profiles and "treat[s] prompts as code"; [Etsy](https://www.etsy.com/codeascraft/understanding-etsyas-vast-inventory-with-llms) stores Pydantic-validated LLM attribute extractions over 100M+ listings. Both store LLM artifacts at scale and version prompts, but neither publicly describes stamping *each artifact* with its prompt version to drive *selective* regeneration: the load-bearing mechanic here.
- We did not find a first-hand account of the full pattern; Zeeguu is our instance.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../centralized-model-selection/">← Centralized Model Selection</a><a class="nav-next" href="../soft-invalidation-of-llm-artifacts/">Soft Invalidation of LLM Artifacts →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM+Output+Provenance%5D+&labels=feedback%2Cdata-management&body=%2A%2ARe%3A%2A%2A+LLM+Output+Provenance%0A%2A%2ASection%3A%2A%2A+Data+Management%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-output-provenance%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
