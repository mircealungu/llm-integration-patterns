# Hot-Path Result Caching

## Example

Multi-word expression (MWE) detection finds the phrases in an article that a learner might want translated as a unit (for example *kick the bucket*). It uses an LLM, gated by a cheap Stanza pass (see *Hybrid Classical+LLM Pipeline*), and the LLM call is the expensive part, so the analysis is worth caching: the detector keeps a 500-entry in-memory cache, so when multiple users read the same article, phrase analyses computed for the first reader are served instantly to the rest. Hit rates are highest for popular articles that many users read in the same window.

## Forces

Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

## Solution

Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

## Tradeoff

Memory overhead and cache invalidation complexity. Best suited for queries where staleness is acceptable and input space has natural clustering (many users reading same content).

## Tradeoff

- A variant of this caches the results in the DB not in-memory. We also have this in Zeeguu.
