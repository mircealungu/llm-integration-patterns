---
layout: default
title: "LLM-Checking-LLM"
permalink: /llm-checking-llm/
---

[← All patterns](../)

**Example (Zeeguu):** After generating contextual example sentences for vocabulary words, a second LLM call reviews the examples for accuracy, naturalness, and appropriate difficulty level.

**Forces:** LLMs are imprecise generators, but verification of specific properties (e.g., grammatical correctness) is a more constrained task than open-ended generation (e.g., text simplification). A second, focused LLM call can catch errors that the first, more complex call introduced.

**Solution:** Use one LLM call to generate a result, then use a separate LLM call to check or refine it. The verification prompt can be simpler and more focused than the generation prompt.

**Note:** This is distinct from ensemble methods or chain-of-thought — the key insight is that checking is a fundamentally easier task than generating, and this asymmetry can be exploited architecturally.

[← All patterns](../)
