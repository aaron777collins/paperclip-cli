"""Project management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def project(ctx):
    """Manage projects within a company.

    Projects are containers for grouping issues and routines.
    Each project belongs to a company and optionally a goal.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@project.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def project_list(ctx, company_id, as_json):
    """List all projects for a company."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/projects")
        projects = result if isinstance(result, list) else result.get("projects", [])
        if as_json:
            click.echo(json.dumps(projects, indent=2))
            return
        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return
        table = Table(title=f"Projects (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Status")
        table.add_column("Description")
        for p in projects:
            table.add_row(
                str(p.get("id", "")),
                p.get("name", ""),
                p.get("status", ""),
                (p.get("description") or "")[:60],
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@project.command("create")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--name", required=True, help="Project name")
@click.option("--description", default=None, help="Project description")
@click.option("--goal", "goal_id", default=None, help="Goal ID to link this project to")
@click.option("--lead", "lead_agent_id", default=None, help="Lead agent ID")
@click.option("--color", default=None, help="Color hex (e.g. #6366f1)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def project_create(ctx, company_id, name, description, goal_id, lead_agent_id, color, as_json):
    """Create a new project."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {"name": name}
        if description:
            payload["description"] = description
        if goal_id:
            payload["goalId"] = goal_id
        if lead_agent_id:
            payload["leadAgentId"] = lead_agent_id
        if color:
            payload["color"] = color
        result = client.post(f"/companies/{company_id}/projects", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        project_id = result.get("id", "?")
        console.print(f"[green]✓[/green] Created project [bold]{name}[/bold] (ID: {project_id})")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@project.command("get")
@click.argument("project_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def project_get(ctx, project_id, as_json):
    """Get project details."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/projects/{project_id}")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@project.command("update")
@click.argument("project_id")
@click.option("--name", default=None, help="New name")
@click.option("--description", default=None, help="New description")
@click.option("--status", default=None,
              type=click.Choice(["backlog", "planned", "in_progress", "completed", "cancelled", "paused"]),
              help="New status")
@click.option("--goal", "goal_id", default=None, help="Goal ID to link to")
@click.option("--lead", "lead_agent_id", default=None, help="Lead agent ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def project_update(ctx, project_id, name, description, status, goal_id, lead_agent_id, as_json):
    """Update a project."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if goal_id is not None:
            payload["goalId"] = goal_id
        if lead_agent_id is not None:
            payload["leadAgentId"] = lead_agent_id
        if not payload:
            console.print("[yellow]No fields to update. Use --name, --description, --status, --goal, or --lead.[/yellow]")
            raise SystemExit(1)
        result = client.patch(f"/projects/{project_id}", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Updated project {project_id}")
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@project.command("delete")
@click.argument("project_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def project_delete(ctx, project_id, yes):
    """Delete a project. ⚠️ Also deletes all routines in the project (cascade)."""
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Delete project {project_id}? This will also delete all routines in it.", abort=True)
    try:
        client.delete(f"/projects/{project_id}")
        console.print(f"[green]✓[/green] Deleted project {project_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
