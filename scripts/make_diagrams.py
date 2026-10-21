#!/usr/bin/env python3
"""Writes the two newer diagrams (selfserve, access) into public/diagrams/ in the Task Board brand style."""
from pathlib import Path
R = Path(__file__).resolve().parent.parent
F = 'font-family="Be Vietnam Pro,system-ui,sans-serif"'
M = 'font-family="JetBrains Mono,ui-monospace,monospace"'
OK, WARN, MUTE, RED = "#86EFAC", "#FCD34D", "#8fa1ad", "#EF5350"

def svg(h, title, body, src, date="20 Oct 2026"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 {h}" role="img"><title>{title}</title>'
            f'<rect width="720" height="{h}" rx="8" fill="#141f26" stroke="#263641"/>'
            f'<text x="24" y="38" {F} font-size="17" font-weight="600" fill="#f1f5f8">{title}</text>{body}'
            f'<text x="24" y="{h-18}" {M} font-size="12" fill="#8fa1ad">Last verified {date}. Sources {src}.</text></svg>')

def box(x, y, w, h, lines, stroke="#263641"):
    t = "".join(f'<text x="{x+w/2}" y="{y+h/2+(i-(len(lines)-1)/2)*17+5}" text-anchor="middle" {F} font-size="13" fill="#f1f5f8">{l}</text>' for i, l in enumerate(lines))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#0c1317" stroke="{stroke}"/>{t}'

def row(steps, y, w, gap, x0=24):
    out = ""
    for i, s in enumerate(steps):
        x = x0 + i * (w + gap); out += box(x, y, w, 52, s)
        if i: out += f'<path d="M{x-gap+2} {y+26}H{x-2}" stroke="#8fa1ad"/>'
    return out

def status(items, y, w, gap, x0=24):
    out = ""
    for i, (t, c) in enumerate(items):
        x = x0 + i * (w + gap)
        out += f'<circle cx="{x+8}" cy="{y}" r="5" fill="{c}"/><text x="{x+20}" y="{y+4}" {M} font-size="11" fill="#c2ced6">{t}</text>'
    return out

selfserve = svg(250, "Gateway self-serve: the path for a new chain",
    f'<text x="24" y="74" {F} font-size="13" fill="#8fa1ad">What Overledger asks for</text>' + row([["Three tests", "pass"], ["POST /nodes", "register"], ["Public or", "private node"], ["Health check", "at registration"], ["Gateway API", "access"]], 84, 116, 20)
    + f'<text x="24" y="170" {F} font-size="13" fill="#8fa1ad">Redbelly today</text>'
    + status([("Partly known", WARN), ("Refused, T3", RED), ("Ankr approved", OK), ("Unknown", MUTE), ("Not in live list", RED)], 194, 116, 20), "S4, S12, S22, T2, T3")

access = svg(210, "How write access works on Redbelly",
    row([["Accredited", "issuer"], ["User claims", "access credential"], ["Account enabled", "by a contract"], ["Can write to", "the network"]], 70, 148, 26)
    + f'<text x="24" y="156" {F} font-size="13" fill="#c2ced6">Whether read-only RPC access needs a credential is Unknown.</text>', "S6, S14")

D = "21 Oct 2026"
def line(x1, y1, x2, y2): return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#8fa1ad"/>'
def note(x, y, t, c="#c2ced6"): return f'<text x="{x}" y="{y}" {F} font-size="13" fill="{c}">{t}</text>'
def cols3(items, y, h=64, w=212, gap=18):
    return "".join(box(24 + i * (w + gap), y, w, h, it) for i, it in enumerate(items))

stack = svg(366, "Overledger in one picture",
    box(24, 60, 672, 40, ["Your application"])
    + line(188, 100, 188, 128) + line(532, 100, 532, 128)
    + box(24, 128, 328, 64, ["Gateway", "One entry to many networks"]) + box(368, 128, 328, 64, ["Fusion Rollup", "Shared layer on the OP Stack"])
    + line(188, 192, 188, 220) + line(532, 192, 532, 220)
    + box(24, 220, 328, 52, ["Connectors", "Self-serve or managed engagement"]) + box(368, 220, 328, 52, ["Bridge and dispute contracts", "One set on each connected chain"])
    + box(24, 282, 672, 34, ["Firewall: a Gateway layer and an on-chain layer"], stroke="#EF5350"),
    "S3, S4, S5, S24", D)

levels = svg(270, "Three meanings of connect, three answers",
    cols3([["Read and send", "through the Gateway"], ["Move value and messages", "through Fusion"], ["A bridge outside", "Overledger"]], 60, 76)
    + "".join(f'<circle cx="{32 + i * 230}" cy="168" r="5" fill="{c}"/><text x="{44 + i * 230}" y="172" {M} font-size="11" fill="#c2ced6">{t}</text><text x="{44 + i * 230}" y="194" {M} font-size="11" fill="#8fa1ad">{u}</text>'
              for i, (c, t, u) in enumerate([(RED, "Refused, Tested", "Not in live list, T2 T3 T5"), (MUTE, "Not listed, Analysis", "No Redbelly in the list, T2"), (OK, "Live, Confirmed", "Not an Overledger route")]))
    + note(24, 232, "Only the third answer is live today, and it does not run through Quant.", "#8fa1ad"),
    "S4, S5, S11, S29, S30, S34, T2, T3, T5", D)

work = svg(300, "The work, step by step (Analysis)",
    cols3([["1. Confirm the basics", "Access rules, network name"], ["2. Decide what connect", "means: Gateway or Fusion"], ["3. Gateway work", "Register a node, health check"]], 60)
    + cols3([["4. Fusion work", "Bridge and dispute contracts"], ["5. Compliance design", "Which assets, who checks"], ["6. Test", "Redbelly 153, Fusion 73073"]], 152)
    + note(24, 248, "Time and cost are Unknown. Quant's figure of about 2 days is for a new chain family.", "#8fa1ad"),
    "S4, S5, S12", D)

rcp = ""
rows = [(["Proof by Query: on chain,", "verifier contract on Redbelly"], ["No public source shows it", "verified on another chain"]),
        (["Selective disclosure:", "off chain only"], ["Cannot be checked by a contract", "on another chain by itself"]),
        (["Issuer trust is set", "per contract"], ["A contract elsewhere needs", "its own choice of issuers"])]
rcp += note(24, 78, "On Redbelly today (Confirmed)", "#8fa1ad") + note(380, 78, "On another chain (Analysis)", "#8fa1ad")
for i, (a, b) in enumerate(rows):
    y = 90 + i * 54
    rcp += box(24, y, 320, 44, a) + line(344, y + 22, 372, y + 22) + box(372, y, 324, 44, b)
receptor = svg(290, "Which Receptor checks could work off Redbelly", rcp, "S7, S28, S31", D)

breaks = svg(300, "Where compliance could break (Analysis)",
    cols3([["Rules left behind", "A copy may move freely"], ["Stale permission", "Entry can outlive credential"], ["Two rule sets", "Firewall and credential differ"]], 60)
    + cols3([["Silent no-op", "Unlisted sender: no effect"], ["Token approval", "Quant's signers must approve"], ["Relayer trust", "Relayers decide what mints"]], 152)
    + note(24, 248, "Each box is a risk described in chapter 8, not a finding that it happens.", "#8fa1ad"),
    "S5, S7, S11, S14, S16, S17, S24", D)

d = R / "public" / "diagrams"; d.mkdir(parents=True, exist_ok=True)
(d / "selfserve.svg").write_text(selfserve); (d / "access.svg").write_text(access)
for n, v in dict(stack=stack, levels=levels, work=work, receptor=receptor, breaks=breaks).items(): (d / f"{n}.svg").write_text(v)
print("wrote 7 diagrams")
