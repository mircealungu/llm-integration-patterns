# Possible Other Patterns

## Temperature as Task Selector

**Example (Zeeguu):** Translation validation uses temperature 0 for deterministic yes/no judgments. Audio lesson script generation uses temperature 0.8 to produce varied, natural-sounding dialogues. The same model serves both purposes with different configuration.

**Forces:** LLMs exhibit different behaviors at different temperature settings. Classification and validation tasks benefit from deterministic outputs (low temperature), while creative generation benefits from variety (higher temperature). Using a single temperature for all tasks either sacrifices reliability or creativity.

**Solution:** Systematically vary temperature based on task type. Use temperature 0–0.3 for tasks requiring consistency (validation, classification, structured extraction). Use temperature 0.7–1.0 for tasks requiring creativity (dialogue generation, example variety).

**Note:** This pattern acknowledges that a single LLM can behave as multiple "virtual components" depending on configuration: deterministic validator vs. creative generator.

## Soft Invalidation of LLM Artifacts

**Example (Zeeguu):** When the prompt that generates audio lesson scripts was improved, the ~900 stored `audio_lesson_meaning` rows produced under the previous prompt were neither regenerated eagerly nor deleted. Instead, each affected row received a `deprecated_at` timestamp, and the cache-lookup helper (`AudioLessonMeaning.find()`) was gated to skip deprecated rows. New daily lessons request a fresh row and trigger regeneration under the new prompt; existing daily lessons that already reference a deprecated row keep playing their old audio without breaking.

**Forces:** When a prompt or model improves, the obvious responses each have a serious drawback:
- *Regenerate everything eagerly*: expensive, floods generation queues if affected rows number in the thousands, and pays for content that may never be re-requested.
- *Delete the stale rows*: breaks any downstream object that references them by id (history, analytics, user-visible past sessions).
- *Leave the stale rows in place and accept future reuse*: silently propagates the old, known-suboptimal quality.

None of these are good defaults for production systems where LLM-generated artifacts are referenced from user-visible history and are also targets for reuse.

**Solution:** Mark stale rows as deprecated rather than mutating or removing them. Gate the cache-lookup / reuse path to skip deprecated rows, forcing fresh generation on next demand. Existing references to a deprecated row remain valid (the row keeps its content for historical playback), but no new consumer picks it up. Regeneration cost is paid lazily, amortized over normal access patterns, and only for content that is actually requested again.

**Notes:**
- This pattern is forward-only: it gates *reuse*, not *playback*. A user replaying an old lesson hears the old (lower-quality) version. That is usually preferable to a silent content swap mid-history.
- Works best when content has a clear "next access triggers regeneration" entry point. If consumers cache aggressively further downstream, the deprecation flag has to propagate to those layers too.
- Composes naturally with *LLM Output Provenance*: provenance answers "which rows are stale?", soft invalidation answers "what do I do with them once I know?".
- **Prerequisite: artifact identity must follow the row, not the upstream key.** If the on-disk artifact (audio file, image, embedding) is named after the *source identity* (e.g. `meaning_id`) rather than the *row identity* (e.g. `audio_lesson_meaning.id`), the regenerated row's artifact overwrites the deprecated row's artifact on the same path, defeating the historical-playback guarantee. Zeeguu encountered this concretely: meaning-lesson audio files were keyed by `meaning_id`, so regeneration silently replaced the audio referenced by old daily lessons. A separate change re-keyed those files by row id to make Soft Invalidation safe. This small structural requirement may deserve being a pattern in its own right (working title: *artifact identity = row identity*).

## Deterministic Postprocessing

**Example (Zeeguu):** LLM-simplified article summaries consistently ended with a Unicode ellipsis (`…`), making every home-card preview read as an unfinished sentence. One option was to add a "do not end with ellipsis" instruction to the simplification prompt; the chosen option was a five-line regex stripping any trailing `…` or `..+` at serialization time. The regex handles every case at 100%, including the ~60k pre-existing rows in the database that no prompt change could retroactively touch.

**Forces:** When LLM output has a deterministic formatting defect (a stable trailing string, a known preamble, leaked markdown in a plain-text field, trailing whitespace), the obvious instinct is to fix it in the prompt. But:
- Prompt compliance is probabilistic; the same constraint in code is 100%.
- Prompt tokens cost money on every call and can distract the model from the actual semantic task.
- Prompt changes do not affect rows already in the database.
- Code is testable and reviewable; prompt instructions are not.

**Solution:** Enforce deterministic constraints in code, at the post-processing or serialization boundary. Reserve prompt instructions for things that genuinely require model judgment.

**Notes:** The boundary between "deterministic" and "semantic" is the test. *Strip a trailing `…`*: deterministic, do it in code. *Don't mention the user's name*: semantic, the model has to enforce. When the deterministic rule list grows long, that is itself a signal that the task is poorly scoped, not that the prompt needs more rules.

## Self-Hosted Slow-Path Inference

**Example (Zeeguu, prospective):** This pattern is not yet implemented. The plan: overnight, a Mac Studio at home drains a queue of slow, batchable jobs that today run against paid APIs (translation validation, example-sentence checking, CEFR pre-classification). A worker on the Mac polls the Zeeguu server over outbound HTTPS, runs each job on a local model (e.g. via Ollama), and posts the result back. Anything not processed by a morning deadline falls back to the cloud API.

**Forces:** API usage is the dominant variable cost of an LLM integration, yet a large share of the work is latency-insensitive: pre-computed, batched, offline (see *Pre-Computing Likely-Needed Results*, *Prompt Amortization*). Capable open models now run on prosumer hardware (for example a Mac Studio with large unified memory) that is already owned and sits idle at night. The obstacle is connectivity: such a machine usually sits behind NAT with no public IP, and opening inbound ports adds an attack surface its owner does not want.

**Solution:** Run the latency-insensitive tasks on a local model on the owned hardware, and connect it outbound-only. The server enqueues jobs; a worker on the home machine polls that queue over HTTPS, runs each job on a local runtime, and posts the result back. The home machine exposes nothing: no public IP, no inbound ports, no listening service, only outbound calls to the server that already exists.

**Consequences:** Trades API cost for sunk hardware and electricity, on the slow path only; real-time paths still use the cloud. Local model quality and throughput are lower, so the cloud API stays as a deadline-bound fallback (composes with *Fail-Fast Provider Chain* and *Escalate to the LLM*): if the home worker has not drained the queue by the time results are needed, the cloud takes over. Availability is best-effort, since the machine may be asleep or off, so only work that can wait is eligible. Results carry a different model identity and should be recorded as such (composes with *LLM Output Provenance*).

**Notes:**

- *Outbound-only is the key.* A pull-based worker exposes nothing and is the smallest attack surface. If the server must instead call the local model synchronously, a mesh VPN such as Tailscale (or a Cloudflare Tunnel) gives the server a route to the machine without port-forwarding or a public IP.
- *Owned versus volunteered.* Here the hardware belongs to the operator. A more ambitious variant accepts compute volunteered by third parties, which adds a trust dimension: outputs from untrusted workers must be validated before use (composes with *LLM Content Validation Tracking*) and may need cross-checking across workers.
