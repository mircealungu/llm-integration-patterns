# LLM-Checking-LLM

## Context

An LLM generates content that will be used or stored, and its output is sometimes wrong in ways a targeted check could catch. Verifying a specific property (grammaticality, factual match, difficulty level) is a narrower task than the open-ended generation that produced it.

## Examples

The vocabulary exercises need example sentences for each word, which an LLM generates at the learner's level, an open-ended task (the sentence must be natural, level-appropriate, and actually use the word). A generated sentence can still be wrong in a specific way: it may use the word in a *different* sense than the one being taught. For the Danish *virker* (translated as *seem*), a generated sentence might use *virker* in its other sense, *work/function*. A second, batched LLM call then asks one narrow question of each sentence, whether it uses the word in the intended [meaning](../zeeguu/#the-learner-model), and drops the ones that fail. Verifying that single property is far narrower than writing a good sentence from scratch.

A second pair ran on [article simplification](../zeeguu/#article-simplification), and has since been switched off, which is what makes it worth reporting. Rewriting an article to a lower CEFR level is open-ended; whether the result is grammatical is not. A second call read each simplified title and body and returned corrections, which were applied to the text.[^check-grammar] Between December 2025 and April 2026 we measured what it caught: roughly 96% of title corrections and 72% of body corrections changed two characters or fewer. The check worked. What it found was not worth what it cost, and it is now disabled by default.

The two pairs differ in what happens on failure, which the pattern deliberately leaves open: an example sentence is expendable, so it is dropped and another word used, while a simplified article is the only version at that level, so the check produced a correction instead. But the retired pair carries the sharper lesson. The asymmetry that makes verification cheaper than generation says nothing about whether the errors are worth catching. That is a separate question, and only measurement answers it.

[^check-grammar]: `GrammarCorrectionService` in the `zeeguu/api` repository.

## Problem

How can an unreliable generator's mistakes be caught, when a second generator would be just as unreliable?


## Forces

- **Verification is narrower than generation.** Checking one property (is it grammatical? does it use the intended meaning?) has a small answer space and a clear criterion, so a focused checker is more reliable on that property than the open-ended generation was: the *generation-discrimination gap* measured by [Saunders et al.](https://arxiv.org/abs/2206.05802). *(pushes toward adding a check)*
- **The checker is itself an LLM.** It can return its own false verdicts, and it costs a full extra call in tokens and latency. *(pushes toward checking only where the asymmetry is large, or where a classical check exists)*
- **The mistakes must be checkable in isolation.** The pattern helps only for errors a targeted, differently-prompted call can catch, not for failures that need the whole generation redone.

## Solution

Use one LLM call to generate a result, then a separate, differently-prompted LLM call to check one specific property of it. This escapes the paradox for two reasons. First, verifying one property (is it grammatical? does it use the intended meaning?) has a small, well-defined answer space and a clear success criterion, so an LLM does it more reliably than the open-ended generation that produced the output. Second, because the checker is prompted differently and asked a different question, its errors are largely *decorrelated* from the generator's rather than shared, so it does not simply repeat the generator's mistakes.

A failed check still needs a policy, and the pattern does not fix one. Dropping the result is cheapest and fits where the item is expendable (the vocabulary sentences above are discarded and other words used instead). Regenerating recovers the item, and works better when the retry is told what went wrong: a plain retry resamples the same distribution and can fail the same way, whereas a prompt extended with the rejected output and the property it missed conditions the next attempt on the failure. Either way it multiplies calls, so it wants a bounded number of attempts rather than a loop. Where neither fits, the verdict can be recorded alongside the output instead of acted on, which is *LLM Content Validation Tracking*. And where a failure is permanent for that input rather than incidental, recording the terminal state stops a scheduled job rediscovering it on every run.

## Consequences

- **A focused check is more reliable than the generation.** Verifying one property is easier than producing the whole output, so the second call catches errors the first introduced, for the price of one extra call.
- **It narrows the error rate, it does not remove it.** The checker is itself an LLM and can return its own false verdicts, and it adds cost and latency.
- **The pair hides behind one interface, not behind a guarantee.** Generation and check can be packaged as a single call, so the rest of the application never sees the judge. That is a convenience, not a contract: the result is still best-effort, exactly as it would be from the generator alone.
- **It pays off only when checking is genuinely narrower than generating.** A check as open-ended as the generation buys little. The verdict composes with *LLM Content Validation Tracking* (record it), and where a classical check exists it is cheaper still.

## Known Uses

- *Documented in the literature.* **[LLM-as-a-judge](https://arxiv.org/abs/2306.05685)** (Zheng et al., NeurIPS 2023) uses a separate strong LLM to score another model's open-ended outputs, now a standard evaluation technique.
- **[Self-Refine](https://arxiv.org/abs/2303.17651)** (Madaan et al., NeurIPS 2023) has the model critique and refine *its own* output in a separate pass: a same-model variant of the idea, where this pattern instead uses a differently-prompted call.
- **[G-Eval](https://arxiv.org/abs/2303.16634)** (Liu et al., 2023), shipped in eval frameworks such as **[DeepEval](https://deepeval.com/docs/metrics-llm-evals)**, uses a separate chain-of-thought (step-by-step reasoning) judge call to grade generated output.

## Notes

- Where *Defensive Output Parsing* guards that the output is well-*formed*, this guards that a well-formed output is *correct*.
- Distinct from ensemble methods and chain-of-thought: an ensemble averages several generations and chain-of-thought elaborates one, whereas this pattern spends the second call on the cheaper *verification* task instead of more generation.
- *Why the asymmetry holds, and where it stops.* Spending a call on verification rather than generation echoes the intuition behind NP, the class of problems where a proposed answer can be checked quickly even when finding one may be hard: confirming a candidate can be far easier than producing it. The gain is empirical here, not guaranteed, and it depends on the check being a narrow, differently-prompted property. It does not extend to open-ended *intrinsic self-correction*, a model revising its own reasoning with no new signal, which shows no such gain and can even degrade accuracy (as [Huang et al.](https://arxiv.org/abs/2310.01798) and [Stechly et al.](https://arxiv.org/abs/2402.08115) find). That is why the check here asks a *different* question through a *separate* call, rather than asking the generator to reconsider.
- *This check may be transient.* It exists because today's models are imprecise enough to need an external verifier. As models improve, or as reliable self-verification moves inside the model itself, the need for a separate checking call may shrink: the pattern answers the current generation's reliability, not a permanent architectural truth.

> [!draft]- Notes after the focus group
> - LLM as a judge -- is this the same? 
> - be cynical prompting for an LLM when judging a paper, e.g. 
