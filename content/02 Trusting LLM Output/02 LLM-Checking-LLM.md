# LLM-Checking-LLM

## Context

An LLM generates content that will be used or stored, and its output is sometimes wrong in ways a targeted check could catch. Verifying a specific property (grammaticality, factual match, difficulty level) is a narrower task than the open-ended generation that produced it.

## Example

The vocabulary exercises need example sentences for each word, which an LLM generates at the learner's level, an open-ended task (the sentence must be natural, level-appropriate, and actually use the word). A generated sentence can still be wrong in a specific way: it may use the word in a *different* sense than the one being taught. For the Danish *virker* (translated as *seem*), a generated sentence might use *virker* in its other sense, *work/function*. A second, batched LLM call then asks one narrow question of each sentence, whether it uses the word in the intended [meaning](../zeeguu/#the-learner-model), and drops the ones that fail. Verifying that single property is far narrower than writing a good sentence from scratch.

## Problem

How can an unreliable generator's mistakes be caught, when a second generator would be just as unreliable?

## Forces

- **Verification is narrower than generation.** Checking one property (is it grammatical? does it use the intended meaning?) has a small answer space and a clear criterion, so a focused checker is more reliable on that property than the open-ended generation was: the *generation-discrimination gap* measured by [Saunders et al.](https://arxiv.org/abs/2206.05802). *(pushes toward adding a check)*
- **The checker is itself an LLM.** It can return its own false verdicts, and it costs a full extra call in tokens and latency. *(pushes toward checking only where the asymmetry is large, or where a classical check exists)*
- **The mistakes must be checkable in isolation.** The pattern helps only for errors a targeted, differently-prompted call can catch, not for failures that need the whole generation redone.

## Solution

Use one LLM call to generate a result, then a separate, differently-prompted LLM call to check one specific property of it. This escapes the paradox for two reasons. First, verifying one property (is it grammatical? does it use the intended meaning?) has a small, well-defined answer space and a clear success criterion, so an LLM does it more reliably than the open-ended generation that produced the output. Second, because the checker is prompted differently and asked a different question, its errors are largely *decorrelated* from the generator's rather than shared, so it does not simply repeat the generator's mistakes.

## Consequences

- **A focused check is more reliable than the generation.** Verifying one property is easier than producing the whole output, so the second call catches errors the first introduced, for the price of one extra call.
- **It narrows the error rate, it does not remove it.** The checker is itself an LLM and can return its own false verdicts, and it adds cost and latency.
- **It pays off only when checking is genuinely narrower than generating.** A check as open-ended as the generation buys little. The verdict composes with *LLM Content Validation Tracking* (record it) and *Hybrid Classical+LLM Pipeline* (a classical check is cheaper still, where one exists).

## Known Uses

- *Documented in the literature.* **[LLM-as-a-judge](https://arxiv.org/abs/2306.05685)** (Zheng et al., NeurIPS 2023) uses a separate strong LLM to score another model's open-ended outputs, now a standard evaluation technique.
- **[Self-Refine](https://arxiv.org/abs/2303.17651)** (Madaan et al., NeurIPS 2023) has the model critique and refine *its own* output in a separate pass: a same-model variant of the idea, where this pattern instead uses a differently-prompted call.
- **[G-Eval](https://arxiv.org/abs/2303.16634)** (Liu et al., 2023), shipped in eval frameworks such as **[DeepEval](https://deepeval.com/docs/metrics-llm-evals)**, uses a separate chain-of-thought (step-by-step reasoning) judge call to grade generated output.

## Notes

- Where *Defensive Output Parsing* guards that the output is well-*formed*, this guards that a well-formed output is *correct*.
- Distinct from ensemble methods and chain-of-thought: an ensemble averages several generations and chain-of-thought elaborates one, whereas this pattern spends the second call on the cheaper *verification* task instead of more generation.
- *Why the asymmetry holds, and where it stops.* Spending a call on verification rather than generation echoes the intuition behind NP: confirming a candidate can be far easier than producing one. The gain is empirical here, not guaranteed, and it depends on the check being a narrow, differently-prompted property. It does not extend to open-ended *intrinsic self-correction*, a model revising its own reasoning with no new signal, which shows no such gain and can even degrade accuracy (as [Huang et al.](https://arxiv.org/abs/2310.01798) and [Stechly et al.](https://arxiv.org/abs/2402.08115) find). That is why the check here asks a *different* question through a *separate* call, rather than asking the generator to reconsider.
- *This check may be transient.* It exists because today's models are imprecise enough to need an external verifier. As models improve, or as reliable self-verification moves inside the model itself, the need for a separate checking call may shrink: the pattern answers the current generation's reliability, not a permanent architectural truth.

> [!draft]- Notes after the focus group
> - LLM as a judge -- is this the same? 
> - be cynical prompting for an LLM when judging a paper, e.g. 
