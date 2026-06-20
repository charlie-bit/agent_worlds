# Triage — B

> **module:** `B` · **consumes:** raw item (`item_schema.md`) · **emits:** topic (`item_schema.md`)

The secretary's value lives here. Collection is mechanical; triage is the part
that turns a pile of raw items into a short, ranked list of topics a human can
act on. B is **source-agnostic** — it reads the raw-item contract and never
branches on which collector produced an item.

```
A.* ──raw items──▶  B (merge → cluster → tag → group → rank → route)  ──topics──▶ C
```

## Input

The merged list of raw items from **all** enabled collectors. B must not
hardcode how many sources there are — it processes whatever arrives. If a
collector returned nothing or failed, that is recorded in Coverage (B does not
invent items, and does not hide a gap).

## Step 1 — Merge & dedupe

Collapse raw items with the same `dedup_key` (the same Slack message hit by two
layers, the same ticket seen twice). When merging duplicates:

- Keep the **most obligation-heavy** `relation`: `action_required` >
  `waiting_on_me` > `fyi`.
- Keep the **richest** `raw_text` (e.g. the thread-expanded version).
- Union the rest (a `link` is enough; pick the canonical permalink).

Dedupe is by key only — no text comparison, no source knowledge. That is exactly
why the collector stamps `dedup_key`.

## Step 2 — Cluster into topics

Group related raw items into one **topic** (the digest's display unit). Cluster
when items are about the same subject:

- **Same thread** → same topic (a Slack `dedup_key` sharing a thread root, items
  with the same ticket/PR id).
- **Same subject across sources** → same topic (a Jira ticket + the Slack thread
  discussing it + the GitHub PR that closes it are one topic, not three).
- Use **semantic** understanding of `raw_text`, not just keyword overlap.

A topic's `items[]` is the raw items it was clustered from — the backlink that
proves the topic is grounded, traceable to original `link`s.

## Step 3 — Tag (project) — borrowed priority ladder

Assign each topic an optional project `tag`, using the registry's `projects:`
(`channels` / `keywords` / `people`) and `aliases`. Apply in **this order**, most
reliable signal first — a deterministic ladder, not a guess:

1. **Channel match** — any item's `context` is a channel listed under a project's
   `channels` → tag it. (Strongest: the owner curated that mapping.)
2. **Keyword match** — any item's `title`/`raw_text` contains a project's
   `keywords` (case-insensitive) → tag it.
3. **Person-primary match** — an item's `who` is in a project's `people` **and**
   no project matched by channel/keyword → tag it. (Weakest: people work across
   projects, so this only breaks ties.)
4. **Multi-match** — if several projects match, pick the one with the most
   signals, weighting **channel > keyword > person**.
5. **Alias resolution** — if the chosen tag is a key in `aliases`, redirect to
   the canonical tag.
6. **Untagged** — if nothing matches confidently, leave `tag` empty. Do **not**
   force a tag; an untagged topic is fine and still appears in the digest.

> Most-reliable-signal-first keeps tagging deterministic, not a guess. The signals
> come from the registry (`config.md`), never hardcoded here.

## Step 4 — Group

Set the topic's `group` (VIP / team / project section) from the registry, via the
items' `context`:

- Channel item → look up `monitored_channels[].group`.
- DM item (no `context`) → group by `who` via `tracked_people[].group`; if the
  sender is untracked, the topic belongs to **Others (DM/Tag)** — included, never
  dropped (the registry decides grouping, not inclusion).

`group` (where it shows in the digest) and `tag` (which project it concerns) are
independent axes — a topic can be `group: VIP` and `tag: widget` at once.

## Step 5 — Rank priority

Every topic gets `HIGH` / `MED` / `LOW`. Priority is driven primarily by
`relation` (source-agnostic), then adjusted by signal:

| priority | when |
| --- | --- |
| `HIGH` | any item is `action_required`, or `waiting_on_me` **and** aging/blocking (an @-mention left unanswered, a review request open > 1 day, a ticket assigned days ago) |
| `MED` | relevant FYI — a tracked person / shared project moved; `waiting_on_me` that is fresh and low-stakes |
| `LOW` | purely informational; safe to skim |

Tie-breaker rule of thumb (from the source skill): a one-off blip is `LOW`, a
drumbeat across the day/period is higher. Company-wide / HR / personal-chat noise
is deprioritized to an "Other Notes" tail, never `HIGH`.

## Step 6 — Route to sections

The digest's top sections come straight from `relation` — no source branching:

- `action_required` items → **Action Items**
- `waiting_on_me` items → **Waiting On Me**
- everything → its `### {source}` block under **Sources**, grouped by `group`.

This is precisely why `relation` is a first-class field on the raw item: B routes
on it without knowing or caring whether the item came from Slack, Jira, or GitHub.

## Output

A list of **topics** (shape in `item_schema.md`): `title`, `summary` (1–2 lines),
`priority`, `group`, `tag`, `participants`, `items[]`. C renders these via
`digest_template.md`, sorted `HIGH → MED → LOW`.

## Invariants

- **Source count is never hardcoded.** Adding a collector adds raw items B
  already knows how to handle — B does not change.
- **Never silently drop.** A direct DM/mention from an untracked person still
  produces a topic (in Others). Ambiguous priority → keep the item, flag the
  uncertainty, lean higher.
- **Coverage is honest.** "No results" and "did not run" stay distinguishable
  through to the digest; B never papers over a collector that failed.
