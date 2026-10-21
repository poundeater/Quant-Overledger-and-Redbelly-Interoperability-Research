import re, html, pathlib, subprocess
def norm(t):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t); t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(t)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2011", "-")): t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()
def load(sid, d="evidence/snapshots"):
    d = pathlib.Path(d)
    for e in ("html", "txt"):
        f = d / f"{sid}.{e}"
        if f.exists(): return norm(f.read_text(errors="ignore"))
    f = d / f"{sid}.pdf"
    if f.exists(): return norm(subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True).stdout)
    f = d / f"{sid}.ocr.txt"   # OCR of a screenshot, used when the source is an image
    if f.exists(): return norm(f.read_text(errors="ignore"))
