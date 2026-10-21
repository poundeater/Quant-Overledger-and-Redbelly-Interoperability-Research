"""Deep checks: labels, PDF and Word text vs report, SVG rules, internal links, home counts."""
import re, subprocess, zipfile, html, pathlib

LABELS = ("Confirmed", "Tested", "Analysis", "Unknown")
ALLOWED = {"#141f26", "#263641", "#f1f5f8", "#0c1317", "#8fa1ad", "#86efac", "#fcd34d", "#ffb3ae", "#ef5350", "#1d3140", "#c2ced6", "#223039", "#34444f", "none", "#17222a"}

def clean(t):
    t = re.sub(r"\[[ST]\d+\]", "", t)
    t = re.sub(r"[*_`]", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = html.unescape(t)
    t = t.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()

def paragraphs(rep):
    """(chapter heading, paragraph) for every body paragraph under a numbered chapter."""
    out, ch = [], None
    for blk in re.split(r"\n\s*\n", rep):
        b = blk.strip()
        if b.startswith("## "):
            ch = b[3:]; continue
        if not ch or not re.match(r"\d+\.", ch): continue
        if b.startswith(("|", "-", "*   ", "#", ">", "```")) or not b or re.match(r"\d+\. ", b) or ch.startswith("11."): continue
        out.append((ch, b))
    return out

def run(R, txt, errs):
    rep = txt["REPORT.md"]; pub = R / "public"
    paras = paragraphs(rep)
    # 1. every chapter paragraph starts with a label
    for ch, p in paras:
        if not re.match(r"\*\*(" + "|".join(LABELS) + r")[.:]?", p) and not re.search(r"\*\*[^*]*\b(" + "|".join(LABELS) + r")\b[^*]*\*\*", p):
            errs.append(f"paragraph without label in '{ch[:30]}': {p[:50]}")
    # 2. PDF and Word contain every chapter heading and the opening words of every paragraph
    pdf = pub / "downloads/Quant-Overledger-Redbelly-Report.pdf"
    dx = pub / "downloads/Quant-Overledger-Redbelly-Report.docx"
    pdf_t = clean(subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout) if pdf.exists() else ""
    dx_t = ""
    if dx.exists():
        import docx
        d = docx.Document(str(dx))
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                parts += [c.text for c in row.cells]
        dx_t = clean("\n".join(parts))
    heads = [h[3:] for h in re.findall(r"^## .+$", rep, re.M)]
    for name, body in (("PDF", pdf_t), ("Word", dx_t)):
        if not body: errs.append(f"{name} text could not be read"); continue
        for h in heads:
            if clean(h) not in body: errs.append(f"{name} lacks heading: {h[:40]}")
        miss = 0
        for ch, p in paras:
            words = clean(re.sub(r"^\*\*(?:Confirmed|Tested|Analysis|Unknown)[.:]?\*\*", "", p)).split()
            probe = " ".join(words[:8]); tail = " ".join(words[-6:])
            if len(words) >= 8 and (probe not in body or tail not in body): miss += 1; errs.append(f"{name} text differs from report near: {probe}")
        for h, _ in [(x, 0) for x in LABELS]: pass
    # 3. SVG rules
    for f in sorted((pub / "diagrams").glob("*.svg")):
        s = f.read_text(); n = f.name
        if "viewBox" not in s: errs.append(f"{n}: no viewBox")
        if 'role="img"' not in s or "<title>" not in s: errs.append(f"{n}: no role=img and title")
        if re.search(r"<script|foreignObject|<image|href=|@import|url\(http", s, re.I): errs.append(f"{n}: forbidden element or external reference")
        if not re.search(r"Last verified \d{1,2}(?:-\d{1,2})? \w+ 2026", s): errs.append(f"{n}: no dated 'Last verified' line")
        for c in set(re.findall(r'(?:fill|stroke)="([^"]+)"', s)):
            if c.lower() not in ALLOWED: errs.append(f"{n}: colour outside brand kit: {c}")
        for fam in set(re.findall(r'font-family="([^"]+)"', s)):
            if "Be Vietnam Pro" not in fam and "JetBrains Mono" not in fam: errs.append(f"{n}: font outside brand kit: {fam[:30]}")
        vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', s)
        if vb:
            W, H = int(vb.group(1)), int(vb.group(2))
            for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"([^>]*)>([^<]*)<', s):
                x, y, attrs, t = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4)
                size = float((re.search(r'font-size="([\d.]+)"', attrs) or [0, 13])[1]); w = len(t) * size * 0.58
                anchor = re.search(r'text-anchor="(\w+)"', attrs); a = anchor.group(1) if anchor else "start"
                lo, hi = (x - w / 2, x + w / 2) if a == "middle" else ((x - w, x) if a == "end" else (x, x + w))
                if lo < 0 or hi > W + 1 or y > H: errs.append(f"{n}: text may overflow the canvas: {t[:30]}")
        for sid in re.findall(r"\b([ST]\d+)\b", re.sub(r"<[^>]+>", " ", s)):
            if not re.search(rf"^\| {sid} \|", txt["SOURCES.md"], re.M): errs.append(f"{n}: cites unknown source {sid}")
    # 4. site: internal links resolve, images have alt, no plain http
    for f in sorted(pub.rglob("*.html")):
        if "/evidence/files/" in f.as_posix(): continue
        h = f.read_text(errors="ignore"); rel = f.relative_to(R)
        for href in set(re.findall(r'(?:href|src)="(/[^"#?]*)', h)):
            t = pub / href.lstrip("/")
            if not (t.is_file() or (t / "index.html").is_file()): errs.append(f"{rel}: broken internal link {href}")
        for img in re.findall(r"<img\b[^>]*>", h):
            if "alt=" not in img: errs.append(f"{rel}: image without alt")
        if re.search(r'(?:href|src)="http://', h): errs.append(f"{rel}: plain http link")
    # 5. home counts match the real numbers
    home = (pub / "index.html").read_text(errors="ignore")
    src_n = len(re.findall(r"^\| S\d+ \|", txt["SOURCES.md"], re.M)); t_n = len(re.findall(r"^\| T\d+ \|", txt["SOURCES.md"], re.M))
    for label, n in (("sources", src_n), ("tests", t_n)):
        m = re.search(rf"(\d+)\s*(?:<[^>]+>\s*)*{label}", home, re.I)
        if m and int(m.group(1)) != n: errs.append(f"home page says {m.group(1)} {label}, SOURCES.md has {n}")
    # 7. reader views: one per saved html source, hash shown, every report quote present, text is word for word from the raw copy
    sys_path = str(R / "scripts")
    import sys as _sy
    if sys_path not in _sy.path: _sy.path.insert(0, sys_path)
    from _norm import norm as _n
    qmap = {}
    for ln in (R / "evidence/quotes.tsv").read_text(encoding="utf-8").splitlines():
        if "\t" in ln: a, b = ln.split("\t", 1); qmap.setdefault(a, []).append(b)
    manifest = (R / "evidence/manifest.txt").read_text(errors="ignore")
    for raw in sorted((R / "evidence/snapshots").glob("S*.html")):
        sid = raw.stem; rv = pub / "evidence/source" / sid / "index.html"
        if not rv.exists(): errs.append(f"{sid}: no reader view"); continue
        h = rv.read_text(errors="ignore"); body = _n(re.search(r'<div class="rd">(.*)</div><p style', h, re.S).group(1)).lower()
        m = re.search(rf"^([0-9a-f]{{64}})  {sid}\.html$", manifest, re.M)
        if m and m.group(1) not in h: errs.append(f"{sid}: reader view does not show the raw SHA-256")
        if f"/evidence/files/snapshots/{sid}.html.txt" not in h: errs.append(f"{sid}: reader view has no link to the raw copy")
        for q in qmap.get(sid, []):
            if _n(q).lower() not in body: errs.append(f"{sid}: quote missing from reader view: {q[:40]}")
        rawn = _n(raw.read_text(errors="ignore")).lower()
        for ptxt in re.findall(r"<(?:p|h3)>(.*?)</(?:p|h3)>", re.search(r'<div class="rd">(.*)</div><p style', h, re.S).group(1), re.S):
            t = _n(re.sub(r"</?mark>", "", ptxt)).lower()
            if t and t not in rawn: errs.append(f"{sid}: reader text not found in raw copy: {t[:40]}"); break
    # 8. raw copies are published as .txt (never as pages) and are byte for byte the saved files
    _sn = pub / "evidence/files/snapshots"
    if _sn.is_dir():
        for f in _sn.iterdir():
            if f.suffix == ".html": errs.append(f"raw copy published as a page: {f.name}")
        for raw in (R / "evidence/snapshots").glob("S*.html"):
            c = _sn / (raw.name + ".txt")
            if not c.exists(): errs.append(f"missing published raw copy: {raw.name}.txt")
            elif c.read_bytes() != raw.read_bytes(): errs.append(f"published raw copy differs from saved file: {raw.name}")
    # 9. inline scripts must parse (a missing semicolon once killed the theme button)
    import shutil, tempfile, os
    if shutil.which("node"):
        for f in sorted(pub.rglob("*.html")):
            if "/evidence/files/" in f.as_posix(): continue
            for i, sc in enumerate(re.findall(r"<script(?![^>]*src=)[^>]*>(.*?)</script>", f.read_text(errors="ignore"), re.S)):
                with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf: tf.write(sc); name = tf.name
                r = subprocess.run(["node", "--check", name], capture_output=True, text=True); os.unlink(name)
                if r.returncode: errs.append(f"{f.relative_to(R)}: inline script {i} has a syntax error"); break
    else: print("node not found, script syntax check skipped")
    # 6. done
    print(f"deep checks: {len(paras)} paragraphs, {len(list((pub/'diagrams').glob('*.svg')))} diagrams, {len(heads)} headings")
