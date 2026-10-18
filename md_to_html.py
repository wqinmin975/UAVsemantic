# -*- coding: utf-8 -*-
"""Regenerate stage2 HTML from stage1/final_draft.md.

The markdown is the single source of truth. This converter reproduces the
formatting conventions of the hand-built HTML:
  - head/CSS and cover section are carried over verbatim from the old HTML
  - the nine hand-crafted <p class="equation"> blocks are reused by number
  - ## -> <h2> inside <div id="section-...">, ### -> <h3>
  - **bold** -> <strong>, *italic* -> <em>, _x -> <sub>x</sub>
  - | tables | -> <p class="table-caption"> + <table class="three-line-table">
  - ![cap](src) -> <p class="figure-img"><img></p> + <p class="figure-caption">
  - > quote -> <p class="note">, N. items -> <ol class="contribution-list">
  - [n] refs -> <p class="reference-item">
"""
import re

BASE = "D:/ace/语义UAV/output/ieee-uav-semantic-ppo-20261014"
MD = BASE + "/stage1/final_draft.md"
HTML = BASE + "/stage2/formatted-uav-semantic-ppo-ieee-paper.html"

SECTION_IDS = {
    "I. Introduction": "section-introduction",
    "II. Related Work": "section-related",
    "III. System Model": "section-system",
    "IV. Methodology": "section-methods",
    "V. Experimental Setup": "section-setup",
    "VI. Results and Discussion": "section-results",
    "VII. Conclusion": "section-conclusion",
    "Acknowledgment": "section-acknowledgment",
    "Data and Code Availability": "section-availability",
    "Nomenclature": "section-nomenclature",
}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    t = re.sub(r"_([A-Za-z0-9]+)", r"<sub>\1</sub>", t)
    return t


def is_equation(block):
    lines = block.split("\n")
    if len(lines) != 1:
        return False
    s = lines[0].strip()
    if not re.search(r"\((\d)\)\s*$", s):
        return False
    if "=" not in s:
        return False
    return not s.startswith(("|", "!", ">", "#"))


def eq_number(block):
    m = re.search(r"\((\d)\)\s*$", block.strip())
    return m.group(1) if m else None


def render_table(block):
    rows = []
    for ln in block.split("\n"):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and all(re.match(r"^:?-+:?$", c) for c in cells if c != ""):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    h = "        <tr>" + "".join("<th>%s</th>" % inline(c) for c in head) + "</tr>"
    b = "\n".join(
        "          <tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>"
        for r in body
    )
    return (
        '      <table class="three-line-table">\n'
        "        <thead>\n          " + h + "\n        </thead>\n"
        "        <tbody>\n" + b + "\n        </tbody>\n"
        "      </table>"
    )


def main():
    old = open(HTML, encoding="utf-8").read()
    head = old[: old.index("<body>") + len("<body>")]
    cover = re.search(
        r"<!-- ============ Cover ============ -->.*?</section>", old, re.S
    ).group(0)
    eqs = {}
    for m in re.finditer(r'<p class="equation">(.*?)</p>', old, re.S):
        inner = m.group(1).strip()
        nm = re.search(r"\((\d)\)\s*$", inner)
        if nm:
            eqs[nm.group(1)] = inner

    md = open(MD, encoding="utf-8").read()
    # defensive: ensure every heading sits in its own block
    md = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", md)
    md = re.sub(r"(#{2,3} [^\n]+)\n(?!\n)", r"\1\n\n", md)
    blocks = [b.strip() for b in md.split("\n\n") if b.strip()]

    abstract = ['    <p class="abstract-heading">&nbsp;&nbsp;Abstract</p>']
    parts = []
    in_abstract = False
    in_refs = False
    div_open = None  # None | "refs" | section id

    def close_div():
        nonlocal div_open, in_refs
        if div_open == "refs":
            parts.append("      </div>")
            parts.append("    </div>")
            in_refs = False
        elif div_open is not None:
            parts.append("    </div>")
        div_open = None

    for b in blocks:
        if b.startswith("# ") and not b.startswith("## "):
            continue  # paper title: lives in the cover
        if b.startswith("## "):
            title = b[3:].strip()
            close_div()
            if title == "Abstract":
                in_abstract = True
                continue
            in_abstract = False
            if title == "References":
                parts.append(
                    '    <div class="references" id="section-references" aria-label="References">'
                )
                parts.append("      <h2>References</h2>")
                parts.append('      <div class="reference-list">')
                div_open = "refs"
                in_refs = True
                continue
            sid = SECTION_IDS[title]
            parts.append('    <div id="%s">' % sid)
            parts.append("      <h2>%s</h2>" % esc(title))
            div_open = sid
            continue
        if b.startswith("### "):
            parts.append("      <h3>%s</h3>" % esc(b[4:].strip()))
            continue
        if b.startswith("**Index Terms**"):
            rest = b[len("**Index Terms**"):].strip()
            abstract.append(
                '    <p class="abstract-text"><span class="cover-meta-label">Index Terms</span> %s</p>'
                % inline(rest)
            )
            continue
        if in_abstract:
            abstract.append(
                '    <p class="abstract-text">&nbsp;&nbsp;%s</p>' % inline(b)
            )
            continue
        if b.startswith("**TABLE"):
            cap = b.strip("*").strip()
            parts.append('      <p class="table-caption">%s</p>' % esc(cap))
            continue
        if b.startswith("|"):
            parts.append(render_table(b))
            continue
        if b.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", b, re.S)
            alt, src = m.group(1).strip(), m.group(2).strip()
            parts.append(
                '      <p class="figure-img"><img src="%s" alt="%s" /></p>'
                % (src, esc(alt))
            )
            parts.append('      <p class="figure-caption">%s</p>' % esc(alt))
            continue
        if b.startswith(">"):
            text = b.lstrip(">").strip()
            parts.append('      <p class="note">&nbsp;&nbsp;%s</p>' % inline(text))
            continue
        lines = b.split("\n")
        if len(lines) > 1 and all(re.match(r"^\d+\.\s", ln) for ln in lines):
            items = "\n".join(
                "        <li>%s</li>" % inline(re.sub(r"^\d+\.\s+", "", ln))
                for ln in lines
            )
            parts.append('      <ol class="contribution-list">\n%s\n      </ol>' % items)
            continue
        if is_equation(b):
            n = eq_number(b)
            if n in eqs:
                parts.append('      <p class="equation">%s</p>' % eqs[n])
            else:
                parts.append('      <p class="equation">%s</p>' % inline(b))
            continue
        if in_refs and re.match(r"^\[\d+\]", b):
            parts.append('        <p class="reference-item">%s</p>' % inline(b))
            continue
        parts.append("      <p>%s</p>" % inline(b))

    close_div()

    abstract_div = (
        '  <div class="abstract" aria-label="Abstract">\n'
        + "\n".join(abstract)
        + "\n  </div>"
    )
    new = (
        head
        + "\n\n"
        + cover
        + '\n\n<!-- ============ Body ============ -->\n'
        + '<section role="body" data-page-restart="1">\n\n'
        + abstract_div
        + '\n\n  <main class="paper-body">\n\n'
        + "\n".join(parts)
        + "\n\n  </main>\n</section>\n</body>\n</html>\n"
    )
    with open(HTML, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("HTML regenerated from md: %d bytes" % len(new))
    print("equations carried over: %s" % sorted(eqs.keys(), key=int))


if __name__ == "__main__":
    main()
