# paperclip-cli — Full Command Reference

## Global Options

```
paperclip-cli [--url URL] [--token TOKEN] [--version] [-h] COMMAND
```

| Option | Env var | Description |
|--------|---------|-------------|
| `--url` | `PAPERCLIP_URL` | Server URL (overrides saved config) |
| `--token` | `PAPERCLIP_TOKEN` | Auth token |
| `--version` | — | Show version |

Config saved to: `~/.config/paperclip-cli/config.json`

---

## company

```bash
paperclip-cli company                         # show help
paperclip-cli company list [--json]
paperclip-cli company create --name X [--description X] [--mission X] [--json]
paperclip-cli company get <id> [--json]
paperclip-cli company update <id> [--name X] [--description X] [--mission X] [--json]
paperclip-cli company delete <id> [--yes]
```

---

## agent

```bash
paperclip-cli agent                           # show help
paperclip-cli agent list --company <id> [--json]
paperclip-cli agent create --company <id> --name X [--role general|ceo] [--title X] [--json]
paperclip-cli agent get <agent-id> [--json]
paperclip-cli agent update <agent-id> [--name X] [--title X] [--role X] [--reports-to X] [--budget CENTS] [--adapter-type X] [--json]
paperclip-cli agent delete <agent-id> [--yes]
paperclip-cli agent wakeup <agent-id>         # only works when status=idle
```

**Roles:**
- `ceo` — auto-approved, `canCreateAgents: true`, starts `idle`
- `general` — requires board approval, starts `pending_approval`

**Budget:** integer cents per month (e.g. `5000` = $50.00/month)

---

## goal

```bash
paperclip-cli goal                            # show help
paperclip-cli goal list --company <id> [--json]
paperclip-cli goal create --company <id> --title X [--description X] [--json]
paperclip-cli goal update <goal-id> [--title X] [--description X] [--status X] [--json]
paperclip-cli goal delete <goal-id> [--yes]
```

---

## issue

```bash
paperclip-cli issue                           # show help
paperclip-cli issue list --company <id> [--status STATUS] [--json]
paperclip-cli issue create --company <id> --title X [--description X] [--goal GOAL_ID] [--json]
paperclip-cli issue update <issue-id> [--title X] [--description X] [--status STATUS] [--assignee AGENT_ID] [--json]
paperclip-cli issue delete <issue-id> [--yes]
```

**Valid statuses:** `backlog`, `todo`, `in_progress`, `done`, `cancelled`
⚠️ `in_progress` **requires** `--assignee <agent-id>`

---

## approval

```bash
paperclip-cli approval                        # show help
paperclip-cli approval list --company <id> [--json]
paperclip-cli approval approve <approval-id>
paperclip-cli approval reject <approval-id>
```

**Approval types:** `hire_agent` (and others as Paperclip adds governance features)
**Approval statuses:** `pending`, `approved`, `rejected`

---

## plugin

```bash
paperclip-cli plugin                          # show help
paperclip-cli plugin list [--json]
paperclip-cli plugin examples [--json]
paperclip-cli plugin install <name-or-url>
```

---

## status / health

```bash
paperclip-cli status [--json]
paperclip-cli health [--json]    # alias
```

Returns server version, deployment mode, auth status.
