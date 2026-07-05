#!/bin/bash
# Publish the AI Patterns paper: pull chapter sources from the Obsidian vault,
# build the multi-page Jekyll site, commit, and push.
#
# Vault is the editing surface; this repo (outside iCloud) is the git source of
# truth + GitHub Pages site (served at patterns.mircealungu.com once DNS is set).

cd "$(dirname "$0")"
[ -f ~/.local_envvars.sh ] && source ~/.local_envvars.sh

if [ -z "$AIPAT_VAULT" ] || [ -z "$AIPAT_REPO" ]; then
    echo "AIPAT_VAULT / AIPAT_REPO not set (see ~/.local_envvars.sh)" >&2
    exit 1
fi

# --- Pull collaborator PRs and guard against same-file collisions ----------
# main is protected: collaborators only open PRs; the maintainer merges on
# GitHub, then runs this. We pull the merge and reverse-import the changed
# chapter sources back into the vault (the editing surface) BEFORE the normal
# vault -> _src mirror, so that mirror's --delete can't wipe the merged work.
#
# The pre-pull HEAD is the last-synced state (every sync ends by committing an
# _src that equals the vault), so git itself is the collision baseline — no
# manifest to keep. Note: PR deletions are NOT propagated to the vault (the
# reverse import has no --delete); remove such files by hand.
BASE=$(git rev-parse HEAD)
git pull --ff-only --quiet || {
    echo "git pull --ff-only failed (local commits or a real conflict?). Resolve, then re-run." >&2
    exit 1
}

# A file edited in BOTH the vault and a just-merged PR is a genuine conflict
# that neither rsync nor git can resolve (the vault copy lives outside git).
# Detect and stop rather than silently overwrite either side.
conflicts=()
while IFS= read -r -d '' path; do
    rel=${path#_src/}
    vfile="$AIPAT_VAULT$rel"
    [ -f "$vfile" ] || continue          # new PR file the vault lacks: not a conflict
    if ! diff -q <(git show "$BASE:$path" 2>/dev/null) "$vfile" >/dev/null 2>&1; then
        conflicts+=("$rel")              # vault differs from baseline => also edited here
    fi
done < <(git diff -z --name-only "$BASE" HEAD -- _src/)

if [ ${#conflicts[@]} -gt 0 ]; then
    echo "CONFLICT — edited in BOTH the vault and a merged PR:" >&2
    printf '  - %s\n' "${conflicts[@]}" >&2
    echo "Reconcile these by hand in the vault, then re-run sync." >&2
    exit 1
fi

# Reverse import: bring the merged (non-conflicting) PR edits into the vault.
# No --delete (never drop a vault file just because _src lacks it — _src is a
# subset). -u keeps a newer vault file; --backup preserves anything overwritten.
if [ "$BASE" != "$(git rev-parse HEAD)" ]; then
    rsync -a -u \
        --backup --backup-dir="$AIPAT_REPO/.sync-backups/reverse-$(date +%Y%m%d-%H%M%S)" \
        --exclude='.DS_Store' --exclude='sync.sh' \
        "$AIPAT_REPO/_src/" "$AIPAT_VAULT"
    echo "Reverse-imported merged PR edits into the vault."
fi

# Chapter sources live in _src/ (underscore = ignored by Jekyll). The stale
# Google-Doc export is left behind in the vault.
mkdir -p "$AIPAT_REPO/_src"
rsync -a --delete \
    --exclude='.DS_Store' \
    --exclude='.obsidian' \
    --exclude='sync.sh' \
    --exclude='(Design_)*' \
    --exclude='_*' \
    "$AIPAT_VAULT" "$AIPAT_REPO/_src/"

# The README is edited in the vault but lives at the repo root (it's the
# GitHub landing page, not a site page).
[ -f "$AIPAT_REPO/_src/README.md" ] && cp "$AIPAT_REPO/_src/README.md" "$AIPAT_REPO/README.md"

# Images: vault images/ -> served /images/ (kept out of assets/ so it never
# collides with the theme override at assets/css/).
if [ -d "$AIPAT_REPO/_src/images" ]; then
    mkdir -p "$AIPAT_REPO/images"
    rsync -a --delete "$AIPAT_REPO/_src/images/" "$AIPAT_REPO/images/"
fi

# Explode chapters into a home page + one page per pattern.
python3 build.py

# Pre-publish checks (broken links/images block; voice/placeholders warn).
python3 check.py || { echo "Pre-publish checks failed — not pushing."; exit 1; }

# Commit + push.
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit."
    exit 0
fi

if [ "$1" = "--non-interactive" ]; then
    git add -A
    git commit -qm "update patterns"
    git push --quiet
    echo "Pushed."
else
    git add -A
    git --no-pager diff --cached --stat
    echo ""
    read -p "Commit all and push? (y/n) " answer
    [ "$answer" != "y" ] && exit 0
    git commit -qm "update patterns"
    git push
    echo "Pushed."
fi
