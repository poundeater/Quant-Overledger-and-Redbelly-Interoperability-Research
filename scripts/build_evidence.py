#!/usr/bin/env python3
"""Rebuilds the <main> of public/evidence/index.html. Run after build_site.py."""
import re, html, subprocess
from pathlib import Path

R = Path(__file__).resolve().parent.parent
PAGE = R / "public" / "evidence" / "index.html"
E = lambda s: html.escape(s, quote=True)

def norm(t):
    t = html.unescape(t)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " ")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()

rows = {}
for l in (R / "SOURCES.md").read_text(encoding="utf-8").split("\n"):
    m = re.match(r"^\| ([ST]\d+) \| (.*?) \| (.*?) \| (.*) \|\s*$", l)
    if m:
        rows[m.group(1)] = m.groups()[1:]
srcs = {k: v for k, v in rows.items() if k[0] == "S"}
tests = {k: v for k, v in rows.items() if k[0] == "T"}
assert srcs and tests, "no rows parsed from SOURCES.md"

quotes = {}
for l in (R / "evidence" / "quotes.tsv").read_text(encoding="utf-8").split("\n"):
    if "\t" in l:
        sid, q = l.split("\t", 1)
        quotes.setdefault(sid.strip(), []).append(q.strip())

def snap(sid):
    d = R / "evidence" / "snapshots"
    for name in (sid + ".ocr.txt", sid + ".txt", sid + ".html", sid + ".pdf"):
        f = d / name
        if not f.exists():
            continue
        if name.endswith(".pdf"):
            try:
                return name, norm(subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True).stdout)
            except Exception:
                return name, ""
        raw = f.read_text(encoding="utf-8", errors="ignore")
        if name.endswith(".html"):
            raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
            raw = re.sub(r"<[^>]+>", " ", raw)
        return name, norm(raw)
    return None, ""

def excerpt(text, q):
    n = norm(q)
    i = text.lower().find(n.lower())
    if i < 0:
        return None
    a, b = max(0, i - 170), min(len(text), i + len(n) + 170)
    return ("&hellip;" if a else "") + E(text[a:i]) + "<mark>" + E(text[i:i + len(n)]) + "</mark>" + E(text[i + len(n):b]) + ("&hellip;" if b < len(text) else "")

def group(url):
    if re.search(r"redbelly\.network|tokeniser\.com", url or ""): return "Redbelly"
    if "overledger.dev" in (url or ""): return "Overledger"
    return "Other"

missing = []

def src_card(sid, v):
    title, url_cell, supports = v
    m = re.search(r"https?://[^\s|]+", url_cell)
    url = m.group(0) if m else ""
    name, text = snap(sid)
    chips, exs = "", []
    allq = quotes.get(sid, [])
    qs, more = allq[:3], allq[3:]
    for q in more:
        if text and excerpt(text, q) is None:
            missing.append((sid, " ".join(norm(q).split()[:8])))
    for q in qs:
        n = norm(q)
        phrase = " ".join(n.split()[:8])
        chips += '<div class="ph"><code>%s</code><button class="cp2" data-p="%s">Copy</button></div>' % (E(phrase), E(phrase))
        if len(n.split()) > 8:
            chips += '<div class="fq">Full line: &ldquo;%s&rdquo;</div>' % E(n)
        ex = excerpt(text, q) if text else None
        if text and ex is None:
            missing.append((sid, phrase))
        if ex:
            exs.append('<p class="ex">%s</p>' % ex)
    if more:
        chips += '<details><summary>%d more exact phrases from this page</summary>%s</details>' % (
            len(more), "".join('<div class="fq">&ldquo;%s&rdquo;</div>' % E(norm(q)) for q in more))
    if not qs:
        chips = '<div class="fq">No exact phrase listed for this source; the claim rests on the page as a whole.</div>'
    arch = ""
    if name:
        arch = '<details><summary>Saved copy: matching passage</summary>%s%s<a class="rawl" href="/evidence/files/snapshots/%s" target="_blank" rel="noopener">Raw copy (%s)</a></details>' % ("".join(exs) or '<p class="ex">No passage matched in the saved text.</p>', ('<a class="rawl" href="/evidence/source/%s/">Reader view</a> ' % E(name.split(".")[0])) if name.endswith(".html") else "", E(name + ".txt" if name.endswith(".html") else name), E(name))
    btn = '<a class="btn p sm" href="%s" target="_blank" rel="noopener">Open source</a>' % E(url) if url else ""
    g = group(url)
    return ('<article class="sc" id="%s" data-g="%s" data-s="%s"><div class="sh"><span class="sid">%s</span><h4>%s</h4>%s</div>'
            '<div class="sp">Page supports: %s</div>%s%s</article>') % (
        sid, g, E((sid + " " + title + " " + supports + " " + " ".join(allq)).lower()), sid, E(title), btn, E(supports), chips, arch)

def test_card(tid, v):
    title, files_cell, result = v
    desc, _, date = title.replace("Own test: ", "").rpartition(", ")
    links, prev = "", ""
    for fn in re.findall(r"[\w.-]+\.(?:txt|json)", files_cell):
        links += '<a class="rawl" href="/evidence/files/%s" target="_blank">%s</a> ' % (E(fn), E(fn))
        f = R / "evidence" / "tests" / fn
        if fn.endswith(".txt") and f.exists():
            t = f.read_text(encoding="utf-8", errors="ignore")
            prev += '<details><summary>Raw output: %s</summary><pre>%s</pre></details>' % (E(fn), E(t[:4000] + ("\n[cut]" if len(t) > 4000 else "")))
    return '<article class="tc" id="%s"><div class="sh"><span class="sid t">%s</span><h4>%s</h4><span class="dt">%s</span></div><div class="sp">Result: %s</div><div>%s</div>%s</article>' % (
        tid, tid, E(desc or title), E(date), E(result), links, prev)

manifest = (R / "evidence" / "manifest.txt").read_text(encoding="utf-8", errors="ignore")
snaps = sorted((R / "evidence" / "snapshots").glob("*"), key=lambda f: (len(f.stem), f.name))
snaplist = " ".join('<a class="rawl" href="/evidence/files/snapshots/%s" target="_blank" rel="noopener">%s</a>' % (E(f.name + '.txt' if f.suffix == '.html' else f.name), E(f.name)) for f in snaps)

CSS = """<style id="evx">
.ev h3{margin:34px 0 10px;font-size:1.25rem}.evlede{color:var(--mu);max-width:70ch;line-height:1.6}
.evnav{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}.evnav a{padding:6px 14px;border:1px solid var(--bd);border-radius:20px;color:var(--tx);text-decoration:none;font-size:.9rem}
.tc,.sc{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px;margin:12px 0}
.sh{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.sh h4{margin:0;flex:1;min-width:200px;font-size:1rem}
.sid{background:var(--tint);color:var(--red);font-weight:700;border-radius:6px;padding:3px 9px;font-size:.85rem}.sid.t{color:var(--te)}
.dt{color:var(--mu);font-size:.85rem}.sp{color:var(--mu);font-size:.9rem;margin:8px 0}
.ph{display:flex;align-items:center;gap:10px;margin:6px 0;flex-wrap:wrap}.ph code{background:var(--bg);border:1px solid var(--bd);border-radius:6px;padding:5px 10px;font-size:.9rem}
.cp2,.fb{background:transparent;color:var(--tx);border:1px solid var(--bd);border-radius:6px;padding:4px 12px;cursor:pointer;font-size:.85rem}
.fb:hover{background:var(--hov);border-color:var(--hovb)}.fb.on,.fb.on:hover{background:var(--act);border-color:var(--ab)}.btn.sm{padding:6px 14px;font-size:.85rem}
.fq{color:var(--mu);font-size:.82rem;margin:2px 0 6px}.evtools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:10px 0}
#evq{flex:1;min-width:220px;background:var(--card);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:9px 12px}
.ev details{margin-top:10px}.ev summary{cursor:pointer;color:var(--mu);font-size:.9rem}.ev pre{white-space:pre-wrap;word-break:break-word;background:var(--bg);border:1px solid var(--bd);border-radius:8px;padding:12px;font-size:.8rem;max-height:340px;overflow:auto}
.ex{background:var(--bg);border-left:3px solid var(--red);padding:8px 12px;font-size:.85rem;line-height:1.55}.ex mark{background:var(--tint);color:var(--tx);padding:0 2px}
.rawl{display:inline-block;margin:4px 10px 0 0;font-size:.82rem;color:var(--te)}
</style>"""

JS = """<script>(function(){var q=document.getElementById('evq'),bs=document.querySelectorAll('.fb'),cs=document.querySelectorAll('.sc'),g='all';
function run(){var t=q.value.toLowerCase();cs.forEach(function(c){var ok=(g==='all'||c.dataset.g===g)&&c.dataset.s.indexOf(t)>-1;c.style.display=ok?'':'none'})}
q.addEventListener('input',run);bs.forEach(function(b){b.addEventListener('click',function(){g=b.dataset.g;bs.forEach(function(x){x.classList.toggle('on',x===b)});run()})});
document.addEventListener('click',function(e){var b=e.target.closest('.cp2');if(!b)return;var p=b.dataset.p;var d=function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1200)};
if(navigator.clipboard){navigator.clipboard.writeText(p).then(d,d)}else{d()}})})();</script>"""

main = ('<main class="ev"><h2 class="sec">Evidence</h2>'
        '<p class="evlede">Every source below has a link and the exact words to look for. Open the source, press Ctrl+F, paste the phrase. '
        'If a phrase has an apostrophe and does not match, search its first four words. Pages can change after our visit, so a saved copy is kept under each card.</p>'
        '<nav class="evnav"><a href="#tests">Our own tests</a><a href="#verify">Verify each source</a><a href="#archive">Archive</a></nav>'
        '<h3 id="tests">Our own tests</h3>' + "".join(test_card(k, v) for k, v in sorted(tests.items())) +
        '<h3 id="verify">Verify each source yourself</h3>'
        '<div class="evtools"><input id="evq" placeholder="Search sources or phrases">'
        '<button class="fb on" data-g="all">All</button><button class="fb" data-g="Redbelly">Redbelly</button>'
        '<button class="fb" data-g="Overledger">Overledger</button><button class="fb" data-g="Other">Other</button></div>' +
        "".join(src_card(k, v) for k, v in sorted(srcs.items(), key=lambda kv: int(kv[0][1:]))) +
        '<h3 id="archive">Archive</h3><details><summary>Manifest (when and where each page was saved)</summary><pre>' + E(manifest) + '</pre></details>'
        '<details><summary>All saved page files and raw lists</summary><p>' + snaplist +
        ' <a class="rawl" href="/evidence/files/quotes.tsv" target="_blank">quotes.tsv</a> <a class="rawl" href="/evidence/files/manifest.txt" target="_blank">manifest.txt</a></p></details>'
        + JS + '</main>')

h = PAGE.read_text(encoding="utf-8")
h = re.sub(r'<style id="evx">.*?</style>', "", h, flags=re.S)
m = re.search(r"<main\b[^>]*>.*?</main>", h, re.S)
assert m and len(re.findall(r"<main\b", h)) == 1, "main block not found"
h = h[:m.start()] + main + h[m.end():]
assert h.count("</head>") == 1
h = h.replace("</head>", CSS + "</head>")
PAGE.write_text(h, encoding="utf-8")
print("evidence page rebuilt: %d tests, %d sources" % (len(tests), len(srcs)))
print("phrases not found in saved text (want none):", missing)
