# Anticipatory Precomputation

## Context

A user-facing feature needs an LLM result, but the model takes seconds while the user expects a response immediately. The possible user input is limited and *which* results a given user will need next is predictable from their past behaviour.

## Example

The vocabulary exercises a learner practices are built from the words they looked up while reading, each paired with a machine translation. At reading time an imperfect translation is low-stakes: the reader is only making sense of the text, and can pick a better option from the alternatives menu. But once the platform selects a word for the learner to *learn*, they will drill that word-translation pair over many days, so its correctness suddenly matters. A regular cron job looks ahead: it finds the words each learner is due to study next and validates them with an LLM, so that when the exercise module asks for new words, the vetted ones are ready straight away. If none are precomputed yet (the learner translated a few words and jumped straight into exercises), the validation runs in real time. 

**An even costlier instance: [audio lessons](../zeeguu/#audio-lessons).** Generating a personalized audio lesson is more expensive again: an LLM writes the lesson script (fed the learner's past lessons so a recurring topic, a "talking to a neighbour" lesson they have had before, comes back fresh rather than repeated), then text-to-speech synthesizes the audio, several seconds of work no learner should wait through. A nightly job pre-computes the next lessons for recently active learners (prioritized by how recently they practiced), on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. 

## Problem

How can we exploit user predictability so that LLM-quality results reach the user's critical path without waiting for the model to generate them?

## Forces

LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. Interactive users expect answers in real time (e.g., within 200ms). Depending on the prompt and the deployment configuration, an LLM can take multiple seconds to produce an answer. 

Precomputing answers based on the expected user input requires to store the LLM output so that the answers can be matched against the actual user input. Both the precomputation and the necessary storage space have a non-negligible cost. Ideally, the answer should be precomputed just before the user needs it so that it can be deleted immediately afterwards.

## Solution

Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs. If the prediction fails and the result is not ready, the user will need to wait for the LLM to generate it in real time. After they have been consumed by the user, no longer needed results should be removed.

## Consequences

- **Zero latency at request time.** The LLM's cost and multi-second latency are paid entirely off the hot path; when the user acts, the result is already waiting for them.
- **Precomputing pays for guesses that miss.** Tokens are spent on results that may never be requested, so the value depends on the accuracy of the behaviour model: a poor predictor wastes spend *and* still misses, wasting the user's time.
- **Needs a reliable "what" and "when" signal, plus a fallback.** It applies only where upcoming needs are predictable; cold, unexpected or mispredicted requests still need an on-demand path.

## Related Patterns

Composes with *Prompt Amortization*: offline results can be batched.

## Known Uses

- **[Yelp](https://engineeringblog.yelp.com/2025/02/search-query-understanding-with-LLMs.html)** pre-computes LLM query-understanding responses for high-frequency ("head") search queries into a key/value store, "caching (pre-computing) high-end LLM responses for only head queries", reaching 95% of traffic for review-highlight expansions, so the expensive model never runs on the hot path.
- **[Instacart](https://tech.instacart.com/building-the-intent-engine-how-instacart-is-revamping-query-understanding-with-llms-3ac8051ae7ac)**'s Intent Engine serves high-frequency search queries from a precomputed cache of LLM outputs, leaving only ~2% of queries to a real-time model.
- **[ColBERT](https://arxiv.org/abs/2004.12832)** (Khattab & Zaharia, SIGIR 2020) precomputes contextualized passage embeddings for the whole corpus offline, so query time runs only cheap late-interaction matching: the canonical "precompute the expensive representation ahead of time."

## Notes

- *Enablers (not instances).* Provider [batch / offline-inference](https://developers.openai.com/api/docs/guides/batch) endpoints are the infrastructure for computing LLM outputs in bulk off the hot path, not a use of the pattern.
