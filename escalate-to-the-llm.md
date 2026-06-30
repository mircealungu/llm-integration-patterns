---
layout: default
title: "Escalate to the LLM"
permalink: /escalate-to-the-llm/
---


[← All patterns](../)


**Example (Zeeguu):** Google Translate serves as the primary translation engine. When a user indicates the translation is inadequate, the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed.

<figure class="img" style="max-width:520px">
  <a href="/images/escalate-to-the-llm.png"><img src="/images/escalate-to-the-llm.png" alt="In Zeeguu, the inline Google translation is the primary path; when the user wants a better rendering they escalate to an LLM on demand via the "Ask LLM" option."></a>
  <figcaption>In Zeeguu, the inline Google translation is the primary path; when the user wants a better rendering they escalate to an LLM on demand via the "Ask LLM" option.</figcaption>
</figure>

**Forces:** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than LLMs for well-defined tasks — but they sometimes fail or produce insufficiently satisfactory results.

**Solution:** Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction.

**Applicability:** This pattern applies broadly — topic classification, named entity recognition, or any NLP task where a cheaper tool handles the common case and the LLM handles the long tail.

**Notes:**

- *Escalation, not fallback.* Unlike a reliability fallback — where the secondary is an equal-or-lesser backup invoked when the primary fails (see *Fail-Fast Provider Chain*) — here the secondary is **more capable and more expensive**, invoked when the primary is not good enough. The movement is *up* in quality and cost, not *down* into degraded mode. That is why we name it escalation.
- *Relationship to the model cascade.* This is the human-/failure-triggered cousin of the **model cascade** in ML serving, where a cheap model runs first and a confidence threshold routes hard inputs to a larger model. The shared shape is *cheap tier first, expensive tier on demand*; the difference is the trigger. A cascade escalates automatically on the model's own low confidence, whereas this pattern escalates on external signals — the primary tool erroring, or the user explicitly declaring the result inadequate. A confidence-based cascade is thus one possible escalation policy; user dissatisfaction is another, and the two can be combined.



---
[← All patterns](../) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BEscalate+to+the+LLM%5D+&labels=feedback%2Ccost-optimization&body=%2A%2ARe%3A%2A%2A+Escalate+to+the+LLM%0A%2A%2ASection%3A%2A%2A+Cost+Optimization+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fescalate-to-the-llm%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
