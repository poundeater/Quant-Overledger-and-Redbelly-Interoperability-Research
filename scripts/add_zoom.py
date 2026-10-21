#!/usr/bin/env python3
"""Adds click-to-zoom for diagrams to every built page. Run after build_site.py. Idempotent."""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "public"

CSS = """<style id="zmcss">
main figure img,main figure svg,main .dg svg,main img[src$=".svg"]{cursor:zoom-in}
#zm{position:fixed;inset:0;z-index:9999;background:rgba(5,9,12,.92);display:none;overflow:auto;-webkit-overflow-scrolling:touch}
#zm.on{display:block}
#zm .zc{min-height:100%;display:flex;align-items:center;justify-content:center;padding:56px 12px 24px}
#zm .zc>*{display:block;width:min(96vw,1400px);height:auto;background:#fff;border-radius:10px;cursor:zoom-in}
#zm.big .zc{justify-content:flex-start;align-items:flex-start}
#zm.big .zc>*{width:240vw;max-width:none;cursor:zoom-out}
#zm .zx{position:fixed;top:12px;right:14px;z-index:10000;background:#141f26;color:#e9eef1;border:1px solid #263641;border-radius:8px;padding:8px 16px;font-size:1rem;cursor:pointer}
#zm .zh{position:fixed;top:16px;left:16px;color:#93a4af;font-size:.85rem}
</style>"""

JS = """<script id="zmjs">(function(){
var o=document.createElement('div');o.id='zm';
o.innerHTML='<span class="zh">Click diagram to zoom. Esc to close.</span><button class="zx" type="button">Close</button><div class="zc"></div>';
document.body.appendChild(o);var c=o.querySelector('.zc');
function shut(){o.classList.remove('on','big');c.innerHTML='';document.body.style.overflow=''}
function open(el){var n;if(el.tagName.toLowerCase()==='img'){n=document.createElement('img');n.src=el.currentSrc||el.src;n.alt=el.alt||''}else{n=el.cloneNode(true);n.removeAttribute('width');n.removeAttribute('height')}
c.innerHTML='';c.appendChild(n);o.classList.add('on');o.classList.remove('big');document.body.style.overflow='hidden'}
document.addEventListener('click',function(e){
if(o.classList.contains('on')){
if(e.target.closest('.zx')||e.target===o||e.target===c){shut();return}
if(e.target.closest('.zc>*')){o.classList.toggle('big');return}
return}
var t=e.target.closest('main figure img,main figure svg,main .dg svg,main img[src$=".svg"]');
if(t&&!t.closest('a')){e.preventDefault();open(t)}});
document.addEventListener('keydown',function(e){if(e.key==='Escape')shut()})})();</script>"""

n = 0
for f in sorted(P.rglob("*.html")):
    if "/evidence/files/" in f.as_posix():
        continue  # saved source copies must stay verbatim
    h = f.read_text(encoding="utf-8")
    if 'id="zmjs"' in h or "</body>" not in h or "</head>" not in h:
        continue
    h = h.replace("</head>", CSS + "</head>", 1).replace("</body>", JS + "</body>", 1)
    f.write_text(h, encoding="utf-8")
    n += 1
assert n > 0 or any('id="zmjs"' in x.read_text(encoding="utf-8") for x in P.rglob("*.html")), "no pages patched"
print("zoom added to %d pages" % n)
