---
title: Architectural Patterns for Integrating LLMs into User-Facing Applications
---

# Architectural Patterns for Integrating LLMs into User-Facing Learning Software

Note about the title: I think the User-Facing needs to be there. And learning, I'm not sure.

### What is this?

A living catalogue of recurring patterns I keep running into when building software with and around large language models — the small, reusable shapes of solution that show up again and again across agents, tools, prompts, and evaluation.

It's a working paper: a draft I'm developing in the open and revising as the ideas (and the tools) mature. Feedback is very welcome.

*Status: working draft, June 2026*

### The Idea

Large Language Models are increasingly being integrated into existing user-facing interactive applications — not as standalone chatbots, but as components working behind the scenes to improve the user experience. While there is growing literature on building LLM-native products (chatbots, agents, RAG systems) and on using LLMs for code generation, there is surprisingly little guidance on the **software engineering challenges of integrating LLMs as components into existing interactive applications** where real users expect fast, reliable, and trustworthy responses.

LLMs have a unique combination of properties that create novel architectural forces: 

- they are expensive (per-token pricing),   
- slow (high latency),   
- non-deterministic (same input can yield different outputs, although this can be to a certain degree controlled with the temperature setting),  
- rapidly evolving  (new models released every few months and old ones regularly deprecated),  
- imprecise (they make mistakes), and   
- general-purpose (they can attempt almost any task described as text). 

These properties demand specific engineering strategies.

Over the past year, we have been integrating LLMs into [Zeeguu](https://zeeguu.unibe.ch/) — an open-source platform for personalized language learning that helps users learn foreign languages by reading authentic online content. Through this work, we have identified a set of recurring architectural patterns for LLM integration. We believe these patterns are general and applicable beyond our specific domain.

### Main Case Study: Zeeguu

Zeeguu is an open-source language learning platform built around the idea that learners benefit most from engaging with authentic content in their target language. Rather than relying on artificial textbook exercises, Zeeguu helps users find real articles — news, blog posts, and other web content — tailored to both 1\) their *level* and 2\) their *interests*.

The platform recommends articles in the learner's target language based on their proficiency and reading preferences, making it **easy to find material that is both interesting and appropriately challenging**. If a text is personally compelling but too difficult, Zeeguu simplifies it to the learner's level using LLMs. 

When users encounter unfamiliar words or phrases while reading, they can get translations on the fly powered by (contextual) Google Translate, so the reading experience remains fluid and uninterrupted. One alternative is provided by a state-of-the-art LLM, offering a more contextually nuanced option. 

Every translation a user requests is logged by the system, which over time builds a **detailed model of the learner's vocabulary knowledge** — tracking which words they know, which ones they struggle with, and how well they've retained previously encountered vocabulary.

Based on this evolving learner model, Zeeguu **generates interactive vocabulary exercises and audio lessons** that focus on the words that matter most for each individual learner, rather than following a generic curriculum. The exercises use the context in which the word was originally encountered, based on the assumption that if the original text was interesting to the learner, then examples from it will also be interesting. 

In essence, Zeeguu unifies reading, translation, learner modeling, and practice into a coherent pipeline, with the learner's own reading interests as the primary driver. 

Zeeguu currently serves over 300 monthly active users, with peaks exceeding 400 during the academic year[^1].

Open question:

- Do these patterns apply beyond the language learning domain of Zeeguu. Do other kinds of applications show to users LLM generated text in a similar manner? 

[^1]: Monthly active users are defined as users with any learning activity (exercises, reading, browsing, audio lessons, or translations) in a given month. Live statistics are available at: https://api.zeeguu.org/stats/monthly_active_users


# Cost Optimization Patterns

## Prompt Amortization

**Example (Zeeguu):** A prompt that verifies whether a word-translation pair is correct requires substantial instructions (explaining what constitutes a valid translation, edge cases, output format). The actual input — a word and its translation — is tiny. Instead of sending one request per word pair, we pack dozens of pairs into a single prompt. Similarly, when generating example sentences for words users will study, we batch the generation for all words in one call. This pattern combines naturally with pre-computation: because results are computed offline, we have the luxury of batching. Article simplification generates all CEFR-level variants (A1, A2, B1, B2) in one call, with the prompt instructing the model to output a JSON object keyed by level. This reduces four API calls to one, cutting cost by ~75%.

**Forces:** Many LLM tasks involve a large instructional preamble (the system prompt explaining the task) and a small variable input. Sending individual requests wastes the prompt overhead, both in cost and latency.

**Solution:** Batch multiple inputs into a single request, amortizing the expensive prompt across many items.

**Notes:** 

- One might still need to split into multiple prompts when too many tasks are batched. One might also have to investigate whether the quality of the response decreases when the cardinality of the batch is increased. In our own experience, it works fine for ...
- Some LLMs provide prompt caching - e.g. Deepseek. Even so, if the cost is amortized with prompt caching, the time saving of amortization can still be a valuable reason for doing it

## LLM as Fallback

**Example (Zeeguu):** Google Translate serves as the primary translation engine. When a user indicates the translation is inadequate, the system escalates to an LLM for a more nuanced, context-aware translation. This keeps costs low and speed high in the common case while providing higher, LLM-quality results when needed.

**Forces:** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than LLMs for well-defined tasks — but they sometimes fail or produce insufficiently satisfactory results.

**Solution:** Use the specialized tool as the primary path and escalate to the LLM only when the primary fails or the user signals dissatisfaction.

**Applicability:** This pattern applies broadly — topic classification, named entity recognition, or any NLP task where a cheaper tool handles the common case and the LLM handles the long tail.


# Latency / Availability Patterns

## Pre-Computing Likely-Needed Results

**Example (from Zeeguu):** The system needs to verify that word/translation pairs obtained from Google Translate or Azure Translate APIs are correct before including them in vocabulary exercises — the system can afford to insert an imprecise translation while the reader is quickly trying to make sense of a text, but it cannot afford to have users repeatedly practice imprecise translations! A regular cron job identifies words users should study next and pre-computes LLM-based verification for the quality of their translation. 

**Forces:** LLMs can provide valuable data for users, but they are slow and expensive, making their invocation impractical when the user needs an answer in real-time. (Real time users expect answers in 200ms, while depending on the prompt and the deployment configuration, an LLM-based system can take multiple seconds to produce an answer).

**Solution:** Anticipate likely user needs and pre-compute LLM results offline (e.g., via cron jobs), so results are available instantly when needed. The system designer should model user behavior in order to predict their LLM needs. 

## Hot-Path Result Caching

**Example (Zeeguu):** MWE detection maintains a 500-entry LRU cache. When multiple users read the same article, phrase analyses computed for the first user are served instantly to subsequent users. Cache hit rates of 40-60% are typical for popular articles.

**Forces:** Pre-computation handles predictable needs, but some LLM queries are repeated unpredictably within short time windows (e.g., multiple users encountering the same phrase, or a single user re-requesting the same analysis). These don't justify persistent storage but do benefit from short-term caching.

**Solution:** Maintain an in-memory LRU cache for recent LLM results. Cache keys include the relevant input parameters; cache entries expire after a short TTL or when capacity is reached.

**Tradeoff**: Memory overhead and cache invalidation complexity. Best suited for queries where staleness is acceptable and input space has natural clustering (many users reading same content).

**Tradeoff:** 
- A variant of this caches the results in the DB not in-memory. We also have this in Zeeguu. 

## Multiplexed Dispatch

**Example (Zeeguu):** Real-time translations are dispatched to multiple translation providers in parallel. The first response is used, and the rest are saved for when the user asks for alternatives. 

**Forces:** Multiple LLM providers offer similar capabilities but with varying latency. When speed matters for user experience, relying on a single provider creates a bottleneck.

**Solution:** Dispatch the same request to multiple providers simultaneously and use the first response that arrives. Track the top two fastest providers, and always dispatch to these. 

An alternative to this is **live retrieval**: when the user encounters a translation that they are not sure of, they ask for alternatives, the UI presents the results that are cached, but also asks for alternatives and displays a UI interface that highlights the fact that some of the results are still streaming in.

**Tradeoff:** Increased cost (you pay for redundant calls) in exchange for reduced latency.

## Fail-Fast Provider Chain

**Example** (Zeeguu): The app uses a unified LLM service proxy which tries Anthropic first; on any error (timeout, rate limit, API error), it immediately switches to DeepSeek without retry. This keeps worst-case latency bounded while maintaining availability.    

**Forces**: LLM providers experience outages, rate limits, and latency spikes. Retry logic increases latency and may still fail. Different providers offer similar capabilities at different price/performance points.    

**Solution**: Configure a chain of LLM providers with no retries. On any failure, immediately fall back to the next provider in the chain. Prioritize speed over exhausting retry budgets.    

**Note**: This differs from the *LLM as Fallback* pattern in that all components in the chain are LLMs offering equivalent capabilities — the fallback is for reliability, not for capability escalation.


# Lifecycle Management Patterns

## LLM as Wizard of Oz

**Example (Zeeguu):** Topic classification of articles is currently performed by pasting the abstract into an LLM. This works but is expensive. Once we are satisfied with the topic taxonomy and have accumulated enough labeled data, we will switch to a dedicated topic detection framework.

**Forces:** LLMs are general-purpose machines that can attempt almost any text-based task. Building dedicated, efficient solutions requires upfront investment and training data that may not yet exist.

**Solution:** Use the LLM to perform a task in production while you build a more efficient replacement. The LLM serves as the "wizard behind the curtain" — convincing to users, allowing early beta-testing and feedback, but intended to be temporary.

**Variant — Bootstrapping:** In a more subtle variant, the LLM *generates the training data for its own replacement.* For example, Zeeguu uses an LLM to estimate text difficulty levels. These LLM-generated difficulty labels are being accumulated as training data for a classical classifier that will eventually take over the task.

**Note:** This pattern has an interesting lifecycle relationship with pattern *LLM as Fallback* a system may start with the LLM as primary (Wizard of Oz), migrate to a specialized tool as primary, and then keep the LLM as fallback — completing a full cycle from LLM-first to LLM-as-backup.


# Data Management Patterns

## LLM Output Provenance

**Example (Zeeguu):** When the system generates example sentences with a given word to be used in exercises, it stores which model and prompt version produced each result. When a prompt is improved, the system can identify and regenerate stale outputs without reprocessing everything. 

**Forces:** LLM-generated data that enters persistent storage becomes a long-lived asset, but models and prompts improve over time. Without knowing how a piece of data was generated, you cannot selectively regenerate it when better models or prompts become available. Prompts evolve more frequently than model versions and can have a larger impact on output quality.

**Solution:** Store the full provenance tuple alongside every LLM-generated artifact: (model version, prompt version, generated output, timestamp). This enables selective regeneration (e.g., *"re-run everything produced by prompt v2 with the improved prompt v3"*) and quality auditing.

**Notes:** 

- The key insight is that the prompt is at least as important to version as the model — a prompt change can completely alter output format, quality, or behavior even with the same model.   
- This is also critical for the Wizard of Oz pattern: when accumulating LLM-generated labels as training data for a classical replacement, provenance tracking lets one exclude data produced by a prompt version that was later found to be noisy or biased.  
- Implicit provenance: Keep model names and prompt versions as constants in code. When one needs to know what generated a piece of data, correlate its `created_at` timestamp with git history to determine which model/prompt was deployed at that time. However, this works for simpler systems where there is a single model/prompt active at any time. A system using alternative prompts, e.g. for A/B testing, will have to track provenance explicitly. Also, explicit tracking makes data analysis faster, and ensures that data is self-describable.
- Provenance must capture the dimension that actually varies. Zeeguu's `audio_lesson_meaning` rows have a `created_by` field that records the model identifier (e.g. `"Claude-Opus-Prompt1"`) — but the prompt template files were edited in place over time without bumping that identifier, so the field carried the same value across two materially different prompt eras and could not drive selective regeneration. When the team later identified ~900 lessons generated under a previous, ambiguous prompt, the only way to find them was a content regex on the output itself — "does the script contain the ambiguous phrasing?". The lesson: if prompts evolve by in-place edits, the provenance field that names them must bump on every edit (e.g. via a versioned filename like `prompt-v2-rev3.txt` or a content hash) — otherwise the field is decorative and selective-regeneration falls back to forensics on the output.


# Quality Assurance Patterns

## LLM-Checking-LLM

**Example (Zeeguu):** After generating contextual example sentences for vocabulary words, a second LLM call reviews the examples for accuracy, naturalness, and appropriate difficulty level.

**Forces:** LLMs are imprecise generators, but verification of specific properties (e.g., grammatical correctness) is a more constrained task than open-ended generation (e.g., text simplification). A second, focused LLM call can catch errors that the first, more complex call introduced.

**Solution:** Use one LLM call to generate a result, then use a separate LLM call to check or refine it. The verification prompt can be simpler and more focused than the generation prompt.

**Note:** This is distinct from ensemble methods or chain-of-thought — the key insight is that checking is a fundamentally easier task than generating, and this asymmetry can be exploited architecturally.

## LLM Content Validation Tracking

**Example (Zeeguu)**: A word-translation pair can exist at several trust levels: generated by Google Translate (unverified), verified by an LLM checker (auto-verified, pattern #2), implicitly accepted by a user who practiced it without complaint, or explicitly corrected by a user. Each level carries different confidence, and the system can make different decisions depending on the validation state — for example, only including explicitly confirmed translations in exercises, while using auto-verified ones for reading assistance where the stakes are lower.

**Forces**: Once LLM-generated data is persisted, it becomes indistinguishable from human-verified data unless explicitly marked. Downstream features and users may silently treat unverified AI output as ground truth. Over time, the system accumulates a mix of trusted and untrusted data with no way to tell them apart.

**Solution**: Maintain an explicit, queryable validation state for all LLM-generated content in the data model. Never let LLM-generated content silently become trusted data. The validation state may be a simple flag, but more often it is a spectrum or state machine reflecting different levels of trust (e.g., unverified → auto-verified → implicitly accepted → explicitly confirmed by user; alternatively, one could track the number of users that have validated a given content).

**Notes:** 

- This pattern complements Provenance (#7) — together they answer two essential questions about any piece of LLM-generated data: how was it produced? and has anyone confirmed it's correct? The right granularity of validation tracking depends on the domain: some systems may need binary (verified/not), others may need multiple validators with agreement thresholds, and others — like Zeeguu — benefit from a trust spectrum that reflects different forms of implicit and explicit user feedback.  
- Implicit validation: One could argue that "if a user practiced a word without complaint, it's implicitly validated"


# Hybrid Pipeline Patterns

## Hybrid Classical+LLM Pipeline

**Example (Zeeguu)**: Multi-word expression (MWE) detection uses Stanza's dependency parser to identify candidate phrases (fast, high recall), then sends candidates to an LLM to filter out false positives based on semantic analysis (slower, high precision). This achieves better F1 than either approach alone, at a fraction of the cost of LLM-only detection.    

**Forces**: Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.    

**Solution**: Use the classical tool as a high-recall candidate generator, then use the LLM as a precision filter on the candidates. Both tools work together in a pipeline, not as alternatives.    

**Tradeoff**: Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity. 


# Related Work

To our knowledge, no peer-reviewed work presents a catalog of architectural patterns for integrating LLMs as components into existing production systems, grounded in real deployment experience and described using the standard pattern format (context, forces, solution, consequences). Our patterns addressing lifecycle management (Wizard of Oz, LLM as Fallback), cost optimization (Pre-computation, Prompt Amortization, Multiplexed Dispatch), quality assurance (LLM-Checking-LLM, Validation Tracking), and data management (Provenance) appear to be novel contributions.

Several practitioner-oriented resources discuss patterns for building LLM-based systems, but they operate at a different level of abstraction and lack the grounding in a specific production system that we aim to provide.

## Practitioner resources

Eugene Yan's "**Patterns for Building LLM-based Systems & Products**" (2023, blog post) identifies seven patterns: Evals, RAG, Fine-tuning, Caching, Guardrails, Defensive UX, and Collecting User Feedback. These address the question "how do I build an LLM product?" — they describe the overall stack for LLM-native applications. Our patterns address a different question: "I have an existing system, and I want to add LLM capabilities as a component — how do I manage cost, quality, latency, and lifecycle?" There is some overlap on caching/pre-computation, but our treatment focuses on prompt amortization and user-need anticipation rather than semantic similarity caching. Yan's work is not peer-reviewed.

ThoughtWorks' "**Emerging Patterns in Building GenAI Products**" (Fowler et al., martinfowler.com) and "Engineering Practices for LLM Applications" focus on operational concerns: testing, evaluation, guardrails, and RAG pipelines. These are primarily about LLMOps rather than the architectural decisions for embedding LLMs as components within an existing application.

Andreessen Horowitz's "**Emerging Architectures for LLM Applications**" (2023) provides a reference architecture for the LLM infrastructure stack (embedding pipelines, vector databases, orchestration layers, agents). Again, this targets LLM-native products rather than LLM integration into existing systems.

Books. "**LLM Design Patterns**" (Huang, Packt, 2024\) and "LLMs in Enterprise" (Menshawy & Fahmy, Packt, 2025\) cover model-level patterns (fine-tuning, quantization, inference optimization, RAG) and enterprise deployment concerns. They do not address application-level integration patterns such as the lifecycle management (Wizard of Oz → specialized tool → LLM as fallback), prompt amortization, or LLM output provenance that we identify.

## Academic surveys. 

There is a large body of work on **using LLMs *for* software engineering tasks** — code generation, bug repair, testing, requirements engineering (see surveys by Fan et al., 2023; Zhang et al., 2024). However, these focus on LLMs as tools for developers, not on the engineering challenges of integrating LLMs as runtime components within production software. 

A recent **systematic literature review on software architecture and LLMs** (Schmid et al., 2025\) found only 18 relevant papers and noted that LLM-based software design remains an open research direction. None of the surveyed academic work addresses the specific architectural patterns for managing cost, quality, latency, and lifecycle when LLMs serve as components in existing applications.

LLM self-verification. For the *LLM-Checking-LLM pattern*, there is relevant work on **LLM self-verification**. Gero et al. (2023) demonstrated that self-verification improves clinical information extraction accuracy, explicitly building on the asymmetry between verification and generation. However, Stechly et al. (2024) showed that self-critique fails for formal reasoning tasks, finding significant performance collapse with self-verification but gains with external verification. Our pattern differs from both in that it uses separate, differently-prompted LLM calls for generation and verification of different properties (e.g., text simplification followed by grammatical correction), rather than asking an LLM to verify its own reasoning.


# What Makes These Patterns LLM-Specific?

Some of these patterns echo general distributed systems wisdom (batching, fallback, redundant dispatch). What makes them distinctly relevant to LLM integration is the specific combination of forces:

* **Cost structure** — per-token pricing with high fixed prompt overhead, unlike flat-rate API calls  
* **Non-determinism** — same input can yield different outputs, necessitating verification chains  
* **Asymmetry between generation and verification** — checking is easier than producing  
* **General-purpose capability** — the same component can serve as prototype, primary, or fallback  
* **Quality–cost–latency tradeoff space** — uniquely wide compared to traditional APIs


# Possible Other Patterns

## Temperature as Task Selector

**Example (Zeeguu):** Translation validation uses temperature 0 for deterministic yes/no judgments. Audio lesson script generation uses temperature 0.8 to produce varied, natural-sounding dialogues. The same model serves both purposes with different configuration.

**Forces:** LLMs exhibit different behaviors at different temperature settings. Classification and validation tasks benefit from deterministic outputs (low temperature), while creative generation benefits from variety (higher temperature). Using a single temperature for all tasks either sacrifices reliability or creativity.

**Solution:** Systematically vary temperature based on task type. Use temperature 0–0.3 for tasks requiring consistency (validation, classification, structured extraction). Use temperature 0.7–1.0 for tasks requiring creativity (dialogue generation, example variety).

**Note:** This pattern acknowledges that a single LLM can behave as multiple "virtual components" depending on configuration — deterministic validator vs. creative generator.

## Soft Invalidation of LLM Artifacts

**Example (Zeeguu):** When the prompt that generates audio lesson scripts was improved, the ~900 stored `audio_lesson_meaning` rows produced under the previous prompt were neither regenerated eagerly nor deleted. Instead, each affected row received a `deprecated_at` timestamp, and the cache-lookup helper (`AudioLessonMeaning.find()`) was gated to skip deprecated rows. New daily lessons request a fresh row and trigger regeneration under the new prompt; existing daily lessons that already reference a deprecated row keep playing their old audio without breaking.

**Forces:** When a prompt or model improves, the obvious responses each have a serious drawback:
- *Regenerate everything eagerly* — expensive, floods generation queues if affected rows number in the thousands, and pays for content that may never be re-requested.
- *Delete the stale rows* — breaks any downstream object that references them by id (history, analytics, user-visible past sessions).
- *Leave the stale rows in place and accept future reuse* — silently propagates the old, known-suboptimal quality.

None of these are good defaults for production systems where LLM-generated artifacts are referenced from user-visible history and are also targets for reuse.

**Solution:** Mark stale rows as deprecated rather than mutating or removing them. Gate the cache-lookup / reuse path to skip deprecated rows, forcing fresh generation on next demand. Existing references to a deprecated row remain valid — the row keeps its content for historical playback — but no new consumer picks it up. Regeneration cost is paid lazily, amortized over normal access patterns, and only for content that is actually requested again.

**Notes:**
- This pattern is forward-only: it gates *reuse*, not *playback*. A user replaying an old lesson hears the old (lower-quality) version. That is usually preferable to a silent content swap mid-history.
- Works best when content has a clear "next access triggers regeneration" entry point. If consumers cache aggressively further downstream, the deprecation flag has to propagate to those layers too.
- Composes naturally with *LLM Output Provenance* (#7): provenance answers "which rows are stale?", soft invalidation answers "what do I do with them once I know?".
- **Prerequisite — artifact identity must follow the row, not the upstream key.** If the on-disk artifact (audio file, image, embedding) is named after the *source identity* (e.g. `meaning_id`) rather than the *row identity* (e.g. `audio_lesson_meaning.id`), the regenerated row's artifact overwrites the deprecated row's artifact on the same path — defeating the historical-playback guarantee. Zeeguu encountered this concretely: meaning-lesson audio files were keyed by `meaning_id`, so regeneration silently replaced the audio referenced by old daily lessons. A separate change re-keyed those files by row id to make Soft Invalidation safe. This small structural requirement may deserve being a pattern in its own right (working title: *artifact identity = row identity*).

## Deterministic Postprocessing

**Example (Zeeguu):** LLM-simplified article summaries consistently ended with a Unicode ellipsis (`…`), making every home-card preview read as an unfinished sentence. One option was to add a "do not end with ellipsis" instruction to the simplification prompt; the chosen option was a five-line regex stripping any trailing `…` or `..+` at serialization time. The regex handles every case at 100%, including the ~60k pre-existing rows in the database that no prompt change could retroactively touch.

**Forces:** When LLM output has a deterministic formatting defect (a stable trailing string, a known preamble, leaked markdown in a plain-text field, trailing whitespace), the obvious instinct is to fix it in the prompt. But:
- Prompt compliance is probabilistic; the same constraint in code is 100%.
- Prompt tokens cost money on every call and can distract the model from the actual semantic task.
- Prompt changes do not affect rows already in the database.
- Code is testable and reviewable; prompt instructions are not.

**Solution:** Enforce deterministic constraints in code, at the post-processing or serialization boundary. Reserve prompt instructions for things that genuinely require model judgment.

**Notes:** The boundary between "deterministic" and "semantic" is the test. *Strip a trailing `…`* — deterministic, do it in code. *Don't mention the user's name* — semantic, the model has to enforce. When the deterministic rule list grows long, that is itself a signal that the task is poorly scoped, not that the prompt needs more rules.


# Possible Paper Contributions

1. **Pattern catalog** — A documented set of architectural patterns for LLM integration, grounded in a real production system, described using the standard context/forces/solution/consequences format.

2. **Pattern interactions and lifecycle** — The patterns are not independent. They compose (pre-computation enables batching) and evolve over a system's lifetime (Wizard of Oz → specialized tool → LLM as fallback). Documenting these interactions is a contribution beyond individual patterns.

3. **Validation** — Several avenues:

   * Evidence from Zeeguu's production deployment (cost savings, latency improvements, quality metrics)  
   * Contributions from other practitioners with complementary examples would be good  
   * Mining GitHub/open-source projects for additional instances (potentially a separate MSR paper)


