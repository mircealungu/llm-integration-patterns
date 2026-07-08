# LLM Output Provenance

## Context

LLM-generated artifacts (example sentences, summaries, labels) are written to persistent storage and reused for a long time, while the models and prompts that produce them keep improving. The prompt changes more often, and often matters more to output quality, than the model.

## Example

When the system generates example sentences with a given word to be used in exercises, it stores which model and prompt version produced each result. When a prompt is improved, the system can identify and regenerate stale outputs without reprocessing everything.

## Problem

When a prompt or model improves, how can exactly the stale artifacts be found and regenerated, without reprocessing the entire store?

## Forces

LLM-generated data that enters persistent storage becomes a long-lived asset, but models and prompts improve over time. Without knowing how a piece of data was generated, it cannot be selectively regenerated when better models or prompts become available. Prompts evolve more frequently than model versions and can have a larger impact on output quality.

## Solution

Store the full provenance tuple alongside every LLM-generated artifact: **model version, prompt version, generated output, timestamp**. This enables selective regeneration (e.g., *"re-run everything produced by prompt v2 with the improved prompt v3"*) and quality auditing.

## Consequences

- **Selective regeneration becomes a query.** Re-run everything a given prompt or model produced and leave the rest, and the same record doubles as a quality-audit trail.
- **The stamp must be present and precise.** Every write has to record the provenance, and it is only as useful as the granularity it captures: a field that is not updated when the prompt is edited in place silently goes stale and drives nothing.
- **One identifier, shared with selection and validation.** The stamped model identifier and the one used to select the model at call time should be the same central constant, kept in one place, and provenance pairs with *LLM Content Validation Tracking*: how an artifact was made, and whether it has been confirmed.

## Known Uses

- *Better attested in tooling than in production self-reports.* The capability is productized: [MLflow Prompt Registry](https://mlflow.org/docs/latest/genai/prompt-registry/) and [LangSmith](https://docs.langchain.com/langsmith/prompt-engineering-concepts) version prompts and record which prompt/model produced each output, confirming the pattern's core claim that the *prompt* deserves versioning as much as the model, but these are tools, not documented in-app deployments.
- *Adjacent production pipelines.* [DoorDash](https://careersatdoordash.com/blog/doordash-profile-generation-llms-understanding-consumers-merchants-and-items/) stores versioned LLM-generated profiles and "treat[s] prompts as code"; [Etsy](https://www.etsy.com/codeascraft/understanding-etsyas-vast-inventory-with-llms) stores Pydantic-validated LLM attribute extractions over 100M+ listings. Both store LLM artifacts at scale and version prompts, but neither publicly describes stamping *each artifact* with its prompt version to drive *selective* regeneration: the load-bearing mechanic here.
- We did not find a first-hand account of the full pattern; Zeeguu is our instance.

## Notes

- The key insight is that the prompt is at least as important to version as the model: a prompt change can completely alter output format, quality, or behavior even with the same model.   
- This is also critical for *Rent, Then Build*: when accumulating LLM-generated labels as training data for a classical replacement, provenance tracking lets one exclude data produced by a prompt version that was later found to be noisy or biased.  
- A field that names a model no longer in the pipeline is worse than no field at all, so stamp the provenance from the same constant used to *select* the model.
- Implicit provenance: Keep model names and prompt versions as constants in code. When one needs to know what generated a piece of data, correlate its `created_at` timestamp with git history to determine which model/prompt was deployed at that time. However, this works for simpler systems where there is a single model/prompt active at any time. A system using alternative prompts, e.g. for A/B testing, will have to track provenance explicitly. Also, explicit tracking makes data analysis faster, and ensures that data is self-describable.

> [!draft]- Notes after the focus group
> - can be solved with the gateway ?
> - related to research data management? 
> ## War Story
> Provenance must capture the dimension that actually varies. Zeeguu's `audio_lesson_meaning` rows have a `created_by` field that records the model identifier (e.g. `"Claude-Opus-Prompt1"`), but the prompt template files were edited in place over time without bumping that identifier, so the field carried the same value across two materially different prompt eras and could not drive selective regeneration. When the team later identified ~900 lessons generated under a previous, ambiguous prompt, the only way to find them was a content regex on the output itself: "does the script contain the ambiguous phrasing?". The lesson: if prompts evolve by in-place edits, the provenance field that names them must bump on every edit (e.g. via a versioned filename like `prompt-v2-rev3.txt` or a content hash); otherwise the field is decorative and selective-regeneration falls back to forensics on the output.
