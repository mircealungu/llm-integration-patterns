# Lifecycle Management

An LLM integration is not static: the models behind it are retired and re-priced on the vendor's schedule, and the role the LLM plays in a feature changes as the system matures. These patterns manage that evolution over time. *Rent, Then Build* treats the LLM as a temporary stand-in, shipping a feature on rented general capability now while a cheaper, dedicated replacement is built. *Centralized Model Selection* keeps every model identifier in one place, so a vendor retiring a dated snapshot is a one-line change rather than a hunt across the codebase.
