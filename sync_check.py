# -*- coding: utf-8 -*-
"""Check that stage1/final_draft.md and stage2 HTML carry the same text.
Normalization: map superscript/subscript unicode, NFKC, strip HTML tags,
then keep ASCII alphanumerics only. Reports md blocks not found in HTML.
"""
import re
import unicodedata
import html

BASE = "D:/ace/语义UAV/output/ieee-uav-semantic-ppo-20261014"
MD = BASE + "/stage1/final_draft.md"
HTML = BASE + "/stage2/formatted-uav-semantic-ppo-ieee-paper.html"

SUP = str.maketrans({
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-",
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
})


def norm(s: str) -> str:
    s = s.translate(SUP)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def main():
    md = open(MD, encoding="utf-8").read()
    # strip ordered-list markers so md blocks match <ol><li> in HTML
    md = re.sub(r"(?m)^\d+\.\s+", "", md)
    html = open(HTML, encoding="utf-8").read()
    hn = norm(html)

    blocks = [b.strip() for b in md.split("\n\n") if b.strip()]
    missing = []
    for b in blocks:
        if b.startswith("!["):
            continue
        nb = norm(b)
        if nb and nb not in hn:
            missing.append(b)

    print("md blocks: %d | missing in HTML: %d" % (len(blocks), len(missing)))
    for m in missing:
        print("  MISS:", m.split("\n")[0][:100])
    # leftovers that should be gone
    for token in ("doc-toc", "Date:", "Version:", "Figure 1", "Figure 2",
                  "TBD", "TODO", "XXX", "strictly more favorable"):
        if token in html:
            print("  LEFTOVER in HTML:", token)


if __name__ == "__main__":
    main()
