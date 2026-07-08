---
layout: default
title: "Managing Change Over Time"
permalink: /managing-change-over-time/
---


[← All patterns](../#the-patterns)


An LLM integration is not static: prompts and models improve, vendors retire dated snapshots on their own schedule, and the LLM's own role in a feature shifts as the system matures. The patterns here manage that change: stamping stored output with the model and prompt that made it so the stale can be found and regenerated, retiring stale artifacts without breaking the past, keeping every model identifier in one place so a deprecation is a one-line edit, and treating the LLM as a temporary stand-in for a cheaper component still to be built. The unifying force is a fast-moving, vendor-controlled substrate sitting under long-lived data.

- [LLM Output Provenance](../llm-output-provenance/) ★
- [Soft Invalidation of LLM Artifacts](../soft-invalidation-of-llm-artifacts/) ★
- [Rent, Then Build](../rent-then-build/) ★
- [Centralized Model Selection](../centralized-model-selection/)



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this category](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BManaging+Change+Over+Time%5D+&labels=feedback%2Cmanaging-change-over-time&body=%2A%2ARe%3A%2A%2A+Managing+Change+Over+Time%0A%2A%2ASection%3A%2A%2A+Managing+Change+Over+Time%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fmanaging-change-over-time%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
