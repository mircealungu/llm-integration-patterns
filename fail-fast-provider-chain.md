---
layout: default
title: "Fail-Fast Provider Chain"
permalink: /fail-fast-provider-chain/
---

[← All patterns](../)

# Fail-Fast Provider Chain


**Example** (Zeeguu): The app uses a unified LLM service proxy which tries Anthropic first; on any error (timeout, rate limit, API error), it immediately switches to DeepSeek without retry. This keeps worst-case latency bounded while maintaining availability.    

**Forces**: LLM providers experience outages, rate limits, and latency spikes. Retry logic increases latency and may still fail. Different providers offer similar capabilities at different price/performance points.    

**Solution**: Configure a chain of LLM providers with no retries. On any failure, immediately fall back to the next provider in the chain. Prioritize speed over exhausting retry budgets.    

**Note**: This differs from the *LLM as Fallback* pattern in that all components in the chain are LLMs offering equivalent capabilities — the fallback is for reliability, not for capability escalation.

[← All patterns](../)
