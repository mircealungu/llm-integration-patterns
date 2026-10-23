"""
Task Fusion figure: the tasks in Zeeguu's article-assessment call, each next to the
article they all read.

    python3 task-fusion-sizes.py [--repo ~/repos/code/zeeguu/api] [--commit c853d767]

Exports zeeguu/ at the commit, renders get_assessment_and_summary_prompt, and assigns
each line of it to the task it instructs (by the block heading or output field it
belongs to). Lines that serve every task (role, output language, format rules) are
"shared instructions". The article is the typical size used in prompt-template-sizes.py.
Writes ../images/task-fusion-sizes.svg and .pdf.
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("pts", os.path.join(HERE, "prompt-template-sizes.py"))
pts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pts)

# (label, block headings that start this task's rules, output fields that belong to it)
TASKS = [
    ("CEFR level", ["CEFR Level Guidelines:"], ["ORIGINAL_LEVEL:"]),
    ("Summary", [], ["ORIGINAL_SUMMARY:"]),
    ("Titles and summaries at simpler levels", ["LEVELS TO SUMMARIZE:"],
     ["SIMPLIFIED_LEVELS:", "[For each level", "[LEVEL]_TITLE:", "[LEVEL]_SUMMARY:"]),
    ("Paywall check", ["IMPORTANT: If the article appears to be incomplete"], ["INCOMPLETE_ARTICLE:"]),
    ("Advertorial check", ["IMPORTANT: If the article appears to be promotional"], ["ADVERTORIAL_CONTENT:"]),
    ("Disturbing-content check", [], ["DISTURBING_CONTENT:"]),
    ("News or evergreen", [], ["ARTICLE_TYPE:"]),
]
SHARED = "Shared instructions"


def measure():
    """Runs inside the snapshot: characters of instructions per task."""
    from zeeguu.core.llm_services.prompts.article_simplification import get_assessment_and_summary_prompt
    prompt = get_assessment_and_summary_prompt("German")
    sizes = {label: 0 for label, _, _ in TASKS}
    sizes[SHARED] = 0
    block = None
    for line in prompt.split("\n"):
        if not line.strip():
            block = None
            continue
        if "{title}" in line or "{content}" in line:
            continue
        owner = next((l for l, heads, _ in TASKS if any(line.startswith(h) for h in heads)), None)
        if owner:
            block = owner
        owner = owner or next((l for l, _, fields in TASKS if any(line.startswith(f) for f in fields)), None)
        sizes[owner or block or SHARED] += len(line) + 1
    print(json.dumps(sizes))


def svg(sizes, sha):
    article = pts.ARTICLE_CHARS
    rows = sorted(((l, sizes[l]) for l, _, _ in TASKS), key=lambda r: -r[1]) + [(SHARED, sizes[SHARED])]
    W, LABEL_X, BAR_X, ROW, TOP = 620, 262, 270, 23, 46
    BAR_MAX = -(-article // 1000) * 1000
    scale = (W - 70 - BAR_X) / BAR_MAX

    body, y = [], TOP

    def bar(label, value, cls, extra=""):
        cy = y + ROW / 2
        body.append(f'<text class="lbl{extra}" x="{LABEL_X}" y="{cy + 4.5}" text-anchor="end">{label}</text>')
        body.append(f'<rect class="{cls}" x="{BAR_X}" y="{y + 3}" width="{value * scale:.1f}" height="{ROW - 6}" rx="1.5"/>')
        body.append(f'<text class="val" x="{BAR_X + value * scale + 4:.1f}" y="{cy + 4}">{value:,}</text>')

    bar("The article (read by every task)", article, "inp")
    y += ROW + 10
    for label, value in rows:
        bar(label, value, "bar" if label != SHARED else "shr")
        y += ROW

    axis = []
    for v in range(0, BAR_MAX + 1, 1000):
        x = BAR_X + v * scale
        axis.append(f'<line class="grid" x1="{x:.1f}" y1="{TOP - 4}" x2="{x:.1f}" y2="{y + 2}"/>')
        axis.append(f'<text class="tick" x="{x:.1f}" y="{y + 17}" text-anchor="middle">{"0" if v == 0 else f"{v / 1000:g}k"}</text>')
    axis.append(f'<text class="axis" x="{BAR_X + BAR_MAX / 2 * scale:.1f}" y="{y + 33}" text-anchor="middle">characters</text>')
    LEG_X = W - 470
    legend = (
        f'<rect class="inp" x="{LEG_X}" y="14" width="13" height="11" rx="1.5"/>'
        f'<text class="leg" x="{LEG_X + 18}" y="24">shared input</text>'
        f'<rect class="bar" x="{LEG_X + 120}" y="14" width="13" height="11" rx="1.5"/>'
        f'<text class="leg" x="{LEG_X + 138}" y="24">instructions for one task</text>'
        f'<rect class="shr" x="{LEG_X + 300}" y="14" width="13" height="11" rx="1.5"/>'
        f'<text class="leg" x="{LEG_X + 318}" y="24">instructions for all tasks</text>'
    )
    H = y + 44
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Charter, Georgia, serif" role="img" aria-label="Instructions for each task in Zeeguu's article-assessment call at commit {sha[:7]}, next to the article all of them read">
<style>
  .bar  {{ fill:#2a78d6; }}
  .shr  {{ fill:#a3a29c; }}
  .inp  {{ fill:#f2c230; }}
  .lbl  {{ font-size:13px; fill:#0b0b0b; }}
  .val,.leg  {{ font-size:11.5px; fill:#52514e; }}
  .tick {{ font-size:11px; fill:#52514e; }}
  .axis {{ font-size:11.5px; fill:#52514e; }}
  .grid {{ stroke:#d8d7d2; stroke-width:0.6; }}
  @media (prefers-color-scheme: dark) {{
    .bar {{ fill:#3987e5; }} .shr {{ fill:#6b6a64; }} .lbl {{ fill:#ffffff; }}
    .val,.leg,.tick,.axis {{ fill:#c3c2b7; }} .grid {{ stroke:#3a3a38; }}
  }}
</style>
{legend}
{chr(10).join(axis)}
{chr(10).join(body)}
</svg>
'''


def main():
    if "--measure" in sys.argv:
        return measure()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.expanduser("~/repos/code/zeeguu/api"))
    ap.add_argument("--commit", default="c853d767")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "images", "task-fusion-sizes.svg"))
    args = ap.parse_args()
    sha = pts.git(args.repo, "rev-parse", args.commit).strip()
    python = os.path.join(args.repo, ".venv", "bin", "python")
    with tempfile.TemporaryDirectory() as snap:
        archive = subprocess.run(["git", "-C", args.repo, "archive", sha, "zeeguu"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", snap], input=archive.stdout, check=True)
        r = subprocess.run([python, os.path.abspath(__file__), "--measure"], cwd=snap,
                           capture_output=True, text=True, env={**os.environ, "PYTHONPATH": snap})
    sizes = json.loads([l for l in r.stdout.splitlines() if l.startswith("{")][-1])
    print(json.dumps(sizes, indent=1), file=sys.stderr)
    open(args.out, "w").write(svg(sizes, sha))
    pts.to_pdf(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
