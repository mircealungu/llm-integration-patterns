---
layout: default
title: "Self-Hosted Slow-Path Inference"
permalink: /self-hosted-slow-path-inference/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../#candidate">Candidate</a>
</nav>


## Example

This pattern is not yet implemented, but it's planned. 

### The Plan

Overnight, a local LLM on a server that belongs to the system creator (e.g. a Mac Studio) drains a queue of slow, batchable jobs that today run against paid APIs (translation validation, example-sentence checking, CEFR pre-classification). 

- A worker on the Mac Studio polls the Zeeguu server over outbound HTTPS, runs each job on a local model (e.g. via Ollama), and posts the result back. 

- Anything not processed by a morning deadline falls back to the cloud API.

## Forces

API usage is the dominant variable cost of an LLM integration, yet a large share of the work is latency-insensitive: pre-computed, batched, offline (see [Pre-Computing Likely-Needed Results](../pre-computing-likely-needed-results/), [Prompt Amortization](../prompt-amortization/)). 

Capable open models now run on prosumer hardware (for example a Mac Studio with large unified memory) that is already owned and sits idle at night. For some tasks (e.g. example sentence generation) one does not need to use the latest online models. 

The obstacle is connectivity: such a machine usually sits behind NAT with no public IP, and opening inbound ports adds an attack surface its owner does not want.

## Solution

Run the latency-insensitive tasks on a local model on the owned hardware, and connect it outbound-only. The server enqueues jobs; a worker on the home machine polls that queue over HTTPS, runs each job on a local runtime, and posts the result back. The home machine exposes nothing: no public IP, no inbound ports, no listening service, only outbound calls to the server that already exists.

## Consequences

Trades API cost for sunk hardware and electricity, on the slow path only; real-time paths still use the cloud. Local model quality and throughput are lower, so the cloud API stays as a deadline-bound fallback (composes with [Fail-Fast Provider Chain](../fail-fast-provider-chain/) and [Escalate to the LLM](../escalate-to-the-llm/)): if the home worker has not drained the queue by the time results are needed, the cloud takes over. Availability is best-effort, since the machine may be asleep or off, so only work that can wait is eligible. Results carry a different model identity and should be recorded as such (composes with [LLM Output Provenance](../llm-output-provenance/)).

## Notes

- *Outbound-only is the key.* A pull-based worker exposes nothing and is the smallest attack surface. If the server must instead call the local model synchronously, a mesh VPN such as Tailscale (or a Cloudflare Tunnel) gives the server a route to the machine without port-forwarding or a public IP.
- *Owned versus volunteered.* Here the hardware belongs to the operator. A more ambitious variant accepts compute volunteered by third parties, which adds a trust dimension: outputs from untrusted workers must be validated before use (composes with [LLM Content Validation Tracking](../llm-content-validation-tracking/)) and may need cross-checking across workers.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../deterministic-postprocessing/">← Deterministic Postprocessing</a><a class="nav-next" href="../defensive-output-parsing/">Defensive Output Parsing →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BSelf-Hosted+Slow-Path+Inference%5D+&labels=feedback%2Ccandidate&body=%2A%2ARe%3A%2A%2A+Self-Hosted+Slow-Path+Inference%0A%2A%2ASection%3A%2A%2A+Candidate+Patterns%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fpatterns.mircealungu.com%2Fself-hosted-slow-path-inference%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
