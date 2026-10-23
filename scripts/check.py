"""Quality gate. Run: python3 scripts/check.py  (must print RESULT: PASS)"""
import re, pathlib, zipfile, sys
R = pathlib.Path(__file__).resolve().parent.parent
txt = {n: (R / n).read_text(encoding="utf-8") for n in ["REPORT.md", "COMMUNITY-SUMMARY.md", "SOURCES.md"] + (["GLOSSARY.md"] if (R / "GLOSSARY.md").exists() else [])}
allt = "\n".join(txt.values()); errs = []
ids = set(re.findall(r"^\| ([ST]\d+) \|", txt["SOURCES.md"], re.M))
used = set(re.findall(r"\[([ST]\d+)\]", txt["REPORT.md"] + txt["COMMUNITY-SUMMARY.md"]))
if used - ids: errs.append(f"cited but not listed: {sorted(used-ids)}")
if ids - used: errs.append(f"listed but never cited: {sorted(ids-used)}")
for line in txt["REPORT.md"].splitlines():
    if line.startswith(("**Confirmed", "**Tested")) and not re.search(r"\[[ST]\d+\]", line): errs.append("uncited Confirmed: " + line[:60])
for pat in [r"partner(s|ed)? with Redbelly", r"in talks", r"will (integrate|partner)", r"collaborat", r"\bprice\b", r"invest(ment|or returns)", r"returns?\b", r"bullish", r"to the moon", "\u2014", "\u2013", r"[\U0001F300-\U0001FAFF]", r"@\w", r"made by", r"Claude", r"Anthropic"]:
    if re.search(pat, allt, re.I): errs.append(f"banned pattern: {pat}")
_dl = R / ".denylist"  # private patterns, one per line; this file is git-ignored on purpose
_pub = "\n".join(f.read_text(errors="ignore") for f in (R / "public").rglob("*.html")) if (R / "public").is_dir() else ""
for pat in ([l.strip() for l in _dl.read_text().splitlines() if l.strip()] if _dl.exists() else []):
    if re.search(re.escape(pat), allt + _pub, re.I): errs.append("private denylist pattern found in text or site")
if "no source reviewed shows a partnership" not in txt["REPORT.md"]: errs.append("missing no-partnership statement")
for p in re.findall(r"^\d/ (.+)$", txt["COMMUNITY-SUMMARY.md"], re.M):
    if len(p) > 280: errs.append(f"post over 280: {len(p)}")

# --- home answers and downloads (v21) ---
_home = (R / "public" / "index.html").read_text(errors="ignore") if (R / "public" / "index.html").exists() else ""
if _home.count('class="card ans"') != 4: errs.append("home page must show the 4 short answers")
for _ext in ("pdf", "docx"):
    _f = R / "public" / "downloads" / f"Quant-Overledger-Redbelly-Report.{_ext}"
    if not _f.exists(): errs.append(f"missing download: {_f.name}")
    elif f"/downloads/{_f.name}" not in _home: errs.append(f"home page does not link {_f.name}")
_hero = (re.search(r'<section class="hero">.*?</section>', _home, re.S) or [""])[0]
if "/downloads/Quant-Overledger-Redbelly-Report.pdf" not in _hero: errs.append("home hero has no PDF button")
_dx = R / "public" / "downloads" / "Quant-Overledger-Redbelly-Report.docx"
if _dx.exists():
    with zipfile.ZipFile(_dx) as z: _body = z.read("word/document.xml").decode(errors="ignore")
    if "\u2014" in _body or "\u2013" in _body: errs.append("dash in docx text")
    if "[ST]" in _body: errs.append("unexpected marker in docx")

import hashlib
ev = R / "evidence"; snaps = ev / "snapshots"
vcf = ev / "VERIFIED-CLAIMS.md"; vc = vcf.read_text() if vcf.exists() else ""
if snaps.is_dir():
    need = {"S1":"On-Chain Money","S2":"On-Chain Money","S3":"multi-DLT","S4":"Self-serve","S5":"Fusion","S6":"Receptor","S7":"Proof by Query","S8":"Eligibility Kit","S9":"useHasChainPermission","S10":"Tokeniser","S11":"cBridge","S12":"governors.mainnet.redbelly.network","S13":"Prague","S14":"access credential","S15":"networks","S17":"trusted-relayer"}
    for sid, phrase in need.items():
        f = snaps / (sid + ".html"); f = f if f.exists() else snaps / (sid + ".txt")
        if not f.exists():
            if sid in ("S2","S3","S4","S5","S15") and vc and re.search(r"^\| " + sid + r" \|", vc, re.M): continue
            errs.append(f"snapshot missing: {sid}"); continue
        if phrase.lower() not in f.read_text(errors="ignore").lower(): errs.append(f"snapshot {sid} lacks expected text '{phrase}' (blocked or wrong page?)")
    man = ev / "manifest.txt"
    if man.exists():
        listed = {name: h for h, name in re.findall(r"^([0-9a-f]{64})  (S\d+(?:\.ocr)?\.(?:html|txt|png|pdf))$", man.read_text(), re.M)}
        for name, h in listed.items():
            f = snaps / name
            if not f.exists(): errs.append(f"manifest lists a missing snapshot: {name}")
            elif hashlib.sha256(f.read_bytes()).hexdigest() != h: errs.append(f"hash mismatch: {name}")
        for f in sorted(snaps.iterdir()):
            if f.is_file() and f.name not in listed: errs.append(f"snapshot has no hash in manifest: {f.name}")
else: print("snapshots: not present, skipped")

# exact-quote check: every line of evidence/quotes.tsv must appear word for word in its snapshot
import sys as _s; _s.path.insert(0, str(R / "scripts"))
from _norm import load as _load, norm as _norm
qf = ev / "quotes.tsv"
if qf.exists():
    nq = 0
    for ln in qf.read_text(encoding="utf-8").splitlines():
        if "\t" not in ln: continue
        sid, q = ln.split("\t", 1); nq += 1
        body = _load(sid, str(snaps))
        if body is None: errs.append(f"quote source has no snapshot: {sid}")
        elif _norm(q).lower() not in body.lower(): errs.append(f"quote not found in {sid}: {q[:50]}")
    print(f"quotes checked: {nq}")
# online link check is optional: python3 scripts/check.py --online
if "--online" in _s.argv:   # add --save to also write evidence/link-check.txt
    import urllib.request, urllib.error, datetime
    _links = ["Checked (UTC): " + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")]
    for sid, url in re.findall(r"^\| (S\d+) \|.*?\| (https?://\S+) \|", txt["SOURCES.md"], re.M):
        try: code = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).status
        except urllib.error.HTTPError as e: code = e.code
        except Exception as e: code = "error " + str(e)[:50]
        _links.append(f"{sid} {code} {url}")
        if code != 200: print(f"link warn {sid}: {code}")
    print("\n".join(_links))
    if "--save" in _s.argv: (ev / "link-check.txt").write_text("\n".join(_links) + "\n", encoding="utf-8")
# --- hygiene checks (v19) ---
import subprocess, shutil, json
if shutil.which("git") and (R / ".git").exists():
    _em = subprocess.run(["git", "-C", str(R), "log", "--format=%ae%n%ce"], capture_output=True, text=True).stdout.split()
    _bad = sorted({e for e in _em if not e.endswith("@users.noreply.github.com") and e != "noreply@github.com"})
    if _bad: errs.append("non-noreply author or committer emails in history: " + ", ".join(_bad))
else: print("git history: not available, email check skipped")
_pdf = R / "public/downloads/Quant-Overledger-Redbelly-Report.pdf"
_pats = [l.strip() for l in _dl.read_text().splitlines() if l.strip()] if _dl.exists() else []
if _pdf.exists() and not shutil.which("pdfinfo"): errs.append("pdfinfo not found, install poppler-utils")
elif _pdf.exists():
    _meta = subprocess.run(["pdfinfo", str(_pdf)], capture_output=True, text=True).stdout
    print("PDF metadata:", " | ".join(l for l in _meta.splitlines() if l.split(":")[0] in ("Title", "Author", "Creator", "Producer")))
    for _pat in _pats:
        if _pat.lower() in _meta.lower(): errs.append("denylist pattern in PDF metadata")
if _pats:
    _ev = " ".join(f.read_text(errors="ignore") for f in (R / "evidence").rglob("*") if f.is_file() and f.suffix in (".html", ".txt", ".md", ".json", ".tsv"))
    for _pat in _pats:
        if _pat.lower() in _ev.lower(): errs.append("denylist pattern in evidence files")
# --- evidence coverage, key-like strings, filler words (v20) ---
_man = (ev / "manifest.txt").read_text(errors="ignore") if (ev / "manifest.txt").exists() else ""
_td = ev / "tests"
if _td.is_dir():
    _listed = {n: h for h, n in re.findall(r"^([0-9a-f]{64})  tests/([\w.-]+)$", _man, re.M)}
    for f in sorted(p for p in _td.iterdir() if p.is_file()):
        if f.name not in _listed: errs.append(f"test log not in manifest: {f.name}")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != _listed[f.name]: errs.append(f"hash mismatch: tests/{f.name}")
    for n in _listed:
        if not (_td / n).exists(): errs.append(f"manifest lists a missing test log: {n}")
    for tid, cell in re.findall(r"^\| (T\d+) \|[^|]*\| ([^|]*) \|", txt["SOURCES.md"], re.M):
        for n in re.findall(r"[\w.-]+\.(?:txt|json)", cell):
            if not (_td / n).exists(): errs.append(f"{tid} names a missing file: {n}")
if snaps.is_dir():
    for sid in sorted((i for i in ids if i[0] == "S"), key=lambda s: int(s[1:])):
        if not any((snaps / f"{sid}.{e}").exists() for e in ("html", "txt", "pdf", "png")): errs.append(f"no saved copy for {sid}")
        elif not re.search(r"^[0-9a-f]{64}  " + sid + r"\.(?:html|txt|pdf|png)$", _man, re.M): errs.append(f"{sid} has no hash in manifest")
_sec = re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|(?i:x-api-key|authorization|bearer)[\"': =]+[A-Za-z0-9._-]{24,}")
for _d in (ev, R / "public"):
    for f in (_d.rglob("*") if _d.is_dir() else []):
        if f.is_file() and f.suffix in (".html", ".txt", ".md", ".json", ".tsv", ".js", ".css") and _sec.search(f.read_text(errors="ignore")): errs.append(f"key-like string in {f.relative_to(R)}")
for n, t in txt.items():
    if _sec.search(t): errs.append(f"key-like string in {n}")
for pat in [r"\bseamless", r"game[- ]chang", r"revolution", r"cutting[- ]edge", r"supercharg"]:
    if re.search(pat, allt, re.I): errs.append(f"filler word: {pat}")
# site-wide: meta tags, zoom, brand rules, docx metadata
import struct, zipfile as _zf
_pub = R / "public"
_need = ['rel="icon"', 'name="description"', 'name="theme-color"', 'property="og:title"', 'property="og:description"', 'property="og:image"', 'property="og:image:alt"', 'property="og:image:width"', 'property="og:image:height"', 'name="twitter:card"']
for f in sorted(_pub.rglob("*.html")):
    if "/evidence/files/" in f.as_posix(): continue
    h = f.read_text(errors="ignore"); rel = f.relative_to(R)
    for t in _need:
        if t not in h: errs.append(f"{rel}: missing meta {t}")
    if 'id="zmjs"' not in h: errs.append(f"{rel}: click-to-zoom script missing")
    if not rel.as_posix().startswith("public/evidence/") and re.search(r"[\u2013\u2014]", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S)): errs.append(f"{rel}: dash character in page text")
    if not rel.as_posix().startswith("public/evidence/") and re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", h): errs.append(f"{rel}: emoji")
_og = _pub / "brand" / "og.png"
if _og.exists():
    _w, _h = struct.unpack(">II", _og.read_bytes()[16:24])
    if (_w, _h) != (1200, 630): errs.append(f"og.png is {_w}x{_h}, want 1200x630")
else: errs.append("brand/og.png missing")
for _d in (_pub / "downloads").glob("*.docx"):
    with _zf.ZipFile(_d) as z:
        core = z.read("docProps/core.xml").decode("utf8", "ignore") if "docProps/core.xml" in z.namelist() else ""
    for tag in ("dc:creator", "cp:lastModifiedBy"):
        m = re.search(rf"<{tag}>([^<]+)</{tag}>", core)
        if m and m.group(1).strip().lower() not in ("anonymous", "(anonymous)"): errs.append(f"{_d.name}: {tag} is set ({m.group(1)})")
_css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", (_pub / "index.html").read_text(), re.S))
if re.search(r"box-shadow:\s*[^n;}]", _css): errs.append("drop shadow in CSS (brand: none)")
if re.search(r"border-radius:\s*(9999|99)px|border-radius:50%\s*;[^}]*\.btn", _css): errs.append("pill button radius")
try: _vj = json.loads((R / "vercel.json").read_text())
except Exception: _vj = None; errs.append("vercel.json missing or not valid JSON")
if _vj is not None:
    if _vj.get("outputDirectory") != "public": errs.append("vercel.json must serve public/")
    if "nosniff" not in json.dumps(_vj.get("headers", [])): errs.append("vercel.json lost its security headers")
import check_deep; check_deep.run(R, txt, errs)
print("\n".join(errs) or "no issues"); print("RESULT:", "FAIL" if errs else "PASS"); sys.exit(1 if errs else 0)
