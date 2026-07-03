# Fail-Fast Provider Chain

## Example

(Zeeguu): The app uses a unified LLM service proxy which tries Anthropic first; on any error (timeout, rate limit, API error), it immediately switches to DeepSeek without retry. This keeps worst-case latency bounded while maintaining availability.

## Forces

LLM providers experience outages, rate limits, and latency spikes. Retry logic increases latency and may still fail. Different providers offer similar capabilities at different price/performance points.

## Solution

Configure a chain of LLM providers with no retries. On any failure, immediately fall back to the next provider in the chain. Prioritize speed over exhausting retry budgets.

## Applicability

The pattern earns its keep most on **real-time paths where a user is waiting**. There the latency budget is tight, so spending it on a retry against a failing provider is the wrong move: failing over immediately keeps the worst case bounded. For offline or batched work, where nobody is waiting, retries and backoff are more affordable, and it can be worth retrying the cheaper provider before moving on.

## Note

This differs from *Escalate to the LLM* in that all components in the chain are LLMs offering equivalent capabilities: this is a *fallback* for reliability, not the *escalation* to a more capable (and more expensive) tier.

## Known Uses

- **[Portkey](https://portkey.ai/docs/product/ai-gateway/fallbacks)** fallback mode walks a prioritized provider list, switching on the first non-2xx response (retries are a separate opt-in).
- **[Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/configuration/fallbacks/)** tries providers sequentially, falling to the next on error or timeout, and reports which provider served via a response header.
- **[LiteLLM Router](https://docs.litellm.ai/docs/proxy/reliability)** supports ordered fallback chains; note it defaults to retry-*then*-fallback, so it is fail-fast only when retries are set to zero.
