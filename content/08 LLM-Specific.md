# What Makes These Patterns LLM-Specific?

Some of these patterns echo general distributed systems wisdom: batching (in *Prompt Amortization*), fallback (in *Escalate to the LLM*), redundant dispatch (in the parallel translation providers). What makes them distinctly relevant to LLM integration is that each draws on forces that are properties of the LLM rather than of any domain:

* **Cost structure**: per-token pricing with high fixed prompt overhead, unlike flat-rate API calls (drives *Prompt Amortization*, *Escalate to the LLM*, *Anticipatory Precomputation*).
* **Non-determinism**: the same input can yield a different, or malformed, output, so correctness must be enforced around the model (drives *Defensive Output Parsing*, *LLM-Checking-LLM*, *LLM Content Validation Tracking*).
* **Asymmetry between generation and verification**: checking one property is easier than producing the whole output (drives *LLM-Checking-LLM*).
* **General-purpose capability**: the same component can serve as prototype, primary, or fallback (drives *Rent, Then Build* and *Escalate to the LLM*).
* **A rapidly evolving, vendor-controlled substrate**: models and prompts improve and are deprecated on the vendor's schedule, underneath long-lived data (drives *LLM Output Provenance* and *Soft Invalidation of LLM Artifacts*).
* **Quality-cost-latency tradeoff space**: uniquely wide compared to traditional APIs, and what the efficiency patterns navigate.

<!-- paper-skip -->

## Relationship to LLM Gateways

Several of these patterns (*Fail-Fast Provider Chain*, *Centralized Model Selection*, and hot-path caching) are being commoditized into LLM-gateway infrastructure (LiteLLM, Portkey, Cloudflare AI Gateway). This does not invalidate them as patterns; it relocates their *implementation* from application code into shared infrastructure. A pattern documents a recurring solution whether it is hand-rolled or shipped by a gateway, and knowing the pattern is precisely what lets one judge whether a given gateway implements it well (e.g. most gateways do *not* provide *Multiplexed Dispatch* with alternative-caching). Connection pooling remained a pattern long after every ORM started shipping one.

The recurring shape across all of these is that the gateway supplies a *mechanism* while the pattern owns the *intent, the domain join, and the decision the mechanism drives*. This is sharpest in *Per-User Consumption Budget*, where the gateway can throttle and cap but only the application knows which resource to bound and what the user should get when the budget is exhausted.

<!-- /paper-skip -->
