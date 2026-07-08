---
layout: default
title: "Using the LLM Efficiently"
permalink: /using-the-llm-efficiently/
---


[← All patterns](../#the-patterns)


An LLM call is slow and metered, so a recurring question in any integration is how *not* to make the call, or how to make each one count. The patterns here keep the model's cost and latency off the user's path: paying a large fixed prompt once across a batch rather than once per item, reaching for the LLM only when a cheaper tool falls short, letting a classical stage gate it so it runs only where its judgment is needed, and computing likely-needed results ahead of time so the model never runs while a user waits. The unifying force is that the LLM is the expensive, slow component: the cheapest call is often the one avoided.

- [Prompt Amortization](../prompt-amortization/) ★
- [Escalate to the LLM](../escalate-to-the-llm/) ★
- [Hybrid Classical+LLM Pipeline](../hybrid-classical-llm-pipeline/) ★
- [Anticipatory Precomputation](../anticipatory-precomputation/) ★
- [Slow-Path Inference](../slow-path-inference/)
- [Hot-Path Result Caching](../hot-path-result-caching/)
- [Multiplexed Dispatch](../multiplexed-dispatch/)
- [Fail-Fast Provider Chain](../fail-fast-provider-chain/)
- [Per-User Consumption Budget](../per-user-consumption-budget/)



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this category](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BUsing+the+LLM+Efficiently%5D+&labels=feedback%2Cusing-the-llm-efficiently&body=%2A%2ARe%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2ASection%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fusing-the-llm-efficiently%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
