# Defensive Output Parsing

*Check the shape of every LLM response in code, and repair it if needed.*

## Context

An LLM is asked for output in a fixed shape (JSON, a delimited record), and code reads that output while the user waits. How much the LLM providers enforce such a shape differs between providers and keeps changing.[^dop-providers]

[^dop-providers]: OpenAI has enforced a requested [JSON schema](https://developers.openai.com/api/docs/guides/structured-outputs) since August 2024 and Anthropic [since November 2025](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). [DeepSeek's JSON Output](https://api-docs.deepseek.com/guides/json_mode) guarantees valid JSON but not a schema, and "may occasionally return empty content".

## Problem

A response in the wrong shape makes the code that reads it throw an error, and the user sees that error instead of what they asked for. How can a system use LLM output in code so that a malformed response never reaches the user as an error?

## Problem in Zeeguu

[Multi-word expression](../zeeguu/#multi-word-expressions) detection asks the LLM for a JSON array: groups of word positions in a sentence. What comes back is not always that array. It may be wrapped in a markdown code fence, preceded by a sentence of explanation, or contain positions that point past the end of the sentence.

## Forces

- **Models do not always follow the format.** Asked for JSON, a model may wrap it in a code fence, add a sentence first, stop halfway at the token limit, or refuse. *(pulls toward not trusting the response)*
- **Providers can enforce the format, but not all of them, and not fully.** A cheaper or fallback model may offer no enforcement, and no schema prevents a cut-off answer, a refusal, or a position outside the input. *(pulls toward leaving it to the provider)*
- **Prompt instructions are cheap to add but unreliable.** "Return only JSON" costs one line, but the model may still slip, and a prompt cannot be unit-tested. *(pulls toward stricter prompts)*
- **Checking code is reliable, but it is code.** It has to be written, tested and kept in step with each prompt. *(pulls toward less code)*

## Solution

Never hand raw LLM output to the code that uses it. At minimum, parse it inside a guard, and when the parse fails, fall back (a default, a skip, a retry, or the next provider) instead of raising. Add the following layers where they pay off:

- **Request the shape.** Where the provider can enforce a schema, ask for it: syntax slips then disappear at the source.
- **Repair the syntax.** Where it cannot, strip known wrappers, attempt a plain parse, and if the model wrapped the output in prose, find the expected structure inside the text and parse that.
- **Check the content.** In both cases, check in code what no schema guarantees: that the response is complete, that it is not a refusal, and that it meets the constraints the code relies on (types, ranges, required fields, positions inside the input).

Keep this strictness in code, where it is deterministic and testable, rather than in ever-longer prompt instructions. The question here is only whether code can use the output; whether usable output is *correct* is the concern of *Reject and Reprompt* and *LLM-Checking-LLM*.

![[defensive-output-parsing-diagram.svg]]
*A provider that enforces a schema sends JSON straight to the check; output from one that does not has its syntax repaired in code first. Either way, code checks what no schema guarantees (the response is complete, not a refusal, and its indices point into the input), and a response that fails degrades to a fallback instead of raising.*

## Solution in Zeeguu

The multi-word expression detector parses in layers. Simplified, its parser reads:[^dop-mwe]

```python
def parse_groups(reply, sentence):
    text = strip_code_fence(reply)
    data = try_json(text)                       # plain parse
    if data is None:
        data = try_json(last_json_array(text))  # skip a preamble if it exists 
    if data is None:
        log(reply)
        return []                               # no expressions, no error
    return [g for g in data                     # drop groups that point
            if all_positions_in(g, sentence)]   # outside the sentence
```

When nothing parses, the sentence is simply shown without expressions marked.

The same layers of repair, check and fall-back appear in the translation validator, the [simplification](../zeeguu/#article-simplification) service and the example generators.

[^dop-mwe]: `_parse_response` and `_validate_groups` in [`zeeguu/core/mwe/llm_mwe_detector.py`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/mwe/llm_mwe_detector.py#L221-L275), in the `zeeguu/api` repository.

## Consequences

- **A malformed response costs one result, not an error.** The layered parse recovers what it can, and the fallback covers the rest: at worst, the user gets the page with one result missing.
- **One parser per kind of call.** Each prompt asks for its own shape, so each needs its own parse and check, kept in step with the prompt as either changes. Zeeguu has about fourteen such functions, and its example generator keeps one copy per provider.
- **The checks shrink as providers improve, but do not go away.** Schema enforcement removes the syntax repair, not cut-off answers, refusals, or constraints a schema cannot state, and a fallback model in the chain may enforce nothing. Waiting for the providers therefore does not remove the need for this pattern; it only makes the repair layer smaller.

## Known Uses

- **[G-Research](https://www.gresearch.com/news/building-a-code-review-tool-the-llm-patterns-that-actually-work/)**'s code-review tool treats LLM output as "unverified input": it normalises responses by "removing wrappers before parsing" (some providers return bare JSON, some wrap it in markdown fences), validates every finding against an authoritative rule index (invalid findings are "rejected outright"), detects truncation via the `length` finish reason and retries with a lower cap, and sends structurally-invalid output back to the model for one repair pass.
- **[Honeycomb](https://www.honeycomb.io/blog/hard-stuff-nobody-talks-about-llm)**'s Query Assistant parses the LLM output, "correct[s] it (if it's correctable)," validates it, and instruments parse vs. validation errors separately before running the query.
- *Prior art.* Finding the expected structure and skipping the text around it is the LLM-output version of [island grammars](https://doi.org/10.1109/WCRE.2001.957806) (parse the fragments of interest, skip the rest) and other error-tolerant parsing long used to pull structure out of irregular input.
- *Libraries.* [Instructor](https://python.useinstructor.com/) (Pydantic validation with automatic retry) and LangChain's [`OutputFixingParser`](https://python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser.html) package parts of this pattern for reuse.

## Related Patterns

A failed parse can trigger a retry, as in *Reject and Reprompt*, or the next provider, as in *Fail-Fast Provider Chain*. Provider schema enforcement taking over part of this pattern is the kind of drift the patterns in Managing Change Over Time address.
