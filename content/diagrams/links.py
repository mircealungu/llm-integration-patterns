#!/usr/bin/env python3
"""Turn a diagram's <name>.links (written by its TikZ, see pattern-map.tikz)
into clickable areas.

    links.py <name>.links <images/name.svg> <images/name.links.json>

- The JSON holds each link as fractions of the figure (x0, y0 top-left, x1, y1
  bottom-right), so both builders can place it at any scale: the site (build.py)
  embeds a linked SVG as an <object>, the paper (build_paper.py) lays hyperlinks
  over the included PDF.
- The SVG gets a transparent <a><rect> per link, pointing at the pattern's page.

Coordinates in .links are TeX pt in picture space; the standalone page adds a
4pt border on every side (style: border=4pt), and the SVG's viewBox spans that
page, so a fraction of the page is the same in the PDF and the SVG.
"""
import json
import re
import sys

BORDER = 4.0  # pt, the standalone border in each diagram's .tex


def pt(v):
    return float(v.rstrip("pt"))


def main(links_path, svg_path, json_path):
    links, bbox = [], None
    for line in open(links_path):
        f = line.split()
        if f and f[0] == "link":
            links.append((f[1], *map(pt, f[2:6])))
        elif f and f[0] == "bbox":
            bbox = tuple(map(pt, f[1:5]))
    minx, miny, maxx, maxy = bbox
    w, h = maxx - minx + 2 * BORDER, maxy - miny + 2 * BORDER

    out = []
    for slug, lx, ly, ux, uy in links:
        out.append({"slug": slug,
                    "x0": round((lx - minx + BORDER) / w, 5),
                    "y0": round((maxy - uy + BORDER) / h, 5),
                    "x1": round((ux - minx + BORDER) / w, 5),
                    "y1": round((maxy - ly + BORDER) / h, 5)})
    json.dump({"aspect": round(w / h, 5), "links": out},
              open(json_path, "w"), indent=1)

    svg = open(svg_path).read()
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    vw, vh = float(vb.group(1)), float(vb.group(2))
    areas = "".join(
        f'<a xlink:href="/{l["slug"]}/" target="_top">'
        f'<rect x="{l["x0"] * vw:.2f}" y="{l["y0"] * vh:.2f}" '
        f'width="{(l["x1"] - l["x0"]) * vw:.2f}" height="{(l["y1"] - l["y0"]) * vh:.2f}" '
        f'fill="transparent" style="cursor:pointer"/></a>\n'
        for l in out)
    svg = svg.replace("</svg>", f'<g id="links">\n{areas}</g>\n</svg>')
    # fill whatever box embeds it (the site's <object>), keeping the aspect
    svg = re.sub(r'(<svg[^>]*?) width="[\d.]+pt" height="[\d.]+pt"',
                 r'\1 width="100%" height="100%"', svg, count=1)
    open(svg_path, "w").write(svg)


if __name__ == "__main__":
    main(*sys.argv[1:4])
