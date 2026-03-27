"""Agent management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group()
def agent():
    """Manage Paperclip agents."""


@agent.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def agent_list(ctx, company_id, as_json):
    """List agents for a company."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/agents")
        agents = result if isinstance(result, list) else result.get("agents", result.get("data", [result]))
        if as_json:
            click.echo(json.dumps(agents, indent=2))
            return
        if not agents:
            console.print("[yellow]No agents found.[/yellow]")
            return
        table = Table(title=f"Agents (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Role")
        table.add_column("Status")
        for a in agents:
            table.add_row(
                str(a.get("id", "")),
                a.get("name", ""),
                a.get("role", a.get("jobTitle", "")),
                a.get("status", a.get("runtimeState", "unknown")),
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@agent.command("create")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--name", required=True, help="Agent name")
@click.option("--role", default="", help="Agent role/job title")
@click.option("--instructions", default="", help="Agent instructions")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def agent_create(ctx, company_id, name, role, instructions, as_json):
    """Create (hire) an agent for a company."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {"name": name}
        if role:
            payload["jobTitle"] = role
        if instructions:
            payload["instructions"] = instructions
        result = client.post(f"/companies/{company_id}/agent-hires", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        agent_id = result.get("id", "?")
        console.print(f"[green]✓[/green] Created agent [bold]{name}[/bold] (ID: {agent_id})")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@agent.command("get")
@click.argument("agent_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def agent_get(ctx, agent_id, as_json):
    """Get agent details."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/agents/{agent_id}")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@agent.command("wakeup")
@click.argument("agent_id")
@click.pass_context
def agent_wakeup(ctx, agent_id):
    """Wake up an agent to process their inbox."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.post(f"/agents/{agent_id}/wakeup")
        console.print(f"[green]✓[/green] Woke up agent {agent_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
