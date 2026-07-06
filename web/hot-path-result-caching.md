---
layout: default
title: "Hot-Path Result Caching"
permalink: /hot-path-result-caching/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../latency-and-availability/">Latency and Availability</a>
</nav>


## Context

The same or near-identical LLM request recurs within a short window — many users hitting the same content, or one user re-requesting — but *which* requests recur is unpredictable, so they cannot be precomputed ahead of time.

## Example

Multi-word expression (MWE) detection finds the phrases in an article that a learner might want translated as a unit (for example *kick the bucket*). It uses an LLM, gated by a cheap Stanza pass (see [Hybrid Classical+LLM Pipeline](../hybrid-classical-llm-pipeline/)), and the LLM call is the expensive part, so the analysis is worth caching: the detector keeps a 500-entry in-memory cache, so when multiple users read the same article, phrase analyses computed for the first reader are served instantly to the rest. Hit rates are highest for popular articles that many users read in the same window.

## Problem

How can the same expensive LLM call be avoided when it recurs unpredictably within a short window?

## Forces

Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

## Solution

Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

## Consequences

- **Repeats are near-free.** A hit within the window returns from memory at ~zero cost and latency; hit rate is highest for popular content many users read in the same window.
- **Memory and staleness are the price.** The cache costs memory and adds invalidation complexity; it fits only where brief staleness is acceptable and the input space clusters naturally.
- **Variant: persist it.** A DB-backed cache outlives process memory and survives restarts (Zeeguu uses this too), trading a little speed for durability.

## Known Uses

- **Walmart** — Walmart's chief software architect describes a production *semantic* cache (vector-similarity, not exact match) for e-commerce search, reporting a hit rate "closer to 50%" on tail queries. *(Reported in a [vendor writeup of the talk](https://portkey.ai/blog/transforming-e-commerce-search-with-generative-ai-insights-from-walmarts-journey/); the claims are attributed to Walmart on the record, but the source is secondary.)*
- *Tools that ship this, not documented deployments.* Result caching is common enough to be productized: dedicated LLM caches ([GPTCache](https://aclanthology.org/2023.nlposs-1.24/), exact + semantic) and gateway caches ([Helicone](https://docs.helicone.ai/features/advanced-usage/caching), [Portkey](https://portkey.ai/docs/product/ai-gateway/cache-simple-and-semantic), [LangChain](https://python.langchain.com/docs/integrations/llm_caching/)).
- *Honest note.* First-party write-ups of *reactive* LLM-output caching are scarce; most published examples (Yelp, Instacart) are *anticipatory precomputation* of head queries (see [Anticipatory Precomputation](../anticipatory-precomputation/)) rather than caching on a miss.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../anticipatory-precomputation/">← Anticipatory Precomputation</a><a class="nav-next" href="../multiplexed-dispatch/">Multiplexed Dispatch →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHot-Path+Result+Caching%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Hot-Path+Result+Caching%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhot-path-result-caching%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
