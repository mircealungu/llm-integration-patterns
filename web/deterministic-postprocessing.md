---
layout: default
title: "Deterministic Postprocessing"
permalink: /deterministic-postprocessing/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../trusting-llm-output/">Trusting LLM Output</a>
</nav>


## Context

LLM output carries a deterministic formatting defect (a stable trailing string, a known preamble, leaked markdown in a plain-text field), the same defect shows up on every call, and it is already present in rows written to the database.

## Example

LLM-simplified article summaries consistently ended with a Unicode ellipsis (`…`), making every home-card preview read as an unfinished sentence. One option was to add a "do not end with ellipsis" instruction to the [simplification](../zeeguu/#article-simplification) prompt; the chosen option was a five-line regex stripping any trailing `…` or `..+` at serialization time. Because it runs as each summary is served, not on the stored row, it fixes every case at 100%, including the ~60k rows already in the database, with no backfill and no row ever rewritten.

## Problem

Should a deterministic defect be fixed by instructing the model, or in code?

## Forces

When LLM output has a deterministic formatting defect (a stable trailing string, a known preamble, leaked markdown in a plain-text field, trailing whitespace), the obvious instinct is to fix it in the prompt. But:
- Prompt compliance is probabilistic; the same constraint in code is 100%.
- Prompt tokens cost money on every call and can distract the model from the actual semantic task.
- Prompt changes do not affect rows already in the database.
- Code is testable and reviewable; prompt instructions are not.

## Solution

Enforce deterministic constraints in code, at the post-processing or serialization boundary. Reserve prompt instructions for things that genuinely require model judgment.

## Consequences

- A code-side fix is 100% reliable, costs no prompt tokens, is testable and reviewable, and (applied at the serialization boundary) cleans every already-stored row on the way out with no backfill, none of which a prompt instruction achieves.
- It applies only to genuinely deterministic defects. The test is whether the rule needs model judgment: *strip a trailing `…`* belongs in code, *don't mention the user's name* the model has to enforce. A code-side rule list that keeps growing is a signal the task is poorly scoped, not that it needs more rules.

## Known Uses

- *Adjacent structural cousin.* Structured-output libraries such as **[Outlines](https://dottxt-ai.github.io/outlines/latest/)** constrain generation so the format is valid upfront, and explicitly contrast this with the common practice of "fixing bad outputs after generation using parsing, regex, or fragile code": evidence that code-side repair is widespread, though Outlines *prevents* rather than *repairs*.
- *Largely best-practice / folklore.* We found no source that names this specific rule: repair a *deterministic* defect in code, not the prompt, because code is 100% reliable and also fixes already-stored rows. The literature documents the stronger cousin (constrained decoding / structured outputs) and generic output sanitization, so we present this as its own contribution and cite these as adjacent, not prior.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../llm-content-validation-tracking/">← LLM Content Validation Tracking</a><a class="nav-next" href="../targeted-user-feedback/">Targeted User Feedback →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BDeterministic+Postprocessing%5D+&labels=feedback%2Ctrusting-llm-output&body=%2A%2ARe%3A%2A%2A+Deterministic+Postprocessing%0A%2A%2ASection%3A%2A%2A+Trusting+LLM+Output%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fdeterministic-postprocessing%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
