---
layout: default
title: "Quality Assurance"
permalink: /quality-assurance/
---


[← All patterns](../#the-patterns)


LLMs are imprecise: they make mistakes, and their output is only probabilistically well-formed. These patterns guard the boundary between that output and the code, data, and users that expect it to be correct. [Hybrid Classical+LLM Pipeline](../hybrid-classical-llm-pipeline/) lets a cheap classical tool gate the LLM, running it only where its judgment is actually needed. [LLM-Checking-LLM](../llm-checking-llm/) catches errors with a second, narrower verification call. [Defensive Output Parsing](../defensive-output-parsing/) refuses to trust the shape of a response, parsing in layers and degrading gracefully rather than crashing on a malformed one. [Deterministic Postprocessing](../deterministic-postprocessing/) fixes stable, judgment-free defects in code rather than in the prompt. [LLM Content Validation Tracking](../llm-content-validation-tracking/) records how far each stored artifact has been trusted, so consumers can gate on it. [Targeted User Feedback](../targeted-user-feedback/) closes the loop, letting users flag the errors that slip through, anchored to the exact place they occur.

- [LLM-Checking-LLM](../llm-checking-llm/)
- [LLM Content Validation Tracking](../llm-content-validation-tracking/)
- [Hybrid Classical+LLM Pipeline](../hybrid-classical-llm-pipeline/)
- [Defensive Output Parsing](../defensive-output-parsing/)
- [Deterministic Postprocessing](../deterministic-postprocessing/)
- [Targeted User Feedback](../targeted-user-feedback/)



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this category](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BQuality+Assurance%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+Quality+Assurance%0A%2A%2ASection%3A%2A%2A+Quality+Assurance%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fquality-assurance%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
