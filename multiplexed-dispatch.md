---
layout: default
title: "Multiplexed Dispatch"
permalink: /multiplexed-dispatch/
---


<nav class="pattern-nav">
  <a class="nav-prev" href="../hot-path-result-caching/">← Hot-Path Result Caching</a>
  <a class="nav-all" href="../">All patterns</a>
  <a class="nav-next" href="../fail-fast-provider-chain/">Fail-Fast Provider Chain →</a>
</nav>


**Example (Zeeguu):** Real-time translations are dispatched to multiple translation providers in parallel. The first response is used, and the rest are saved for when the user asks for alternatives. 

**Forces:** Multiple LLM providers offer similar capabilities but with varying latency. When speed matters for user experience, relying on a single provider creates a bottleneck.

**Solution:** Dispatch the same request to multiple providers simultaneously and use the first response that arrives. Track the top two fastest providers, and always dispatch to these. 

An alternative to this is **live retrieval**: when the user encounters a translation that they are not sure of, they ask for alternatives, the UI presents the results that are cached, but also asks for alternatives and displays a UI interface that highlights the fact that some of the results are still streaming in.

**Tradeoff:** Increased cost (paying for redundant calls) in exchange for reduced latency.



---
[← Hot-Path Result Caching](../hot-path-result-caching/) &nbsp;·&nbsp; [All patterns](../) &nbsp;·&nbsp; [Fail-Fast Provider Chain →](../fail-fast-provider-chain/) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BMultiplexed+Dispatch%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Multiplexed+Dispatch%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fmultiplexed-dispatch%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
