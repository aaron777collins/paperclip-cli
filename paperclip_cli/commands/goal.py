"""Goal management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def goal(ctx):
    """Manage company goals."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@goal.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def goal_list(ctx, company_id, as_json):
    """List goals for a company."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/goals")
        goals = result if isinstance(result, list) else result.get("goals", result.get("data", []))
        if as_json:
            click.echo(json.dumps(goals, indent=2))
            return
        if not goals:
            console.print("[yellow]No goals found.[/yellow]")
            return
        table = Table(title=f"Goals (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold")
        table.add_column("Status")
        for g in goals:
            table.add_row(str(g.get("id", "")), g.get("title", ""), g.get("status", ""))
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@goal.command("create")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--title", required=True, help="Goal title")
@click.option("--description", default="", help="Goal description")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def goal_create(ctx, company_id, title, description, as_json):
    """Create a goal for a company."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {"title": title}
        if description:
            payload["description"] = description
        result = client.post(f"/companies/{company_id}/goals", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        goal_id = result.get("id", "?")
        console.print(f"[green]✓[/green] Created goal [bold]{title}[/bold] (ID: {goal_id})")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@goal.command("update")
@click.argument("goal_id")
@click.option("--title", default=None, help="New title")
@click.option("--description", default=None, help="New description")
@click.option("--status", default=None, help="New status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def goal_update(ctx, goal_id, title, description, status, as_json):
    """Update a goal."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        result = client.patch(f"/goals/{goal_id}", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Updated goal {goal_id}")
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@goal.command("delete")
@click.argument("goal_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def goal_delete(ctx, goal_id, yes):
    """Delete a goal."""
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Delete goal {goal_id}?", abort=True)
    try:
        client.delete(f"/goals/{goal_id}")
        console.print(f"[green]✓[/green] Deleted goal {goal_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@goal.command("get")
@click.argument("goal_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def goal_get(ctx, goal_id, as_json):
    """Get full details for a goal."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/goals/{goal_id}")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
