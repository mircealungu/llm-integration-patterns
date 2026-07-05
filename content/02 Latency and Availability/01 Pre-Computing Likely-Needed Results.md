# Pre-Computing Likely-Needed Results

## Example

When a learner reads a text and asks for a translation, the most important thing is to return a good-enough translation **fast**. The system can afford an imprecise translation while the reader is quickly making sense of a text, but it cannot afford to have learners repeatedly *practice* an imprecise one.

The vocabulary exercises are built from the words a learner has looked up, so those pairs (from Google or Azure Translate) must be verified before they enter an exercise. Verifying with an LLM is too slow to run at the moment a learner opens a session. So a regular cron job looks ahead: it identifies the words a learner is due to study next and pre-computes the LLM verification, so that when the session starts the words are already vetted and ready, with no LLM call on the critical path.

**An even costlier instance: audio lessons.** Generating a personalized audio lesson is more expensive again: an LLM writes the lesson script, then text-to-speech synthesizes the audio, several seconds of work no learner should wait through. A nightly job pre-computes the next lessons for recently active learners (prioritized by how recently they practiced), on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. 

## Forces

LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real-time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

## Solution

Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.

## Known Uses

- **[ColBERT](https://arxiv.org/abs/2004.12832)** (Khattab & Zaharia, SIGIR 2020) precomputes contextualized passage embeddings for the whole corpus offline, so query time runs only cheap late-interaction matching — the canonical "precompute the expensive representation ahead of time."
- Provider **[batch / offline-inference](https://developers.openai.com/api/docs/guides/batch)** pipelines are the enabling infrastructure for computing LLM outputs in bulk off the hot path.
- *Honest gap.* We did not find a well-documented production system that precomputes *user-facing* LLM answers on a schedule the way Zeeguu does; the closest analogues are the materialized-view / prefetching principle and the offline-index precomputation above.
