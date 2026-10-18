# -*- coding: utf-8 -*-
"""Debug: find exact divergence point between md blocks and HTML text."""
import re
import unicodedata
import html as H

BASE = "D:/ace/语义UAV/output/ieee-uav-semantic-ppo-20261014"
SUP = str.maketrans({
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-",
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
})


def norm(s):
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s)
    s = s.translate(SUP)
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    return re.sub(r"[^a-z0-9]+", "", s)


md = open(BASE + "/stage1/final_draft.md", encoding="utf-8").read()
ht = open(BASE + "/stage2/formatted-uav-semantic-ppo-ieee-paper.html", encoding="utf-8").read()
hn = norm(ht)

blocks = [b.strip() for b in md.split("\n\n") if b.strip()]
n_miss = 0
for b in blocks:
    if b.startswith("![") or b.lstrip().startswith("|"):
        continue
    nb = norm(b)
    if not nb or nb in hn:
        continue
    n_miss += 1
    lo, hi = 0, len(nb)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if nb[:mid] in hn:
            lo = mid
        else:
            hi = mid - 1
    print("=" * 90)
    print("BLOCK:", b[:70].replace("\n", " "))
    print("matched %d / %d chars" % (lo, len(nb)))
    print("  md  :", nb[max(0, lo - 30):lo + 50])
    ctx = nb[max(0, lo - 30):lo]
    j = hn.find(ctx)
    if j >= 0:
        print("  html:", hn[j:j + 110])
print("=" * 90)
print("total missing:", n_miss)
