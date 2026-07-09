# Trusting LLM Output

An LLM's output is only probabilistically correct, and only probabilistically well-formed, yet it flows into code and data that assume it is neither wrong nor malformed. The patterns in this section guard that boundary: refusing to trust the shape of a response, catching content errors with a second, narrower check, recording how far each stored piece of output has been trusted. The unifying force is non-determinism: the same prompt can return a different, or malformed, answer, so correctness has to be enforced around the model rather than assumed from it.
