# Cost Optimization Patterns

## Prompt Amortization

**Example (Zeeguu):** Two flavours of batching show up. *Horizontal* batching packs many independent inputs into one prompt, amortizing a large instructional preamble across the whole batch: meaning frequency/type classification sends ~15 meanings per call, and validation of generated example sentences checks ~20 examples per call. *Vertical* batching produces many outputs from a single input: article simplification generates every CEFR variant simpler than the original in one call, emitting one section per level — turning up to four or five requests into one (~75% fewer calls for a typical article). Both combine naturally with pre-computation: because results are computed offline, there is the luxury of batching.

**Forces:** Many LLM tasks involve a large instructional preamble (the system prompt explaining the task) and a small variable input. Sending individual requests wastes the prompt overhead, both in cost and latency.

**Solution:** Batch multiple inputs into a single request, amortizing the expensive prompt across many items.

**Code (Zeeguu):**

- [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L72) — the per-pair validation prompt: the "substantial instructions" (what counts as a valid translation, edge cases, output format). It runs once *per word* — the large preamble this pattern exists to amortize.
- [`create_batch_meaning_frequency_and_type_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/meaning_frequency_classifier.py#L52-L67) — horizontal batching: ~15 meanings classified in one call.
- [`validate_examples_batch`](https://github.com/zeeguu/api/blob/master/tools/validate_and_clean_examples.py#L186-L196) — horizontal batching: generated examples validated ~20 at a time (`BATCH_SIZE`).
- [`get_adaptive_simplification_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/article_simplification.py#L8-L14) — vertical batching: one call produces simplified versions for *all* CEFR levels simpler than the original.

**Notes:** 

- How large can a batch be? Two ceilings bound it, and you operate at the lower one. A **token ceiling** — input *and* output must fit the context window; for vertical batching (simplification) the binding side is the *output*, since each variant is a full article. And a **quality ceiling** — accuracy and consistency degrade as the item count grows, independent of tokens. In our experience the quality ceiling binds first for small items: classification and example validation run at **15–20 items per call**, far below what the window allows, because beyond that the model starts dropping or muddling entries.
- Not every candidate is amortized yet: translation validation currently runs **one call per word** (`validate_and_fix`); a batched validation prompt exists in the codebase but is not wired up — a standing opportunity to apply this pattern.
- Some LLMs provide prompt caching - e.g. Deepseek. Even so, if the cost is amortized with prompt caching, the time saving of amortization can still be a valuable reason for doing it

## Escalate to the LLM

**Example (Zeeguu):** Google Translate serves as the primary translation engine. When a user indicates the translation is inadequate, the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed.

![[escalate-to-the-llm.png|220]]
*In Zeeguu, the inline Google translation is the primary path; when the user wants a better rendering they escalate to an LLM on demand via the "Ask LLM" option.*

**Forces:** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than LLMs for well-defined tasks — but they sometimes fail or produce insufficiently satisfactory results.

**Solution:** Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction.

**Applicability:** This pattern applies broadly — topic classification, named entity recognition, or any NLP task where a cheaper tool handles the common case and the LLM handles the long tail.

**Notes:**

- *Escalation, not fallback.* Unlike a reliability fallback — where the secondary is an equal-or-lesser backup invoked when the primary fails (see *Fail-Fast Provider Chain*) — here the secondary is **more capable and more expensive**, invoked when the primary is not good enough. The movement is *up* in quality and cost, not *down* into degraded mode. That is why we name it escalation.
- *Relationship to the model cascade.* This is the human-/failure-triggered cousin of the **model cascade** in ML serving, where a cheap model runs first and a confidence threshold routes hard inputs to a larger model. The shared shape is *cheap tier first, expensive tier on demand*; the difference is the trigger. A cascade escalates automatically on the model's own low confidence, whereas this pattern escalates on external signals — the primary tool erroring, or the user explicitly declaring the result inadequate. A confidence-based cascade is thus one possible escalation policy; user dissatisfaction is another, and the two can be combined.
