# Defensive Output Parsing

*Check the format of every LLM response in code, and repair it if needed.*

## Context

An LLM is asked for output in a fixed format (JSON, or fields separated by a character such as `|`), and code reads that output. How much the LLM providers enforce such a format differs between providers and keeps changing.[^dop-providers]

[^dop-providers]: OpenAI has enforced a requested [JSON schema](https://developers.openai.com/api/docs/guides/structured-outputs) since August 2024 and Anthropic [since November 2025](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). [DeepSeek's JSON Output](https://api-docs.deepseek.com/guides/json_mode) guarantees valid JSON but not a schema.
[^dop-regress]: Nor can a provider's guarantee be taken on trust: a provider can ship a regression like any other dependency, and DeepSeek's own documentation warns that its JSON mode "may occasionally return empty content". The checks in code stay as the last line of defense.

## Problem

A response in the wrong format makes the code that reads it fail: either with an error the user sees, or, worse, by carrying on as if the response had said something it did not (treating an unreadable verdict as a yes, say). How can code use LLM output safely when some responses arrive malformed?

## Problem in Zeeguu

Before a learner practices a word they saved while reading, Zeeguu asks an LLM whether the translation they saved with it is right, and code reads the verdict out of the reply. The reply used to be a single line: `VALID` followed by details about the word (how common it is, its CEFR level, A1 to C2, and its type), or `FIX` followed by the corrected word and translation. Two lines in that format, for a French word glossed in English (empty fields are allowed); the second corrects *campagne* from "campaign" to "countryside":

```text
    VALID|common|A1|single_word||
    FIX|campagne|countryside|common|A2|single_word|||
```

In October 2026, Zeeguu moved from Sonnet 4.5 to Sonnet 5.5. The new model behaved differently with the same prompt: it wrote its reasoning before the `VALID|FIX` verdict line. On 22 of 50 production cases, it hit the 200-token limit before reaching the line. The parser found neither `VALID` nor `FIX`, and its rule for an unexpected reply was to assume valid. So 22 replies were passed, and almost all of them were translations that needed fixing.[^dop-834]

[^dop-834]: Pull request [#834](https://github.com/zeeguu/api/pull/834) in the `zeeguu/api` repository, with the measurement on the 50 cases.

## Forces

- **Trusting the output is easy.** Most responses come back in the requested format, and more and more providers enforce it, so handing the response straight to the code is simple and usually works. *(pulls toward trusting the response)*
- **Models do not always follow the format.** Asked for JSON, a model may wrap it in a code fence, add a sentence first, stop halfway at the token limit, or refuse. *(pulls toward not trusting the response)*

## Solution

Parse every LLM response inside a guard (a `try`/`except` around the parse) before any code uses it, and when the parse fails, fall back instead of raising. The fallback must count as a failure, never as a pass: skip the item, retry, or ask the next provider, and use a default only if it is the safe answer. On top of that minimum, add the following layers where they pay off:

- **Request the format.** Where the provider can enforce a schema, ask for it: formatting errors then disappear at the source.
- **Repair only known formatting errors.** Where the provider cannot enforce a schema, strip known wrappers (such as markdown code fences), attempt a plain parse, and if the model wrapped the output in prose, find the expected structure inside the text and parse that. Reject anything else rather than guess.
- **Check the content.** In both cases, check in code what no schema guarantees: that the response is complete, that it is not a refusal, and that it meets the constraints the code relies on (types, ranges, required fields, or that an index the model returns falls inside the input).
- **Make the fallbacks visible.** Log every response that fell back, with its raw text, and count them, so a change that breaks every response shows up as a jump in the count rather than as quietly emptier results.

Keep this strictness in code, where it is deterministic and testable, rather than in ever-longer prompt instructions. The question here is only whether code can use the output; whether usable output is *correct* is the concern of *Reject and Reprompt* and *LLM-Checking-LLM*.

![[defensive-output-parsing-diagram.svg]]
*A provider that enforces a schema sends JSON straight to the check; output from one that does not has its syntax repaired in code first. Either way, code checks what no schema guarantees (the response is complete, not a refusal, and any index it returns falls inside the input), and a response that fails degrades to a fallback instead of raising.*

## Solution in Zeeguu

The fix answers each part of that failure.[^dop-834] The validator now requests structured output: the API holds the reply to a JSON schema, so no free text can come before the verdict, and the schema's first field, `reason`, gives the model a place for the reasoning it wants to write. The model fills the fields in order, so the reasoning comes first and cannot crowd out the verdict. With the schema enforced, no repair layer is needed. The token limit went from 200 to 1000, so the reply is not cut off. And a reply that still cannot be read no longer counts as a pass: the word stays unchecked and the failure is reported. On the same 50 cases, no reply was wrongly passed. Simplified, the validator reads:[^dop-validator]

```python
def validate(word, translation, sentence):
    try:
        # a JSON schema with `reason` first; room for the whole reply
        reply = ask_llm(prompt, schema=VALIDATION_SCHEMA, max_tokens=1000)
        result = parse(reply)              # an unreadable reply raises
    except Exception as error:
        report(error)                      # shows up in error tracking
        return None                        # no verdict: the word stays unchecked
    return result
```

[^dop-validator]: `validate_and_classify`, `_ask` and `_parse_response` in [`zeeguu/core/llm_services/translation_validator.py`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/translation_validator.py), in the `zeeguu/api` repository.

## Consequences

- **A malformed response costs one result, not an error.** The layered parse recovers what it can, and the fallback covers the rest: at worst, one item is missing or, as in Zeeguu, one word stays unchecked.
- **The fallback rate has to be watched.** Users never see a malformed response, so only the log and the count show when a prompt or model change breaks them.
- **Repair can hide a broken reply.** The more the code repairs, the more it guesses: closing the brackets of a reply cut off at the token limit turns it into valid JSON that is silently missing its last items. Repairing only known formatting errors, and rejecting the rest, keeps the guessing small.
- **One parser per kind of call.** Each prompt asks for its own output format, so each needs its own parser and check, kept in step with the prompt as either changes. Zeeguu has about a dozen such functions.
- **The checks shrink as providers improve, but do not go away.** Schema enforcement removes the syntax repair, not cut-off answers, refusals, or constraints a schema cannot state, and a fallback model in the chain may enforce nothing. Waiting for the providers therefore does not remove the need for this pattern; it only makes the repair layer smaller.[^dop-regress]

## Known Uses

- **[G-Research](https://www.gresearch.com/news/building-a-code-review-tool-the-llm-patterns-that-actually-work/)**'s code-review tool treats LLM output as "unverified input": it normalizes responses by "removing wrappers before parsing" (some providers return bare JSON, some wrap it in markdown fences), validates every finding against an authoritative rule index (invalid findings are "rejected outright"), detects truncation via the `length` finish reason (the API's signal that a reply was cut off) and retries with a lower cap, and sends structurally-invalid output back to the model for one repair pass.
- **[Honeycomb](https://www.honeycomb.io/blog/hard-stuff-nobody-talks-about-llm)**'s Query Assistant parses the LLM output, "correct[s] it (if it's correctable)," validates it, and instruments parse vs. validation errors separately before running the query.
- *Prior art.* Finding the expected structure and skipping the text around it is the LLM-output version of [island grammars](https://doi.org/10.1109/WCRE.2001.957806) (parse the fragments of interest, skip the rest) and other error-tolerant parsing long used to pull structure out of irregular input.
- *Libraries.* [Instructor](https://python.useinstructor.com/) (Pydantic validation with automatic retry) and LangChain's [`OutputFixingParser`](https://python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser.html) package parts of this pattern for reuse.

## Related Patterns

A failed parse can trigger a retry, as in *Reject and Reprompt*, or the next provider, as in *Fail-Fast Provider Chain*. Provider schema enforcement taking over part of this pattern is the kind of drift the patterns in the section Managing Change Over Time address.
