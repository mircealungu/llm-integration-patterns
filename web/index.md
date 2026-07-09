---
layout: default
title: "Architectural Patterns for Integrating LLMs into User-Facing Applications"
description: "Lessons from a language-learning platform"
subtitle: "Lessons from a language-learning platform"
permalink: /
---


*Status: working draft, Jul 2026*
*See also: the [PDF version](/paper.pdf), a selection of these patterns submitted to PLoP 2026.*

### What is this?

A living catalogue of the recurring patterns that come up when integrating LLMs into real, user-facing software, grounded in the Zeeguu language-learning platform and developed in the open as a working paper. Contributions are welcome: an **instance** (a note that a pattern also appears in another system) or a **case study** (a rich example from a new domain, which earns its own page alongside Zeeguu). Contributors receive named credit.




### The Idea

While there is growing literature on building LLM-native products such as chatbots, agents, and retrieval-augmented generation (RAG) pipelines, and on using LLMs for code generation, there is surprisingly little guidance on the **software engineering challenges of integrating LLMs as components into existing interactive applications** where real users expect fast, reliable, and trustworthy responses.

We expect this integration to become the common case: over time, more and more existing user-facing applications will adopt LLMs not as standalone chatbots but as components working behind the scenes to improve the user experience. This is why we present a set of patterns that highlight the challenges and opportunities such integrations raise. 

Indeed, LLMs have a unique combination of properties that create novel architectural forces: 

- they are expensive (per-token pricing),   
- slow (high latency),   
- non-deterministic (same input can yield different outputs),  
- rapidly evolving (new models released every few months and old ones regularly deprecated),  
- imprecise (they make mistakes), and   
- general-purpose (they can attempt almost any task described as text). 

These properties demand specific engineering strategies, and they recur as the forces each pattern must balance.

Over the past year, we have been integrating LLMs into [Zeeguu](https://zeeguu.org), an open-source platform for personalized language learning that helps users learn foreign languages by reading authentic online content (real articles, not textbook exercises). Through this work, we have identified a set of recurring architectural patterns for LLM integration. Because these forces are properties of the LLM itself rather than of language learning, we expect the patterns to generalise beyond our specific domain.

Each pattern that follows is presented in the same format: context, example, problem, forces, solution, consequences, known uses, and notes.

## Case Studies

- [Zeeguu](zeeguu/)

## The Patterns

*★ marks the patterns in the [PLoP workshop paper](/paper.pdf); the rest are part of the extended catalogue we are growing toward a book.*

### [Using the LLM Efficiently](using-the-llm-efficiently/)
- [Prompt Amortization](prompt-amortization/) ★
- [Escalate to the LLM](escalate-to-the-llm/) ★
- [Hybrid Classical+LLM Pipeline](hybrid-classical-llm-pipeline/) ★
- [Anticipatory Precomputation](anticipatory-precomputation/) ★
- [Slow-Path Inference](slow-path-inference/)
- [Hot-Path Result Caching](hot-path-result-caching/)
- [Multiplexed Dispatch](multiplexed-dispatch/)
- [Fail-Fast Provider Chain](fail-fast-provider-chain/)
- [Per-User Consumption Budget](per-user-consumption-budget/)

### [Trusting LLM Output](trusting-llm-output/)
- [Defensive Output Parsing](defensive-output-parsing/) ★
- [LLM-Checking-LLM](llm-checking-llm/) ★
- [LLM Content Validation Tracking](llm-content-validation-tracking/) ★
- [Deterministic Postprocessing](deterministic-postprocessing/)
- [Targeted User Feedback](targeted-user-feedback/)

### [Managing Change Over Time](managing-change-over-time/)
- [LLM Output Provenance](llm-output-provenance/) ★
- [Soft Invalidation of LLM Artifacts](soft-invalidation-of-llm-artifacts/) ★
- [Rent, Then Build](rent-then-build/) ★
- [Centralized Model Selection](centralized-model-selection/)

### [Candidate](candidate/)
- [Temperature as Task Selector](temperature-as-task-selector/)
- [Prompt Injection Containment](prompt-injection-containment/)

## More

- [Related Work](related-work/)
- [What Makes These Patterns LLM-Specific?](what-makes-these-patterns-llm-specific/)
- [Limitations and Future Work](limitations-and-future-work/)
- [Conclusion](conclusion/)



---
[💬 Open an issue about this paper](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5Bthe+paper%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+the+paper%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
