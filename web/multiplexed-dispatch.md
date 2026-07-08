---
layout: default
title: "Multiplexed Dispatch"
permalink: /multiplexed-dispatch/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../latency-and-availability/">Latency and Availability</a>
</nav>


## Context

Several models or providers can produce the same result at different and individually *variable* latencies, and the request sits on the user's critical path where a slow tail hurts the experience.

## Example

Zeeguu races calls on its real-time paths, where a waiting user feels every slow response.

- **On-demand simplification.** When a reader opens an article that has to be simplified right now, the request goes to two models at once; the first response is rendered, and the slower one is kept as an alternative the reader can switch to. Racing collapses the latency tail on the one path where a human is blocked, and it doubles as failover: if one provider is slow or down, the other still answers. The redundant cost is affordable because on-demand simplification is rare next to the crawled batch.
- **Translation.** Real-time translations are likewise dispatched to several providers in parallel; the first response is used and the rest are surfaced as alternative translations.

## Problem

How can worst-case latency stay low when any single provider can be intermittently slow?

## Forces

Multiple LLM providers offer similar capabilities but with varying latency. When speed matters for user experience, relying on a single provider creates a bottleneck.

## Solution

Dispatch the same request to multiple providers simultaneously and use the first response that arrives. To cap the redundant cost, race only the few providers that have historically been fastest rather than all of them.

This composes with **live retrieval**: when a user is unsure of a translation and asks for alternatives, the UI shows the already-raced cached results immediately, then fetches more on demand, streaming them in as they arrive.

## Consequences

- **Latency tracks the fastest responder, not the average.** Racing collapses the slow tail: worst-case latency becomes the *best* of N providers rather than any one's.
- **N× the cost for one used result**: every dispatch bills its own tokens. (Zeeguu recoups some of this by keeping the losing responses as alternatives; see the note below.)
- **It doubles as failover.** Each racer is a full, independent attempt, so a provider that errors or hangs simply loses the race instead of failing the request: availability comes for free, where [Fail-Fast Provider Chain](../fail-fast-provider-chain/) buys it with an explicit fallback.

## Note

In itself this is not LLM-specific. It is the *hedged requests* pattern from distributed systems (Dean and Barroso, *The Tail at Scale*, CACM 2013), also known as request racing or tied requests. Two things give it an LLM flavour here.
1. First, the hedge is across independent, competing vendors (Anthropic, DeepSeek, Google Translate) rather than replicas of a single service. 
2. Second, each redundant call costs real money per token, so the losing responses are not thrown away: they are kept and surfaced to future readers of the same text as alternative translations, turning the redundant work into a feature.

## Known Uses

- **[Hedged requests](https://cacm.acm.org/research/the-tail-at-scale/)** (Dean & Barroso, "The Tail at Scale," CACM 2013) are the classical ancestor: send a duplicate to another replica after a latency threshold, take the first, cancel the rest, cutting BigTable p99 from 1800ms to 74ms at ~2% extra load.
- General infrastructure ships it: **[gRPC `hedgingPolicy`](https://grpc.io/docs/guides/request-hedging/)** and **[Polly](https://www.pollydocs.org/strategies/hedging)** (.NET) race concurrent copies and take the first response.
- *Honest gap / opportunity.* We could not find a major LLM gateway that ships true provider *racing* as a first-class feature; most do sequential fallback (see [Fail-Fast Provider Chain](../fail-fast-provider-chain/)) or learned single-model routing. Zeeguu's parallel dispatch, across translation providers and across two models for on-demand simplification, appears to be an under-adopted transfer of the hedging idea to LLMs.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../fail-fast-provider-chain/">← Fail-Fast Provider Chain</a><a class="nav-next" href="../rent-then-build/">Rent, Then Build →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BMultiplexed+Dispatch%5D+&labels=feedback%2Clatency-and-availability&body=%2A%2ARe%3A%2A%2A+Multiplexed+Dispatch%0A%2A%2ASection%3A%2A%2A+Latency+and+Availability%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fmultiplexed-dispatch%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
