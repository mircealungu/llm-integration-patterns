---
layout: default
title: "Prompt Amortization"
permalink: /prompt-amortization/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../using-the-llm-efficiently/">Using the LLM Efficiently</a>
</nav>


<figure class="img" style="max-width:420px">
  <a href="/images/prompt-amortization-combined-validation.png"><img src="/images/prompt-amortization-combined-validation.png" alt="The [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L72) template: ~250 lines of validation rules, frequency/[CEFR](../zeeguu/#cefr-levels)/phrase-type taxonomies, output format, and examples, wrapped around just three variables (`{word}`, `{translation}`, `{context}`). Sent one pair at a time, the entire preamble is re-paid on every call. This fixed overhead is the cost the pattern amortizes."></a>
  <figcaption>The [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L72) template: ~250 lines of validation rules, frequency/[CEFR](../zeeguu/#cefr-levels)/phrase-type taxonomies, output format, and examples, wrapped around just three variables (`{word}`, `{translation}`, `{context}`). Sent one pair at a time, the entire preamble is re-paid on every call. This fixed overhead is the cost the pattern amortizes.</figcaption>
</figure>


## Context

Many LLM calls share the same shape: a large, fixed instructional prompt (rules, taxonomies, output format, examples) wrapped around a tiny variable input (see figure). The work is offline and batchable: nobody is blocked on any single result.

## Example

Several Zeeguu jobs have exactly this shape. Rather than pay the preamble once per item, they batch (i.e., pack) related items into a single call, in one of two directions: **fan-in** (many inputs, one call) or **fan-out** (one input, many outputs):

- **[Meaning](../zeeguu/#the-learner-model) classification** (*fan-in*) sends ~15 word-meanings per call, sharing one frequency/CEFR-type taxonomy prompt across the whole batch.[^amort-meaning]
- **Example-sentence validation** (*fan-in*) checks ~20 generated examples per call.[^amort-validate]
- **[Article simplification](../zeeguu/#article-simplification)** (*fan-out*) produces every CEFR level simpler than the original in one call, one section per level, turning four or five requests into one, about 75% fewer calls for a typical article.[^amort-simplify]

[^amort-meaning]: The batched meaning-classifier prompt, [`create_batch_meaning_frequency_and_type_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/meaning_frequency_classifier.py#L52-L67) in the `zeeguu/api` repository.
[^amort-validate]: The batch example-sentence validator, [`validate_examples_batch`](https://github.com/zeeguu/api/blob/master/tools/validate_and_clean_examples.py#L186-L196) in the `zeeguu/api` repository.
[^amort-simplify]: The multi-level simplification prompt, [`get_adaptive_simplification_prompt`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/prompts/article_simplification.py#L8-L14) in the `zeeguu/api` repository.



## Problem

Sent one item at a time, that fixed preamble is re-paid on every call and dominates token cost and latency. How can it be paid once instead of once per item, without blowing past the model's quality or context limits?

## Forces

- **Preamble overhead.** The preamble is large by necessity: detailed rules, taxonomies, and examples are what make the output accurate and consistent, so quality pulls it up, and it cannot be trimmed without losing quality. Sent one item at a time, that fixed preamble is re-paid on every call, in tokens, cost, and latency. The only lever left is to amortize it. *(pushes toward bigger batches)*
- **Quality ceiling.** Accuracy and consistency degrade as more items share one call; past ~15–20 small items some models start dropping or muddling entries. *(pushes toward smaller batches)*
- **Context ceiling.** Input *and* output must fit the window; for fan-out the output side binds first, since each result is full-length.
- **Interactive latency.** Fan-in requires waiting to accumulate enough items to fill a batch: fine offline, but unacceptable when a user is blocked on a single result.

## Solution

At its core, this is `map` for LLM calls: apply one shared, expensive prompt across a batch so its setup is paid once, not once per item. It takes two forms:

- ***Fan-in* batching** packs many independent inputs into one prompt, spreading a large instructional preamble across the whole batch.
- ***Fan-out* batching** produces many outputs from a single input, emitting one section per output and collapsing several requests into one.

Both combine naturally with [Anticipatory Precomputation](../anticipatory-precomputation/): because results are computed offline, there is the luxury of batching.

## Consequences

- **Cost and latency amortize with batch size.** The fixed preamble is paid once per call instead of once per item, so per-item token cost *and* wall-clock latency fall roughly inversely with the batch size.
- **Batch size is capped by the tightest ceiling, and which ceiling binds flips by direction.** For fan-in (many small items) the *quality* ceiling binds first (~15–20 items before the model drops or muddles entries), far below what the token window allows; for fan-out (full-length outputs) the *token* ceiling binds first, on the output side, since each result is full-length. So the workable batch size is workload-specific and must be tuned, not maximized.
- **Applies only to deferrable work.** Fan-in must wait to accumulate items, so the pattern fits offline / pre-computed paths (composes with [Anticipatory Precomputation](../anticipatory-precomputation/)) and is unavailable when a user is blocked on a single result.

## Known Uses

- **[Batch prompting](https://arxiv.org/abs/2301.08721)** (Cheng, Kasai & Yu, EMNLP 2023) packs multiple independent samples under one shared instructional prompt in a single call, cutting token and time cost roughly inverse-linearly with batch size.
- The *fan-out* direction maps directly to structured-output calls that emit several keyed results at once, and to the OpenAI/Anthropic multi-output `n` parameter.
- *Distinguish from provider batch APIs.* The [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch) and [Anthropic Message Batches](https://platform.claude.com/docs/en/docs/build-with-claude/batch-processing) give ~50% off large asynchronous jobs, but each request still carries and pays for its own full prompt; they amortize scheduling and rate-limit overhead, *not* the in-prompt instructional overhead this pattern targets.

## Notes

- **Both directions are the same `map`, over a different axis.** Fan-in maps the prompt over inputs, e.g. `map(validate, examples)`. Fan-out maps over outputs for a fixed input, e.g. `map(level → simplify(article, level), levels)`. Either way the shared prompt is the function whose fixed setup the batch pays for once.
- *Prompt caching is a partial substitute.* Some providers (e.g. DeepSeek) cache a repeated prompt prefix and discount it. That amortizes the preamble's *cost*, but not its *latency* or the per-call overhead of many round-trips, so batching still earns its keep even where the provider caches prompts.



---
<div class="pattern-footer-nav"><a class="nav-next" href="../escalate-to-the-llm/">Escalate to the LLM →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BPrompt+Amortization%5D+&labels=feedback%2Cusing-the-llm-efficiently&body=%2A%2ARe%3A%2A%2A+Prompt+Amortization%0A%2A%2ASection%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fprompt-amortization%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
