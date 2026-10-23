---
layout: default
title: "Escalate to the LLM"
permalink: /escalate-to-the-llm/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../using-the-llm-efficiently/">Using the LLM Efficiently</a>
</nav>


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

<figure class="img">
  <a href="/images/escalate-to-the-llm-diagram.svg"><img src="/images/escalate-to-the-llm-diagram.svg" alt="The cheap tool serves the common case. The LLM runs only when the user asks for a better result."></a>
  <figcaption>The cheap tool serves the common case. The LLM runs only when the user asks for a better result.</figcaption>
</figure>

## Solution in Zeeguu

When the reader is not convinced by a translation, they tap *Explain* in the translation menu, and an LLM explains what the word means in this sentence, at the reader's level. The explanation works as a check: the reader can judge the translation instead of having to take it on trust.

<figure class="img" style="max-width:35%">
  <a href="/images/escalate-to-the-llm-explain.png"><img src="/images/escalate-to-the-llm-explain.png" alt="In Zeeguu, the inline [translation](../zeeguu/#translation) is the primary path; when the reader wants more, they escalate to an LLM on demand via the &quot;Explain&quot; option."></a>
  <figcaption>In Zeeguu, the inline [translation](../zeeguu/#translation) is the primary path; when the reader wants more, they escalate to an LLM on demand via the &quot;Explain&quot; option.</figcaption>
</figure>

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



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../prompt-amortization/">← Prompt Amortization</a><a class="nav-next" href="../high-recall-gate-precision-verdict/">High-Recall Gate, Precision Verdict →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BEscalate+to+the+LLM%5D+&labels=feedback%2Cusing-the-llm-efficiently&body=%2A%2ARe%3A%2A%2A+Escalate+to+the+LLM%0A%2A%2ASection%3A%2A%2A+Using+the+LLM+Efficiently%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Fescalate-to-the-llm%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
