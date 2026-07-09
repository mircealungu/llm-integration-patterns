# Limitations and Future Work

The patterns in this catalogue have been extracted from a single production system, Zeeguu, in the language-learning domain. We have argued throughout that these forces arise from the LLM's own properties (per-token cost, multi-second latency, non-determinism, imprecision, a rapidly shifting provider landscape, and general-purpose capability) meeting the demands of a live application, neither of which is specific to language learning, and that the patterns should therefore generalise to other interactive applications that surface LLM-generated text to end users. Whether this is borne out in practice is an empirical question we cannot fully answer from a single case study. The most direct way to validate or refute the catalogue is to gather complementary examples (and counter-examples) from practitioners working in other domains. A PLoP writers' workshop is one venue for exactly this kind of community refinement; mining open-source repositories for additional instances of these patterns (and patterns we missed) is a natural follow-up.

A second limitation is that the catalogue reports patterns we have found useful but does not yet quantify their impact systematically. Cost and latency improvements are reported informally for some patterns; a more rigorous deployment-level evaluation (measuring, for example, how much of Zeeguu's LLM bill is attributable to which patterns, or how much user-perceived latency racing providers removes) is future work.

A further direction is to treat the catalogue as the seed of a *pattern language* rather than a flat list. The patterns are not independent: they compose (pre-computation feeds *Prompt Amortization*; *LLM Output Provenance* flags which artifacts *Soft Invalidation of LLM Artifacts* should retire) and they evolve over a system's lifetime (an LLM may begin as a *Rent, Then Build* stand-in, hand off to a specialized tool, and remain as the *Escalate to the LLM* fallback). Documenting these interactions, sequences, and tensions, so a designer can navigate from one pattern to the next, is a contribution beyond the individual patterns.

These choices are not made once. A system's pattern mix is actively revised as it scales and the provider landscape shifts: Zeeguu began by making single LLM calls and only recently added parallel, raced ones, and may later drop that approach or fold it together with per-user budgeting as usage grows. A longitudinal account of how and why a system's chosen patterns change over time would deepen the lifecycle dimension that this single-snapshot catalogue can only sketch.

Finally, we expect the catalogue to be incomplete: further patterns will likely surface only through engagement with practitioners working at different scales, in different domains, and with different LLM providers.

<!-- paper-skip -->
Some proto-patterns already in progress are collected under *Candidate Patterns*.
<!-- /paper-skip -->
