# One Wish per Genie

## Context

A feature can be served by more than one LLM provider, for availability, cost, or both. Its prompt was written and tuned while one of those providers served it, and the others answer the same API shape, so switching looks like a change of endpoint and key. The output feeds decisions downstream (a classification, a gate, a parsed field), not only text a person reads.

## Problem

How can a feature fall back to another model without silently changing what the feature does?

## Problem in Zeeguu

Zeeguu's crawler assesses every new article with one LLM call: its [CEFR](../zeeguu/#cefr-levels) level, a summary per level, and two rejection signals for paywalled and promotional articles ([crawling](../zeeguu/#crawling)). The call could go to Anthropic or to DeepSeek through the same function.

In August 2026 DeepSeek rejected 90 to 100% of articles as paywalled. It was read as a DeepSeek regression and the crawler was pinned to Anthropic. The cause was the prompt. Its only way to reject an article was to answer with the bare word `unfinished`, which also let a model end the whole answer in one word. Anthropic's model used it as intended; DeepSeek took it as an exit. On six complete Danish articles, DeepSeek answered every one with 10 characters in about a second. The swap had changed the feature's behavior, and nothing in the code had flagged it.

The pin then cost more than the misdiagnosis. With one provider left, Anthropic's monthly spend cap stopped assessment in every language, and the 664 most recent Danish articles went without a level or a summary for over a week.

## Forces

- **Every model is a genie, and the prompt is its wish.** A genie grants the wish as worded, and each genie reads the wording its own way: ambiguous instructions, formatting habits, readiness to stop early. A prompt iterated on one model ends up worded for that genie, without anyone deciding so.
- **Provider APIs look interchangeable.** The request shape is the same (messages in, text out), so the switch is one line, and the type checker and tests have nothing to say about it.
- **Divergence arrives as plausible data, not as errors.** A model that rejects 19% of articles instead of 3% returns well-formed answers. *Defensive Output Parsing* catches a malformed answer; it cannot catch a well-formed answer to a slightly different question.
- **Fallback paths run rarely.** A path taken only during an outage is the least exercised code in the system, and it runs exactly when nobody is watching the output closely.
- **Variants cost upkeep.** A prompt per model per feature multiplies the prompts to maintain and re-check whenever a model changes.

## Solution

Make the unit of fallback a *task*: a genie (a model that may serve the feature) together with its wish (the prompt it is given and, where they differ, the request settings it needs, such as stop sequences, token budget or thinking level, and the parser that reads its answer). Never fall back to a genie alone. Declare, for each feature, its tasks in fallback order, and admit a task to the list only after seeing how its genie grants its wish on recorded production inputs. That evaluation compares decisions, not only parse success: rejection rates, the distribution of assigned labels, and agreement with the first genie on the same inputs.

A task declared without a wish of its own gets the wish of the task before it, so the common case (one prompt that several models read alike) costs a single line. The default is a convenience, not a claim of equivalence: the shared wish still deserves an evaluation on each new genie, and a task gets a wish worded for its genie as soon as that genie reads the shared one differently.

A failover walks the declared list and nothing else. A feature with no evaluated second task has no fallback, and its outage is reported rather than papered over by an untested substitute.

## Solution in Zeeguu

Turning the rejection signals into fields (`INCOMPLETE_ARTICLE: YES/NO`, which a model must fill in and cannot end on) made DeepSeek usable: on the same articles, 6 of 6 complete ones were assessed and 6 of 6 truncated copies rejected. The second divergence came with the fixed prompt. The prompt says that fewer than three paragraphs probably means an incomplete article. DeepSeek applied that rule literally and rejected 19% of a Danish backfill, against the 2 to 3% the old prompt had rejected on Anthropic. The rejected articles averaged 190 words against 598, so DeepSeek was arguably the more correct of the two, but it was a different pipeline, and a coverage alarm calibrated on Anthropic's numbers would have misfired on it.

When provider failover was later added, its first draft took the obvious form ("on a provider outage, retry on the other provider") and so carried the first failure onto a second path: the full-simplification prompt still had the bare-word exit, so an Anthropic outage there would send its articles into DeepSeek's escape hatch and mark them paywalled. The final version declares, per feature, its tasks: which models may serve it, each with which prompt ([`_TASKS`](https://github.com/zeeguu/api/pull/850)). The assessment feature lists DeepSeek and Anthropic's Haiku with the same prompt, which Haiku had run on 200 stored production articles with no parse failures; full simplification lists Anthropic only, until its prompt has a wording that DeepSeek grants as intended.

## Consequences

- **A fallback does the same job as the primary.** Behavioral drift is found once, in an evaluation, rather than in production during an outage. Divergences that are acceptable (DeepSeek's stricter rejection) become known and calibrated for, rather than discovered.
- **The default keeps the cost down, and hides what was not checked.** Reusing the previous wish makes a new task cheap to declare, but one declared that way looks the same whether its wish was evaluated on its genie or not. Recording the evaluation next to the declaration (a comment, a link to the result) keeps that visible.
- **Upkeep grows with the list.** Each task brings a wish to maintain and to re-evaluate whenever that model is upgraded, so a second one is worth declaring only for features where an outage matters. A recorded input set and a comparison script make re-evaluation cheap enough to repeat on every model upgrade.
- **Scope.** The pattern matters most where the output drives a decision (a gate, a label, a parsed field). For free text read by a person, a slightly different style from the fallback is usually tolerable, and the declaration can be as short as "any model, same prompt".
- **It sharpens neighboring patterns.** *Fail-Fast Provider Chain* decides *when* to move to the next provider; this decides *what* the next provider is allowed to be. *Centralized Model Selection* maps a role to a model; here the role maps to a list of tasks, each a genie with an evaluated wish. *Track Output Provenance* should record the model that actually served, so output from a fallback stays attributable after the outage is over.

## Known Uses

- **[Slack](https://slack.engineering/slack-ai-the-path-to-multi-cloud/)** declares the fallback per feature and evaluates it before use: "We developed a model hierarchy for every AI feature", with backup models admitted once they "passed our internal quality and metrics bars".

Slack documents the declaration and the evaluation; it does not say whether prompts differ between the models in a hierarchy. We did not find a documented production system that pairs each fallback model with its own evaluated prompt, so that facet is presented as our own contribution, grounded in Zeeguu.

## Notes

- **The misdiagnosis is the expensive part.** A prompt that a second model reads differently looks like a broken model. In Zeeguu that reading took DeepSeek out of service and left the system on one provider, which is what turned a spend cap into a week without assessment. When a substitute model misbehaves on an existing prompt, the prompt is the first suspect.
- **Escape hatches are model-specific.** Any instruction that lets an answer end early (a bare token, "if X, reply only with Y") is taken with different eagerness by different models. Moving such signals into fields that every answer must contain removed the divergence that mattered most in Zeeguu.
- **Why genie.** Stories about genies are stories about wording: the wish is granted exactly as phrased, and the phrasing matters more than the wisher expected. Here no malice is implied; a genie that grants a wish differently from another is reading the same words another way, and may well be the more literal of the two (DeepSeek's paragraph rule).
