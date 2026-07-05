# Cost Optimization

We use *cost* as shorthand for any expensive, metered resource — most visibly the per-token API bill, but also latency, compute, and energy. The unifying force is that LLM calls carry a large, often *fixed* overhead (the instructional prompt, the network round-trip), so invoking them naïvely wastes that setup on a tiny payload.

These patterns are really about *economy*: **amortizing a fixed overhead** across many uses (*Prompt Amortization*), and **paying the expensive resource only in proportion to the value returned** (*Escalate to the LLM*). The same frugality transfers to non-monetary resources — which is why Prompt Amortization cuts latency as well as dollars.
