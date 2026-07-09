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

Indeed, LLMs have a unique combination of properties: 

- **expensive**: billed per token, with a large fixed prompt re-paid on every call;   
- **slow**: responses take seconds, not the milliseconds an interactive interface expects;   
- **non-deterministic**: the same input can return a different answer;  
- **rapidly evolving**: models are released and retired on the vendor's schedule, every few months;  
- **imprecise**: they make mistakes, from a malformed response to a confident but wrong answer; and   
- **general-purpose**: they can attempt almost any task expressed in text. 

Integrating a component with these properties into a live, user-facing system is what creates the architectural forces these patterns resolve: the tension between what the model is (slow, costly, non-deterministic) and what users and the surrounding code expect (fast, affordable, well-formed).

Over the past year, we have been integrating LLMs into [Zeeguu](https://zeeguu.org), an open-source platform for personalized language learning that helps users learn foreign languages by enabling them to read authentic online content (real articles, not textbook exercises). Through this work, we have identified a set of architectural patterns for LLM integration, several of them corroborated by documented use in other systems. Because these forces arise from the LLM's own properties and the generic demands of a live application, not from anything specific to language learning, we expect them, and the patterns that resolve them, to recur wherever LLMs are integrated into user-facing systems.

The remainder of the paper is organised as follows. Section 2 introduces Zeeguu, the platform that grounds every example. The catalogue then follows in three themes, using the LLM efficiently (Section 3), trusting its output (Section 4), and managing change over time (Section 5), each pattern given in the same format: context, example, problem, forces, solution, consequences, known uses, notes. Section 6 asks what makes these patterns specific to LLMs, and the paper closes with related work, limitations, and conclusions.

## Case Studies

- [Zeeguu](zeeguu/)

## The Patterns

*★ marks the patterns in the [PLoP workshop paper](/paper.pdf); the rest are part of the extended online catalogue.*

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
- [Acknowledgments](acknowledgments/)



---
[💬 Open an issue about this paper](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5Bthe+paper%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+the+paper%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
