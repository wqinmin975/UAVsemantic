# -*- coding: utf-8 -*-
"""Verify key properties of the generated IEEE docx."""
import re
import sys
import zipfile

path = sys.argv[1]
z = zipfile.ZipFile(path)
names = z.namelist()
media = [n for n in names if n.startswith("word/media/")]
doc = z.read("word/document.xml").decode("utf-8")

print("file:", path)
print("media files:", len(media))
print("blips (image refs in body):", doc.count("<a:blip"))
print("tables:", doc.count("<w:tbl>"))
print("tblBorders:", doc.count("<w:tblBorders"))
print("'Figure ' occurrences:", doc.count("Figure "))
print("'Fig. ' occurrences:", doc.count("Fig. "))
print("TBD/TODO:", doc.count("TBD"), doc.count("TODO"))
print("literal backslash:", doc.count(chr(92)))
print("double hyphen:", doc.count("--"))
eqs = sorted(set(int(m) for m in re.findall(r"\((\d)\)", doc)))
print("parenthesized single digits present:", eqs)
print("sub tags (true subscripts):", doc.count("<w:sub"))
print("sup tags (true superscripts):", doc.count("<w:sup"))
print("doc size bytes:", len(doc))
