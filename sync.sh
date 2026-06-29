#!/bin/bash
# Sync the AI Patterns content from the Obsidian vault into this repo and push.
# Mirrors the mircealungu.com publish pattern: vault is the editing surface,
# this repo (outside iCloud) is the git source of truth + GitHub Pages site.

cd "$(dirname "$0")"
[ -f ~/.local_envvars.sh ] && source ~/.local_envvars.sh

if [ -z "$AIPAT_VAULT" ] || [ -z "$AIPAT_REPO" ]; then
    echo "AIPAT_VAULT / AIPAT_REPO not set (see ~/.local_envvars.sh)" >&2
    exit 1
fi

# Pull the chapter Markdown from the vault. Repo-only files are excluded so
# --delete does not wipe them, and the stale Google-Doc export is left behind.
rsync -a --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='.obsidian' \
    --exclude='sync.sh' \
    --exclude='README.md' \
    --exclude='_config.yml' \
    --exclude='index.md' \
    --exclude='(Design_)*' \
    "$AIPAT_VAULT" "$AIPAT_REPO"

# Build the single-page GitHub Pages document from the numbered chapters.
{
    echo "---"
    echo "title: Architectural Patterns for Integrating LLMs into User-Facing Applications"
    echo "---"
    echo
    for f in [0-9]*.md; do
        cat "$f"
        echo
        echo
    done
} > index.md

# Stage any new untracked files.
NEW_FILES=$(git ls-files --others --exclude-standard)
if [ -n "$NEW_FILES" ]; then
    if [ "$1" = "--non-interactive" ]; then
        git add -A
    else
        echo "New untracked files:"
        echo "$NEW_FILES"
        echo ""
        read -p "Add and commit these new files? (y/n) " answer
        [ "$answer" != "y" ] && exit 0
        git add -A
    fi
fi

# Anything to commit?
if git diff --quiet HEAD && git diff --quiet --cached HEAD; then
    echo "No changes to commit."
    exit 0
fi

if [ "$1" = "--non-interactive" ]; then
    git commit -aqm "update patterns"
    git push --quiet
    echo "Pushed."
else
    echo ""
    git --no-pager diff --stat HEAD
    echo ""
    read -p "Commit all and push? (y/n) " answer
    [ "$answer" != "y" ] && exit 0
    git commit -aqm "update patterns"
    git push
    echo "Pushed."
fi
