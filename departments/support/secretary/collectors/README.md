# Secretary — Collectors

One file per source. A collector is module **A** in the pipeline:

```
A. collectors  ──raw item──▶  B. triage  ──topic──▶  C. digest md
```

## The contract every collector honors

Each collector scans one source for a date and emits a list of **raw items** —
the exact shape pinned in `../item_schema.md`. That shared shape is the whole
point: B never branches on which source an item came from, so adding a collector
never touches B or C.

## What a collector spec must define

1. **Capability** — *what* it gathers, in plain terms ("Slack DMs and @-mentions
   to the owner"). Host-agnostic; never a host-specific call.
2. **Query layers** — how it sweeps the source (e.g. Slack's DM / mention /
   tracked-people / outbound layers).
3. **Field mapping** — how each raw result fills the raw-item fields, including
   the `relation` it judges (`action_required` / `waiting_on_me` / `fyi`) and a
   source-correct `dedup_key`.
4. **Dedup key** — the source's natural unique id (Slack `ts`, Jira issue key,
   GitHub PR/issue number), so B can collapse duplicates without reading text.
5. **Adapter binding** — *how* the current host actually fetches it (Claude Code
   → MCP; Codex → connector; script → REST). This is the only host-specific part
   and lives at the bottom of the spec, clearly fenced off.

## Rules (inherited from `../agent.md`)

- **Read-only.** Scan and report; never reply, react, or mark-as-read.
- **Sources are config.** Real IDs live in the external registry (`../config.md`
  points to it), never in these specs.
- **Never silently drop or skip.** Report what was scanned and what found nothing
  vs. failed — the digest's Coverage line depends on it.

## Status

| collector | capability | adapter (Claude Code) | spec |
| --- | --- | --- | --- |
| `slack`  | DMs / @-mentions / tracked-people / outbound | MCP `slack`     | `slack.md` ✅ |
| `jira`   | assigned / awaiting-transition / stale       | MCP `atlassian` | TODO |
| `github` | review-requested PRs / @-mention issues      | MCP `github`    | TODO |
| `gmail`  | unread / awaiting-reply mail                 | Gmail MCP (read-only scope) — not yet connected | `gmail.md` ✅ |
| `feishu` | messages / tasks / doc @-mentions            | interim: `cso1z/Feishu-MCP` (tasks only); long-term: build own read-only Feishu MCP (all 3 surfaces) | `feishu.md` ✅ |
