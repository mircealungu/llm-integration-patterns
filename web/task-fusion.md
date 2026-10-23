---
layout: default
title: "Task Fusion"
permalink: /task-fusion/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../candidate/">Candidate</a>
</nav>


*Ask several questions about one input in a single call, so the input is sent and read once.*

## Context

Several features need different answers about the same input: its level, a summary, a classification, a yes/no check. The input is large compared to each question, for example a whole article, or a word with the sentence it appeared in. Each answer needs the whole input to be read.

## Example

When Zeeguu's crawler finds a new article, it needs seven things from it: its [CEFR level](../zeeguu/#cefr-levels), a summary, a title and summary at each simpler level, whether it is news or evergreen, and whether it is disturbing, cut off by a paywall, or advertising. Each task needs the whole article, and each task's instructions are much shorter than the article (Figure 1). Asked one at a time, the article would be sent and read seven times.

<figure class="img" style="max-width:85%">
  <a href="/images/task-fusion-sizes.svg"><img src="/images/task-fusion-sizes.svg" alt="Instructions for each task in Zeeguu&#x27;s article-assessment call, in characters, next to a typical article (about 600 words), at commit [`c853d76`](https://github.com/zeeguu/api/tree/c853d767). Every task reads the whole article."></a>
  <figcaption>Instructions for each task in Zeeguu&#x27;s article-assessment call, in characters, next to a typical article (about 600 words), at commit [`c853d76`](https://github.com/zeeguu/api/tree/c853d767). Every task reads the whole article.</figcaption>
</figure>

## Problem

How can several answers about one input be obtained without paying for the input once per answer?

## Forces

- **Big input.** The input is often much larger than any one question about it, and every call that needs it pays for all of it again. *(pulls toward reading the input once)*
- **Quality risk.** A call that asks for more can answer each part worse. How much depends on the model and the task, and only measuring tells. *(pulls toward one call per task)*
- **Independent tasks.** Different features own different answers, change them on different schedules, and may want different models for them. *(pulls toward one call per task)*

## Solution

Ask for all the answers about one input in one call, each in its own named field, so the input is sent once. Keep together the tasks that need the same reading of the input, and split a task off when it needs a different model, changes often, or makes the other answers worse.

## Example Resolved

- **Article assessment.** One call returns all seven answers about a new article, each in its own field, so the article is sent once instead of seven times.[^fusion-assess]
- **Translation validation.** When a learner saves a word, one call both checks the translation (and corrects it if needed) and fills in everything the flashcard needs: how common the meaning is, its CEFR level, whether it is a single word, a collocation or an idiom, a short explanation, and the dictionary form.[^fusion-validate]

[^fusion-assess]: [`get_assessment_and_summary_prompt`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/article_simplification.py#L139) in the `zeeguu/api` repository.
[^fusion-validate]: [`COMBINED_VALIDATION_PROMPT`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/translation_validator.py#L8-L94) and its output schema in the `zeeguu/api` repository.

## Consequences

- **The input is paid for once.** Cost and latency no longer grow with the number of questions asked about it.
- **The tasks fail together.** One malformed field, or a model that ends its answer early, loses every answer at once. Zeeguu's assessment prompt let a model reject an article with a single word, and one provider used that exit for almost every article, so no article got a level or a summary either (see [One Wish per Genie](../one-wish-per-genie/)).
- **The tasks change together.** Editing the prompt for one answer means re-checking all of them, and all of them run on the same model.
- **The number of tasks is capped by quality.** Zeeguu once assessed an article and simplified it to every level in the same call, and split this into an assessment call and one call per level when the simplifications came out shortened and merged.

## Known Uses

- **Published evaluation.** [*Multi-Task Inference*](https://arxiv.org/abs/2402.11597) (Son et al., ACL 2024) asks whether a model can answer several instructions about one input in a single call. On their benchmark of 25 tasks, each with two or three sub-tasks, a single call took on average 1.46 times less time than one call per sub-task, and accuracy did not drop: it rose by up to 7.3% for Llama-2-Chat-70B and up to 12.4% for GPT-4.
- **A mixed result.** A comparison of [single-task and multitask prompts](https://doi.org/10.3390/electronics13234712) (*Electronics*, 2024) on smaller open models found single-task prompts better in three of five experiments and multitask prompts better in two, with the outcome depending on the model. This is the *Quality risk* force, measured.
- **Practitioner report.** Microsoft's ISE team [extracts themes, the sentiment of each theme, and comparisons with competitors](https://devblogs.microsoft.com/ise/insights_generation_from_customer_feedback_using_llms/) from each piece of retail customer feedback with one prompt and one JSON answer; the competitor comparison was added by extending the existing prompt rather than with a new call. The post does not say how many calls run per comment, so this is close but not certain.

## Related Patterns

[Prompt Amortization](../prompt-amortization/) shares one set of instructions across many items; *Task Fusion* shares one input across many tasks. Both put more into one call, and both carry the same quality risk. [One Wish per Genie](../one-wish-per-genie/) describes how a fused prompt's early exit behaved differently across providers.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../check-what-should-exist/">← Check What Should Exist</a><a class="nav-next" href="../regression-set-per-llm-task/">Regression Set per LLM Task →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BTask+Fusion%5D+&labels=feedback%2Ccandidate&body=%2A%2ARe%3A%2A%2A+Task+Fusion%0A%2A%2ASection%3A%2A%2A+Candidate+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Ftask-fusion%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
