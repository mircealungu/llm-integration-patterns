---
layout: default
title: "Defensive Output Parsing"
permalink: /defensive-output-parsing/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../quality-assurance/">Quality Assurance</a>
</nav>


## Context

An LLM is asked for output in a fixed shape (JSON, a delimited record), but format compliance is only probabilistic, and the parsed result feeds code on the critical path.

## Example

Multi-word-expression detection asks the LLM for a JSON array but refuses to blindly trust that it will get one. 

- `_parse_response` first strips any markdown code fence (the model often wraps the JSON in one), tries `json.loads`, and on failure regex-extracts the last JSON array in the text (models tend to add a preamble), parses that, and checks for a bare `[]`. 

- If nothing parses, it logs the raw text and returns `[]` rather than raising. 

- A separate `_validate_groups` step then checks the parsed shape (token indices in range) before anything downstream uses it. 

The same layered try / extract / validate / fall-back appears in the translation validator, the simplification service, and the example generators.

## Problem

How can a probabilistic formatting slip be kept from turning into a failed request?

## Forces

- A fixed output format is required (JSON, a delimited record)
- Format compliance is probabilistic 
- A naive parse on the critical path can turn a formatting slip into a failed request

## Solution

Do not trust the raw output's shape. 

Parse in layers: strip known wrappers, attempt a lenient parse, extract the expected structure from the surrounding text if that fails, validate the parsed shape (types, ranges, required fields), and then degrade gracefully (a default, a skip, a retry, or the next provider) instead of raising. 

Keep the strictness in code, where it is deterministic and testable, rather than in ever-longer prompt instructions.

## Consequences

- A malformed response degrades a single result instead of failing the request: the layered parse recovers what it can, and a clean fallback (a default, a skip, a retry, the next provider) covers the rest.
- The strictness lives in parsing code that is deterministic and testable, rather than in ever-longer prompt instructions.
- Provider "JSON mode" or function-calling reduces malformed output but does not remove the need to validate the shape before use.

## Notes

- Composes with a one-shot retry and with [Fail-Fast Provider Chain](../fail-fast-provider-chain/) (a parse failure can trigger the next provider).
- Related to [Deterministic Postprocessing](../deterministic-postprocessing/), which repairs a specific, known formatting defect; this pattern is the broader stance of not trusting the structure at all.

## Known Uses

- **[G-Research](https://www.gresearch.com/news/building-a-code-review-tool-the-llm-patterns-that-actually-work/)**'s code-review tool treats LLM output as "unverified input": it normalises responses by "removing wrappers before parsing" (some providers return bare JSON, some wrap it in markdown fences), validates every finding against an authoritative rule index (invalid findings are "rejected outright"), detects truncation via the `length` finish reason and retries with a lower cap, and sends structurally-invalid output back to the model for one repair pass.
- **[Honeycomb](https://www.honeycomb.io/blog/hard-stuff-nobody-talks-about-llm)**'s Query Assistant parses the LLM output, "correct[s] it (if it's correctable)," validates it, and instruments parse vs. validation errors separately before running the query.
- *Tools that ship this.* Validation/repair is widely productized — [Instructor](https://python.useinstructor.com/) (Pydantic + auto-retry), [LangChain](https://python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser.html) `OutputFixingParser`, and provider [structured-output](https://developers.openai.com/api/docs/guides/structured-outputs) modes (which still require handling truncation and refusals) — but a library that *provides* validation is the mechanism, not evidence of an in-app stance.

Thanks to [Cesare Pautasso](http://www.pautasso.org/) for the discussion that prompted this pattern.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../hybrid-classical-llm-pipeline/">← Hybrid Classical+LLM Pipeline</a><a class="nav-next" href="../deterministic-postprocessing/">Deterministic Postprocessing →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BDefensive+Output+Parsing%5D+&labels=feedback%2Cquality-assurance&body=%2A%2ARe%3A%2A%2A+Defensive+Output+Parsing%0A%2A%2ASection%3A%2A%2A+Quality+Assurance%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fdefensive-output-parsing%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
