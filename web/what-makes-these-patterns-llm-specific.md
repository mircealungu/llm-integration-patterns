---
layout: default
title: "What Makes These Patterns LLM-Specific?"
permalink: /what-makes-these-patterns-llm-specific/
---


[← All patterns](../#the-patterns)


Some of these patterns echo general distributed systems wisdom: batching (in [Prompt Amortization](../prompt-amortization/)), fallback (in [Escalate to the LLM](../escalate-to-the-llm/)), redundant dispatch (in the parallel translation providers). What makes them distinctly relevant to LLM integration is that each draws on forces that are properties of the LLM rather than of any domain:

* **Cost structure**: per-token pricing with high fixed prompt overhead, unlike flat-rate API calls (drives [Prompt Amortization](../prompt-amortization/), [Escalate to the LLM](../escalate-to-the-llm/), [Anticipatory Precomputation](../anticipatory-precomputation/)).
* **Non-determinism**: the same input can yield a different, or malformed, output, so correctness must be enforced around the model (drives [Defensive Output Parsing](../defensive-output-parsing/), [LLM-Checking-LLM](../llm-checking-llm/), [LLM Content Validation Tracking](../llm-content-validation-tracking/)).
* **Asymmetry between generation and verification**: checking one property is easier than producing the whole output (drives [LLM-Checking-LLM](../llm-checking-llm/)).
* **General-purpose capability**: the same component can serve as prototype, primary, or fallback (drives [Rent, Then Build](../rent-then-build/) and [Escalate to the LLM](../escalate-to-the-llm/)).
* **A rapidly evolving, vendor-controlled substrate**: models and prompts improve and are deprecated on the vendor's schedule, underneath long-lived data (drives [LLM Output Provenance](../llm-output-provenance/) and [Soft Invalidation of LLM Artifacts](../soft-invalidation-of-llm-artifacts/)).
* **Quality-cost-latency tradeoff space**: uniquely wide compared to traditional APIs, and what the efficiency patterns navigate.



## Relationship to LLM Gateways

Several of these patterns ([Fail-Fast Provider Chain](../fail-fast-provider-chain/), [Centralized Model Selection](../centralized-model-selection/), and hot-path caching) are being commoditized into LLM-gateway infrastructure (LiteLLM, Portkey, Cloudflare AI Gateway). This does not invalidate them as patterns; it relocates their *implementation* from application code into shared infrastructure. A pattern documents a recurring solution whether it is hand-rolled or shipped by a gateway, and knowing the pattern is precisely what lets one judge whether a given gateway implements it well (e.g. most gateways do *not* provide [Multiplexed Dispatch](../multiplexed-dispatch/) with alternative-caching). Connection pooling remained a pattern long after every ORM started shipping one.

The recurring shape across all of these is that the gateway supplies a *mechanism* while the pattern owns the *intent, the domain join, and the decision the mechanism drives*. This is sharpest in [Per-User Consumption Budget](../per-user-consumption-budget/), where the gateway can throttle and cap but only the application knows which resource to bound and what the user should get when the budget is exhausted.



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this section](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BWhat+Makes+These+Patterns+LLM-Specific%3F%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+What+Makes+These+Patterns+LLM-Specific%3F%0A%2A%2ASection%3A%2A%2A+What+Makes+These+Patterns+LLM-Specific%3F%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fwhat-makes-these-patterns-llm-specific%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
