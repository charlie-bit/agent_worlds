#!/usr/bin/env python3
# agent_worlds concept hero diagram — the company org chart.
# Renders: company -> departments -> roles, in the warm Claude palette.
#
# ── SINGLE SOURCE OF TRUTH ───────────────────────────────────────────
#   This script reads the org structure from  company.yaml  (NOT the agent
#   READMEs). To change the diagram, edit company.yaml, then run:
#       python3 generate_concept.py
#   Stub roles (status: stub) render muted + dashed; active roles solid.
#   No third-party deps — a tiny purpose-built parser reads company.yaml.
# ─────────────────────────────────────────────────────────────────────
import os, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
COMPANY = os.path.join(REPO, "company.yaml")


def esc(s):
    return html.escape(str(s), quote=True)


# ---- minimal company.yaml parser (indentation-based, fixed schema) -----
def load_company(path):
    """Parse company.yaml into {company, tagline, departments:[{name,purpose,
    roles:[{name,summary,status}]}]}. Tolerant of our own file's shape only."""
    company = {"company": "agent_worlds", "tagline": "", "departments": []}
    cur_dept = cur_role = None
    section = None  # None | 'departments'

    def indent(s):
        return len(s) - len(s.lstrip(" "))

    for raw in open(path, encoding="utf-8").read().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        ind = indent(raw)
        line = raw.strip()
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip().strip('"').strip("'")

        if ind == 0:
            if key == "company":
                company["company"] = val
            elif key == "tagline":
                company["tagline"] = val
            elif key == "departments":
                section = "departments"
            else:
                section = None
        elif section == "departments" and ind == 2:           # department name
            cur_dept = {"name": key, "purpose": "", "roles": []}
            company["departments"].append(cur_dept)
            cur_role = None
        elif section == "departments" and ind == 4 and cur_dept is not None:
            if key == "purpose":
                cur_dept["purpose"] = val
            elif key == "roles":
                pass
        elif section == "departments" and ind == 6 and cur_dept is not None:  # role name
            cur_role = {"name": key, "summary": "", "status": "active"}
            cur_dept["roles"].append(cur_role)
        elif section == "departments" and ind == 8 and cur_role is not None:
            if key == "summary":
                cur_role["summary"] = val
            elif key == "status":
                cur_role["status"] = val
    return company


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


# ---- palette (Claude Official warm cream, matches pipeline.svg) --------
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,'PingFang SC','Microsoft YaHei','SimHei',sans-serif"
MONO = "'SF Mono','Fira Code','Cascadia Code','Courier New',monospace"
BG = "#f8f6f3"
INK, SUB, HEAD = "#1a1a1a", "#6a6a6a", "#1a1a1a"
PANEL_FILL, PANEL_STROKE = "#efe9e1", "#d8d0c6"
ACTIVE_FILL, ACTIVE_STROKE = "#9dd4c7", "#4a4a4a"   # active role (teal, like proc node)
STUB_FILL, STUB_STROKE = "#ffffff", "#b7afa1"   # stub role (muted)
COMPANY_FILL, COMPANY_STROKE = "#f4e4c1", "#4a4a4a"  # company crown (warm gold)
LINE = "#9a9a9a"

# ---- geometry ----------------------------------------------------------
W = 1100
MARGIN = 40
GUTTER = 20
TOP = 40
COMPANY_H = 64
DEPT_TOP = TOP + COMPANY_H + 54     # room for connector
DEPT_HEAD_H = 64
ROLE_H_NAME = 26
ROLE_LINE = 15
ROLE_PAD_V = 12
ROLE_GAP = 12
DEPT_PAD = 16
ROLE_BLURB_CHARS = 26
ROLE_BLURB_LINES = 2


def role_h(blurb):
    return ROLE_PAD_V + ROLE_H_NAME + max(len(blurb), 1) * ROLE_LINE + ROLE_PAD_V


def dept_h(roles):
    h = DEPT_PAD + DEPT_HEAD_H
    h += sum(role_h(r["_blurb"]) for r in roles)
    h += max(len(roles) - 1, 0) * ROLE_GAP
    h += DEPT_PAD
    return h


def build(company):
    depts = company["departments"]
    n = len(depts)
    avail = W - 2 * MARGIN - (n - 1) * GUTTER
    col_w = avail // n

    # precompute blurbs + per-dept heights
    for d in depts:
        for r in d["roles"]:
            r["_blurb"] = wrap(r["summary"], ROLE_BLURB_CHARS, ROLE_BLURB_LINES)
    body_h = max((dept_h(d["roles"]) for d in depts), default=120)
    H = DEPT_TOP + body_h + 50

    L = []
    L.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    L.append('  <style>text { font-family: %s; } .mono { font-family: %s; }</style>' % (FONT, MONO))
    L.append('  <defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#00000014"/></filter></defs>')
    L.append('  <rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))

    # ---- company crown (centered top) ----
    cw, cx = 360, W // 2
    cxx = cx - cw // 2
    L.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="2.5" filter="url(#sh)"/>' % (
        cxx, TOP, cw, COMPANY_H, COMPANY_FILL, COMPANY_STROKE))
    L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="20" font-weight="700">%s</text>' % (
        cx, TOP + 27, INK, esc(company["company"])))
    L.append('  <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="11.5">%s</text>' % (
        cx, TOP + 47, SUB, esc(company["tagline"])))

    # ---- department columns ----
    col_x = []
    x = MARGIN
    for _ in depts:
        col_x.append(x)
        x += col_w + GUTTER

    # connectors company -> each department head
    bus_y = TOP + COMPANY_H + 26
    L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.6"/>' % (cx, TOP + COMPANY_H, cx, bus_y, LINE))
    if n > 1:
        L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.6"/>' % (
            col_x[0] + col_w // 2, bus_y, col_x[-1] + col_w // 2, bus_y, LINE))
    for cxp in col_x:
        mid = cxp + col_w // 2
        L.append('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.6"/>' % (mid, bus_y, mid, DEPT_TOP, LINE))

    for d, cxp in zip(depts, col_x):
        ph = dept_h(d["roles"])
        L.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
            cxp, DEPT_TOP, col_w, ph, PANEL_FILL, PANEL_STROKE))
        L.append('  <text x="%d" y="%d" fill="%s" font-size="16" font-weight="700">%s</text>' % (
            cxp + DEPT_PAD, DEPT_TOP + 30, HEAD, esc(d["name"])))
        for i, ln in enumerate(wrap(d["purpose"], int(col_w / 6.4), 2)):
            L.append('  <text x="%d" y="%d" fill="%s" font-size="11">%s</text>' % (
                cxp + DEPT_PAD, DEPT_TOP + 48 + i * 14, SUB, esc(ln)))

        by = DEPT_TOP + DEPT_PAD + DEPT_HEAD_H
        for r in d["roles"]:
            rh = role_h(r["_blurb"])
            bx, bw = cxp + DEPT_PAD, col_w - 2 * DEPT_PAD
            stub = r["status"] == "stub"
            fill = STUB_FILL if stub else ACTIVE_FILL
            stroke = STUB_STROKE if stub else ACTIVE_STROKE
            dash = ' stroke-dasharray="5,3"' if stub else ''
            L.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="1.5"%s/>' % (
                bx, by, bw, rh, fill, stroke, dash))
            L.append('  <text x="%d" y="%d" class="mono" fill="%s" font-size="13.5" font-weight="700">%s</text>' % (
                bx + 14, by + 24, INK, esc(r["name"])))
            if stub:
                L.append('  <text x="%d" y="%d" text-anchor="end" fill="%s" font-size="9.5">stub</text>' % (
                    bx + bw - 12, by + 24, SUB))
            ty = by + 24 + ROLE_LINE
            for bl in (r["_blurb"] or [""]):
                L.append('  <text x="%d" y="%d" fill="%s" font-size="11">%s</text>' % (bx + 14, ty, SUB, esc(bl)))
                ty += ROLE_LINE
            by += rh + ROLE_GAP

    L.append('</svg>')
    return '\n'.join(L)


company = load_company(COMPANY)
svg = build(company)
with open(os.path.join(HERE, "concept.svg"), "w") as f:
    f.write(svg)

print("Company:", company["company"])
for d in company["departments"]:
    print("  department: %-12s (%d roles)" % (d["name"], len(d["roles"])))
    for r in d["roles"]:
        print("    %-12s [%s] %s" % (r["name"], r["status"], r["summary"]))
print("wrote", os.path.join(HERE, "concept.svg"))
