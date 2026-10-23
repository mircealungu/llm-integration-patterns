"""
Prompt-template sizes of Zeeguu's LLM calls, now and over time.

    python3 prompt-template-sizes.py [--all] [--repo ~/repos/code/zeeguu/api] [--out ../images/prompt-template-sizes.svg]

Writes the SVG (site) and, next to it, a PDF of it (paper), printed with headless Chrome.

For the last commit of every month since START (and HEAD), exports zeeguu/ from
the repo, imports each prompt from that snapshot, and measures:

  template  characters of fixed text (placeholders removed, system prompt included)
  input     characters a typical call puts into the placeholders (samples below)
  batch     template of the batched variant, where one exists

Measurements are cached per commit in prompt-template-sizes.json next to this file.
A prompt that cannot be found at a commit (not written yet, or named differently)
is left out of that month.
"""

import argparse
import ast
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

START = "2025-01"

# ---------------------------------------------------------------------------
# Measuring (runs inside a snapshot, with the snapshot first on sys.path)
# ---------------------------------------------------------------------------

WORD, TRANSLATION = "anrufen", "to call"
SENTENCE = "Ich rufe dich morgen früh an, wenn ich mit der Arbeit fertig bin."
ARTICLE_CHARS = 4000  # a typical article: about 600 words
SCRIPT_CHARS = 2500  # a typical audio-lesson script
MEANINGS_PER_BATCH = 15
SENTENCES_PER_ARTICLE = 30
MWES_PER_SENTENCE = 2

SAMPLES = {
    **dict.fromkeys(
        "word origin_word searched_word selection expected typed mwe_text mwe1 mwe2".split(), WORD),
    **dict.fromkeys(
        "translation translation_word translation1 translation2 expected_translation".split(), TRANSLATION),
    **dict.fromkeys("sentence context context_paragraph".split(), SENTENCE),
    **dict.fromkeys(
        "language source_lang target_lang source_name target_name origin_language translation_language "
        "learned_name translation_name target_language".split(), "German"),
    **dict.fromkeys("native_language teacher_name source_language".split(), "English"),
    "cefr_level": "B1", "level": "B1", "count": "3", "lesson_type": "topic",
    "suggestion": "ordering coffee",
    "token_list": "\n".join(f"{i}: {t}" for i, t in enumerate(SENTENCE.split())),
    "examples": "\n".join([SENTENCE] * 3),
    "title": "x" * 60, "summary": "x" * 200, "content": "x" * ARTICLE_CHARS,
    "script": "x" * SCRIPT_CHARS, "numbered_script": "x" * SCRIPT_CHARS,
}

FIELD = re.compile(r"\{([^{}]*)\}")


def fixed(template):
    """Characters left once the {placeholders} are removed and {{ }} unescaped."""
    t = template.replace("{{", "\0").replace("}}", "\1")
    return len(FIELD.sub("", t))


def typical_input(template):
    t = template.replace("{{", "\0").replace("}}", "\1")
    return sum(len(SAMPLES.get(name.split(":")[0].split("!")[0], "")) for name in FIELD.findall(t))


def fstring(module, function, variable="prompt"):
    """The f-string assigned to `variable` in `function`, with each {expr} as {expr}."""
    tree = ast.parse(open(module.__file__, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            for a in ast.walk(node):
                if isinstance(a, ast.Assign) and getattr(a.targets[0], "id", None) == variable:
                    parts = []
                    for v in a.value.values:
                        if isinstance(v, ast.Constant):
                            parts.append(v.value.replace("{", "{{").replace("}", "}}"))
                        else:
                            parts.append("{" + ast.unparse(v.value) + "}")
                    return "".join(parts)
    raise LookupError(function)


def mod(name):
    import importlib
    return importlib.import_module(name)


def audio_prompt(pattern):
    sg = mod("zeeguu.core.audio_lessons.script_generator")
    files = sorted(glob.glob(os.path.join(os.path.dirname(sg.__file__), "prompts", pattern)))
    if not files:
        raise LookupError(pattern)
    text = open(files[-1], encoding="utf-8").read()
    system = sg.language_contract("German", "English") if hasattr(sg, "language_contract") else ""
    return text, system


def mwe_detector(attr):
    m = mod("zeeguu.core.mwe.llm_mwe_detector")
    for v in vars(m).values():
        if isinstance(v, type) and attr in vars(v):
            return vars(v)[attr]
    raise LookupError(attr)


P = "zeeguu.core.llm_services.prompts."

# (group, label, single template -> str or (str, system), batched template or None, batch size)
TASKS = [
    ("Reader", "Word translation in context",
     lambda: mod("zeeguu.core.llm_services.mwe_translation_service").GENERAL_WORD_TRANSLATION_PROMPT, None, 0),
    ("Reader", "Multi-word expression translation",
     lambda: mod("zeeguu.core.llm_services.mwe_translation_service").TRANSLATION_PROMPT,
     lambda: fstring(mod("zeeguu.core.llm_services.mwe_translation_service"), "translate_separated_mwe_batch"),
     MWES_PER_SENTENCE),
    ("Reader", "Multi-word expression detection",
     lambda: mwe_detector("PROMPT_TEMPLATE"), lambda: mwe_detector("BATCH_PROMPT_TEMPLATE"),
     SENTENCES_PER_ARTICLE),
    ("Reader", "Word explanation",
     lambda: (mod(P + "word_explanation").WORD_EXPLANATION_PROMPT, mod(P + "word_explanation").WORD_EXPLANATION_SYSTEM),
     None, 0),
    ("Words", "Translation validation", lambda: mod(P + "translation_validator").COMBINED_VALIDATION_PROMPT, None, 0),
    ("Words", "Semantic equivalence", lambda: mod(P + "translation_validator").SEMANTIC_EQUIVALENCE_PROMPT, None, 0),
    ("Words", "Meaning-frequency and idiom-tagging",
     lambda: mod(P + "meaning_frequency_classifier").MEANING_FREQUENCY_AND_TYPE_PROMPT,
     lambda: mod(P + "meaning_frequency_classifier").BATCH_MEANING_FREQUENCY_AND_TYPE_PROMPT,
     MEANINGS_PER_BATCH),
    ("Words", "Learning-card generation", lambda: mod(P + "learning_card_generator").LEARNING_CARD_PROMPT, None, 0),
    ("Words", "Example-sentence generation",
     lambda: (mod(P + "example_generation").get_prompt_template()["user"],
              mod(P + "example_generation").get_prompt_template()["system"]), None, 0),
    ("Exercises", "Cloze answer judge", lambda: mod(P + "cloze_alternative").CLOZE_ALTERNATIVE_PROMPT, None, 0),
    ("Exercises", "Translation answer judge",
     lambda: mod(P + "translation_alternative").TRANSLATION_ALTERNATIVE_PROMPT, None, 0),
    ("Articles", "CEFR assessment + summary",
     lambda: mod(P + "article_simplification").get_assessment_and_summary_prompt("German"), None, 0),
    ("Articles", "Simplification, one level",
     lambda: mod(P + "level_simplification").get_level_simplification_prompt("de", "", "", "B1")
     + "{title}{content}", None, 0),
    ("Articles", "Simplification, all levels",
     lambda: mod(P + "article_simplification").get_adaptive_simplification_prompt("German"), None, 0),
    ("Articles", "Grammar correction",
     lambda: mod(P + "grammar_correction").get_full_article_correction_prompt("de"), None, 0),
    ("Audio lessons", "Word lesson script", lambda: audio_prompt("meaning_lesson--*-v*.txt"), None, 0),
    ("Audio lessons", "Topic dialogue script", lambda: audio_prompt("dialogue_lesson--topic-v*.txt"), None, 0),
    ("Audio lessons", "Beginner dialogue script", lambda: audio_prompt("a0_dialogue_lesson--*-v*.txt"), None, 0),
    ("Audio lessons", "Lesson word extraction", lambda: mod("zeeguu.core.audio_lessons.lesson_words")._PROMPT, None, 0),
    ("Audio lessons", "Lesson correctness check",
     lambda: (mod("zeeguu.core.audio_lessons.lesson_correctness_check").LESSON_PROMPT,
              mod("zeeguu.core.audio_lessons.lesson_correctness_check").LESSON_SYSTEM), None, 0),
    ("Audio lessons", "Topic validation",
     lambda: mod("zeeguu.core.audio_lessons.suggestion_validator").VALIDATION_PROMPT, None, 0),
]


def measure():
    import io, contextlib, logging
    logging.disable(logging.CRITICAL)
    out = {}
    for _, label, single, batched, _n in TASKS:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                t = single()
            template, system = t if isinstance(t, tuple) else (t, "")
            row = {"template": fixed(template) + len(system), "input": typical_input(template)}
        except Exception:
            continue
        try:
            if batched:
                row["batch"] = fixed(batched())
        except Exception:
            pass
        out[label] = row
    print(json.dumps(out))


# ---------------------------------------------------------------------------
# Sampling the history
# ---------------------------------------------------------------------------

def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def monthly_commits(repo):
    """The last first-parent commit of each month since START, plus HEAD."""
    last = {}
    for line in git(repo, "log", "--first-parent", "--format=%ad %H", "--date=short").splitlines():
        date, sha = line.split()
        month = date[:7]
        if month >= START and month not in last:
            last[month] = (date, sha)
    head = git(repo, "log", "-1", "--format=%ad %H", "--date=short").split()
    commits = sorted(last.values())
    if commits[-1][1] != head[1]:
        commits.append(tuple(head))
    return commits


def measure_at(repo, sha):
    python = os.path.join(repo, ".venv", "bin", "python")
    with tempfile.TemporaryDirectory() as snap:
        archive = subprocess.run(["git", "-C", repo, "archive", sha, "zeeguu"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", snap], input=archive.stdout, check=True)
        r = subprocess.run([python, os.path.abspath(__file__), "--measure"],
                           cwd=snap, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": snap})
    lines = [l for l in r.stdout.splitlines() if l.startswith("{")]
    return json.loads(lines[-1]) if lines else {}


def history(repo, cache_file):
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}
    rows = []
    for date, sha in monthly_commits(repo):
        if sha not in cache:
            print(f"measuring {date} {sha[:8]}", file=sys.stderr)
            cache[sha] = {"date": date, "sizes": measure_at(repo, sha)}
            json.dump(cache, open(cache_file, "w"), indent=1)
        rows.append((date, sha, cache[sha]["sizes"]))
    return rows


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

# The calls the chapter's figure shows: big fixed template, small variable input.
CHAPTER = [
    "Word lesson script",
    "Translation validation",
    "Example-sentence generation",
    "Meaning-frequency and idiom-tagging",
]


def svg(rows, labels):
    date_now, sha_now, now = rows[-1]
    # The paper embeds this W-px chart at 85% of its 430pt text block, i.e.
    # 0.59pt per px. Font sizes are chosen so the text lands on the TikZ
    # diagrams' two sizes there: labels 9pt (\small), the rest 8pt
    # (\footnotesize). Changing W or the embed width changes that scale.
    W, LABEL_X, BAR_X = 620, 290, 298
    ROW, GROUP_GAP, TOP = 26, 18, 50
    F_LBL, F_SM = 15.3, 13.6
    longest = max(now[l]["template"] + now[l]["input"] for l in labels if l in now)
    BAR_MAX = -(-longest // 2500) * 2500
    scale = (W - 110 - BAR_X) / BAR_MAX
    grouped = len(labels) > len(CHAPTER)

    body, y = [], TOP
    groups = []
    tasks = TASKS if grouped else sorted(TASKS, key=lambda t: -now.get(t[1], {}).get("template", 0))
    for group, label, *_ in tasks:
        if label not in now or label not in labels:
            continue
        if grouped and (not groups or groups[-1] != group):
            if groups:
                y += GROUP_GAP
            groups.append(group)
            body.append(f'<text class="grp" x="{LABEL_X}" y="{y + 12}" text-anchor="end">{group}</text>')
            y += 20
        r = now[label]
        t, i = r["template"], r["input"]
        cy = y + ROW / 2
        body.append(f'<text class="lbl" x="{LABEL_X}" y="{cy + 5}" text-anchor="end">{label}</text>')
        body.append(f'<rect class="bar" x="{BAR_X}" y="{y + 3}" width="{t * scale:.1f}" height="{ROW - 6}" rx="1.5"/>')
        body.append(f'<rect class="inp" x="{BAR_X + t * scale:.1f}" y="{y + 3}" width="{max(i * scale, 1.2):.1f}" '
                    f'height="{ROW - 6}" rx="1.5"/>')
        end = BAR_X + (t + i) * scale + 4
        body.append(f'<text class="val" x="{end:.1f}" y="{cy + 4.5}">{t:,} <tspan class="inpv">+ {i:,}</tspan></text>')

        # first measured version of this prompt, on the same scale
        v0 = next(s[label]["template"] for _, _, s in rows if label in s)
        if v0 != t:
            x0 = BAR_X + v0 * scale
            body.append(f'<line class="was" x1="{x0:.1f}" y1="{y + 1}" x2="{x0:.1f}" y2="{y + ROW - 1}"/>')
        y += ROW

    H = y + 48
    axis = []
    for v in range(0, BAR_MAX + 1, 2500):
        x = BAR_X + v * scale
        axis.append(f'<line class="grid" x1="{x:.1f}" y1="{TOP - 4}" x2="{x:.1f}" y2="{y + 2}"/>')
        axis.append(f'<text class="tick" x="{x:.1f}" y="{y + 18}" text-anchor="middle">'
                    f'{"0" if v == 0 else f"{v / 1000:g}k"}</text>')
    axis.append(f'<text class="axis" x="{BAR_X + BAR_MAX / 2 * scale:.1f}" y="{y + 36}" text-anchor="middle">characters</text>')
    LEG_X = min(BAR_X, W - 470)  # legend is ~470px wide at F_SM
    legend = (
        f'<rect class="bar" x="{LEG_X}" y="15" width="13" height="11" rx="1.5"/>'
        f'<text class="leg" x="{LEG_X + 18}" y="25">fixed template</text>'
        f'<rect class="inp" x="{LEG_X + 125}" y="15" width="13" height="11" rx="1.5"/>'
        f'<text class="leg" x="{LEG_X + 143}" y="25">typical input</text>'
        f'<line class="was" x1="{LEG_X + 245}" y1="13" x2="{LEG_X + 245}" y2="29"/>'
        f'<text class="leg" x="{LEG_X + 253}" y="25">template at its first version</text>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Charter, Georgia, serif" role="img" aria-label="Fixed prompt-template size and typical input size of Zeeguu LLM calls at commit {sha_now[:7]}, with each template's first-version size">
<style>
  .bar  {{ fill:#2a78d6; }}
  .inp  {{ fill:#f2c230; }}
  .lbl  {{ font-size:{F_LBL}px; fill:#0b0b0b; }}
  .grp  {{ font-size:{F_SM}px; fill:#52514e; font-style:italic; }}
  .val,.leg  {{ font-size:{F_SM}px; fill:#52514e; }}
  .inpv {{ fill:#a8820f; }}
  .tick {{ font-size:{F_SM}px; fill:#52514e; }}
  .axis {{ font-size:{F_SM}px; fill:#52514e; }}
  .grid {{ stroke:#d8d7d2; stroke-width:0.6; }}
  .was  {{ stroke:#0b0b0b; stroke-width:1.4; }}
  @media (prefers-color-scheme: dark) {{
    .bar {{ fill:#3987e5; }} .was {{ stroke:#ffffff; }} .inpv {{ fill:#f2c230; }} .lbl {{ fill:#ffffff; }}
    .val,.leg,.tick,.axis,.grp {{ fill:#c3c2b7; }} .grid {{ stroke:#3a3a38; }}
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
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.expanduser("~/repos/code/zeeguu/api"))
    ap.add_argument("--out", default=os.path.join(here, "..", "images", "prompt-template-sizes.svg"))
    ap.add_argument("--all", action="store_true", help="every call, grouped, not only the chapter's")
    args = ap.parse_args()
    rows = history(args.repo, os.path.join(here, "prompt-template-sizes.json"))
    rows = [r for r in rows if r[2]]
    for date, sha, sizes in rows:
        print(date, sha[:8], len(sizes), "prompts", file=sys.stderr)
    open(args.out, "w").write(svg(rows, [t[1] for t in TASKS] if args.all else CHAPTER))
    to_pdf(args.out)
    print(args.out)


def to_pdf(svg_file):
    """Print the SVG, light scheme, to a PDF of the same size.

    The PDF is set in Linux Biolinum, the paper's caption font (from the TeX
    install), so the figure's text matches the captions; the site SVG keeps its
    own font. The SVG is inlined so the page's @font-face reaches it."""
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    src = open(svg_file).read()
    w, h = re.search(r'width="(\d+)" height="(\d+)"', src).groups()
    font = subprocess.run(["kpsewhich", "LinBiolinum_R.otf"], capture_output=True, text=True,
                          check=True).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "page.html")
        open(page, "w").write(
            f'<html><head><meta name="color-scheme" content="light"><style>@page {{ size: {w}px {h}px; margin: 0 }}'
            f' body {{ margin: 0 }} @font-face {{ font-family: Biolinum; src: url("file://{font}"); }}'
            f' svg {{ font-family: Biolinum !important; text-rendering: geometricPrecision; display: block }}</style></head><body>{src}</body></html>')
        subprocess.run([chrome, "--headless", "--disable-gpu", "--allow-file-access-from-files",
                        "--blink-settings=preferredColorScheme=1", "--no-pdf-header-footer",
                        f"--print-to-pdf={svg_file[:-4]}.pdf", f"file://{page}"],
                       capture_output=True, check=True)


if __name__ == "__main__":
    main()
