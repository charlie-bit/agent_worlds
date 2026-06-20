# Secretary — Config

This defines **where** the secretary looks and **what** it tracks (the source
registry), plus how each source is triaged. It is the secretary's equivalent of
a project registry: process is data, not prompt.

## The split: schema here, real IDs outside the repo

Real channel data (Slack user/channel IDs, Jira project keys, GitHub repos,
teammate names) is **personal/company data** and must **not** be committed to
this repo. It lives in an external registry file the owner controls:

```
~/.agent_worlds/secretary/registry.yaml      # default registry path
```

This file only defines the **schema** that registry must follow, plus a worked
example with placeholder IDs. At run time, the secretary reads the external
registry; if it is missing, it reports that and scans nothing.

## Capability vs adapter: this registry is host-agnostic

This registry declares **capabilities** — *what* to gather and *who/what* to
track (`tracked_people`, `monitored_channels`, `project_keys`, `repos`). It does
**not** say *how* the current host reaches a source. The "how" is a swappable
**adapter** the host resolves:

| capability (here, host-agnostic) | Claude Code adapter | Codex adapter (planned) |
| --- | --- | --- |
| `slack`  | MCP `slack`     | connector / Slack Web API |
| `jira`   | MCP `atlassian` | Jira REST API |
| `github` | MCP `github`    | `gh` CLI / GitHub REST API |

Never write a host-specific call (e.g. `mcp__slack__…`) into this registry.
Changing host swaps the adapter binding only — this file and the raw-item schema
the collectors emit stay unchanged.

## Registry schema

```yaml
# ~/.agent_worlds/secretary/registry.yaml
owner:
  slack_user_id: <my Slack user ID>     # used for "to:me" / "from:me" queries
  timezone: <IANA tz>                   # e.g. Asia/Hong_Kong — collectors compute the day's window in owner-local time

sources:
  slack:
    enabled: true
    tracked_people:                      # grouping only — NOT an inclusion filter
      - { name: <name>, user_id: <id>, group: <group label>, dm_channel: <id> }
    monitored_channels:
      - { name: <name>, channel_id: <id>, group: <group label> }
  jira:
    enabled: false
    project_keys: [<KEY>]                # tickets assigned to / watched by owner
  github:
    enabled: false
    repos: [<org/repo>]                  # PRs to review, issues mentioning owner

  # The source list is OPEN — add a block per source the owner uses. Each block
  # is host-agnostic config; the adapter (per host) decides how to fetch it.
  calendar:                              # adapter: local CLI (e.g. gws) / Calendar API
    enabled: false
  gmail:                                 # adapter: Gmail API (no MCP on current host)
    enabled: false
  feishu:                                # adapter: 飞书 open-platform API (TBD)
    enabled: false

# Topic tagging (optional): map keywords/channels to a project tag so the
# digest can group cross-channel chatter under one heading.
projects:
  - { id: <project-id>, keywords: [<kw>], channels: [<id>], people: [<name>] }
aliases:
  <old-tag>: <canonical-tag>
```

## Example (placeholder IDs — do not commit real ones)

```yaml
owner:
  slack_user_id: U000OWNER
  timezone: Asia/Hong_Kong

sources:
  slack:
    enabled: true
    tracked_people:
      - { name: Alice, user_id: U000ALICE, group: core, dm_channel: D000ALICE }
      - { name: Bob,   user_id: U000BOB,   group: core, dm_channel: D000BOB }
    monitored_channels:
      - { name: eng-general, channel_id: C000ENG, group: eng }
  jira:
    enabled: true
    project_keys: [PROJ]
  github:
    enabled: true
    repos: [acme/widget-api]

projects:
  - { id: widget, keywords: [widget, api], channels: [C000ENG], people: [Alice] }
aliases:
  widget-api: widget
```

## Per-source triage notes

- **Slack** — the heaviest inbox. Collect in layers: DMs to the owner, messages
  @-mentioning the owner, tracked people's activity, the owner's own outbound
  (to catch threads they're in). Deduplicate by message timestamp. Anyone who
  DM'd or tagged the owner appears in the digest even if untracked.
- **Jira** — tickets assigned to the owner or awaiting a status transition from
  them. Surface stale ones (assigned but untouched for N days) as `HIGH`.
- **GitHub** — PRs requesting the owner's review, issues mentioning them.
  A review request open > 1 day is `HIGH`.
- **Calendar** — today's agenda, meetings, meeting notes. Adapter is a local CLI
  (host-agnostic) or the Calendar API; not an MCP on the current host.
- **Gmail** — unread / awaiting-reply mail. No MCP on the current host; adapter
  is the Gmail API or a self-built fetch.
- **飞书 (Feishu)** — messages, todos, doc @-mentions. Adapter (open-platform
  API) still to be scoped.

## Adding a source

1. Add a block under `sources:` in the registry (host-agnostic capability).
2. Document its triage rule here.
3. Bind an **adapter** for the current host (how it's actually fetched) — see the
   capability-vs-adapter table above; this binding lives with the host, not here.

Only add a source the owner actually uses — this grows by being used.
