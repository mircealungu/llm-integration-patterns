# Escalate to the LLM

## Context

A feature can be produced two ways: a cheap, fast specialized tool (a translation API, a classical classifier) that is adequate for the common case, and a slower, costlier LLM that does better on the hard cases. Crucially, the cheap tool's shortfalls are *observable*: it either errors, or the user visibly rejects the result.

## Example

In Zeeguu, translation APIs (from Google, Azure, and DeepL) serve as the primary translation engines. When a user indicates the translation is inadequate (by choosing *Ask AI* from the alternatives menu), the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed. 

![[escalate-to-the-llm.png|220]]
*In Zeeguu, the inline Google translation is the primary path; when the user wants a better rendering they escalate to an LLM on demand via the "[Ask AI](../zeeguu/#translation)" option.*

## Problem

LLM quality is only worth its cost on the minority of requests the cheap tool handles poorly, and those cannot be told apart up front. How can the LLM be spent *only* where it pays off?

## Forces

Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than LLMs for well-defined tasks, but they sometimes fail or produce insufficiently satisfactory results.

## Solution

Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction. The LLM receives the original input, and (where it helps) the specialized tool's output and the user's feedback alongside it, so the escalation refines rather than restarts.

## Consequences

- **Cheap in the common case.** The LLM runs only on failure or dissatisfaction, so the vast majority of requests never incur its cost or latency.
- **User-triggered escalation costs usability.** Unless it fires automatically on a detectable failure, the user must be given, and must notice and use, a way to signal dissatisfaction: extra UI surface, and the routing burden falls on them.
- **A miss doubles the wait.** When escalation happens the user has already waited for the cheap result first, so time-to-answer for those cases is the sum of both.

## Known Uses

- **[FrugalGPT](https://arxiv.org/abs/2305.05176)** (Chen, Zaharia & Zou, 2023) queries cheaper models first and escalates to more capable, expensive ones only when a scorer rejects the cheap answer.
- **[RouteLLM](https://arxiv.org/abs/2406.18665)** (Ong et al., 2024) trains a router that sends easy queries to a weak/cheap model and escalates only hard ones to the strong model; shipped as an open-source framework.
- These are the *model-cascade* cousins of the pattern (automatic, confidence-triggered) whereas Zeeguu's trigger is a failure of the cheaper *non-LLM* tool or explicit user dissatisfaction.

## Notes

- *Applies broadly.* Beyond translation: topic classification, named entity recognition, or any task where a cheaper tool handles the common case and the LLM handles the long tail.
- *Escalation, not fallback.* Unlike a reliability fallback (where the secondary is an equal-or-lesser backup invoked when the primary fails; see *Fail-Fast Provider Chain*), here the secondary is **more capable and more expensive**, invoked when the primary is not good enough. The movement is *up* in quality and cost, not *down* into degraded mode. That is why we name it escalation.
- *Relationship to the model cascade.* This is the human-/failure-triggered cousin of the **model cascade** in ML serving, where a cheap model runs first and a confidence threshold routes hard inputs to a larger model. The shared shape is *cheap tier first, expensive tier on demand*; the difference is the trigger. A cascade escalates automatically on the model's own low confidence, whereas this pattern escalates on external signals: the primary tool erroring, or the user explicitly declaring the result inadequate. A confidence-based cascade is thus one possible escalation policy; user dissatisfaction is another, and the two can be combined.

> [!draft]- Notes after the focus group
> - name? why does the user have to know the LLM?
> - just ask: "explain"
> - user should not even ask (Uwe)
> - escalate to more powerful
> - why do we even do news? you could have 1k articles about …
> - premium version — only shows news articles
> - free users only get what the paying users get
> - which patterns still stand if you replace LLMs with expensive components?
