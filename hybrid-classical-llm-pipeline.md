---
layout: default
title: "Hybrid Classical+LLM Pipeline"
permalink: /hybrid-classical-llm-pipeline/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../#quality-assurance">Quality Assurance</a>
</nav>


## Example

Multi-word expression (MWE) detection runs Stanza's dependency parser first, as a cheap high-recall gate. If Stanza flags no candidate in a sentence, the LLM is never called. When it does flag one, an LLM re-analyzes the whole sentence and its verdict is used (and if the LLM finds no expression, its precision is trusted over Stanza's). The LLM therefore runs on only the fraction of sentences that might contain an expression, rather than on every sentence.

## Forces

Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.

## Solution

Run the cheap classical tool first, as a high-recall gate: invoke the LLM only when the classical stage fires, and skip it otherwise (the common case, and the main cost saving). When it fires, let the LLM make the precision decision. The two are not alternatives: the classical stage controls *when* the LLM runs; the LLM controls *what counts*.

## Tradeoff

Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity.

## Note

Close kin to [Escalate to the LLM](../escalate-to-the-llm/) and to a model cascade: all three run a cheap step first and call the LLM selectively. The difference is the trigger. Escalate uses the cheap tool's answer and reaches for the LLM only when it is inadequate (a failure, or user dissatisfaction); here the cheap tool gates on detected difficulty (a flagged candidate) and the LLM's verdict replaces it, as in a confidence-based cascade.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../llm-content-validation-tracking/">← LLM Content Validation Tracking</a><a class="nav-next" href="../temperature-as-task-selector/">Temperature as Task Selector →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHybrid+Classical%2BLLM+Pipeline%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+Hybrid+Classical%2BLLM+Pipeline%0A%2A%2ASection%3A%2A%2A+Quality+Assurance%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhybrid-classical-llm-pipeline%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
