# Cost Optimization Patterns

## Prompt Amortization

**Example (Zeeguu):** A prompt that verifies whether a word-translation pair is correct requires substantial instructions (explaining what constitutes a valid translation, edge cases, output format). The actual input — a word and its translation — is tiny. Instead of sending one request per word pair, we pack dozens of pairs into a single prompt. Similarly, when generating example sentences for words users will study, we batch the generation for all words in one call. This pattern combines naturally with pre-computation: because results are computed offline, we have the luxury of batching. Article simplification generates all CEFR-level variants (A1, A2, B1, B2) in one call, with the prompt instructing the model to output a JSON object keyed by level. This reduces four API calls to one, cutting cost by ~75%.

**Forces:** Many LLM tasks involve a large instructional preamble (the system prompt explaining the task) and a small variable input. Sending individual requests wastes the prompt overhead, both in cost and latency.

**Solution:** Batch multiple inputs into a single request, amortizing the expensive prompt across many items.

**Notes:** 

- One might still need to split into multiple prompts when too many tasks are batched. One might also have to investigate whether the quality of the response decreases when the cardinality of the batch is increased. In our own experience, it works fine for ...
- Some LLMs provide prompt caching - e.g. Deepseek. Even so, if the cost is amortized with prompt caching, the time saving of amortization can still be a valuable reason for doing it

## LLM as Fallback

**Example (Zeeguu):** Google Translate serves as the primary translation engine. When a user indicates the translation is inadequate, the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed.

**Forces:** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than LLMs for well-defined tasks — but they sometimes fail or produce insufficiently satisfactory results.

**Solution:** Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction.

**Applicability:** This pattern applies broadly — topic classification, named entity recognition, or any NLP task where a cheaper tool handles the common case and the LLM handles the long tail.
