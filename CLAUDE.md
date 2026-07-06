# Working on the LLM Integration Patterns paper

The prose is authored in an **Obsidian vault** (the source of truth), mirrored into `content/` by `sync.sh`, built into the `web/` site and `paper/paper.pdf`, and deployed to GitHub Pages. **Edit the vault, never `content/` or `web/`** — those are generated and overwritten on every sync. The Zeeguu system code that grounds the examples lives at `github.com/zeeguu/api` (locally `~/code/zeeguu/api`).

## Writing voice — follow proactively (`check.py` is only a backstop)

- **No second person.** Never address the reader: avoid *you / your / you're / yourself*. Write impersonally — "How *can* X be done?", not "How do *you* do X?".
- **No em-dashes.** Use commas, parentheses, or colons instead of `—`; it reads as an AI tell.
- **Never use the word "interesting".**
- **No placeholders** in committed prose: no TODO / FIXME / TK / XXX / trailing `…`.

## Pattern template — canonical form for every pattern

`## Context` → `## Example` → `## Problem` → `## Forces` → `## Solution` → `## Consequences` → `## Notes` → `## Known Uses`

- Every section must add real signal. If `Problem` would only restate `Forces`, drop it rather than pad.
- **Context**: the specific recurring situation and preconditions (not "X is available").
- **Problem**: one sharp, pattern-specific question.
- **Consequences**: resolve the forces — benefit, then liability/tuning, then scope. This replaces ad-hoc `Notes` / `Tradeoff` sections.
- **Known Uses**: real, *documented* production deployments (engineering blogs, papers, case studies). Libraries and gateways that merely *enable* the pattern are enablers, not uses; label them as such rather than passing them off as instances. Fetch and verify a source before citing it (the web has fabricated LLM postmortems).
- Reference other patterns inline as *Pattern Name* in italics (the build auto-links them). A pattern's URL comes from its `# H1`, not the filename.

## Publishing

- `./sync.sh --non-interactive` pulls, mirrors the vault, rebuilds the site and PDF, commits, and pushes. `main` is protected; Mircea is on the bypass list, so the internal push works.
- The Pages deploy occasionally throttles ("Deployment failed, try again later"); the workflow retries once, and a failed run can be re-run with `gh run rerun <id> --failed`. Batch changes into fewer syncs to stay under the rate limit.
- Collaborators (e.g. Cesare / @pautasso) contribute via PRs against `content/`; on merge, `sync.sh` reverse-imports their changes into the vault before the forward mirror.
