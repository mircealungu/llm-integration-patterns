# Hot-Path Result Caching

## Context

The same or near-identical LLM request recurs within a short window (many users hitting the same content, or one user re-requesting) but *which* requests recur is unpredictable, so they cannot be precomputed ahead of time.

## Example

Any expensive LLM call whose inputs recur can be cached in memory, keyed on those inputs, so every repeat after the first is near-free. Zeeguu does this for [Multi-word expression](../zeeguu/#multi-word-expressions) (MWE) detection, which finds the phrases in an article a learner might want translated as a unit (for example *break the ice*). It runs an LLM, gated by a cheap [Stanza](https://arxiv.org/abs/2003.07082) (an NLP library) pass (see *Hybrid Classical+LLM Pipeline*), and the LLM call is the expensive part. The detector keeps a 500-entry in-memory cache keyed on the article's sentences (dropping its oldest entries when full), so when many users read the same article, the analysis computed for the first reader is served instantly to the rest. Hit rates are highest for popular articles read by many learners in the same window. Only LLM results are cached: when the LLM is unavailable and the detector falls back to Stanza, those weaker results are deliberately not stored.

## Problem

How can the same expensive LLM call be avoided when it recurs unpredictably within a short window?

## Forces

Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

## Solution

Maintain an in-memory cache for recent LLM results, keyed on the call's inputs. Bound it by capacity and evict the oldest entries when full (the example above caps the cache at 500 entries). No time-based expiry is needed where the cached result is a pure function of its inputs.

## Consequences

- **Repeats are near-free.** A hit within the window returns from memory at ~zero cost and latency; hit rate is highest for popular content many users read in the same window.
- **Memory is the price, and it only pays where inputs repeat.** The cache costs memory and returns nothing on a wide, flat input space; it fits where requests cluster on the same content, so the same calls actually recur.
- **Variant: persist it.** A DB-backed cache outlives process memory and survives restarts (Zeeguu uses this too), trading a little speed for durability.

## Known Uses

- **Walmart**: Walmart's chief software architect describes a production *semantic* cache (vector-similarity, not exact match) for e-commerce search, reporting a hit rate "closer to 50%" on tail queries. *(Reported in a [vendor writeup of the talk](https://portkey.ai/blog/transforming-e-commerce-search-with-generative-ai-insights-from-walmarts-journey/); the claims are attributed to Walmart on the record, but the source is secondary.)*
- *Honest note.* First-party write-ups of *reactive* LLM-output caching are scarce; most published examples (Yelp, Instacart) are *anticipatory precomputation* of head queries (see *Anticipatory Precomputation*) rather than caching on a miss.

## Notes

- *Enablers (not instances).* Result caching is common enough to be productized: dedicated LLM caches ([GPTCache](https://aclanthology.org/2023.nlposs-1.24/), exact + semantic) and gateway caches ([Helicone](https://docs.helicone.ai/features/advanced-usage/caching), [Portkey](https://portkey.ai/docs/product/ai-gateway/cache-simple-and-semantic), [LangChain](https://python.langchain.com/docs/integrations/llm_caching/)).
