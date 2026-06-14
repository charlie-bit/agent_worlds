# agent_worlds

[English](README.md) · **中文**

<p align="center">
  <img src="diagrams/concept.svg" alt="agent_worlds — 服务于我的两个 agent 世界" width="860">
</p>

我自己的一套 AI agent 集合——把反复出现的工作流和创造流,
沉淀成随时可复用的 agent。

每个 agent 都归属于两大世界之一:

| | **assistants（工作小助手）** | **builders（业务/项目 agent）** |
|---|---|---|
| **目的** | 扛我已有的活 | 造我想做的东西 |
| **面向** | 现有工作 & 日常负荷 | 新项目 & 想法 |
| **做什么** | 处理杂事、收集未处理的事情 | 设计、拆解项目 |
| **一句话** | *减负* | *造未来* |

- **assistants** —— 工作小助手。盯着我的各类收件箱,收集需要关注的事情
  (@、DM、待办),把例行杂事从我手上接走。
- **builders** —— 项目 agent。把粗糙的想法变成可落地的方案:
  产品规范、游戏策划,以及我接下来决定要做的任何东西。

## 目录结构

```
agent_worlds/
├── agents/
│   ├── assistants/                工作小助手
│   │   └── secretary-agent/        收件箱 & 待办收集器
│   └── builders/                  项目 agent
│       ├── pm-agent/               粗糙想法 → 规范包
│       └── game-agent/             游戏设计 & 玩法
└── diagrams/                      共享图表资源 + 生成脚本
```

## Agents

### assistants（工作小助手）

| Agent | 一句话 |
|-------|--------|
| [secretary-agent](agents/assistants/secretary-agent/) | 盯着我的收件箱,收集未处理的事情,不让任何东西漏掉。 |

### builders（业务/项目 agent）

| Agent | 一句话 |
|-------|--------|
| [pm-agent](agents/builders/pm-agent/) | 把粗糙的产品想法变成小而可落地的规范包。 |
| [game-agent](agents/builders/game-agent/) | 把游戏想法变成设计文档和核心玩法。 |

## 基调约定

这是每个 agent 都要遵守的基本规矩——让集合越长越大也保持一致。

1. **目录名**:简洁、kebab-case、以 `-agent` 结尾——如 `pm-agent`、`game-agent`、`secretary-agent`。
2. **README 第一句就是简介**:在 H1 标题正下方写一句话描述这个 agent。务必简短。这句话是唯一事实来源——概念图会自动读取它。需要细节就写进 README 更下方,而不是这一句。
3. **每个 agent 两件套**:`README.md`(就是这个 agent,人和 LLM 都读它)+ 一个 `<agent-名>-system/` 目录(它赖以运作的方法论,如 `pm-system/`、`game-system/`、`secretary-system/`——按 agent 命名,一眼看出归属)。
4. **README 双语**:每个 agent 都有 `README.md`(英文)和 `README.zh.md`(中文),各自第一行带语言切换链接。
5. **图里文字只用英文**;图是生成的,不是手画的——运行 `python3 diagrams/generate_concept.py`,它扫描 `agents/` 并从英文 `README.md` 拉取简介。永远不要手动改图。

## 新增一个 Agent

1. 先定世界归属:**assistant**(帮已有的工作)还是 **builder**(创造新东西)。
2. 建目录 `agents/<world>/<name>-agent/`。
3. 加 `README.md` + `README.zh.md`(简洁 H1 + 第一句正文写一句话简介),以及一个 `<name>-system/` 目录(`<name>` 是去掉 `-agent` 后缀的部分——如 `pm-agent` → `pm-system/`)。`/new-agent` skill 会自动帮你做完这些。
4. 跑 `python3 diagrams/generate_concept.py` 刷新概念图,并在上方表格加一行。
