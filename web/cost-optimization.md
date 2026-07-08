---
layout: default
title: "Cost Optimization"
permalink: /cost-optimization/
---


[← All patterns](../#the-patterns)


We use *cost* as shorthand for any expensive, metered resource: most visibly the per-token API bill. However, costs are also latency, compute, and energy. The unifying force is that LLM calls carry a large, often *fixed* overhead (the instructional prompt, the network round-trip), so invoking them naïvely wastes that setup on a tiny payload.

These patterns are really about *economy*, each attacking the bill from a different angle. [Prompt Amortization](../prompt-amortization/) **amortizes a fixed overhead** across many calls, so the expensive preamble is paid once rather than per item. [Escalate to the LLM](../escalate-to-the-llm/) **spends the LLM only in proportion to the value it adds**, reaching for it only where a cheaper tool falls short. [Slow-Path Inference](../slow-path-inference/) **pays premium, low-latency rates only when a user is waiting**, routing deferrable work to a cheaper path. [Per-User Consumption Budget](../per-user-consumption-budget/) **bounds what any single user can consume**, so user-driven demand cannot run the bill up without limit. The same frugality transfers to non-monetary resources, which is why Prompt Amortization cuts latency as well as dollars.

- [Prompt Amortization](../prompt-amortization/)
- [Escalate to the LLM](../escalate-to-the-llm/)
- [Slow-Path Inference](../slow-path-inference/)
- [Per-User Consumption Budget](../per-user-consumption-budget/)



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this category](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BCost+Optimization%5D+&labels=feedback%2Ccost-optimization&body=%2A%2ARe%3A%2A%2A+Cost+Optimization%0A%2A%2ASection%3A%2A%2A+Cost+Optimization%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fcost-optimization%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
