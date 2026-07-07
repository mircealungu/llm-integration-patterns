# Centralized Model Selection

## Context

A single LLM model identifier is referenced from many call sites across a codebase. Providers retire dated model snapshots on their own schedule, so an ID that is valid today can start returning 404 at a future date with no change to the code.

## Example

Zeeguu's reader has an on-demand "Ask LLM" translation action. Its model ID, `claude-sonnet-4-20250514`, was hardcoded at three call sites in the translation service and two more in the MWE detector. Anthropic retired that snapshot; every call began returning `404 not_found_error`. The error was swallowed one layer down (the helper returns `None` on any exception), so the endpoint returned a generic `404 "LLM translation failed"` and the reader silently degraded to an "**Ask LLM — try again**" button that could never succeed.

![[centralized-model-selection-try-again.png|420]]

Nothing in the code had changed; a date had passed. The error started showing up. 


The fix itself was mechanical: swap to the live snapshot the rest of the codebase already used. But finding it took a dig through production logs, and the swap had to be repeated at five sites. 

To avoid this happening again in the future, Zeeguu now keeps every model identifier in [one module](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/models.py), keyed by *role* (`WORD_TRANSLATION`, `MWE_DETECTION`, `SIMPLIFICATION`, …) and each resolving to a canonical vendor ID declared once; a feature asks for `models.WORD_TRANSLATION` and never names a snapshot, so the next retirement is a one-line edit.

## Problem

How can a provider's model retirement be survived without hunting down every hardcoded model ID scattered across the codebase?

## Forces

- Model identifiers are volatile in a way ordinary configuration is not 
- Providers deprecate and retire dated snapshots on *their* schedule, so a hardcoded ID that works today returns a 404 at some future date, with no change to the code at all. 
- Model choice is also cross-cutting: the same handful of IDs get copy-pasted across many features and several cost/quality tiers, so a single retirement breaks many call sites at once, and there is no one place to see, or change, which model each feature uses. Because the failure is a runtime error on a string that looks perfectly valid, it survives code review and type-checking.

## Solution

Keep every model identifier in one central module. Declare the canonical vendor IDs once, then expose *role-based aliases* (one per use: translation, classification, simplification…) that resolve to them. Call sites import the role, never the raw string. Surviving a vendor retirement, or moving one feature to a cheaper or faster tier, becomes a one-line change in a file that documents the whole model landscape on one screen.

## Consequences

- **A retirement is a one-line edit.** Surviving a deprecation, or re-pointing a feature to a cheaper or faster tier, changes one line in a module that shows the whole model landscape on one screen, rather than a hunt across call sites.
- **The registry only helps if nothing bypasses it.** It adds one layer of indirection, and a single stray hardcoded ID reintroduces the exact failure the pattern prevents, so the discipline has to hold everywhere.
- **One constant keeps selection and provenance in sync.** Because the same central constant both selects the model and stamps it onto output, the two cannot drift (composes with *LLM Output Provenance*); it also names which model each entry of a *Fail-Fast Provider Chain* uses.

## Notes

- The mechanism is classical (single source of truth; no magic strings). What makes it an LLM pattern is the *force*: vendor-driven model deprecation turns an innocuous hardcoded string into a scheduled runtime failure. It is the direct defense against the *"old ones regularly deprecated"* property listed among the core LLM forces in the introduction.
- Prefer **role-based** aliases over vendor-based constants. `WORD_TRANSLATION = HAIKU` reads as intent and lets one re-point a single feature's tier without touching others; a bare `HAIKU = "claude-haiku-…"` re-exported everywhere quietly couples unrelated features to the same choice.
- Composes with *LLM Output Provenance*: the identifier a system stamps onto a generated artifact and the identifier it uses to *select* the model at call time should be the same central constant, so the two can never drift apart.
- Composes with *Fail-Fast Provider Chain*: the chain decides the *order* of providers to try; this module names *which model* each provider entry uses.
- *Alternative — AI gateway.* An AI gateway can host the role→model mapping as named aliases in its config, relocating this pattern's registry out of application code. See the broader treatment of what gateways do and do not subsume in *What Makes These Patterns LLM-Specific? → Relationship to LLM Gateways*.

## War Story

The same commit that repaired the retirement uncovered a second casualty of the identical disease. Simplified articles were being stamped `ai_model="claude-3-5-sonnet"` while the simplifier had long since moved to Haiku. The provenance field named a model that was no longer even in the pipeline (see *LLM Output Provenance*). Same root cause as the retirement: a model identifier duplicated into a place nobody remembers to update, silently going stale. Centralizing selection lets the provenance stamp and the call-time choice read from the same constant, so they cannot disagree.

## Known Uses

- **[Sourcegraph Cody](https://sourcegraph.com/docs/cody/enterprise/model-configuration)** binds each feature *role* — `chat`, `fastChat`, `codeCompletion` — to a `modelRef` in a central `defaultModels` map, so changing which model powers a feature is a single config edit rather than a call-site change: genuine role-based central selection in a shipped product.
- *Enablers.* Gateways relocate the role→model map into their config as aliases ([LiteLLM model aliases](https://docs.litellm.ai/docs/completion/model_alias), [Portkey Model Catalog](https://portkey.ai/docs/product/ai-gateway/virtual-keys)) — the same mechanism, hosted outside app code.
- The mechanism is the classic *single source of truth*; what makes it LLM-specific is vendor-driven model deprecation (see this pattern's forces). We did not find a public first-hand account of centralizing model IDs *in response to a deprecation outage* — Zeeguu's is our instance.

> [!draft]- Alternatives to explore after the focus group
> - proxy, dependency injection
> - agent anti-pattern?
