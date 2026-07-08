# Slow-Path Inference

## Context

A user-facing app makes many LLM calls, but only some are on a user's critical path. The rest (pre-computation, batch classification, offline validation) are latency-insensitive. Latency-tolerant execution costs far less: an asynchronous batch endpoint runs the *same* model at roughly half price, and a cheaper provider or owned hardware less still.

## Example

Zeeguu runs the pattern in two places.

**Two model tiers for one task.** [Article simplification](../zeeguu/#article-simplification) takes two paths, chosen by whether a reader is waiting.

1. When a learner opens an article that has not been simplified yet, the on-demand simplification runs on a fast model (Anthropic Haiku, the "real-time text-simplification" path), so the reader is waiting as little as possible. 
2. The bulk, ahead-of-time simplification of the [crawled article feed](../zeeguu/#crawling), which no user is blocking on, is pinned to the cheaper, slower DeepSeek model (`crawl_round_robin(..., simplification_provider='deepseek')`); the [CEFR](../zeeguu/#cefr-levels) (reading-difficulty) assessment done during crawling is likewise DeepSeek-only, "for consistency with batch crawling".

Same task, two model tiers, selected by latency-sensitivity rather than by the task itself.

**An owned machine as the slow path.** Zeeguu's latency-insensitive LLM work (CEFR assessment, translation validation, [meaning](../zeeguu/#the-learner-model)-frequency classification, ahead-of-time example generation) all bills against metered APIs, yet none of it is on a user's critical path. A single owned machine (a Mac Studio running Ollama) drains that entire queue overnight on a local model at zero per-token cost, with the cloud API as a deadline-bound fallback for whatever is not done by morning. It moves a whole category of spend off the metered bill onto hardware that already sits idle at night.

## Problem

How can the premium cost of the real-time model be avoided on the large share of LLM work that no user is waiting for?

## Forces

- In a user-facing app, a large share of LLM work is *not* on a user's critical path: content pre-computed for later, batch classification, offline validation. Only a fraction is real-time.
- The real-time path must pay for low latency: a fast, often premium model. Paying those same rates for work no one is waiting on is wasteful.
- Latency-tolerant execution (a batch endpoint, a cheaper provider, owned hardware) is far cheaper than a premium real-time model, and fine for work no user is waiting on as long as its output is still good enough for the job. On the real-time path it is unacceptable.
- A single model for everything forces a bad compromise: premium cost on all of it, or premium latency and quality on none.

## Solution

Split inference into a **fast path** and a **slow path**, and route each task by whether a user is blocking on the result, not by what the task is.

- **Fast path**: real-time, user-facing work runs on a low-latency model.
- **Slow path**: deferrable work (pre-computation, batch, offline) runs on the cheapest adequate path.

Realize the slow path with whatever is cheapest for the work, in rough order of adoption cost:

- **A cheaper model.** The lightest realization: point the batch path at a cheaper provider. Zeeguu uses DeepSeek for batch simplification and crawl-time CEFR assessment while the reader-facing path stays on Anthropic Haiku: the same call behind a different endpoint.
- **A provider batch API.** Asynchronous endpoints (OpenAI Batch, Anthropic Message Batches) run at roughly half price for up to ~24h turnaround, with no infrastructure to own.
- **Self-hosted local inference.** A local model on owned hardware draining an overnight queue at zero per-token cost: the largest saving, the most infrastructure (the owned-machine example above).

## Consequences

Slow-path output is much cheaper and best-effort in timing, so only latency-insensitive work is eligible, and the fast path (or cloud) stays as a deadline-bound fallback (composes with *Fail-Fast Provider Chain* and *Escalate to the LLM*). Route only work whose slow-path result will actually be accepted: output that is rejected and recomputed on the fast path costs *more* than never taking the slow path at all. Results carry a different model identity and should be recorded as such (composes with *LLM Output Provenance*); untrusted slow-path output may need validation (composes with *LLM Content Validation Tracking*). Which model runs on which path should live in one place (composes with *Centralized Model Selection*), so re-tiering a feature is a one-line change.

## Notes

- *The owned machine is a pull worker.* It has no public IP and is not on the server's network, so it connects outbound-only: the server enqueues jobs, the machine polls over HTTPS and posts results back. A deployment detail, not an LLM concern.
- *Route by latency-sensitivity, not by task.* The same task, article simplification, runs on both paths; what selects the path is whether a human is blocked, not what is being computed. That is what separates this pattern from simply using a cheap model for cheap tasks.

## Known Uses

This pattern is the LLM specialization of the long-standing **batch vs. online inference** split in production ML serving: an offline, high-throughput, latency-tolerant tier running alongside a real-time serving tier. That split is the established instance-class; what is specific here is tiering the *same* task across cheaper and premium *LLM* endpoints by whether a user is waiting.

- **[Apple Intelligence + Private Cloud Compute](https://security.apple.com/blog/private-cloud-compute/)** is a shipped tiered-inference system (an on-device model for immediate requests, a heavier model on fallback), though it tiers by *capability* rather than latency-tolerance, and inverts the economics (local is the fast path).
- *Enablers, not instances.* The mechanisms that make a cheap slow path practical are widely used, but each supplies only the slow path, not the tiering *decision*: provider batch APIs at ~half price ([OpenAI Batch](https://platform.openai.com/docs/guides/batch), [Anthropic Message Batches](https://docs.claude.com/en/docs/build-with-claude/batch-processing)), local runtimes on owned hardware ([Ollama](https://ollama.com/)), and outbound-only workers ([GitHub Actions self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/communicating-with-self-hosted-runners)). We did not find a documented LLM application that names this same-task, latency-tiered split: Zeeguu is our instance, and the batch/online ML practice its lineage.
