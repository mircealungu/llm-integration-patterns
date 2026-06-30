# Architectural Patterns for Integrating LLMs into User-Facing Applications

*Lessons from a language-learning platform.*

A living catalogue of recurring patterns for integrating LLMs **as components into existing user-facing applications** — managing their cost, latency, quality, and lifecycle — grounded in production experience with [Zeeguu](https://zeeguu.unibe.ch/).

It is a working paper, developed in the open and revised as the ideas (and the tools) mature. **Feedback and contributions are very welcome.**

📖 **Read it:** https://patterns.mircealungu.com/

## Structure

The paper is written as numbered chapter files, kept in [`_src/`](_src/):

- `00 Intro.md` → the home page (*What is this?* + *The Idea*).
- `00a Case Study - Zeeguu.md` → a **case study** page. Any file titled `# Case Study: X` becomes its own page, listed under *Case Studies* on the home page.
- `01`–`06`, `09` (`* Patterns`) → each `## ` section becomes its own **pattern** page.
- `07 Related Work`, `08 LLM-Specific`, `10 Possible Paper Contributions` → one page each.

At publish time, [`build.py`](build.py) explodes these into the multi-page site: a home page (`index.md`) with the intro and a catalogue, one page per pattern, one per case study, and the prose pages. **The generated `.md` files at the repo root are produced by the build — do not hand-edit them.**

## Contributing

Have a complementary example, a counter-example, or a pattern we missed? Open an issue (every page on the site has a pre-filled "Open an issue" link) or a pull request against the chapter files in [`_src/`](_src/). Each pattern follows the standard format: **Example → Forces → Solution → Notes/Tradeoffs**.

## Editing workflow (maintainer)

Source lives in an Obsidian vault (including this README). `sync.sh` rsyncs the vault into `_src/`, copies the README to the repo root, runs `build.py`, commits, and pushes. The site is served by GitHub Pages (cayman theme) at `patterns.mircealungu.com`.
