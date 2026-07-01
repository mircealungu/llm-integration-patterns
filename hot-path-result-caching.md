---
layout: default
title: "Hot-Path Result Caching"
subtitle: "Latency and Availability Patterns"
subtitle_url: "../#latency-and-availability-patterns"
permalink: /hot-path-result-caching/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a>
</nav>


**Example (Zeeguu):** MWE detection maintains a 500-entry LRU cache. When multiple users read the same article, phrase analyses computed for the first user are served instantly to subsequent users. Cache hit rates of 40-60% are typical for popular articles.

**Forces:** Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

**Solution:** Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

**Tradeoff**: Memory overhead and cache invalidation complexity. Best suited for queries where staleness is acceptable and input space has natural clustering (many users reading same content).

**Tradeoff:** 
- A variant of this caches the results in the DB not in-memory. We also have this in Zeeguu.



---
[← Pre-Computing Likely-Needed Results](../pre-computing-likely-needed-results/){:.nav-prev} &nbsp;·&nbsp; [All patterns](../#the-patterns) &nbsp;·&nbsp; [Multiplexed Dispatch →](../multiplexed-dispatch/){:.nav-next}

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BHot-Path+Result+Caching%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Hot-Path+Result+Caching%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fhot-path-result-caching%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
