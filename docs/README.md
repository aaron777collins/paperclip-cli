# paperclip-cli Documentation

Full-featured CLI for the [Paperclip](https://github.com/paperclipai/paperclip) AI agent orchestration platform.

## Guides

- [Configuration & Status](configuration.md) — Server URL, auth token, environment variables
- [company](company.md) — Create and manage AI companies
- [agent](agent.md) — Hire agents, approval flow, roles, wakeup
- [goal](goal.md) — Company objectives
- [issue](issue.md) — Tasks and tickets; `in_progress` requires assignee
- [project](project.md) — Group issues and routines; cascade delete warning
- [routine](routine.md) — Recurring tasks; schedule/webhook/api triggers; no hard delete
- [approval](approval.md) — Board approval queue for agent hires
- [plugin](plugin.md) — Extend agent capabilities with plugins
- [heartbeat](heartbeat.md) — Agent activation history and run diagnostics
- [secret](secret.md) — Encrypted credentials for agents

## Quick Start

```bash
# Install
git clone https://github.com/aaron777collins/paperclip-cli.git
cd paperclip-cli && pip install -e .

# Configure
paperclip-cli configure --url http://localhost:3100
paperclip-cli status

# Create a company and hire agents
CO=$(paperclip-cli company create --name "AcmeCorp" --json | jq -r '.id')
paperclip-cli agent create --company "$CO" --name "CEO" --role ceo --title "Chief Executive Officer"
paperclip-cli agent create --company "$CO" --name "Engineer" --role general --title "Backend Engineer"

# Approve the general agent hire
paperclip-cli approval list --company "$CO"
paperclip-cli approval approve <approval-id>

# Create goals and issues
paperclip-cli goal create --company "$CO" --title "Launch v1.0"
paperclip-cli issue create --company "$CO" --title "Build auth system"
```

## Command Coverage

| Resource | `list` | `create` | `get` | `update` | `delete` | Extra |
|----------|:------:|:--------:|:-----:|:--------:|:--------:|-------|
| **company** | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **agent** | ✅ | ✅ | ✅ | ✅ | ✅ | `wakeup` |
| **goal** | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **issue** | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **project** | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **routine** | ✅ | ✅ | ✅ | ✅ | `archive`¹ | `trigger-add`, `triggers`, `runs`, `run` |
| **approval** | ✅ | — | — | — | — | `approve`, `reject` |
| **plugin** | ✅ | — | — | — | — | `examples`, `install` |
| **heartbeat** | ✅ | — | — | — | — | — |
| **secret** | ✅ | — | — | — | — | — |

> ¹ Routines cannot be hard-deleted. `archive` stops future runs. Delete the parent project to fully remove.
