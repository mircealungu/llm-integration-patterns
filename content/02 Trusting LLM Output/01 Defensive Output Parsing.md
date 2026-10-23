# Defensive Output Parsing

*Check the shape of every LLM response in code, and repair it if needed.*

## Context

An LLM is asked for output in a fixed shape (JSON, a delimited record), and the parsed result feeds code on the critical path. Some providers can enforce a schema and some cannot, and even an enforced schema does not guarantee a response the code can consume.

## Example

[Multi-word-expression](../zeeguu/#multi-word-expressions) detection asks the LLM for a JSON array (groups of word positions in a sentence) but refuses to blindly trust that it will get one. 

- `_parse_response` first strips any markdown code fence (a triple-backtick code block the model often wraps the JSON in), tries `json.loads`, and on failure regex-extracts the last JSON array in the text (models tend to add a preamble), parses that, and distinguishes a legitimately empty result (`[]`) from a parse failure. 

- If nothing parses, it logs the raw text and returns `[]` rather than raising. 

- A separate `_validate_groups` step then checks the parsed shape (token indices in range) before anything downstream uses it. 

The same layered try / extract / validate / fall-back appears in the translation validator, the [simplification](../zeeguu/#article-simplification) service, and the example generators.

## Problem

How can a malformed response, one that code cannot safely consume, be kept from turning into a failed request?

## Forces

- **Format compliance is never fully guaranteed, and a naive parse fails the request.** Without an enforced schema the model can wrap the output in a code fence or add a preamble. With one, the response can still be cut off at the token limit or replaced by a refusal, and the schema language cannot state every constraint the code relies on (an index that must point into the input). Either way the parsed result feeds downstream code, so an unhandled slip turns into a failed request.
- **Provider schema enforcement is free where it exists, but not everywhere.** Constrained decoding removes syntax slips at the source, yet a cheaper, local, or fallback model in the chain may offer only a JSON mode or nothing at all. *(pushes toward relying on the provider for syntax, and keeping code for the rest)*
- **Strictness in the prompt is tempting but brittle.** Formatting failures invite ever-longer prompt instructions, which are hard to test and still only probabilistic. *(pushes toward prompt-stuffing)*
- **Strictness in parsing code is deterministic and testable**, at the cost of code to write and maintain. *(pushes toward defensive parsing)*

## Solution

Do not trust the raw output's shape. 

Where the provider can enforce a schema (structured output), request it: syntax slips then disappear at the source. Where it cannot, repair the syntax in code: strip known wrappers, attempt a plain parse, and if the model wrapped the output in prose, find the expected structure inside the text and parse that.

In both cases, check in code what the schema cannot guarantee: that the response is complete, that it is not a refusal, and that it satisfies the structural constraints the code relies on (types, ranges, required fields, references into the input). On failure, degrade gracefully (a default, a skip, a retry, or the next provider in a fallback chain of LLM vendors) instead of raising.

Keep the strictness in code, where it is deterministic and testable, rather than in ever-longer prompt instructions. The question here is only whether code can consume the output; whether consumable output is *correct* is the concern of *Reject and Reprompt* and *LLM-Checking-LLM*.

![[defensive-output-parsing-diagram.svg]]
*A provider that enforces a schema sends JSON straight to the check; output from one that does not has its syntax repaired in code first. Either way, code checks what no schema guarantees (the response is complete, not a refusal, and its indices point into the input), and a response that fails degrades to a fallback instead of raising.*

## Consequences

- A malformed response degrades a single result instead of failing the request: the layered parse recovers what it can, and a clean fallback (a default, a skip, a retry, the next provider) covers the rest.
- The parse layer is code to write and maintain, and it has to be kept in step with the prompt and the provider as the output format drifts.
- Provider structured output removes the syntax repair where it is offered, but not truncation, refusals, or the constraints its schema language cannot state, so the checks shrink rather than disappear.

## Known Uses

- **[G-Research](https://www.gresearch.com/news/building-a-code-review-tool-the-llm-patterns-that-actually-work/)**'s code-review tool treats LLM output as "unverified input": it normalises responses by "removing wrappers before parsing" (some providers return bare JSON, some wrap it in markdown fences), validates every finding against an authoritative rule index (invalid findings are "rejected outright"), detects truncation via the `length` finish reason and retries with a lower cap, and sends structurally-invalid output back to the model for one repair pass.
- **[Honeycomb](https://www.honeycomb.io/blog/hard-stuff-nobody-talks-about-llm)**'s Query Assistant parses the LLM output, "correct[s] it (if it's correctable)," validates it, and instruments parse vs. validation errors separately before running the query.

## Notes

- Composes with a one-shot retry and with a provider fallback chain (a parse failure can trigger the next provider).
- *Partly absorbed by the providers.* When the pattern was first written, every layer was application code. Since 2024 providers enforce schemas by constrained decoding ([OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs) from August 2024, [Anthropic](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) from November 2025), which removes the fence-and-preamble repair for those providers. What their documentation still leaves to the caller is the remainder this pattern keeps: both can return output cut off at the token limit or a refusal in place of the schema, Anthropic's schemas cannot state `minimum` or `maximum`, and [DeepSeek's JSON Output](https://api-docs.deepseek.com/guides/json_mode) guarantees valid JSON but not a schema, and "may occasionally return empty content". A pattern shrinking as the platform absorbs part of it is the kind of drift the patterns in Managing Change Over Time address.
- Broader than repairing a specific, known formatting defect: this pattern is the stance of not trusting the structure at all.
- *Prior art: error-tolerant parsing.* Recovering the expected structure and skipping the surrounding text is the LLM-output analogue of [island grammars](https://doi.org/10.1109/WCRE.2001.957806) (parse the fragments of interest, skip the rest) and other lenient, error-tolerant parsing long used to pull structure out of irregular input.
- *Enablers (not instances).* Validation/repair is widely productized, [Instructor](https://python.useinstructor.com/) (Pydantic + auto-retry), [LangChain](https://python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser.html) `OutputFixingParser`, and provider [structured-output](https://developers.openai.com/api/docs/guides/structured-outputs) modes (which still require handling truncation and refusals), but a library that *provides* validation is the mechanism, not evidence of an in-app stance.
