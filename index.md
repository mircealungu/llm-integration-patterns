---
layout: default
title: "Architectural Patterns for Integrating LLMs into User-Facing Applications"
permalink: /
---


# Architectural Patterns for Integrating LLMs into User-Facing Learning Software


### What is this?

A living catalogue of recurring patterns I keep running into when building software with and around large language models — the small, reusable shapes of solution that show up again and again across agents, tools, prompts, and evaluation.

It's a working paper: a draft I'm developing in the open and revising as the ideas (and the tools) mature. Feedback is very welcome.

*Status: working draft, June 2026*

### The Idea

Large Language Models are increasingly being integrated into existing user-facing interactive applications — not as standalone chatbots, but as components working behind the scenes to improve the user experience. While there is growing literature on building LLM-native products (chatbots, agents, RAG systems) and on using LLMs for code generation, there is surprisingly little guidance on the **software engineering challenges of integrating LLMs as components into existing interactive applications** where real users expect fast, reliable, and trustworthy responses.

LLMs have a unique combination of properties that create novel architectural forces: 

- they are expensive (per-token pricing),   
- slow (high latency),   
- non-deterministic (same input can yield different outputs, although this can be to a certain degree controlled with the temperature setting),  
- rapidly evolving  (new models released every few months and old ones regularly deprecated),  
- imprecise (they make mistakes), and   
- general-purpose (they can attempt almost any task described as text). 

These properties demand specific engineering strategies.

Over the past year, we have been integrating LLMs into [Zeeguu](https://zeeguu.unibe.ch/) — an open-source platform for personalized language learning that helps users learn foreign languages by reading authentic online content. Through this work, we have identified a set of recurring architectural patterns for LLM integration. We believe these patterns are general and applicable beyond our specific domain.

### Main Case Study: Zeeguu

Zeeguu is an open-source language learning platform built around the idea that learners benefit most from engaging with authentic content in their target language. Rather than relying on artificial textbook exercises, Zeeguu helps users find real articles — news, blog posts, and other web content — tailored to both 1\) their *level* and 2\) their *interests*.

The platform recommends articles in the learner's target language based on their proficiency and reading preferences, making it **easy to find material that is both interesting and appropriately challenging**. If a text is personally compelling but too difficult, Zeeguu simplifies it to the learner's level using LLMs. 

When users encounter unfamiliar words or phrases while reading, they can get translations on the fly powered by (contextual) Google Translate, so the reading experience remains fluid and uninterrupted. One alternative is provided by a state-of-the-art LLM, offering a more contextually nuanced option. 

Every translation a user requests is logged by the system, which over time builds a **detailed model of the learner's vocabulary knowledge** — tracking which words they know, which ones they struggle with, and how well they've retained previously encountered vocabulary.

Based on this evolving learner model, Zeeguu **generates interactive vocabulary exercises and audio lessons** that focus on the words that matter most for each individual learner, rather than following a generic curriculum. The exercises use the context in which the word was originally encountered, based on the assumption that if the original text was interesting to the learner, then examples from it will also be interesting. 

In essence, Zeeguu unifies reading, translation, learner modeling, and practice into a coherent pipeline, with the learner's own reading interests as the primary driver. 

Zeeguu currently serves over 300 monthly active users, with peaks exceeding 400 during the academic year[^1].

Open question:

- Do these patterns apply beyond the language learning domain of Zeeguu. Do other kinds of applications show to users LLM generated text in a similar manner? 

[^1]: Monthly active users are defined as users with any learning activity (exercises, reading, browsing, audio lessons, or translations) in a given month. Live statistics are available at: https://api.zeeguu.org/stats/monthly_active_users

## The Patterns

### Cost Optimization Patterns
- [Prompt Amortization](prompt-amortization/)
- [LLM as Fallback](llm-as-fallback/)

### Latency / Availability Patterns
- [Pre-Computing Likely-Needed Results](pre-computing-likely-needed-results/)
- [Hot-Path Result Caching](hot-path-result-caching/)
- [Multiplexed Dispatch](multiplexed-dispatch/)
- [Fail-Fast Provider Chain](fail-fast-provider-chain/)

### Lifecycle Management Patterns
- [LLM as Wizard of Oz](llm-as-wizard-of-oz/)

### Data Management Patterns
- [LLM Output Provenance](llm-output-provenance/)

### Quality Assurance Patterns
- [LLM-Checking-LLM](llm-checking-llm/)
- [LLM Content Validation Tracking](llm-content-validation-tracking/)

### Hybrid Pipeline Patterns
- [Hybrid Classical+LLM Pipeline](hybrid-classical-llm-pipeline/)

### Possible Other Patterns
- [Temperature as Task Selector](temperature-as-task-selector/)
- [Soft Invalidation of LLM Artifacts](soft-invalidation-of-llm-artifacts/)
- [Deterministic Postprocessing](deterministic-postprocessing/)

## More

- [Related Work](related-work/)
- [What Makes These Patterns LLM-Specific?](what-makes-these-patterns-llm-specific/)
- [Possible Paper Contributions](possible-paper-contributions/)
