# Collector — Feishu (飞书 / Lark)

> **module:** `A.feishu` · **emits:** raw item (`../item_schema.md`) · **adapter:** ⚠️ none on current host, API TBD (see bottom)

Sweeps Feishu for one date and emits **raw items**. Feishu is not one inbox but
three surfaces in one platform — **IM messages, Tasks (todos), and Docs
@-mentions** — so this collector's shape mirrors that: one layer per surface, each
mapped to the same raw-item contract. B does not care that they came from one
platform; it sees uniform raw items.

## Capability (host-agnostic)

Gather, for the owner, on a given date:

- **Messages** — DMs to the owner and group-chat messages @-mentioning the owner.
- **Tasks (待办)** — todos assigned to the owner, or due/overdue.
- **Doc @-mentions** — places the owner was @-mentioned in a Feishu Doc / Wiki,
  or a doc comment directed at them.

Who/what is tracked (chats, doc spaces, group→group-label) is **config, not
prompt**: from the external registry (`../config.md`). The registry decides
*grouping*, never *inclusion* — a direct message or @-mention reaches the digest
even from an untracked sender.

## Time window

Same model as `slack.md` / `gmail.md`: compute `[oldest, latest)` in
`owner.timezone` (registry), plus the previous day (`oldest_prev`) for cross-day
threads / comment chains. Report only activity on `D`. Tasks are the exception:
an **overdue** task surfaces regardless of when it was created (see layer 2).

## Query layers

| # | layer | what it gathers | default `relation` |
| --- | --- | --- | --- |
| 1 | **message** | DMs to the owner; group messages @-mentioning them | `waiting_on_me` |
| 2 | **task** | todos assigned to the owner; due or overdue items | `action_required` |
| 3 | **doc-mention** | @-mentions of the owner in Docs/Wiki; comments directed at them | `waiting_on_me` |

Notes:

- **Layer 2 (task) defaults to `action_required`** — a todo *is* an action by
  definition, unlike a message that merely might need a reply. An **overdue**
  task is the clearest `HIGH` signal Feishu produces; surface it even if it
  wasn't touched on `D`.
- **Strong signal still overrides:** a layer-1 message that's pure FYI (a tracked
  person posting in a group, not addressing the owner) → `fyi`; a doc comment
  that's just an ack → `fyi`.
- Group messages that merely mention a tracked person but not the owner are
  awareness only → `fyi` (parallels Slack's tracked layer).
- Read-only: never send a message, complete/reassign a task, or resolve a
  comment. Reading must not change read/unread or task state.

## Field mapping (Feishu object → raw item)

| raw item field | from Feishu |
| --- | --- |
| `source` | literal `feishu` |
| `context` | chat id (messages) / doc or wiki token (doc-mentions) / empty for a personal task with no container — B looks it up for `group` |
| `type` | `message` (layer 1) / `task` (layer 2) / `doc_mention` (layer 3) |
| `relation` | per-layer default above, overridden on signal |
| `title` | one-line gist: message text / task title / doc title + the mention snippet |
| `who` | originator's Feishu `open_id` / `union_id` (resolvable handle for tracked-people matching) |
| `when` | message ts / task due-or-update time / mention time, as ISO 8601 |
| `link` | deep link: `https://…feishu.cn/…` to the message, task, or doc anchor |
| `raw_text` | message body / task title + notes / the doc passage around the mention |
| `dedup_key` | per-surface id — see below |

## Dedup key

One platform, three id spaces — the key is prefixed by surface so they never
collide:

```
message      → feishu:msg:{message_id}
task         → feishu:task:{task_guid}
doc-mention  → feishu:doc:{doc_token}:{mention_id or comment_id}
```

Each is the surface's natural unique id. The same object surfacing twice (a DM
that's also a tracked-person message; a task hit by both "assigned" and "overdue"
queries) carries one key, so **B collapses it**, keeping the most
obligation-heavy `relation`. Cross-surface clustering (a message *about* a task,
a comment *about* a doc) is B's clustering step, not dedupe — keep the two
distinct.

## Coverage (never silently skip)

Report, per layer: scanned scope → count, "no results", or "did not run —
{reason}". A quiet day and a failed/unauthorized scan must read differently in
the digest.

## Adapter binding (host-specific) — ⚠️ none connected; partial-coverage MCP exists

The capability above is host-agnostic and ready. **The current host (Claude Code)
has no Feishu adapter connected.** `A.feishu` is **spec-complete but not runnable
here** until one is bound. Two paths, with an important coverage gap.

> **Decision (roadmap):**
> 1. **Short term** — adopt [`cso1z/Feishu-MCP`](https://github.com/cso1z/Feishu-MCP)
>    for **layer 2 (tasks) only**, with read-only enforced via Feishu **app
>    scopes** (the MCP itself cannot filter writes — see caveats below). Layers 1
>    and 3 stay `not run`, reported honestly in Coverage.
> 2. **Long term** — **build our own read-only Feishu MCP** to cover all three
>    surfaces (IM messages, tasks, doc @-mentions) the way the capability above
>    defines, with read-only enforced *at the MCP* (a tool filter like the Gmail
>    MCP's `--scopes`), not just at the app. When that exists it replaces the
>    short-term adapter and `A.feishu` becomes fully runnable.
>
> Comparison of off-the-shelf options is below; both inform what the eventual
> in-house MCP should and shouldn't do.

### Candidate MCP — `cso1z/Feishu-MCP` (partial: tasks only)

[`cso1z/Feishu-MCP`](https://github.com/cso1z/Feishu-MCP) (actively maintained,
TypeScript, `feishu-app-id`/`secret`, `--enabled-modules`, also ships a
`feishu-tool` CLI). It is a **docs + tasks** server — **it does not cover IM
messages**. Mapping against our layers:

| layer | this MCP | verdict |
| --- | --- | --- |
| 1 message (DM / @me) | — no IM tools at all | ✗ **not covered** |
| 2 task | `list_feishu_tasks` ("我负责的任务") | ✓ covered |
| 3 doc-mention | doc read/search (`get_feishu_document_blocks`, `search_feishu_documents`) but **no direct "@me" / comment query** | 🟡 only by working around |

So this MCP can satisfy **layer 2 today**, approximate layer 3, and **cannot do
layer 1** — which is Feishu's heaviest surface. Treat it as a *task* adapter, not
a full one.

Two caveats to honor:

- **Read-only is NOT enforceable at the MCP here.** Its task/doc tools are full
  CRUD (`create`/`update`/`delete_feishu_task`, doc edits). `--enabled-modules`
  limits *modules* (e.g. only `task`), but module ≠ read-only — enabling `task`
  still exposes write tools. Unlike the Gmail MCP's `--scopes` filter, this one
  has no read-only tool filter. So the read-only guarantee must come from the
  **Feishu app scopes** (grant only `…:readonly`; it supports
  `FEISHU_SCOPE_VALIDATION` to validate). Do not grant write scopes, and prefer
  pointing the collector only at the read tools.
- **Auth type must be `user`.** "Tasks I'm responsible for" needs `user` auth
  (acts as the owner), not `tenant` (the app's own identity).

### Full coverage — Feishu Open Platform API directly

For all three layers (especially layer 1 messages), the Open Platform API with a
custom app and per-surface **readonly** scopes:

- layer 1 → IM API (`im:message:readonly`, `im:chat:readonly`)
- layer 2 → Task API (`task:task:readonly`)
- layer 3 → Docs/Wiki + Comment API (`docx:document:readonly`,
  `drive:drive:readonly`, comment read scope)
- **Read-only enforcement:** request only `…:readonly` scopes when creating the
  app — write/complete/send are then unauthorized at the OAuth layer, same
  guarantee as `gmail`.

### Until connected

A run with `feishu.enabled: true` and no adapter must report `feishu: did not run
— no adapter connected` in Coverage. If only the task-MCP is wired, Coverage must
say so honestly, e.g. `feishu: tasks scanned → N; messages/docs not run — adapter
covers tasks only`. **Never** let a partial adapter read as full coverage. Per
the repo rule, wire this up only when the owner actually lives in Feishu enough to
need it — grow by being used.
