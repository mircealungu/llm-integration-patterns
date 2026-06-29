---
layout: default
title: "LLM as Fallback"
permalink: /llm-as-fallback/
---


[← All patterns](../)


**Example (Zeeguu):** Google Translate serves as the primary translation engine. When a user indicates the translation is inadequate, the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed.

**Forces:** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than LLMs for well-defined tasks — but they sometimes fail or produce insufficiently satisfactory results.

**Solution:** Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction.

**Applicability:** This pattern applies broadly — topic classification, named entity recognition, or any NLP task where a cheaper tool handles the common case and the LLM handles the long tail.



---
[← All patterns](../) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM+as+Fallback%5D+&labels=feedback%2Ccost-optimization&body=%2A%2ARe%3A%2A%2A+LLM+as+Fallback%0A%2A%2ASection%3A%2A%2A+Cost+Optimization+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-as-fallback%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
