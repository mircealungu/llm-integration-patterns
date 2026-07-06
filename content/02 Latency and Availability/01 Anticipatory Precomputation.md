# Anticipatory Precomputation

## Context

A user-facing feature needs an LLM result, but the model takes seconds while the user expects a response in well under one — and *which* results a given user will need next is predictable from their behaviour.

## Example

When a learner reads a text and asks for a translation, the most important thing is to return a good-enough translation **fast**. The system can afford an imprecise translation while the reader is quickly making sense of a text, but it cannot afford to have learners repeatedly *practice* an imprecise one.

The vocabulary exercises are built from the words a learner has looked up, so those pairs (from Google or Azure Translate) must be verified before they enter an exercise. Verifying with an LLM is too slow to run at the moment a learner opens a session. So a regular cron job looks ahead: it identifies the words a learner is due to study next and pre-computes the LLM verification, so that when the session starts the words are already vetted and ready, with no LLM call on the critical path.

**An even costlier instance: audio lessons.** Generating a personalized audio lesson is more expensive again: an LLM writes the lesson script, then text-to-speech synthesizes the audio, several seconds of work no learner should wait through. A nightly job pre-computes the next lessons for recently active learners (prioritized by how recently they practiced), on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. 

## Problem

How do you put an LLM-quality result on the user's critical path without making them wait for the model — given that you can often predict what they will need?

## Forces

LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real-time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

## Solution

Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs.

## Consequences

- **Zero latency at request time.** The LLM's cost and multi-second latency are paid entirely off the hot path; when the user acts, the result is already waiting.
- **You pay for guesses that miss.** Precomputing spends tokens on results that may never be requested, so the value depends on the accuracy of the behaviour model — a poor predictor wastes spend *and* still misses.
- **Needs a reliable "what" and "when" signal, plus a fallback.** It applies only where upcoming needs are predictable; cold or mispredicted requests still need an on-demand path. Composes with *Prompt Amortization* (offline results can be batched).

## Known Uses

- **[Yelp](https://engineeringblog.yelp.com/2025/02/search-query-understanding-with-LLMs.html)** pre-computes LLM query-understanding responses for high-frequency ("head") search queries into a key/value store — "caching (pre-computing) high-end LLM responses for only head queries" — reaching 95% of traffic for review-highlight expansions, so the expensive model never runs on the hot path.
- **[Instacart](https://tech.instacart.com/building-the-intent-engine-how-instacart-is-revamping-query-understanding-with-llms-3ac8051ae7ac)**'s Intent Engine serves high-frequency search queries from a precomputed cache of LLM outputs, leaving only ~2% of queries to a real-time model.
- **[ColBERT](https://arxiv.org/abs/2004.12832)** (Khattab & Zaharia, SIGIR 2020) precomputes contextualized passage embeddings for the whole corpus offline, so query time runs only cheap late-interaction matching — the canonical "precompute the expensive representation ahead of time."
- *Enabler, not instance.* Provider [batch / offline-inference](https://developers.openai.com/api/docs/guides/batch) endpoints are the infrastructure for computing LLM outputs in bulk off the hot path — not a use of the pattern.
