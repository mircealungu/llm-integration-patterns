# Architectural Patterns for Integrating LLMs into User-Facing Applications

### What is this?

A living catalogue of recurring patterns I keep running into when building software with and around large language models, the small, reusable shapes of solution that show up again and again across agents, tools, prompts, and evaluation.

It's a working paper: a draft I'm developing in the open and revising as the ideas (and the tools) mature. Feedback is very welcome.

*Status: working draft, June 2026*

### The Idea

Large Language Models are increasingly being integrated into existing user-facing interactive applications, not as standalone chatbots, but as components working behind the scenes to improve the user experience. While there is growing literature on building LLM-native products (chatbots, agents, RAG systems) and on using LLMs for code generation, there is surprisingly little guidance on the **software engineering challenges of integrating LLMs as components into existing interactive applications** where real users expect fast, reliable, and trustworthy responses.

LLMs have a unique combination of properties that create novel architectural forces: 

- they are expensive (per-token pricing),   
- slow (high latency),   
- non-deterministic (same input can yield different outputs, although this can be to a certain degree controlled with the temperature setting),  
- rapidly evolving  (new models released every few months and old ones regularly deprecated),  
- imprecise (they make mistakes), and   
- general-purpose (they can attempt almost any task described as text). 

These properties demand specific engineering strategies.

Over the past year, we have been integrating LLMs into [Zeeguu](https://zeeguu.unibe.ch/), an open-source platform for personalized language learning that helps users learn foreign languages by reading authentic online content. Through this work, we have identified a set of recurring architectural patterns for LLM integration. We believe these patterns are general and applicable beyond our specific domain.
