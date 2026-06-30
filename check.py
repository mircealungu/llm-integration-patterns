#!/usr/bin/env python3
"""Pre-publish checks. Run by sync.sh after build.py, before commit/push.

ERRORS (exit 1 — block the push): broken internal links and missing images in
the generated site. These are deterministic, no network.

WARNINGS (printed, never block): second-person voice and placeholder markers,
checked only on lines ADDED since the last commit — so pre-existing prose is
not re-flagged every sync, and genuinely new regressions surface.
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
errors, warnings = [], []

# --- ERRORS: internal links + image refs in the generated pages ---
pages = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(ROOT, "*.md"))}
for f in glob.glob(os.path.join(ROOT, "*.md")):
    name = os.path.basename(f)
    if name == "README.md":
        continue
    text = open(f, encoding="utf-8").read()
    for m in re.finditer(r"\]\(([a-z0-9][a-z0-9-]*)/\)", text):   # ](slug/)
        if m.group(1) not in pages:
            errors.append(f"{name}: link to /{m.group(1)}/ but no {m.group(1)}.md")
    for m in re.finditer(r"/images/([^\s\"')]+)", text):          # /images/FILE
        if not os.path.exists(os.path.join(ROOT, "images", m.group(1))):
            errors.append(f"{name}: image /images/{m.group(1)} is missing")

# --- WARNINGS: voice + placeholders, on added source lines only ---
diff = subprocess.run(["git", "diff", "--unified=0", "--", "_src"],
                      cwd=ROOT, capture_output=True, text=True).stdout
added = [ln[1:] for ln in diff.splitlines()
         if ln.startswith("+") and not ln.startswith("+++")]
# Lexical rules from the writing guidelines (warn-only — human judges):
#   "Do Not Address the Reader" and "Never Use The Word Interesting".
VOICE = re.compile(r"\b(you|your|you're|you'll|yourself)\b", re.I)
INTERESTING = re.compile(r"\binteresting\b", re.I)
PLACEHOLDER = re.compile(r"\bTODO\b|\bFIXME\b|\bTK\b|\bXXX\b|(\.\.\.|…)\s*$")
for ln in added:
    if VOICE.search(ln):
        warnings.append(f"second-person voice: {ln.strip()[:90]}")
    if INTERESTING.search(ln):
        warnings.append(f"'interesting' (writing rule): {ln.strip()[:90]}")
    if PLACEHOLDER.search(ln):
        warnings.append(f"placeholder/TODO: {ln.strip()[:90]}")

for w in warnings:
    print(f"  ⚠ {w}")
for e in errors:
    print(f"  ✗ {e}")
if errors:
    print(f"\n{len(errors)} error(s) — not publishing. Fix and re-sync.")
    sys.exit(1)
print(f"pre-publish checks passed ({len(warnings)} warning(s)).")
