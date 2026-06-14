#!/usr/bin/env python3
# Generate the PM Agent pipeline as a VERTICAL, human-centric diagram.
# A person ("Me") feeds raw ideas in at the top; the agent works the spine
# with semantic icons (not cold ①②③ numbers); at the blocking-questions
# step a person ("You") steps back in to decide. Output: SVG (CJK-safe in
# browsers).
#
# Usage:
#   python3 generate_all.py          # writes pipeline.svg  (style 8, the standard)
#   python3 generate_all.py --all    # also writes 1-flat-icon.svg ... 8-dark-luxury.svg
import os, sys, html

OUT = os.path.dirname(os.path.abspath(__file__))
STANDARD = "6-claude-official"      # the one embedded in PM Agent README → pipeline.svg

# ---- Shared geometry (vertical spine) ----
W = 860
H = 990
CX = 430
NW = 340
NX = CX - NW // 2          # 260
NH = 54

# spine: (top_y, icon_key, name, sublabel)
SPINE = [
    (76,  "idea",   "Input",                 "raw ideas · notes · PM decisions"),
    (168, "target", "Extract core goal",     "the one product goal to hit"),
    (256, "loop",   "Define MVP loop",       "the minimal usable loop"),
    (344, "tags",   "Classify P0/P1/Later",  "Decided · Assumption · Open"),
    (432, "doc",    "Generate spec bundle",  "three core files"),
    (520, "check",  "Run spec checklist",    "validate before build"),
    (608, "ask",    "Surface blocking Qs",   "ask only what blocks"),
]

# output container + files
CT_X, CT_Y, CT_W, CT_H = 180, 706, 500, 240
FILES = [
    ("00_project_brief.md",    False),
    ("01_mvp_spec.md",         False),
    ("02_tasks_acceptance.md", False),
    ("03_open_questions.md",   True),
    ("04_change_log.md",       True),
]
FROW_Y = 748
FROW_PITCH = 37


def esc(s):
    return html.escape(s, quote=True)


# ---------- human figures & semantic icons (style-adaptive) ----------
def avatar(cx, by, c, s=1.0):
    """Filled person figure; (cx, by) = bottom-center."""
    r, sw = 11 * s, 19 * s
    hy = by - 31 * s
    return [
        '  <circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (cx, hy, r, c),
        '  <path d="M %g,%g Q %g,%g %g,%g Q %g,%g %g,%g Z" fill="%s"/>' % (
            cx - sw, by, cx - sw, by - 24 * s, cx, by - 24 * s,
            cx + sw, by - 24 * s, cx + sw, by, c),
    ]


def icon(key, cx, cy, c):
    """Return a small (~24px) semantic glyph centered at (cx, cy), stroke color c."""
    o = []
    a = 'stroke="%s" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"' % c
    if key == "idea":            # lightbulb = raw idea
        o.append('  <circle cx="%g" cy="%g" r="7" %s/>' % (cx, cy - 3, a))
        o.append('  <path d="M %g,%g L %g,%g M %g,%g L %g,%g" %s/>' % (cx - 3, cy + 6, cx + 3, cy + 6, cx - 2, cy + 9, cx + 2, cy + 9, a))
    elif key == "target":        # concentric target = goal
        o.append('  <circle cx="%g" cy="%g" r="10" %s/>' % (cx, cy, a))
        o.append('  <circle cx="%g" cy="%g" r="4.5" %s/>' % (cx, cy, a))
        o.append('  <circle cx="%g" cy="%g" r="1.6" fill="%s"/>' % (cx, cy, c))
    elif key == "loop":          # circular arrow = MVP loop
        o.append('  <path d="M %g,%g A 9,9 0 1 1 %g,%g" %s/>' % (cx + 1, cy - 9, cx - 9, cy - 1, a))
        o.append('  <path d="M %g,%g l 5,-2 l -1,5" %s/>' % (cx + 1, cy - 9, a))
    elif key == "tags":          # stacked priority bars P0/P1/Later
        o.append('  <rect x="%g" y="%g" width="20" height="5" rx="2" %s/>' % (cx - 10, cy - 9, a))
        o.append('  <rect x="%g" y="%g" width="14" height="5" rx="2" %s/>' % (cx - 10, cy - 2, a))
        o.append('  <rect x="%g" y="%g" width="9" height="5" rx="2" %s/>' % (cx - 10, cy + 5, a))
    elif key == "doc":           # document with folded corner = spec file
        o.append('  <path d="M %g,%g L %g,%g L %g,%g L %g,%g L %g,%g Z" %s/>' % (
            cx - 8, cy - 11, cx + 3, cy - 11, cx + 9, cy - 5, cx + 9, cy + 11, cx - 8, cy + 11, a))
        o.append('  <path d="M %g,%g L %g,%g L %g,%g" %s/>' % (cx + 3, cy - 11, cx + 3, cy - 5, cx + 9, cy - 5, a))
        o.append('  <path d="M %g,%g L %g,%g M %g,%g L %g,%g" %s/>' % (cx - 4, cy + 1, cx + 5, cy + 1, cx - 4, cy + 6, cx + 5, cy + 6, a))
    elif key == "check":         # checkmark in a box = checklist
        o.append('  <rect x="%g" y="%g" width="20" height="20" rx="4" %s/>' % (cx - 10, cy - 10, a))
        o.append('  <path d="M %g,%g L %g,%g L %g,%g" stroke="%s" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' % (cx - 5, cy, cx - 1, cy + 5, cx + 6, cy - 5, c))
    elif key == "ask":           # question = human decision needed
        o.append('  <circle cx="%g" cy="%g" r="10" %s/>' % (cx, cy, a))
        o.append('  <text x="%g" y="%g" text-anchor="middle" fill="%s" font-size="14" font-weight="700">?</text>' % (cx, cy + 5, c))
    return o


def build(cfg):
    L = []
    L.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    L.append('  <style>')
    L.append('    text { font-family: %s; }' % cfg["font"])
    if cfg.get("title_font"):
        L.append('    .ttl { font-family: %s; }' % cfg["title_font"])
    L.append('  </style>')
    L.append('  <defs>')
    for d in cfg.get("defs", []):
        L.append('    ' + d)
    L.append('    <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    L.append('      <polygon points="0 0, 10 3.5, 0 7" fill="%s"/>' % cfg["arrow"])
    L.append('    </marker>')
    L.append('  </defs>')
    for b in cfg["bg"]:
        L.append('  ' + b)

    icon_c = cfg["arrow"]
    av_c = cfg.get("avatar", cfg["title_fill"])

    # title
    tcls = ' class="ttl"' if cfg.get("title_font") else ''
    L.append('  <text x="%d" y="46" text-anchor="middle"%s fill="%s" font-size="21" font-weight="700">PM Agent · Spec Pipeline</text>' % (CX, tcls, cfg["title_fill"]))

    # left layer labels
    for (ly, txt) in [(120, "INPUT"), (388, "DECOMPOSE"), (815, "OUTPUT")]:
        L.append('  <text x="40" y="%d" fill="%s" font-size="11" font-weight="700" letter-spacing="0.08em">%s</text>' % (ly, cfg["layer_fill"], txt))

    # spine connecting arrows (draw before nodes)
    pts = [y for (y, _, _, _) in SPINE]
    for i in range(len(pts) - 1):
        L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" %smarker-end="url(#arr)"/>' % (
            CX, pts[i] + NH + 2, CX, pts[i + 1] - 4, cfg["arrow"], cfg.get("dash", "")))
    L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" marker-end="url(#arr)"/>' % (
        CX, SPINE[-1][0] + NH + 2, CX, CT_Y - 4, cfg["arrow"]))

    # --- human "Me" feeding the input (left of node 0) ---
    n0y = SPINE[0][0] + NH // 2
    L += avatar(150, n0y + 16, av_c)
    L.append('  <text x="150" y="%d" text-anchor="middle" fill="%s" font-size="12" font-weight="600">Me</text>' % (n0y + 34, cfg["title_fill"]))
    L.append('  <line x1="178" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#arr)"/>' % (n0y, NX - 4, n0y, cfg["arrow"]))
    L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="10">raw ideas</text>' % ((178 + NX) // 2, n0y - 6, cfg["sub_fill"]))

    # spine nodes (icon + left-anchored label)
    for idx, (y, ikey, name, sub) in enumerate(SPINE):
        role = cfg["input"] if idx == 0 else cfg["proc"]
        if cfg.get("accent_strip"):
            L.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (
                NX, y, NW, NH, cfg["rx"], role["fill"], role["stroke"], cfg["stroke_w"], cfg.get("nfilter", "")))
            L.append('  <rect x="%d" y="%d" width="4" height="%d" rx="2" fill="%s"/>' % (NX, y, NH, cfg["accent_strip"]))
        else:
            L.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (
                NX, y, NW, NH, cfg["rx"], role["fill"], role["stroke"], cfg["stroke_w"], cfg.get("nfilter", "")))
        L += icon(ikey, NX + 30, y + NH // 2, icon_c)
        L.append('  <text x="%d" y="%d" fill="%s" font-size="15" font-weight="600">%s</text>' % (NX + 56, y + 23, role["text"], esc(name)))
        L.append('  <text x="%d" y="%d" fill="%s" font-size="11">%s</text>' % (NX + 56, y + 41, cfg["sub_fill"], esc(sub)))

    # --- human "You" decides at the blocking-questions step (right of last node) ---
    nly = SPINE[-1][0] + NH // 2
    ax = NX + NW
    L += avatar(710, nly + 16, av_c)
    L.append('  <text x="710" y="%d" text-anchor="middle" fill="%s" font-size="12" font-weight="600">You</text>' % (nly + 34, cfg["title_fill"]))
    # agent asks ->
    L.append('  <line x1="%d" y1="%d" x2="684" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#arr)"/>' % (ax + 4, nly - 8, nly - 8, cfg["arrow"]))
    L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="10">asks</text>' % ((ax + 684) // 2, nly - 14, cfg["sub_fill"]))
    # you decide <-
    L.append('  <line x1="684" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8" marker-end="url(#arr)"/>' % (nly + 12, ax + 4, nly + 12, cfg["arrow"]))
    L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="10">decides</text>' % ((ax + 684) // 2, nly + 26, cfg["sub_fill"]))

    # output container
    L.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="1.5" stroke-dasharray="6,4"/>' % (
        CT_X, CT_Y, CT_W, CT_H, cfg["rx"], cfg["ct_fill"], cfg["ct_stroke"]))
    L.append('  <text x="%d" y="%d" fill="%s" font-size="13" font-weight="700">Spec Bundle</text>' % (CT_X + 18, CT_Y + 26, cfg["title_fill"]))

    out = cfg["out"]
    for i, (fname, optional) in enumerate(FILES):
        fy = FROW_Y + i * FROW_PITCH
        fx = CT_X + 22
        fw = CT_W - 44
        dash = ' stroke-dasharray="4,3"' if optional else ''
        L.append('  <rect x="%d" y="%d" width="%d" height="28" rx="%d" fill="%s" stroke="%s" stroke-width="1.2"%s/>' % (
            fx, fy, fw, max(cfg["rx"] - 4, 2), out["fill"], out["stroke"], dash))
        L += icon("doc", fx + 18, fy + 14, out["stroke"])
        L.append('  <text x="%d" y="%d" fill="%s" font-size="12.5" font-family="%s">%s</text>' % (
            fx + 36, fy + 19, out["text"], cfg["mono"], esc(fname)))
        if optional:
            L.append('  <text x="%d" y="%d" text-anchor="end" fill="%s" font-size="10">optional</text>' % (
                fx + fw - 14, fy + 19, cfg["sub_fill"]))

    L.append('</svg>')
    return '\n'.join(L)


# ---- Per-style configs ----
SANS = "'Helvetica Neue',Helvetica,Arial,'PingFang SC','Microsoft YaHei','Microsoft JhengHei','SimHei',sans-serif"
SYS  = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,'PingFang SC','Microsoft YaHei','SimHei',sans-serif"
MONO = "'SF Mono','Fira Code','Cascadia Code','Courier New','Microsoft YaHei','SimHei',monospace"
COURIER = "'Courier New','Lucida Console','Microsoft YaHei','SimHei',monospace"

styles = {}

styles["1-flat-icon"] = dict(
    font=SANS, mono=MONO, arrow="#2563eb", rx=8, stroke_w="1.5", avatar="#1f2937",
    bg=['<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H)],
    title_fill="#111827", sub_fill="#6b7280", layer_fill="#9ca3af",
    input=dict(fill="#eff6ff", stroke="#bfdbfe", text="#111827"),
    proc=dict(fill="#ffffff", stroke="#d1d5db", text="#111827"),
    out=dict(fill="#f0fdf4", stroke="#16a34a", text="#111827"),
    ct_fill="none", ct_stroke="#d1d5db",
)

styles["2-dark-terminal"] = dict(
    font=MONO, mono=MONO, arrow="#a855f7", rx=6, stroke_w="1.5", avatar="#e2e8f0",
    defs=['<linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0f0f1a"/><stop offset="100%" stop-color="#1a1a2e"/></linearGradient>'],
    bg=['<rect width="%d" height="%d" fill="url(#bg-grad)"/>' % (W, H)],
    title_fill="#e2e8f0", sub_fill="#94a3b8", layer_fill="#64748b",
    input=dict(fill="#1e3a5f", stroke="#3b82f6", text="#e2e8f0"),
    proc=dict(fill="#1e1b4b", stroke="#7c3aed", text="#e2e8f0"),
    out=dict(fill="#052e16", stroke="#059669", text="#d1fae5"),
    ct_fill="#0f172a", ct_stroke="#334155",
)

styles["3-blueprint"] = dict(
    font=COURIER, mono=COURIER, arrow="#00b4d8", rx=2, stroke_w="1", avatar="#caf0f8",
    defs=['<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M 30 0 L 0 0 0 30" fill="none" stroke="#112240" stroke-width="0.5"/></pattern>'],
    bg=['<rect width="%d" height="%d" fill="#0a1628"/>' % (W, H),
        '<rect width="%d" height="%d" fill="url(#grid)" opacity="0.6"/>' % (W, H)],
    title_fill="#caf0f8", sub_fill="#48cae4", layer_fill="#00b4d8",
    input=dict(fill="#0d1f3c", stroke="#00b4d8", text="#caf0f8"),
    proc=dict(fill="#0d1f3c", stroke="#00b4d8", text="#caf0f8"),
    out=dict(fill="#0d1f3c", stroke="#06d6a0", text="#caf0f8"),
    ct_fill="none", ct_stroke="#00b4d8",
)

styles["4-notion-clean"] = dict(
    font=SYS, mono=SYS, arrow="#3b82f6", rx=4, stroke_w="1", avatar="#111827",
    bg=['<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H)],
    title_fill="#111827", sub_fill="#9ca3af", layer_fill="#9ca3af",
    input=dict(fill="#f9fafb", stroke="#e5e7eb", text="#111827"),
    proc=dict(fill="#f9fafb", stroke="#e5e7eb", text="#111827"),
    out=dict(fill="#ffffff", stroke="#9ca3af", text="#111827"),
    ct_fill="none", ct_stroke="#e5e7eb",
)

styles["5-glassmorphism"] = dict(
    font=SYS, mono=MONO, arrow="#58a6ff", rx=12, stroke_w="1", avatar="#f0f6fc",
    defs=[
        '<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0d1117"/><stop offset="50%" stop-color="#161b22"/><stop offset="100%" stop-color="#0d1117"/></linearGradient>',
        '<radialGradient id="glow-blue" cx="30%" cy="30%" r="45%"><stop offset="0%" stop-color="#58a6ff" stop-opacity="0.16"/><stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/></radialGradient>',
        '<radialGradient id="glow-purple" cx="70%" cy="75%" r="45%"><stop offset="0%" stop-color="#bc8cff" stop-opacity="0.14"/><stop offset="100%" stop-color="#bc8cff" stop-opacity="0"/></radialGradient>',
    ],
    bg=['<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H),
        '<rect width="%d" height="%d" fill="url(#glow-blue)"/>' % (W, H),
        '<rect width="%d" height="%d" fill="url(#glow-purple)"/>' % (W, H)],
    title_fill="#f0f6fc", sub_fill="#8b949e", layer_fill="#8b949e",
    input=dict(fill="rgba(255,255,255,0.07)", stroke="rgba(88,166,255,0.4)", text="#f0f6fc"),
    proc=dict(fill="rgba(255,255,255,0.06)", stroke="rgba(255,255,255,0.15)", text="#f0f6fc"),
    out=dict(fill="rgba(255,255,255,0.05)", stroke="rgba(63,185,80,0.5)", text="#f0f6fc"),
    ct_fill="rgba(255,255,255,0.03)", ct_stroke="rgba(255,255,255,0.18)",
)

styles["6-claude-official"] = dict(
    font=SYS, mono=SYS, arrow="#5a5a5a", rx=12, stroke_w="2.5", avatar="#4a4a4a",
    defs=['<filter id="shadow-soft" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#00000014"/></filter>'],
    nfilter='filter="url(#shadow-soft)"',
    bg=['<rect width="%d" height="%d" fill="#f8f6f3"/>' % (W, H)],
    title_fill="#1a1a1a", sub_fill="#6a6a6a", layer_fill="#6a6a6a",
    input=dict(fill="#a8c5e6", stroke="#4a4a4a", text="#1a1a1a"),
    proc=dict(fill="#9dd4c7", stroke="#4a4a4a", text="#1a1a1a"),
    out=dict(fill="#f4e4c1", stroke="#4a4a4a", text="#1a1a1a"),
    ct_fill="#e8e6e3", ct_stroke="#4a4a4a",
)

styles["7-openai"] = dict(
    font=SYS, mono=SYS, arrow="#71717a", rx=8, stroke_w="1.5", accent_strip="#10a37f", avatar="#0d0d0d",
    bg=['<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H)],
    title_fill="#0d0d0d", sub_fill="#6e6e80", layer_fill="#6e6e80",
    input=dict(fill="#ffffff", stroke="#e5e5e5", text="#0d0d0d"),
    proc=dict(fill="#ffffff", stroke="#e5e5e5", text="#0d0d0d"),
    out=dict(fill="#ffffff", stroke="#10a37f", text="#0d0d0d"),
    ct_fill="none", ct_stroke="#e5e5e5",
)

styles["8-dark-luxury"] = dict(
    font=SANS, mono=MONO, title_font="Georgia,'Times New Roman',serif",
    arrow="#d4a574", rx=6, stroke_w="1.5", avatar="#d4a574",
    defs=['<radialGradient id="glow" cx="50%" cy="42%" r="34%"><stop offset="0%" stop-color="#d4a574" stop-opacity="0.05"/><stop offset="100%" stop-color="#d4a574" stop-opacity="0"/></radialGradient>'],
    bg=['<rect width="%d" height="%d" fill="#0a0a0a"/>' % (W, H),
        '<rect width="%d" height="%d" fill="url(#glow)"/>' % (W, H)],
    title_fill="#f5f0eb", sub_fill="#a39787", layer_fill="#c9a96e",
    input=dict(fill="#111111", stroke="#fbbf24", text="#fbbf24"),
    proc=dict(fill="#111111", stroke="#5a9e6f", text="#5a9e6f"),
    out=dict(fill="#111111", stroke="#38bdf8", text="#38bdf8"),
    ct_fill="none", ct_stroke="#c9a96e",
)

for cfg in styles.values():
    cfg.setdefault("defs", [])
    cfg.setdefault("dash", "")
    cfg.setdefault("nfilter", "")

write_all = "--all" in sys.argv
if write_all:
    for name, cfg in styles.items():
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(build(cfg))
        print("wrote", name + ".svg")

# always (re)write the standard pipeline.svg from the standard style
with open(os.path.join(OUT, "pipeline.svg"), "w") as f:
    f.write(build(styles[STANDARD]))
print("wrote pipeline.svg (style: %s)" % STANDARD)
