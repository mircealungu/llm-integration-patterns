---
layout: default
title: "Targeted User Feedback"
permalink: /targeted-user-feedback/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../trusting-llm-output/">Trusting LLM Output</a>
</nav>


## Context

An LLM generates content that users consume directly (a lesson script, example sentences, a translation). Automated validation catches many errors, but some still reach users, and the users reading the output are the best-placed detectors of what slipped through.

## Example

Zeeguu lets learners flag LLM-generated content as wrong, in the form that fits each surface:

- **Audio lessons (continuous content).** A lesson script is delivered as audio. When a listener notices a mistake, a **Report** button captures the exact position in the script they were at, so the report points at the specific line rather than the whole lesson.
- **Example sentences (discrete content).** Each generated sentence carries its own report control, so a learner flags the individual sentence that is wrong.

Either way the report says *which* piece of output is wrong, not merely *that* something is.

## Problem

How can errors that slip past automated checks be caught and pinpointed, using the users who are already reading the output?

## Forces

- Automated validation ([LLM-Checking-LLM](../llm-checking-llm/), classical checks) catches many errors but never all; some reach users.
- The user who hits an error is the cheapest, best-placed detector, but only if reporting is low-friction and in the moment.
- A bare "this is wrong" is hard to act on; a report tied to a specific position or item is directly actionable.
- The right report granularity depends on the content: continuous content (audio, long text) needs a position anchor; discrete content (a sentence, a card) is naturally reported as a unit.

## Solution

Give users a low-friction way to flag LLM-generated output, and capture enough context to act on it. Match the report's anchor to the shape of the content: for **continuous** content, anchor to the user's current position (the point in the script); for **discrete** content, attach a per-item report control so the flagged unit is unambiguous.

Route each report into the quality machinery: record it against the artifact (composes with [LLM Content Validation Tracking](../llm-content-validation-tracking/)), let it trigger regeneration (composes with [Soft Invalidation of LLM Artifacts](../soft-invalidation-of-llm-artifacts/)), and use [LLM Output Provenance](../llm-output-provenance/) to identify the prompt and model that produced the flagged output.

## Consequences

- **Users become a last-line error detector.** Mistakes that pass every automated check are still caught, by the people best placed to notice, at almost no cost to the system.
- **A pinpointed report is actionable.** Anchoring to a position or an item turns "something is wrong" into "*this* is wrong," so a report can drive a targeted regeneration instead of a manual hunt.
- **The affordance and the plumbing both have to exist.** A report control has to be designed into each surface, and reports only help if something consumes them (a review queue, an automatic deprecation). A flag nobody acts on is theater.

## Known Uses

- Generic thumbs-up / thumbs-down feedback on LLM output is ubiquitous: **ChatGPT**, **GitHub Copilot**, and most assistant UIs collect it.
- The facet this pattern adds, and that is far less common, is feedback **anchored to a position or item** and wired to **regeneration** of the flagged artifact rather than to offline model training.

## Notes

- Collecting user feedback is itself well-known; the facet worth stating is *granularity*: match the anchor to the content (position for continuous, per-item for discrete).
- Explicit reports are the active end of the spectrum whose passive end [LLM Content Validation Tracking](../llm-content-validation-tracking/) already captures (a user who practiced a word without complaint). Together they run from silent acceptance to active correction.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../deterministic-postprocessing/">← Deterministic Postprocessing</a><a class="nav-next" href="../llm-output-provenance/">LLM Output Provenance →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BTargeted+User+Feedback%5D+&labels=feedback%2Ctrusting-llm-output&body=%2A%2ARe%3A%2A%2A+Targeted+User+Feedback%0A%2A%2ASection%3A%2A%2A+Trusting+LLM+Output%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Ftargeted-user-feedback%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
