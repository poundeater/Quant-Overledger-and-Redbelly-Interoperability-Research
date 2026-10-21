#!/usr/bin/env python3
"""Renders public/brand/og.png (1200x630, the Discord and Open Graph size) in headless Chromium."""
import pathlib
from playwright.sync_api import sync_playwright
R = pathlib.Path(__file__).resolve().parent.parent
out = R / "public" / "brand"; out.mkdir(parents=True, exist_ok=True)
H = """<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<body style="margin:0;width:1200px;height:630px;background:#1d3140;color:#f1f5f8;font-family:'Be Vietnam Pro',sans-serif;padding:64px;box-sizing:border-box;position:relative">
<img src="https://taskboard.redbellydao.network/brand/dao-logo-on-dark.png" height="96">
<div style="font-size:64px;font-weight:700;letter-spacing:-.02em;line-height:1.1;margin-top:40px;max-width:900px">Could Redbelly connect to Quant's Overledger?</div>
<div style="font-size:24px;color:#c2ced6;margin-top:24px">Feasibility research. Sources linked, tests included.</div>
<div style="position:absolute;left:64px;bottom:48px;font:500 20px 'JetBrains Mono',monospace;color:#8fa1ad">Last verified 20 Oct 2026</div>
<div style="position:absolute;left:0;bottom:0;width:1200px;height:8px;background:#EF5350"></div></body>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.set_content(H, wait_until="networkidle"); pg.wait_for_timeout(1500)
    pg.screenshot(path=str(out / "og.png")); b.close()
print("wrote", out / "og.png")
