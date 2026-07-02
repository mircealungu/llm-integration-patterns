# Defensive Output Parsing

**Example (Zeeguu):** MWE detection asks the LLM for a JSON array and refuses to trust that it gets one. `_parse_response` first strips any markdown code fence (the model often wraps the JSON in one), tries `json.loads`, and on failure regex-extracts the last JSON array in the text (models tend to add a preamble), parses that, and checks for a bare `[]`. If nothing parses, it logs the raw text and returns `[]` rather than raising. A separate `_validate_groups` step then checks the parsed shape (token indices in range) before anything downstream uses it. The same layered try / extract / validate / fall-back appears in the translation validator, the simplification service, and the example generators.

**Forces:** A fixed output format is requested (JSON, a delimited record), but format compliance is probabilistic. The model may wrap the payload in markdown, add an explanation before or after it, emit a trailing comma, use the wrong shape, or occasionally answer in prose. A naive parse on the critical path turns a formatting slip into a failed request, and a formatting slip is far more common than a genuine error.

**Solution:** Do not trust the raw output's shape. Parse in layers: strip known wrappers, attempt a lenient parse, extract the expected structure from the surrounding text if that fails, validate the parsed shape (types, ranges, required fields), and then degrade gracefully (a default, a skip, a retry, or the next provider) instead of raising. Keep the strictness in code, where it is deterministic and testable, rather than in ever-longer prompt instructions.

**Notes:**

- A slip degrades a single result instead of failing the request. It composes with a one-shot retry and with *Fail-Fast Provider Chain* (a parse failure can trigger the next provider).
- Provider "JSON mode" or function-calling reduces malformed output but does not remove the need to validate the shape before use.
- Related to *Deterministic Postprocessing*, which repairs a specific, known formatting defect; this pattern is the broader stance of not trusting the structure at all. Related to *LLM Content Validation Tracking*, which tracks whether the content is correct; this pattern is about whether the output has the expected form.
