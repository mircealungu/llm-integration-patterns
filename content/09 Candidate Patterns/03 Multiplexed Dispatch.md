# Multiplexed Dispatch

## Context

Several providers offer the same capability (e.g. translation) at different and individually *variable* latencies, and the request sits on the user's critical path where a slow tail hurts.

## Example

Real-time translations are dispatched to multiple translation providers in parallel. The first response is used, and the rest are saved for when the user asks for alternatives.

## Problem

How can worst-case latency stay low when any single provider can be intermittently slow?

## Forces

Multiple LLM providers offer similar capabilities but with varying latency. When speed matters for user experience, relying on a single provider creates a bottleneck.

## Solution

Dispatch the same request to multiple providers simultaneously and use the first response that arrives. To cap the redundant cost, race only the few providers that have historically been fastest rather than all of them.

This composes with **live retrieval**: when a user is unsure of a translation and asks for alternatives, the UI shows the already-raced cached results immediately, then fetches more on demand, streaming them in as they arrive.

## Consequences

- **Latency tracks the fastest responder, not the average.** Racing collapses the slow tail: worst-case latency becomes the *best* of N providers rather than any one's.
- **N× the cost for one used result**: every dispatch bills its own tokens. (Zeeguu recoups some of this by keeping the losing responses as alternative translations; see the note below.)

## Note

In itself this is not LLM-specific. It is the *hedged requests* pattern from distributed systems (Dean and Barroso, *The Tail at Scale*, CACM 2013), also known as request racing or tied requests. Two things give it an LLM flavour here.
1. First, the hedge is across independent, competing vendors (Anthropic, DeepSeek, Google Translate) rather than replicas of a single service. 
2. Second, each redundant call costs real money per token, so the losing responses are not thrown away: they are kept and surfaced to future readers of the same text as alternative translations, turning the redundant work into a feature.

## Status

Included as a candidate. This is the general *hedged requests* pattern applied to translation providers (a mix that includes non-LLM engines such as Google Translate), rather than a distinctly LLM-specific technique. Racing calls across LLMs specifically, for the cases that most need low latency, is plausible but not something Zeeguu currently does.

## Known Uses

- **[Hedged requests](https://cacm.acm.org/research/the-tail-at-scale/)** (Dean & Barroso, "The Tail at Scale," CACM 2013) are the classical ancestor: send a duplicate to another replica after a latency threshold, take the first, cancel the rest, cutting BigTable p99 from 1800ms to 74ms at ~2% extra load.
- General infrastructure ships it: **[gRPC `hedgingPolicy`](https://grpc.io/docs/guides/request-hedging/)** and **[Polly](https://www.pollydocs.org/strategies/hedging)** (.NET) race concurrent copies and take the first response.
- *Honest gap / opportunity.* We could not find a major LLM gateway that ships true provider *racing* as a first-class feature; most do sequential fallback (see *Fail-Fast Provider Chain*) or learned single-model routing. Zeeguu's parallel dispatch across translation providers appears to be an under-adopted transfer of the hedging idea to LLMs.
