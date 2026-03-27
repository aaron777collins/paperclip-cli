# routine

Routines are recurring tasks assigned to an agent. They run on a schedule (cron), via HTTP webhook, or manually via the API/CLI. Each routine belongs to a project.

## Quick Example

```bash
# Create a routine
R=$(paperclip-cli routine create \
  --company "$CO" --project "$PROJ" \
  --name "Daily Standup" --assignee "$AGENT" \
  --json | jq -r '.id')

# Add a schedule trigger (9am UTC every weekday)
paperclip-cli routine trigger-add "$R" --kind schedule --cron "0 9 * * 1-5" --label "Weekday 9am"

# View triggers
paperclip-cli routine triggers "$R"

# Manually fire a run
paperclip-cli routine run "$R"

# View run history
paperclip-cli routine runs "$R"

# Archive when done (no hard delete)
paperclip-cli routine archive "$R" --yes
```

---

## No Hard Delete

> **Critical:** The Paperclip API does **not** support deleting routines. `routine archive` sets `status=archived` and stops all future runs. To fully remove a routine, delete its parent project (which cascades).

---

## routine list

List all routines for a company.

```bash
paperclip-cli routine list --company <company-id>
paperclip-cli routine list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
     Routines (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Title           ┃ Status      ┃ Concurrency        ┃ Assignee                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ b9c0d1e2-f3a4-5678-0123-456789012345 │ Daily Standup   │ active      │ coalesce_if_active │ a1b2c3d4-e5f6-7890-abcd-ef0123456789 │
│ c0d1e2f3-a4b5-6789-1234-567890123456 │ Weekly Report   │ active      │ coalesce_if_active │ a1b2c3d4-e5f6-7890-abcd-ef0123456789 │
└──────────────────────────────────────┴─────────────────┴─────────────┴────────────────────┴──────────────────────────────────────┘
```

---

## routine create

Create a new routine. Both `--project` and `--assignee` are required by the API.

```bash
paperclip-cli routine create \
  --company <company-id> \
  --project <project-id> \
  --name "Daily Standup" \
  --assignee <agent-id>

# With all options
paperclip-cli routine create \
  --company <company-id> \
  --project <project-id> \
  --name "Weekly Report" \
  --assignee <agent-id> \
  --description "Generate weekly progress report" \
  --priority high \
  --concurrency coalesce_if_active \
  --catchup skip_missed
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--project` | Yes | — | Project ID (routines must belong to a project) |
| `--name` | Yes | — | Routine title |
| `--assignee` | Yes | — | Agent ID to run this routine |
| `--description` | No | — | Description |
| `--goal` | No | — | Goal ID to link to |
| `--priority` | No | `medium` | `critical`, `high`, `medium`, `low` |
| `--status` | No | `active` | `active`, `paused`, `archived` |
| `--concurrency` | No | `coalesce_if_active` | What to do if a run is already active (see below) |
| `--catchup` | No | `skip_missed` | What to do with missed runs after downtime |
| `--json` | No | false | Output created routine as JSON |

### Concurrency Policies

| Policy | Behavior |
|--------|----------|
| `coalesce_if_active` | Skip new run if one is already active (default, safe) |
| `skip_if_active` | Same as coalesce but strictly no queuing |
| `always_enqueue` | Queue every triggered run regardless |

### Catch-up Policies

| Policy | Behavior |
|--------|----------|
| `skip_missed` | Ignore missed runs after downtime (default) |
| `enqueue_missed_with_cap` | Enqueue missed runs up to a cap |

### Example Output

```
✓ Created routine Daily Standup (ID: b9c0d1e2-f3a4-5678-0123-456789012345)
  Add a trigger: paperclip-cli routine trigger-add b9c0d1e2-... --kind schedule --cron "0 9 * * *"
```

### Error Cases

| Error | Cause |
|-------|-------|
| `422 Unprocessable Entity` | `--project` or `--assignee` missing |
| `404 Not Found` | Company, project, or agent ID not found |

---

## routine get

Get full details for a routine, including its triggers.

```bash
paperclip-cli routine get <routine-id>
paperclip-cli routine get <routine-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Example JSON Output

```json
{
  "id": "b9c0d1e2-f3a4-5678-0123-456789012345",
  "title": "Daily Standup",
  "status": "active",
  "priority": "medium",
  "concurrencyPolicy": "coalesce_if_active",
  "catchUpPolicy": "skip_missed",
  "assigneeAgentId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "projectId": "f7a8b9c0-d1e2-3456-f012-345678901234",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "triggers": [
    {
      "id": "d1e2f3a4-b5c6-7890-1234-567890123456",
      "kind": "schedule",
      "cronExpression": "0 9 * * 1-5",
      "timezone": "UTC",
      "enabled": true,
      "nextRunAt": "2026-03-28T09:00:00.000Z"
    }
  ]
}
```

---

## routine update

Update a routine's title, description, status, assignee, priority, or concurrency policy.

```bash
paperclip-cli routine update <routine-id> --name "Daily Check-in"
paperclip-cli routine update <routine-id> --status paused
paperclip-cli routine update <routine-id> --assignee <new-agent-id>
paperclip-cli routine update <routine-id> --concurrency always_enqueue
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | No | — | New title |
| `--description` | No | — | New description |
| `--status` | No | — | `active`, `paused`, `archived` |
| `--assignee` | No | — | New assignee agent ID |
| `--priority` | No | — | `critical`, `high`, `medium`, `low` |
| `--concurrency` | No | — | New concurrency policy |
| `--json` | No | false | Output updated routine as JSON |

---

## routine archive

Archive a routine to stop all future runs. There is no hard-delete.

```bash
paperclip-cli routine archive <routine-id>
paperclip-cli routine archive <routine-id> --yes
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--yes` | No | false | Skip confirmation |

### Example Output

```
✓ Archived routine b9c0d1e2-f3a4-5678-0123-456789012345 (no more runs will fire)
```

> To fully remove a routine, delete its parent project with `paperclip-cli project delete <project-id>`.

---

## routine trigger-add

Add a trigger to a routine. A routine can have multiple triggers.

```bash
# Schedule trigger (cron)
paperclip-cli routine trigger-add <routine-id> --kind schedule --cron "0 9 * * *"
paperclip-cli routine trigger-add <routine-id> --kind schedule --cron "0 9 * * 1-5" --timezone America/New_York --label "Weekdays 9am ET"

# Webhook trigger (generates an HTTP POST URL)
paperclip-cli routine trigger-add <routine-id> --kind webhook

# API/manual trigger
paperclip-cli routine trigger-add <routine-id> --kind api --label "Manual"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--kind` | Yes | — | `schedule`, `webhook`, or `api` |
| `--cron` | Conditional | — | Cron expression (required when `--kind schedule`) |
| `--timezone` | No | `UTC` | Timezone for cron (e.g. `America/New_York`) |
| `--label` | No | — | Human-readable label for this trigger |
| `--json` | No | false | Output created trigger as JSON |

### Cron Expression Examples

| Expression | Meaning |
|------------|---------|
| `0 9 * * *` | Daily at 9:00 AM UTC |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * 1` | Every Monday midnight |

### Example Output

```
✓ Added schedule trigger (ID: d1e2f3a4-b5c6-7890-1234-567890123456)
  Cron: 0 9 * * 1-5 (UTC)
  Next run: 2026-03-30T09:00:00.000Z
```

### Error Cases

| Error | Cause |
|-------|-------|
| `--cron is required for schedule triggers` | Forgot `--cron` with `--kind schedule` |
| `Invalid cron expression` | Malformed cron string |

---

## routine triggers

List all triggers for a routine.

```bash
paperclip-cli routine triggers <routine-id>
paperclip-cli routine triggers <routine-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Example Output

```
    Triggers for Routine (b9c0d1e2-…)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Kind       ┃ Enabled   ┃ Cron/Details ┃ Next Run            ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ d1e2f3a4-… │ schedule   │ ✅        │ 0 9 * * 1-5  │ 2026-03-30T09:00:00 │
└────────────┴────────────┴───────────┴──────────────┴─────────────────────┘
```

---

## routine run

Manually trigger a routine to run immediately (requires an `api` trigger to be configured, or works regardless in some server versions).

```bash
paperclip-cli routine run <routine-id>
paperclip-cli routine run <routine-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Example Output

```
✓ Triggered routine b9c0d1e2-f3a4-5678-0123-456789012345
{
  "runId": "e2f3a4b5-c6d7-8901-2345-678901234567",
  "status": "queued"
}
```

---

## routine runs

View the run history for a routine.

```bash
paperclip-cli routine runs <routine-id>
paperclip-cli routine runs <routine-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `routine-id` | Yes | UUID of the routine |

### Example Output

```
     Routine Runs (b9c0d1e2-…)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Status      ┃ Source    ┃ Triggered At        ┃ Linked Issue                         ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ e2f3a4b5-… │ completed   │ manual    │ 2026-03-27T10:00:00 │ e5f6a7b8-c9d0-1234-ef01-234567890123 │
│ f3a4b5c6-… │ completed   │ schedule  │ 2026-03-26T09:00:00 │ f6a7b8c9-d0e1-2345-f012-345678901234 │
└────────────┴─────────────┴───────────┴─────────────────────┴──────────────────────────────────────┘
```

### Run Fields

| Field | Description |
|-------|-------------|
| `status` | `queued`, `running`, `completed`, `failed` |
| `source` | `manual`, `schedule`, `webhook`, `api` |
| `linkedIssueId` | Issue created for this run (if the routine creates issues) |
| `triggeredAt` | When the run was triggered |

---

## API Gotchas

- **Cron quoting**: Always quote cron expressions in the shell: `--cron "0 9 * * *"`. Without quotes, the shell expands `*` as a glob and passes garbage to the CLI.
- **No hard delete**: There is no DELETE endpoint for routines. `archive` is the only way to stop a routine without deleting its parent project.
- **Trigger list is on the routine**: `routine triggers` fetches `GET /routines/:id` and reads the `triggers` field — it is not a separate endpoint.
- **`--project` is mandatory**: The API rejects routine creation without a `projectId`. Always create a project first.
- **`--assignee` is mandatory**: The API rejects routine creation without an `assigneeAgentId`.
