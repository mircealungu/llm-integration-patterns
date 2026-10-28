---
layout: default
title: "Check What Should Exist"
permalink: /check-what-should-exist/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../candidate/">Candidate</a>
</nav>


## Context

An LLM call sits inside a pipeline that is supposed to leave something behind: a level and a summary on every new article, a lesson script in the learner's language, a verdict on every translation. The pipeline is monitored the usual way, by watching the calls: errors, timeouts, failover events, latency. The things it leaves behind are read later, by users or by other features, and nobody reads all of them.

## Problem

How do you find out that an LLM-backed pipeline has stopped doing its job, when each call either succeeded, failed in a way that looked routine, or was never made?

## Problem in Zeeguu

Zeeguu's crawler assesses every new article with one LLM call, which gives it a [CEFR](../zeeguu/#cefr-levels) level and a summary per level ([crawling](../zeeguu/#crawling)). In August 2026 Anthropic's monthly spend cap stopped that call. The errors were in the crawler's logs, but they looked like the occasional failed call that logs always contain, and the crawl itself kept running and saving articles. Over the following week the share of new articles that got assessed went 0, 0, 15, 38, 37, 4 and 4%, against 95 to 99% on a normal day. The 664 most recent Danish articles went without a level or a summary, and the feed, which needs the level to place an article, quietly had less to offer.

## Forces

- **Call-level monitoring answers "did the model work?", not "do we have what we need?".** A failed call is visible; a call that was skipped, answered something well-formed but wrong, or was made by code that no longer runs is not.
- **LLM failures are partial and plausible.** A spend cap, a rate limit, or a prompt a model reads differently produces a share of missing or odd outputs, not a crash. Logs keep moving, and a 40% failure rate looks like noise in a log.
- **The output is read late and by few.** An article without a level is simply not shown; nobody reports what they never saw. The gap shows up as a feed that feels thin, days later.
- **Every check in the pipeline shares the pipeline's assumptions.** A check written in the same code path is skipped when that path is skipped, and is wrong when the prompt it checks against is wrong.
- **Domain expectations need calibration.** "Every article gets assessed" is never literally true: some articles are rejected on purpose, some languages are quiet. A threshold set without looking at healthy days either never fires or always does.

## Solution

State, in domain terms, what the pipeline should have produced over a window, and check the stored data against that statement from outside the pipeline. Phrase the expectation as a ratio of what exists to what should exist ("assessed originals / crawled originals in 24 hours"), so it is independent of how many calls were made, which provider served them, or whether any were made at all. Run the check on its own schedule, not as a step of the job it watches, and send its result to a place a person reads.

Calibrate the threshold on recorded healthy days and on a recorded failure, if there is one, and give it a minimum volume, so that small numbers do not fire it. Count intended exclusions back in, or out, explicitly: an article the LLM rejected as paywalled was handled, not missed.

Keep the call-level monitoring as well. The two answer different questions: the outcome check says that something is wrong and how much, the call-level counts say which model and why.

## Solution in Zeeguu

The fix for the cause was provider failover ([Model-Bound Prompt](../model-bound-prompt/)), with an email the first time a run fails over. The fix for the symptom was a separate check that ignores the LLM calls entirely and asks the database what the crawler should have produced: of the original articles crawled in the last 24 hours, how many have a level? It runs from cron, outside the crawler, every six hours, and alarms below 80%, overall and per language, with a minimum volume so a quiet language on a quiet day does not trip it ([`feed_delivery_health_check.py`](https://github.com/zeeguu/api/pull/887)). Replayed over August, it would have fired on the first day.

Zeeguu had already learned the same lesson once. On 18 August 2026 the check that verifies a summary is written in the article's language was passing on every call, while the prompt asked for the wrong language on every first attempt; 55 English summaries reached storage before anyone looked. A nightly audit now reads stored summaries back and checks their language, independently of generation. Its crontab entry states the reason: *a check that runs inside the thing it is checking cannot catch the case where that thing was never called.*

## Consequences

- **It catches causes nobody has thought of yet.** The check fires on a spend cap, a broken deploy, a skipped code path or a prompt regression alike, because it does not model any of them.
- **It is slow and coarse by design.** A 24-hour window run every six hours finds an outage hours after it starts, and says only that output is missing. Diagnosis still needs the call-level view.
- **It encodes a domain fact that has to be maintained.** When the domain changes (Zeeguu dropped its 100-word minimum for assessment), the expectation changes with it, and a stale expectation fires falsely or not at all.
- **It does not see wrong output that looks right.** A ratio of rows with a level says nothing about whether the levels are right. A model that rejects too many articles as paywalled removes them from the denominator and leaves the ratio healthy; that divergence is caught by evaluating the prompt on each model ([Model-Bound Prompt](../model-bound-prompt/)), or by a check on the rejection rate.
- **It adds a job to run and to keep quiet.** Each outcome check is one more alarm, and alarms that fire on noise get ignored; the calibration step is what keeps it worth reading.

## Known Uses

- **Google SRE** distinguishes black-box from white-box monitoring and recommends paging on symptoms, what users see, rather than on causes ([*Site Reliability Engineering*, ch. 6, "Monitoring Distributed Systems"](https://sre.google/sre-book/monitoring-distributed-systems/)). This pattern applies that rule to stored LLM output, where the "user-visible symptom" is content that should exist and does not.
- **Data-quality tools** check stored data against declared expectations, independently of the jobs that wrote it: [dbt tests](https://docs.getdbt.com/docs/build/data-tests) and [Great Expectations](https://docs.greatexpectations.io/) for row counts, nulls and value ranges; data-observability products monitor table *freshness* and *volume* for the same reason.

We have not found a documented LLM system that monitors the domain output of its LLM calls this way rather than the calls themselves; the LLM-specific part (partial, plausible failure, and checks that share the prompt's assumptions) is grounded in Zeeguu.

## Notes

- **Two kinds of test.** One tests that the agent did something; the other tests that what the domain expects is there. The first is cheap to write and comes with every SDK and tracing tool; the second needs someone to say what "done" means for the domain, which is why it tends to be missing.
- **Relation to [LLM Content Validation Tracking](../llm-content-validation-tracking/).** That pattern marks how far each stored artifact can be trusted; this one counts whether the artifacts are there at all. A validation state that is never set is also a missing output, and can be checked the same way.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../model-bound-prompt/">← Model-Bound Prompt</a><a class="nav-next" href="../task-fusion/">Task Fusion →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BCheck+What+Should+Exist%5D+&labels=feedback%2Ccandidate&body=%2A%2ARe%3A%2A%2A+Check+What+Should+Exist%0A%2A%2ASection%3A%2A%2A+Candidate+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Fcheck-what-should-exist%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
