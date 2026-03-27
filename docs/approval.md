# approval

The board approval queue. When a general agent is hired (or other governed actions occur), they appear here as pending approvals. Approvals must be processed before the agent becomes active.

## Quick Example

```bash
# List pending approvals
paperclip-cli approval list --company "$CO"

# Approve a hire
paperclip-cli approval approve <approval-id>

# Reject a hire
paperclip-cli approval reject <approval-id>

# Approve all pending in one go
paperclip-cli approval list --company "$CO" --json \
  | jq -r '.[] | select(.status=="pending") | .id' \
  | while read id; do paperclip-cli approval approve "$id"; done
```

---

## How Board Approval Works

1. A `general` agent is created with `paperclip-cli agent create --role general`
2. The agent's status is set to `pending_approval`
3. An approval record of type `hire_agent` appears in the queue
4. A human (or automation) calls `approval approve <id>`
5. The agent's status changes to `idle` — it can now receive tasks

CEO agents (`--role ceo`) are **auto-approved** and skip this flow entirely.

---

## Approval Types

| Type | Trigger |
|------|---------|
| `hire_agent` | A `general` agent was created |

More types may be added in future Paperclip versions.

---

## approval list

List all approvals for a company (pending and historical).

```bash
paperclip-cli approval list --company <company-id>
paperclip-cli approval list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
       Approvals (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Type        ┃ Status      ┃ Requested By                         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ g7h8i9j0-k1l2-3456-7890-abcdef012345 │ hire_agent  │ pending     │ a1b2c3d4-e5f6-7890-abcd-ef0123456789 │
│ h8i9j0k1-l2m3-4567-8901-bcdef0123456 │ hire_agent  │ approved    │ a1b2c3d4-e5f6-7890-abcd-ef0123456789 │
└──────────────────────────────────────┴─────────────┴─────────────┴──────────────────────────────────────┘
```

### JSON Output Fields

```json
[
  {
    "id": "g7h8i9j0-k1l2-3456-7890-abcdef012345",
    "type": "hire_agent",
    "status": "pending",
    "requestedByAgentId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
    "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
    "payload": {
      "agentId": "b2c3d4e5-f6a7-8901-bcde-f01234567890"
    },
    "createdAt": "2026-03-27T10:00:00.000Z"
  }
]
```

### Approval Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Waiting for a decision |
| `approved` | Approved — agent is now `idle` |
| `rejected` | Rejected — agent remains inactive |

---

## approval approve

Approve a pending action. For `hire_agent` approvals, the agent's status changes to `idle`.

```bash
paperclip-cli approval approve <approval-id>
paperclip-cli approval approve <approval-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `approval-id` | Yes | UUID of the approval record |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output result as JSON |

### Example Output

```
✓ Approved g7h8i9j0-k1l2-3456-7890-abcdef012345
```

After approving a `hire_agent`:
- The agent's status changes from `pending_approval` to `idle`
- The agent can now receive wakeup signals and process tasks

### Error Cases

| Error | Cause |
|-------|-------|
| `404 Not Found` | Approval ID not found |
| `400 Bad Request` | Approval is not in `pending` state (already approved/rejected) |

---

## approval reject

Reject a pending action. For `hire_agent` approvals, the agent remains inactive.

```bash
paperclip-cli approval reject <approval-id>
paperclip-cli approval reject <approval-id> --json
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `approval-id` | Yes | UUID of the approval record |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output result as JSON |

### Example Output

```
✓ Rejected g7h8i9j0-k1l2-3456-7890-abcdef012345
```

---

## API Gotchas

- `approval list` returns **all** approvals (including historical approved/rejected ones), not just pending. Filter with `jq`: `jq '.[] | select(.status=="pending")'`.
- The `requestedByAgentId` is the CEO (or other agent) that triggered the hire, not a user ID.
- The `payload.agentId` field contains the ID of the agent being hired.
- You cannot re-approve a rejected approval. If you reject by mistake, delete the agent and re-hire it.
- In `local_trusted` mode (dev), approvals still go through the queue for general agents. This is by design.
