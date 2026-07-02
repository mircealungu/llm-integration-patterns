---
layout: default
title: "Pre-Computing Likely-Needed Results"
permalink: /pre-computing-likely-needed-results/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../#latency-and-availability">Latency and Availability</a>
</nav>


**Example (from Zeeguu):** 

When a learner reads a text and asks for a translation, the most important thing is to return a good-enough translation **fast**. The system can afford an imprecise translation while the reader is quickly making sense of a text, but it cannot afford to have learners repeatedly *practice* an imprecise one.

The vocabulary exercises are built from the words a learner has looked up, so those pairs (from Google or Azure Translate) must be verified before they enter an exercise. Verifying with an LLM is too slow to run at the moment a learner opens a session. So a regular cron job looks ahead: it identifies the words a learner is due to study next and pre-computes the LLM verification, so that when the session starts the words are already vetted and ready, with no LLM call on the critical path.

**An even costlier instance: audio lessons.** Generating a personalized audio lesson is more expensive again: an LLM writes the lesson script, then text-to-speech synthesizes the audio, several seconds of work no learner should wait through. A nightly job pre-computes the next lessons for recently active learners (prioritized by how recently they practiced), on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. 

**Forces:** LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real-time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

**Solution:** Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../escalate-to-the-llm/">← Escalate to the LLM</a><a class="nav-next" href="../hot-path-result-caching/">Hot-Path Result Caching →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BPre-Computing+Likely-Needed+Results%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Pre-Computing+Likely-Needed+Results%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fpre-computing-likely-needed-results%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
