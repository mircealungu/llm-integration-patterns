# LLM-Checking-LLM

## Example

After generating contextual example sentences for vocabulary words, a second LLM call reviews the examples for accuracy, naturalness, and appropriate difficulty level.

## Forces

LLMs are imprecise generators, but verification of specific properties (e.g., grammatical correctness) is a more constrained task than open-ended generation (e.g., text simplification). A second, focused LLM call can catch errors that the first, more complex call introduced.

## Solution

Use one LLM call to generate a result, then use a separate LLM call to check or refine it. The verification prompt can be simpler and more focused than the generation prompt.

## Note

This is distinct from ensemble methods or chain-of-thought: the key insight is that checking is a fundamentally easier task than generating, and this asymmetry can be exploited architecturally.

## Known Uses

- **[LLM-as-a-judge](https://arxiv.org/abs/2306.05685)** (Zheng et al., NeurIPS 2023) uses a separate strong LLM to score another model's open-ended outputs.
- **[Self-Refine](https://arxiv.org/abs/2303.17651)** (Madaan et al., NeurIPS 2023): a separate pass critiques and refines the first output.
- **[G-Eval](https://arxiv.org/abs/2303.16634)** (Liu et al., 2023), shipped in eval frameworks such as **[DeepEval](https://deepeval.com/docs/metrics-llm-evals)**, uses a separate chain-of-thought judge call to grade generated output.
- *Contrast.* Unlike self-critique on the same reasoning, this pattern uses a differently-prompted call to check a *different property* (see *Related Work* on Stechly et al.).

> [!draft]- Notes after the focus group
> - LLM as a judge -- is this the same? 
> - be cynical prompting for an LLM when judging a paper, e.g. 
