# Data Management

LLM output that lands in persistent storage becomes a long-lived asset, reused long after the prompt and model that produced it have moved on. These patterns manage that stored output as it ages. *LLM Output Provenance* stamps each artifact with the model and prompt that made it, so exactly the stale ones can be found and regenerated when something improves. *Soft Invalidation of LLM Artifacts* then retires the stale ones without breaking the past, deprecating rather than deleting and regenerating lazily on next demand while old references keep resolving.
