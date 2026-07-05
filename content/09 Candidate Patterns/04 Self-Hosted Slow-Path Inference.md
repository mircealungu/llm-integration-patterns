# Self-Hosted Slow-Path Inference

## Example (planned)

Overnight, a local LLM on a server that belongs to the system creator (e.g. a Mac Studio) drains a queue of slow, batchable jobs that today run against paid APIs (translation validation, example-sentence checking, CEFR pre-classification). 

- A worker on the Mac Studio polls the Zeeguu server over outbound HTTPS, runs each job on a local model (e.g. via Ollama), and posts the result back. 

- Anything not processed by a morning deadline falls back to the cloud API.

## Forces

API usage is the dominant variable cost of an LLM integration, yet a large share of the work is latency-insensitive: pre-computed, batched, offline (see *Pre-Computing Likely-Needed Results*, *Prompt Amortization*). 

Capable open models now run on prosumer hardware (for example a Mac Studio with large unified memory) that is already owned and sits idle at night. For some tasks (e.g. example sentence generation) one does not need to use the latest online models. 

The obstacle is connectivity: such a machine usually sits behind NAT with no public IP, and opening inbound ports adds an attack surface its owner does not want.

## Solution

Run the latency-insensitive tasks on a local model on the owned hardware, and connect it outbound-only. The server enqueues jobs; a worker on the home machine polls that queue over HTTPS, runs each job on a local runtime, and posts the result back. The home machine exposes nothing: no public IP, no inbound ports, no listening service, only outbound calls to the server that already exists.

## Consequences

Trades API cost for sunk hardware and electricity, on the slow path only; real-time paths still use the cloud. Local model quality and throughput are lower, so the cloud API stays as a deadline-bound fallback (composes with *Fail-Fast Provider Chain* and *Escalate to the LLM*): if the home worker has not drained the queue by the time results are needed, the cloud takes over. Availability is best-effort, since the machine may be asleep or off, so only work that can wait is eligible. Results carry a different model identity and should be recorded as such (composes with *LLM Output Provenance*).

## Notes

- *Outbound-only is the key.* A pull-based worker exposes nothing and is the smallest attack surface. If the server must instead call the local model synchronously, a mesh VPN such as Tailscale (or a Cloudflare Tunnel) gives the server a route to the machine without port-forwarding or a public IP.
- *Owned versus volunteered.* Here the hardware belongs to the operator. A more ambitious variant accepts compute volunteered by third parties, which adds a trust dimension: outputs from untrusted workers must be validated before use (composes with *LLM Content Validation Tracking*) and may need cross-checking across workers.

## Known Uses

- **[Ollama / llama.cpp on Apple Silicon](https://daily.dev/blog/running-llms-locally-ollama-llama-cpp-self-hosted-ai-developers/)** are routinely used to run extraction/summarization batch jobs overnight on an owned Mac with no per-token cost and no rate limits — the slow-path use directly.
- **[Apple Intelligence + Private Cloud Compute](https://security.apple.com/blog/private-cloud-compute/)** ships a local-first / cloud-fallback split, escalating to a larger cloud model only when needed — the same local+cloud division of labour, though *inverted*: Apple uses local as the fast path, this pattern uses it as the slow/cheap path.
- **[GitHub Actions self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/communicating-with-self-hosted-runners)** are the outbound-only pull-worker mechanism: the runner long-polls over HTTPS so "only an outbound connection… is required," exposing no inbound ports — exactly the NAT-traversal design proposed here.
- *Novel composition.* Each mechanism is well-attested independently; combining local slow-path + cloud deadline-fallback + outbound-only worker into one LLM system is this candidate's contribution.

> [!draft]- Notes to explore
> - batch processing?
> - priority queues?
> - I kind of assume that we call APIs in many places where I talk about LLMs
> - business / engineering / design? another category
