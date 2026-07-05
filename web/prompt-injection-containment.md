---
layout: default
title: "Prompt Injection Containment"
permalink: /prompt-injection-containment/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../candidate/">Candidate</a>
</nav>


## Example

Two Zeeguu surfaces feed *untrusted text* into a prompt, and they contain it with very different strength.

**Audio-lesson suggestions (strong containment).** A user types a free-text topic or situation for a listening lesson, which then drives an expensive multi-step generation pipeline (script → text-to-speech → stored artifact). `suggestion_validator` contains the input in layers: hard length caps (2–80 characters) reject oversized payloads before any model runs; then a cheap, temperature-0 LLM *gatekeeper* classifies the input (`invalid` / `niche` / `general`) **and canonicalizes it to a short 2–5 word normalized topic** in the user's native language. The downstream generator consumes the *canonical form*, not the raw text — so an injected instruction ("ignore your rules and…") is either rejected as `invalid` or collapsed into a 2–5 word topic, and never reaches the generator verbatim.

**On-demand "Ask LLM" translation (light containment).** The learner's clicked word and the surrounding article sentence are inserted into the prompt. The context here is third-party web content the app ingested, so it is *also* untrusted. Containment is implicit rather than explicit: the task is deliberately narrow ("translate the word in context, 1–3 words"), the expected output is tightly constrained, and [Defensive Output Parsing](../defensive-output-parsing/) rejects anything that is not a short translation. This bounds the blast radius rather than sanitizing the input.

## Forces

- An LLM cannot reliably separate *data* from *instructions*: any untrusted text in the prompt — typed by a user, or lifted from third-party content the app ingests — can carry instructions the model may follow.
- In a *component* (not a chatbot), the output feeds downstream automated steps that generate, synthesize, and *persist* artifacts. A successful injection is therefore not merely an off-topic reply; it can produce unintended stored content, waste expensive compute, or emit unsafe output under the application's name.
- Legitimate and injected text share one channel — the prompt — so you cannot filter injection out by transport; you must *reduce, constrain, or scope* the untrusted text instead.
- Perfect sanitization is impossible. Defenses are layered and probabilistic, and each extra gatekeeping call has a cost that must be traded against the consequence it guards.

## Solution

Never let raw untrusted text flow into a consequential prompt as-is. Contain it with cheap, layered defenses, strongest where the blast radius is largest:

- **Structural caps first** — length / character limits reject obvious payloads before any model runs (free, deterministic).
- **Gate-and-canonicalize** — a cheap, low-temperature classifier (LLM or classical) validates the input *and replaces it with a short normalized canonical form*; downstream prompts consume the canonical form, not the original. Reducing untrusted free text to a 2–5 word token is itself a strong injection defense: there is almost no room left to smuggle instructions.
- **Narrow the task and constrain the output** — a prompt that can only emit a 1–3 word translation, validated by [Defensive Output Parsing](../defensive-output-parsing/), bounds what a successful injection achieves even without sanitizing the input.
- **Fail safe** — on validator error, degrade to the most restrictive behavior the feature can tolerate, never to "pass the raw text through."

Match containment strength to consequence: the audio pipeline (multi-step, persists artifacts, real cost) earns a dedicated gatekeeper call; a throwaway inline translation leans on scoping and output validation.

## Notes

- Composes with [Defensive Output Parsing](../defensive-output-parsing/) — constraining and validating the *output* is the second half of containment: limit what goes in *and* what can come out. It also composes with [LLM-Checking-LLM](../llm-checking-llm/): the gatekeeper is a checker specialized for safety rather than quality.
- **Honest gap:** the article-context vector is only *partially* contained. Article text is third-party and could carry injection; today's defense there is task-narrowing plus output constraint, not context sanitization. We flag this rather than claim full coverage.
- **Fail-open vs. fail-closed:** `suggestion_validator` deliberately *fails open* — on LLM error it lets the suggestion through with only basic sanitization, trading safety for availability on a low-stakes feature. A higher-stakes surface should fail *closed*. Making that choice explicit per feature is part of the pattern.

## Relationship to LLM Gateways

Some gateways offer prompt-injection / content guardrails (Portkey guardrails, LiteLLM hooks, dedicated screens such as Lakera or prompt-shield features) that can run a screening pass at the gateway. But the strongest containment here is not a generic screen — it is *domain canonicalization* (reduce the input to a 2–5 word topic in the user's language) and *task-narrowing*, both of which require the application's knowledge of what a legitimate input looks like. A gateway can add a screening layer; it cannot know that "a valid audio-lesson topic is a 2–5 word phrase" or "a valid translation is 1–3 words." As elsewhere (see *What Makes These Patterns LLM-Specific? → Relationship to LLM Gateways*): gateway = generic guardrail; pattern = domain-specific reduction and scoping.

## Status

Partly implemented: the audio-lesson suggestion validator is a full instance; translation relies on task-narrowing plus defensive parsing; the third-party article-context vector is only partially addressed. Included as a candidate to discuss the boundary with [Defensive Output Parsing](../defensive-output-parsing/) and [LLM-Checking-LLM](../llm-checking-llm/) — whether "contain untrusted input" and "validate untrusted output" are two halves of one pattern or two.

## Known Uses

- **[OWASP Top 10 for LLM Applications](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)** (LLM01: Prompt Injection) codifies the threat and lists mitigations matching this pattern's layers: constrain behavior, validate/constrain output, filter input/output, and segregate untrusted content from trusted prompts.
- **[Simon Willison's Dual-LLM pattern](https://simonwillison.net/2023/Apr/25/dual-llm-pattern/)** handles untrusted text only in a tool-less quarantined LLM while a controller substitutes variable tokens, so raw untrusted content never reaches the privileged LLM — a stronger sibling of our canonicalize-before-use step.
- **[NVIDIA NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/latest/getting-started/4-input-rails/README.html)** "input rails" screen user messages for jailbreak/injection before they reach the LLM.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../per-user-consumption-budget/">← Per-User Consumption Budget</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BPrompt+Injection+Containment%5D+&labels=feedback%2Ccandidate&body=%2A%2ARe%3A%2A%2A+Prompt+Injection+Containment%0A%2A%2ASection%3A%2A%2A+Candidate+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fprompt-injection-containment%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
