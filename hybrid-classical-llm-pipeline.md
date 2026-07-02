---
layout: default
title: "Hybrid Classical+LLM Pipeline"
subtitle: "Quality Assurance Patterns"
subtitle_url: "../#quality-assurance-patterns"
permalink: /hybrid-classical-llm-pipeline/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a>
</nav>


**Example (Zeeguu)**: Multi-word expression (MWE) detection runs Stanza's dependency parser first, as a cheap high-recall gate. If Stanza flags no candidate in a sentence, the LLM is never called. When it does flag one, an LLM re-analyzes the whole sentence and its verdict is used (and if the LLM finds no expression, its precision is trusted over Stanza's). The LLM therefore runs on only the fraction of sentences that might contain an expression, rather than on every sentence.    

**Forces**: Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.    

**Solution**: Run the cheap classical tool first, as a high-recall gate: invoke the LLM only when the classical stage fires, and skip it otherwise (the common case, and the main cost saving). When it fires, let the LLM make the precision decision. The two are not alternatives: the classical stage controls *when* the LLM runs; the LLM controls *what counts*.    

**Tradeoff**: Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity.



---
[← LLM Content Validation Tracking](../llm-content-validation-tracking/){:.nav-prev} &nbsp;·&nbsp; [All patterns](../#the-patterns) &nbsp;·&nbsp; [Temperature as Task Selector →](../temperature-as-task-selector/){:.nav-next}

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHybrid+Classical%2BLLM+Pipeline%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+Hybrid+Classical%2BLLM+Pipeline%0A%2A%2ASection%3A%2A%2A+Quality+Assurance+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhybrid-classical-llm-pipeline%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
