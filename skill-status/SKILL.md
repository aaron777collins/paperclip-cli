---
name: paperclip-status
description: Check status, progress, and activity across all Paperclip AI companies. Use when asked about project progress, agent activity, open issues, goals, what's happening in Paperclip, or generating a digest/summary of work across all companies. Triggers on "paperclip status", "what's happening in paperclip", "project progress", "paperclip digest", "check on companies", "agent activity".
---

# Paperclip Status Skill

Check progress across all Paperclip companies using `paperclip-cli`.

## Server
`http://localhost:3100` (local_trusted, no auth)

## Companies
| ID prefix | Name |
|-----------|------|
| `6ef9c662` | TenantHelper |
| `3e131528` | CashClaw v2 |
| `f1a2507c` | Returnzie |
| `bd36327a` | Bible Drawing Pipeline |

## Quick Status Check

```bash
CLI=/home/ubuntu/.local/bin/paperclip-cli

# All companies + agent count
paperclip-cli company list

# For each company: goals, open issues, agent statuses
for CO in 6ef9c662-776f-43e0-8e7e-55f36c309edb 3e131528-923f-4bfb-aa4b-dc882c117e73 f1a2507c-1f2b-482c-a5d7-c5f7b115cec1 bd36327a-b84b-46a7-91f8-9ccfcbe179c8; do
  NAME=$(paperclip-cli company get $CO --json | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])")
  echo "=== $NAME ==="
  echo "Goals:"
  paperclip-cli goal list --company $CO
  echo "Issues (open):"
  paperclip-cli issue list --company $CO --status backlog
  echo "Agents:"
  paperclip-cli agent list --company $CO
  echo "Recent heartbeats:"
  paperclip-cli heartbeat list --company $CO --limit 5
done
```

## Digest Generation Pattern

For a concise digest (use in update summaries):

```bash
CLI=/home/ubuntu/.local/bin/paperclip-cli

python3 << 'EOF'
import subprocess, json

COMPANIES = [
  ("6ef9c662-776f-43e0-8e7e-55f36c309edb", "TenantHelper"),
  ("3e131528-923f-4bfb-aa4b-dc882c117e73", "CashClaw v2"),
  ("f1a2507c-1f2b-482c-a5d7-c5f7b115cec1", "Returnzie"),
  ("bd36327a-b84b-46a7-91f8-9ccfcbe179c8", "Bible Drawing Pipeline"),
]

BASE = "http://localhost:3100/api"

def api(path):
    import urllib.request
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read())

for co_id, name in COMPANIES:
    goals = api(f"/companies/{co_id}/goals")
    issues = api(f"/companies/{co_id}/issues")
    agents = api(f"/companies/{co_id}/agents")
    hb = api(f"/companies/{co_id}/heartbeat-runs")
    
    open_issues = [i for i in issues if i.get("status") in ("backlog", "todo", "in_progress")]
    done_issues = [i for i in issues if i.get("status") == "done"]
    idle_agents = [a for a in agents if a.get("status") == "idle"]
    recent_hb = hb[:3] if hb else []
    
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"  Goals: {len(goals)} | Open issues: {len(open_issues)} | Done: {len(done_issues)}")
    print(f"  Agents: {len(agents)} total, {len(idle_agents)} idle")
    for g in goals[:3]:
        print(f"  🎯 {g['title']}")
    for i in open_issues[:5]:
        print(f"  📋 [{i['status']}] {i['title']}")
    if recent_hb:
        last = recent_hb[0]
        print(f"  ❤️  Last heartbeat: {last.get('status')} ({last.get('startedAt','?')[:10]})")
EOF
```

## Key Metrics to Surface in Digest
- Goals count and status per company
- Open/in-progress issue count
- Done issues this week
- Agent heartbeat health (any failures?)
- Routine run history (did scheduled routines fire?)
