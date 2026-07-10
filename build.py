#!/usr/bin/env python3
"""Build a multi-page Jekyll site from the numbered chapter sources in content/.

Source lives in content/; the generated Jekyll pages are written into web/
(the Jekyll site root: _config.yml, _layouts/, assets/, images/). GitHub Pages
builds web/ via .github/workflows/pages.yml.

- 00 Intro            -> home page (What is this? + The Idea) + catalogue,
                         and a separate Preamble page (the Zeeguu case study)
- "* Patterns" chapters with ## sections -> one page per pattern
- other chapters (Related Work, LLM-Specific, Contributions) -> one page each

Every page carries a pre-filled "Open an issue" link (labels + title + body).
Links between pages are RELATIVE, so the site works both at
mircealungu.github.io/llm-integration-patterns/ and at llm-patterns.mircealungu.com/.
"""
import glob
import html
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "content")   # chapter sources (mirror of the vault)
OUT = os.path.join(ROOT, "web")       # Jekyll site root; generated pages go here
REPO = "mircealungu/llm-integration-patterns"
SITE = "https://llm-patterns.mircealungu.com"
TITLE = ("Architectural Patterns for Integrating LLMs "
         "into User-Facing Applications")
SUBTITLE = "Lessons from a language-learning platform"

# "All patterns" links land on the catalogue heading, not the top of the home
# page (kramdown auto-ids "## The Patterns" as #the-patterns).
ALL_PATTERNS_HREF = "../#the-patterns"

used_labels = set()


def _load_paper_set():
    """Slugs of patterns in the workshop paper; badged with a star on the site."""
    p = os.path.join(ROOT, "paper", "paper-set.txt")
    try:
        with open(p, encoding="utf-8") as f:
            return {ln.strip() for ln in f if ln.strip() and not ln.startswith("#")}
    except FileNotFoundError:
        return set()


PAPER_SET = _load_paper_set()
STAR_COLOR = "#c8a415"   # muted gold: distinguishes the paper patterns without shouting
PAPER_BADGE = f' <span style="color:{STAR_COLOR}">★</span>'


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def strip_patterns_suffix(category_title: str) -> str:
    """"Latency and Availability Patterns" -> "Latency and Availability".
    The site is already about patterns, so the suffix is redundant in
    breadcrumbs and catalogue headings."""
    return re.sub(r"\s*Patterns$", "", category_title.rstrip("?").strip())


def section_label(category_title: str) -> str:
    return slug(strip_patterns_suffix(category_title))


def strip_working_notes(text: str) -> str:
    return "\n".join(
        ln for ln in text.splitlines()
        if not ln.strip().startswith("Note about the title")
    )


def process_callouts(text: str) -> str:
    """Obsidian callouts, shared convention with the paper build (paper/build_paper.py):

    - `> [!draft]` blocks are working notes -> stripped from the published site.
    - `> [!ack]`  blocks are acknowledgements -> unwrapped, kept inline as text.
    - any other callout -> unwrapped to plain text (kramdown has no callout support).
    """
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
            if ctype == "draft":
                continue
            out.extend(re.sub(r"^>\s?", "", b) for b in block[1:])
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def strip_paper_skip(text: str) -> str:
    """Drop <!-- paper-skip -->…<!-- /paper-skip --> only marks paper-only cuts;
    the site keeps that content, so here we just remove the marker comments."""
    return re.sub(r"<!--\s*/?paper-skip\s*-->", "", text)


def render_embeds(text: str) -> str:
    """Turn Obsidian image embeds into responsive <figure>s.

    ![[file.png]]            -> default-capped, centered, tap-to-zoom
    ![[file.png|220]]        -> capped at 220px (Obsidian's own width syntax)

    Caption: write it as an *italic line directly under the embed* — Obsidian
    renders it, and the build folds it into the <figcaption>:

        ![[file.png|220]]
        *A caption.*

    (A caption inside the embed, ![[file|A caption|220]], still works as a
    fallback. Put any width LAST so Obsidian honors it too.)
    Images live in the vault's images/ folder, served from /images/.
    """
    embed = re.compile(
        r"!\[\[([^\]]+)\]\]"                                  # the embed
        r"(?:[ \t]*\n[ \t]*\*([^\n*][^\n]*?)\*[ \t]*(?=\n|$))?")  # opt. caption

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
        src = f"/images/{fname}"
        style = f' style="max-width:{width}px"' if width else ""
        alt = html.escape(caption or fname.rsplit(".", 1)[0].replace("-", " "))
        cap = (f"\n  <figcaption>{html.escape(caption)}</figcaption>"
               if caption else "")
        return (f'<figure class="img"{style}>\n'
                f'  <a href="{src}"><img src="{src}" alt="{alt}"></a>{cap}\n'
                f"</figure>")
    return embed.sub(repl, text)


def front_matter(title: str, permalink: str, description: str = None,
                 subtitle: str = None, subtitle_url: str = None) -> str:
    safe = title.replace('"', "'")
    fm = f'---\nlayout: default\ntitle: "{safe}"\n'
    if description:
        fm += f'description: "{description}"\n'
    if subtitle:
        fm += f'subtitle: "{subtitle}"\n'
    if subtitle_url:
        fm += f'subtitle_url: "{subtitle_url}"\n'
    return fm + f"permalink: {permalink}\n---\n"


def issue_link(name, slug_path, noun, section=None, label=None):
    body = [f"**Re:** {name}"]
    if section:
        body.append(f"**Section:** {section}")
    body.append(f"**Page:** {SITE}/{slug_path + '/' if slug_path else ''}")
    body.append("")
    body.append("<!-- Your feedback, example, or counter-example goes here. -->")
    labels = "feedback"
    if label:
        labels += f",{label}"
        used_labels.add(label)
    used_labels.add("feedback")
    q = urllib.parse.urlencode({
        "title": f"[{name}] ",
        "labels": labels,
        "body": "\n".join(body),
    })
    return f"[💬 Open an issue about {noun}](https://github.com/{REPO}/issues/new?{q})"


def nav_bar(prev, nxt):
    """Footer nav: prev flush-left, next flush-right (styled by
    `.pattern-footer-nav` in assets/css/style.scss). "All patterns" is omitted
    here — it already lives in the top breadcrumb. The prev/next links keep
    their `.nav-prev` / `.nav-next` classes so the ← / → keyboard handler in
    _layouts/default.html can drive off them.

    prev/nxt are (name, slug) tuples or None at the ends of the sequence.
    """
    links = []
    if prev:
        links.append(f'<a class="nav-prev" href="../{prev[1]}/">'
                     f"← {html.escape(prev[0])}</a>")
    if nxt:
        links.append(f'<a class="nav-next" href="../{nxt[1]}/">'
                     f"{html.escape(nxt[0])} →</a>")
    if not links:
        return ""
    return f'<div class="pattern-footer-nav">{"".join(links)}</div>'


def nav_bar_html(cat=None, cat_href=None):
    """Sticky bar for the top of a pattern page: a breadcrumb back to the
    catalogue, then the pattern's category. Prev/next live in the footer only.
    Styled by `.pattern-nav` in assets/css/style.scss."""
    crumbs = [f'<a href="{ALL_PATTERNS_HREF}">← All patterns</a>']
    if cat:
        sep = '<span class="crumb-sep">‹</span>'
        cat_html = f'<a href="{cat_href}">{html.escape(cat)}</a>' if cat_href \
            else html.escape(cat)
        crumbs.append(f"{sep} {cat_html}")
    return f'<nav class="pattern-nav">\n  {" ".join(crumbs)}\n</nav>'


def footer(issue, nav=None):
    if not nav:
        return f"\n\n---\n{issue}\n"
    return f"\n\n---\n{nav}\n\n{issue}\n"


def write(slug_path, fm_title, top_nav, foot_nav, body, issue,
          home=False, description=None, subtitle=None, subtitle_url=None):
    fname = "index.md" if home else f"{slug_path}.md"
    parts = [front_matter(fm_title, f"/{slug_path}/" if slug_path else "/",
                          description, subtitle, subtitle_url)]
    if top_nav:
        parts.append(f"\n{top_nav}\n")
    parts.append("\n" + body.strip() + "\n")
    parts.append(footer(issue, nav=foot_nav))
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write("\n".join(parts))


def autolink(body, self_slug, name2slug, home=False):
    """Turn *Pattern Name* cross-references into links to that pattern's page.

    Only exact, italicized pattern names become links (the deliberate
    cross-reference convention) — never the page's own name, never **bold**,
    and never a non-pattern italic like *up* or *reuse*.
    """
    prefix = "" if home else "../"

    def repl(m):
        name = m.group(1)
        s = name2slug.get(name)
        if not s or s == self_slug:
            return m.group(0)
        return f"[{name}]({prefix}{s}/)"

    return re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", repl, body)


def clean_generated():
    for f in glob.glob(os.path.join(OUT, "*.md")):
        os.remove(f)


def read_page(path):
    """Return (title, body) for a source .md: title from its `# H1` (falling
    back to the filename without its NN- prefix), body = everything after."""
    text = render_embeds(strip_paper_skip(process_callouts(
        open(path, encoding="utf-8").read())))
    m = re.search(r"^# (.+)$", text, re.M)
    title = (m.group(1).strip() if m
             else re.sub(r"^\d+\s+", "", os.path.basename(path)[:-3]))
    body = re.sub(r"^# .+$", "", text, count=1, flags=re.M).strip()
    return title, body


def main():
    os.makedirs(OUT, exist_ok=True)
    clean_generated()

    home_body = ""
    case_studies = []  # (name, slug, body)
    catalogue = []   # (category_title, [(pattern_name, slug)], prose_slug_or_None)
    pending = []     # (slug, title, back, body, issue, home, description)
    name2slug = {}   # page name -> slug, for cross-reference auto-linking
    pattern_cat = {}  # pattern slug -> its category title (for the subtitle)

    # Walk top-level entries in order. A numbered FOLDER is a pattern category
    # (folder name = title); each .md inside is one pattern. A numbered FILE is
    # the intro (00), a case study, or a prose section (Related Work, etc.).
    for entry in sorted(os.listdir(SRC)):
        full = os.path.join(SRC, entry)

        if os.path.isdir(full):
            if not re.match(r"\d", entry):
                continue
            cat = re.sub(r"^\d+\s+", "", entry)
            label = section_label(cat)
            pats = []
            cat_intro = ""
            for pf in sorted(glob.glob(os.path.join(full, "*.md"))):
                # A `00 …`-prefixed file is the section overview, not a pattern.
                if os.path.basename(pf).startswith("00"):
                    _, cat_intro = read_page(pf)
                    continue
                name, body = read_page(pf)
                s = slug(name)
                il = issue_link(name, s, "this pattern", section=cat, label=label)
                pending.append((s, name, "All patterns", body, il, False, None))
                name2slug[name] = s
                pattern_cat[s] = cat
                pats.append((name, s))
            if pats:
                catalogue.append((cat, pats, cat_intro))
            continue

        if not entry.endswith(".md") or not re.match(r"\d", entry):
            continue
        title, body = read_page(full)

        if "case stud" in title.lower():
            name = re.sub(r"(?i)^(main\s+)?case stud(y|ies):?\s*",
                          "", title).strip() or title
            case_studies.append((name, slug(name), body))
            name2slug[name] = slug(name)
        elif entry[:2] == "00":
            home_body = strip_working_notes(body).strip()
        else:
            s = slug(title)
            il = issue_link(title, s, "this section", section=title)
            pending.append((s, title, "All patterns", body, il, False, None))
            name2slug[title] = s
            catalogue.append((title, [], s))

    # Case study pages (e.g. the Zeeguu case study).
    for name, cs_slug, body in case_studies:
        il = issue_link(name, cs_slug, "this case study", section="Case Studies")
        pending.append((cs_slug, name, "Home", body, il, False, None))

    # Category pages: the category's overview (its `00` file) followed by the
    # list of its patterns. A category with no `00` file just shows the list —
    # graceful degradation, so overviews can be filled in one at a time.
    for ctitle, pats, cat_intro in catalogue:
        if not pats:
            continue                       # prose section, not a pattern category
        cat_slug = section_label(ctitle)
        blocks = []
        if cat_intro and cat_intro.strip():
            blocks.append(cat_intro.strip())
        blocks.append("\n".join(
            f"- [{name}](../{s}/){PAPER_BADGE if s in PAPER_SET else ''}"
            for name, s in pats))
        il = issue_link(ctitle, cat_slug, "this category", section=ctitle,
                        label=section_label(ctitle))
        pending.append((cat_slug, strip_patterns_suffix(ctitle), "All patterns",
                        "\n\n".join(blocks), il, False, None))

    # Home page: What is this? + The Idea + Case Studies + catalogue.
    lines = [home_body, ""]
    if case_studies:
        lines += ["## Case Studies", ""]
        lines += [f"- [{name}]({cs_slug}/)" for name, cs_slug, _ in case_studies]
        lines.append("")
    lines += ["## The Patterns", "",
              f'<span style="color:{STAR_COLOR}">★</span> *marks the patterns in the [PLoP 2026 workshop paper](/paper.pdf); '
              "the rest are part of the extended online catalogue.*",
              ""]
    for ctitle, pats, prose in catalogue:
        if pats:
            # Heading links to the category page (overview lives there now).
            lines.append(f"### [{strip_patterns_suffix(ctitle)}]({section_label(ctitle)}/)")
            lines += [f"- [{name}]({s}/){PAPER_BADGE if s in PAPER_SET else ''}"
                      for name, s in pats]
            lines.append("")
    extras = [(c, p) for (c, pats, p) in catalogue if not pats]
    if extras:
        lines += ["## More", ""]
        lines += [f"- [{c}]({p}/)" for c, p in extras]
        lines.append("")
    home_issue = issue_link("the paper", "", "this paper")
    pending.append(("", TITLE, None, "\n".join(lines), home_issue, True, SUBTITLE))

    # Flatten the catalogue into one ordered sequence of patterns (same order as
    # the home-page listing) so each pattern page can link to its neighbours.
    pattern_seq = [(name, s) for _c, pats, _p in catalogue for name, s in pats]
    pattern_nav = {}
    for i, (name, s) in enumerate(pattern_seq):
        prev = pattern_seq[i - 1] if i > 0 else None
        nxt = pattern_seq[i + 1] if i < len(pattern_seq) - 1 else None
        pattern_nav[s] = (prev, nxt)

    # Flush every page, auto-linking *Pattern Name* cross-references now that the
    # full name -> slug map is known. Pattern pages get a sticky prev/all/next
    # bar up top (and the inline version in the footer); the rest keep a simple
    # back link.
    for slug_path, title, back, body, issue, home, description in pending:
        body = autolink(body, slug_path, name2slug, home=home)
        subtitle = subtitle_url = None
        if slug_path in pattern_nav:
            prev, nxt = pattern_nav[slug_path]
            cat = pattern_cat.get(slug_path)
            cat_label = strip_patterns_suffix(cat) if cat else None
            cat_href = f"../{section_label(cat)}/" if cat else None
            top_nav = nav_bar_html(cat_label, cat_href)
            foot_nav = nav_bar(prev, nxt)
        elif back:
            href = ALL_PATTERNS_HREF if back == "All patterns" else "../"
            top_nav = foot_nav = f"[← {back}]({href})"
        else:
            top_nav = foot_nav = None
        if home and description:
            subtitle = description  # the paper subtitle, shown under the title
        write(slug_path, title, top_nav, foot_nav, body, issue,
              home=home, description=description,
              subtitle=subtitle, subtitle_url=subtitle_url)

    pages = len(glob.glob(os.path.join(OUT, "*.md")))
    print(f"Built {pages} pages. Labels used: {sorted(used_labels)}")


if __name__ == "__main__":
    main()
