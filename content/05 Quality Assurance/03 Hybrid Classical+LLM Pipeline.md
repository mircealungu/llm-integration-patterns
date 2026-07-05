# Hybrid Classical+LLM Pipeline

## Example

Multi-word expression (MWE) detection runs Stanza's dependency parser first, as a cheap high-recall gate. If Stanza flags no candidate in a sentence, the LLM is never called. When it does flag one, an LLM re-analyzes the whole sentence and its verdict is used (and if the LLM finds no expression, its precision is trusted over Stanza's). The LLM therefore runs on only the fraction of sentences that might contain an expression, rather than on every sentence.

## Forces

Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.

## Solution

Run the cheap classical tool first, as a high-recall gate: invoke the LLM only when the classical stage fires, and skip it otherwise (the common case, and the main cost saving). When it fires, let the LLM make the precision decision. The two are not alternatives: the classical stage controls *when* the LLM runs; the LLM controls *what counts*.

## Tradeoff

Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity.

## Note

Close kin to *Escalate to the LLM* and to a model cascade: all three run a cheap step first and call the LLM selectively. The difference is the trigger. Escalate uses the cheap tool's answer and reaches for the LLM only when it is inadequate (a failure, or user dissatisfaction); here the cheap tool gates on detected difficulty (a flagged candidate) and the LLM's verdict replaces it, as in a confidence-based cascade.

## Known Uses

- **[RankGPT](https://arxiv.org/abs/2304.09542)** (Sun et al., EMNLP 2023) uses BM25 to retrieve ~100 candidates, then an LLM for listwise reranking — classical high-recall generator + LLM precision filter.
- **[spaCy-llm](https://github.com/explosion/spacy-llm)** (Explosion) is designed to mix LLM components with classical/rule-based ones in a single pipeline.
- **Retrieve-then-rerank** (e.g. [Cohere Rerank](https://docs.cohere.com/docs/rerank-overview)) keeps a high-recall first-stage search and adds a neural precision reranker.

> [!draft]- Notes after the focus group
> - Hybrid Pipeline: Classical + LLM 
> - Chain of Delegation ? 
> - Is this a Pipeline ?
