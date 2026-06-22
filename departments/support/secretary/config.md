# Secretary — Config

Defines **where** the secretary looks and **what** it tracks, plus how each
source is triaged.

## Setup

Real IDs (Slack user/channel IDs, Jira project keys, GitHub repos) are
**personal data — never committed here**. They live in:

```
~/.agent_worlds/secretary/registry.yaml
```

Copy `registry.example.yaml` to that path and fill in your real IDs. At run
time the secretary reads that file; if it is missing it reports that and scans
nothing.

## Capability vs adapter

The registry declares **capabilities** — *what* to gather, not *how* the host
fetches it. The "how" is a swappable adapter:

| capability | Claude Code adapter | Codex (planned) |
| --- | --- | --- |
| `slack`  | MCP `slack`     | Slack Web API |
| `jira`   | MCP `atlassian` | Jira REST API |
| `github` | MCP `github`    | `gh` CLI |

Never write host-specific calls (e.g. `mcp__slack__…`) into the registry.
Changing host swaps the adapter only — the registry and item schema stay
unchanged.

## Per-source triage rules

- **Slack** — Collect in layers: DMs to owner, @-mentions, tracked people's
  activity, owner's outbound (to catch threads they're in). Deduplicate by
  message timestamp. Anyone who DM'd or tagged the owner appears in the digest
  even if untracked.
- **Jira** — Tickets assigned to or awaiting a transition from the owner.
  Stale tickets (assigned but untouched for N days) → `HIGH`.
- **GitHub** — PRs requesting the owner's review, issues mentioning them.
  Review request open > 1 day → `HIGH`.
- **Calendar** — Today's agenda and meetings. Adapter: local CLI or Calendar
  API (no MCP on current host).
- **Gmail** — Unread / awaiting-reply mail. Adapter: Gmail API or self-built
  fetch (no MCP on current host).
- **飞书 (Feishu)** — Messages, todos, doc @-mentions. Adapter: open-platform
  API (still to be scoped).

## Adding a source

1. Add a block under `sources:` in `registry.example.yaml` and your local
   registry.
2. Add its triage rule above.
3. Bind an adapter for the current host — that binding lives with the host,
   not here.

Only add a source the owner actually uses — this grows by being used.
