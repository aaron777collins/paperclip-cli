"""Routine management commands.

Routines are recurring tasks that run on a schedule (cron), webhook, or manual trigger.
Each routine belongs to a project and is assigned to an agent.

Trigger kinds:
  schedule  — cron expression (e.g. "0 9 * * *" = daily at 9am UTC)
  webhook   — HTTP POST to a generated URL triggers a run
  api       — Manual trigger via API/CLI (paperclip-cli routine run)

Concurrency policies (what happens when a routine is still running at trigger time):
  coalesce_if_active  — Skip new run if one is already active (default, safe)
  skip_if_active      — Same as coalesce but stricter
  always_enqueue      — Queue every run regardless

Catch-up policies (what happens after downtime/missed runs):
  skip_missed         — Ignore missed runs (default)
  enqueue_missed_with_cap — Enqueue missed runs up to a cap
"""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def routine(ctx):
    """Manage recurring routines (scheduled / webhook / manual agent tasks).

    \b
    Routines are recurring tasks assigned to an agent.
    They require a project (--project) and an assignee (--assignee).

    \b
    Quick example — daily standup routine:
      paperclip-cli routine create \\
        --company <company-id> --project <project-id> \\
        --name "Daily Standup" --assignee <agent-id>
      paperclip-cli routine trigger-add <routine-id> \\
        --kind schedule --cron "0 9 * * *" --label "Daily 9am UTC"
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@routine.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def routine_list(ctx, company_id, as_json):
    """List all routines for a company."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/routines")
        routines = result if isinstance(result, list) else result.get("routines", [])
        if as_json:
            click.echo(json.dumps(routines, indent=2))
            return
        if not routines:
            console.print("[yellow]No routines found.[/yellow]")
            return
        table = Table(title=f"Routines (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold")
        table.add_column("Status")
        table.add_column("Concurrency")
        table.add_column("Assignee")
        for r in routines:
            table.add_row(
                str(r.get("id", "")),
                r.get("title", ""),
                r.get("status", ""),
                r.get("concurrencyPolicy", ""),
                str(r.get("assigneeAgentId") or ""),
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@routine.command("create")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--project", "project_id", required=True, help="Project ID (routines must belong to a project)")
@click.option("--name", required=True, help="Routine title")
@click.option("--assignee", "assignee_agent_id", required=True,
              help="Agent ID to run this routine (required)")
@click.option("--description", default=None, help="Description")
@click.option("--goal", "goal_id", default=None, help="Goal ID to link to")
@click.option("--priority", default="medium",
              type=click.Choice(["critical", "high", "medium", "low"]),
              help="Priority (default: medium)")
@click.option("--status", default="active",
              type=click.Choice(["active", "paused", "archived"]),
              help="Status (default: active)")
@click.option("--concurrency", default="coalesce_if_active",
              type=click.Choice(["coalesce_if_active", "always_enqueue", "skip_if_active"]),
              help="What to do if a run is already active (default: coalesce_if_active)")
@click.option("--catchup", default="skip_missed",
              type=click.Choice(["skip_missed", "enqueue_missed_with_cap"]),
              help="What to do with missed runs after downtime (default: skip_missed)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def routine_create(ctx, company_id, project_id, name, assignee_agent_id, description,
                   goal_id, priority, status, concurrency, catchup, as_json):
    """Create a new routine.

    \b
    ⚠️  REQUIRED: --project and --assignee (the API enforces both).

    After creating, add a trigger with:
      paperclip-cli routine trigger-add <routine-id> --kind schedule --cron "0 9 * * *"
    """
    client: PaperclipClient = ctx.obj
    try:
        payload = {
            "title": name,
            "projectId": project_id,
            "assigneeAgentId": assignee_agent_id,
            "priority": priority,
            "status": status,
            "concurrencyPolicy": concurrency,
            "catchUpPolicy": catchup,
        }
        if description:
            payload["description"] = description
        if goal_id:
            payload["goalId"] = goal_id
        result = client.post(f"/companies/{company_id}/routines", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        routine_id = result.get("id", "?")
        console.print(f"[green]✓[/green] Created routine [bold]{name}[/bold] (ID: {routine_id})")
        console.print(f"  Add a trigger: [dim]paperclip-cli routine trigger-add {routine_id} --kind schedule --cron \"0 9 * * *\"[/dim]")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@routine.command("get")
@click.argument("routine_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def routine_get(ctx, routine_id, as_json):
    """Get routine details."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/routines/{routine_id}")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@routine.command("update")
@click.argument("routine_id")
@click.option("--name", default=None, help="New title")
@click.option("--description", default=None, help="New description")
@click.option("--status", default=None,
              type=click.Choice(["active", "paused", "archived"]),
              help="New status")
@click.option("--assignee", "assignee_agent_id", default=None, help="New assignee agent ID")
@click.option("--priority", default=None,
              type=click.Choice(["critical", "high", "medium", "low"]),
              help="New priority")
@click.option("--concurrency", default=None,
              type=click.Choice(["coalesce_if_active", "always_enqueue", "skip_if_active"]),
              help="New concurrency policy")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def routine_update(ctx, routine_id, name, description, status, assignee_agent_id, priority, concurrency, as_json):
    """Update a routine."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {}
        if name is not None:
            payload["title"] = name
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if assignee_agent_id is not None:
            payload["assigneeAgentId"] = assignee_agent_id
        if priority is not None:
            payload["priority"] = priority
        if concurrency is not None:
            payload["concurrencyPolicy"] = concurrency
        if not payload:
            console.print("[yellow]No fields to update.[/yellow]")
            raise SystemExit(1)
        result = client.patch(f"/routines/{routine_id}", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Updated routine {routine_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@routine.command("archive")
@click.argument("routine_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def routine_archive(ctx, routine_id, yes):
    """Archive a routine (Paperclip has no hard-delete for routines).

    \b
    ⚠️  The Paperclip API does not support deleting routines.
    Archiving sets status=archived and stops all future runs.
    To fully remove a routine, delete its parent project.
    """
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Archive routine {routine_id}? (stops all future runs)", abort=True)
    try:
        client.patch(f"/routines/{routine_id}", {"status": "archived"})
        console.print(f"[green]✓[/green] Archived routine {routine_id} (no more runs will fire)")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@routine.command("trigger-add")
@click.argument("routine_id")
@click.option("--kind", required=True,
              type=click.Choice(["schedule", "webhook", "api"]),
              help="Trigger kind: schedule (cron), webhook (HTTP), or api (manual)")
@click.option("--cron", "cron_expression", default=None,
              help="Cron expression for schedule triggers (e.g. '0 9 * * *' = daily 9am UTC)")
@click.option("--timezone", default="UTC",
              help="Timezone for cron schedule (default: UTC, e.g. America/New_York)")
@click.option("--label", default=None, help="Human-readable label for this trigger")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def routine_trigger_add(ctx, routine_id, kind, cron_expression, timezone, label, as_json):
    """Add a trigger to a routine.

    \b
    Schedule trigger (cron):
      paperclip-cli routine trigger-add <id> --kind schedule --cron "0 9 * * *"
      paperclip-cli routine trigger-add <id> --kind schedule --cron "0 9 * * 1-5" --timezone America/New_York

    \b
    Webhook trigger (returns a URL to POST to):
      paperclip-cli routine trigger-add <id> --kind webhook

    \b
    API trigger (run manually via CLI):
      paperclip-cli routine trigger-add <id> --kind api
      paperclip-cli routine run <routine-id>
    """
    client: PaperclipClient = ctx.obj
    try:
        payload = {"kind": kind}
        if label:
            payload["label"] = label
        if kind == "schedule":
            if not cron_expression:
                console.print("[red]Error:[/red] --cron is required for schedule triggers")
                console.print("  Example: --cron \"0 9 * * *\"  (daily at 9am UTC)")
                raise SystemExit(1)
            payload["cronExpression"] = cron_expression
            payload["timezone"] = timezone
        result = client.post(f"/routines/{routine_id}/triggers", payload)
        trigger = result.get("trigger", result)
        if as_json:
            click.echo(json.dumps(trigger, indent=2))
            return
        trigger_id = trigger.get("id", "?")
        console.print(f"[green]✓[/green] Added {kind} trigger (ID: {trigger_id})")
        if kind == "schedule":
            console.print(f"  Cron: {cron_expression} ({timezone})")
            if trigger.get("nextRunAt"):
                console.print(f"  Next run: {trigger['nextRunAt']}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@routine.command("run")
@click.argument("routine_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def routine_run(ctx, routine_id, as_json):
    """Manually trigger a routine run now."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.post(f"/routines/{routine_id}/run", {"source": "manual"})
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Triggered routine {routine_id}")
        if result:
            console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
