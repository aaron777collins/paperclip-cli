# issue

Issues are tasks and tickets that agents work on. They can be linked to goals and assigned to agents.

## Quick Example

```bash
ISS=$(paperclip-cli issue create --company "$CO" --title "Build auth system" --json | jq -r '.id')
paperclip-cli issue list --company "$CO"
paperclip-cli issue get "$ISS"

# Assign and mark in progress (MUST provide --assignee for in_progress)
paperclip-cli issue update "$ISS" --status in_progress --assignee "$AGENT_ID"

# Mark done
paperclip-cli issue update "$ISS" --status done
paperclip-cli issue delete "$ISS" --yes
```

---

## Status Enum

Issues use a strict status enum. Invalid values cause a `422` error.

| Status | Meaning |
|--------|---------|
| `backlog` | Not scheduled yet |
| `todo` | Scheduled for work |
| `in_progress` | Actively being worked (requires `assigneeAgentId`) |
| `done` | Completed |
| `cancelled` | Will not be done |

> **Critical:** Setting `status=in_progress` requires `--assignee <agent-id>`. The API enforces this — you'll get a `422` if you try `in_progress` without an assignee.

---

## issue list

List all issues for a company, optionally filtered by status.

```bash
paperclip-cli issue list --company <company-id>
paperclip-cli issue list --company <company-id> --status in_progress
paperclip-cli issue list --company <company-id> --status done --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--status` | No | — | Filter: `backlog`, `todo`, `in_progress`, `done`, `cancelled` |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
        Issues (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Title                ┃ Status      ┃ Assignee                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ e5f6a7b8-c9d0-1234-ef01-234567890123 │ Build auth system    │ in_progress │ a1b2c3d4-e5f6-7890-abcd-ef0123456789 │
│ f6a7b8c9-d0e1-2345-f012-345678901234 │ Fix signup bug       │ todo        │                                      │
└──────────────────────────────────────┴──────────────────────┴─────────────┴──────────────────────────────────────┘
```

---

## issue create

Create a new issue, optionally linked to a goal.

```bash
paperclip-cli issue create --company <company-id> --title "Implement login flow"
paperclip-cli issue create --company <company-id> --title "Fix signup bug" --description "Users can't sign up with Gmail"
paperclip-cli issue create --company <company-id> --title "Add dashboard" --goal <goal-id>
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--title` | Yes | — | Issue title |
| `--description` | No | — | Detailed description |
| `--goal` | No | — | Goal ID to link this issue to |
| `--json` | No | false | Output created issue as JSON |

### Example Output

```
✓ Created issue Build auth system (ID: e5f6a7b8-c9d0-1234-ef01-234567890123)
```

### JSON Output (with --json)

```json
{
  "id": "e5f6a7b8-c9d0-1234-ef01-234567890123",
  "title": "Build auth system",
  "description": "",
  "status": "backlog",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "goalId": null,
  "assigneeAgentId": null,
  "createdAt": "2026-03-27T10:00:00.000Z"
}
```

---

## issue get

Get full details for a single issue.

```bash
paperclip-cli issue get <issue-id>
paperclip-cli issue get <issue-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `issue-id` | Yes | UUID of the issue |

### Example JSON Output

```json
{
  "id": "e5f6a7b8-c9d0-1234-ef01-234567890123",
  "title": "Build auth system",
  "description": "Implement JWT-based authentication",
  "status": "in_progress",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "goalId": "c3d4e5f6-a7b8-9012-cdef-012345678901",
  "assigneeAgentId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "priority": "medium",
  "createdAt": "2026-03-01T12:00:00.000Z",
  "updatedAt": "2026-03-27T10:00:00.000Z"
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `assigneeAgentId` | UUID of the agent assigned to this issue (not a user ID) |
| `goalId` | Linked goal, or `null` |
| `priority` | `critical`, `high`, `medium`, `low` |

---

## issue update

Update an issue's title, description, status, or assignee.

```bash
# Change title
paperclip-cli issue update <issue-id> --title "Fix signup bug (Gmail)"

# Mark done
paperclip-cli issue update <issue-id> --status done

# Assign to an agent and mark in_progress (BOTH required)
paperclip-cli issue update <issue-id> --status in_progress --assignee <agent-id>

# Just assign without changing status
paperclip-cli issue update <issue-id> --assignee <agent-id>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `issue-id` | Yes | UUID of the issue |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--title` | No | — | New title |
| `--description` | No | — | New description |
| `--status` | No | — | New status: `backlog`, `todo`, `in_progress`, `done`, `cancelled` |
| `--assignee` | No | — | Agent ID to assign issue to (⚠️ required when setting `in_progress`) |
| `--json` | No | false | Output updated issue as JSON |

### Example Output

```
✓ Updated issue e5f6a7b8-c9d0-1234-ef01-234567890123
{
  "id": "e5f6a7b8-...",
  "status": "in_progress",
  "assigneeAgentId": "a1b2c3d4-...",
  ...
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `422 Unprocessable Entity` | Setting `in_progress` without `--assignee` |
| `422 Unprocessable Entity` | Invalid status value (not in the enum) |
| `404 Not Found` | Issue ID not found |

---

## issue delete

Delete an issue permanently.

```bash
paperclip-cli issue delete <issue-id>
paperclip-cli issue delete <issue-id> --yes
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `issue-id` | Yes | UUID of the issue |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--yes` | No | false | Skip confirmation |

### Example Output

```
✓ Deleted issue e5f6a7b8-c9d0-1234-ef01-234567890123
```

---

## API Gotchas

- **`in_progress` requires `assigneeAgentId`** — this is enforced by the API. If you send `status: "in_progress"` without `assigneeAgentId`, you get a `422` error. Always pass `--assignee` together with `--status in_progress`.
- The `--status` filter on `issue list` passes the value as a query parameter. Some status values that work in `update` may not be filterable — `in_progress` and `done` are the most commonly filtered.
- The assignee field in the API is `assigneeAgentId` (not `assigneeUserId`). Always use an agent ID, not a user ID.
- New issues default to `backlog` status.
