# Hybrid Classical+LLM Pipeline

**Example (Zeeguu)**: Multi-word expression (MWE) detection runs Stanza's dependency parser first, as a cheap high-recall gate. If Stanza flags no candidate in a sentence, the LLM is never called. When it does flag one, an LLM re-analyzes the whole sentence and its verdict is used (and if the LLM finds no expression, its precision is trusted over Stanza's). The LLM therefore runs on only the fraction of sentences that might contain an expression, rather than on every sentence.    

**Forces**: Classical NLP tools (dependency parsers, POS taggers, rule-based extractors) are fast and deterministic but miss edge cases. LLMs handle edge cases well but are expensive to run on every input. Neither alone achieves both high recall and high precision.    

**Solution**: Run the cheap classical tool first, as a high-recall gate: invoke the LLM only when the classical stage fires, and skip it otherwise (the common case, and the main cost saving). When it fires, let the LLM make the precision decision. The two are not alternatives: the classical stage controls *when* the LLM runs; the LLM controls *what counts*.    

**Tradeoff**: Requires maintaining two systems, but the cost savings from not sending every input to the LLM typically justify the complexity.
