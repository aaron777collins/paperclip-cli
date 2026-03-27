# paperclip-cli

A full-featured Python CLI for [Paperclip](https://github.com/paperclipai/paperclip) — the open-source AI agent orchestration platform.

Manage your AI companies, agents, goals, issues, board approvals, and plugins entirely from the terminal.

## 📚 Full Documentation

Detailed per-command docs with option tables, example outputs, and API gotchas:

**[https://aaron777collins.github.io/paperclip-cli/](https://aaron777collins.github.io/paperclip-cli/)**

Or browse locally in the [`docs/`](docs/) folder:
[company](docs/company.md) · [agent](docs/agent.md) · [goal](docs/goal.md) · [issue](docs/issue.md) · [project](docs/project.md) · [routine](docs/routine.md) · [approval](docs/approval.md) · [plugin](docs/plugin.md) · [heartbeat](docs/heartbeat.md) · [secret](docs/secret.md)

---

## Command Coverage at a Glance

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

> ¹ The Paperclip API has no hard-delete for routines. `routine archive` sets status=`archived` to stop all future runs. To fully remove, delete the parent project.

Every command supports `--json` for machine-readable output and `-h`/`--help` for usage info.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Commands Reference](#commands-reference)
  - [status](#status)
  - [company](#company)
  - [agent](#agent)
  - [goal](#goal)
  - [issue](#issue)
  - [project](#project)
  - [routine](#routine)
  - [approval](#approval)
  - [plugin](#plugin)
  - [heartbeat](#heartbeat)
  - [secret](#secret)
- [JSON Output](#json-output)
- [Environment Variables](#environment-variables)
- [Tips & Patterns](#tips--patterns)

---

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

---

## Quick Start

```bash
# 1. Point the CLI at your Paperclip server (one-time setup)
paperclip-cli configure --url http://localhost:3100

# 2. Verify it can reach the server
paperclip-cli status

# 3. Create your first company
paperclip-cli company create --name "AcmeCorp" --description "My first AI company"

# 4. Grab the company ID
paperclip-cli company list

# 5. Hire a CEO (auto-approved, can create other agents)
paperclip-cli agent create --company <company-id> --name "CEO" --role ceo --title "Chief Executive Officer"

# 6. Hire a general agent
paperclip-cli agent create --company <company-id> --name "Engineer" --role general --title "Backend Engineer"

# 7. Approve the hire from the board queue
paperclip-cli approval list --company <company-id>
paperclip-cli approval approve <approval-id>

# 8. Create a goal and track work
paperclip-cli goal create --company <company-id> --title "Launch v1.0"
paperclip-cli issue create --company <company-id> --title "Build auth system"
```

---

## Configuration

Configure the CLI once with your server URL (and optionally an auth token):

```bash
paperclip-cli configure --url http://localhost:3100
# With auth token (for authenticated/private mode servers):
paperclip-cli configure --url https://paperclip.example.com --token my-secret-token
```

Config is saved to `~/.config/paperclip-cli/config.json`.

You can also use environment variables (override the saved config):

```bash
export PAPERCLIP_URL=http://localhost:3100
export PAPERCLIP_TOKEN=your-token
```

Or pass flags directly on any command:

```bash
paperclip-cli --url http://localhost:3100 company list
```

---

## Commands Reference

All commands support `-h` / `--help`. Running a command group with no subcommand also shows help:

```bash
paperclip-cli --help
paperclip-cli company        # shows company subcommands
paperclip-cli agent --help
```

---

### status

Check that the Paperclip server is reachable and healthy.

```bash
paperclip-cli status
paperclip-cli status --json
```

**Example output:**
```
✓ Paperclip is healthy
  URL:  http://localhost:3100
  Version: 2026.325.0
  Mode: local_trusted
```

---

### company

Manage your AI companies. Each company is an isolated org with its own agents, goals, issues, and budget.

#### `company list`

List all companies on the server.

```bash
paperclip-cli company list
paperclip-cli company list --json
```

#### `company create`

Create a new company.

```bash
paperclip-cli company create --name "AcmeCorp"
paperclip-cli company create --name "AcmeCorp" --description "AI-powered operations platform"
paperclip-cli company create --name "AcmeCorp" --description "..." --mission "Automate business ops"
```

| Option | Required | Description |
|--------|----------|-------------|
| `--name` | ✅ | Company name |
| `--description` | No | Short description |
| `--mission` | No | Mission statement |
| `--json` | No | Output raw JSON |

#### `company get`

Get full details for one company.

```bash
paperclip-cli company get <company-id>
paperclip-cli company get 6ef9c662-776f-43e0-8e7e-55f36c309edb --json
```

#### `company update`

Update a company's name, description, or mission.

```bash
paperclip-cli company update <company-id> --name "New Name"
paperclip-cli company update <company-id> --description "Updated description" --mission "New mission"
```

| Option | Description |
|--------|-------------|
| `--name` | New company name |
| `--description` | New description |
| `--mission` | New mission statement |

#### `company delete`

Permanently delete a company and all its data.

```bash
paperclip-cli company delete <company-id> --yes
# Without --yes, you'll be prompted to confirm
paperclip-cli company delete <company-id>
```

> ⚠️ This is irreversible. All agents, goals, and issues will be deleted.

---

### agent

Manage agents (the AI workers) inside a company.

**Roles:**
- `ceo` — Auto-approved. Has `canCreateAgents: true`. Sits at the top of the org chart.
- `general` — Regular agent. Requires board approval before becoming active.

#### `agent list`

List all agents in a company.

```bash
paperclip-cli agent list --company <company-id>
paperclip-cli agent list --company <company-id> --json
```

Shows: ID, name, role, status (idle / pending_approval / active / paused).

#### `agent create`

Hire a new agent. CEOs are auto-approved; general agents go to the board approval queue.

```bash
# Hire a CEO
paperclip-cli agent create --company <company-id> --name "CEO" --role ceo --title "Chief Executive Officer"

# Hire a general agent
paperclip-cli agent create --company <company-id> --name "Engineer" --role general --title "Senior Backend Engineer"
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--company` | ✅ | — | Company ID |
| `--name` | ✅ | — | Agent name |
| `--role` | No | `general` | `general` or `ceo` |
| `--title` | No | — | Job title (display only) |

#### `agent get`

Get full details for one agent.

```bash
paperclip-cli agent get <agent-id>
paperclip-cli agent get <agent-id> --json
```

Shows all fields: status, role, permissions, budget, adapter config, last heartbeat.

#### `agent update`

Update an agent's name, title, role, budget, or adapter config.

```bash
paperclip-cli agent update <agent-id> --title "Lead Engineer"
paperclip-cli agent update <agent-id> --name "CTO" --role ceo
paperclip-cli agent update <agent-id> --budget 5000   # $50.00/month in cents
```

| Option | Description |
|--------|-------------|
| `--name` | New name |
| `--title` | New job title |
| `--role` | New role (`general` or `ceo`) |
| `--reports-to` | Agent ID this agent reports to |
| `--budget` | Monthly budget cap in cents (e.g. `5000` = $50/month) |
| `--adapter-type` | Adapter type (default: `process`) |

#### `agent delete`

Remove an agent from a company.

```bash
paperclip-cli agent delete <agent-id> --yes
```

#### `agent wakeup`

Send a wake-up signal to an idle agent so it checks its inbox and processes pending tasks.

```bash
paperclip-cli agent wakeup <agent-id>
```

> Note: Only works when the agent's status is `idle`. Active or paused agents will return an error.

---

### goal

Goals are high-level objectives for a company. Issues/tasks are attached to goals.

#### `goal list`

List all goals for a company.

```bash
paperclip-cli goal list --company <company-id>
paperclip-cli goal list --company <company-id> --json
```

#### `goal create`

Create a new goal.

```bash
paperclip-cli goal create --company <company-id> --title "Reach $10k MRR"
paperclip-cli goal create --company <company-id> --title "Reach $10k MRR" --description "By end of Q2 2026"
```

| Option | Required | Description |
|--------|----------|-------------|
| `--company` | ✅ | Company ID |
| `--title` | ✅ | Goal title |
| `--description` | No | Longer description |

#### `goal update`

Update a goal's title, description, or status.

```bash
paperclip-cli goal update <goal-id> --title "Reach $20k MRR"
paperclip-cli goal update <goal-id> --status completed
```

#### `goal delete`

Delete a goal.

```bash
paperclip-cli goal delete <goal-id> --yes
```

---

### issue

Issues are tasks/tickets that agents work on. They can be attached to a goal.

#### `issue list`

List all issues for a company.

```bash
paperclip-cli issue list --company <company-id>
paperclip-cli issue list --company <company-id> --status backlog
paperclip-cli issue list --company <company-id> --status in_progress --json
```

| Option | Description |
|--------|-------------|
| `--company` | ✅ Company ID |
| `--status` | Filter by status: `backlog`, `todo`, `in_progress`, `done`, `cancelled` |

#### `issue create`

Create a new issue/task, optionally linked to a goal.

```bash
paperclip-cli issue create --company <company-id> --title "Implement login flow"
paperclip-cli issue create --company <company-id> --title "Fix signup bug" --description "Users can't sign up with Gmail" --goal <goal-id>
```

| Option | Required | Description |
|--------|----------|-------------|
| `--company` | ✅ | Company ID |
| `--title` | ✅ | Issue title |
| `--description` | No | Detailed description |
| `--goal` | No | Goal ID to attach this issue to |

#### `issue update`

Update an issue's title, description, status, or assignee.

```bash
paperclip-cli issue update <issue-id> --status done
paperclip-cli issue update <issue-id> --title "Fix signup bug (Gmail)" --status done
# in_progress requires an assignee:
paperclip-cli issue update <issue-id> --status in_progress --assignee <agent-id>
```

| Option | Description |
|--------|-------------|
| `--title` | New title |
| `--description` | New description |
| `--status` | New status: `backlog`, `todo`, `in_progress`, `done`, `cancelled` |
| `--assignee` | Agent ID to assign the issue to (⚠️ required when setting `in_progress`) |

> **Note:** Setting `--status in_progress` requires `--assignee <agent-id>` — the API enforces that in-progress issues must have an assignee.

#### `issue delete`

Delete an issue.

```bash
paperclip-cli issue delete <issue-id> --yes
```

---

### approval

The board approval queue. When a general agent is hired (or other governed actions occur), they appear here as pending approvals. You must approve them before the agent becomes active.

#### `approval list`

List all pending (and past) approvals for a company.

```bash
paperclip-cli approval list --company <company-id>
paperclip-cli approval list --company <company-id> --json
```

Shows: ID, type (e.g. `hire_agent`), status (`pending` / `approved` / `rejected`), requested by.

#### `approval approve`

Approve a pending action (e.g. hire an agent).

```bash
paperclip-cli approval approve <approval-id>
```

Once approved, the agent's status changes from `pending_approval` to `idle` and they become active.

#### `approval reject`

Reject a pending action.

```bash
paperclip-cli approval reject <approval-id>
```

---

### plugin

Manage Paperclip plugins that extend agent capabilities.

#### `plugin list`

List currently installed plugins.

```bash
paperclip-cli plugin list
paperclip-cli plugin list --json
```

#### `plugin examples`

Browse available example plugins from the Paperclip registry.

```bash
paperclip-cli plugin examples
paperclip-cli plugin examples --json
```

#### `plugin install`

Install a plugin by name or URL.

```bash
paperclip-cli plugin install <name-or-url>
```

---

## JSON Output

Every read command supports `--json` for clean machine-readable output — great for scripting, piping to `jq`, or agent automation:

```bash
# Get a company ID by name
paperclip-cli company list --json | jq -r '.[] | select(.name=="AcmeCorp") | .id'

# List all pending approvals across all companies
paperclip-cli company list --json | jq -r '.[].id' | while read id; do
  echo "=== $id ==="
  paperclip-cli approval list --company $id --json | jq '.[] | select(.status=="pending")'
done

# Check all agent statuses
paperclip-cli agent list --company <id> --json | jq '.[] | {name, status, role}'
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PAPERCLIP_URL` | Server URL (overrides saved config) |
| `PAPERCLIP_TOKEN` | Auth token (overrides saved config) |

```bash
PAPERCLIP_URL=http://localhost:3100 paperclip-cli company list
```

---

## Tips & Patterns

### Get IDs quickly

Use `--json` + `jq` to grab IDs without copying from tables:

```bash
# Company ID
COMPANY=$(paperclip-cli company list --json | jq -r '.[] | select(.name=="AcmeCorp") | .id')

# Agent ID
AGENT=$(paperclip-cli agent list --company "$COMPANY" --json | jq -r '.[] | select(.name=="CEO") | .id')
```

### Approve all pending hires at once

```bash
COMPANY=<company-id>
paperclip-cli approval list --company $COMPANY --json \
  | jq -r '.[] | select(.status=="pending") | .id' \
  | while read id; do paperclip-cli approval approve $id; done
```

### Bootstrap a new company end-to-end

```bash
# Create company
CO=$(paperclip-cli company create --name "NewCo" --description "New AI company" --json | jq -r '.id')

# Hire CEO (auto-approved)
paperclip-cli agent create --company $CO --name "CEO" --role ceo --title "Chief Executive Officer"

# Hire some agents
paperclip-cli agent create --company $CO --name "Engineer" --role general --title "Backend Engineer"
paperclip-cli agent create --company $CO --name "Designer" --role general --title "Product Designer"

# Approve all pending hires
paperclip-cli approval list --company $CO --json \
  | jq -r '.[] | select(.status=="pending") | .id' \
  | while read id; do paperclip-cli approval approve $id; done

# Set a goal
paperclip-cli goal create --company $CO --title "Ship MVP" --description "First working product"

echo "Done! Company $CO is running."
```

---

## License

MIT
