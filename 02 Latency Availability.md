# Latency / Availability Patterns

## Pre-Computing Likely-Needed Results

**Example (from Zeeguu):** The system needs to verify that word/translation pairs obtained from Google Translate or Azure Translate APIs are correct before including them in vocabulary exercises — the system can afford to insert an imprecise translation while the reader is quickly trying to make sense of a text, but it cannot afford to have users repeatedly practice imprecise translations! A regular cron job identifies words users should study next and pre-computes LLM-based verification for the quality of their translation. 

**Forces:** LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

**Solution:** Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs. 

## Hot-Path Result Caching

**Example (Zeeguu):** MWE detection maintains a 500-entry LRU cache. When multiple users read the same article, phrase analyses computed for the first user are served instantly to subsequent users. Cache hit rates of 40-60% are typical for popular articles.

**Forces:** Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

**Solution:** Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

**Tradeoff**: Memory overhead and cache invalidation complexity. Best suited for queries where staleness is acceptable and input space has natural clustering (many users reading same content).

**Tradeoff:** 
- A variant of this caches the results in the DB not in-memory. We also have this in Zeeguu. 

## Multiplexed Dispatch

**Example (Zeeguu):** Real-time translations are dispatched to multiple translation providers in parallel. The first response is used, and the rest are saved for when the user asks for alternatives. 

**Forces:** Multiple LLM providers offer similar capabilities but with varying latency. When speed matters for user experience, relying on a single provider creates a bottleneck.

**Solution:** Dispatch the same request to multiple providers simultaneously and use the first response that arrives. Track the top two fastest providers, and always dispatch to these. 

An alternative to this is **live retrieval**: when the user encounters a translation that they are not sure of, they ask for alternatives, the UI presents the results that are cached, but also asks for alternatives and displays a UI interface that highlights the fact that some of the results are still streaming in.

**Tradeoff:** Increased cost (you pay for redundant calls) in exchange for reduced latency.

## Fail-Fast Provider Chain

**Example** (Zeeguu): The app uses a unified LLM service proxy which tries Anthropic first; on any error (timeout, rate limit, API error), it immediately switches to DeepSeek without retry. This keeps worst-case latency bounded while maintaining availability.    

**Forces**: LLM providers experience outages, rate limits, and latency spikes. Retry logic increases latency and may still fail. Different providers offer similar capabilities at different price/performance points.    

**Solution**: Configure a chain of LLM providers with no retries. On any failure, immediately fall back to the next provider in the chain. Prioritize speed over exhausting retry budgets.    

**Note**: This differs from the *LLM as Fallback* pattern in that all components in the chain are LLMs offering equivalent capabilities — the fallback is for reliability, not for capability escalation.
