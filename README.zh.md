# agent_worlds

[English](README.md) · **中文**

<p align="center">
  <img src="diagrams/concept.svg" alt="agent_worlds — 一个人的 agent 公司" width="900">
</p>

**一个人的 agent 公司**——从粗糙的想法,到发布的功能。

`agent_worlds` 不是一堆松散的 agent,而是像一家公司一样组织起来:

```
公司 → 部门 → 角色 → agent
```

组织结构在 [`company.yaml`](company.yaml) 里声明一次。公司如何把想法变成发布,
是**数据,而不是 prompt**——它以声明式步骤的形式住在 [`workflows/`](workflows/) 里。

## 核心想法

大多数 agent 项目是一张扁平的 agent 清单。真正缺的不是更多 agent,而是**组织**:
谁做什么、按什么顺序、把什么交给谁。所以这个仓库把自己建模成一家公司:

- **部门(department)** 按职能聚合角色(`product`、`engineering`、`quality`、`support`)。
- **角色(role)** 是具体的岗位(`pm`、`architect`、`qa`…)。V1 里一个角色就是一个 agent。
- **工作流(workflow)** 把角色串成流水线。角色之间通过**产物文件**交接——
  文件系统就是消息总线。没有服务,没有常驻进程。

> **流程即数据。** 要改变公司怎么运作,就改 workflow YAML——而不是某个藏起来的 prompt。

## 目录结构

```
agent_worlds/
├── company.yaml          组织:部门 → 角色(单一事实来源)
├── CLAUDE.md             如何在本仓库工作(规则)
├── workflows/            公司如何跑一个任务(流程即数据)
│   └── software_feature.yaml
├── departments/
│   ├── product/          pm · researcher
│   ├── engineering/      architect · backend · web · game
│   ├── quality/          qa
│   └── support/          secretary
└── diagrams/             生成的组织图 + 流水线图(永不手改)
```

每个角色位于 `departments/<部门>/<角色>/`,含一个 `agent.md`(角色本体);
方法论文件可平铺,文件多时再归进 `playbook/`(它的方法论)。

## 默认工作流:`software_feature`

```
调研 → 需求确认 → 架构设计 → 构建(backend/web/game) → 测试 → 发布
 pm·researcher   pm★        architect        engineering        qa    pm★
```

★ = owner 确认点(`gate`)。每一步 `consumes`(消费)上游产物、`produces`(产出)
下游产物——例如 `pm` 写出 `01_mvp_spec.md`,`architect` 读它。
详见 [`workflows/software_feature.yaml`](workflows/software_feature.yaml)。

## 角色

| 部门 | 角色 | 状态 | 一句话 |
|---|---|---|---|
| product | [pm](departments/product/pm/agent.md) | active | 把粗糙的产品想法变成小而可落地的规范包。 |
| product | [researcher](departments/product/researcher/agent.md) | stub | 在锁定范围前调研问题空间。 |
| engineering | [architect](departments/engineering/architect/agent.md) | stub | 把锁定的 MVP 规范变成系统设计与 ADR。 |
| engineering | [backend](departments/engineering/backend/agent.md) | stub | 构建服务端逻辑、API 与数据。 |
| engineering | [web](departments/engineering/web/agent.md) | stub | 构建 Web 客户端。 |
| engineering | [game](departments/engineering/game/agent.md) | stub | 把游戏想法变成设计文档和核心玩法。 |
| quality | [qa](departments/quality/qa/agent.md) | stub | 对照验收标准校验交付物。 |
| support | [secretary](departments/support/secretary/agent.md) | stub | 盯着我的收件箱,收集未处理的事情。 |

> **stub 是有意的。** stub 角色的存在是为了让工作流能端到端跑通;
> 等真有任务需要时再充实它——不要提前。`pm` 是一个完整角色的参照样板。

## 基调约定

每次新增都遵守的基本规矩(完整版见 [`CLAUDE.md`](CLAUDE.md)):

1. **角色目录名 = 角色名**,kebab-case、无后缀(`pm/`,而不是 `pm-agent/`)。部门提供命名空间。
2. **`agent.md` 以角色头开头**(`> **role:** … · **department:** …`)加一句话简介。
3. **`company.yaml` 是组织的单一事实来源**。概念图读它——没有别处定义部门/角色。
4. **图是生成的,从不手画**——改完 `company.yaml` 后跑 `python3 diagrams/generate_concept.py`。
5. **双语只存在于顶层这里**;角色文件用英文(主要给 LLM 读)。

## 新增

- **新角色**:建 `departments/<部门>/<角色>/agent.md`,在 `company.yaml` 对应部门下加一行,重新生成图。
- **新部门**:在 `company.yaml` 里加它,建目录,至少加 1 个角色。
- **新工作流**:加 `workflows/<名字>.yaml`,尽量复用已有角色。

## 接下来往哪走

V1 刻意保持轻:文件 + 一个 workflow,没有 runtime。公司靠**被使用**而成长,
而不是被过度设计。一个薄薄的 orchestrator——真正去**执行** workflow(把每一步派给
对应角色、在 owner 确认点停下)——是自然的下一步,但只在结构配得上它之后才做。
