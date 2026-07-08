# LLM-Checking-LLM

## Context

An LLM generates content that is sometimes wrong in ways a targeted check could catch. It is possible to specify how to verify compliance of the content against a specific property as a narrower task than the open-ended generation that produced it.

## Example

After generating contextual example sentences for vocabulary words, a second LLM call reviews the examples for accuracy, naturalness, and appropriate difficulty level.

## Problem

How can an unreliable generator's mistakes be caught, when a second generator would be just as unreliable?

## Forces

LLMs can perform both open-ended generation tasks as well as verification of specific properties (e.g., grammatical correctness, factual match, difficulty level), a more constrained task than open-ended generation (e.g., [article simplification](../zeeguu/#article-simplification), rewriting a text at a simpler reading level). A second, focused LLM call can sometimes catch errors that the first, more complex call introduced. Each LLM call has a cost and adds latency.

The caller of the LLM should not have to be concerned about whether the property is satisfied by the result.

## Solution

Use one LLM call to generate a result, then use a separate LLM call to check or refine it. This escapes the paradox because verifying one specific property (is it grammatical? does it match the source?) is a narrower task than the open-ended generation prompt that produced the output, so the checker fails less often on that property while the generator may have ignored it. The verification prompt should be simpler and more focused than the generation prompt.

## Consequences

- **A focused check is more reliable than the generation.** Verifying one property is easier than producing the whole output, so the second call catches errors the first introduced, for the price of one extra call.
- **It narrows the error rate, it does not remove it.** The checker is itself an LLM and can return its own false verdicts. The caller should not expect full compliance, just like if it was directly calling the LLM to generate the result.
- **It pays off only when checking is genuinely narrower than generating.** A check as open-ended as the generation buys little.

## Related Patterns

The LLM-checking-LLM verdict composes with *LLM Content Validation Tracking* (record it) and could be replaced by or combined by an inverted *Hybrid Classical+LLM Pipeline* (a classical downstream check is cheaper still, where one exists).

## Known Uses

- **[LLM-as-a-judge](https://arxiv.org/abs/2306.05685)** (Zheng et al., NeurIPS 2023) uses a separate strong LLM to score another model's open-ended outputs.
- **[Self-Refine](https://arxiv.org/abs/2303.17651)** (Madaan et al., NeurIPS 2023): a separate pass critiques and refines the first output.
- **[G-Eval](https://arxiv.org/abs/2303.16634)** (Liu et al., 2023), shipped in eval frameworks such as **[DeepEval](https://deepeval.com/docs/metrics-llm-evals)**, uses a separate chain-of-thought judge call to grade generated output.
- *Contrast.* Unlike self-critique on the same reasoning, this pattern uses a differently-prompted call to check a *different property* (see *Related Work* on Stechly et al.).

## Notes

This is distinct from ensemble methods or chain-of-thought: the key insight is that checking is a fundamentally easier task than generating, and this asymmetry can be exploited architecturally.

> [!draft]- Notes after the focus group
> - LLM as a judge -- is this the same? 
> - be cynical prompting for an LLM when judging a paper, e.g. 
