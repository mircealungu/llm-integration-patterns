---
layout: default
title: "Anticipatory Precomputation"
permalink: /anticipatory-precomputation/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../latency-and-availability/">Latency and Availability</a>
</nav>


## Context

A user-facing feature needs an LLM result, but the model takes seconds while the user expects a response in well under one, and *which* results a given user will need next is predictable from their behaviour.

## Example

The vocabulary exercises a learner practices are built from the words they looked up while reading. The imperfection of machine translation at reading time can be solved manually by the reader by choosing alternatives from the alternative menu. And even if there are imperfections at the reading time, they are not as consequential as they would be at exercise creation time. Indeed, once the platform decides that a reader has to "learn" a word/translation pair, the user will drill that word meaning over many days. At that point, it becomes critical that the translation is correct. To ensure this, a regular cron job constantly checks for words that learners are due to study and evaluates their appropriateness with LLM calls such that, when the exercises module is looking for new words, the validated words are ready to be presented straight away. Evidently if precomputed words are not available (the user translated a few words and then quickly went to exercises) the appropriateness is computed in real time. 

**An even costlier instance: [audio lessons](../zeeguu/#audio-lessons).** Generating a personalized audio lesson is more expensive again: an LLM writes the lesson script, then text-to-speech synthesizes the audio, several seconds of work no learner should wait through. A nightly job pre-computes the next lessons for recently active learners (prioritized by how recently they practiced), on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. 

## Problem

How can an LLM-quality result reach the user's critical path without a wait for the model, when upcoming needs are often predictable?

## Forces

LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real-time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

## Solution

Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.

## Consequences

- **Zero latency at request time.** The LLM's cost and multi-second latency are paid entirely off the hot path; when the user acts, the result is already waiting.
- **Precomputing pays for guesses that miss.** It spends tokens on results that may never be requested, so the value depends on the accuracy of the behaviour model: a poor predictor wastes spend *and* still misses.
- **Needs a reliable "what" and "when" signal, plus a fallback.** It applies only where upcoming needs are predictable; cold or mispredicted requests still need an on-demand path. Composes with [Prompt Amortization](../prompt-amortization/) (offline results can be batched).

## Known Uses

- **[Yelp](https://engineeringblog.yelp.com/2025/02/search-query-understanding-with-LLMs.html)** pre-computes LLM query-understanding responses for high-frequency ("head") search queries into a key/value store, "caching (pre-computing) high-end LLM responses for only head queries", reaching 95% of traffic for review-highlight expansions, so the expensive model never runs on the hot path.
- **[Instacart](https://tech.instacart.com/building-the-intent-engine-how-instacart-is-revamping-query-understanding-with-llms-3ac8051ae7ac)**'s Intent Engine serves high-frequency search queries from a precomputed cache of LLM outputs, leaving only ~2% of queries to a real-time model.
- **[ColBERT](https://arxiv.org/abs/2004.12832)** (Khattab & Zaharia, SIGIR 2020) precomputes contextualized passage embeddings for the whole corpus offline, so query time runs only cheap late-interaction matching: the canonical "precompute the expensive representation ahead of time."
- *Enabler, not instance.* Provider [batch / offline-inference](https://developers.openai.com/api/docs/guides/batch) endpoints are the infrastructure for computing LLM outputs in bulk off the hot path, not a use of the pattern.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../per-user-consumption-budget/">← Per-User Consumption Budget</a><a class="nav-next" href="../hot-path-result-caching/">Hot-Path Result Caching →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BAnticipatory+Precomputation%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Anticipatory+Precomputation%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fanticipatory-precomputation%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
