# Anticipatory Precomputation

*Generate the LLM results users will likely need before they ask.*

## Context

A user-facing feature needs LLM results that are slow to compute, but what each user is likely to need next is predictable.

## Problem

The user expects the result at once. How can a feature use LLM results without making the user wait for the model?

## Problem in Zeeguu

The vocabulary exercises a learner practices are built from the words they looked up while reading, each paired with a machine translation. At reading time an imperfect translation is low-stakes: the reader is only making sense of the text, and can pick a better option from the alternatives menu. But once the platform selects a word for the learner to *learn*, they will drill that word-translation pair over many days, so its correctness suddenly matters: a learner should not drill a wrong translation. Checking with an LLM whether a word–translation pair is correct and worth learning takes seconds that an exercise screen would rather not wait for.

Generating an [audio lesson](../zeeguu/#audio-lessons) takes much longer than checking a translation. The LLM writes a long lesson script, from a long prompt: so that a recurring topic, a "talking to a neighbour" lesson the learner has had before, comes back fresh rather than repeated, the prompt tells the model what the learner has already heard in past lessons. Text-to-speech then turns the script into audio. Together this takes many seconds, far more than a learner should wait.

## Forces

- **Users expect the result at once.** A real-time interface is expected to answer in about 200ms, and an LLM takes seconds. *(pulls toward having the answer before the user asks)*
- **Work nobody asks for is wasted.** A result made for a need that never comes is paid for and never used. *(pulls toward generating only on request)*
- **Results made early must be stored.** A result has to be kept from the moment it is generated to the moment it is asked for: bytes for a validated translation, megabytes for an audio lesson, for every user and every result ahead. *(pulls toward generating only on request)*

## Solution

Predict what each user will need next, generate those LLM results offline (for example, in a scheduled job), and store them, so they are ready the moment the user asks. Keep an on-demand path for requests nobody predicted, so a miss degrades to a normal wait rather than a failure.

The prediction usually comes from one of three places:

- **A schedule the system controls.** When the system itself decides what comes next, such as which words a learner studies tomorrow, it knows the need in advance.
- **Habit.** A user who was active recently is likely to come back, so their next result is worth preparing.
- **Popularity.** Some requests recur across users, such as the most frequent search queries, so their results can be prepared once for everyone.

![[anticipatory-precomputation-diagram.svg]]
*Ahead of time, the LLM answers the requests the system predicts and the answers are stored. A predicted request is then served from the store with no LLM call; an unpredicted one falls back to an on-demand call, a normal wait rather than a failure.*

## Solution in Zeeguu

Zeeguu uses the first two sources:

- **Schedule: validated translations.** A regular cron job finds the words each learner is due to study next and validates them with an LLM, so when the exercise module asks for new words, the vetted ones are ready straight away. If none are precomputed yet (the learner translated a few words and jumped straight into exercises), the validation runs on demand.
- **Habit: audio lessons.** A nightly job generates the next lessons for recently active learners, those who practiced most recently first, on the assumption that someone who has been studying will be back for the next one. When they return, the lesson is already waiting. Only a learner who switches to a new topic waits, while that day's first lesson on it is generated on demand.

## Consequences

- **No wait for the model.** The LLM's cost and its seconds of latency are paid off the user's path; when the user acts, a predicted result is already there.
- **Some of the work is wasted.** How much depends on the prediction: a schedule the system controls wastes little, while habit and popularity pay for every guess that misses.
- **Storage grows with how far ahead the system looks.** Precomputing for more users, or further ahead, keeps more results waiting.
- **Two paths to maintain.** The on-demand path stays for requests nobody predicted, so the feature is built for both.

## Known Uses

- **[Yelp](https://engineeringblog.yelp.com/2025/02/search-query-understanding-with-LLMs.html)** precomputes LLM query-understanding responses for high-frequency ("head") search queries into a key/value store, "caching (pre-computing) high-end LLM responses for only head queries", reaching 95% of traffic for review-highlight expansions, so the expensive model never runs on the critical path.
- **[Instacart](https://tech.instacart.com/building-the-intent-engine-how-instacart-is-revamping-query-understanding-with-llms-3ac8051ae7ac)**'s Intent Engine serves high-frequency search queries from a precomputed cache of LLM outputs, leaving only ~2% of queries to a real-time model.

## Related Patterns

*Hot-Path Result Caching* also serves stored LLM results, but stores an answer only after it was first requested; this pattern computes it before anyone asks. Yelp's own description, "caching (pre-computing)", sits between the two. Precomputed work is offline, so it can be batched with *Prompt Amortization*. The same move appears outside generation: **[ColBERT](https://arxiv.org/abs/2004.12832)** (Khattab & Zaharia, SIGIR 2020) precomputes passage embeddings for a whole corpus, so a query runs only cheap matching.
