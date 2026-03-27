# goal

Goals are high-level objectives for a company. Issues and projects can be linked to a goal to track progress toward it.

## Quick Example

```bash
GOAL=$(paperclip-cli goal create --company "$CO" --title "Reach $10k MRR" --json | jq -r '.id')
paperclip-cli goal list --company "$CO"
paperclip-cli goal get "$GOAL"
paperclip-cli goal update "$GOAL" --status completed
paperclip-cli goal delete "$GOAL" --yes
```

---

## goal list

List all goals for a company.

```bash
paperclip-cli goal list --company <company-id>
paperclip-cli goal list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
        Goals (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ID                                   ┃ Title             ┃ Status      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ c3d4e5f6-a7b8-9012-cdef-012345678901 │ Reach $10k MRR    │ active      │
│ d4e5f6a7-b8c9-0123-def0-123456789012 │ Launch mobile app │ completed   │
└──────────────────────────────────────┴───────────────────┴─────────────┘
```

---

## goal create

Create a new goal for a company.

```bash
paperclip-cli goal create --company <company-id> --title "Reach $10k MRR"
paperclip-cli goal create --company <company-id> --title "Reach $10k MRR" --description "By end of Q2 2026"
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--title` | Yes | — | Goal title |
| `--description` | No | — | Longer description or context |
| `--json` | No | false | Output created goal as JSON |

### Example Output

```
✓ Created goal Reach $10k MRR (ID: c3d4e5f6-a7b8-9012-cdef-012345678901)
```

### JSON Output (with --json)

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-012345678901",
  "title": "Reach $10k MRR",
  "description": "By end of Q2 2026",
  "status": "active",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "createdAt": "2026-03-27T10:00:00.000Z"
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `422 Unprocessable Entity` | `--title` or `--company` missing |
| `404 Not Found` | Company ID not found |

---

## goal get

Get full details for a single goal.

```bash
paperclip-cli goal get <goal-id>
paperclip-cli goal get <goal-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `goal-id` | Yes | UUID of the goal |

### Example JSON Output

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-012345678901",
  "title": "Reach $10k MRR",
  "description": "By end of Q2 2026",
  "status": "active",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "issueCount": 5,
  "createdAt": "2026-03-01T12:00:00.000Z",
  "updatedAt": "2026-03-15T08:00:00.000Z"
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `404 Not Found` | Goal ID not found |

---

## goal update

Update a goal's title, description, or status.

```bash
paperclip-cli goal update <goal-id> --title "Reach $20k MRR"
paperclip-cli goal update <goal-id> --status completed
paperclip-cli goal update <goal-id> --description "Updated timeline: Q3 2026"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `goal-id` | Yes | UUID of the goal |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--title` | No | — | New title |
| `--description` | No | — | New description |
| `--status` | No | — | New status (free-form string, e.g. `active`, `completed`, `paused`) |
| `--json` | No | false | Output updated goal as JSON |

### Example Output

```
✓ Updated goal c3d4e5f6-a7b8-9012-cdef-012345678901
{
  "id": "c3d4e5f6-...",
  "title": "Reach $20k MRR",
  "status": "active",
  ...
}
```

---

## goal delete

Delete a goal. Linked issues will have their `goalId` cleared but are not deleted.

```bash
paperclip-cli goal delete <goal-id>
paperclip-cli goal delete <goal-id> --yes
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `goal-id` | Yes | UUID of the goal |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--yes` | No | false | Skip confirmation prompt |

### Example Output

```
✓ Deleted goal c3d4e5f6-a7b8-9012-cdef-012345678901
```

---

## API Gotchas

- `--status` is a free-form string on goals (unlike issues which have an enum). Common values are `active`, `completed`, `paused`, `cancelled`.
- Deleting a goal does **not** delete issues linked to it — those issues remain but lose their `goalId` association.
- Use `paperclip-cli issue create --goal <goal-id>` to link issues to a goal at creation time.
