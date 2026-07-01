---
layout: default
title: "LLM-Checking-LLM"
subtitle: "Quality Assurance Patterns"
subtitle_url: "../#quality-assurance-patterns"
permalink: /llm-checking-llm/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a>
</nav>


**Example (Zeeguu):** After generating contextual example sentences for vocabulary words, a second LLM call reviews the examples for accuracy, naturalness, and appropriate difficulty level.

**Forces:** LLMs are imprecise generators, but verification of specific properties (e.g., grammatical correctness) is a more constrained task than open-ended generation (e.g., text simplification). A second, focused LLM call can catch errors that the first, more complex call introduced.

**Solution:** Use one LLM call to generate a result, then use a separate LLM call to check or refine it. The verification prompt can be simpler and more focused than the generation prompt.

**Note:** This is distinct from ensemble methods or chain-of-thought: the key insight is that checking is a fundamentally easier task than generating, and this asymmetry can be exploited architecturally.



---
[← LLM Output Provenance](../llm-output-provenance/){:.nav-prev} &nbsp;·&nbsp; [All patterns](../#the-patterns) &nbsp;·&nbsp; [LLM Content Validation Tracking →](../llm-content-validation-tracking/){:.nav-next}

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM-Checking-LLM%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+LLM-Checking-LLM%0A%2A%2ASection%3A%2A%2A+Quality+Assurance+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-checking-llm%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
