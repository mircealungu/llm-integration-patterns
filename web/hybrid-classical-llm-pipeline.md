---
layout: default
title: "Hybrid Classical+LLM Pipeline"
permalink: /hybrid-classical-llm-pipeline/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../quality-assurance/">Quality Assurance</a>
</nav>


## Context

A task can be served by a fast, deterministic classical tool (a dependency parser, a POS tagger, a rule extractor) that misses edge cases, and by an LLM that handles the edge cases but is too expensive to run on every input.

## Example

[Multi-word expression](../zeeguu/#multi-word-expressions) (MWE) detection runs Stanza (a classical NLP library) first, as a cheap *high-recall* gate: it catches every possible candidate, tolerating false positives. If Stanza flags no candidate in a sentence, the LLM is never called. When it does flag one, an LLM re-analyzes the whole sentence and makes the *precision* call, rejecting the false positives; its verdict is used even when it overrides Stanza and finds no expression. The LLM therefore runs on only the fraction of sentences that might contain an expression, rather than on every sentence.

## Problem

How can both high recall and high precision be reached without paying LLM cost on every input?

## Forces

Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.

## Solution

Run the cheap classical tool first, as a high-recall gate: invoke the LLM only when the classical stage fires, and skip it otherwise (the common case, and the main cost saving). When it fires, let the LLM make the precision decision. The two are not alternatives: the classical stage controls *when* the LLM runs; the LLM controls *what counts*.

## Consequences

- **The LLM runs only where it is needed.** It fires on the fraction of inputs the classical gate flags, so the common case costs nothing extra while the LLM still makes the precision call.
- **Two systems must be built and kept in sync.** That is real added complexity, usually justified by the saving from skipping the LLM on the common case.
- **The gate must have high recall.** A candidate the classical stage misses never reaches the LLM, so the recall of the cheap stage caps the precision of the whole.

## Note

Close kin to [Escalate to the LLM](../escalate-to-the-llm/) and to a model cascade: all three run a cheap step first and call the LLM selectively. The difference is the trigger. Escalate uses the cheap tool's answer and reaches for the LLM only when it is inadequate (a failure, or user dissatisfaction); here the cheap tool gates on detected difficulty (a flagged candidate) and the LLM's verdict replaces it, as in a confidence-based cascade.

## Known Uses

- **[RankGPT](https://arxiv.org/abs/2304.09542)** (Sun et al., EMNLP 2023) uses BM25 to retrieve ~100 candidates, then an LLM for listwise reranking: classical high-recall generator + LLM precision filter.
- **[spaCy-llm](https://github.com/explosion/spacy-llm)** (Explosion) is designed to mix LLM components with classical/rule-based ones in a single pipeline.
- **Retrieve-then-rerank** (e.g. [Cohere Rerank](https://docs.cohere.com/docs/rerank-overview)) keeps a high-recall first-stage search and adds a neural precision reranker.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../llm-content-validation-tracking/">← LLM Content Validation Tracking</a><a class="nav-next" href="../defensive-output-parsing/">Defensive Output Parsing →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHybrid+Classical%2BLLM+Pipeline%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+Hybrid+Classical%2BLLM+Pipeline%0A%2A%2ASection%3A%2A%2A+Quality+Assurance%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhybrid-classical-llm-pipeline%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
