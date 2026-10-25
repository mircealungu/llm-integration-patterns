# Regression Set per LLM Task

## Context

An application has several LLM tasks: features that each send a prompt and act on the answer (validate a translation, assess an article, generate example sentences). The prompts get tuned in production, often after an incident, and each wording is the one that worked on the cases someone looked at then. Later something forces the prompt to change for a reason that has nothing to do with its output: a cost optimization, a model upgrade, a new field in the reply, a fix to a neighboring rule.

## Example

In October 2026 we looked at turning on prompt caching for Zeeguu's Anthropic calls. Caching only reuses an identical prefix of the prompt, and every Zeeguu prompt starts with its variable part: the translation validator opens with the highlighted word, the sentence and the two languages, and only then gives about 1,100 tokens of fixed instructions. Caching it means moving the instructions to the front, a change meant to alter nothing the model decides.

The change stopped there. The validator prompt had been tuned case by case (the "to understand" form rule, the dictionary case, the "noget af" context-only gloss), each fix checked on the cases at hand, and none of those cases had been kept. Re-evaluating meant first rebuilding an input set from production and deciding, again, what the right verdicts were. Zeeguu had done that work before, more than once: `eval_haiku_models.py` sampled 200 articles to admit Haiku 5.5, the validator comments cite "50 prod cases" and "max 266 on 50 prod cases", audits sampled stored output. Each evaluation was built for its occasion and thrown away with it.

## Problem

How do you change a tuned prompt, for any reason, without silently undoing what earlier tuning fixed?

## Forces

- **Prompts are code without tests.** A change to a prompt is a change to behavior, but nothing fails when it regresses; the regression shows up later, in stored output, as a share of wrong verdicts.
- **The cases that shaped a prompt are its specification.** Each fix was made for a concrete input; once that input is lost, so is the reason for the wording, and the next edit can undo it.
- **Rebuilding an evaluation costs more than keeping one.** Sampling production, labeling the right answers and writing a comparison script is a day of work; repeating it for every change means small, cheap changes (reordering for caching) do not get made at all.
- **Many changes are meant to be neutral.** Reordering, a model upgrade, a provider switch, a schema change: the question is not "is it better" but "did anything move", which a recorded set answers cheaply.
- **Running a set costs money.** Every evaluation run spends tokens, so the set has to stay small enough to run on every change, and the run needs its own caching and batching.

## Solution

Give every LLM task a regression set from the day it ships, kept next to the prompt and versioned with it: recorded production inputs together with the output the current prompt gives and, where someone has judged it, the output it should give. Add a case whenever the prompt is fixed for one: the input that showed the bug, with the answer the fix is meant to produce. Keep a script per task (or one generic runner) that sends the set through a candidate prompt or model and reports what changed against the recorded answers: changed decisions first, then label distributions, then cost and latency.

No change to a task's prompt, model or request settings merges without a run on its set. A change meant to be neutral passes when nothing moves; a change meant to improve passes when the intended cases move and nothing else does.

## Consequences

- **Neutral changes become cheap.** Caching, model upgrades and reordering can be done and shown harmless in one run, instead of being deferred because checking them costs a day.
- **Fixes stay fixed.** The case behind each rule in the prompt is in the set, so an edit that undoes it fails the run.
- **The set is a specification someone has to maintain.** When the domain changes (a rule is deliberately relaxed), the recorded answers change with it, and a stale answer fails a correct prompt.
- **Recorded production inputs are user data.** Sentences learners highlighted, articles from publishers: the set needs the same care as the database it came from, and may not be shareable with the code.
- **It catches drift only on what it contains.** A small set misses rare failures; it complements, not replaces, checking stored output (*Check What Should Exist*).

## Relation to other patterns

- *One Wish per Genie* admits a fallback only after evaluating it on recorded production inputs. That is one occasion for this set; this pattern makes the set permanent and per task, so the evaluation is there for every change, not built for the one at hand.
- *LLM Output Provenance* records which prompt version and model produced each stored output; together with a regression set it lets a past run be replayed against a new prompt.

## Known Uses

To find. Candidates: eval-driven development as recommended by model providers (build the evaluation before tuning the prompt), and tools such as promptfoo and OpenAI Evals that run a prompt over a stored test set in CI.

## Notes

- Came up on 23 Oct 2026 while trying to turn on prompt caching for the validator; see the Example.
