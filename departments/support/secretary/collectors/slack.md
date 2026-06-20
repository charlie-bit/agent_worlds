# Collector — Slack

> **module:** `A.slack` · **emits:** raw item (`../item_schema.md`) · **adapter:** host-resolved (see bottom)

The heaviest inbox, so the first collector built. It sweeps Slack for one date
and emits a flat list of **raw items**. It does not group, rank, or dedupe across
sources — that is B's job. It only gathers and stamps each item with the fields
B needs.

## Capability (host-agnostic)

Gather, for the owner, on a given date:

- **DMs** sent to the owner.
- **@-mentions** of the owner in any accessible channel.
- **Tracked people's** activity (the registry's `tracked_people` — for awareness).
- **The owner's own outbound**, used as a lead to find threads they're in that
  got new replies.

Who/what is tracked is **config, not prompt**: read from the external registry
(`../config.md` defines the schema and points to the file). The registry decides
*grouping*, never *inclusion* — anyone who DMs or @-mentions the owner is
collected even if untracked.

## Time window

Slack queries take Unix timestamps. The owner's timezone lives in the registry
(`owner.timezone`, e.g. `Asia/Hong_Kong` = UTC+8). For target date `D`:

```
oldest      = D 00:00 owner-local  → UTC epoch
latest      = D+1 00:00 owner-local → UTC epoch
oldest_prev = D-1 00:00 owner-local → UTC epoch   # cross-day thread catch
```

`oldest_prev` exists because a thread from yesterday can get a new reply today;
scanning only `[oldest, latest)` would miss the parent. Pull the previous day too
when expanding threads, but only **report** activity that falls on `D`.

## Query layers

Four gathering layers + one enrichment pass. Layers are independent and run in
parallel; the enrichment pass runs after, on items already collected.

| # | layer | what it gathers | default `relation` |
| --- | --- | --- | --- |
| 1 | **DM** | messages in the owner's DM channels | `waiting_on_me` |
| 2 | **@me** | messages @-mentioning the owner | `waiting_on_me` |
| 3 | **tracked** | tracked people's messages across accessible channels | `fyi` |
| 4 | **outbound** | messages the owner sent (lead to their threads) | `fyi` |
| 5 | **thread expand** | full context for items that have substantive threads | inherits parent |

Notes:

- **Layer 3 (tracked)** is for awareness — what the team is doing — not
  obligation, hence `fyi`. The registry MAY mark some people for *full activity*
  monitoring (all their channel messages) vs *interaction-only* (surface during
  triage only what touches the owner); this is a registry flag, not logic baked
  into this collector.
- **Layer 5 (thread expand)** is enrichment, not a query layer: for an already
  collected item with a thread, pull the thread to give B better clustering
  material. Skip pure "on it" / "noted" / emoji-only threads.
- `relation` defaults are **per-layer**, but a strong textual signal overrides:
  a DM saying "can you do X" → `action_required`; a tracked-person message that
  @-mentions the owner is really an @me hit → `waiting_on_me`.

## Field mapping (Slack result → raw item)

| raw item field | from Slack |
| --- | --- |
| `source` | literal `slack` |
| `context` | channel id/name for channel messages; **empty for DMs** (a DM has no channel to group by — B leaves DMs ungrouped or groups by `who`) |
| `type` | `dm` (layer 1) / `mention` (layer 2) / `message` (layers 3–4) |
| `relation` | per-layer default above, upgraded on strong textual signal |
| `title` | one-line gist of the message (first meaningful line, trimmed) |
| `who` | sender's Slack user id (a resolvable handle, so tracked-people matching works) |
| `when` | message timestamp, as ISO 8601 |
| `link` | permalink to the message |
| `raw_text` | the message text (thread text appended when layer 5 expanded it) |
| `dedup_key` | `slack:{channel_id}:{message_ts}` — see below |

## Dedup key

```
dedup_key = "slack:{channel_id}:{message_ts}"
```

The message `ts` is unique within a channel, so this identifies a message
exactly. The same message legitimately surfaces in more than one layer — a
tracked person who @-mentions the owner hits both layer 2 and layer 3; an
outbound reply hits both layer 1 and layer 4. The collector stamps the key;
**B collapses matching keys**, keeping the item with the most obligation-heavy
`relation` (`action_required` > `waiting_on_me` > `fyi`) and the richest
`raw_text`. The collector itself does not dedupe across layers — it may emit
duplicates, and that is fine; the stable key makes B's merge trivial.

## Coverage (never silently skip)

The collector reports, per layer: scanned scope → item count, "no results", or
"did not run — {reason}". An empty inbox and a failed scan must read
differently in the digest's Coverage section.

## Adapter binding (host-specific — the only part that changes per host)

The capability above is host-agnostic. *How* it is fetched is resolved by the
current host and is the **only** thing that changes when moving hosts.

- **Claude Code (current)** → MCP `slack`:
  - layer 1 / monitored channels → read each channel over `[oldest, latest)`
  - layers 2–4 → search with `to:me`, `from:<@owner>`, `from:<@tracked>` scoped
    to the date (also the previous day for cross-day threads)
  - layer 5 → read the specific thread
- **Codex (planned)** → its Slack connector / Slack Web API with the same queries.
- **Plain script** → Slack Web API + a bot token.

Do not hardcode host-specific call names into the capability sections above; keep
them confined to this binding block.
