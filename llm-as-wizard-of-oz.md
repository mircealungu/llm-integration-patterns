---
layout: default
title: "LLM as Wizard of Oz"
permalink: /llm-as-wizard-of-oz/
---


<nav class="pattern-nav">
  <a class="nav-prev" href="../fail-fast-provider-chain/">← Fail-Fast Provider Chain</a>
  <a class="nav-all" href="../">All patterns</a>
  <a class="nav-next" href="../llm-output-provenance/">LLM Output Provenance →</a>
</nav>


**Example (Zeeguu):** Topic classification of articles is currently performed by pasting the abstract into an LLM. This works but is expensive. Once we are satisfied with the topic taxonomy and have accumulated enough labeled data, we will switch to a dedicated topic detection framework.

**Forces:** LLMs are general-purpose machines that can attempt almost any text-based task. Building dedicated, efficient solutions requires upfront investment and training data that may not yet exist.

**Solution:** Use the LLM to perform a task in production while building a more efficient replacement. The LLM serves as the "wizard behind the curtain": convincing to users, allowing early beta-testing and feedback, but intended to be temporary.

**Bootstrapping variant:** In a more subtle variant, the LLM *generates the training data for its own replacement.* For example, Zeeguu uses an LLM to estimate text difficulty levels. These LLM-generated difficulty labels are being accumulated as training data for a classical classifier that will eventually take over the task.

**Note:** This pattern has a lifecycle relationship with [Escalate to the LLM](../escalate-to-the-llm/): a system may start with the LLM as primary (Wizard of Oz), migrate to a specialized tool as primary, and then keep the LLM as the escalation path, completing a full cycle from LLM-first to LLM-on-demand.



---
[← Fail-Fast Provider Chain](../fail-fast-provider-chain/) &nbsp;·&nbsp; [All patterns](../) &nbsp;·&nbsp; [LLM Output Provenance →](../llm-output-provenance/) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM+as+Wizard+of+Oz%5D+&labels=feedback%2Clifecycle-management&body=%2A%2ARe%3A%2A%2A+LLM+as+Wizard+of+Oz%0A%2A%2ASection%3A%2A%2A+Lifecycle+Management+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fllm-as-wizard-of-oz%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
