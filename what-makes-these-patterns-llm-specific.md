---
layout: default
title: "What Makes These Patterns LLM-Specific?"
permalink: /what-makes-these-patterns-llm-specific/
---


[← All patterns](../#the-patterns)


Some of these patterns echo general distributed systems wisdom (batching, fallback, redundant dispatch). What makes them distinctly relevant to LLM integration is the specific combination of forces:

* **Cost structure**: per-token pricing with high fixed prompt overhead, unlike flat-rate API calls  
* **Non-determinism**: same input can yield different outputs, necessitating verification chains  
* **Asymmetry between generation and verification**: checking is easier than producing  
* **General-purpose capability**: the same component can serve as prototype, primary, or fallback  
* **Quality–cost–latency tradeoff space**: uniquely wide compared to traditional APIs

## Relationship to LLM Gateways

Several of these patterns ([Fail-Fast Provider Chain](../fail-fast-provider-chain/), [Centralized Model Selection](../centralized-model-selection/), and hot-path caching) are being commoditized into LLM-gateway infrastructure (LiteLLM, Portkey, Cloudflare AI Gateway). This does not invalidate them as patterns; it relocates their *implementation* from application code into shared infrastructure. A pattern documents a recurring solution regardless of whether you hand-roll it or a gateway ships it, and knowing the pattern is precisely what lets you judge whether a given gateway implements it well (e.g. most gateways do *not* provide [Multiplexed Dispatch](../multiplexed-dispatch/) with alternative-caching). Connection pooling remained a pattern long after every ORM started shipping one.

The recurring shape across all of these is that the gateway supplies a *mechanism* while the pattern owns the *intent, the domain join, and the decision the mechanism drives*. This is sharpest in [Per-User Consumption Budget](../per-user-consumption-budget/), where the gateway can throttle and cap but only the application knows which resource to bound and what the user should get when the budget is exhausted.



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this section](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BWhat+Makes+These+Patterns+LLM-Specific%3F%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+What+Makes+These+Patterns+LLM-Specific%3F%0A%2A%2ASection%3A%2A%2A+What+Makes+These+Patterns+LLM-Specific%3F%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fwhat-makes-these-patterns-llm-specific%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
