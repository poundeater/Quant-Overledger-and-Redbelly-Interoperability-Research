#!/usr/bin/env python3
"""Builds public/ from REPORT.md, SOURCES.md and evidence/. Run from repo root."""
import re, json, html, shutil, glob
from pathlib import Path
import markdown

R = Path(__file__).resolve().parent.parent
P = R / "public"
E = html.escape
ST = ["Confirmed", "Tested", "Analysis", "Unknown"]
MD = lambda t: markdown.markdown(t, extensions=["tables", "fenced_code"])

rep = (R / "REPORT.md").read_text()
title = (re.search(r"^# (.+)$", rep, re.M) or [None, "Research report"])[1]
parts = re.split(r"^#{1,3}\s+(?=\d+\.\s)", rep, flags=re.M)
chapters = []
for p in parts[1:]:
    head, _, body = p.partition("\n")
    m = re.match(r"(\d+)\.\s+(.*)", head.strip())
    chapters.append(dict(n=int(m[1]), title=m[2].strip(), md=body.strip(), slug=f"{m[1]}-" + re.sub(r"[^a-z0-9]+", "-", m[2].lower()).strip("-")))
intro = parts[0].split("\n", 1)[-1].strip() if parts else ""

def cite(t):
    return re.sub(r"\[([ST]\d+)\]", lambda m: '<a class="chip" href="/%s/#%s">%s</a>' % ("evidence" if m.group(1)[0] == "T" else "sources", m.group(1), m.group(1)), t)

def status_html(h):
    def f(m):
        s = m[1]
        return f'<div class="blk {s.lower()}"><span class="lbl"><i></i>{s}</span><p>'
    h = re.sub(r"<p><strong>(Confirmed|Tested|Analysis|Unknown)\.?</strong>\.?\s*", f, h)
    h = re.sub(r'(<div class="blk[^>]*>.*?)</p>', r"\1</p></div>", h, flags=re.S)
    return h

def chapter_html(c):
    h = status_html(MD(c["md"]))
    return cite(h)

def counts(md):
    return {s: len(re.findall(rf"^\*\*{s}\.?\*\*", md, re.M)) for s in ST}

CSS = """@font-face{font-family:'Be Vietnam Pro';font-weight:400;src:url(/fonts/BeVietnamPro-Regular.ttf)}@font-face{font-family:'Be Vietnam Pro';font-weight:600;src:url(/fonts/BeVietnamPro-SemiBold.ttf)}@font-face{font-family:'Be Vietnam Pro';font-weight:700;src:url(/fonts/BeVietnamPro-Bold.ttf)}@font-face{font-family:'JetBrains Mono';font-weight:400;src:url(/fonts/JetBrainsMono-Regular.ttf)}@font-face{font-family:'JetBrains Mono';font-weight:700;src:url(/fonts/JetBrainsMono-Bold.ttf)}
:root{--ab:#fff;--hov:#223039;--hovb:#34444f;--act:#17222a;--bg:#0c1317;--card:#141f26;--bd:#263641;--tx:#f1f5f8;--mu:#8fa1ad;--red:#EF5350;--acct:#ffb3ae;--hero:#1d3140;--tint:rgba(239,83,80,.12);--ok:#86EFAC;--te:#8fa1ad;--an:#8fa1ad;--un:#FCD34D}
:root[data-theme=light]{--ab:#8fa1ad;--hov:#F4F7F9;--hovb:#8fa1ad;--act:#fff;--bg:#EDF1F4;--card:#fff;--bd:#C9D5DC;--tx:#0F1A22;--mu:#51626d;--acct:#B3272A;--tint:rgba(239,83,80,.09);--ok:#86EFAC;--te:#8fa1ad;--an:#8fa1ad;--un:#FCD34D}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.5 'Be Vietnam Pro',system-ui,sans-serif}
a{color:var(--acct)}code,.mono{font-family:'JetBrains Mono',monospace}
.nav .logo-l{display:none}:root[data-theme=light] .nav .logo-l{display:block}:root[data-theme=light] .nav .logo-d{display:none}
header{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--bd)}
.nav{max-width:1180px;margin:auto;padding:12px 24px;display:flex;align-items:center;gap:16px}
.nav img{height:44px;display:block}.sp{flex:1}
.nav a.b,.tg{font:600 14px 'Be Vietnam Pro';color:var(--tx);text-decoration:none;padding:7px 14px;border:1px solid var(--bd);border-radius:4px;background:var(--card);cursor:pointer;transition:.15s}
.nav a.b:hover{border-color:var(--hovb);background:var(--hov)}.nav a.b:active,.nav a.on,.nav a.on:hover{background:var(--act);border-color:var(--ab);color:var(--tx)}
.tg:hover{border-color:var(--hovb);background:var(--hov)}
.tg{width:38px;height:36px;padding:0;display:grid;place-items:center}.tg svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2}
.tg .sun{display:none}:root[data-theme=light] .tg .sun{display:block}:root[data-theme=light] .tg .moon{display:none}
.hero{background:var(--hero);color:#fff;border-bottom:1px solid var(--bd)}
.hero div{max-width:1180px;margin:auto;padding:64px 24px}
.hero h1{font-size:clamp(30px,5vw,48px);line-height:1.15;margin:0 0 16px;max-width:820px}
.hero p{color:#c3d0d8;max-width:720px;margin:0 0 24px}
.btn{display:inline-block;font:600 14px 'Be Vietnam Pro';padding:10px 20px;border-radius:4px;text-decoration:none;margin:0 10px 10px 0;border:1px solid #3b4d5a;background:#1d3140;color:#fff;transition:.15s}.btn:hover{border-color:#fff}.btn.p{background:#EF5350;border-color:#EF5350}.btn.p:hover{filter:brightness(1.08)}
main{max-width:1180px;margin:auto;padding:40px 24px 80px}
h2.sec{font-size:24px;margin:48px 0 18px}h2.sec:first-child{margin-top:0}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
.card{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:20px;color:inherit;text-decoration:none;display:block;transition:.15s}
a.card:hover{border-color:var(--hovb);background:var(--hov)}
.card .n{font:700 13px 'JetBrains Mono';color:var(--acct)}.card h3{margin:6px 0 10px;font-size:17px;line-height:1.35}
.card p{margin:0;color:var(--mu);font-size:14px;line-height:1.55}
.dots{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;font:12px 'JetBrains Mono';color:var(--mu)}
.dots span{display:flex;align-items:center;gap:5px}
i{width:8px;height:8px;border-radius:50%;background:var(--un);display:inline-block}
.confirmed i{background:var(--ok)}.tested i{background:var(--te)}.analysis i{background:var(--an)}
.stat{text-align:left}.stat b{display:block;font:700 34px 'JetBrains Mono'}.stat span{font:12px 'JetBrains Mono';text-transform:uppercase;letter-spacing:.06em;color:var(--mu);display:flex;gap:6px;align-items:center}
.layout{display:grid;grid-template-columns:270px minmax(0,1fr);gap:48px}
aside{position:sticky;top:84px;align-self:start;max-height:calc(100vh - 100px);overflow:auto;padding:16px 12px;background:var(--card);border:1px solid var(--bd);border-radius:8px;scrollbar-width:thin;scrollbar-color:var(--bd) transparent}
aside .tg-h{font:11px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--mu);margin:20px 8px 6px}aside .tg-h:first-child{margin-top:0}
aside a{display:grid;grid-template-columns:28px 1fr;align-items:baseline;gap:10px;color:var(--mu);text-decoration:none;padding:9px 10px;border:1px solid transparent;border-radius:4px;font-size:15px;line-height:1.4}
aside a .nn{font:12px 'JetBrains Mono',monospace;color:var(--mu)}
aside a:hover{background:var(--hov);border-color:var(--hovb);color:var(--tx)}aside a.on{border-color:var(--ab);background:var(--act);color:var(--tx);font-weight:600}aside a.on .nn{color:var(--acct)}
aside a:focus-visible{outline:2px solid var(--acct);outline-offset:2px}
article{min-width:0;max-width:780px}article h1{font-size:36px;line-height:1.2;margin:0 0 24px}
article h2,article h3{margin:32px 0 10px}article table{border-collapse:collapse;width:100%;display:block;overflow:auto;margin:16px 0}
article th,article td{border:1px solid var(--bd);padding:8px 12px;text-align:left;font-size:14px}article th{background:var(--card)}
.blk{background:var(--card);border:1px solid var(--bd);border-radius:6px;padding:14px 18px;margin:16px 0}

.blk p{margin:6px 0 0}.lbl{display:flex;align-items:center;gap:7px;font:700 12px 'JetBrains Mono';text-transform:uppercase;letter-spacing:.06em;color:var(--mu)}
.chip{font:600 11px/0 'JetBrains Mono',monospace;vertical-align:super;position:relative;top:-.05em;text-decoration:none;color:var(--acct);background:none;border:0;border-radius:0;padding:0 1px;margin:0 1px 0 0;letter-spacing:-.02em}
.chip+.chip{margin-left:3px}
.chip:hover,.chip:focus-visible{text-decoration:underline;text-underline-offset:2px;color:var(--tx)}
pre{background:#0a1014;color:#d6e2e9;border:1px solid var(--bd);border-radius:6px;padding:16px;overflow:auto;font:13px/1.6 'JetBrains Mono'}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:48px}.pn .card{padding:16px}.pn small{font:12px 'JetBrains Mono';color:var(--mu);display:block}.pn .r{text-align:right}
.src{scroll-margin-top:90px}.ext{display:inline-block;font:600 13px 'Be Vietnam Pro';text-decoration:none;color:#fff;background:var(--red);padding:6px 14px;border-radius:4px}.src h3{margin:6px 0 4px}.src dl{margin:10px 0 0;font-size:14px}.src dt{font:700 11px 'JetBrains Mono';color:var(--mu);text-transform:uppercase;margin-top:8px}.src dd{margin:2px 0 0;word-break:break-word}
.ev h3{margin:0 0 4px;font-size:16px}.ev .meta{font:12px 'JetBrains Mono';color:var(--mu);margin-bottom:12px}
details{margin-top:12px}summary{cursor:pointer;font-weight:600;color:var(--red)}
.tw{overflow:auto;max-height:460px;border:1px solid var(--bd);border-radius:6px}.tw table{border-collapse:collapse;width:100%;font-size:13px}
.tw th{position:sticky;top:0;background:var(--hero);color:#fff;text-align:left;font:600 12px 'JetBrains Mono'}.tw th,.tw td{padding:7px 12px;border-bottom:1px solid var(--bd);white-space:nowrap}

.md h1{font-size:20px;margin:12px 0}.md h2{font-size:17px}.md table{border-collapse:collapse;display:block;overflow:auto;font-size:13px}.md td,.md th{border:1px solid var(--bd);padding:6px 10px;text-align:left}.md p{font-size:14px;color:var(--mu)}
footer{border-top:1px solid var(--bd);padding:24px;text-align:center;color:var(--mu);font:12px 'JetBrains Mono'}
@media(max-width:860px){.layout{grid-template-columns:1fr}aside{position:static;max-height:none}.nav{flex-wrap:wrap}.nav img{height:36px}.hero div{padding:40px 24px}}
"""

CSS += """.ans h3{font-size:18px;line-height:1.35;margin:0 0 10px}.ans p{color:var(--tx);font-size:16px;line-height:1.5;margin:0 0 14px;max-width:72ch}.ans .lbl{margin-top:auto}.ans{display:flex;flex-direction:column}
.cp{font:600 13px 'Be Vietnam Pro';color:#fff;background:#EF5350;border:1px solid #EF5350;border-radius:4px;padding:6px 14px;cursor:pointer}.cp:hover{filter:brightness(1.08)}
.post p{margin:8px 0 14px;color:var(--tx);font-size:15px}.pf{display:flex;justify-content:space-between;align-items:center;gap:12px}.pf span{font:12px 'JetBrains Mono';color:var(--mu)}
.card svg,.fig svg{width:100%;height:auto;display:block;border-radius:6px}.fig{margin:24px 0}.gl h3{margin:0 0 6px;font-size:16px}.gl p{margin:0;font-size:15px;color:var(--mu)}.card.lead p{color:var(--tx);font-size:16px;margin:0 0 14px}
"""

SITE="Quant Overledger"
DESC="Feasibility research on whether Redbelly could connect to Quant Overledger. Public sources only, every claim sourced and labelled Confirmed, Tested, Analysis or Unknown."
def page(name, body, active, extra="", desc=None):
    desc = desc or DESC
    links = [("Report", "/chapters/" + chapters[0]["slug"] + "/", "report"), ("Sources", "/sources/", "sources"), ("Evidence", "/evidence/", "evidence"), ("Community", "/community/", "community"), ("Glossary", "/glossary/", "glossary")]
    nav = "".join(f'<a class="b{" on" if k == active else ""}" href="{h}">{t}</a>' for t, h, k in links)
    for ext, lab in (("pdf", "PDF"), ("docx", "Word")):
        nav += f'<a class="b" href="/downloads/Quant-Overledger-Redbelly-Report.{ext}" target="_blank" rel="noopener">{lab}</a>'
    logo = '<img class="logo-d" src="/brand/dao-logo-on-dark.png" alt="Redbelly DAO" onerror="this.onerror=null;this.src=\'https://taskboard.redbellydao.network/brand/dao-logo-on-dark.png\'"><img class="logo-l" src="/brand/dao-logo-on-light.png" alt="Redbelly DAO" onerror="this.onerror=null;this.src=\'https://taskboard.redbellydao.network/brand/dao-logo-on-light.png\'">'
    icon = '<button class="tg" id="tg" aria-label="Toggle theme"><svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>'
    js = "var r=document.documentElement,t=null;try{t=localStorage.getItem('th')}catch(e){}r.dataset.theme=t||'dark';document.getElementById('tg').onclick=function(){var n=r.dataset.theme=='dark'?'light':'dark';r.dataset.theme=n;try{localStorage.setItem('th',n)}catch(e){}}"
    js += ";document.addEventListener('click',function(e){var b=e.target.closest('.cp');if(b){navigator.clipboard.writeText(b.dataset.t).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent=b.dataset.l},1500)})}});"
    boot = "<script>try{document.documentElement.dataset.theme=localStorage.getItem('th')||'dark'}catch(e){document.documentElement.dataset.theme='dark'}</script>"
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(name)}</title>
<meta name="description" content="{E(desc)}"><meta name="theme-color" content="#1d3140"><meta name="color-scheme" content="dark light"><meta property="og:type" content="website"><meta property="og:site_name" content="{E(SITE)}"><link rel="icon" href="/brand/favicon.svg" type="image/svg+xml"><link rel="icon" href="/brand/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/brand/favicon.png"><meta property="og:title" content="{E(name)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="https://quant-overledger-research.vercel.app/brand/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Feasibility research: could Redbelly connect to Quant Overledger"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(name)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="https://quant-overledger-research.vercel.app/brand/og.png">
{boot}<style>{CSS}</style></head><body><header><div class="nav"><a href="/">{logo}</a><span class="sp"></span>{nav}{icon}</div></header>{body}<footer>Last verified 21 Oct 2026</footer><script>{js}</script></body></html>'''

def write(rel, s):
    f = P / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s)

for f in glob.glob(str(R/"scripts"/"fonts"/"*.ttf")): (P/"fonts").mkdir(parents=True,exist_ok=True); shutil.copy(f,P/"fonts")
for d in ("chapters", "sources", "evidence", "community", "glossary"): shutil.rmtree(P / d, ignore_errors=True)
for old in P.glob("*.html"): old.unlink()
(R / "vercel.json").write_text(json.dumps({"outputDirectory": "public", "cleanUrls": True, "trailingSlash": True}, indent=2))
FIG = {2: ["stack"], 3: ["selfserve", "fusion"], 4: ["access", "receptor"], 5: ["routes", "levels"], 6: ["work"], 8: ["boundary", "breaks"]}
def figs(n):
    out = ""
    for k in FIG.get(n, []):
        f = P / "diagrams" / f"{k}.svg"
        if f.exists(): out += f'<figure class="fig">{f.read_text()}</figure>'
    return out
# chapters
TOC_GROUPS = [("Background", [1, 2, 3]), ("Redbelly", [4, 5]), ("Analysis", [6, 7, 8]), ("Open questions", [9, 10, 11])]
for i, c in enumerate(chapters):
    side = ""
    for g, nums in TOC_GROUPS:
        side += f'<p class="tg-h">{g}</p>'
        for j, x in enumerate(chapters):
            if x["n"] in nums:
                side += f'<a class="{"on" if j == i else ""}" href="/chapters/{x["slug"]}/"{" aria-current=page" if j == i else ""}><span class="nn">{x["n"]:02d}</span><span>{E(x["title"])}</span></a>'
    pv = f'<a class="card" href="/chapters/{chapters[i-1]["slug"]}/"><small>Previous</small>{E(chapters[i-1]["title"])}</a>' if i else "<span></span>"
    nx = f'<a class="card r" href="/chapters/{chapters[i+1]["slug"]}/"><small>Next</small>{E(chapters[i+1]["title"])}</a>' if i < len(chapters) - 1 else "<span></span>"
    body = f'<main><div class="layout"><aside>{side}</aside><article><h1>{c["n"]}. {E(c["title"])}</h1>{figs(c["n"])}{chapter_html(c)}<div class="pn">{pv}{nx}</div></article></div></main>'
    write(f'chapters/{c["slug"]}/index.html', page(f'{c["title"]} | {SITE}', body, "report"))

# sources
src_md = (R / "SOURCES.md").read_text() if (R / "SOURCES.md").exists() else ""
rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in src_md.splitlines() if l.strip().startswith("|")]
hdr = rows[0] if rows else []
def link(v):
    return re.sub(r"(https?://[^\s<>)|]+)", r'<a class="ext" href="\1" target="_blank" rel="noopener">Open source</a>', E(v)) if re.match(r"^https?://", v) else E(v)
def mk(r):
    dl = "".join(f"<dt>{E(h)}</dt><dd>{link(v)}</dd>" for h, v in list(zip(hdr, r))[2:] if v)
    return f'<div class="card src" id="{r[0]}"><span class="n">{r[0]}</span><h3>{E(r[1]) if len(r) > 1 else ""}</h3><dl>{dl}</dl></div>'
srow = [r for r in rows[1:] if re.match(r"^S\d+$", r[0])]
trow = [r for r in rows[1:] if re.match(r"^T\d+$", r[0])]
G = '<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(340px,1fr));align-items:start">'
write("sources/index.html", page("Sources | " + SITE, f'<main><h2 class="sec">Sources</h2><p style="color:var(--mu);margin:-8px 0 24px">Every claim in the report cites one of these. Statements are paraphrased.</p>{G}{"".join(mk(r) for r in srow)}</div></main>', "sources"))

# evidence
ev = R / "evidence"; out = P / "evidence" / "files"; out.mkdir(parents=True, exist_ok=True)
def jtable(d):
    items = d.get("data") if isinstance(d, dict) else d
    if not (isinstance(items, list) and items and isinstance(items[0], dict)): return ""
    keys = [k for k in items[0] if all(not isinstance(it.get(k), (dict, list)) for it in items)][:7]
    if not keys: return ""
    th = "".join(f"<th>{E(k)}</th>" for k in keys)
    tr = "".join("<tr>" + "".join(f"<td>{E(str(it.get(k, '')))}</td>" for k in keys) + "</tr>" for it in items)
    return f'<p class="meta">{len(items)} entries</p><div class="tw"><table><tr>{th}</tr>{tr}</table></div>'
tcards = (f'<h2 class="sec">Own tests</h2>{G}' + "".join(mk(r) for r in trow) + '</div><h2 class="sec">Files</h2>') if trow else ''
blocks = ""
files = sorted(f for f in ev.rglob("*") if f.is_file() and "snapshots" not in f.parts) if ev.exists() else []
for f in files:
    rel = f.relative_to(ev); txt = f.read_text(errors="replace"); shutil.copy(f, out / f.name)
    note = f'<div class="meta">{rel} &middot; <a href="/evidence/files/{f.name}" target="_blank">raw file</a></div>'
    if f.suffix == ".json":
        try:
            d = json.loads(txt); pretty = json.dumps(d, indent=2)
            body = jtable(d) + f"<details><summary>Formatted JSON</summary><pre>{E(pretty)}</pre></details>"
        except Exception:
            body = f"<pre>{E(txt)}</pre>"
    elif f.suffix == ".md":
        body = f'<div class="md">{cite(MD(txt))}</div>'
    else:
        body = f"<pre>{E(txt)}</pre>"
    blocks += f'<section class="card ev" style="margin-bottom:16px"><h3>{E(f.stem.replace("-", " ").title())}</h3>{note}{body}</section>'

import hashlib
sn = ev / "snapshots"
if sn.exists():
    (out / "snapshots").mkdir(exist_ok=True)
    rws = ""
    for f in sorted(sn.glob("S*"), key=lambda x: int(re.sub(r"\D", "", x.stem) or 0)):
        pn = f.name + ".txt" if f.suffix == ".html" else f.name
        shutil.copy(f, out / "snapshots" / pn)
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        rws += f'<tr><td>{f.stem}</td><td><a href="/evidence/files/snapshots/{pn}" target="_blank">{f.name}</a></td><td>{f.stat().st_size // 1024 or 1} KB</td><td class="mono">{h[:16]}</td></tr>'
    if rws:
        blocks += f'<section class="card ev" style="margin-bottom:16px"><h3>Saved page copies</h3><div class="meta">One copy per source page. Hash shown is the start of the SHA-256.</div><div class="tw"><table><tr><th>Source</th><th>File</th><th>Size</th><th>SHA-256</th></tr>{rws}</table></div></section>'
write("evidence/index.html", page("Evidence | " + SITE, f'<main><h2 class="sec">Evidence</h2>{tcards}{blocks or "<p>No evidence files found.</p>"}</main>', "evidence"))

# community
cs_f = R / "COMMUNITY-SUMMARY.md"
if cs_f.exists():
    cs = cs_f.read_text()
    posts = re.findall(r"^(\d)/ (.+)$", cs, re.M)
    paras = [b.strip() for b in cs.split("\n\n") if b.strip() and not b.startswith("#") and not b.startswith("**X thread") and not re.match(r"\d/ ", b.strip())]
    plain = "\n\n".join(re.sub(r"\*\*|\[[ST]\d+\]", "", x).replace("In a few paragraphs. ", "") for x in paras)
    ptxt = "".join(f'<p>{cite(E(x.replace("**In a few paragraphs.** ", "")))}</p>' for x in paras)
    pc = "".join(f'<div class="card post"><span class="n">{n}/{len(posts)}</span><p>{cite(E(t))}</p><div class="pf"><span>{len(t)} / 280 characters</span><button class="cp" data-l="Copy post" data-t="{E(t)}">Copy post</button></div></div>' for n, t in posts)
    cbody = (f'<main><h2 class="sec">Community summary</h2><div class="card lead" style="max-width:820px">{ptxt}<button class="cp" data-l="Copy summary" data-t="{E(plain)}">Copy summary</button></div>'
             f'<h2 class="sec">X thread</h2><p style="color:var(--mu);margin:-8px 0 20px">Each post is under 280 characters.</p><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(340px,1fr));align-items:start">{pc}</div></main>')
    write("community/index.html", page("Community summary | " + SITE, cbody, "community"))
gl_f = R / "GLOSSARY.md"
if gl_f.exists():
    ents = re.findall(r"^- \*\*(.+?):\*\*\s*(.+)$", gl_f.read_text(), re.M)
    gc = "".join(f'<div class="card gl"><h3>{E(t)}</h3><p>{cite(E(d))}</p></div>' for t, d in ents)
    write("glossary/index.html", page("Plain words | " + SITE, f'<main><h2 class="sec">Plain words</h2><p style="color:var(--mu);margin:-8px 0 24px">Short meanings of the terms used in the report.</p><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(320px,1fr))">{gc}</div></main>', "glossary"))

# home
tot = {s: 0 for s in ST}
for c in chapters:
    c["cnt"] = counts(c["md"])
    for s in ST: tot[s] += c["cnt"][s]
stats = "".join(f'<div class="card stat blk-{s.lower()}"><b>{tot[s]}</b><span class="{s.lower()}"><i></i>{s}</span></div>' for s in ST)
def first(md):
    t = fb = ""
    for b in md.split("\n\n"):
        b = b.strip()
        if not b or b.startswith(("|", "-", "1.", "```")): continue
        t = re.sub(r"^\*\*(Confirmed|Tested|Analysis|Unknown)[^*]*\*\*\.?\s*", "", b)
        t = re.sub(r"\[[ST]\d+\]", "", t); t = re.sub(r"[*_`#>]", "", t)
        t = re.sub(r"\s+([.,;:])", r"\1", t).strip()
        if len(t) >= 60 and not b.endswith(":"): break
        fb = fb or t
    else:
        t = fb
    return E(t[:140] + ("..." if len(t) > 140 else ""))
def short_answers():
    m = re.search(r"^## Short answer\s*\n(.*?)(?=^## )", rep, re.M | re.S)
    rows = [r for r in (m[1].splitlines() if m else []) if r.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", r)][1:]
    out = ""
    for r in rows:
        q, a, lab = [c.strip() for c in r.strip().strip("|").split("|")]
        out += f'<div class="card ans"><h3>{E(q)}</h3><p>{cite(E(a))}</p><span class="lbl {lab.lower()}"><i></i>{E(lab)}</span></div>'
    return out
ans = short_answers()
ans = f'<h2 class="sec">The short answers</h2><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(320px,1fr))">{ans}</div>' if ans else ""
cc = "".join(f'<a class="card" href="/chapters/{c["slug"]}/"><span class="n">{c["n"]:02d}</span><h3>{E(c["title"])}</h3><p>{first(c["md"])}</p><div class="dots">' + "".join(f'<span class="{s.lower()}"><i></i>{c["cnt"][s]} {s}</span>' for s in ST if c["cnt"][s]) + "</div></a>" for c in chapters)
dg = "".join(f'<div class="card dg" style="padding:0;overflow:hidden;background:#141f26">{Path(d).read_text()}</div>' for d in sorted(glob.glob(str(P / "diagrams" / "*.svg")), key=lambda x: (["stack","routes","levels","selfserve","fusion","access","receptor","work","boundary","breaks"] + [Path(x).stem]).index(Path(x).stem)))
dg = f'<h2 class="sec">Diagrams</h2><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(340px,1fr));align-items:start">{dg}</div>' if dg else ""
lede = E(re.sub(r"[*_`#>]|\[[ST]\d+\]", "", intro.split("\n\n")[0])[:260]) if intro else ""
home = f'<section class="hero"><div><h1>{E(title)}</h1><p>{lede}</p><a class="btn p" href="/chapters/{chapters[0]["slug"]}/">Read the report</a><a class="btn" href="/sources/">Sources</a><a class="btn" href="/evidence/">Evidence</a></div></section><main>{ans}<h2 class="sec">Chapters</h2><div class="grid">{cc}</div>{dg}<h2 class="sec">Evidence status across the report</h2><div class="grid">{stats}</div></main>'
write("index.html", page(SITE, home, ""))
print(f"built {len(chapters)} chapters, {len(files)} evidence files")
