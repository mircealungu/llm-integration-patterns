---
layout: default
title: "Pre-Computing Likely-Needed Results"
permalink: /pre-computing-likely-needed-results/
---


<nav class="pattern-nav">
  <a class="nav-prev" href="../escalate-to-the-llm/">← Escalate to the LLM</a>
  <a class="nav-all" href="../">All patterns</a>
  <a class="nav-next" href="../hot-path-result-caching/">Hot-Path Result Caching →</a>
</nav>


**Example (from Zeeguu):** The system needs to verify that word/translation pairs obtained from Google Translate or Azure Translate APIs are correct before including them in vocabulary exercises: the system can afford to insert an imprecise translation while the reader is quickly trying to make sense of a text, but it cannot afford to have users repeatedly practice imprecise translations! A regular cron job identifies words users should study next and pre-computes LLM-based verification for the quality of their translation. 

**Forces:** LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

**Solution:** Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.



---
[← Escalate to the LLM](../escalate-to-the-llm/) &nbsp;·&nbsp; [All patterns](../) &nbsp;·&nbsp; [Hot-Path Result Caching →](../hot-path-result-caching/) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BPre-Computing+Likely-Needed+Results%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Pre-Computing+Likely-Needed+Results%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fpre-computing-likely-needed-results%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
