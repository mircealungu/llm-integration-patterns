---
layout: default
title: "Limitations and Future Work"
permalink: /limitations-and-future-work/
---


[← All patterns](../#the-patterns)


The patterns in this catalogue have been extracted from a single production system, Zeeguu, in the language-learning domain. We have argued throughout that the underlying forces — per-token cost, multi-second latency, non-determinism, a rapidly shifting provider landscape, and general-purpose capability — are not specific to language learning, and that the patterns should therefore generalise to other interactive applications that surface LLM-generated text to end users. Whether this is borne out in practice is an empirical question we cannot fully answer from a single case study. The most direct way to validate or refute the catalogue is to gather complementary examples — and counter-examples — from practitioners working in other domains. A PLoP writers' workshop is one venue for exactly this kind of community refinement; mining open-source repositories for additional instances of these patterns (and patterns we missed) is a natural follow-up.

A second limitation is that the catalogue reports patterns we have found useful but does not yet quantify their impact systematically. Anecdotal cost and latency improvements are reported per pattern; a more rigorous deployment-level evaluation — measuring, for example, how much of Zeeguu's LLM bill is attributable to which patterns, or how much user-perceived latency [Multiplexed Dispatch](../multiplexed-dispatch/) removes — is future work.

Finally, we expect the catalogue to be incomplete. Several proto-patterns are listed in *Candidate Patterns*; others will likely surface only through engagement with practitioners working at different scales, in different domains, and with different LLM providers.



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this section](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLimitations+and+Future+Work%5D+&labels=feedback&body=%2A%2ARe%3A%2A%2A+Limitations+and+Future+Work%0A%2A%2ASection%3A%2A%2A+Limitations+and+Future+Work%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Flimitations-and-future-work%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
