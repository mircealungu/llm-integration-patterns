---
layout: default
title: "What Makes These Patterns LLM-Specific?"
permalink: /what-makes-these-patterns-llm-specific/
---

[← All patterns](../)

# What Makes These Patterns LLM-Specific?

Some of these patterns echo general distributed systems wisdom (batching, fallback, redundant dispatch). What makes them distinctly relevant to LLM integration is the specific combination of forces:

* **Cost structure** — per-token pricing with high fixed prompt overhead, unlike flat-rate API calls  
* **Non-determinism** — same input can yield different outputs, necessitating verification chains  
* **Asymmetry between generation and verification** — checking is easier than producing  
* **General-purpose capability** — the same component can serve as prototype, primary, or fallback  
* **Quality–cost–latency tradeoff space** — uniquely wide compared to traditional APIs

[← All patterns](../)
