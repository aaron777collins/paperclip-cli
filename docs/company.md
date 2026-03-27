# company

Manage AI companies. Each company is an isolated org with its own agents, goals, issues, projects, and budget.

## Quick Example

```bash
CO=$(paperclip-cli company create --name "AcmeCorp" --description "AI operations" --json | jq -r '.id')
paperclip-cli company list
paperclip-cli company get "$CO"
paperclip-cli company update "$CO" --mission "Automate everything"
paperclip-cli company delete "$CO" --yes
```

---

## company list

List all companies on the server.

```bash
paperclip-cli company list
paperclip-cli company list --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output raw JSON array |

### Example Output

```
                    Companies
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID                                   ┃ Name     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 6ef9c662-776f-43e0-8e7e-55f36c309edb │ AcmeCorp │
│ 3a1b2c3d-4e5f-6789-abcd-ef0123456789 │ BetaCo   │
└──────────────────────────────────────┴──────────┘
```

### JSON Output Fields

```json
[
  {
    "id": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
    "name": "AcmeCorp",
    "description": "AI operations platform",
    "mission": "Automate everything",
    "createdAt": "2026-03-01T12:00:00.000Z",
    "updatedAt": "2026-03-15T09:30:00.000Z"
  }
]
```

---

## company create

Create a new company.

```bash
paperclip-cli company create --name "AcmeCorp"
paperclip-cli company create --name "AcmeCorp" --description "AI-powered operations"
paperclip-cli company create --name "AcmeCorp" --description "..." --mission "Automate business ops"
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | Yes | — | Company name (must be unique on the server) |
| `--description` | No | — | Short description of what this company does |
| `--mission` | No | — | Mission statement |
| `--json` | No | false | Output the created company as JSON |

### Example Output

```
✓ Created company AcmeCorp (ID: 6ef9c662-776f-43e0-8e7e-55f36c309edb)
```

### JSON Output (with --json)

```json
{
  "id": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "name": "AcmeCorp",
  "description": "AI-powered operations",
  "mission": "Automate business ops",
  "createdAt": "2026-03-27T10:00:00.000Z"
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `Company name already exists` | A company with that name already exists on the server |
| `422 Unprocessable Entity` | `--name` missing or empty |

---

## company get

Get full details for a single company by ID.

```bash
paperclip-cli company get <company-id>
paperclip-cli company get 6ef9c662-776f-43e0-8e7e-55f36c309edb --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `company-id` | Yes | UUID of the company |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output raw JSON |

### Example Output

```json
{
  "id": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
  "name": "AcmeCorp",
  "description": "AI-powered operations",
  "mission": "Automate everything",
  "agentCount": 3,
  "createdAt": "2026-03-01T12:00:00.000Z",
  "updatedAt": "2026-03-27T10:00:00.000Z"
}
```

### Error Cases

| Error | Cause |
|-------|-------|
| `404 Not Found` | No company with that ID exists |

---

## company update

Update a company's name, description, or mission. Pass only the fields you want to change.

```bash
paperclip-cli company update <company-id> --name "New Name"
paperclip-cli company update <company-id> --description "Updated description"
paperclip-cli company update <company-id> --mission "New mission statement"
paperclip-cli company update <company-id> --name "MyCompany" --description "..." --mission "..."
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `company-id` | Yes | UUID of the company to update |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | No | — | New company name |
| `--description` | No | — | New description |
| `--mission` | No | — | New mission statement |
| `--json` | No | false | Output updated company as JSON |

### Example Output

```
✓ Updated company 6ef9c662-776f-43e0-8e7e-55f36c309edb
```

### Error Cases

| Error | Cause |
|-------|-------|
| `404 Not Found` | Company ID not found |
| `No fields to update` | No `--name`, `--description`, or `--mission` provided |

---

## company delete

Permanently delete a company and **all** of its data (agents, goals, issues, projects, routines).

```bash
# Prompt for confirmation
paperclip-cli company delete <company-id>

# Skip confirmation (useful in scripts)
paperclip-cli company delete <company-id> --yes
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `company-id` | Yes | UUID of the company to delete |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--yes` | No | false | Skip the confirmation prompt |

### Example Output

```
✓ Deleted company 6ef9c662-776f-43e0-8e7e-55f36c309edb
```

> **Warning:** This is irreversible. All agents, goals, issues, projects, and routines belonging to the company are permanently deleted. The server must have `companyDeletionEnabled: true` (check `paperclip-cli status --json`).

### Error Cases

| Error | Cause |
|-------|-------|
| `404 Not Found` | Company ID not found |
| `403 Forbidden` | Company deletion is disabled on this server |
| `Aborted!` | User declined the confirmation prompt |

---

## API Gotchas

- Company deletion is gated by the server config flag `companyDeletionEnabled`. On production servers this is often `false`. Check `paperclip-cli status --json` to see the current setting.
- Company names are not guaranteed to be unique by the API in all versions — always use IDs in scripts, not names.
- The `--json` flag on `create` returns the full company object, making it easy to capture the ID: `jq -r '.id'`.
