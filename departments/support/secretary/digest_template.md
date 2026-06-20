# Secretary — Digest Template

The shape of a digest. A human reads it top to bottom; the most actionable things
come first. The same template serves every cadence — only the period and the
inputs change (see **Cadence & aggregation** below).

## Files & naming (sortable, aggregation-ready)

```
outbox/
  2026-06-21-digest.md          # daily   — the atomic unit
  2026-W25-weekly.md            # weekly  — rolls up that ISO week's dailies
  2026-06-monthly.md            # monthly — rolls up that month's dailies (top cadence)
```

- Dates are always **`YYYY-MM-DD`** (ISO, zero-padded) so filenames sort
  chronologically and a roll-up can glob a date range deterministically.
- A daily is produced from live sources. A **roll-up consumes the lower-cadence
  digests already in `outbox/`** — weekly reads that week's dailies, monthly reads
  the weeklies (or dailies). Monthly is the top cadence; there is no yearly report
  (twelve monthlies are easy to skim — rolling further adds little). The
  filesystem is the message bus.

## Rules

- Sort every list by priority: `HIGH` → `MED` → `LOW`.
- Skip a section entirely if it has no items (except **Coverage**, always shown).
- **Stable headers.** Section titles are fixed strings (`## Action Items`,
  `## Waiting On Me`, …). Roll-ups parse dailies by these headers — do not rename
  or localize them.
- **Fixed topic line:** `- [PRIORITY] **{Topic}** — {1–2 line summary} ({participants})`.
  This shape is what a roll-up dedupes and merges on.
- **Source sections are open, not hardcoded.** Render one `### {source}` block
  per *enabled* source in the registry (Slack, Jira, GitHub, Calendar, Gmail,
  Feishu, …). Adding a source must not require editing this template.
- Group headings within a source (VIP / team / project) come from the registry.
- **Privacy guardrail.** Excerpts of message text are allowed (they keep triage
  accurate), but **never** paste credentials, tokens, API keys, or full secrets
  even if a source contains them — summarize and link instead. The whole digest
  is local-only (`outbox/` is gitignored).

## Daily digest

```markdown
# Secretary Digest — {YYYY-MM-DD}

## Action Items
- [ ] {what the owner must do} → {source/link}
{Consolidated from all sources, highest priority first. Empty section omitted.}

## Waiting On Me
- [HIGH] **{where}** — {who, context} → {link} **[ACTION: what to do]**
{Anything that @-mentions or DMs the owner. Untracked senders included here.}

## Sources
{One `### {source}` block per enabled source. Order: heaviest inbox first.}

### Slack
#### {Group A, e.g. VIP}
- [HIGH] **{Topic}** — {summary} ({participants})
- [MED] **{Topic}** — {summary} ({participants})
#### Others (DM / Tag)
- [MED] **{Topic}** — {summary} ({participants})
{People not in the tracked registry who DM'd or tagged the owner.}

### Jira
- [HIGH] **{KEY-123}** — {title}; {why it needs me, e.g. assigned 4d ago, no update}

### GitHub
- [HIGH] **PR #{n}** {title} — review requested {age} ({repo})
- [MED] **issue #{n}** {title} — mentions me ({repo})

{… more `### {source}` blocks for any other enabled source …}

## Coverage
{Always shown — proves nothing was silently skipped.}
- {source}: scanned {scope} → {K} items
- {source}: no results
- {source}: did not run — {reason: disabled / registry missing / scan failed}

## Summary
{2–3 sentences: what landed today, what needs the owner first, what can wait.}
```

## Cadence & aggregation

Higher-cadence digests reuse the **same section headers** but summarize instead
of list. A roll-up is itself a secretary run whose sources are the lower digests.

```markdown
# Secretary Digest — {period}        # e.g. "2026-W25 (Jun 16–22)" or "2026-06"

## Action Items
- [ ] {items still open at period end, oldest first} → {link}
{Carry forward anything unchecked in the dailies; drop what got done.}

## Themes
- [HIGH] **{recurring theme}** — {what kept coming up, across which days} ({who})
{Cluster the period's topics into themes; a one-day blip is LOW, a daily drumbeat is HIGH.}

## By Source
- **Slack**: {N topics, M action items; the one thing that mattered}
- **Jira**: {tickets opened/closed/stalled this period}
- {… per source …}

## Coverage
- Days covered: {list or count} of {expected}    # surfaces missed days
- {source}: {days it ran / total}

## Summary
{3–5 sentences: the shape of the period — what moved, what stalled, what to watch next.}
```

## Notes

- **Coverage is the anti-silent-failure section.** "No results" and "did not
  run" must read differently — never let an empty source look like a clean one.
  In roll-ups, Coverage also surfaces **missing days** so a gap in the record is
  visible, not silent.
- **Markdown is the canonical, diffable data base.** The intended human-facing
  view is an **HTML dashboard rendered from these `.md` files** by a small script
  (same pattern as `company.yaml → generate_concept.py → concept.svg`). That
  renderer is deferred until the markdown pipeline is solid. A machine-readable
  `.json` sibling is added only if a consumer that is not our own renderer
  appears — not before.
