# Architectural Patterns for Integrating LLMs into User-Facing Applications

<!-- paper-skip -->

*Status: working draft, Jul 2026*
*See also: the [PDF version](/paper.pdf), a selection of these patterns submitted to PLoP 2026.*

### What is this?

A living catalogue of the recurring patterns that come up when integrating LLMs into real, user-facing software, grounded in the Zeeguu language-learning platform and developed in the open as a working paper. Contributions are welcome: an **instance** (a note that a pattern also appears in another system) or a **case study** (a rich example from a new domain, which earns its own page alongside Zeeguu). Contributors receive named credit.


<!-- /paper-skip -->

### The Idea

While there is growing literature on building LLM-native products such as chatbots, agents, and retrieval-augmented generation (RAG) pipelines, and on using LLMs for code generation, there is surprisingly little guidance on the **software engineering challenges of integrating LLMs as components into existing interactive applications** where real users expect fast, reliable, and trustworthy responses.

We expect this integration to become the common case: over time, more and more existing user-facing applications will adopt LLMs not as standalone chatbots but as components working behind the scenes to improve the user experience. This is why we present a set of patterns that highlight the challenges and opportunities such integrations raise. 

Indeed, LLMs have a unique combination of properties that create novel architectural forces: 

- they are expensive (per-token pricing),   
- slow (high latency),   
- non-deterministic (same input can yield different outputs),  
- rapidly evolving (new models released every few months and old ones regularly deprecated),  
- imprecise (they make mistakes), and   
- general-purpose (they can attempt almost any task described as text). 

These properties demand specific engineering strategies, and they recur as the forces each pattern must balance.

Over the past year, we have been integrating LLMs into [Zeeguu](https://zeeguu.org), an open-source platform for personalized language learning that helps users learn foreign languages by reading authentic online content (real articles, not textbook exercises). Through this work, we have identified a set of recurring architectural patterns for LLM integration. Because these forces are properties of the LLM itself rather than of language learning, we expect the patterns to generalise beyond our specific domain.

Each pattern that follows is presented in the same format: context, example, problem, forces, solution, consequences, known uses, and notes.
