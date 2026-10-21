#!/usr/bin/env python3
"""Reader view for every saved HTML source: article text only, taken word for word from the raw copy.
Raw copies stay untouched and are offered as downloads. Run after build_site.py, before add_zoom.py."""
import re, html, pathlib, hashlib, sys
from bs4 import BeautifulSoup
R = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "scripts"))
from _norm import norm
E = lambda s: html.escape(s, quote=True)
BASE = ["script", "style", "noscript", "svg", "template"]
NOISE = BASE + ["nav", "header", "footer", "aside", "form", "button", "dialog", "iframe", "select"]
BLOCK = ["h1", "h2", "h3", "h4", "p", "li", "pre", "td", "th", "blockquote", "div", "span"]

def extract(raw, mode):
    s = BeautifulSoup(raw, "html.parser")
    for t in s(BASE if mode == "full" else NOISE): t.decompose()
    root = None
    if mode == "main":
        c = [e for sel in ("article", "main", "[role=main]") for e in s.select(sel)]
        if c: root = max(c, key=lambda e: len(e.get_text(" ", strip=True)))
    root = root or s.body or s
    out = []
    for el in root.find_all(BLOCK):
        inner = ["p", "li", "pre", "h1", "h2", "h3", "h4", "td", "blockquote"]
        if el.name in ("div", "span"):
            if el.find(inner + ["div", "span", "table"]): continue
        elif el.name in ("li", "td", "th", "blockquote") and el.find(inner): continue
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if t and (not out or out[-1][1] != t): out.append((el.name, t))
    return out

def mapped(text):
    """normalised text plus, for each normalised char, its index in the original text"""
    rep = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"', "\u00a0": " ", "\u2011": "-"}
    chars, idx, prev_space = [], [], True
    for i, ch in enumerate(text):
        ch = rep.get(ch, ch)
        if ch.isspace():
            if prev_space: continue
            ch = " "; prev_space = True
        else: prev_space = False
        chars.append(ch.lower()); idx.append(i)
    return "".join(chars), idx

def render(text, quotes):
    n, idx = mapped(text); spans = []
    for q in quotes:
        qn = norm(q).lower(); k = n.find(qn)
        if k >= 0: spans.append((idx[k], idx[k + len(qn) - 1] + 1))
    spans.sort(); out, pos = "", 0
    for a, b in spans:
        if a < pos: continue
        out += E(text[pos:a]) + "<mark>" + E(text[a:b]) + "</mark>"; pos = b
    return out + E(text[pos:])

quotes = {}
for ln in (R / "evidence" / "quotes.tsv").read_text(encoding="utf-8").splitlines():
    if "\t" in ln: sid, q = ln.split("\t", 1); quotes.setdefault(sid, []).append(q)
man = (R / "evidence" / "manifest.txt").read_text(errors="ignore")
tpl = (R / "public" / "glossary" / "index.html").read_text()
head, tail = tpl[:tpl.index("</header>") + 9], tpl[tpl.index("<footer"):]
CSS = ('<style id="rdcss">.rd{max-width:78ch}.rd h3{font-size:19px;line-height:1.35;margin:28px 0 8px}.rd p{margin:0 0 14px;font-size:16px;line-height:1.5}'
       '.rd mark{background:rgba(252,211,77,.28);color:inherit;padding:0 2px;border-radius:2px}.rdm{display:grid;gap:8px;margin:0 0 28px;font-size:14px}'
       '.rdm div{display:flex;gap:12px;flex-wrap:wrap}.rdm b{font:600 12px "JetBrains Mono",monospace;color:var(--mu);min-width:96px;text-transform:uppercase;letter-spacing:.05em}'
       '.rdm code{overflow-wrap:anywhere;font-size:12px}</style>')
n = 0
for f in sorted((R / "evidence" / "snapshots").glob("S*.html"), key=lambda x: int(x.stem[1:])):
    sid = f.stem; raw = f.read_text(errors="ignore"); qs = quotes.get(sid, [])
    for mode in ("main", "body", "full"):
        lines = extract(raw, mode); body = norm(" ".join(t for _, t in lines)).lower()
        if all(norm(q).lower() in body for q in qs): break
    title = norm(re.search(r"(?is)<title[^>]*>(.*?)</title>", raw).group(1)) if re.search(r"(?is)<title", raw) else sid
    m = re.search(rf"^{sid} (\S+) (\S+)$", man, re.M); cap, url = (m.group(1), m.group(2)) if m else ("", "")
    hm = re.search(rf"^([0-9a-f]{{64}})  {sid}\.html$", man, re.M); sha = hm.group(1) if hm else ""
    paras = "".join(("<h3>%s</h3>" if t.startswith("h") else "<p>%s</p>") % render(x, qs) for t, x in lines)
    meta = (f'<div><b>Source</b><a href="{E(url)}" target="_blank" rel="noopener">{E(url)}</a></div>' if url else "") + \
           (f'<div><b>Captured</b><span class="mono">{E(cap)}</span></div>' if cap else "") + \
           (f'<div><b>Raw SHA-256</b><code>{sha}</code></div>' if sha else "") + \
           f'<div><b>Raw copy</b><a href="/evidence/files/snapshots/{f.name}.txt" target="_blank" rel="noopener">Open {f.name} (verbatim, as plain text)</a></div>' + \
           '<div><b>What this is</b><span>Article text from the saved raw copy, words unchanged. Menus, sign-in forms, footers and scripts are left out. Phrases used in the report are highlighted.</span></div>'
    body_html = f'<main><h2 class="sec">{sid}: {E(title)}</h2><div class="rdm card">{meta}</div><div class="rd">{paras}</div><p style="margin-top:32px"><a href="/evidence/#{sid}">Back to evidence</a></p></main>'
    h = head.replace("</head>", CSS + "</head>", 1)
    h = re.sub(r'<meta property="og:site_name" content="[^"]*"', '<meta property="og:site_name" content="Quant Overledger"', h)
    h = re.sub(r"<title>.*?</title>", f"<title>{E(sid)} reader view | Quant Overledger</title>", h, flags=re.S)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(sid + " reader view"), h)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*', lambda m: m.group(1) + E(sid + " reader view"), h)
    d = R / "public" / "evidence" / "source" / sid; d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(h + body_html + tail, encoding="utf-8"); n += 1
print("reader views:", n)
