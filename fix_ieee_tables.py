# -*- coding: utf-8 -*-
"""Post-process docx: apply IEEE three-line table borders (top 1.5pt, header rule 0.5pt, bottom 1.5pt; no verticals)."""
import sys
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

path = sys.argv[1]
doc = Document(path)

def set_borders(el, edges):
    borders = el.find(qn('w:tblBorders'))
    if borders is None:
        borders = OxmlElement('w:tblBorders')
        # tblBorders must come after tblW/tblInd per schema; append is tolerated by Word
        el.append(borders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        old = borders.find(qn(f'w:{edge}'))
        if old is not None:
            borders.remove(old)
        e = OxmlElement(f'w:{edge}')
        sz = edges.get(edge)
        if sz is None:
            e.set(qn('w:val'), 'none'); e.set(qn('w:sz'), '0'); e.set(qn('w:space'), '0')
        else:
            e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000')
        borders.append(e)

def cell_bottom_border(cell, sz=4):
    tcPr = cell._tc.get_or_add_tcPr()
    old = tcPr.find(qn('w:tcBorders'))
    if old is not None:
        tcPr.remove(old)
    b = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        e = OxmlElement(f'w:{edge}')
        if edge == 'bottom':
            e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000')
        else:
            e.set(qn('w:val'), 'none'); e.set(qn('w:sz'), '0'); e.set(qn('w:space'), '0')
        b.append(e)
    tcPr.append(b)

n = 0
for tbl in doc.tables:
    set_borders(tbl._tbl.tblPr, {'top': 12, 'bottom': 12})
    if len(tbl.rows) >= 1:
        for cell in tbl.rows[0].cells:
            cell_bottom_border(cell, 4)
    n += 1

doc.save(path)
print(f"three-line borders applied to {n} tables")
