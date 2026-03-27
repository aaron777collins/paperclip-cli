# paperclip-cli Documentation

Full-featured CLI for the [Paperclip](https://github.com/paperclipai/paperclip) AI agent orchestration platform. Manage companies, agents, goals, issues, projects, routines, approvals, plugins, heartbeats, and secrets — entirely from the terminal.

## Quick Start

```bash
# Install
git clone https://github.com/aaron777collins/paperclip-cli.git
cd paperclip-cli && pip install -e .

# Point at your server
paperclip-cli configure --url http://localhost:3100

# Verify connection
paperclip-cli status

# Create a company and hire a CEO
CO=$(paperclip-cli company create --name "AcmeCorp" --json | jq -r '.id')
paperclip-cli agent create --company "$CO" --name "CEO" --role ceo --title "Chief Executive Officer"
```

## Installation

**From source (recommended while in development):**

```bash
git clone https://github.com/aaron777collins/paperclip-cli.git
cd paperclip-cli
pip install -e .
```

**Via pip (when published):**

```bash
pip install paperclip-cli
```

## Global Flags

These flags work on every command:

| Flag | Description |
|------|-------------|
| `--url <url>` | Override server URL for this invocation |
| `--token <token>` | Override auth token for this invocation |
| `--json` | Output raw JSON (great for scripting with `jq`) |
| `-h` / `--help` | Show help for any command or subcommand |

## Command Reference

| Command group | What it manages |
|---------------|-----------------|
| [configure](configuration.md) | Server URL and auth token |
| [status](configuration.md#status) | Server health check |
| [company](company.md) | AI companies (isolated orgs) |
| [agent](agent.md) | Agents (AI workers) inside a company |
| [goal](goal.md) | High-level company objectives |
| [issue](issue.md) | Tasks/tickets agents work on |
| [project](project.md) | Containers grouping issues and routines |
| [routine](routine.md) | Recurring scheduled/webhook/manual tasks |
| [approval](approval.md) | Board approval queue for agent hires |
| [plugin](plugin.md) | Plugins extending agent capabilities |
| [heartbeat](heartbeat.md) | Agent activation history |
| [secret](secret.md) | Encrypted agent credentials |

## Coverage at a Glance

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

> ¹ Routines cannot be hard-deleted via the API. `archive` sets `status=archived` to stop future runs. To fully remove, delete the parent project.

Every command supports `--json` for machine-readable output and `-h`/`--help` for usage.
