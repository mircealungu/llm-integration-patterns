# Hot-Path Result Caching

**Example (Zeeguu):** Multi-word expression (MWE) detection finds the phrases in an article that a learner might want translated as a unit (for example *kick the bucket*). Because it runs an LLM over candidate phrases (see *Hybrid Classical+LLM Pipeline*), the results are worth caching: the detector maintains a 500-entry LRU cache, so when multiple users read the same article, phrase analyses computed for the first reader are served instantly to the rest. Cache hit rates of 40-60% are typical for popular articles.

**Forces:** Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

**Solution:** Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

**Tradeoff**: Memory overhead and cache invalidation complexity. Best suited for queries where staleness is acceptable and input space has natural clustering (many users reading same content).

**Tradeoff:** 
- A variant of this caches the results in the DB not in-memory. We also have this in Zeeguu.
