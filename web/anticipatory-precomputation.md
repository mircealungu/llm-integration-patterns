---
layout: default
title: "Anticipatory Precomputation"
permalink: /anticipatory-precomputation/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../using-the-llm-efficiently/">Using the LLM Efficiently</a>
</nav>


## Context

A user-facing feature needs an LLM result, but the model takes seconds while the user expects a response in well under one, and *which* results a given user will need next is predictable from their behaviour.

## Example

The vocabulary exercises a learner practices are built from the words they looked up while reading, each paired with a machine translation. At reading time an imperfect translation is low-stakes: the reader is only making sense of the text, and can pick a better option from the alternatives menu. But once the platform selects a word for the learner to *learn*, they will drill that word-translation pair over many days, so its correctness suddenly matters. A regular cron job looks ahead: it finds the words each learner is due to study next and validates them with an LLM, so that when the exercise module asks for new words, the vetted ones are ready straight away. If none are precomputed yet (the learner translated a few words and jumped straight into exercises), the validation runs in real time. 

**An even costlier instance: [audio lessons](../zeeguu/#audio-lessons).** Generating a personalized audio lesson is more expensive again: an LLM writes the lesson script (fed the learner's past lessons so a recurring topic, a "talking to a neighbour" lesson they have had before, comes back fresh rather than repeated), then text-to-speech synthesizes the audio, several seconds of work no learner should wait through. A nightly job precomputes the next lessons for recently active learners (prioritized by how recently they practiced), on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. Only a learner who switches to a new topic waits, briefly, while that day's first lesson on it is generated on demand. 

## Problem

How can an LLM-quality result reach the user's critical path without a wait for the model, when upcoming needs are often predictable?

## Forces

- **Latency.** Real-time users expect an answer in about 200ms, but an LLM can take several seconds depending on the prompt and deployment, so it cannot run on the critical path. *(pushes toward precomputing)*
- **Wasted spend on misses.** Precomputing spends tokens on results that may never be requested, so a poor predictor pays for nothing and still misses. *(pushes toward precomputing only high-probability needs)*
- **Predictability.** The pattern is available only where upcoming needs can be forecast from behaviour; the better the behaviour model, the more of the work can move off the critical path.

## Solution

Anticipate likely user needs and precompute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behaviour in order to predict their LLM needs. Keep an on-demand path for cold or mispredicted requests, so a miss degrades to a normal wait rather than a failure.

## Consequences

- **Zero latency at request time.** The LLM's cost and multi-second latency are paid entirely off the critical path; when the user acts, the result is already waiting.
- **Precomputing pays for guesses that miss.** It spends tokens on results that may never be requested, so the value depends on the accuracy of the behaviour model: a poor predictor wastes spend *and* still misses.
- **Needs a reliable "what" and "when" signal, plus a fallback.** It applies only where upcoming needs are predictable; cold or mispredicted requests still need an on-demand path. Composes with [Prompt Amortization](../prompt-amortization/) (offline results can be batched).

## Known Uses

- **[Yelp](https://engineeringblog.yelp.com/2025/02/search-query-understanding-with-LLMs.html)** precomputes LLM query-understanding responses for high-frequency ("head") search queries into a key/value store, "caching (pre-computing) high-end LLM responses for only head queries", reaching 95% of traffic for review-highlight expansions, so the expensive model never runs on the critical path.
- **[Instacart](https://tech.instacart.com/building-the-intent-engine-how-instacart-is-revamping-query-understanding-with-llms-3ac8051ae7ac)**'s Intent Engine serves high-frequency search queries from a precomputed cache of LLM outputs, leaving only ~2% of queries to a real-time model.
- **[ColBERT](https://arxiv.org/abs/2004.12832)** (Khattab & Zaharia, SIGIR 2020) precomputes contextualized passage embeddings for the whole corpus offline, so query time runs only cheap late-interaction matching: the canonical "precompute the expensive representation ahead of time" (the pattern's shape applied to retrieval rather than generation).



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../hybrid-classical-llm-pipeline/">← Hybrid Classical+LLM Pipeline</a><a class="nav-next" href="../slow-path-inference/">Slow-Path Inference →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BAnticipatory+Precomputation%5D+&labels=feedback%2Cusing-the-llm-efficiently&body=%2A%2ARe%3A%2A%2A+Anticipatory+Precomputation%0A%2A%2ASection%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fanticipatory-precomputation%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
