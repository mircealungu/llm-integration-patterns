---
layout: default
title: "LLM Content Validation Tracking"
permalink: /llm-content-validation-tracking/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../trusting-llm-output/">Trusting LLM Output</a>
</nav>


*Tag every stored LLM output with its validation state.*

## Context

An application stores what an LLM generates next to data people wrote or checked, and later features read both. Some of the generated data has been checked, some has not, and once stored the two look the same.

## Problem

How can trusted and untrusted LLM-generated data be told apart after it lands in the database, so each use relies only on data checked enough for it?

## Problem in Zeeguu

Zeeguu has an LLM rewrite each article it offers at easier reading [levels](../zeeguu/#article-simplification), and stores every version for the next reader who asks for that level. Most versions are fine, but some are not: the LLM sometimes writes a version in the wrong language, and readers find others confusing or broken. Once stored, a bad version looks like a good one, and it is served to every reader at that level.

## Forces

- **Checking before storing keeps the database clean.** If only output that passed a check is stored, everything in it can be trusted as it is. *(pushes toward checking before storing)*
- **Not every error can be caught before storing.** A cheap check can run on every output, but a thorough one, by another model or by a person, costs more than the system can spend on every item. And some errors only a reader notices, such as a text that is correct but confusing. *(pushes toward catching errors after storing)*

## Solution

Maintain an explicit, queryable validation state for all LLM-generated content in the data model. Never let LLM-generated content silently become trusted data. Every query that reads this content filters on the states its use can tolerate. The validation state may be a simple flag, but more often it has several ordered levels (e.g., rejected, or one of the ordered levels unverified → passed an automatic check → used without complaint → confirmed by a trusted user).

The state records how far an item has been checked, not that it is right. A confirmed item can still be wrong, so a later signal must be able to lower its validation state.

<figure class="img">
  <a href="/images/llm-content-validation-tracking-diagram.svg"><img src="/images/llm-content-validation-tracking-diagram.svg" alt="Every stored LLM-generated record carries a validation state, raised or lowered by checks and by what users report. Each use reads only the states it can tolerate: a low-stakes use accepts any level, a high-stakes one only confirmed records."></a>
  <figcaption>Every stored LLM-generated record carries a validation state, raised or lowered by checks and by what users report. Each use reads only the states it can tolerate: a low-stakes use accepts any level, a high-stakes one only confirmed records.</figcaption>
</figure>

## Solution in Zeeguu

Each stored simplified article version carries a `broken` flag, together with the reason it was set.[^cvt-broken] Most versions in the wrong language are never stored: a language check runs when a version is written, and asks the LLM to write it again ([Reject and Reprompt](../reject-and-reprompt/)). Two things set the flag. A script that checks the stored versions marks those that slipped through in the wrong language, and readers can report a version: two reports mark it broken, and so does a single report from a teacher, whose judgment the system trusts more. A broken version is no longer offered, and the next reader who asks for that level gets a newly generated one. This is the simplest form of the pattern: a single flag that only takes trust away, while versions nobody has checked are served by default.

[^cvt-broken]: `Article.broken`, `UserArticleBrokenReport`, `available_simplified_versions`, `generate_in_language`, and `tools/audit_stored_article_languages.py` in the `zeeguu/api` repository.

## Consequences

- **Each feature decides how much checking it needs.** A feature where an error does real harm uses only output that a check or a person has confirmed; one where an error costs little can also use output nobody has checked yet. Either way, rejected output is never used as if it were good.
- **The data model carries a validation state to maintain.** It must be set on every write and updated on every check, and every feature that reads the content must filter on it: one that forgets serves rejected output. It can be a yes/no flag, several levels, or a count of the people who confirmed an item; which one fits depends on the domain.

## Known Uses

The documented uses are data-labeling tools. We found no first-hand account of an application that tracks the trust state of its own LLM output, which is one reason we consider this pattern still emerging.

- **[Argilla](https://docs.argilla.io/latest/how_to_guides/annotate/)**, an open-source platform for annotating and reviewing model-generated data, gives every record an explicit status: a model suggestion starts as *pending*, becomes a *draft* and then *submitted* as someone works on it, and ends up *validated* or *discarded*. A suggestion is never treated as correct until a human has moved it to *validated*.
- **[Label Studio](https://docs.humansignal.com/guide/ground_truths)**, another annotation tool, flags each item as ground truth or not and records whether it has been reviewed, so human-verified "gold" data stays clearly separate from unreviewed model predictions.
- **[Snorkel](https://arxiv.org/abs/1711.10160)** (Ratner et al., VLDB 2017) attaches probabilistic confidence to programmatically generated labels rather than treating them as ground truth: a confidence score rather than fixed states.

The three tools show the range of options for how finely trust is recorded: a lifecycle with several states (Argilla), a yes/no "gold" flag (Label Studio), and a probability score (Snorkel).

## Related Patterns

[Track Output Provenance](../track-output-provenance/) records how an artifact was made; this pattern records whether it has been confirmed. Together they answer both questions about a stored artifact. [LLM-Checking-LLM](../llm-checking-llm/) is one way to check an output, and its verdict is what this pattern stores.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../llm-checking-llm/">← LLM-Checking-LLM</a><a class="nav-next" href="../deterministic-postprocessing/">Deterministic Postprocessing →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM+Content+Validation+Tracking%5D+&labels=feedback%2Ctrusting-llm-output&body=%2A%2ARe%3A%2A%2A+LLM+Content+Validation+Tracking%0A%2A%2ASection%3A%2A%2A+Trusting+LLM+Output%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Fllm-content-validation-tracking%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
