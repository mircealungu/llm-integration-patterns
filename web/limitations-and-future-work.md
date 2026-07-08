---
layout: default
title: "Limitations and Future Work"
permalink: /limitations-and-future-work/
---


[← All patterns](../#the-patterns)


The patterns in this catalogue have been extracted from a single production system, Zeeguu, in the language-learning domain. We have argued throughout that the underlying forces (per-token cost, multi-second latency, non-determinism, a rapidly shifting provider landscape, and general-purpose capability) are not specific to language learning, and that the patterns should therefore generalise to other interactive applications that surface LLM-generated text to end users. Whether this is borne out in practice is an empirical question we cannot fully answer from a single case study. The most direct way to validate or refute the catalogue is to gather complementary examples (and counter-examples) from practitioners working in other domains. A PLoP writers' workshop is one venue for exactly this kind of community refinement; mining open-source repositories for additional instances of these patterns (and patterns we missed) is a natural follow-up.

A second limitation is that the catalogue reports patterns we have found useful but does not yet quantify their impact systematically. Anecdotal cost and latency improvements are reported per pattern; a more rigorous deployment-level evaluation (measuring, for example, how much of Zeeguu's LLM bill is attributable to which patterns, or how much user-perceived latency racing providers removes) is future work.

A further direction is to treat the catalogue as the seed of a *pattern language* rather than a flat list. The patterns are not independent: they compose (pre-computation feeds [Prompt Amortization](../prompt-amortization/); [LLM Output Provenance](../llm-output-provenance/) flags which artifacts [Soft Invalidation of LLM Artifacts](../soft-invalidation-of-llm-artifacts/) should retire) and they evolve over a system's lifetime (an LLM may begin as a [Rent, Then Build](../rent-then-build/) stand-in, hand off to a specialized tool, and remain as the [Escalate to the LLM](../escalate-to-the-llm/) fallback). Documenting these interactions, sequences, and tensions, so a designer can navigate from one pattern to the next, is a contribution beyond the individual patterns.

These choices are not made once. A system's pattern mix is actively revised as it scales and the provider landscape shifts: Zeeguu began by making single LLM calls and only recently added parallel, raced ones, and may later drop that approach or fold it together with per-user budgeting as usage grows. A longitudinal account of how and why a system's chosen patterns change over time would deepen the lifecycle dimension that this single-snapshot catalogue can only sketch.

Finally, we expect the catalogue to be incomplete: further patterns will likely surface only through engagement with practitioners working at different scales, in different domains, and with different LLM providers.


Some proto-patterns already in progress are collected under *Candidate Patterns*.



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this section](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLimitations+and+Future+Work%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+Limitations+and+Future+Work%0A%2A%2ASection%3A%2A%2A+Limitations+and+Future+Work%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Flimitations-and-future-work%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
