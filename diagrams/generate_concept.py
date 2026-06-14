#!/usr/bin/env python3
# agent_worlds concept hero diagram — Flat Icon style (fireworks-tech-graph style 1).
# "Me" at the center, flanked by two worlds (assistants / builders) that take my
# input and return value. Output: SVG (English only, no CJK).
#
# ── ZERO MAINTENANCE ─────────────────────────────────────────────────
#   This script DISCOVERS agents by scanning  agents/<world>/<agent>/  and
#   pulls each blurb straight from that agent's README.md. To add an agent
#   to the diagram, just create its directory + README.md, then run:
#       python3 generate_concept.py
#   Nothing in this file needs editing.
#
#   Per agent it reads, from that agent's README.md:
#     • display name = the H1 title            (# Xxx)
#     • blurb        = the first prose line     (the one-line summary that
#                      every agent README puts right under its title)
#   Convention: keep the H1 short and put a one-sentence summary on the
#   first non-empty prose line. That line IS what the diagram shows.
# ─────────────────────────────────────────────────────────────────────
import os, re, html, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
AGENTS = os.path.join(REPO, "agents")

# Palette — Claude Official (warm cream), matching diagrams/pipeline.svg
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,'PingFang SC','Microsoft YaHei','SimHei',sans-serif"
BG = "#f8f6f3"                          # warm cream canvas
BLUE, GREEN = "#3f6896", "#4f8a76"      # give (I→agents) / return (agents→me)
INK, SUB = "#1a1a1a", "#6a6a6a"
HEAD = "#1a1a1a"                         # panel header text
PANEL_FILL, PANEL_STROKE = "#efe9e1", "#d8d0c6"   # soft warm panel
BOX_FILL, BOX_STROKE = "#ffffff", "#8a8278"       # agent card on cream
AVATAR = "#4a4a4a"

# geometry
W = 1060
CX = 530
PANEL_W = 340
LPX, RPX = 50, W - 50 - PANEL_W
PANEL_TOP = 130
HEADER_H = 95
NAME_H, LINE_H = 30, 18                 # box: name row + blurb lines
BOX_PAD_V, BOX_GAP = 16, 22
PAD_TOP, PAD_BOT = 30, 30
BLURB_MAX_CHARS = 34                    # per blurb line before wrapping
BLURB_MAX_LINES = 2


def esc(s):
    return html.escape(str(s), quote=True)


# ---- README parsing ----------------------------------------------------
def parse_readme(path):
    """Return (display_name, blurb_lines) pulled from a README.md.

    Prefers explicit HTML-comment fields; falls back to H1 + first prose.
    """
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        return None, []

    name, prose = None, None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("# ") and name is None:        # H1 title
            name = s[2:].strip()
            continue
        if s.startswith((">", "<", "#", "![", "|", "-", "*", "`")):
            continue                                    # quote / html / heading / list / img
        if prose is None:
            prose = s                                   # first real prose line
            break

    if prose:
        sentence = re.split(r"(?<=[.!?])\s", prose)[0].strip()
        blurb_lines = wrap(sentence, BLURB_MAX_CHARS, BLURB_MAX_LINES)
    else:
        blurb_lines = []
    return name, blurb_lines


def wrap(text, max_chars, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
        else:
            cur = (cur + " " + w).strip()
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if lines and (len(words) > sum(len(l.split()) for l in lines)):
        lines[-1] = lines[-1].rstrip(".") + "…"
    return lines


def discover(world):
    """Scan agents/<world>/*/README.md → list of (name, blurb_lines)."""
    out = []
    for readme in sorted(glob.glob(os.path.join(AGENTS, world, "*", "README.md"))):
        name, blurb = parse_readme(readme)
        if name:
            out.append((name, blurb))
    return out


ASSISTANTS = discover("assistants")
BUILDERS = discover("builders")


# ---- layout ------------------------------------------------------------
def box_height(blurb_lines):
    return BOX_PAD_V + NAME_H + max(len(blurb_lines), 1) * LINE_H + BOX_PAD_V


def panel_height(items):
    h = PAD_TOP + HEADER_H + PAD_BOT
    h += sum(box_height(b) for _, b in items)
    h += max(len(items) - 1, 0) * BOX_GAP
    return h


def avatar(cx, by, scale=1.0):
    r, sw = 18 * scale, 32 * scale
    hy = by - 52 * scale
    return [
        '  <circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (cx, hy, r, AVATAR),
        '  <path d="M %g,%g Q %g,%g %g,%g Q %g,%g %g,%g Z" fill="%s"/>' % (
            cx - sw, by, cx - sw, by - 40 * scale, cx, by - 40 * scale,
            cx + sw, by - 40 * scale, cx + sw, by, AVATAR),
    ]


def draw_panel(x, items, head, sub1, sub2):
    ph = panel_height(items)
    out = []
    out.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        x, PANEL_TOP, PANEL_W, ph, PANEL_FILL, PANEL_STROKE))
    out.append('  <text x="%d" y="%d" fill="%s" font-size="18" font-weight="700">%s</text>' % (x + 22, PANEL_TOP + 34, HEAD, esc(head)))
    out.append('  <text x="%d" y="%d" fill="%s" font-size="12.5">%s</text>' % (x + 22, PANEL_TOP + 54, SUB, esc(sub1)))
    out.append('  <text x="%d" y="%d" fill="%s" font-size="11.5">%s</text>' % (x + 22, PANEL_TOP + 72, SUB, esc(sub2)))
    by = PANEL_TOP + PAD_TOP + HEADER_H
    for name, blurb in items:
        bh = box_height(blurb)
        bx, bw = x + 28, PANEL_W - 56
        out.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="1.5"/>' % (bx, by, bw, bh, BOX_FILL, BOX_STROKE))
        out.append('  <text x="%d" y="%d" fill="%s" font-size="14.5" font-weight="600">%s</text>' % (bx + 18, by + 30, INK, esc(name)))
        ty = by + 30 + LINE_H
        for bl in (blurb or [""]):
            out.append('  <text x="%d" y="%d" fill="%s" font-size="12">%s</text>' % (bx + 18, ty, SUB, esc(bl)))
            ty += LINE_H
        by += bh + BOX_GAP
    return out, ph


L = []
body_h = max(panel_height(ASSISTANTS), panel_height(BUILDERS), 233)
H = PANEL_TOP + body_h + 120
L.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
L.append('  <style>text { font-family: %s; }</style>' % FONT)
L.append('  <defs>')
L.append('    <marker id="a-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % BLUE)
L.append('    <marker id="a-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="%s"/></marker>' % GREEN)
L.append('  </defs>')
L.append('  <rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))

L.append('  <text x="%d" y="46" text-anchor="middle" fill="%s" font-size="24" font-weight="700">agent_worlds</text>' % (CX, INK))
L.append('  <text x="%d" y="72" text-anchor="middle" fill="%s" font-size="14">Two worlds of agents that serve me</text>' % (CX, SUB))

lp, _ = draw_panel(LPX, ASSISTANTS, "ASSISTANTS", "work helpers", "Carry the work I already have")
rp, _ = draw_panel(RPX, BUILDERS, "BUILDERS", "project agents", "Create the things I want to make")
L += lp
L += rp

ME_BY = PANEL_TOP + 155
L += avatar(CX, ME_BY)
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="16" font-weight="700">Me</text>' % (CX, ME_BY + 26, INK))
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="11">raw work + ideas</text>' % (CX, ME_BY + 44, SUB))

ay_out, ay_back = ME_BY - 45, ME_BY - 15
L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#a-blue)"/>' % (CX - 32, ay_out, LPX + PANEL_W + 4, ay_out - 28, BLUE))
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="12">work · inboxes</text>' % ((CX - 32 + LPX + PANEL_W) // 2, ay_out - 26, BLUE))
L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#a-green)"/>' % (LPX + PANEL_W + 4, ay_back, CX - 32, ay_back + 4, GREEN))
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="12">handled · digests</text>' % ((CX - 32 + LPX + PANEL_W) // 2, ay_back + 24, GREEN))
L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#a-blue)"/>' % (CX + 32, ay_out, RPX - 4, ay_out - 28, BLUE))
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="12">rough ideas</text>' % ((CX + 32 + RPX) // 2, ay_out - 26, BLUE))
L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#a-green)"/>' % (RPX - 4, ay_back, CX + 32, ay_back + 4, GREEN))
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="12">results</text>' % ((CX + 32 + RPX) // 2, ay_back + 24, GREEN))

tag_y = PANEL_TOP + body_h + 32
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="15" font-weight="700">Lighten the load</text>' % (LPX + PANEL_W // 2, tag_y, BLUE))
L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="15" font-weight="700">Build the future</text>' % (RPX + PANEL_W // 2, tag_y, GREEN))

ly = H - 30
L.append('  <line x1="60" y1="%d" x2="92" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#a-blue)"/>' % (ly, ly, BLUE))
L.append('  <text x="100" y="%d" fill="%s" font-size="12">I hand over work &amp; ideas</text>' % (ly + 4, SUB))
L.append('  <line x1="320" y1="%d" x2="352" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#a-green)"/>' % (ly, ly, GREEN))
L.append('  <text x="360" y="%d" fill="%s" font-size="12">agents return value</text>' % (ly + 4, SUB))

L.append('</svg>')

with open(os.path.join(HERE, "concept.svg"), "w") as f:
    f.write('\n'.join(L))

print("Discovered agents:")
for nm, bl in ASSISTANTS:
    print("  [assistant] %-28s %s" % (nm, " ".join(bl)))
for nm, bl in BUILDERS:
    print("  [builder]   %-28s %s" % (nm, " ".join(bl)))
print("wrote", os.path.join(HERE, "concept.svg"))
