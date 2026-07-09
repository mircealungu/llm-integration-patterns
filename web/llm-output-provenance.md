---
layout: default
title: "LLM Output Provenance"
permalink: /llm-output-provenance/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../managing-change-over-time/">Managing Change Over Time</a>
</nav>


## Context

LLM-generated artifacts (example sentences, summaries, labels) are written to persistent storage and reused for a long time, while the models and prompts that produce them keep improving. The prompt changes more often, and often matters more to output quality, than the model.

## Example

When the system generates example sentences for a word, it stamps each stored sentence with a `created_by` value naming the model and prompt version that produced it (for example, `claude-opus / examples-v3`). When the example-generation prompt is improved to `v4`, the stale sentences are exactly those still stamped `v3`, so a single query finds them and they are regenerated, without touching the rest of the store.

## Problem

When a prompt or model improves, how can exactly the stale artifacts be found and regenerated, without reprocessing the entire store?

## Forces

- **Selective regeneration needs to know how each artifact was made.** Without a record of the model and prompt behind a stored artifact, applying an improved prompt means reprocessing everything. *(pushes toward stamping provenance)*
- **Every write must record and maintain the stamp.** A stamp that goes stale is worse than useless: a field not bumped when a prompt is edited in place silently names the wrong version. *(pushes toward stamping only what drives regeneration)*
- **The prompt is the higher-churn axis**: it changes more often than the model and can change the output more, so the stamp must capture the prompt version, not just the model.

## Solution

Store the full provenance tuple alongside every LLM-generated artifact: **model version, prompt version, generated output, timestamp**. This enables selective regeneration (e.g., *"re-run everything produced by prompt v2 with the improved prompt v3"*) and quality auditing.

## Consequences

- **Selective regeneration becomes a query.** Re-run everything a given prompt or model produced and leave the rest, and the same record doubles as a quality-audit trail.
- **The stamp must be present and precise.** Every write has to record the provenance, and it is only as useful as the granularity it captures: a field that is not updated when the prompt is edited in place silently goes stale and drives nothing.
- **One identifier, shared with selection and validation.** The stamped model identifier and the one used to select the model at call time should be the same central constant, kept in one place, and provenance pairs with [LLM Content Validation Tracking](../llm-content-validation-tracking/): how an artifact was made, and whether it has been confirmed.

## Known Uses

- *Better attested in tooling than in production self-reports.* The capability is productized: [MLflow Prompt Registry](https://mlflow.org/docs/latest/genai/prompt-registry/) and [LangSmith](https://docs.langchain.com/langsmith/prompt-engineering-concepts) version prompts and record which prompt/model produced each output, confirming the pattern's core claim that the *prompt* deserves versioning as much as the model, but these are tools, not documented in-app deployments.
- *Adjacent production pipelines.* [DoorDash](https://careersatdoordash.com/blog/doordash-profile-generation-llms-understanding-consumers-merchants-and-items/) stores versioned LLM-generated profiles and "treat[s] prompts as code"; [Etsy](https://www.etsy.com/codeascraft/understanding-etsyas-vast-inventory-with-llms) stores Pydantic-validated LLM attribute extractions over 100M+ listings. Both store LLM artifacts at scale and version prompts, but neither publicly describes stamping *each artifact* with its prompt version to drive *selective* regeneration: the load-bearing mechanic here.
- We did not find a first-hand account of the full pattern; Zeeguu is our instance.

## Notes

- The key insight is that the prompt is at least as important to version as the model: a prompt change can completely alter output format, quality, or behaviour even with the same model.   
- This is also critical for [Rent, Then Build](../rent-then-build/): when accumulating LLM-generated labels as training data for a classical replacement, provenance tracking lets one exclude data produced by a prompt version that was later found to be noisy or biased.  
- A field that names a model no longer in the pipeline is worse than no field at all, so stamp the provenance from the same constant used to *select* the model.
- Implicit provenance: Keep model names and prompt versions as constants in code. When one needs to know what generated a piece of data, correlate its `created_at` timestamp with git history to determine which model/prompt was deployed at that time. However, this works for simpler systems where there is a single model/prompt active at any time. A system using alternative prompts, e.g. for A/B testing, will have to track provenance explicitly. Also, explicit tracking makes data analysis faster, and ensures that data is self-describing.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../targeted-user-feedback/">← Targeted User Feedback</a><a class="nav-next" href="../soft-invalidation-of-llm-artifacts/">Soft Invalidation of LLM Artifacts →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM+Output+Provenance%5D+&labels=feedback%2Cmanaging-change-over-time&body=%2A%2ARe%3A%2A%2A+LLM+Output+Provenance%0A%2A%2ASection%3A%2A%2A+Managing+Change+Over+Time%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-output-provenance%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
