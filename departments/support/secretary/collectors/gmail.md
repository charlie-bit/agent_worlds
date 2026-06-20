# Collector — Gmail

> **module:** `A.gmail` · **emits:** raw item (`../item_schema.md`) · **adapter:** Gmail MCP, read-only scope (see bottom)

Sweeps the owner's mailbox for one date and emits **raw items**. Email is noisier
than Slack — most of it is `fyi` (newsletters, automated notifications) and only a
slice genuinely waits on the owner. So this collector's main job, beyond
gathering, is stamping a defensible `relation` per layer so B can route the few
real obligations to the top.

## Capability (host-agnostic)

Gather, for the owner, on a given date:

- **Unread** mail in the inbox addressed to the owner.
- **Awaiting-reply** threads — the owner is a recipient and the last message is
  **not** from them (someone is waiting on a reply).

What counts as "mine to handle" vs noise is refined by the registry (sender /
domain / label → group, and an optional mute list). Config, not prompt.

## Time window

Same model as `slack.md`: compute `[oldest, latest)` in `owner.timezone`
(registry), plus the previous day (`oldest_prev`) so a thread that got a new
reply today is caught even if its root is older. Report only activity on `D`.

## Query layers

| # | layer | what it gathers | default `relation` |
| --- | --- | --- | --- |
| 1 | **unread-to-me** | unread inbox mail where the owner is in `to:` | `waiting_on_me` |
| 2 | **awaiting-reply** | threads where the owner is a recipient and the last message is not theirs | `waiting_on_me` |
| 3 | **bulk / notification** | list-mail, automated senders, newsletters | `fyi` |

Notes:

- Layers 1–2 overlap heavily (an unread thread awaiting reply hits both); that is
  fine — `dedup_key` collapses them in B.
- **Layer 3 is a demotion, not a separate fetch.** Mail carrying a
  `List-Unsubscribe` header, a no-reply sender, or a registry-muted domain is
  forced to `fyi` regardless of unread state — this is what keeps newsletters out
  of "Waiting On Me."
- **Strong textual signal upgrades** `relation`: a direct ask ("can you review by
  Friday", "please approve") → `action_required`. Default per-layer otherwise.
- Read-only: never mark-as-read, archive, or send. Reading must not change unread
  state (use a metadata/peek mode, not a fetch that flips the read flag).

## Field mapping (Gmail message → raw item)

| raw item field | from Gmail |
| --- | --- |
| `source` | literal `gmail` |
| `context` | the most specific user label on the thread, else empty (B looks up label/domain → group; plain inbox mail may be ungrouped) |
| `type` | `email` |
| `relation` | per-layer default above, demoted by layer 3 rules, upgraded on strong ask |
| `title` | the subject line (trimmed) |
| `who` | sender email address (resolvable handle for tracked-people / domain grouping) |
| `when` | the message's `Date`, as ISO 8601 |
| `link` | permalink, e.g. `https://mail.google.com/mail/u/0/#inbox/{message_id}` |
| `raw_text` | subject + snippet/body (plain text); strip quoted history when expanding a thread |
| `dedup_key` | `gmail:{message_id}` — see below |

## Dedup key

```
dedup_key = "gmail:{message_id}"          # RFC 822 Message-ID — globally unique
```

Use the immutable per-message id (not the thread id — a thread holds many
messages). The same message surfacing in layers 1 and 2 carries the same key, so
B keeps one copy, preferring the most obligation-heavy `relation`. To cluster a
whole thread into one topic, B groups by thread id at the **clustering** step
(`triage.md` step 2) — that is clustering, not dedupe; keep the two distinct.

## Coverage (never silently skip)

Report, per layer: scanned scope → count, "no results", or "did not run —
{reason}". A clean inbox and an auth failure must read differently in the digest.

## Adapter binding (host-specific)

The capability above is host-agnostic. *How* it is fetched is resolved by the
current host and is the only thing that changes when moving hosts.

- **Claude Code (current)** → **Gmail MCP**, not yet connected. Candidate:
  [`ArtyMcLabin/Gmail-MCP-Server`](https://github.com/ArtyMcLabin/Gmail-MCP-Server)
  (a maintained fork of `GongRzhe/Gmail-MCP-Server`; local stdio server, OAuth2).
  Layer mapping:
  - layers 1–2 → `search_emails` (`is:unread in:inbox to:me`,
    awaiting-reply query) + `list_inbox_threads` / `get_inbox_with_threads` to
    judge "last message not mine"
  - thread clustering material → `get_thread`
  - field detail (subject, sender, CC/BCC, body) → `read_email`
  - **Read-only enforcement — non-negotiable for this role.** This server also
    exposes send / delete / mark-read / move / draft tools. Authenticate with its
    `--scopes` flag limited to **`gmail.readonly`**: the server then *filters out*
    the write tools, so they are never callable. This turns the read-only
    boundary from a prose convention (`agent.md`) into an **OAuth-level
    guarantee** — exactly the least-privilege rule the role requires. Do not
    grant a broader scope "for convenience."
- **Codex (planned)** → its Gmail connector / the Gmail API with the same queries.
- **Plain script** → Gmail API (OAuth `gmail.readonly`): `users.messages.list`
  with the queries above → `users.messages.get` for headers/body.

Until this MCP is actually connected (with read-only scope) and authenticated, a
run with `gmail.enabled: true` must report `gmail: did not run — no adapter
connected` in Coverage. It must **not** silently skip. Per the repo rule, only
wire this up when the owner actually needs email in the digest — grow by being
used.
