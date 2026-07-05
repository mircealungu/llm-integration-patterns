# Temperature as Task Selector

## Example

Translation validation uses temperature 0 for deterministic yes/no judgments. Audio lesson script generation uses temperature 0.8 to produce varied, natural-sounding dialogues. The same model serves both purposes with different configuration.

## Forces

LLMs exhibit different behaviors at different temperature settings. Classification and validation tasks benefit from deterministic outputs (low temperature), while creative generation benefits from variety (higher temperature). Using a single temperature for all tasks either sacrifices reliability or creativity.

## Solution

Systematically vary temperature based on task type. Use temperature 0–0.3 for tasks requiring consistency (validation, classification, structured extraction). Use temperature 0.7–1.0 for tasks requiring creativity (dialogue generation, example variety).

## Note

This pattern acknowledges that a single LLM can behave as multiple "virtual components" depending on configuration: deterministic validator vs. creative generator.

## Known Uses

- **Vendor guidance**: [Anthropic's Messages API](https://platform.claude.com/docs/en/api/messages) advises temperature near 0 for analytical/multiple-choice tasks and near 1 for creative ones; the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/blob/main/examples/Multiclass_classification_for_transactions.ipynb) hard-codes `temperature=0` for classification.
- **Azure OpenAI** guidance recommends 0–0.3 for extraction/categorization and 0.7–1.0 for creative generation.
- *Caveat worth keeping.* [Renze & Guven](https://arxiv.org/abs/2402.05201) (EMNLP Findings 2024) found temperature 0.0–1.0 has *no* statistically significant effect on problem-solving accuracy — evidence that this pattern's justification is determinism/consistency and output variety, not correctness.

> [!draft]- Notes after the focus group
> - very model dependent 
> - can of worms?
> - zero - follow training data? 
> - 
