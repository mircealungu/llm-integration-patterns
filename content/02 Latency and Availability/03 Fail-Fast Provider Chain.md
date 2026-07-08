# Fail-Fast Provider Chain

## Context

A request is served by one of several LLM providers on the user's critical path, and any provider can intermittently error, rate-limit, or spike in latency. The providers are interchangeable for this request: a valid answer from any of them is acceptable, even if their quality varies slightly, because availability matters more than which one served.

## Example

(Zeeguu): The app uses a unified LLM service proxy which tries Anthropic first; on any error (timeout, rate limit, API error), it immediately switches to DeepSeek without retry. This keeps worst-case latency bounded while maintaining availability.

## Problem

How can the request keep succeeding within its latency budget when a provider fails, without burning that budget on retries?

## Forces

LLM providers experience outages, rate limits, and latency spikes. Retry logic increases latency and may still fail. Different providers offer similar capabilities at different price/performance points. On this path what matters is a valid answer within the latency budget: quality variation between the providers is tolerable, so whichever one serves the request is fine.

## Solution

Configure a chain of LLM providers with no retries. On any failure, immediately fall back to the next provider in the chain. Prioritize speed over exhausting retry budgets.

## Consequences

- **The request survives an outage, and latency stays bounded.** A dead or slow provider no longer fails the request, and skipping retries keeps the worst case tight.
- **It shines on real-time paths, less so offline.** Where a user waits, spending the budget on a retry against a failing provider is the wrong move. For offline or batched work nobody is waiting, so retry-and-backoff, even retrying the cheaper provider first, is more affordable.
- **Cost attribution shifts to whoever served.** A fallback changes which provider is billed and at what rate (composes with *Per-User Consumption Budget* and *Centralized Model Selection*).

## Note

This differs from *Escalate to the LLM* in that all components in the chain are LLMs offering equivalent capabilities: this is a *fallback* for reliability, not the *escalation* to a more capable (and more expensive) tier.

*Pair it with a circuit breaker.* Fail-fast falls back per request, but a provider that stays down still costs its full timeout on every call before the chain moves on. A circuit breaker removes that tax: once a provider trips (repeated failures or slow responses), it is skipped for a cooldown and the next provider is called directly, so a sustained outage stops taxing every request. Slack's routing layer does exactly this (see Known Uses).

*Or race instead of chaining.* This chain is sequential: one call, a second only on failure, so it costs 1× but a slow or dead primary adds its timeout to that request. Where the latency tail matters more than cost and the call is cheap or low-volume, dispatch to several providers in parallel and take the first (*Multiplexed Dispatch*): N× the cost, but the tail collapses and failover is immediate.

## Known Uses

- **[Karrot](https://medium.com/daangn/karrots-genai-platform-5cf6e813838e)** (Korea's largest secondhand marketplace) runs a tiered resilience chain on its GenAI platform: retry, then region failover, then cross-provider fallback: "If Google's `gemini-2.5-flash` is unavailable even across regions, we route to OpenAI's GPT-5."
- **[Slack](https://slack.engineering/slack-ai-the-path-to-multi-cloud/)**'s routing layer trips a circuit breaker on latency/error spikes and diverts to a designated backup: "we always designate backup models for every feature; if the primary choice doesn't meet our performance or quality thresholds in real-time, the system knows exactly where to go next."
- **[Digits](https://www.youtube.com/watch?v=Zv490D5Lvgw)** routes LLM calls through an internal proxy specifically to fail over between providers, because "neither OpenAI nor Anthropic maintain 100% uptime."
- **[Whatnot](https://medium.com/whatnot-engineering/the-model-is-the-easy-part-building-the-llm-platform-at-whatnot-ec8730fa9bdf)** treats reliability as a platform concern, adding "multi-provider support, moving toward fallback behavior by default."
- *Tools that ship this.* Gateways provide fallback chains as a configurable feature ([Portkey](https://portkey.ai/docs/product/ai-gateway/fallbacks), [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/configuration/fallbacks/), [LiteLLM Router](https://docs.litellm.ai/docs/proxy/reliability), which defaults to retry-then-fallback), the enforcement mechanism, not a deployment.
