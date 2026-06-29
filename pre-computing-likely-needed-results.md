---
layout: default
title: "Pre-Computing Likely-Needed Results"
permalink: /pre-computing-likely-needed-results/
---

[← All patterns](../)

**Example (from Zeeguu):** The system needs to verify that word/translation pairs obtained from Google Translate or Azure Translate APIs are correct before including them in vocabulary exercises — the system can afford to insert an imprecise translation while the reader is quickly trying to make sense of a text, but it cannot afford to have users repeatedly practice imprecise translations! A regular cron job identifies words users should study next and pre-computes LLM-based verification for the quality of their translation. 

**Forces:** LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

**Solution:** Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.

[← All patterns](../)
