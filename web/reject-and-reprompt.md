---
layout: default
title: "Reject and Reprompt"
permalink: /reject-and-reprompt/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../trusting-llm-output/">Trusting LLM Output</a>
</nav>


## Examples

Audio lesson scripts are generated at a high temperature so the dialogues sound natural, and the same freedom occasionally lets a dialogue drift into the wrong language. A cheap classical language detector checks each generated script. When it rejects one, the script is neither repaired nor silently dropped: it is regenerated with a prompt extended by the rejected output and the constraint it broke. The detector costs almost nothing next to the generation, and the second attempt is conditioned on the specific failure rather than resampling the same distribution.

The same loop runs over [article simplification](../zeeguu/#article-simplification), where a stored summary or a simplified level occasionally comes back in the article's original language instead of the target one. It was extracted into a shared helper once a third call site needed it, and the helper deliberately refuses to decide what happens when the attempts run out, because the three call sites disagree: the assessment-and-summary path drops the summary and keeps the assessment, simplification fails the run or drops the offending CEFR level and keeps the rest, and the provider services return nothing and let their caller decide.[^rr-helper]

What varies is not the check or the retry but the exhaustion policy, and it varies with how much of the result survives partial failure. Where the output is a bundle of independently droppable pieces, the loop can give up on one and keep the others; where it is a single artifact, giving up means losing all of it.

[^rr-helper]: [`generate_in_language`](https://github.com/zeeguu/api/blob/master/zeeguu/core/language/generate_in_language.py) in the `zeeguu/api` repository.

## Forces

A validator can be cheap and classical even when the thing it validates can only be produced by an LLM, so the check costs a fraction of the generation and can afford to run on every output.

Some defects cannot be repaired in place. A stray trailing ellipsis has a deterministic fix; a dialogue in the wrong language does not, and the only route to a correct result is another generation.

A plain retry against a non-deterministic generator carries roughly the same failure probability as the first attempt, so a retry that does not say what went wrong buys another sample rather than a better one.

## Solution

Validate generated output with a cheap classical check placed downstream of the LLM. On rejection, regenerate rather than repair, extending the prompt with the rejected output and the property it violated, so the next attempt is conditioned on the failure. Bound the number of attempts, and record a terminal state when they run out. Some failures are permanent for a given input rather than incidental: a model that declines a topic on policy grounds declines it again tomorrow, and a generator that never produces output gives the check nothing to reject. Without a record, a scheduled job rediscovers the same dead end on every run.

## Known Uses

- **Zeeguu** validates generated [audio lesson](../zeeguu/#audio-lessons) scripts with a classical language detector and regenerates with an extended prompt when the detector rejects a script. The same loop carries the terminal case: when the model refuses a topic outright, judging the example offensive, the loop stops and the word is marked as one no lesson will be generated for, so the nightly job does not retry it indefinitely. *Added in 2026, and too recent to report how often the second attempt succeeds.*
- **[Instructor](https://python.useinstructor.com/)** feeds the Pydantic validation error back into the prompt and reasks the model: the same loop with a schema validator in place of the language check.

## Notes

- Distinct from its neighbours in *Trusting LLM Output*. [Defensive Output Parsing](../defensive-output-parsing/) handles output that is malformed rather than wrong, and recovers what it can from the response in hand. A stable, well-understood defect is better fixed in place, with no second call at all. [LLM-Checking-LLM](../llm-checking-llm/) spends a second LLM call on the check, whereas here the check is classical and nearly free.
- The error-informed retry is the part that generalizes beyond a classical checker: the same move applies whenever a check of any kind rejects a generation, which is why [LLM-Checking-LLM](../llm-checking-llm/) now names it as one of its failure policies.
- The terminal record is not [LLM Content Validation Tracking](../llm-content-validation-tracking/). That pattern tracks the trust level of content that exists; this records that content will never exist for a given input, so the work is not attempted again. It matters most under [Anticipatory Precomputation](../anticipatory-precomputation/), where a scheduled job would otherwise rediscover the same refusal on every run.
- A refusal and a rejected generation are not the same event. The check fires on output the generator produced; a refusal means there is no output to check. The trigger differs, the terminal branch is the same.
- *Maturity.* Four call sites across three Zeeguu features (assessment and summary, article simplification, audio lesson scripts), each with its own policy for what happens when the attempts run out, plus one productized enabler in Instructor. The retry loop was extracted into a shared helper, `generate_in_language`, once a third call site needed it; the helper deliberately does not decide the exhaustion policy, because the call sites disagree about it.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../targeted-user-feedback/">← Targeted User Feedback</a><a class="nav-next" href="../llm-output-provenance/">LLM Output Provenance →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BReject+and+Reprompt%5D+&labels=feedback%2Ctrusting-llm-output&body=%2A%2ARe%3A%2A%2A+Reject+and+Reprompt%0A%2A%2ASection%3A%2A%2A+Trusting+LLM+Output%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Freject-and-reprompt%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
