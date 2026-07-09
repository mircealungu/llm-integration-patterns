# Soft Invalidation of LLM Artifacts

## Context

An LLM-generated artifact has been stored and is reused as a cache, and it is also referenced from user-visible history. Then the prompt or model that produced it improves, so the stored version is now known to be suboptimal while old references still point at it.

## Example

When the prompt that generates [audio lesson](../zeeguu/#audio-lessons) scripts was improved, the ~900 stored `audio_lesson_meaning` rows (each caching one vocabulary item's generated audio) produced under the previous prompt were neither regenerated eagerly nor deleted: a learner who had already listened to one should not have its content change underneath them. Instead, each affected row received a `deprecated_at` timestamp, and the cache-lookup helper (`AudioLessonMeaning.find()`) was gated to skip deprecated rows. New daily lessons request a fresh row and trigger regeneration under the new prompt; existing daily lessons that already reference a deprecated row keep playing their old audio without breaking.

## Problem

When the generator improves, how can stored artifacts be refreshed without either paying to regenerate everything up front or breaking the past references that still point at the old ones?

## Forces

When a prompt or model improves, the obvious responses each have a serious drawback:

- *Regenerate everything eagerly*: expensive, floods generation queues if affected rows number in the thousands, and pays for content that may never be re-requested.
- *Delete the stale rows*: breaks any downstream object that references them by id (history, analytics, user-visible past sessions).
- *Leave the stale rows in place and accept future reuse*: silently propagates the old, known-suboptimal quality.

None of these are good defaults for production systems where LLM-generated artifacts are referenced from user-visible history and are also targets for reuse.

## Solution

Mark stale rows as deprecated rather than mutating or removing them. Gate the cache-lookup / reuse path to skip deprecated rows, forcing fresh generation on next demand. Existing references to a deprecated row remain valid (the row keeps its content for historical playback), but no new consumer picks it up. For this to preserve history, key each stored artifact by its own row id, not by the source it describes, so a regenerated row produces a new file rather than overwriting the deprecated one (see the note). Regeneration cost is paid lazily, amortized over normal access patterns, and only for content that is actually requested again.

## Consequences

- **Cost is lazy and history stays intact.** Regeneration is paid only for content requested again, and old references keep resolving to their original artifact, so user-visible history does not break.
- **Old versions linger until next demand.** A replay hears the old quality until something triggers regeneration, and the deprecation flag has to reach every downstream cache to be effective.


## Known Uses

- **[`stale-while-revalidate`](https://datatracker.ietf.org/doc/html/rfc5861)** (IETF RFC 5861) is the same mechanic in HTTP caching: keep a stale entry usable and revalidate it lazily on next demand rather than eagerly regenerating.
- The **[soft-delete / tombstone](https://brandur.org/soft-deletion)** database idiom marks a row with a timestamp and gates every read (`WHERE deleted_at IS NULL`), so the row stays intact for existing references but drops out of the active path: structurally identical to a `deprecated_at` gate.

Note that both the above are *analogues and not exact instances.* Both capture the mechanism, but we did not find a documented LLM system that combines mark-deprecated + gate-reuse + **keep-old-rows-resolvable-for-user-history** + lazy regeneration; the history-preservation facet appears novel, so we present it as our own contribution, grounded in Zeeguu.

## Notes

- **The mechanism is soft-delete; the trigger is what makes it LLM-specific.** A soft-delete retires a record someone chose to remove. Here nothing is deleted and nothing is wrong: the row is retired from reuse only because the prompt or model that produced it improved, so its once-good output is now merely suboptimal. Unlike a cached database row, a stored LLM artifact goes stale on its own as its generator gets better. In Zeeguu the trigger was a prompt rewrite, the common case, since prompts change more often than models.
- This pattern is forward-only: it gates *reuse*, not *playback*. A user replaying an old lesson hears the old (lower-quality) version. That is usually preferable to a silent content swap mid-history.
- Composes naturally with *LLM Output Provenance*: provenance answers "which rows are stale?", soft invalidation answers "what do I do with them once I know?".
- **Name the stored file after the row, not after what it describes.** The history guarantee needs each regeneration to produce a *new* file rather than overwrite the old one. In Zeeguu this broke at first: each lesson's audio was stored under its `meaning_id` (the vocabulary item the lesson teaches), which stays the same when the lesson is regenerated. So regenerating a deprecated lesson wrote the new audio to the same path and silently replaced the recording that old daily lessons still played. The fix was to key each file by the row's own id (`audio_lesson_meaning.id`), so every generation gets its own file and the deprecated one survives for playback. 
