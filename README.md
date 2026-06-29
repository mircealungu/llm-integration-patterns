# Architectural Patterns for Integrating LLMs into User-Facing Applications

A living catalogue of recurring patterns for integrating LLMs **as components into existing user-facing applications** — managing their cost, latency, quality, and lifecycle — grounded in production experience with [Zeeguu](https://zeeguu.unibe.ch/).

It is a working paper, developed in the open and revised as the ideas (and the tools) mature. **Feedback and contributions are very welcome.**

📖 **Read it:** https://patterns.mircealungu.com/

## Structure

The paper is written as numbered chapter files, kept in [`_src/`](_src/) (`00 Intro.md` … `10 Possible Paper Contributions.md`). At publish time [`build.py`](build.py) explodes them into a multi-page site: a home page (`index.md`) with the intro and a catalogue, one page per pattern, and a page each for Related Work / LLM-Specific / Contributions. All generated `.md` files at the repo root are produced by the build — do not hand-edit them.

## Contributing

Have a complementary example, a counter-example, or a pattern we missed? Open an issue or a pull request against the chapter files in [`_src/`](_src/). Each pattern follows the standard format: **Example → Forces → Solution → Notes/Tradeoffs**.

## Editing workflow (maintainer)

Source lives in an Obsidian vault. `sync.sh` rsyncs it into `_src/`, runs `build.py`, commits, and pushes. The site is served by GitHub Pages (cayman theme) at `patterns.mircealungu.com`.
