# -*- coding: utf-8 -*-
"""Apply de-AIGC edits (JSON list of {loc, before, after}) to the markdown.
Each `before` must occur exactly once; apostrophe style is auto-adapted.
`after` == "[deleted]" removes the matched text. Usage: python apply_edits.py edits.json
"""
import json
import re
import sys

MD = "D:/ace/语义UAV/output/ieee-uav-semantic-ppo-20261014/stage1/final_draft.md"


def smart_replace(text, before, after):
    if after == "[deleted]":
        for b in (before, before.replace("'", "\u2019"), before.replace("\u2019", "'")):
            if b in text:
                text = text.replace(b, "", 1)
                text = re.sub(r"[ \t]+\n", "\n", text)
                text = re.sub(r" +([.,;:])", r"\1", text)
                text = re.sub(r"\n{3,}", "\n\n", text)
                return text, "deleted"
        raise AssertionError("BEFORE not found:\n%s" % before[:160])
    if before in text:
        return text.replace(before, after, 1), "exact"
    for a, b in (("'", "\u2019"), ("\u2019", "'")):
        b2, a2 = before.replace(a, b), after.replace(a, b)
        if b2 in text:
            return text.replace(b2, a2, 1), "apostrophe-adapted"
    raise AssertionError("BEFORE not found:\n%s" % before[:160])


def main():
    text = open(MD, encoding="utf-8").read()
    total = 0
    for path in sys.argv[1:]:
        edits = json.load(open(path, encoding="utf-8"))
        for i, e in enumerate(edits, 1):
            text, how = smart_replace(text, e["before"], e["after"])
            print("EDIT %d applied (%s): %s" % (total + i, how, e["loc"][:70]))
        total += len(edits)
    open(MD, "w", encoding="utf-8", newline="\n").write(text)
    print("all %d edits applied -> %s" % (total, MD))


if __name__ == "__main__":
    main()
