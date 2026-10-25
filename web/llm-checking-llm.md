---
layout: default
title: "LLM-Checking-LLM"
permalink: /llm-checking-llm/
---


<nav class="pattern-nav">
  <a href="../#the-patterns">← All patterns</a> <span class="crumb-sep">‹</span> <a href="../trusting-llm-output/">Trusting LLM Output</a>
</nav>


*Check the output of an LLM with a second LLM call that asks a narrow question about it.*

## Context

An LLM generates content that will be used or stored, and its output can be wrong in a specific way. A narrow question about the result (is it grammatical? does it use the word in the intended sense? does it suit the learner's level?) can be answered on its own, without redoing the whole generation. No deterministic check can answer it, and there are too many outputs for a person to review each one.

## Problem

How can an unreliable generator's mistakes be caught, when a second generator would be just as unreliable?

## Problem in Zeeguu

The vocabulary exercises show a word in a sentence, with the learner's translation above it. For each word a learner studies, an LLM writes example sentences at the learner's level, and its prompt gives the word together with the translation being taught (its [meaning](../zeeguu/#the-learner-model)). Even so, a generated sentence can use the word in a way the translation does not fit. Asked for a sentence with the Danish *selv* translated as *even* (as in *selv børn kan det*, "even children can do it"), the generator wrote *Selv om det regner, går vi en tur* ("even though it's raining, we're going for a walk"). The sentence is natural and contains the word, but there *selv* is part of *selv om* (*even though*) and does not mean *even* on its own. The exercise shows *even* above it, and a learner who practices with that sentence learns the wrong meaning.

That sentence was generated in October 2025. A year later it is the example of what not to do in the generation prompt, which now forbids using the word inside a larger expression. Such sentences became rarer, but did not stop. Other errors slip through the same way: a sentence that is not grammatical, or one that needs another form of the translation (*means* where the translation says *mean*).


## Forces

- **Another LLM call is no more trustworthy, and costs as much.** It can be wrong in the same ways as the first, and it adds a full call in tokens and latency to every item. *(pushes against a second call)*
- **Some checks are too general for a deterministic test.** No rule can tell whether a word is used in the intended sense: that takes understanding the sentence. *(pushes toward a model checking the output)*

## Solution

Use one LLM call to generate a result, then a separate, differently-prompted LLM call to ask one narrow question about it.[^check-separate] The checker's prompt holds only what the question needs (the item and the question about it) and asks for a short verdict. 

This escapes the paradox because a narrow question (*Is it grammatical?*, or *Does it use the intended meaning?*) has a small, well-defined answer space and a clear success criterion, so an LLM can do it more reliably than the open-ended generation that produced the output. [Saunders et al.](https://arxiv.org/abs/2206.05802) measured this: models judge whether an answer is right more reliably than they produce a right answer.


[^check-separate]: A separate call with its own prompt, not necessarily a different model.

<figure class="img">
  <a href="/images/llm-checking-llm-diagram.svg"><img src="/images/llm-checking-llm-diagram.svg" alt="A second LLM call asks one narrow question about the output of the first. An output that passes is used; what happens to one that fails is a separate choice: drop it or regenerate it."></a>
  <figcaption>A second LLM call asks one narrow question about the output of the first. An output that passes is used; what happens to one that fails is a separate choice: drop it or regenerate it.</figcaption>
</figure>

A failed check still needs a policy, and the pattern does not fix one: drop the result, or regenerate it with [Reject and Reprompt](../reject-and-reprompt/). Dropping is cheapest and fits where the item is expendable (as with Zeeguu's example sentences below). Regenerating with the reason the check gave, within a bounded number of attempts, is [Reject and Reprompt](../reject-and-reprompt/), whose loop works with any checker, an LLM included.

## Solution in Zeeguu

Before a generated sentence is used in an exercise, a second LLM call asks one narrow question: does this translation fit the word in this sentence? The check receives the word, the translation and the sentence, and works through a few steps that all serve that question: is the sentence grammatical, does the translation read correctly in place of the word and in the form the sentence needs, and is it the meaning of the word itself rather than of a larger expression around it. *Selv om det regner…* fails at the last step. A sentence that fails is dropped, and the exercise uses other sentences when they are available. And it works because answering whether one translation fits one sentence is far narrower than writing a good sentence from scratch.

## Consequences

- **Errors are caught for the price of one extra call per item.**
- **It narrows the error rate, it does not remove it.** The checker is itself an LLM and can return its own false verdicts. Generation and check can sit behind one call, so the rest of the application never sees the checker, but what comes out is still best-effort.


## War Story: A Check Not Worth Its Cost

A check that works can still not be worth what it costs. Zeeguu ran a second call over every [simplified article](../zeeguu/#article-simplification): it read each simplified title and body and returned grammar corrections, which were applied to the text.[^check-grammar] Between December 2025 and April 2026, roughly 96% of title corrections and 72% of body corrections changed two characters or fewer: small slips, not broken sentences. The check worked, but every simplified version paid an extra call for changes few readers would notice, and it is now disabled by default. That verification is cheaper than generation says nothing about whether the errors are worth catching; only measurement answers that.

## Known Uses

- *Documented in the literature.* **[LLM-as-a-judge](https://arxiv.org/abs/2306.05685)** (Zheng et al., NeurIPS 2023) uses a separate strong LLM to score another model's open-ended outputs, now a standard evaluation technique.
- **[Self-Refine](https://arxiv.org/abs/2303.17651)** (Madaan et al., NeurIPS 2023) has the model critique and refine *its own* output in a separate pass: a same-model variant of the idea, where this pattern instead uses a differently-prompted call.
- **[G-Eval](https://arxiv.org/abs/2303.16634)** (Liu et al., 2023), shipped in eval frameworks such as **[DeepEval](https://deepeval.com/docs/metrics-llm-evals)**, uses a separate chain-of-thought (step-by-step reasoning) judge call to grade generated output.

## Related Patterns

[Defensive Output Parsing](../defensive-output-parsing/) checks that an output is well-*formed*; this pattern checks that a well-formed output is *correct*. A failed check can feed [Reject and Reprompt](../reject-and-reprompt/). Whatever happens on a failure, the verdict itself, pass or fail, can be stored with the output by [LLM Content Validation Tracking](../llm-content-validation-tracking/), so later code knows what was checked.

The second call is not more generation. An ensemble averages several generations, and chain-of-thought elaborates one; this pattern spends the call on verification instead. Nor is it self-correction: a model asked to revise its own reasoning with no new signal shows no such gain and can even get worse ([Huang et al.](https://arxiv.org/abs/2310.01798), [Stechly et al.](https://arxiv.org/abs/2402.08115)). The check works because it asks a *different* question in a *separate* call, much as checking a proposed answer is often easier than finding one.

[^check-grammar]: `GrammarCorrectionService` in the `zeeguu/api` repository.



---
<div class="pattern-footer-nav"><a class="nav-prev" href="../defensive-output-parsing/">← Defensive Output Parsing</a><a class="nav-next" href="../llm-content-validation-tracking/">LLM Content Validation Tracking →</a></div>

[💬 Open an issue about this pattern](https://github.com/mircealungu/llm-integration-patterns/issues/new?title=%5BLLM-Checking-LLM%5D+&labels=feedback%2Ctrusting-llm-output&body=%2A%2ARe%3A%2A%2A+LLM-Checking-LLM%0A%2A%2ASection%3A%2A%2A+Trusting+LLM+Output%0A%2A%2APage%3A%2A%2A+https%3A%2F%2Fllm-patterns.mircealungu.com%2Fllm-checking-llm%2F%0A%0A%3C%21--+Your+feedback%2C+example%2C+or+counter-example+goes+here.+--%3E)
