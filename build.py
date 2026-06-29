#!/usr/bin/env python3
"""Build a multi-page Jekyll site from the numbered chapter sources in _src/.

- 00 Intro            -> home page (index.md) + auto-generated catalogue
- "* Patterns" chapters with ## sections -> one page per pattern
- other chapters (Related Work, LLM-Specific, Contributions) -> one page each

Links between pages are RELATIVE, so the site works both at
mircealungu.github.io/llm-integration-patterns/ and at patterns.mircealungu.com/.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_src")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def strip_working_notes(text: str) -> str:
    # Drop the maintainer-only "Note about the title:" line from the public page.
    return "\n".join(
        ln for ln in text.splitlines()
        if not ln.strip().startswith("Note about the title")
    )


def front_matter(title: str, permalink: str) -> str:
    safe = title.replace('"', "'")
    return f'---\nlayout: default\ntitle: "{safe}"\npermalink: {permalink}\n---\n'


def clean_generated():
    for f in glob.glob(os.path.join(ROOT, "*.md")):
        if os.path.basename(f) != "README.md":
            os.remove(f)


def main():
    chapters = sorted(glob.glob(os.path.join(SRC, "[0-9]*.md")))
    clean_generated()

    home_body = ""
    catalogue = []   # (category_title, [(pattern_name, slug)], prose_slug_or_None)

    for path in chapters:
        text = open(path, encoding="utf-8").read()
        m = re.search(r"^# (.+)$", text, re.M)
        ctitle = (m.group(1).strip() if m else os.path.basename(path))
        num = os.path.basename(path)[:2]

        if num == "00":
            # The cayman hero shows the title, so drop the body's leading H1.
            home_body = re.sub(r"^\s*# .+$", "", strip_working_notes(text),
                               count=1, flags=re.M).lstrip()
            continue

        splits = bool(re.search(r"^## ", text, re.M)) and \
            ctitle.rstrip("?").strip().endswith("Patterns")

        if splits:
            parts = re.split(r"^(## .+)$", text, flags=re.M)
            pats = []
            rest = parts[1:]
            for i in range(0, len(rest), 2):
                head = rest[i]
                body = rest[i + 1] if i + 1 < len(rest) else ""
                name = head[3:].strip()
                s = slug(name)
                page = (front_matter(name, f"/{s}/")
                        + "\n[← All patterns](../)\n\n"
                        + f"{body.strip()}\n\n"
                        + "[← All patterns](../)\n")
                open(os.path.join(ROOT, f"{s}.md"), "w", encoding="utf-8").write(page)
                pats.append((name, s))
            catalogue.append((ctitle, pats, None))
        else:
            s = slug(ctitle)
            body = re.sub(r"^# .+$", "", text, count=1, flags=re.M).strip()
            page = (front_matter(ctitle, f"/{s}/")
                    + "\n[← All patterns](../)\n\n"
                    + f"{body}\n\n"
                    + "[← All patterns](../)\n")
            open(os.path.join(ROOT, f"{s}.md"), "w", encoding="utf-8").write(page)
            catalogue.append((ctitle, [], s))

    # Home page: intro + catalogue.
    out = [front_matter(
        "Architectural Patterns for Integrating LLMs into User-Facing Applications",
        "/"), "", home_body, "", "## The Patterns", ""]
    for ctitle, pats, prose in catalogue:
        if pats:
            out.append(f"### {ctitle}")
            for name, s in pats:
                out.append(f"- [{name}]({s}/)")
            out.append("")
    extras = [(c, p) for (c, pats, p) in catalogue if not pats]
    if extras:
        out.append("## More")
        out.append("")
        for ctitle, prose in extras:
            out.append(f"- [{ctitle}]({prose}/)")
        out.append("")
    open(os.path.join(ROOT, "index.md"), "w", encoding="utf-8").write("\n".join(out))
    print(f"Built {len(glob.glob(os.path.join(ROOT, '*.md')))} pages.")


if __name__ == "__main__":
    main()
