# Architectural Patterns for Integrating LLMs into User-Facing Applications

A living catalogue of recurring patterns for integrating LLMs **as components into existing user-facing applications** — managing their cost, latency, quality, and lifecycle — grounded in production experience with [Zeeguu](https://zeeguu.unibe.ch/).

It is a working paper, developed in the open and revised as the ideas (and the tools) mature. **Feedback and contributions are very welcome.**

📖 **Read it:** https://mircealungu.github.io/llm-integration-patterns/

## Structure

The paper is written as numbered chapter files (`00 Intro.md` … `10 Possible Paper Contributions.md`). The GitHub Pages site (`index.md`) is generated from these by concatenation at publish time.

## Contributing

Have a complementary example, a counter-example, or a pattern we missed? Open an issue or a pull request against the numbered chapter files. Each pattern follows the standard format: **Example → Forces → Solution → Notes/Tradeoffs**.

## Editing workflow (maintainer)

Source lives in an Obsidian vault; `sync.sh` rsyncs it here, rebuilds `index.md`, commits, and pushes. Do not hand-edit `index.md` — it is regenerated on every sync.
