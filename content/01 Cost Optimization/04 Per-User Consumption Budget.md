# Per-User Consumption Budget

## Example

Several of Zeeguu's LLM actions are triggered *directly by a user's click* and charge a shared provider account the instant the user acts: on-demand "Ask LLM" translation, on-demand article simplification, and audio-lesson generation (LLM script + text-to-speech). Because the spend is attached to individual user behaviour, a single enthusiastic user — or a buggy client, or a script — can run up the bill or exhaust shared rate limits for everyone.

Zeeguu already contains a crude instance of the defense. Audio-lesson generation allows **only one active generation per user at a time**: `AudioLessonGenerationProgress.create_for_user` deletes any existing record and `find_active_for_user` gates new requests. That is a per-user *concurrency* budget of exactly one — the cheapest possible bound — chosen precisely because the audio pipeline is among the most expensive actions in the system.

The general pattern extends this idea to any LLM-backed resource: cap each user's consumption over a time window, denominated in whatever proxy is cheap to measure and *good enough* — number of on-demand translations per day, characters simplified per week, generations per hour, or, at the precise end, actual token cost.

## Forces

- On-demand LLM actions cost real money and latency per invocation, and — unlike a pre-computed or cached feature — they are driven by user behaviour, so from the system's side consumption is unbounded.
- Consumption is wildly uneven across users. A small number of heavy users, an abusive script, or a runaway client can dominate cost and exhaust the shared provider's rate limits, degrading service for everyone.
- The bound must be per *user* (the entity the spend is attached to), not global, or one user's overuse silently taxes the rest.
- Exact cost accounting is precise but comparatively expensive to build (capture token usage, maintain a current price table). Often a coarse proxy — a count, a concurrency cap, a time budget — is far cheaper and adequately bounds the failure you actually care about.

## Solution

Give each user a budget on an LLM-backed resource and refuse or degrade once it is exhausted. Denominate the budget in the **coarsest proxy that adequately tracks the risk**:

- **concurrency** — at most *N* in flight per user (the audio-lesson case, *N* = 1);
- **count over a window** — translations per day, simplifications per week;
- **volume** — characters simplified, tokens consumed;
- **actual cost** — the precise variant (see below).

When a budget is exhausted, **degrade rather than fail** where possible: fall back to the cheaper non-LLM path (serve the Google Translate result and simply stop escalating to the LLM — see *Escalate to the LLM*), queue the request, or show a friendly "try again later."

**Precise variant — Per-User Cost Attribution.** At the accurate end, meter every LLM call as `(user, feature, model, provider, input_tokens, output_tokens, timestamp)`, store **tokens** (provider-neutral) and derive **cost** through a central price table, and aggregate per user. This is the most accurate budget denomination and doubles as observability — it answers *which users and which features drive the bill*. It also composes with *Centralized Model Selection* (price table keyed by the same model constants) and *LLM Output Provenance* (the per-artifact provenance record is the natural place to also stamp token counts: provenance says *how was it made*, this adds *what did it cost, and to whom*). Prefer a coarse proxy unless you genuinely need this precision.

## Notes

- Choose the coarsest proxy that prevents the failure you care about. If the risk is "a script hammers *simplify*," a per-hour count stops it; you do not need per-token accounting.
- Attribute to the provider that **actually** served the call — a *Fail-Fast Provider Chain* fallback changes who you pay and at what rate.
- The graceful-degradation clause is what keeps this user-friendly rather than punitive: a language learner who exhausts their LLM-translation budget still gets Google Translate, not an error.

## Relationship to LLM Gateways

Gateways provide per-key / per-user rate limiting and spend caps out of the box (LiteLLM virtual-key budgets and RPM/TPM limits, Portkey, Cloudflare AI Gateway), so both the coarse and the cost-based variants can be *partly* delegated — but only if the application tags each call with a user id (and, for per-feature budgets, with the feature). As with metering generally (see *What Makes These Patterns LLM-Specific? → Relationship to LLM Gateways*), the gateway supplies the **enforcement primitive** (count, throttle, cap); the pattern owns the **policy** — which resource, which window, and crucially *what the user gets when the budget is exhausted* (degrade to Google Translate vs. hard refuse), which is a product decision no gateway can make.

## Status

A crude instance (single active audio generation per user) already ships. The general per-user budget across on-demand actions, and the cost-accounting variant, are not yet implemented — included as a candidate to invite discussion on whether this is one pattern with several denominations (concurrency / count / volume / cost) or several distinct patterns.

## Known Uses

- **[LiteLLM Proxy](https://docs.litellm.ai/docs/proxy/users)** supports per-key `max_budget` (with auto-reset), per-user budgets across a user's keys, and rpm/tpm/parallel-request caps.
- **[Portkey](https://portkey.ai/docs/product/administration/enforce-budget-and-rate-limit)** attaches a USD budget and rate limits to an individual key, expiring it when the budget is exhausted.
- **[Helicone](https://docs.helicone.ai/features/advanced-usage/custom-rate-limits)** rate-limits per user via a policy header denominated in request count or cost (e.g. "$5.00/hour/user").
- *Note.* All three are gateway primitives: they enforce the *mechanism* but not the domain *policy* (which resource, and what the user gets when exhausted) — consistent with this pattern's gateway discussion.
