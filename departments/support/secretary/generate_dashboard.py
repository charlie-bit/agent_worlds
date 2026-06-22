#!/usr/bin/env python3
"""
Secretary — Dashboard Generator
Reads outbox/{date}-digest.md  →  structured JSON  →  injects into
dashboard.template.html  →  writes outbox/dashboard.html.

Usage:
  python3 generate_dashboard.py            # all digests in outbox/
  python3 generate_dashboard.py 2026-06-21 # single date
"""

import json
import re
import sys
from pathlib import Path
from datetime import date as Date

OUTBOX   = Path(__file__).parent / "outbox"
TEMPLATE = Path(__file__).parent / "dashboard.template.html"
REGISTRY = Path.home() / ".agent_worlds" / "secretary" / "registry.yaml"
CHANNELS = OUTBOX / "channels_cache.json"
OUTPUT   = OUTBOX / "dashboard.html"


# ── Parser: md → structured dict ─────────────────────────────────────────────

def parse_digest(path: Path) -> dict:
    date_str = path.stem.replace("-digest", "")
    text = path.read_text()
    sections = _split_sections(text)

    return {
        "date":          date_str,
        "summary":       sections.get("Summary", "").strip(),
        "action_items":  _parse_action_items(sections.get("Action Items", "")),
        "waiting_on_me": _parse_topics(sections.get("Waiting On Me", "")),
        "sources":       _parse_sources(sections.get("Sources", "")),
        "coverage":      _parse_coverage(sections.get("Coverage", "")),
    }


def _split_sections(text: str) -> dict:
    sections, current, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(buf).strip()
            current, buf = line[3:].strip(), []
        elif line.startswith("# "):
            pass  # title line — skip
        else:
            if current is not None:
                buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def _parse_action_items(text: str) -> list:
    items = []
    for line in text.splitlines():
        m = re.match(r"^-\s*\[( |x)\]\s*(.+)", line.strip())
        if m:
            items.append({"type": "action", "done": m.group(1) == "x", "text": m.group(2).strip()})
    return items


def _parse_topics(text: str) -> list:
    items = []
    for line in text.splitlines():
        m = re.match(r"^-\s*\[(HIGH|MED|LOW)\]\s*(.+)", line.strip())
        if m:
            items.append({"type": "topic", "priority": m.group(1), "text": m.group(2).strip()})
        elif line.strip().startswith("- "):
            items.append({"type": "plain", "text": line.strip()[2:]})
    return items


def _parse_sources(text: str) -> list:
    """Split by ### source heading, then by #### subgroup."""
    sources = []
    blocks = re.split(r"\n(?=###\s)", "\n" + text)
    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("###"):
            continue
        lines = block.splitlines()
        src_name = lines[0].lstrip("#").strip()
        body = "\n".join(lines[1:])

        # check for #### subgroups
        subgroups = re.split(r"\n(?=####\s)", "\n" + body)
        groups = []
        flat_items = []
        for sg in subgroups:
            sg = sg.strip()
            if not sg:
                continue
            if sg.startswith("####"):
                sg_lines = sg.splitlines()
                g_name = sg_lines[0].lstrip("#").strip()
                g_body = "\n".join(sg_lines[1:])
                groups.append({"name": g_name, "items": _parse_topics(g_body)})
            else:
                flat_items.extend(_parse_topics(sg))

        if groups:
            sources.append({"name": src_name, "groups": groups})
        else:
            sources.append({"name": src_name, "items": flat_items})
    return sources


def _parse_coverage(text: str) -> list:
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append({"type": "coverage", "text": line[2:]})
    return items


# ── Renderer: JSON → HTML via template ───────────────────────────────────────

def load_registry() -> dict:
    base = {
        "owner": {"slack_user_id": "", "name": "", "timezone": ""},
        "channels": [],
        "sources_enabled": [],
        "model": "claude-code",
    }
    if not REGISTRY.exists():
        return base
    try:
        import re as _re
        text = REGISTRY.read_text()
        reg = {"owner": {"slack_user_id": "", "name": "", "timezone": ""}, "channels": [], "sources_enabled": [], "model": "claude-code"}
        uid  = _re.search(r'slack_user_id:\s*["\']?([^\s"\']+)', text)
        tz   = _re.search(r'timezone:\s*["\']?([^\s"\']+)', text)
        name = _re.search(r'name:\s*["\']?([^\s"\']+)', text)
        mdl  = _re.search(r'model:\s*["\']?([^\s"\']+)', text)
        if uid:  reg["owner"]["slack_user_id"] = uid.group(1)
        if tz:   reg["owner"]["timezone"]      = tz.group(1)
        if name: reg["owner"]["name"]          = name.group(1)
        if mdl:  reg["model"]                  = mdl.group(1)
        for m in _re.finditer(r'-\s*\{[^}]*name:\s*(\S+)[^}]*channel_id:\s*(\S+)[^}]*group:\s*(\S+)', text):
            reg["channels"].append({"name": m.group(1), "channel_id": m.group(2), "group": m.group(3)})
        for src in ["slack","jira","github","calendar","gmail","feishu"]:
            m = _re.search(rf'{src}:\s*\n\s*enabled:\s*(true|false)', text)
            if m and m.group(1) == "true":
                reg["sources_enabled"].append(src)
        return reg
    except Exception:
        return {}


def load_channels() -> list:
    if not CHANNELS.exists():
        return []
    try:
        return json.loads(CHANNELS.read_text())
    except Exception:
        return []


def render(digests: list) -> str:
    template  = TEMPLATE.read_text()
    data_json = json.dumps(digests, ensure_ascii=False, indent=2)
    reg_json  = json.dumps(load_registry(), ensure_ascii=False)
    ch_json   = json.dumps(load_channels(), ensure_ascii=False)
    html = template.replace("__DIGEST_DATA__", data_json)
    # inject data tags BEFORE the main <script> block so JS can read them immediately
    tags = (
        f'<script id="registry-data" type="application/json">\n{reg_json}\n</script>\n'
        f'<script id="channels-data" type="application/json">\n{ch_json}\n</script>\n'
    )
    return html.replace('<script id="digest-data"', tags + '<script id="digest-data"')


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None

    md_files = sorted(OUTBOX.glob("*-digest.md"), reverse=True)
    if target:
        md_files = [f for f in md_files if f.stem.startswith(target)]

    digests = [parse_digest(f) for f in md_files]

    OUTBOX.mkdir(exist_ok=True)
    OUTPUT.write_text(render(digests))

    print(f"✓ Dashboard written → {OUTPUT}")
    print(f"  Dates: {[d['date'] for d in digests] or ['(none — template with empty state rendered)']}")


if __name__ == "__main__":
    main()
