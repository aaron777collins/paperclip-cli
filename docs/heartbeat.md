# heartbeat

Heartbeat runs are records of agent activations — when an agent was woken up, why (the invocation source), and whether the run succeeded or failed. Useful for debugging agent activity and diagnosing failures.

## Quick Example

```bash
# List recent runs
paperclip-cli heartbeat list --company "$CO"

# Show only the 10 most recent
paperclip-cli heartbeat list --company "$CO" --limit 10

# Machine-readable for analysis
paperclip-cli heartbeat list --company "$CO" --json | jq '.[] | select(.status=="failed")'
```

---

## heartbeat list

List recent agent heartbeat runs for a company.

```bash
paperclip-cli heartbeat list --company <company-id>
paperclip-cli heartbeat list --company <company-id> --limit 20
paperclip-cli heartbeat list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--limit` | No | — | Max number of results to return (most recent first) |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
      Heartbeat Runs (Company: 6ef9c662-…)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Agent ID   ┃ Status      ┃ Source                ┃ Trigger            ┃ Started At          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ i9j0k1l2-… │ a1b2c3d4-… │ success     │ routine_schedule      │ Daily Standup      │ 2026-03-27T09:00:00 │
│ j0k1l2m3-… │ a1b2c3d4-… │ success     │ manual_wakeup         │                    │ 2026-03-26T14:30:00 │
│ k1l2m3n4-… │ b2c3d4e5-… │ failed      │ routine_schedule      │ Weekly Report      │ 2026-03-26T09:00:00 │
└────────────┴────────────┴─────────────┴───────────────────────┴────────────────────┴─────────────────────┘
```

---

## Field Reference

### JSON Output Fields

```json
[
  {
    "id": "i9j0k1l2-m3n4-5678-9012-345678901234",
    "agentId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
    "status": "success",
    "invocationSource": "routine_schedule",
    "triggerDetail": "Daily Standup",
    "startedAt": "2026-03-27T09:00:00.000Z",
    "completedAt": "2026-03-27T09:00:45.000Z",
    "durationMs": 45000,
    "error": null
  }
]
```

### Field Descriptions

| Field | Description |
|-------|-------------|
| `id` | Unique run ID |
| `agentId` | Which agent was activated |
| `status` | `success`, `failed`, or `running` |
| `invocationSource` | What triggered the activation (see below) |
| `triggerDetail` | Human-readable context (e.g. routine name) |
| `startedAt` | When the agent was woken |
| `completedAt` | When the run finished (null if still running) |
| `durationMs` | Duration in milliseconds |
| `error` | Error message if `status=failed`, otherwise `null` |

### Invocation Source Values

| Source | Meaning |
|--------|---------|
| `manual_wakeup` | Triggered by `paperclip-cli agent wakeup` |
| `routine_schedule` | Triggered by a cron schedule trigger |
| `routine_webhook` | Triggered by an HTTP webhook |
| `routine_api` | Triggered by `paperclip-cli routine run` |
| `system` | Internal system activation |

---

## Common Queries with jq

```bash
# Find all failed runs
paperclip-cli heartbeat list --company "$CO" --json \
  | jq '.[] | select(.status=="failed") | {id, agentId, error, startedAt}'

# Count runs per agent
paperclip-cli heartbeat list --company "$CO" --json \
  | jq 'group_by(.agentId) | map({agent: .[0].agentId, count: length})'

# Show average duration of successful runs
paperclip-cli heartbeat list --company "$CO" --json \
  | jq '[.[] | select(.status=="success") | .durationMs] | add / length'

# Most recent run per agent
paperclip-cli heartbeat list --company "$CO" --json \
  | jq 'group_by(.agentId) | map(sort_by(.startedAt) | last)'
```

---

## API Gotchas

- Heartbeat runs are created automatically by the platform whenever an agent is activated. You cannot create them manually.
- The list is returned in reverse-chronological order (newest first).
- `--limit` is applied client-side by the CLI (the API returns all records and the CLI truncates). For large deployments, use `--json` and pipe to `jq` with `.[0:N]` if needed.
- On a fresh server with no agent activity, `heartbeat list` returns an empty table — this is normal.
