---
layout: default
title: "Deterministic Postprocessing"
permalink: /deterministic-postprocessing/
---


[← All patterns](../)


**Example (Zeeguu):** LLM-simplified article summaries consistently ended with a Unicode ellipsis (`…`), making every home-card preview read as an unfinished sentence. One option was to add a "do not end with ellipsis" instruction to the simplification prompt; the chosen option was a five-line regex stripping any trailing `…` or `..+` at serialization time. The regex handles every case at 100%, including the ~60k pre-existing rows in the database that no prompt change could retroactively touch.

**Forces:** When LLM output has a deterministic formatting defect (a stable trailing string, a known preamble, leaked markdown in a plain-text field, trailing whitespace), the obvious instinct is to fix it in the prompt. But:
- Prompt compliance is probabilistic; the same constraint in code is 100%.
- Prompt tokens cost money on every call and can distract the model from the actual semantic task.
- Prompt changes do not affect rows already in the database.
- Code is testable and reviewable; prompt instructions are not.

**Solution:** Enforce deterministic constraints in code, at the post-processing or serialization boundary. Reserve prompt instructions for things that genuinely require model judgment.

**Notes:** The boundary between "deterministic" and "semantic" is the test. *Strip a trailing `…`*: deterministic, do it in code. *Don't mention the user's name*: semantic, the model has to enforce. When the deterministic rule list grows long, that is itself a signal that the task is poorly scoped, not that the prompt needs more rules.



---
[← All patterns](../) &nbsp;·&nbsp; [💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BDeterministic+Postprocessing%5D+&labels=feedback%2Cpossible-other&body=%2A%2ARe%3A%2A%2A+Deterministic+Postprocessing%0A%2A%2ASection%3A%2A%2A+Possible+Other+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fdeterministic-postprocessing%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
