---
layout: default
title: "Prompt Amortization"
permalink: /prompt-amortization/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../using-the-llm-efficiently/">Using the LLM Efficiently</a>
</nav>


*Batch many items into one call, so the fixed prompt is paid once.*

## Context

Many LLM calls share the same shape: a large, fixed instructional prompt (rules, output format, examples) wrapped around a tiny variable input, and re-sent in full on every call.

The work is offline and nobody is blocked on any single result, so an item can wait for others to join it.

## Problem

Many calls send a prompt far bigger than the item it carries, and send it again for every item, so most of what is paid for is the same instructions, repeated. How can a system keep its detailed prompt without paying for it once per item?

## Problem in Zeeguu

Zeeguu makes twenty-one kinds of LLM call. In most of them, a fixed template of a few hundred to several thousand characters wraps an input many times smaller (Figure 1). The [translation-validation prompt](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L94), for example, wraps 5,096 characters of rules around a word, its translation and the sentence it came from. The templates also keep growing as rules are added: all four in the figure are longer than their first version (marked by the vertical tick). 

<figure class="img" style="max-width:85%">
  <a href="/images/prompt-template-sizes.svg"><img src="/images/prompt-template-sizes.svg" alt="Fixed prompt template (blue) and typical input (yellow), in characters, for four of Zeeguu&#x27;s LLM calls at commit [`c853d76`](https://github.com/zeeguu/api/tree/c853d767) (October 2026). The black tick marks each template&#x27;s size at its first version."></a>
  <figcaption>Fixed prompt template (blue) and typical input (yellow), in characters, for four of Zeeguu&#x27;s LLM calls at commit [`c853d76`](https://github.com/zeeguu/api/tree/c853d767) (October 2026). The black tick marks each template&#x27;s size at its first version.</figcaption>
</figure>

## Forces

- **Detailed prompts work better.** The more precisely the rules describe the task, the more accurate and consistent the output. *(pulls toward big prompts)*
- **Cost follows the tokens sent.** Providers charge per token, and locally hosted LLMs use energy in proportion to the tokens they process. Every call sends its whole prompt again, so a big prompt is paid for once per item. *(pulls toward sending fewer tokens)*
- **Quality risk.** The more items one call handles, the worse the model can handle each one: it might skip some, mix them up, or shorten its answers. With many small inputs this starts after about 15 to 20 items, long before the context window is full; with full-length outputs, after only a few. How much depends on the model and the task, and only measuring tells. *(pulls toward small calls)*

## Solution

Put several items into one call, so the prompt is paid once per call instead of once per item,[^amort-cache] and stop adding items before the quality of the answers drops. There are two ways to do it:

- ***Fan-in* batching** packs many independent inputs into one prompt, spreading a large instructional preamble across the whole batch.
- ***Fan-out* batching** produces many outputs from a single input, emitting one section per output and collapsing several requests into one.

<figure class="img">
  <a href="/images/prompt-amortization-diagram.svg"><img src="/images/prompt-amortization-diagram.svg" alt="Fan-in packs many inputs behind one preamble; fan-out asks for many outputs (here, several example sentences for one word) from one. Either way the preamble is paid once per call."></a>
  <figcaption>Fan-in packs many inputs behind one preamble; fan-out asks for many outputs (here, several example sentences for one word) from one. Either way the preamble is paid once per call.</figcaption>
</figure>

## Solution in Zeeguu

Zeeguu uses both forms, on two of the calls in Figure 1:

- **Fan-in: meaning-frequency and idiom-tagging.** Zeeguu stores each word a learner saves together with its translation, a pair it calls a [*meaning*](../zeeguu/#the-learner-model). An offline job sends about 15 of them per call and gets back for each one how common it is and whether the phrase is worth studying as a unit: an idiom such as *break the ice* is, a random pair such as *doctor for* is not.[^amort-meaning]
- **Fan-out: example-sentence generation.** One call asks for three example sentences for a word, so its template is paid once for all three.[^amort-examples]

Fan-out also has a case where Zeeguu went back to one call per item. It used to ask for an article to be [simplified](../zeeguu/#article-simplification) to several levels in a single call: a B2 article came back at B1, A2 and A1 at once. Writing several versions in one answer, the model shortened them and merged paragraphs. An evaluation showed that one call per level simplifies much better, so Zeeguu now pays for the extra calls.[^amort-simplify] For that task, the batch size that works is one.

[^amort-meaning]: The batched tagging prompt, [`create_batch_meaning_frequency_and_type_prompt`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/meaning_frequency_classifier.py#L52-L67) in the `zeeguu/api` repository, run by [`tools/reclassify_unclassified_phrases.py`](https://github.com/zeeguu/api/blob/c853d767/tools/reclassify_unclassified_phrases.py).
[^amort-examples]: The example-generation prompt, [`format_prompt`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/example_generation.py#L223-L236) in the `zeeguu/api` repository, called with `count=3`.
[^amort-simplify]: The old multi-level prompt, [`get_adaptive_simplification_prompt`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/article_simplification.py#L28), is now reached only from a manual tool, `tools/simplify_article.py`. The split, its evaluation and its cost are in [zeeguu/api#773](https://github.com/zeeguu/api/pull/773).
[^amort-cache]: Two provider features sound similar but do something else. *Batch APIs* ([OpenAI Batch](https://developers.openai.com/api/docs/guides/batch), [Anthropic Message Batches](https://platform.claude.com/docs/en/docs/build-with-claude/batch-processing)) discount large asynchronous jobs, but every request in the job still pays for its full prompt. *Prompt caching* does discount a prompt that repeats across calls, but each item still makes its own call and waits for its own answer. It also works only under conditions: the cached prompt expires if no call reuses it soon enough (five minutes by default on Anthropic), and short prompts are not cached at all. As of October 2026 Anthropic's minimum is 512 tokens, about 2,000 characters, so the meaning-frequency and idiom-tagging template (about 1,000) is too short.

## Consequences

- **Cost and latency amortize with batch size.** The fixed preamble is paid once per call instead of once per item, so per-item token cost *and* wall-clock latency fall roughly inversely with the batch size.
- **A batch size to tune, and to tune again.** The size that works depends on the model, the prompt and the items, and only measuring finds it. Nothing signals when a new model or a longer prompt has moved it, so it has to be measured again after each change.
- **Outputs have to be matched back to their items.** A batched answer can skip an item or stop short, so the code checks which items got a usable output, rather than assuming they line up, and sends the rest again ([Defensive Output Parsing](../defensive-output-parsing/)).
- **Fan-in adds a wait.** Items sit until a batch fills, so each result arrives later than it would on its own. This is why the pattern needs work that nobody is waiting on.

## Known Uses

- *The fan-in direction is prior art.* Packing many independent inputs under one shared prompt is the published **[batch prompting](https://arxiv.org/abs/2301.08721)** technique (Cheng, Kasai & Yu, EMNLP 2023), which cuts token and time cost roughly inverse-linearly with batch size. This pattern's contribution is to add the *fan-out* direction and to frame both as a single move: amortizing one fixed preamble.
- The *fan-out* direction maps directly to structured-output calls that emit several keyed results at once, and to the OpenAI/Anthropic multi-output `n` parameter (which requests several completions per call).

## Related Patterns

[Anticipatory Precomputation](../anticipatory-precomputation/) (computing likely-needed results ahead of time) makes work offline, and offline work can wait for a batch to fill. [Task Fusion](../task-fusion/) is the mirror image: it shares one input across many tasks, where this pattern shares one set of instructions across many items.



---
<div class="pattern-footer-nav"><a class="nav-next" href="../escalate-to-the-llm/">Escalate to the LLM →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BPrompt+Amortization%5D+&labels=feedback%2Cusing-the-llm-efficiently&body=%2A%2ARe%3A%2A%2A+Prompt+Amortization%0A%2A%2ASection%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Fprompt-amortization%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
