---
layout: default
title: "Prompt Amortization"
permalink: /prompt-amortization/
---


[← All patterns](../)


**Example (Zeeguu):** When many items need the same expensive prompt, they can be packed into a single call instead of sent one at a time. This *batching* takes two forms. 

*Horizontal* batching packs many independent inputs into one prompt, amortizing a large instructional preamble across the whole batch: meaning frequency/type classification sends ~15 meanings per call, and validation of generated example sentences checks ~20 examples per call. 

*Vertical* batching produces many outputs from a single input: article simplification generates every CEFR variant simpler than the original in one call, emitting one section per level, turning up to four or five requests into one (~75% fewer calls for a typical article). 

Both combine naturally with pre-computation: because results are computed offline, there is the luxury of batching.

**Forces:** Many LLM tasks involve a large instructional preamble (the system prompt explaining the task) and a small variable input. Sending individual requests wastes the prompt overhead, both in cost and latency.

**Solution:** Batch multiple inputs into a single request, amortizing the expensive prompt across many items.

**Code (Zeeguu):**

- [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L72). The per-pair validation prompt: the "substantial instructions" (what counts as a valid translation, edge cases, output format). It runs once *per word*: the large preamble this pattern exists to amortize.
- [`create_batch_meaning_frequency_and_type_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/meaning_frequency_classifier.py#L52-L67). Horizontal batching: ~15 meanings classified in one call.
- [`validate_examples_batch`](https://github.com/zeeguu/api/blob/master/tools/validate_and_clean_examples.py#L186-L196). Horizontal batching: generated examples validated ~20 at a time (`BATCH_SIZE`).
- [`get_adaptive_simplification_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/article_simplification.py#L8-L14). Vertical batching: one call produces simplified versions for *all* CEFR levels simpler than the original.

**Notes:** 

- How large can a batch be? Two ceilings bound it, and the effective limit is whichever is lower. A **token ceiling**: input *and* output must fit the context window; for vertical batching (simplification) the binding side is the *output*, since each variant is a full article. And a **quality ceiling**: accuracy and consistency degrade as the item count grows, independent of tokens. In our experience the quality ceiling binds first for small items: classification and example validation run at **15–20 items per call**, far below what the window allows, because beyond that the model starts dropping or muddling entries.
- Not every candidate is amortized yet: translation validation currently runs **one call per word** (`validate_and_fix`); a batched validation prompt exists in the codebase but is not wired up, a standing opportunity to apply this pattern.
- Some LLMs provide prompt caching - e.g. Deepseek. Even so, if the cost is amortized with prompt caching, the time saving of amortization can still be a valuable reason for doing it



---
[← All patterns](../) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BPrompt+Amortization%5D+&labels=feedback%2Ccost-optimization&body=%2A%2ARe%3A%2A%2A+Prompt+Amortization%0A%2A%2ASection%3A%2A%2A+Cost+Optimization+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fprompt-amortization%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
