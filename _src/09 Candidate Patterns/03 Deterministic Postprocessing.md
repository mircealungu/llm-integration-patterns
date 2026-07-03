# Deterministic Postprocessing

## Example

LLM-simplified article summaries consistently ended with a Unicode ellipsis (`…`), making every home-card preview read as an unfinished sentence. One option was to add a "do not end with ellipsis" instruction to the simplification prompt; the chosen option was a five-line regex stripping any trailing `…` or `..+` at serialization time. The regex handles every case at 100%, including the ~60k pre-existing rows in the database that no prompt change could retroactively touch.

## Forces

When LLM output has a deterministic formatting defect (a stable trailing string, a known preamble, leaked markdown in a plain-text field, trailing whitespace), the obvious instinct is to fix it in the prompt. But:
- Prompt compliance is probabilistic; the same constraint in code is 100%.
- Prompt tokens cost money on every call and can distract the model from the actual semantic task.
- Prompt changes do not affect rows already in the database.
- Code is testable and reviewable; prompt instructions are not.

## Solution

Enforce deterministic constraints in code, at the post-processing or serialization boundary. Reserve prompt instructions for things that genuinely require model judgment.

## Notes

The boundary between "deterministic" and "semantic" is the test. *Strip a trailing `…`*: deterministic, do it in code. *Don't mention the user's name*: semantic, the model has to enforce. When the deterministic rule list grows long, that is itself a signal that the task is poorly scoped, not that the prompt needs more rules.

## Known Uses

- *Adjacent structural cousin.* Structured-output libraries such as **[Outlines](https://dottxt-ai.github.io/outlines/latest/)** constrain generation so the format is valid upfront, and explicitly contrast this with the common practice of "fixing bad outputs after generation using parsing, regex, or fragile code" — evidence that code-side repair is widespread, though Outlines *prevents* rather than *repairs*.
- *Largely best-practice / folklore.* We found no source that names this specific rule — repair a *deterministic* defect in code, not the prompt, because code is 100% reliable and also fixes already-stored rows. The literature documents the stronger cousin (constrained decoding / structured outputs) and generic output sanitization, so we present this as its own contribution and cite these as adjacent, not prior.

> [!draft]- Notes after the focus group
> - is it even more generic? favor programming ? 
> - lllm envy? 
