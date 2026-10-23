# Escalate to the LLM

*Serve the common case with a cheap tool; call the LLM only when the user questions the result.*

## Context

A feature can be produced either by a cheap specialized tool (a translation API, a classical classifier) or by an LLM. The tool's answer is shown to the user. The tool gives no score saying how sure it is, but the user often notices when its answer feels off.

## Problem

Most results from the cheap tool are good enough, and paying for the LLM on those is waste. A few are not, and on those the LLM is worth its cost. How can a system call the LLM only for the results that fall short?

## Problem in Zeeguu

In Zeeguu, translation APIs (from Google, Azure, and DeepL) translate the words a reader taps. Most of the time the translation is enough. Sometimes the reader is not convinced: the gloss does not fit the sentence, or a compound or idiom seems to mean something else here.

## Forces

- **The LLM does better on the hard cases.** On the inputs where the cheap tool falls short, such as idioms and compounds, an LLM usually does better. *(pulls toward using the LLM)*
- **Every LLM call costs money and time.** An LLM call costs more than the cheap tool and is slower, so making it on every request would make the common case slower and costlier. *(pulls toward using the cheap tool)*

## Solution

Show the cheap tool's result first, and give the user a way to ask for a better one. On that signal, call the LLM with the original input and, where it helps, the cheap tool's output and the user's feedback, so the escalation refines rather than restarts. The LLM may answer a different question than the tool did: Zeeguu's translation gives a word, the escalation explains it.

![[escalate-to-the-llm-diagram.svg]]
*The cheap tool serves the common case. The LLM runs only when the user asks for a better result.*

## Solution in Zeeguu

When the reader is not convinced by a translation, they tap *Explain* in the translation menu, and an LLM explains what the word means in this sentence, at the reader's level. The explanation works as a check: the reader can judge the translation instead of having to take it on trust.

![[escalate-to-the-llm-explain.png|35%]]
*In Zeeguu, the inline [translation](../zeeguu/#translation) is the primary path; when the reader wants more, they escalate to an LLM on demand via the "Explain" option.*

*Explain* does not send the LLM the translation the reader was shown, because the gloss misled it. For the Danish *narrøv* glossed as "foolish ass", the model reasoned backwards from the gloss and split the word into *nar* + *øv* ("donkey") rather than *nar* + *røv*. With the gloss in the prompt, 0 of 3 runs were correct; with only the word and its sentence, 3 of 3.[^esc-explain] Whether the cheap tool's output helps the escalation or misleads it has to be measured.

[^esc-explain]: [`explain_selection`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/llm_service.py#L139) and the measurements in [`prompts/word_explanation.py`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/prompts/word_explanation.py), in the `zeeguu/api` repository.

## Consequences

- **Cheap in the common case.** The LLM runs only when a user asks, so most requests never incur its cost or latency.
- **The user carries the routing.** They must notice the option and use it, and it takes space in the interface. Some readers of earlier versions argued that the user should never have to ask; this pattern accepts that cost because nothing else can tell a poor result from a good one.
- **The better answer comes later.** The LLM starts only when the user asks, so its answer takes a full LLM call to arrive. The user is not left empty-handed meanwhile: they already have the cheap result.

## Known Uses

**[Duolingo Max](https://investors.duolingo.com/news-releases/news-release-details/duolingo-max-shows-future-ai-education)** (2023): after an exercise the learner sees the usual correction, and can tap *Explain My Answer* to get a GPT-4 explanation of why their answer was right or wrong. The explanation is generated only for learners who ask.

## Related Patterns

- **Model cascade.** In ML serving, a model cascade has the same shape, cheap tier first and expensive tier on demand, but escalates automatically when the cheap model's own confidence is low. **[FrugalGPT](https://arxiv.org/abs/2305.05176)** (Chen, Zaharia & Zou, 2023) escalates when a scorer rejects the cheap answer, and **[RouteLLM](https://arxiv.org/abs/2406.18665)** (Ong et al., 2024) trains a router that sends only the hard queries to the strong model. The difference is who decides: a score, or the user. Where the cheap tool gives a usable score, a cascade can decide without asking, and the two can be combined.
- ***Fail-Fast Provider Chain*** moves to another provider when a call fails. Here the cheap tool did not fail: its answer was not good enough for this reader.
- **Routing.** When the hard cases can be recognized before the cheap tool runs, send them straight to the LLM. Zeeguu does this for [multi-word expressions](../zeeguu/#multi-word-expressions) whose parts are separated in the sentence, as *call* and *back* are in *I'll call you back*: a translation API would get a fragment without its context, so the whole sentence goes to the LLM and the API is never called.[^esc-mwe]

[^esc-mwe]: [`translate_separated_mwe`](https://github.com/zeeguu/api/blob/c853d767/zeeguu/core/llm_services/mwe_translation_service.py#L114) in the `zeeguu/api` repository.

> [!draft]- Notes after the focus group
> - name? why does the user have to know the LLM?
> - just ask: "explain"
> - user should not even ask (Uwe)
> - escalate to more powerful
> - why do we even do news? you could have 1k articles about …
> - premium version — only shows news articles
> - free users only get what the paying users get
> - which patterns still stand if you replace LLMs with expensive components?
