---
layout: default
title: "Fail-Fast Provider Chain"
permalink: /fail-fast-provider-chain/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../latency-and-availability/">Latency and Availability</a>
</nav>


## Example

(Zeeguu): The app uses a unified LLM service proxy which tries Anthropic first; on any error (timeout, rate limit, API error), it immediately switches to DeepSeek without retry. This keeps worst-case latency bounded while maintaining availability.

## Forces

LLM providers experience outages, rate limits, and latency spikes. Retry logic increases latency and may still fail. Different providers offer similar capabilities at different price/performance points.

## Solution

Configure a chain of LLM providers with no retries. On any failure, immediately fall back to the next provider in the chain. Prioritize speed over exhausting retry budgets.

## Applicability

The pattern earns its keep most on **real-time paths where a user is waiting**. There the latency budget is tight, so spending it on a retry against a failing provider is the wrong move: failing over immediately keeps the worst case bounded. For offline or batched work, where nobody is waiting, retries and backoff are more affordable, and it can be worth retrying the cheaper provider before moving on.

## Note

This differs from [Escalate to the LLM](../escalate-to-the-llm/) in that all components in the chain are LLMs offering equivalent capabilities: this is a *fallback* for reliability, not the *escalation* to a more capable (and more expensive) tier.

## Known Uses

- **[Karrot](https://medium.com/daangn/karrots-genai-platform-5cf6e813838e)** (Korea's largest secondhand marketplace) runs a tiered resilience chain on its GenAI platform — retry, then region failover, then cross-provider fallback: "If Google's `gemini-2.5-flash` is unavailable even across regions, we route to OpenAI's GPT-5."
- **[Slack](https://slack.engineering/slack-ai-the-path-to-multi-cloud/)**'s routing layer trips a circuit breaker on latency/error spikes and diverts to a designated backup: "we always designate backup models for every feature; if the primary choice doesn't meet our performance or quality thresholds in real-time, the system knows exactly where to go next."
- **[Digits](https://www.youtube.com/watch?v=Zv490D5Lvgw)** routes LLM calls through an internal proxy specifically to fail over between providers, because "neither OpenAI nor Anthropic maintain 100% uptime."
- **[Whatnot](https://medium.com/whatnot-engineering/the-model-is-the-easy-part-building-the-llm-platform-at-whatnot-ec8730fa9bdf)** treats reliability as a platform concern, adding "multi-provider support, moving toward fallback behavior by default."
- *Tools that ship this.* Gateways provide fallback chains as a configurable feature ([Portkey](https://portkey.ai/docs/product/ai-gateway/fallbacks), [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/configuration/fallbacks/), [LiteLLM Router](https://docs.litellm.ai/docs/proxy/reliability), which defaults to retry-then-fallback) — the enforcement mechanism, not a deployment.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../multiplexed-dispatch/">← Multiplexed Dispatch</a><a class="nav-next" href="../llm-as-wizard-of-oz/">LLM as Wizard of Oz →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BFail-Fast+Provider+Chain%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Fail-Fast+Provider+Chain%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Ffail-fast-provider-chain%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
