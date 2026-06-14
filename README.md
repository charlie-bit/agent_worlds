# agent_worlds

**English** · [中文](README.zh.md)

<p align="center">
  <img src="diagrams/concept.svg" alt="agent_worlds — two worlds of agents that serve me" width="860">
</p>

A personal collection of AI agents — recurring workflows and creative work,
distilled into reusable agents I can pick up at any time.

Every agent falls into one of two worlds:

| | **assistants** | **builders** |
|---|---|---|
| **Purpose** | Carry the work I already have | Create the things I want to make |
| **Faces** | My existing job & daily load | New projects & ideas |
| **Does** | Handles chores, collects unhandled items | Designs and decomposes projects |
| **In one line** | *Lighten the load* | *Build the future* |

- **assistants** — work helpers. They watch my inboxes, collect what needs
  attention (mentions, DMs, todos), and take routine work off my plate.
- **builders** — project agents. They turn rough ideas into buildable plans:
  product specs, game designs, and whatever I decide to make next.

## Structure

```
agent_worlds/
├── agents/
│   ├── assistants/                work helpers
│   │   └── secretary-agent/        inbox & todo collector
│   └── builders/                  project agents
│       ├── pm-agent/               rough idea → spec pack
│       └── game-agent/             game design & mechanics
└── diagrams/                      shared diagram assets + generators
```

## Agents

### assistants

| Agent | One line |
|-------|----------|
| [secretary-agent](agents/assistants/secretary-agent/) | Watches my inboxes and collects unhandled items so nothing slips. |

### builders

| Agent | One line |
|-------|----------|
| [pm-agent](agents/builders/pm-agent/) | Turns a rough product idea into a small, buildable spec pack. |
| [game-agent](agents/builders/game-agent/) | Turns a game idea into a design doc and core mechanics. |

## Conventions

These are the ground rules every agent follows — so the collection stays consistent as it grows.

1. **Directory name**: short and kebab-case, ending in `-agent` — e.g. `pm-agent`, `game-agent`, `secretary-agent`.
2. **README first line is the summary**: right under the H1 title, write one sentence describing the agent. Keep it short. That line is the single source of truth — the concept diagram reads it automatically. Anything detailed lives deeper in the README, not in that line.
3. **Two pieces per agent**: `README.md` (the agent, for both humans and the LLM) and a `<agent-name>-system/` directory (the methodology it operates on, e.g. `pm-system/`, `game-system/`, `secretary-system/` — named after the agent so its owner is obvious).
4. **Bilingual README**: every agent ships `README.md` (English) and `README.zh.md` (中文), with a language switcher on the first line of each.
5. **Diagram text is English only**; the diagram is generated, not drawn — run `python3 diagrams/generate_concept.py`. It scans `agents/` and pulls each summary from the English `README.md`. Never edit the diagram by hand.

## Adding a New Agent

1. Decide the world: **assistant** (helps with existing work) or **builder** (creates something new).
2. Create `agents/<world>/<name>-agent/`.
3. Add `README.md` + `README.zh.md` (short H1 + one-line summary on the first prose line) and a `<name>-system/` directory (the `<name>` without the `-agent` suffix — e.g. `pm-agent` → `pm-system/`). The `/new-agent` skill does all of this for you.
4. Run `python3 diagrams/generate_concept.py` to refresh the concept diagram, and add a row to the table above.
