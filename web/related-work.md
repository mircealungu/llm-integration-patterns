---
layout: default
title: "Related Work"
permalink: /related-work/
---


[← All patterns](../#the-patterns)


To our knowledge, no peer-reviewed work presents a catalog of architectural patterns for integrating LLMs as components into existing production systems, grounded in real deployment experience and described using the standard pattern format (context, forces, solution, consequences). The contribution is the catalogue itself, organised by three themes: using the LLM efficiently, trusting its output, and managing change over time. Some patterns apply established mechanisms (batching, precomputation, recall gates, soft-delete, distillation) to the distinctive forces of LLM integration; others, notably [LLM Output Provenance](../llm-output-provenance/), [LLM Content Validation Tracking](../llm-content-validation-tracking/), and the external-signal trigger of [Escalate to the LLM](../escalate-to-the-llm/), appear to be new. We flag each honestly as one or the other throughout.

Several practitioner-oriented resources discuss patterns for building LLM-based systems, but they operate at a different level of abstraction and lack the grounding in a specific production system that we aim to provide.

## Practitioner resources

Eugene Yan's **[Patterns for Building LLM-based Systems & Products](https://eugeneyan.com/writing/llm-patterns/)** (2023, blog post) identifies seven patterns: Evals, RAG, Fine-tuning, Caching, Guardrails, Defensive UX, and Collecting User Feedback. These address the question "how do I build an LLM product?" They describe the overall stack for LLM-native applications. Our patterns address a different question: "I have an existing system, and I want to add LLM capabilities as a component: how do I manage cost, quality, latency, and lifecycle?" There is some overlap on caching/pre-computation, but our treatment focuses on prompt amortization and user-need anticipation rather than semantic similarity caching. Yan's work is not peer-reviewed.

ThoughtWorks' **[Emerging Patterns in Building GenAI Products](https://martinfowler.com/articles/gen-ai-patterns/)** (Fowler et al.) and "Engineering Practices for LLM Applications" focus on operational concerns: testing, evaluation, guardrails, and RAG pipelines. These are primarily about LLMOps rather than the architectural decisions for embedding LLMs as components within an existing application.

Andreessen Horowitz's **[Emerging Architectures for LLM Applications](https://a16z.com/emerging-architectures-for-llm-applications/)** (2023) provides a reference architecture for the LLM infrastructure stack (embedding pipelines, vector databases, orchestration layers, agents). Again, this targets LLM-native products rather than LLM integration into existing systems.

Books. "**LLM Design Patterns**" (Huang, Packt, 2024\) and "LLMs in Enterprise" (Menshawy & Fahmy, Packt, 2025\) cover model-level patterns (fine-tuning, quantization, inference optimization, RAG) and enterprise deployment concerns. They do not address application-level integration patterns such as the lifecycle management (Rent, Then Build → specialized tool → Escalate to the LLM), prompt amortization, or LLM output provenance that we identify.

## Academic surveys. 

There is a large body of work on **using LLMs *for* software engineering tasks**: code generation, bug repair, testing, requirements engineering (see surveys by [Fan et al., 2023](https://arxiv.org/abs/2310.03533); [Zhang et al., 2024](https://arxiv.org/abs/2312.15223)). However, these focus on LLMs as tools for developers, not on the engineering challenges of integrating LLMs as runtime components within production software. 

A recent **systematic literature review on software architecture and LLMs** ([Schmid et al., 2025](https://arxiv.org/abs/2505.16697)) found only 18 relevant papers and noted that LLM-based software design remains an open research direction. None of the surveyed academic work addresses the specific architectural patterns for managing cost, quality, latency, and lifecycle when LLMs serve as components in existing applications.

LLM self-verification. For the [LLM-Checking-LLM](../llm-checking-llm/) pattern, there is relevant work on **LLM self-verification**. [Gero et al. (2023)](https://arxiv.org/abs/2306.00024) demonstrated that self-verification improves clinical information extraction accuracy, explicitly building on the asymmetry between verification and generation. However, [Stechly et al. (2024)](https://arxiv.org/abs/2402.08115) showed that self-critique fails for formal reasoning tasks, finding significant performance collapse with self-verification but gains with external verification. Our pattern differs from both in that it uses separate, differently-prompted LLM calls for generation and verification of different properties (e.g., text simplification followed by grammatical correction), rather than asking an LLM to verify its own reasoning.



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this section](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BRelated+Work%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+Related+Work%0A%2A%2ASection%3A%2A%2A+Related+Work%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Frelated-work%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
