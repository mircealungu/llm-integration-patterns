# Hybrid Pipeline Patterns

## Hybrid Classical+LLM Pipeline

**Example (Zeeguu)**: Multi-word expression (MWE) detection uses Stanza's dependency parser to identify candidate phrases (fast, high recall), then sends candidates to an LLM to filter out false positives based on semantic analysis (slower, high precision). This achieves better F1 than either approach alone, at a fraction of the cost of LLM-only detection.    

**Forces**: Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.    

**Solution**: Use the classical tool as a high-recall candidate generator, then use the LLM as a precision filter on the candidates. Both tools work together in a pipeline, not as alternatives.    

**Tradeoff**: Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity. 
