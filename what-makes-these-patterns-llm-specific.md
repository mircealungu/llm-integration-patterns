---
layout: default
title: "What Makes These Patterns LLM-Specific?"
permalink: /what-makes-these-patterns-llm-specific/
---


[← All patterns](../)


Some of these patterns echo general distributed systems wisdom (batching, fallback, redundant dispatch). What makes them distinctly relevant to LLM integration is the specific combination of forces:

* **Cost structure**: per-token pricing with high fixed prompt overhead, unlike flat-rate API calls  
* **Non-determinism**: same input can yield different outputs, necessitating verification chains  
* **Asymmetry between generation and verification**: checking is easier than producing  
* **General-purpose capability**: the same component can serve as prototype, primary, or fallback  
* **Quality–cost–latency tradeoff space**: uniquely wide compared to traditional APIs



---
[← All patterns](../) &nbsp;·&nbsp; [💬 Open an issue about this section](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BWhat+Makes+These+Patterns+LLM-Specific%3F%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+What+Makes+These+Patterns+LLM-Specific%3F%0A%2A%2ASection%3A%2A%2A+What+Makes+These+Patterns+LLM-Specific%3F%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fwhat-makes-these-patterns-llm-specific%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
