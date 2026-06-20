# CLAUDE.md — how to work in agent_worlds

> Read this before doing anything in this repo. It defines **the rules**
> (how the company is organized, how to add to it). For **what exists**, read
> `README.md`. For **how the company runs a job**, read `workflows/`.

## What this repo is

`agent_worlds` is a **one-person company of agents**. It is not (yet) a runtime —
it is the company's structure and method, kept as plain files:

```
company → department → role → agent
```

The org is declared once in `company.yaml`. Each role is a directory
`departments/<department>/<role>/` holding:

- `agent.md` — the role itself (who it is, what it does, its rules). Read by
  humans and by the LLM acting as that role.
- the methodology that role operates on (templates, checklists, config) — the
  role's own **playbook**. A role with several such artifacts MAY group them in a
  `playbook/` subdirectory (see `pm/`); a role with only a couple MAY keep them
  flat in the role directory (see `support/secretary/` — `config.md`,
  `digest_template.md`). Prefer flat until the count makes a subdirectory clearly
  worth it.

## The one rule that drives the design

**Process is data, not a prompt.** How the company turns an idea into a release
lives in `workflows/*.yaml` as declarative steps — never hardcoded into an
agent's system prompt. To change how the company works, edit the workflow.

A workflow step hands off to the next via **artifact files** (e.g. pm produces
`01_mvp_spec.md`, architect consumes it). The filesystem is the message bus.
There is no service, no daemon — a step can run when its `consumes` files exist.

## Single source of truth

- **Org structure** → `company.yaml`. The concept diagram reads it; nothing else
  defines the departments/roles.
- **A role's one-line summary** → its entry in `company.yaml`. The diagram pulls
  from there. Keep `agent.md`'s headline in sync, but `company.yaml` wins.
- **Diagrams are generated, never hand-edited** → run
  `python3 diagrams/generate_concept.py` after changing `company.yaml`.

## Conventions

1. **Role dir = role name**, kebab-case, no suffix: `pm/`, `architect/`, not
   `pm-agent/`. The department gives the namespace.
2. **`agent.md` opens with a role header**: `> **role:** ... · **department:** ...`
   then a one-line summary on the next prose line.
3. **English is the working language** inside role files (they're for the LLM).
   Bilingual lives only at the top-level `README` / `README.zh`.
4. **Stubs are allowed and labeled.** A role that only exists to let a workflow
   run end-to-end says `**status:** stub`. Flesh it out when a real job needs it —
   not before. (See `pm/agent.md` for the shape of a complete role.)

## Adding to the company

- **New role**: create `departments/<dept>/<role>/agent.md`, add it under that
  department in `company.yaml`, then regenerate the diagram.
- **New department**: add it to `company.yaml`, create the dir, add at least one
  role.
- **New workflow**: add `workflows/<name>.yaml`. Reuse existing roles; only add a
  role if no existing one fits.

## Stay lightweight

This company grows by being *used*, not by being *architected*. Do not add
services, registries, buses, or org layers ahead of a concrete need — when the
process is already expressible as files + a workflow, that is the answer.
