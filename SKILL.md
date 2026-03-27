---
name: paperclip-cli
description: Manage Paperclip AI agent companies from the command line. Use when creating or listing companies, hiring agents, creating goals, or managing issues/tasks in a Paperclip instance. Requires paperclip-cli installed (pip install paperclip-cli) and a running Paperclip server.
---

# paperclip-cli Skill

Paperclip is an AI agent orchestration platform. This CLI lets you manage it programmatically.

## Prerequisites

```bash
pip install paperclip-cli --break-system-packages
paperclip-cli configure --url http://localhost:3100
paperclip-cli status  # verify connection
```

## Key Commands

```bash
# Companies
paperclip-cli company list --json
paperclip-cli company create --name "TenantHelper" --description "AI property management SaaS" --json
paperclip-cli company get <company-id> --json

# Agents
paperclip-cli agent list --company <id> --json
paperclip-cli agent create --company <id> --name "Coordinator" --role "Project Coordinator" --json
paperclip-cli agent wakeup <agent-id>

# Goals
paperclip-cli goal list --company <id> --json
paperclip-cli goal create --company <id> --title "Launch MVP" --json

# Issues (tasks)
paperclip-cli issue list --company <id> --json
paperclip-cli issue create --company <id> --title "Implement feature X" --goal <goal-id> --json
```

## JSON Output Pattern

All commands support `--json` for structured output. Always use `--json` when parsing results:

```bash
COMPANY_ID=$(paperclip-cli company create --name "My Company" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

## Environment Variables

```bash
export PAPERCLIP_URL=http://localhost:3100  # or set via configure
export PAPERCLIP_TOKEN=<token>              # if auth required
```
