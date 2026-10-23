# Escalate to the LLM

*Serve the common case with a cheap tool; call the LLM only when the user questions the result.*

## Context

A feature can be produced two ways: a cheap, fast specialized tool (a translation API, a classical classifier) that is adequate for the common case, and a slower, costlier LLM that does better on the hard cases. The tool's result is shown to the user, who can see whether it serves them.

## Examples

In Zeeguu, translation APIs (from Google, Azure, and DeepL) serve as the primary translation engines. Most of the time the translation is enough. Sometimes the reader is not convinced: the gloss does not fit the sentence, or a compound or idiom seems to mean something else here. The reader then taps *Explain* in the translation menu, and an LLM explains what the word means in this sentence, at the reader's level. The explanation works as a check: the reader can judge the translation instead of having to take it on trust. This keeps costs low and speed high in the common case, and the LLM runs only when a reader doubts the cheap answer.

![[escalate-to-the-llm-explain.png|45%]]
*In Zeeguu, the inline [translation](../zeeguu/#translation) is the primary path; when the reader wants more, they escalate to an LLM on demand via the "Explain" option.*

## Problem

LLM quality is only worth its cost on the minority of requests the cheap tool handles poorly, and the system cannot tell which those are: whether a translation is good enough depends on what this reader needed, and only the reader knows when they are not convinced. How can the LLM be spent *only* where it pays off?

## Forces

- **Quality on the hard cases.** Specialized tools (translation APIs, NLP pipelines, classical classifiers) are faster, cheaper, and more deterministic than an LLM for well-defined tasks, but on a minority of inputs they fall short, and there the LLM tends to do better. *(pushes toward escalating)*
- **Cost and latency of each escalation.** Each escalation adds the LLM's cost and, because it runs after the cheap result, doubles the wait for that request. *(pushes toward escalating rarely)*

## Solution

Show the specialized tool's result first, and give the user a cheap way to ask for a better one. On that signal, call the LLM with the original input and, where it helps, the specialized tool's output and the user's feedback, so the escalation refines rather than restarts. The LLM may answer a different question than the tool did: Zeeguu's translation gives a word, the escalation explains it.

![[escalate-to-the-llm-diagram.svg]]
*The specialized tool serves the common case. The LLM runs only when the user asks for a better result.*

## Consequences

- **Cheap in the common case.** The LLM runs only when a user asks, so the vast majority of requests never incur its cost or latency.
- **The user carries the routing.** They must notice the option and use it, and it takes space in the interface. Some readers of earlier versions argued that the user should never have to ask; this pattern accepts the cost because nothing else can tell a poor result from a good one.
- **A miss doubles the wait.** When escalation happens the user has already waited for the cheap result first, so time-to-answer for those cases is the sum of both.

## Known Uses

**[Duolingo Max](https://investors.duolingo.com/news-releases/news-release-details/duolingo-max-shows-future-ai-education)** (2023): after an exercise the learner sees the usual correction, and can tap *Explain My Answer* to get a GPT-4 explanation of why their answer was right or wrong. The explanation is generated only for learners who ask. 

## Notes

- *Applies broadly.* Beyond translation: topic classification, named entity recognition, or any task where a cheaper tool handles the common case and the user can see when it falls short.
- *Escalation, not fallback.* A fallback steps in when the primary fails: the API is down or returns an error. That stays a fallback even when the backup is an LLM, the stronger component. Here the primary worked, and its result was not good enough for this reader. The movement is *up* in quality and cost, not around a failure. That is why we name it escalation.
- *Passing the cheap tool's output can hurt.* Zeeguu's *Explain* deliberately does not send the LLM the translation the reader was shown. Given an ambiguous gloss, the model reasoned backwards from it and invented structure to fit: for the Danish *narrøv* glossed as "foolish ass", it split the word into *nar* + *øv* ("donkey") rather than *nar* + *røv*. With the gloss in the prompt, 0 of 3 runs were correct; with only the word and its sentence, 3 of 3.[^esc-explain] Whether the tool's output helps the escalation or misleads it has to be measured.
- *Routing, not escalation.* When the hard cases can be recognized before the cheap tool runs, send them straight to the LLM. Zeeguu does this for [multi-word expressions](../zeeguu/#multi-word-expressions) whose parts are separated in a sentence (German *ich rufe dich morgen an*, where *dich morgen* splits *rufe* from *an*): a translation API would receive a fragment without its context, so the parse routes the whole sentence to the LLM and the API is never called.[^esc-mwe] That is routing on the shape of the input, not this pattern.
- *Relationship to the model cascade.* The **model cascade** in ML serving has the same shape, cheap tier first and expensive tier on demand, but escalates automatically when the cheap model's own confidence is low. **[FrugalGPT](https://arxiv.org/abs/2305.05176)** (Chen, Zaharia & Zou, 2023) escalates when a scorer rejects the cheap answer, and **[RouteLLM](https://arxiv.org/abs/2406.18665)** (Ong et al., 2024) trains a router that sends only the hard queries to the strong model. The difference is who decides: the model's confidence, or the user. The two can be combined.
- *A cascade needs a confidence score; translation APIs do not give one.* Zeeguu's translation APIs (Google, Azure, DeepL) return a translation but no score saying how sure they are, so a cascade cannot be built on them. The user is the only judge left.

[^esc-explain]: [`explain_selection`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/llm_service.py) and the measurements in `llm_services/prompts/word_explanation.py`, in the `zeeguu/api` repository.
[^esc-mwe]: [`translate_separated_mwe`](https://github.com/zeeguu/api/blob/master/zeeguu/core/llm_services/mwe_translation_service.py) in the `zeeguu/api` repository.

> [!draft]- Notes after the focus group
> - name? why does the user have to know the LLM?
> - just ask: "explain"
> - user should not even ask (Uwe)
> - escalate to more powerful
> - why do we even do news? you could have 1k articles about …
> - premium version — only shows news articles
> - free users only get what the paying users get
> - which patterns still stand if you replace LLMs with expensive components?
