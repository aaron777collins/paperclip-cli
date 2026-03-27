"""Issue (task) management commands — Paperclip calls these 'issues'."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def issue(ctx):
    """Manage issues/tasks within a company."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@issue.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--status", default=None, help="Filter by status (open, in_progress, done, etc.)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def issue_list(ctx, company_id, status, as_json):
    """List issues for a company."""
    client: PaperclipClient = ctx.obj
    try:
        params = {}
        if status:
            params["status"] = status
        result = client.get(f"/companies/{company_id}/issues", params=params)
        issues = result if isinstance(result, list) else result.get("issues", result.get("data", []))
        if as_json:
            click.echo(json.dumps(issues, indent=2))
            return
        if not issues:
            console.print("[yellow]No issues found.[/yellow]")
            return
        table = Table(title=f"Issues (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold")
        table.add_column("Status")
        table.add_column("Assignee")
        for i in issues:
            table.add_row(
                str(i.get("id", "")),
                i.get("title", ""),
                i.get("status", ""),
                i.get("assignee", {}).get("name", "") if isinstance(i.get("assignee"), dict) else str(i.get("assigneeId", "")),
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@issue.command("create")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--title", required=True, help="Issue title")
@click.option("--description", default="", help="Issue description")
@click.option("--goal", "goal_id", default=None, help="Goal ID to attach to")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def issue_create(ctx, company_id, title, description, goal_id, as_json):
    """Create an issue/task."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {"title": title}
        if description:
            payload["description"] = description
        if goal_id:
            payload["goalId"] = goal_id
        result = client.post(f"/companies/{company_id}/issues", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        issue_id = result.get("id", "?")
        console.print(f"[green]✓[/green] Created issue [bold]{title}[/bold] (ID: {issue_id})")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@issue.command("update")
@click.argument("issue_id")
@click.option("--title", default=None, help="New title")
@click.option("--description", default=None, help="New description")
@click.option("--status", default=None, help="New status")
@click.option("--assignee", "assignee_id", default=None, help="Assignee agent ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def issue_update(ctx, issue_id, title, description, status, assignee_id, as_json):
    """Update an issue."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if assignee_id is not None:
            payload["assigneeId"] = assignee_id
        result = client.patch(f"/issues/{issue_id}", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Updated issue {issue_id}")
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@issue.command("delete")
@click.argument("issue_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def issue_delete(ctx, issue_id, yes):
    """Delete an issue."""
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Delete issue {issue_id}?", abort=True)
    try:
        client.delete(f"/issues/{issue_id}")
        console.print(f"[green]✓[/green] Deleted issue {issue_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
