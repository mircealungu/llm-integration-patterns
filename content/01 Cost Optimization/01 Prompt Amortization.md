# Prompt Amortization

![[prompt-amortization-combined-validation.png|420]]
*The `COMBINED_VALIDATION_PROMPT` template: ~250 lines of validation rules, frequency/CEFR/phrase-type taxonomies, output format, and examples, wrapped around just three variables (`{word}`, `{translation}`, `{context}`). Sent one pair at a time, the entire preamble is re-paid on every call. This fixed overhead is the cost the pattern amortizes.*


## Context

Many LLM calls share the same shape: a large, fixed instructional prompt (rules, taxonomies, output format, examples) wrapped around a tiny variable input. The work is offline and batchable — nobody is blocked on any single result.

## Example

Several Zeeguu jobs share the same shape (a large instructional prompt wrapped around a tiny variable input, see figure) and run offline over many items. Instead of paying that preamble once per item, related items are packed into a single call:

- **Meaning classification** sends ~15 word-meanings per call, sharing one frequency/CEFR-type taxonomy prompt across the whole batch.
- **Example-sentence validation** checks ~20 generated examples per call.
- **Article simplification** produces every CEFR level simpler than the original in one call, one section per level, turning four or five requests into one (~75% fewer calls for a typical article).



## Problem

Sent one item at a time, that fixed preamble is re-paid on every call and dominates token cost and latency. How can it be paid once instead of once per item — without blowing past the model's quality or context limits?

## Forces

- **Preamble overhead.** A large, fixed instructional prompt wrapped around a tiny variable input; sent one item at a time, that preamble is re-paid on every call, in tokens, cost, and latency alike. *(pushes toward bigger batches)*
- **Quality ceiling.** Accuracy and consistency degrade as more items share one call; past ~15–20 small items some models start dropping or muddling entries. *(pushes toward smaller batches)*
- **Context ceiling.** Input *and* output must fit the window; for fan-out the output side binds first, since each result is full-length.
- **Interactive latency.** Fan-in requires waiting to accumulate enough items to fill a batch: fine offline, but unacceptable when a user is blocked on a single result.

## Solution

Batch multiple items into a single request, amortizing the expensive prompt across all of them. This takes two forms:

- ***Fan-in* batching** packs many independent inputs into one prompt, spreading a large instructional preamble across the whole batch.
- ***Fan-out* batching** produces many outputs from a single input, emitting one section per output and collapsing several requests into one.

Both combine naturally with pre-computation: because results are computed offline, there is the luxury of batching.

## Consequences

- **Cost and latency amortize with batch size.** The fixed preamble is paid once per call instead of once per item, so per-item token cost *and* wall-clock latency fall roughly inversely with the batch size.
- **Batch size is capped by the tightest ceiling — and which ceiling binds flips by direction.** For fan-in (many small items) the *quality* ceiling binds first (~15–20 items before the model drops or muddles entries), far below what the token window allows; for fan-out (full-length outputs) the *token* ceiling binds first, on the output side, since each result is full-length. So the workable batch size is workload-specific and must be tuned, not maximized.
- **Applies only to deferrable work.** Fan-in must wait to accumulate items, so the pattern fits offline / pre-computed paths (composes with *Anticipatory Precomputation*) and is unavailable when a user is blocked on a single result.

## Code

- [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L72). The per-pair validation prompt: the "substantial instructions" (what counts as a valid translation, edge cases, output format). It runs once *per word*: the large preamble this pattern exists to amortize.
- [`create_batch_meaning_frequency_and_type_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/meaning_frequency_classifier.py#L52-L67). Fan-in batching: ~15 meanings classified in one call.
- [`validate_examples_batch`](https://github.com/zeeguu/api/blob/master/tools/validate_and_clean_examples.py#L186-L196). Fan-in batching: generated examples validated ~20 at a time (`BATCH_SIZE`).
- [`get_adaptive_simplification_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/article_simplification.py#L8-L14). Fan-out batching: one call produces simplified versions for *all* CEFR levels simpler than the original.

## Notes

- *Prompt caching is a partial substitute.* Some providers (e.g. DeepSeek) cache a repeated prompt prefix and discount it. That amortizes the preamble's *cost*, but not its *latency* or the per-call overhead of many round-trips — so batching still earns its keep even where the provider caches prompts.

## Known Uses

- **[Batch prompting](https://arxiv.org/abs/2301.08721)** (Cheng, Kasai & Yu, EMNLP 2023) packs multiple independent samples under one shared instructional prompt in a single call, cutting token and time cost roughly inverse-linearly with batch size.
- **Vertical batching** maps to structured-output calls that emit several keyed results at once (and to the OpenAI/Anthropic multi-output `n` parameter).
- *Distinguish from provider batch APIs.* The [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch) and [Anthropic Message Batches](https://platform.claude.com/docs/en/docs/build-with-claude/batch-processing) give ~50% off large asynchronous jobs, but each request still carries and pays for its own full prompt — they amortize scheduling and rate-limit overhead, *not* the in-prompt instructional overhead this pattern targets.

> [!draft]- Notes after the focus group
> - drain pattern?
