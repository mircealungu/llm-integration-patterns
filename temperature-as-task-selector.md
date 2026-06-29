---
layout: default
title: "Temperature as Task Selector"
permalink: /temperature-as-task-selector/
---

[← All patterns](../)

# Temperature as Task Selector


**Example (Zeeguu):** Translation validation uses temperature 0 for deterministic yes/no judgments. Audio lesson script generation uses temperature 0.8 to produce varied, natural-sounding dialogues. The same model serves both purposes with different configuration.

**Forces:** LLMs exhibit different behaviors at different temperature settings. Classification and validation tasks benefit from deterministic outputs (low temperature), while creative generation benefits from variety (higher temperature). Using a single temperature for all tasks either sacrifices reliability or creativity.

**Solution:** Systematically vary temperature based on task type. Use temperature 0–0.3 for tasks requiring consistency (validation, classification, structured extraction). Use temperature 0.7–1.0 for tasks requiring creativity (dialogue generation, example variety).

**Note:** This pattern acknowledges that a single LLM can behave as multiple "virtual components" depending on configuration — deterministic validator vs. creative generator.

[← All patterns](../)
