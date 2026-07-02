---
layout: default
title: "Centralized Model Selection"
permalink: /centralized-model-selection/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../#lifecycle-management">Lifecycle Management</a>
</nav>


## Example

Zeeguu's reader has an on-demand "Ask LLM" translation action. Its model ID, `claude-sonnet-4-20250514`, was hardcoded at three call sites in the translation service and two more in the MWE detector. Anthropic retired that snapshot; every call began returning `404 not_found_error`. The error was swallowed one layer down (the helper returns `None` on any exception), so the endpoint returned a generic `404 "LLM translation failed"` and the reader silently degraded to an "**Ask LLM — try again**" button that could never succeed.

<figure class="img" style="max-width:420px">
  <a href="/images/centralized-model-selection-try-again.png"><img src="/images/centralized-model-selection-try-again.png" alt="centralized model selection try again"></a>
</figure>

Nothing in the code had changed; a date had passed. The error started showing up. 


The fix itself was mechanical: swap to the live snapshot the rest of the codebase already used. But finding it took a dig through production logs, and the swap had to be repeated at five sites. 

To avoid this happening again in the future, Zeeguu now keeps every model identifier in [one module](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/models.py), keyed by *role* (`WORD_TRANSLATION`, `MWE_DETECTION`, `SIMPLIFICATION`, …) and each resolving to a canonical vendor ID declared once; a feature asks for `models.WORD_TRANSLATION` and never names a snapshot, so the next retirement is a one-line edit.

## Forces

- Model identifiers are volatile in a way ordinary configuration is not 
- Providers deprecate and retire dated snapshots on *their* schedule, so a hardcoded ID that works today returns a 404 at some future date, with no change to the code at all. 
- Model choice is also cross-cutting: the same handful of IDs get copy-pasted across many features and several cost/quality tiers, so a single retirement breaks many call sites at once, and there is no one place to see, or change, which model each feature uses. Because the failure is a runtime error on a string that looks perfectly valid, it survives code review and type-checking.

## Solution

Keep every model identifier in one central module. Declare the canonical vendor IDs once, then expose *role-based aliases* (one per use: translation, classification, simplification…) that resolve to them. Call sites import the role, never the raw string. Surviving a vendor retirement, or moving one feature to a cheaper or faster tier, becomes a one-line change in a file that documents the whole model landscape on one screen.

## Notes

- The mechanism is classical (single source of truth; no magic strings). What makes it an LLM pattern is the *force*: vendor-driven model deprecation turns an innocuous hardcoded string into a scheduled runtime failure. It is the direct defense against the *"old ones regularly deprecated"* property listed among the core LLM forces in the introduction.
- Prefer **role-based** aliases over vendor-based constants. `WORD_TRANSLATION = HAIKU` reads as intent and lets one re-point a single feature's tier without touching others; a bare `HAIKU = "claude-haiku-…"` re-exported everywhere quietly couples unrelated features to the same choice.
- Composes with [LLM Output Provenance](../llm-output-provenance/): the identifier a system stamps onto a generated artifact and the identifier it uses to *select* the model at call time should be the same central constant, so the two can never drift apart.
- Composes with [Fail-Fast Provider Chain](../fail-fast-provider-chain/): the chain decides the *order* of providers to try; this module names *which model* each provider entry uses.

## War Story

The same commit that repaired the retirement uncovered a second casualty of the identical disease. Simplified articles were being stamped `ai_model="claude-3-5-sonnet"` while the simplifier had long since moved to Haiku. The provenance field named a model that was no longer even in the pipeline (see [LLM Output Provenance](../llm-output-provenance/)). Same root cause as the retirement: a model identifier duplicated into a place nobody remembers to update, silently going stale. Centralizing selection lets the provenance stamp and the call-time choice read from the same constant, so they cannot disagree.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../llm-as-wizard-of-oz/">← LLM as Wizard of Oz</a><a class="nav-next" href="../llm-output-provenance/">LLM Output Provenance →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BCentralized+Model+Selection%5D+&labels=feedback%2Clifecycle-management&body=%2A%2ARe%3A%2A%2A+Centralized+Model+Selection%0A%2A%2ASection%3A%2A%2A+Lifecycle+Management%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fcentralized-model-selection%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
