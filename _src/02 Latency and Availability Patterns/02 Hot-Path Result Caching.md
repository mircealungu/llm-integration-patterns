# Hot-Path Result Caching

**Example (Zeeguu):** MWE detection maintains a 500-entry LRU cache. When multiple users read the same article, phrase analyses computed for the first user are served instantly to subsequent users. Cache hit rates of 40-60% are typical for popular articles.

**Forces:** Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

**Solution:** Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

**Tradeoff**: Memory overhead and cache invalidation complexity. Best suited for queries where staleness is acceptable and input space has natural clustering (many users reading same content).

**Tradeoff:** 
- A variant of this caches the results in the DB not in-memory. We also have this in Zeeguu.
