# Prompt Amortization

![[prompt-amortization-combined-validation.png|420]]
*The `COMBINED_VALIDATION_PROMPT` template: ~250 lines of validation rules, frequency/CEFR/phrase-type taxonomies, output format, and examples, wrapped around just three variables (`{word}`, `{translation}`, `{context}`). Sent one pair at a time, the entire preamble is re-paid on every call. This fixed overhead is the cost the pattern amortizes.*


## Example

Several Zeeguu jobs share the same shape (a large instructional prompt wrapped around a tiny variable input, see figure) and run offline over many items. Instead of paying that preamble once per item, related items are packed into a single call:

- **Meaning classification** sends ~15 word-meanings per call, sharing one frequency/CEFR-type taxonomy prompt across the whole batch.
- **Example-sentence validation** checks ~20 generated examples per call.
- **Article simplification** produces every CEFR level simpler than the original in one call, one section per level, turning four or five requests into one (~75% fewer calls for a typical article).



## Forces

- **Preamble overhead.** A large, fixed instructional prompt wrapped around a tiny variable input; sent one item at a time, that preamble is re-paid on every call, in tokens, cost, and latency alike. *(pushes toward bigger batches)*
- **Quality ceiling.** Accuracy and consistency degrade as more items share one call; past ~15–20 small items the model starts dropping or muddling entries. *(pushes toward smaller batches)*
- **Context ceiling.** Input *and* output must fit the window; for fan-out the output side binds first, since each result is full-length.
- **Interactive latency.** Fan-in requires waiting to accumulate enough items to fill a batch: fine offline, but unacceptable when a user is blocked on a single result.

## Solution

Batch multiple items into a single request, amortizing the expensive prompt across all of them. This takes two forms:

- ***Fan-in* batching** packs many independent inputs into one prompt, spreading a large instructional preamble across the whole batch.
- ***Fan-out* batching** produces many outputs from a single input, emitting one section per output and collapsing several requests into one.

Both combine naturally with pre-computation: because results are computed offline, there is the luxury of batching.

## Code

- [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L72). The per-pair validation prompt: the "substantial instructions" (what counts as a valid translation, edge cases, output format). It runs once *per word*: the large preamble this pattern exists to amortize.
- [`create_batch_meaning_frequency_and_type_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/meaning_frequency_classifier.py#L52-L67). Fan-in batching: ~15 meanings classified in one call.
- [`validate_examples_batch`](https://github.com/zeeguu/api/blob/master/tools/validate_and_clean_examples.py#L186-L196). Fan-in batching: generated examples validated ~20 at a time (`BATCH_SIZE`).
- [`get_adaptive_simplification_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/article_simplification.py#L8-L14). Fan-out batching: one call produces simplified versions for *all* CEFR levels simpler than the original.

## Notes

- Which ceiling binds first? For small items it is the *quality* ceiling, not the token one: classification and example validation run at **15–20 items per call**, far below what the window allows, because beyond that the model starts dropping or muddling entries. For fan-out simplification it flips: the *token* ceiling binds on the output side, since each variant is a full article.
- Not every candidate is amortized yet: translation validation currently runs **one call per word** (`validate_and_fix`); a batched validation prompt exists in the codebase but is not wired up, a standing opportunity to apply this pattern.
- Some LLMs provide prompt caching - e.g. Deepseek. Even so, if the cost is amortized with prompt caching, the time saving of amortization can still be a valuable reason for doing it


- after focus group
	- drain pattern?
