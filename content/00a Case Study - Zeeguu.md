# Case Study: Zeeguu

Zeeguu is an open-source language learning platform built around the idea that learners benefit most from engaging with comprehensive and authentic content in their target language. Rather than relying on artificial textbook texts and exercises, Zeeguu helps users find real articles (news, blog posts, and other web content) tailored to both 1\) their *level* and 2\) their *interests*. Then based on the words they don't understand generates personalized vocabulary exercises and audio lessons. 

The platform recommends articles in the learner's target language based on their proficiency and reading preferences, making it **easy to find material that is both engaging and appropriately challenging**. If a text is personally compelling but too difficult, Zeeguu simplifies it to the learner's level using LLMs. 

When users encounter unfamiliar words or phrases while reading, they can get contextual translations on the fly from several translation providers, so the reading experience remains fluid and uninterrupted. One alternative is provided by a state-of-the-art LLM, offering a more contextually nuanced option. 

Every translation a user requests is logged by the system, which over time builds a **detailed model of the learner's vocabulary knowledge**, tracking which words they know, which ones they struggle with, and how well they've retained previously encountered vocabulary.

Based on this evolving learner model, Zeeguu **generates interactive vocabulary exercises and audio lessons** that focus on the words that matter most for each individual learner, rather than following a generic curriculum. The exercises use the context in which the word was originally encountered, based on the assumption that if the original text was compelling to the learner, examples drawn from it will be too. 

In essence, Zeeguu unifies reading, translation, learner modeling, and practice into a coherent pipeline, with the learner's own reading interests as the primary driver. 

## The Pieces

A handful of Zeeguu-specific concepts recur across the patterns. They are collected here once, so a pattern can point back to a single definition rather than re-explaining them.

### CEFR Levels

The Common European Framework of Reference grades language proficiency on an ordered six-level scale, from A1 (beginner) to C2 (mastery). Zeeguu uses it in two directions: to estimate how hard an article is, and to simplify an article down to the level of a given learner.

### Article Simplification

When an article is compelling but too hard, Zeeguu rewrites it with an LLM to easier CEFR levels, producing one simplified version per level below the original. It runs both on demand, when a reader opens an article that has not been simplified yet, and ahead of time, over the crawled feed for some articles deemed likely to appeal to readers.

### Crawling

Zeeguu builds its article recommendations by crawling news sites and blogs multiple times per day; this steady feed of freshly crawled articles is where most ahead-of-time LLM work happens (CEFR assessment, simplification), off any reader's critical path. On demand, readers push their own content in: a browser extension sends any article to Zeeguu for study, and on mobile the system share sheet sends any web page to be made interactive and studied within the application.

### Multi-Word Expressions

A multi-word expression (MWE) is a group of words whose meaning is not the sum of its parts, for example *break the ice*. Zeeguu detects them so a learner can translate the phrase as a unit rather than word by word. A cheap dependency-parse gate ([Stanza](https://arxiv.org/abs/2003.07082)) fires first, and an LLM confirms only the flagged sentences.

### Meanings and The Learner Model {#the-learner-model}

Every translation a learner requests is logged, building a model of which words they know and which they struggle with. Each word-in-context is a *meaning*; meanings are classified (by frequency, CEFR level, and phrase type) and drive which exercises and lessons the learner sees. Vocabulary training trains *meanings*, not words. 

### Translation

While reading, a learner gets an instant contextual translation that is generated with the help of multiple parallel translation APIs. If they all agree, the translation is inserted above the word. If they disagree a popup surfaces the disagreement, together with the choice of them to escalate to an LLM through the "Ask AI" action. That is done as one extra, more expensive way of helping the learner that is not confident in which of the translations is the correct one. 

### Audio Lessons

Zeeguu generates personalized audio lessons: an LLM writes a short script built around the words a learner is studying, and text-to-speech synthesizes the audio. Both steps are slow and costly, so lessons are pre-computed for recently active learners. Once a learner choose a topic (european history) or a situation (talking to elderly neighbour on the stairway), a new lesson is generated every day, conditional to the learner having listened to the previous day's lesson. 

### Vocabulary Exercises

Exercises are built from the words a learner has looked up. They use example sentences drawn from the learner's own reading where possible, and LLM-generated, then LLM-validated, sentences otherwise. Where possible, because not all contexts in which the learner has encounter words are appropriate for exercises (some context sentences are too long, others don't make sense outside of their own context).

## Reach

Zeeguu currently serves over 300 monthly active users, with peaks exceeding 400 during the academic year[^1]. It is publicly available to try: the web app is at [zeeguu.org](https://zeeguu.org) with the invite code `zeeguu-beta`, and the mobile apps can be downloaded from the iOS and Android app stores.

[^1]: Monthly active users are defined as users with any learning activity (exercises, reading, browsing, audio lessons, or translations) in a given month. Live statistics are available at: https://api.zeeguu.org/stats/monthly_active_users

