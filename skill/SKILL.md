---
name: paperclip-cli
description: Manage Paperclip AI agent companies, agents, goals, issues, approvals, and plugins using the paperclip-cli tool. Use when: creating or managing AI companies in Paperclip, hiring/firing/updating agents, managing goals and issues/tasks, approving board actions, managing plugins, or querying org structure. Triggers on "paperclip", "agent company", "hire agent", "approve agent", "paperclip company", "paperclip goal", "paperclip issue", or any task involving the Paperclip AI orchestration platform.
---

# paperclip-cli Skill

CLI tool for the [Paperclip](https://github.com/paperclipai/paperclip) AI agent orchestration platform.

## Setup (one-time)

```bash
pip install -e /home/ubuntu/repos/paperclip-cli   # or: pip install paperclip-cli
paperclip-cli configure --url http://localhost:3100
```

No token needed for `local_trusted` mode (default dev setup).

## Command Coverage

| Resource | list | create | get | update | delete | extras |
|----------|:----:|:------:|:---:|:------:|:------:|--------|
| company | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| agent | ✅ | ✅ | ✅ | ✅ | ✅ | `wakeup` |
| goal | ✅ | ✅ | — | ✅ | ✅ | — |
| issue | ✅ | ✅ | — | ✅ | ✅ | — |
| project | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| routine | ✅ | ✅ | ✅ | ✅ | `archive`¹ | `trigger-add`, `run` |
| approval | ✅ | — | — | — | — | `approve`, `reject` |
| plugin | ✅ | — | — | — | — | `examples`, `install` |

> ¹ API has no hard-delete for routines. Use `routine archive` to stop runs. Delete parent project to fully remove.

All commands: `--json` for machine output, `-h`/`--help` for usage, no-arg group → shows help.

## Key Patterns

### Get IDs (use --json + python3)
```bash
# Company ID by name
CO=$(paperclip-cli company list --json | python3 -c "import sys,json; print(next(c['id'] for c in json.load(sys.stdin) if c['name']=='MyCompany'))")

# Agent ID by name
AG=$(paperclip-cli agent list --company $CO --json | python3 -c "import sys,json; print(next(a['id'] for a in json.load(sys.stdin) if a['name']=='CEO'))")
```

### Hire an agent
```bash
# CEO — auto-approved, canCreateAgents:true, status starts as idle
paperclip-cli agent create --company $CO --name "CEO" --role ceo --title "Chief Executive Officer"

# General agent — goes to board approval queue, status starts as pending_approval
paperclip-cli agent create --company $CO --name "Engineer" --role general --title "Backend Engineer"

# Approve the hire
APPROVAL=$(paperclip-cli approval list --company $CO --json | python3 -c "import sys,json; print(next(a['id'] for a in json.load(sys.stdin) if a['status']=='pending'))")
paperclip-cli approval approve $APPROVAL
```

### Approve all pending hires at once
```bash
paperclip-cli approval list --company $CO --json \
  | python3 -c "import sys,json; [print(a['id']) for a in json.load(sys.stdin) if a['status']=='pending']" \
  | while read id; do paperclip-cli approval approve $id; done
```

### Issue statuses
Valid: `backlog`, `todo`, `in_progress`, `done`, `cancelled`
⚠️ `in_progress` requires `--assignee <agent-id>`:
```bash
paperclip-cli issue update $ISSUE --status in_progress --assignee $AGENT_ID
```

### Bootstrap a company end-to-end
```bash
CO=$(paperclip-cli company create --name "MyCompany" --description "..." --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
paperclip-cli agent create --company $CO --name "CEO" --role ceo --title "Chief Executive Officer"
paperclip-cli agent create --company $CO --name "Engineer" --role general --title "Backend Engineer"
# approve all pending
paperclip-cli approval list --company $CO --json \
  | python3 -c "import sys,json; [print(a['id']) for a in json.load(sys.stdin) if a['status']=='pending']" \
  | while read id; do paperclip-cli approval approve $id; done
paperclip-cli goal create --company $CO --title "Ship MVP"
```

## API Notes (important gotchas)

- **Assignee field**: API uses `assigneeAgentId` (not `assigneeId`)
- **Agent statuses**: `idle`, `pending_approval`, `active`, `paused`, `error`
- **Agent wakeup**: only works when status = `idle`
- **Issue default status**: newly created issues start as `backlog`
- **Issue statuses**: `backlog`, `todo`, `in_progress`, `done`, `cancelled` — NOT `open`
- **`in_progress` issues require `--assignee`**: API 422 if no assignee set
- **Agent roles**: `ceo` (auto-approved) or `general` (requires approval)
- **Routines require project + assignee**: both fields are mandatory on create
- **No routine hard-delete**: use `routine archive` (sets status=archived); delete parent project to fully purge
- **Routine triggers**: `schedule` (cron), `webhook` (HTTP POST), `api` (manual via `routine run`)
- **Project delete cascades**: deletes all routines in that project
- **Server config**: bound to `127.0.0.1:3100`; Docker reaches it via socat proxy on `172.18.0.1:3101`

## Full Reference

📖 See [references/commands.md](references/commands.md) for complete option tables for every command.
