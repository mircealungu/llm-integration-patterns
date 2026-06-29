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

# Chapter sources live in _src/ (underscore = ignored by Jekyll). The stale
# Google-Doc export is left behind in the vault.
mkdir -p "$AIPAT_REPO/_src"
rsync -a --delete \
    --exclude='.DS_Store' \
    --exclude='.obsidian' \
    --exclude='sync.sh' \
    --exclude='(Design_)*' \
    "$AIPAT_VAULT" "$AIPAT_REPO/_src/"

# Explode chapters into a home page + one page per pattern.
python3 build.py

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
