#!/usr/bin/env python3
"""Build a multi-page Jekyll site from the numbered chapter sources in _src/.

- 00 Intro            -> home page (What is this? + The Idea) + catalogue,
                         and a separate Preamble page (the Zeeguu case study)
- "* Patterns" chapters with ## sections -> one page per pattern
- other chapters (Related Work, LLM-Specific, Contributions) -> one page each

Every page carries a pre-filled "Open an issue" link (labels + title + body).
Links between pages are RELATIVE, so the site works both at
mircealungu.github.io/llm-integration-patterns/ and at patterns.mircealungu.com/.
"""
import glob
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_src")
REPO = "mircealungu/llm-integration-patterns"
SITE = "https://patterns.mircealungu.com"
TITLE = ("Architectural Patterns for Integrating LLMs "
         "into User-Facing Applications")
SUBTITLE = "Lessons from a language-learning platform"

used_labels = set()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def section_label(category_title: str) -> str:
    return slug(re.sub(r"\s*Patterns$", "", category_title.rstrip("?").strip()))


def strip_working_notes(text: str) -> str:
    return "\n".join(
        ln for ln in text.splitlines()
        if not ln.strip().startswith("Note about the title")
    )


def render_embeds(text: str) -> str:
    """Turn Obsidian image embeds into responsive <figure>s.

    ![[file.png]]                 -> default-capped, centered, tap-to-zoom
    ![[file.png|420]]             -> figure capped at 420px (Obsidian's own
                                     width syntax, so it matches in Obsidian)
    ![[file.png|420|A caption]]   -> ...with a caption
    ![[file.png|A caption]]       -> default width, with a caption
    Images live in the vault's images/ folder, served from /images/.
    """
    def repl(m):
        parts = [p.strip() for p in m.group(1).split("|")]
        fname, width, caption = parts[0], None, None
        for p in parts[1:]:
            w = re.match(r"^(\d+)(?:x\d+)?$", p)
            if w:
                width = w.group(1)
            elif p:
                caption = p
        src = f"/images/{fname}"
        style = f' style="max-width:{width}px"' if width else ""
        alt = caption or fname.rsplit(".", 1)[0].replace("-", " ")
        cap = f"\n  <figcaption>{caption}</figcaption>" if caption else ""
        return (f'<figure class="img"{style}>\n'
                f'  <a href="{src}"><img src="{src}" alt="{alt}"></a>{cap}\n'
                f"</figure>")
    return re.sub(r"!\[\[([^\]]+)\]\]", repl, text)


def front_matter(title: str, permalink: str, description: str = None) -> str:
    safe = title.replace('"', "'")
    fm = f'---\nlayout: default\ntitle: "{safe}"\n'
    if description:
        fm += f'description: "{description}"\n'
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


def footer(issue, back=None):
    if not back:
        return f"\n\n---\n{issue}\n"
    return f"\n\n---\n[← {back}](../) &nbsp;·&nbsp; {issue}\n"


def write(slug_path, fm_title, back, body, issue, home=False, description=None):
    fname = "index.md" if home else f"{slug_path}.md"
    parts = [front_matter(fm_title, f"/{slug_path}/" if slug_path else "/",
                          description)]
    if back:
        parts.append(f"\n[← {back}](../)\n")
    parts.append("\n" + body.strip() + "\n")
    parts.append(footer(issue, back=back))
    open(os.path.join(ROOT, fname), "w", encoding="utf-8").write("\n".join(parts))


def clean_generated():
    for f in glob.glob(os.path.join(ROOT, "*.md")):
        if os.path.basename(f) != "README.md":
            os.remove(f)


def main():
    chapters = sorted(glob.glob(os.path.join(SRC, "[0-9]*.md")))
    clean_generated()

    home_body = ""
    case_studies = []  # (name, slug, body)
    catalogue = []   # (category_title, [(pattern_name, slug)], prose_slug_or_None)

    for path in chapters:
        text = render_embeds(open(path, encoding="utf-8").read())
        m = re.search(r"^# (.+)$", text, re.M)
        ctitle = (m.group(1).strip() if m else os.path.basename(path))
        num = os.path.basename(path)[:2]

        if "case stud" in ctitle.lower():
            # A whole file titled "Case Study: X" becomes its own page,
            # listed under "## Case Studies" on the home page. Checked before
            # the intro test because these files also start with "00".
            name = re.sub(r"(?i)^(main\s+)?case stud(y|ies):?\s*",
                          "", ctitle).strip() or ctitle
            body = re.sub(r"^# .+$", "", text, count=1, flags=re.M).strip()
            case_studies.append((name, slug(name), body))
            continue

        if num == "00":
            intro = strip_working_notes(text)
            home_body = re.sub(r"^\s*# .+$", "", intro, count=1,
                               flags=re.M).strip()
            continue

        splits = bool(re.search(r"^## ", text, re.M)) and \
            ctitle.rstrip("?").strip().endswith("Patterns")

        if splits:
            label = section_label(ctitle)
            chunks = re.split(r"^(## .+)$", text, flags=re.M)[1:]
            pats = []
            for j in range(0, len(chunks), 2):
                name = chunks[j][3:].strip()
                body = chunks[j + 1] if j + 1 < len(chunks) else ""
                s = slug(name)
                il = issue_link(name, s, "this pattern", section=ctitle, label=label)
                write(s, name, "All patterns", body, il)
                pats.append((name, s))
            catalogue.append((ctitle, pats, None))
        else:
            s = slug(ctitle)
            body = re.sub(r"^# .+$", "", text, count=1, flags=re.M).strip()
            il = issue_link(ctitle, s, "this section", section=ctitle)
            write(s, ctitle, "All patterns", body, il)
            catalogue.append((ctitle, [], s))

    # Case study pages (e.g. the Zeeguu case study).
    for name, cs_slug, body in case_studies:
        il = issue_link(name, cs_slug, "this case study", section="Case Studies")
        write(cs_slug, name, "Home", body, il)

    # Home page: What is this? + The Idea + Case Studies + catalogue.
    lines = [home_body, ""]
    if case_studies:
        lines += ["## Case Studies", ""]
        lines += [f"- [{name}]({cs_slug}/)" for name, cs_slug, _ in case_studies]
        lines.append("")
    lines += ["## The Patterns", ""]
    for ctitle, pats, prose in catalogue:
        if pats:
            lines.append(f"### {ctitle}")
            lines += [f"- [{name}]({s}/)" for name, s in pats]
            lines.append("")
    extras = [(c, p) for (c, pats, p) in catalogue if not pats]
    if extras:
        lines += ["## More", ""]
        lines += [f"- [{c}]({p}/)" for c, p in extras]
        lines.append("")
    home_issue = issue_link("the paper", "", "this paper")
    write("", TITLE, None, "\n".join(lines), home_issue, home=True,
          description=SUBTITLE)

    pages = len(glob.glob(os.path.join(ROOT, "*.md")))
    print(f"Built {pages} pages. Labels used: {sorted(used_labels)}")


if __name__ == "__main__":
    main()
