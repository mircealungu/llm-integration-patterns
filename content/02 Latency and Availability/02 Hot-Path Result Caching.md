# Hot-Path Result Caching

## Context

The same or near-identical LLM request recurs within a short window — many users hitting the same content, or one user re-requesting — but *which* requests recur is unpredictable, so they cannot be precomputed ahead of time.

## Example

Multi-word expression (MWE) detection finds the phrases in an article that a learner might want translated as a unit (for example *kick the bucket*). It uses an LLM, gated by a cheap Stanza pass (see *Hybrid Classical+LLM Pipeline*), and the LLM call is the expensive part, so the analysis is worth caching: the detector keeps a 500-entry in-memory cache, so when multiple users read the same article, phrase analyses computed for the first reader are served instantly to the rest. Hit rates are highest for popular articles that many users read in the same window.

## Problem

How do you avoid paying for the same expensive LLM call again and again when the repeats are unpredictable?

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
- *Honest note.* First-party write-ups of *reactive* LLM-output caching are scarce; most published examples (Yelp, Instacart) are *anticipatory precomputation* of head queries (see *Anticipatory Precomputation*) rather than caching on a miss.
