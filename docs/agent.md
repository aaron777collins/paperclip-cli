# agent

Manage agents — the AI workers inside a company. Agents run tasks, process issues, and communicate with the Paperclip orchestration platform.

## Quick Example

```bash
# Hire a CEO (auto-approved)
paperclip-cli agent create --company "$CO" --name "CEO" --role ceo --title "Chief Executive Officer"

# Hire a general agent (requires board approval)
paperclip-cli agent create --company "$CO" --name "Engineer" --role general --title "Backend Engineer"

# Approve the hire
paperclip-cli approval list --company "$CO"
paperclip-cli approval approve <approval-id>

# Wake up an idle agent
paperclip-cli agent wakeup <agent-id>
```

---

## Adapters

Every agent needs an adapter — the runtime that actually executes work. Specify with `--adapter` on create.

| Adapter | Description | Best for |
|---------|-------------|----------|
| `claude_local` | **Claude Code CLI** (default, recommended) | Most agents |
| `codex_local` | OpenAI Codex CLI | Codex-specific workflows |
| `opencode_local` | OpenCode CLI | OpenCode users |
| `pi_local` | Pi coding agent | Pi workflows |
| `cursor` | Cursor IDE | IDE-integrated agents |
| `openclaw_gateway` | OpenClaw / Sophie gateway | Sophie/Hermes integration |
| `hermes_local` | Hermes local agent | Hermes workflows |

For `claude_local`, set the model with `--model`:

| Model | Use for |
|-------|---------|
| `claude-opus-4-6` | CEOs, architects, strategic roles (auto-default for CEO role) |
| `claude-sonnet-4-6` | Most workers — balanced speed/quality (default for general) |
| `claude-haiku-4-6` | High-volume, fast, low-cost tasks |


### ⚠️ Important: runtimeConfig vs adapterConfig

When using `claude_local`, the CLI automatically sets these in `runtimeConfig` (NOT `adapterConfig`):

| Field | Default | Description |
|-------|---------|-------------|
| `model` | `claude-sonnet-4-6` (CEO: `claude-opus-4-6`) | Claude model to use |
| `dangerouslySkipPermissions` | `true` | Skip Claude Code permission prompts (required for automation) |
| `maxTurnsPerRun` | `250` | Max tool-use turns before the run ends |
| `cwd` | (Paperclip sets this) | Working directory for the agent |
| `effort` | (not set) | Reasoning effort: `low`, `medium`, or `high` |

**Leave `adapterConfig: {}` empty** — Paperclip auto-populates it with the correct `instructionsFilePath` pointing to the agent's `AGENTS.md`. If you put `model` or `cwd` in `adapterConfig` it blocks this auto-setup and your agent instructions will be empty.

### Assignment Wakeup

When you assign an issue to an agent, **they wake up immediately** — no need to wait for their scheduled heartbeat. The agent receives `PAPERCLIP_WAKE_REASON=assignment` and `PAPERCLIP_TASK_ID=<issue-id>`.

---

## Roles

| Role | Description | Approval required? | `canCreateAgents` |
|------|-------------|:------------------:|:-----------------:|
| `ceo` | Top of org chart. Auto-approved on create. | No | Yes |
| `general` | Regular worker agent. Goes through board approval. | Yes | No |

---

## agent list

List all agents in a company.

```bash
paperclip-cli agent list --company <company-id>
paperclip-cli agent list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
            Agents (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Name       ┃ Role              ┃ Status           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ a1b2c3d4-e5f6-7890-abcd-ef0123456789 │ CEO        │ ceo               │ idle             │
│ b2c3d4e5-f6a7-8901-bcde-f01234567890 │ Engineer   │ general           │ pending_approval │
└──────────────────────────────────────┴────────────┴───────────────────┴──────────────────┘
```

### Agent Status Values

| Status | Meaning |
|--------|---------|
| `idle` | Agent is active and waiting for tasks |
| `pending_approval` | Hire is pending board approval |
| `active` | Currently processing a task |
| `paused` | Manually paused |

---

## agent create

Hire a new agent. CEOs are immediately active; general agents enter the board approval queue.

```bash
# Hire a CEO (auto-approved, gets opus model by default)
paperclip-cli agent create --company <company-id> --name "CEO" --role ceo --title "Chief Executive Officer"

# Hire a general agent (sonnet by default)
paperclip-cli agent create --company <company-id> --name "Engineer" --role general --title "Senior Backend Engineer"

# Specify adapter explicitly
paperclip-cli agent create --company <company-id> --name "Codex Worker" --adapter codex_local

# Use haiku for high-volume cheap tasks
paperclip-cli agent create --company <company-id> --name "Reporter" --adapter claude_local --model claude-haiku-4-6

# With budget cap ($50/month = 5000 cents)
paperclip-cli agent create --company <company-id> --name "Analyst" --role general --budget 5000
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--name` | Yes | — | Agent display name |
| `--role` | No | `general` | `general` or `ceo` |
| `--title` | No | — | Job title (display only) |
| `--adapter` | No | `claude_local` | Runtime adapter (see Adapters section above) |
| `--model` | No | `claude-sonnet-4-6` | Claude model (CEO auto-defaults to `claude-opus-4-6`) |
| `--max-turns` | No | `250` | Max turns per run (claude_local only) |
| `--reports-to` | No | — | Agent ID this agent reports to |
| `--budget` | No | — | Monthly budget cap in cents (e.g. `5000` = $50/month) |
| `--json` | No | false | Output created agent as JSON |

### Example Output

```
✓ Created agent Engineer (ID: b2c3d4e5-f6a7-8901-bcde-f01234567890)
  Status: pending_approval — approve with: paperclip-cli approval approve <approval-id>
```

### Error Cases

| Error | Cause |
|-------|-------|
| `422 Unprocessable Entity` | `--name` or `--company` missing |
| `404 Not Found` | Company ID not found |

---

## agent get

Get full details for a single agent.

```bash
paperclip-cli agent get <agent-id>
paperclip-cli agent get <agent-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `agent-id` | Yes | UUID of the agent |

### Example JSON Output

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "name": "CEO",
  "role": "ceo",
  "title": "Chief Executive Officer",
  "status": "idle",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "canCreateAgents": true,
  "monthlyBudgetCents": null,
  "reportsToAgentId": null,
  "adapterType": "process",
  "lastHeartbeatAt": "2026-03-27T10:05:00.000Z",
  "createdAt": "2026-03-01T12:00:00.000Z"
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `canCreateAgents` | `true` for CEO role |
| `monthlyBudgetCents` | Spend cap; `null` = unlimited |
| `adapterType` | How the agent runs (default: `process`) |
| `lastHeartbeatAt` | Last time agent checked in |

---

## agent update

Update an agent's name, title, role, budget, or reporting relationship.

```bash
paperclip-cli agent update <agent-id> --title "Lead Engineer"
paperclip-cli agent update <agent-id> --name "CTO" --role ceo
paperclip-cli agent update <agent-id> --budget 5000
paperclip-cli agent update <agent-id> --reports-to <other-agent-id>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `agent-id` | Yes | UUID of the agent to update |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | No | — | New display name |
| `--title` | No | — | New job title |
| `--role` | No | — | New role: `general` or `ceo` |
| `--reports-to` | No | — | Agent ID this agent reports to |
| `--budget` | No | — | Monthly budget in cents (`5000` = $50/month) |
| `--adapter` | No | `claude_local` | Runtime adapter (see Adapters section) |
| `--json` | No | false | Output updated agent as JSON |

### Example Output

```
✓ Updated agent a1b2c3d4-e5f6-7890-abcd-ef0123456789
```

---

## agent delete

Remove an agent from a company. This is permanent.

```bash
paperclip-cli agent delete <agent-id>
paperclip-cli agent delete <agent-id> --yes
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `agent-id` | Yes | UUID of the agent |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--yes` | No | false | Skip confirmation prompt |

### Example Output

```
✓ Deleted agent a1b2c3d4-e5f6-7890-abcd-ef0123456789
```

---

## agent wakeup

Send a wake-up signal to an idle agent so it checks its inbox and processes pending tasks.

```bash
paperclip-cli agent wakeup <agent-id>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `agent-id` | Yes | UUID of the agent to wake |

### Example Output

```
✓ Woke up agent a1b2c3d4-e5f6-7890-abcd-ef0123456789
```

### Error Cases

| Error | Cause |
|-------|-------|
| `Agent is not idle` | Agent must be in `idle` status to receive a wakeup |
| `404 Not Found` | Agent ID not found |

---

## API Gotchas

- **CEO agents** are auto-approved and immediately `idle`. They don't appear in the approval queue.
- **General agents** start as `pending_approval`. They won't process any tasks until approved via `paperclip-cli approval approve <id>`.
- `wakeup` only works when `status == "idle"`. If the agent is `active` or `paused`, the call returns an error.
- The `--budget` flag takes **cents**, not dollars. `5000` = $50.00/month.
- The `assigneeAgentId` field in issues/routines must match an agent in the same company.
