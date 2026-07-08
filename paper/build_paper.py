#!/usr/bin/env python3
"""Build an ACM (acmart) PDF from the SAME vault Markdown that feeds the website.

Single source: the chapter Markdown in content/ (the in-repo mirror of the
Obsidian vault; pass --vault to read the live vault directly instead). The
website (build.py) and this paper build are two *views* of that one source.
This script adds only a thin, paper-only layer on top:

  - MANIFEST      : which chapters, in what order, go in the paper (the site
                    includes a few extra meta pages this omits).
  - metadata      : ACM title block (title, author, abstract, keywords) — lives
                    here, never in the shared Markdown body.
  - callouts      : `> [!draft]` blocks are stripped; `> [!ack]` blocks are
                    hoisted into an Acknowledgments section; other callouts are
                    unwrapped to plain text.
  - `<!-- paper-skip -->…<!-- /paper-skip -->` regions are dropped (website-only
    framing such as the "What is this?" intro).
  - Obsidian `![[img|width]]` embeds -> pandoc figures.

Pipeline:  vault .md  ->  assemble one body.md  ->  pandoc -t latex  ->
           wrap in acmart main.tex  ->  xelatex x2  ->  paper.pdf
"""
import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build")
BIB = os.path.join(HERE, "references.bib")

# Source defaults to the in-repo content/ mirror, so contributors and CI can
# build the PDF without the Obsidian vault. `--vault` reads the live vault
# (AIPAT_VAULT) instead — handy for a local preview of not-yet-synced edits.
CONTENT = os.path.normpath(os.path.join(HERE, os.pardir, "content"))
if "--vault" in sys.argv:
    SRC = os.environ.get(
        "AIPAT_VAULT",
        "/Users/mircea/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
        "Megavault/writing/26 - AI Patterns",
    ).rstrip("/")
else:
    SRC = CONTENT

# --- PAPER-ONLY METADATA (edit here; never touches the shared Markdown) -------
META = {
    "title": "Architectural Patterns for Integrating LLMs "
             "into User-Facing Applications",
    "subtitle": "Lessons from a language-learning platform",
    "author": "Mircea Lungu",
    "institution": "IT University of Copenhagen",
    "city": "Copenhagen",
    "country": "Denmark",
    "email": "mircea.lungu@gmail.com",  # <- swap for institutional address
    "author2": "Cesare Pautasso",
    "institution2": "University of Lugano",
    "city2": "Lugano",
    "country2": "Switzerland",
    "email2": "",  # <- Cesare's email (institutional/IEEE)
    "keywords": "large language models, software architecture, design patterns, "
                "LLM integration, cost, latency, quality assurance",
    "abstract": (
        "Large Language Models are increasingly being integrated as components "
        "into existing user-facing applications, alongside the more visible "
        "wave of LLM-native products such as chatbots and agents. The "
        "engineering concerns of the two cases differ: when an LLM is a "
        "component behind an existing feature rather than the product itself, "
        "designers must reconcile its per-token cost, multi-second latency, "
        "non-determinism, rapidly shifting provider landscape, and "
        "general-purpose capability with the expectations of users who already "
        "rely on the system. We present a catalogue of recurring architectural "
        "patterns that address these concerns, grounded in over a year of LLM "
        "integration work on Zeeguu, an open-source language-learning platform "
        "with several hundred monthly active users. The catalogue spans five "
        "concerns --- cost optimization, latency and availability, lifecycle "
        "management, data management, and quality assurance --- and is "
        "described using the standard pattern format. The patterns are "
        "presented as a starting point for community refinement and extension, "
        "not as a closed taxonomy."
    ),
}

# --- MANIFEST: ordered paper chapters (relative to VAULT) ---------------------
# ('intro'|'prose'|'category', relpath, section_title_for_category)
MANIFEST = [
    ("intro",    "00 Intro.md", None),
    ("prose",    "00a Case Study - Zeeguu.md", None),
    ("category", "01 Using the LLM Efficiently", "Using the LLM Efficiently"),
    ("category", "02 Trusting LLM Output", "Trusting LLM Output"),
    ("category", "03 Managing Change Over Time", "Managing Change Over Time"),
    ("prose",    "08 LLM-Specific.md", None),
    ("prose",    "07 Related Work.md", None),
    ("prose",    "11 Limitations and Future Work.md", None),
    ("prose",    "12 Conclusion.md", None),
]
# NOTE: '09 Candidate Patterns' (provisional, site-only) and '10 Possible Paper
# Contributions.md' (repo/site meta) are intentionally excluded from the paper.

# Unicode symbols that pdf/xelatex + acmart fonts may lack a glyph for; route
# them through inline math so they always render, regardless of engine/font.
# Paper figures render smaller than the web embeds: the screenshots carry UI
# text that otherwise looks oversized next to 10pt body type. 0.5 = half the
# width the Obsidian embed asks for (web/vault sizes are unaffected).
PAPER_FIG_SCALE = 0.5

SYMBOL_MATH = {
    "→": r"$\rightarrow$",   # →
    "←": r"$\leftarrow$",    # ←
    "≥": r"$\ge$",           # ≥
    "≤": r"$\le$",           # ≤
    "×": r"$\times$",        # ×
    "≈": r"$\approx$",       # ≈
}


def strip_paper_skip(text):
    return re.sub(r"<!--\s*paper-skip\s*-->.*?<!--\s*/paper-skip\s*-->",
                  "", text, flags=re.S)


def process_callouts(text, acks):
    """Drop [!draft] callouts, hoist [!ack] into `acks`, unwrap the rest."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^>\s*\[!(\w+)\][-+]?\s?(.*)$", lines[i])
        if m:
            ctype = m.group(1).lower()
            block = [lines[i]]
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                block.append(lines[i])
                i += 1
            body = [re.sub(r"^>\s?", "", b) for b in block[1:]]
            if ctype == "draft":
                continue                       # stripped everywhere
            if ctype == "ack":
                acks.append("\n".join(body).strip())
                continue
            out.extend(body)                   # unknown callout -> plain text
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def convert_embeds(text):
    """Obsidian ![[file|width]] (+ optional italic caption line) -> pandoc figure."""
    embed = re.compile(
        r"!\[\[([^\]]+)\]\]"
        r"(?:[ \t]*\n[ \t]*\*([^\n*][^\n]*?)\*[ \t]*(?=\n|$))?")

    def repl(m):
        parts = [p.strip() for p in m.group(1).split("|")]
        fname, width, pipe_cap = parts[0], None, None
        for p in parts[1:]:
            w = re.match(r"^(\d+)(?:x\d+)?$", p)
            if w:
                width = w.group(1)
            elif p:
                pipe_cap = p
        caption = (m.group(2) or pipe_cap or "").strip()
        if width:
            w = max(1, round(int(width) * PAPER_FIG_SCALE))
            attr = f"{{ width={w}px }}"
        else:
            attr = ""
        return f"![{caption}](images/{fname}){attr}"

    return embed.sub(repl, text)


def demote(md, by):
    out = []
    for ln in md.split("\n"):
        m = re.match(r"^(#{1,6})(\s.*)$", ln)
        out.append("#" * min(6, len(m.group(1)) + by) + m.group(2) if m else ln)
    return "\n".join(out)


def process_file(path, acks):
    text = open(path, encoding="utf-8").read()
    text = strip_paper_skip(text)
    text = process_callouts(text, acks)
    text = convert_embeds(text)
    return text.strip()


def load_bib_urls(path):
    """Map every `url = {...}` in the .bib to its citekey, so a Markdown link to
    that URL can be turned into a \\cite in the paper (framework-doc links, which
    have no bib entry, stay as hyperlinks)."""
    if not os.path.exists(path):
        return {}
    text = open(path, encoding="utf-8").read()
    url2key = {}
    for key, body in re.findall(r"@\w+\s*\{\s*([^,]+),(.*?)\n\}", text, re.S):
        m = re.search(r"url\s*=\s*[{\"]([^}\"]+)[}\"]", body)
        if m:
            url2key[m.group(1).strip().rstrip("/")] = key.strip()
    return url2key


def linkify_citations(md, url2key):
    """`[Anchor](url)` -> `Anchor [@key]` when url has a bib entry; else unchanged.
    The negative lookbehind for `!` leaves image embeds alone."""
    def repl(m):
        key = url2key.get(m.group(2).rstrip("/"))
        return f"{m.group(1)} [@{key}]" if key else m.group(0)
    return re.sub(r"(?<!\!)\[([^\]]+)\]\((https?://[^)]+)\)", repl, md)


def load_paper_set():
    """Slugs of the patterns that go in the workshop paper (one per line)."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper-set.txt")
    with open(p, encoding="utf-8") as f:
        return {ln.strip() for ln in f if ln.strip() and not ln.startswith("#")}


PAPER_SET = load_paper_set()


def pattern_slug(path):
    name = re.sub(r"\.md$", "", re.sub(r"^\d+\s+", "", os.path.basename(path)))
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def assemble():
    parts, acks = [], []
    for kind, rel, title in MANIFEST:
        full = os.path.join(SRC, rel)
        if kind == "intro":
            t = process_file(full, acks)
            t = re.sub(r"^#\s+.*$", "", t, count=1, flags=re.M)   # drop H1 title
            t = t.replace("### The Idea", "# Introduction")
            parts.append(t.strip())
        elif kind == "prose":
            parts.append(process_file(full, acks))
        elif kind == "category":
            files = sorted(glob.glob(os.path.join(full, "*.md")))
            parts.append(f"# {title}\n")
            # A `00 …`-prefixed file is the section overview, not a pattern: keep
            # its body at section level (drop its H1); everything else is a pattern.
            for f in [f for f in files if os.path.basename(f).startswith("00")]:
                t = re.sub(r"^#\s+.*$", "", process_file(f, acks), count=1,
                           flags=re.M).strip()
                parts.append(t)
            for pf in [f for f in files if not os.path.basename(f).startswith("00")
                       and pattern_slug(f) in PAPER_SET]:
                parts.append(demote(process_file(pf, acks), 1))
    body = "\n\n".join(p.strip() for p in parts) + "\n"
    if acks:
        body += "\n\n# Acknowledgments\n\n" + "\n\n".join(acks) + "\n"
    body = linkify_citations(body, load_bib_urls(BIB))
    for sym, rep in SYMBOL_MATH.items():
        body = body.replace(sym, rep)
    # Web links to another page's anchor ([x](../slug/#anchor)) are one document
    # in the PDF, so rewrite them to intra-document anchors ([x](#anchor));
    # pandoc then renders them as internal cross-references, not dead web URLs.
    body = re.sub(r"\]\(\.\./[^)#]*#", "](#", body)
    # Stray trailing whitespace (a 2-space markdown "hard break") on a list item
    # becomes \\ in LaTeX and spaces bullets far apart; strip it line by line.
    body = "\n".join(line.rstrip() for line in body.split("\n"))
    return body


def tex_escape_meta(s):
    return s  # META strings are pre-escaped (use --- for em-dash etc.)


def main_tex():
    m = META
    sub = f"\\subtitle{{{m['subtitle']}}}\n" if m.get("subtitle") else ""
    email2 = f"\\email{{{m['email2']}}}\n" if m.get("email2") else ""
    return rf"""\documentclass[manuscript,nonacm,screen]{{acmart}}
\settopmatter{{printacmref=false, printccs=false, printfolios=true}}
\setcopyright{{none}}
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\providecommand{{\passthrough}}[1]{{#1}}
\providecommand{{\pandocbounded}}[1]{{#1}}
\graphicspath{{{{images/}}}}
\begin{{document}}
\title{{{m['title']}}}
{sub}\author{{{m['author']}}}
\affiliation{{%
  \institution{{{m['institution']}}}
  \city{{{m['city']}}}
  \country{{{m['country']}}}}}
\email{{{m['email']}}}
\author{{{m['author2']}}}
\affiliation{{%
  \institution{{{m['institution2']}}}
  \city{{{m['city2']}}}
  \country{{{m['country2']}}}}}
{email2}\begin{{abstract}}
{m['abstract']}
\end{{abstract}}
\keywords{{{m['keywords']}}}
\maketitle
\input{{body.tex}}
\bibliographystyle{{ACM-Reference-Format}}
\bibliography{{references}}
\end{{document}}
"""


def run(cmd, **kw):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, **kw)


def main():
    if shutil.which("pandoc") is None:
        sys.exit("pandoc not found")
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "images"))

    # images from the source (basenames, no spaces in the build dir)
    for img in glob.glob(os.path.join(SRC, "images", "*")):
        if os.path.isfile(img):
            shutil.copy(img, os.path.join(OUT, "images", os.path.basename(img)))

    body_md = os.path.join(OUT, "body.md")
    open(body_md, "w", encoding="utf-8").write(assemble())

    lua_filter = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "links-to-footnotes.lua")
    r = run(["pandoc", body_md, "-f",
             "markdown+tex_math_dollars+footnotes+pipe_tables",
             "-t", "latex", "--natbib", "--wrap=preserve",
             "--lua-filter", lua_filter,
             "-o", os.path.join(OUT, "body.tex")])
    if r.returncode:
        sys.exit("pandoc failed")

    open(os.path.join(OUT, "main.tex"), "w", encoding="utf-8").write(main_tex())
    if os.path.exists(BIB):
        shutil.copy(BIB, os.path.join(OUT, "references.bib"))

    engine = "xelatex" if shutil.which("xelatex") else "pdflatex"
    tex = [engine, "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
    # xelatex -> bibtex -> xelatex x2 resolves \cite and the References section.
    # bibtex takes the .aux basename and NONE of the tex engine flags.
    for cmd in (tex, ["bibtex", "main"], tex, tex):
        r = run(cmd, cwd=OUT, capture_output=True, text=True)
    pdf = os.path.join(OUT, "main.pdf")
    if not os.path.exists(pdf):
        # surface the last ~40 lines of the log for debugging
        log = os.path.join(OUT, "main.log")
        if os.path.exists(log):
            print("\n".join(open(log, encoding="utf-8", errors="replace")
                            .read().splitlines()[-45:]))
        sys.exit(f"{engine} did not produce a PDF")

    dest = os.path.join(HERE, "paper.pdf")
    shutil.copy(pdf, dest)
    print(f"\nOK -> {dest}")


if __name__ == "__main__":
    main()
