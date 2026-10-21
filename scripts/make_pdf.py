#!/usr/bin/env python3
"""Builds public/downloads/report.pdf from REPORT.md in Redbelly DAO brand style (light page, steel cover band)."""
import re, glob, html
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor as H, white
from reportlab.lib.styles import ParagraphStyle as S
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Preformatted

R = Path(__file__).resolve().parent.parent
F = R / "scripts" / "fonts"
for n, f in [("BV", "BeVietnamPro-Regular"), ("BV-SB", "BeVietnamPro-SemiBold"), ("BV-B", "BeVietnamPro-Bold"), ("JM", "JetBrainsMono-Regular"), ("JM-B", "JetBrainsMono-Bold")]:
    pdfmetrics.registerFont(TTFont(n, str(F / f"{f}.ttf")))
pdfmetrics.registerFontFamily("BV", normal="BV", bold="BV-B", italic="BV", boldItalic="BV-B")
RED, STEEL, INK, MUTE, LINE = H("#EF5350"), H("#1d3140"), H("#0c1317"), H("#51626d"), H("#d8e0e5")
COL = {"Confirmed": H("#1f8a55"), "Tested": H("#1d79b5"), "Analysis": H("#9a6b0a"), "Unknown": H("#51626d")}
body = S("b", fontName="BV", fontSize=9.8, leading=15, textColor=INK, spaceAfter=7)
h1 = S("h1", fontName="BV-B", fontSize=17, leading=22, textColor=INK, spaceBefore=14, spaceAfter=8)
h2 = S("h2", fontName="BV-B", fontSize=12, leading=16, textColor=INK, spaceBefore=10, spaceAfter=5)
cell = S("c", parent=body, fontSize=8.2, leading=11, spaceAfter=0)
bul = S("bl", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=3)
W, Hh = A4

def inline(t):
    t = html.escape(t)
    t = re.sub(r"\[([ST]\d+)\]", r'<font name="JM-B" size="8" color="#EF5350">[\1]</font>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r'<font name="JM" size="8.6">\1</font>', t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2"><font color="#EF5350"><u>\1</u></font></link>', t)
    t = re.sub(r"(?<![\"=>])(https?://[^\s<)]+)", r'<link href="\1"><font color="#EF5350"><u>\1</u></font></link>', t)
    return t

def status(t):
    m = re.match(r"\*\*(Confirmed|Tested|Analysis|Unknown)\.?\*\*\.?\s*(.*)", t, re.S)
    if not m: return Paragraph(inline(t), body)
    c = COL[m[1]]
    lab = Paragraph(f'<font name="JM-B" size="7.6" color="{c.hexval().replace("0x", "#")}">{m[1].upper()}</font>', cell)
    tb = Table([[lab, Paragraph(inline(m[2]), cell.clone("x", fontSize=9.4, leading=14))]], colWidths=[22 * mm, None])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 8), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("BACKGROUND", (0, 0), (-1, -1), H("#f5f7f8"))]))
    return KeepTogether([tb, Spacer(1, 6)])

def table(rows):
    rows = [r for r in rows if not re.match(r"^\|[\s:|-]+\|$", r)]
    data = [[Paragraph(inline(c.strip()) if i else f'<font name="BV-B" color="#ffffff">{html.escape(c.strip())}</font>', cell) for c in r.strip().strip("|").split("|")] for i, r in enumerate(rows)]
    n = len(data[0]); t = Table(data, colWidths=[(W - 36 * mm) / n] * n, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), STEEL), ("GRID", (0, 0), (-1, -1), .4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, H("#f5f7f8")]), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return [t, Spacer(1, 8)]

def story(md):
    out, para, tb, code = [], [], [], None
    def flush():
        nonlocal para, tb
        if para: out.append(status(" ".join(para))); para = []
        if tb: out.extend(table(tb)); tb = []
    for l in md.splitlines():
        if l.startswith("```"):
            if code is None: flush(); code = []
            else: out.append(Preformatted("\n".join(code), S("p", fontName="JM", fontSize=7.8, leading=11, backColor=H("#f5f7f8"), borderPadding=6, spaceAfter=8))); code = None
            continue
        if code is not None: code.append(l); continue
        if l.startswith("|"): tb.append(l); continue
        flush()
        if re.match(r"^#{1,2} ", l): out.append(Paragraph(inline(l.lstrip("# ")), h1))
        elif l.startswith("#"): out.append(Paragraph(inline(l.lstrip("# ")), h2))
        elif re.match(r"^\s*[-*] ", l): out.append(Paragraph(inline(re.sub(r"^\s*[-*] ", "", l)), bul, bulletText="\u2022"))
        elif re.match(r"^\d+\. ", l) and not l.strip().endswith(":") and False: pass
        elif l.strip(): para.append(l.strip())
        else: flush()
    flush(); return out

md = (R / "REPORT.md").read_text()
title = (re.search(r"^# (.+)$", md, re.M) or [0, "Research report"])[1]
md_body = re.sub(r"^# .+\n", "", md, count=1, flags=re.M)

def cover(c, d):
    c.setFillColor(STEEL); c.rect(0, Hh - 120 * mm, W, 120 * mm, 0, 1)
    c.setFillColor(RED); c.rect(18 * mm, Hh - 52 * mm, 14 * mm, 1.6 * mm, 0, 1)
    lg = R / "public" / "brand" / "dao-logo-on-dark.png"
    if lg.exists(): c.drawImage(str(lg), 18 * mm, Hh - 40 * mm, height=16 * mm, preserveAspectRatio=True, mask="auto")
    c.setFillColor(white); c.setFont("BV-B", 26)
    y = Hh - 70 * mm
    for ln in __import__("textwrap").wrap(title, 34): c.drawString(18 * mm, y, ln); y -= 11 * mm
    c.setFont("BV", 11); c.setFillColor(H("#c3d0d8")); c.drawString(18 * mm, Hh - 108 * mm, "Redbelly DAO research task")
    c.setFont("JM", 8.5); c.setFillColor(MUTE); c.drawString(18 * mm, 18 * mm, "Last verified 21 Oct 2026")

def later(c, d):
    c.setStrokeColor(LINE); c.line(18 * mm, Hh - 14 * mm, W - 18 * mm, Hh - 14 * mm)
    c.setFont("BV-SB", 8); c.setFillColor(MUTE); c.drawString(18 * mm, Hh - 11 * mm, title[:80])
    c.setFillColor(RED); c.rect(W - 18 * mm - 1.6 * mm, Hh - 12 * mm, 1.6 * mm, 1.6 * mm, 0, 1)
    c.setFont("JM", 8); c.setFillColor(MUTE); c.drawRightString(W - 18 * mm - 4 * mm, Hh - 11 * mm, f"{d.page}")
    c.drawString(18 * mm, 10 * mm, "Last verified 21 Oct 2026")

(R / "public" / "downloads").mkdir(parents=True, exist_ok=True)
for old in glob.glob(str(R / "public" / "downloads" / "*.pdf")): Path(old).unlink()
outp = R / "public" / "downloads" / "Quant-Overledger-Redbelly-Report.pdf"
doc = BaseDocTemplate(str(outp), pagesize=A4, title=title, leftMargin=18 * mm, rightMargin=18 * mm)
fr = Frame(18 * mm, 18 * mm, W - 36 * mm, Hh - 36 * mm, id="f")
doc.addPageTemplates([PageTemplate("cover", [Frame(18 * mm, 18 * mm, W - 36 * mm, Hh - 140 * mm)], onPage=cover), PageTemplate("body", [fr], onPage=later)])
from reportlab.platypus import NextPageTemplate
doc.build([NextPageTemplate("body"), Paragraph("Contents", h1)] + [Paragraph(inline(m), body) for m in re.findall(r"^#{1,3} (\d+\. .+)$", md_body, re.M)] + [PageBreak()] + story(md_body))
print("pdf ok")
