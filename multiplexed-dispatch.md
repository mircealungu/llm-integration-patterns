---
layout: default
title: "Multiplexed Dispatch"
permalink: /multiplexed-dispatch/
---

[← All patterns](../)

# Multiplexed Dispatch


**Example (Zeeguu):** Real-time translations are dispatched to multiple translation providers in parallel. The first response is used, and the rest are saved for when the user asks for alternatives. 

**Forces:** Multiple LLM providers offer similar capabilities but with varying latency. When speed matters for user experience, relying on a single provider creates a bottleneck.

**Solution:** Dispatch the same request to multiple providers simultaneously and use the first response that arrives. Track the top two fastest providers, and always dispatch to these. 

An alternative to this is **live retrieval**: when the user encounters a translation that they are not sure of, they ask for alternatives, the UI presents the results that are cached, but also asks for alternatives and displays a UI interface that highlights the fact that some of the results are still streaming in.

**Tradeoff:** Increased cost (you pay for redundant calls) in exchange for reduced latency.

[← All patterns](../)
