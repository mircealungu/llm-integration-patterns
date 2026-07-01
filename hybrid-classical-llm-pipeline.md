---
layout: default
title: "Hybrid Classical+LLM Pipeline"
subtitle: "Hybrid Pipeline Patterns"
subtitle_url: "../#hybrid-pipeline-patterns"
permalink: /hybrid-classical-llm-pipeline/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a>
</nav>


**Example (Zeeguu)**: Multi-word expression (MWE) detection uses Stanza's dependency parser to identify candidate phrases (fast, high recall), then sends candidates to an LLM to filter out false positives based on semantic analysis (slower, high precision). This achieves better F1 than either approach alone, at a fraction of the cost of LLM-only detection.    

**Forces**: Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.    

**Solution**: Use the classical tool as a high-recall candidate generator, then use the LLM as a precision filter on the candidates. Both tools work together in a pipeline, not as alternatives.    

**Tradeoff**: Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity.



---
[← LLM Content Validation Tracking](../llm-content-validation-tracking/){:.nav-prev} &nbsp;·&nbsp; [All patterns](../#the-patterns) &nbsp;·&nbsp; [Temperature as Task Selector →](../temperature-as-task-selector/){:.nav-next}

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHybrid+Classical%2BLLM+Pipeline%5D+&labels=feedback%2Chybrid-pipeline&body=%2A%2ARe%3A%2A%2A+Hybrid+Classical%2BLLM+Pipeline%0A%2A%2ASection%3A%2A%2A+Hybrid+Pipeline+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhybrid-classical-llm-pipeline%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
