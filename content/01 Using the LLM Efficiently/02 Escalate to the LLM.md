# Escalate to the LLM

## Context

A feature can be produced two ways: a cheap, fast specialized tool (a translation API, a classical classifier) that is adequate for the common case, and a slower, costlier LLM that does better on the hard cases. Crucially, the cheap tool's shortfalls are *observable*: it either errors, or the user visibly rejects the result.

## Example

In Zeeguu, translation APIs (from Google, Azure, and DeepL) serve as the primary translation engines. When a user indicates the translation is inadequate (by choosing *Ask an AI* from the alternatives menu), the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed. 

![[escalate-to-the-llm.png|220]]
*In Zeeguu, the inline [translation](../zeeguu/#translation) is the primary path; when the user wants a better rendering they escalate to an LLM on demand via the "[Ask an AI](../zeeguu/#translation)" option.*

## Problem

LLM quality is only worth its cost on the minority of requests the cheap tool handles poorly, and those cannot be told apart up front. How can the LLM be spent *only* where it pays off?

## Forces

- **Quality on the hard cases.** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than an LLM for well-defined tasks, but on a minority of inputs they fail or fall short, and there the LLM tends to do better. *(pushes toward escalating)*
- **Cost, latency, and usability.** Each escalation adds the LLM's cost and, because it runs after the cheap path, doubles the wait for that request; when the trigger is a user signal, it also costs UI surface and puts the routing burden on the user. *(pushes toward escalating rarely, and automatically where possible)*
- **The hard cases cannot be told apart up front.** The system cannot know which inputs the cheap tool will handle poorly before running it, so escalation must fire on an observable signal: the tool erroring, or the user rejecting the result.

## Solution

Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction. The LLM receives the original input, and (where it helps) the specialized tool's output and the user's feedback alongside it, so the escalation refines rather than restarts.

## Consequences

- **Cheap in the common case.** The LLM runs only on failure or dissatisfaction, so the vast majority of requests never incur its cost or latency.
- **User-triggered escalation costs usability.** Unless it fires automatically on a detectable failure, the user must be given, and must notice and use, a way to signal dissatisfaction: extra UI surface, and the routing burden falls on them.
- **A miss doubles the wait.** When escalation happens the user has already waited for the cheap result first, so time-to-answer for those cases is the sum of both.

## Known Uses

**[FrugalGPT](https://arxiv.org/abs/2305.05176)** (Chen, Zaharia & Zou, 2023) escalates when a scorer rejects the cheap answer, and **[RouteLLM](https://arxiv.org/abs/2406.18665)** (Ong et al., 2024) trains a confidence router that sends only the hard queries to the strong model. Both decide automatically from the model's own confidence, the *model cascade* variant of escalation discussed in the Notes below. The *external*-signal trigger this pattern centers on (the primary tool erroring, or the user rejecting the result) is less documented; Zeeguu is our instance of it.


## Notes

- *Applies broadly.* Beyond translation: topic classification, named entity recognition, or any task where a cheaper tool handles the common case and the LLM handles the long tail.
- *Distinct from Hybrid Classical+LLM Pipeline.* There a classical stage runs on every input as a recall gate and the LLM runs only on what it flags; here the cheap tool is the whole answer in the common case, and the LLM is reached only when it errors or the user rejects the result.
- *Escalation, not fallback.* Unlike a reliability fallback (where the secondary is an equal-or-lesser backup invoked when the primary fails), here the secondary is **more capable and more expensive**, invoked when the primary is not good enough. The movement is *up* in quality and cost, not *down* into degraded mode. That is why we name it escalation.
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
