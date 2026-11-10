# Model tiers

Roles ask for a tier, not a product. Map the tier to whatever tool you are running in.

| Tier | Use for | Do not use for |
|---|---|---|
| **light** | Locating files and symbols, extracting facts with citations, filling templates, summarising a run, simple mechanical edits | Design, anything ambiguous |
| **standard** | Implementing a work order, writing documents from an approved outline, running and reading checks | Architecture across many modules |
| **heavy** | Intake judgement on unclear requests, plans for M/L tasks, root-cause analysis after two failures, final review of risky work | Routine steps |

## Default tier per role

| Role | Tier | Notes |
|---|---|---|
| Admin | standard | heavy only for an L task or a request that is still unclear after one question round |
| Scout | light | |
| Planner | standard for S/M, heavy for L | |
| Lead | standard | large tasks only; one per workstream (`agents/lead.md`) |
| Builder | standard | light for mechanical work orders marked `mechanical: yes` |
| Verifier | standard | light when checks are a fixed command list |
| Pre-mortem | light | fresh session, one prompt (`core/admin.md` §3.3) |
| Reviewer | heavy | only L tasks or `risk: high`; same model, fresh session, blind first pass |

## Mapping per tool

Model line-ups change often. Check the mapping when you set the Factory up and correct this table; the tiers
above stay the same.

| Tool | light | standard | heavy | How roles run |
|---|---|---|---|---|
| Claude Code | Haiku | Sonnet | Opus | Subagents in `.claude/agents/` (already provided, model set per role) |
| Claude desktop/web app | Haiku | Sonnet | Opus | One chat per stage; pick the model in the model selector before starting it |
| Codex / ChatGPT | *fill in: smallest current model* | *fill in: default coding model* | *fill in: highest reasoning model* | Reads `AGENTS.md` natively; one session per stage |
| Cursor / other IDE agent | *fill in* | *fill in* | *fill in* | Point the agent at `AGENTS.md`; choose the model per chat |

All roles can run on one model family. Independence between maker and checker comes from fresh sessions and
from what each is shown, not from using a different vendor.

In tools with no subagents, a "role" is a new session that starts with: "Read AGENTS.md. Your role is <role>.
Your work order is runs/<id>/<file>."
