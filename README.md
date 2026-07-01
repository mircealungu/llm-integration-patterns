# Architectural Patterns for Integrating LLMs into User-Facing Applications

*Lessons from a language-learning platform.*

A living catalogue of recurring patterns for integrating LLMs **as components into existing user-facing applications** (managing their cost, latency, quality, and lifecycle), grounded in production experience with [Zeeguu](https://zeeguu.unibe.ch/).

It is a working paper, developed in the open and revised as the ideas (and the tools) mature. **Feedback and contributions are very welcome.**

📖 **Read it:** https://patterns.mircealungu.com/

## Structure

The source lives in [`_src/`](_src/) and mirrors the site one-to-one:

- `00 Intro.md` → the home page (*What is this?* + *The Idea*).
- `00a Case Study - Zeeguu.md` → a **case study** page. Any file titled `# Case Study: X` becomes its own page, listed under *Case Studies* on the home page.
- **Category folders** like `01 Cost Optimization Patterns/` → each `.md` inside is one **pattern** page (its `# H1` is the pattern name); the folder name is the category heading on the home page.
- `07 Related Work.md`, `08 LLM-Specific.md`, `10 Possible Paper Contributions.md` → one prose page each.

To **add a pattern**, drop a `# Pattern Name` file into the right category folder. To **add a category**, make a new numbered folder. The leading `NN ` on folders and files only sets ordering; it is stripped from the displayed title. Page URLs come from the pattern name (its *slug*), not the file path, so moving or renumbering files never changes a URL.

At publish time, [`build.py`](build.py) assembles the multi-page site: a home page (`index.md`) with the intro and a catalogue, one page per pattern, one per case study, and the prose pages. It also auto-links `*Pattern Name*` cross-references and turns `![[image]]` embeds into responsive figures. **The generated `.md` files at the repo root are produced by the build; do not hand-edit them.**

## Contributing

Contributions come in two forms:

- **An instance.** Have you seen one of these patterns in another system? Say so, with a counter-example or a force we missed. This is the lightest and most useful contribution: each extra instance strengthens the pattern. Use the pre-filled "Open an issue" link on any pattern page, or a pull request against [`_src/`](_src/).
- **A case study.** Is your production system a rich example from a *different* domain? It can become its own case study page alongside Zeeguu (add a `# Case Study: <name>` file under [`_src/`](_src/); the build lists it automatically). Good candidates are real systems that exhibit several of the patterns.

Each pattern follows the standard format: **Example → Forces → Solution → Notes/Tradeoffs**. Contributors who substantively shape or add a pattern or case study receive **named credit** on the paper and the site.

## Editing workflow (maintainer)

Source lives in an Obsidian vault (including this README). `sync.sh` rsyncs the vault into `_src/`, copies the README to the repo root, runs `build.py`, commits, and pushes. The site is served by GitHub Pages (cayman theme) at `patterns.mircealungu.com`.
