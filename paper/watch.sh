#!/bin/bash
# Rebuild paper.pdf from the live vault whenever a chapter or diagram changes,
# and keep it open in Skim (which reloads the file on its own).
#   paper/watch.sh        Ctrl-C to stop
cd "$(dirname "$0")/.."
[ -f ~/.local_envvars.sh ] && source ~/.local_envvars.sh
export PATH="/opt/homebrew/bin:/Library/TeX/texbin:$PATH"
VAULT="${AIPAT_VAULT%/}"

STAMP=$(mktemp); trap 'rm -f "$STAMP"' EXIT

build() {
    touch "$STAMP"
    echo "[$(date +%H:%M:%S)] building..."
    # diagrams/build.sh only rebuilds diagrams whose .tex is newer than their PDF
    "$VAULT/diagrams/build.sh" >/dev/null || echo "  diagram build failed"
    if python3 paper/build_paper.py --vault >/tmp/aipat-paper-build.log 2>&1; then
        echo "[$(date +%H:%M:%S)] ok"
    else
        echo "[$(date +%H:%M:%S)] FAILED, see /tmp/aipat-paper-build.log"; tail -5 /tmp/aipat-paper-build.log
    fi
}

build
open -a Skim paper/paper.pdf

# -l 2: wait 2s so a burst of saves is one batch. Paths are filtered here rather
# than with fswatch -e/-i, where an include overrides a later exclude. Generated
# diagram images are skipped, or each diagram rebuild would trigger another build.
# A path counts only if it is newer than the last build: iCloud sends a second
# event for a just-saved file without changing it.
dirty=false
fswatch -r -l 2 --batch-marker=BATCH "$VAULT" | while read -r path; do
    if [ "$path" = BATCH ]; then
        $dirty && build
        dirty=false
        continue
    fi
    case "$path" in
        */_meta/*|*/.obsidian/*|*/images/*-diagram.*) ;;
        *.md|*.tex|*.png|*.svg|*.jpg|*.jpeg|*.pdf) [ "$path" -nt "$STAMP" ] && dirty=true ;;
    esac
done
