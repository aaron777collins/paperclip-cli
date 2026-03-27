# project

Projects are containers that group issues and routines. They belong to a company and can optionally be linked to a goal.

## Quick Example

```bash
PROJ=$(paperclip-cli project create --company "$CO" --name "Auth System" --json | jq -r '.id')
paperclip-cli project list --company "$CO"
paperclip-cli project get "$PROJ"
paperclip-cli project update "$PROJ" --status in_progress
paperclip-cli project delete "$PROJ" --yes
```

> **Warning:** Deleting a project also deletes all routines inside it (cascade delete).

---

## project list

List all projects for a company.

```bash
paperclip-cli project list --company <company-id>
paperclip-cli project list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
      Projects (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Name           ┃ Status      ┃ Description                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ f7a8b9c0-d1e2-3456-f012-345678901234 │ Auth System    │ in_progress │ JWT auth and session management   │
│ a8b9c0d1-e2f3-4567-0123-456789012345 │ Dashboard      │ planned     │                                   │
└──────────────────────────────────────┴────────────────┴─────────────┴───────────────────────────────────┘
```

---

## project create

Create a new project in a company.

```bash
paperclip-cli project create --company <company-id> --name "Auth System"
paperclip-cli project create --company <company-id> --name "Auth System" --description "JWT auth and sessions"
paperclip-cli project create --company <company-id> --name "Dashboard" --goal <goal-id> --lead <agent-id>
paperclip-cli project create --company <company-id> --name "Design" --color "#6366f1"
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--name` | Yes | — | Project name |
| `--description` | No | — | Project description |
| `--goal` | No | — | Goal ID to link this project to |
| `--lead` | No | — | Lead agent ID (responsible agent) |
| `--color` | No | — | Hex color for visual grouping (e.g. `#6366f1`) |
| `--json` | No | false | Output created project as JSON |

### Example Output

```
✓ Created project Auth System (ID: f7a8b9c0-d1e2-3456-f012-345678901234)
```

### JSON Output (with --json)

```json
{
  "id": "f7a8b9c0-d1e2-3456-f012-345678901234",
  "name": "Auth System",
  "description": "JWT auth and sessions",
  "status": "backlog",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "goalId": null,
  "leadAgentId": null,
  "color": null,
  "createdAt": "2026-03-27T10:00:00.000Z"
}
```

---

## project get

Get full details for a single project.

```bash
paperclip-cli project get <project-id>
paperclip-cli project get <project-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `project-id` | Yes | UUID of the project |

### Example JSON Output

```json
{
  "id": "f7a8b9c0-d1e2-3456-f012-345678901234",
  "name": "Auth System",
  "description": "JWT auth and sessions",
  "status": "in_progress",
  "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "goalId": "c3d4e5f6-a7b8-9012-cdef-012345678901",
  "leadAgentId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "color": "#6366f1",
  "routineCount": 2,
  "createdAt": "2026-03-01T12:00:00.000Z",
  "updatedAt": "2026-03-27T10:00:00.000Z"
}
```

---

## project update

Update a project's name, description, status, goal, or lead agent.

```bash
paperclip-cli project update <project-id> --name "Auth v2"
paperclip-cli project update <project-id> --status in_progress
paperclip-cli project update <project-id> --lead <agent-id>
paperclip-cli project update <project-id> --goal <goal-id>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `project-id` | Yes | UUID of the project |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | No | — | New project name |
| `--description` | No | — | New description |
| `--status` | No | — | New status: `backlog`, `planned`, `in_progress`, `completed`, `cancelled`, `paused` |
| `--goal` | No | — | Goal ID to link to |
| `--lead` | No | — | Lead agent ID |
| `--json` | No | false | Output updated project as JSON |

### Project Status Values

| Status | Meaning |
|--------|---------|
| `backlog` | Not yet planned |
| `planned` | Scheduled for future work |
| `in_progress` | Actively being worked on |
| `completed` | Done |
| `cancelled` | Abandoned |
| `paused` | Temporarily on hold |

### Error Cases

| Error | Cause |
|-------|-------|
| `No fields to update` | No update flags provided |
| `404 Not Found` | Project ID not found |

---

## project delete

Delete a project permanently. **All routines inside the project are also deleted (cascade).**

```bash
paperclip-cli project delete <project-id>
paperclip-cli project delete <project-id> --yes
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `project-id` | Yes | UUID of the project |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--yes` | No | false | Skip confirmation prompt |

### Example Output

```
✓ Deleted project f7a8b9c0-d1e2-3456-f012-345678901234
```

---

## API Gotchas

- **Cascade delete**: Deleting a project deletes all routines inside it. There is no way to undo this. If you want to keep the routines, move them to another project first (not currently supported by the CLI — use the API directly).
- **Routines require a project**: Every routine must belong to a project. You cannot create a routine without specifying `--project`.
- `routineCount` is returned in the project `get` response — useful for checking before deletion.
- The `--color` field accepts CSS hex colors (`#6366f1`, `#ff0000`, etc.). It's purely cosmetic for the web UI.
