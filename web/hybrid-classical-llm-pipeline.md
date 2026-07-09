---
layout: default
title: "Hybrid Classical+LLM Pipeline"
permalink: /hybrid-classical-llm-pipeline/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../using-the-llm-efficiently/">Using the LLM Efficiently</a>
</nav>


## Context

A task can be served by a fast, deterministic classical tool (a dependency parser, a POS (part-of-speech) tagger, a rule extractor) that misses edge cases, and by an LLM that handles the edge cases but is too expensive to run on every input.

## Example

[Multi-word expression (MWE) detection](../zeeguu/#multi-word-expressions) runs [Stanza](https://arxiv.org/abs/2003.07082) (a classical NLP library) first, as a cheap *high-recall* gate: it catches every possible candidate, tolerating false positives. If Stanza flags no candidate in a sentence, the LLM is never called. When it does flag one, an LLM re-analyzes the whole sentence and makes the *precision* call, rejecting the false positives; its verdict is used even when it overrides Stanza and finds no expression. The LLM therefore runs on only the fraction of sentences that might contain an expression, rather than on every sentence.

## Problem

How can both high recall and high precision be reached without paying LLM cost on every input?

## Forces

- **Recall at the gate.** The classical stage must flag every input the LLM might need to judge; anything it misses never reaches the LLM and is lost, so the gate is tuned for high recall. *(pushes toward a looser, more permissive gate)*
- **Cost of the LLM.** Every input the gate passes costs an LLM call, so a gate that flags too much erodes the saving that motivates the pattern. *(pushes toward a tighter gate)*
- **Precision needs the LLM.** The classical stage is fast but blunt; only the LLM can make the fine distinction and reject the false positives a permissive gate lets through. Neither stage alone achieves both high recall and high precision.

## Solution

Run the cheap classical tool first, as a high-recall gate: invoke the LLM only when the classical stage fires, and skip it otherwise (the common case, and the main cost saving). When it fires, let the LLM make the precision decision. The two are not alternatives: the classical stage controls *when* the LLM runs; the LLM controls *what counts*.

## Consequences

- **The LLM runs only where it is needed.** It fires on the fraction of inputs the classical gate flags, so the common case costs nothing extra while the LLM still makes the precision call.
- **Two components instead of one.** The classical gate and the LLM stage are each built, tuned, and maintained separately, and the hand-off between them (what the gate flags, what the LLM is asked) has to stay correct as either evolves. That added complexity is usually justified by the saving from skipping the LLM on the common case.
- **The gate must have high recall.** A candidate the classical stage misses never reaches the LLM, so the recall of the cheap stage caps the recall, and thus the overall quality, of the whole pipeline.

## Known Uses

- **[RankGPT](https://arxiv.org/abs/2304.09542)** (Sun et al., EMNLP 2023) uses BM25 (a classical keyword-ranking function) to retrieve ~100 candidates, then an LLM for listwise reranking: a classical high-recall generator with an LLM precision filter.
- The same *retrieve-then-rerank* shape, a high-recall first-stage search followed by a neural precision reranker ([Nogueira and Cho](https://arxiv.org/abs/1901.04085)), is the standard two-stage architecture behind modern production search.

## Notes

- Close kin to [Escalate to the LLM](../escalate-to-the-llm/) and to a model cascade: all three run a cheap step first and call the LLM selectively. The difference is the trigger. Escalate uses the cheap tool's answer and reaches for the LLM only when it is inadequate (a failure, or user dissatisfaction); here the cheap tool gates on detected difficulty (a flagged candidate) and the LLM's verdict replaces it, like a cascade, but the gating signal comes from a separate classical stage rather than the model's own confidence.
- *Enablers (not instances).* Frameworks such as [spaCy-llm](https://github.com/explosion/spacy-llm) (mixing LLM and rule-based components in one pipeline) and rerank products such as [Cohere Rerank](https://docs.cohere.com/docs/rerank-overview) make it easy to wire a classical stage to an LLM, but a library that provides the plumbing is the mechanism, not evidence of an in-app instance.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../escalate-to-the-llm/">← Escalate to the LLM</a><a class="nav-next" href="../anticipatory-precomputation/">Anticipatory Precomputation →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHybrid+Classical%2BLLM+Pipeline%5D+&labels=feedback%2Cusing-the-llm-efficiently&body=%2A%2ARe%3A%2A%2A+Hybrid+Classical%2BLLM+Pipeline%0A%2A%2ASection%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhybrid-classical-llm-pipeline%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
