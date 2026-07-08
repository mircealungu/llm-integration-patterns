---
layout: default
title: "Lifecycle Management"
permalink: /lifecycle-management/
---


[← All patterns](../#the-patterns)


An LLM integration is not static: the models behind it are retired and re-priced on the vendor's schedule, and the role the LLM plays in a feature changes as the system matures. These patterns manage that evolution over time. [Rent, Then Build](../rent-then-build/) treats the LLM as a temporary stand-in, shipping a feature on rented general capability now while a cheaper, dedicated replacement is built. [Centralized Model Selection](../centralized-model-selection/) keeps every model identifier in one place, so a vendor retiring a dated snapshot is a one-line change rather than a hunt across the codebase.

- [Rent, Then Build](../rent-then-build/)
- [Centralized Model Selection](../centralized-model-selection/)



---
[← All patterns](../#the-patterns)

[💬 Open an issue about this category](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLifecycle+Management%5D+&labels=feedback%2Clifecycle-management&body=%2A%2ARe%3A%2A%2A+Lifecycle+Management%0A%2A%2ASection%3A%2A%2A+Lifecycle+Management%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Flifecycle-management%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
