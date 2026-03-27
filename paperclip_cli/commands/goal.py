"""Goal management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group()
def goal():
    """Manage company goals."""


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
