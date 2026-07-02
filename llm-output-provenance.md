---
layout: default
title: "LLM Output Provenance"
permalink: /llm-output-provenance/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../#data-management">Data Management</a>
</nav>


## Example

When the system generates example sentences with a given word to be used in exercises, it stores which model and prompt version produced each result. When a prompt is improved, the system can identify and regenerate stale outputs without reprocessing everything.

## Forces

LLM-generated data that enters persistent storage becomes a long-lived asset, but models and prompts improve over time. Without knowing how a piece of data was generated, it cannot be selectively regenerated when better models or prompts become available. Prompts evolve more frequently than model versions and can have a larger impact on output quality.

## Solution

Store the full provenance tuple alongside every LLM-generated artifact: (model version, prompt version, generated output, timestamp). This enables selective regeneration (e.g., *"re-run everything produced by prompt v2 with the improved prompt v3"*) and quality auditing.

## Notes

- The key insight is that the prompt is at least as important to version as the model: a prompt change can completely alter output format, quality, or behavior even with the same model.   
- This is also critical for the Wizard of Oz pattern: when accumulating LLM-generated labels as training data for a classical replacement, provenance tracking lets one exclude data produced by a prompt version that was later found to be noisy or biased.  
- The identifier stamped for provenance should be the *same* constant the code uses to select the model, kept in one place ([Centralized Model Selection](../centralized-model-selection/)). When the two are separate literals, the selection can move to a new model while the provenance field keeps naming the old one. A field that names a model no longer in the pipeline is worse than no field at all.
- Implicit provenance: Keep model names and prompt versions as constants in code. When one needs to know what generated a piece of data, correlate its `created_at` timestamp with git history to determine which model/prompt was deployed at that time. However, this works for simpler systems where there is a single model/prompt active at any time. A system using alternative prompts, e.g. for A/B testing, will have to track provenance explicitly. Also, explicit tracking makes data analysis faster, and ensures that data is self-describable.
- after the focus group
	- can be solved with the gateway ?
	- related to research data management? 


## War Story

Provenance must capture the dimension that actually varies. Zeeguu's `audio_lesson_meaning` rows have a `created_by` field that records the model identifier (e.g. `"Claude-Opus-Prompt1"`), but the prompt template files were edited in place over time without bumping that identifier, so the field carried the same value across two materially different prompt eras and could not drive selective regeneration. When the team later identified ~900 lessons generated under a previous, ambiguous prompt, the only way to find them was a content regex on the output itself: "does the script contain the ambiguous phrasing?". The lesson: if prompts evolve by in-place edits, the provenance field that names them must bump on every edit (e.g. via a versioned filename like `prompt-v2-rev3.txt` or a content hash); otherwise the field is decorative and selective-regeneration falls back to forensics on the output.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../centralized-model-selection/">← Centralized Model Selection</a><a class="nav-next" href="../llm-checking-llm/">LLM-Checking-LLM →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM+Output+Provenance%5D+&labels=feedback%2Cdata-management&body=%2A%2ARe%3A%2A%2A+LLM+Output+Provenance%0A%2A%2ASection%3A%2A%2A+Data+Management%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-output-provenance%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
