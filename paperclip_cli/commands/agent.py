"""Agent management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def agent(ctx):
    """Manage Paperclip agents."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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


ADAPTER_CHOICES = [
    "claude_local",    # Claude Code CLI (recommended default)
    "codex_local",     # OpenAI Codex CLI
    "opencode_local",  # OpenCode CLI
    "pi_local",        # Pi coding agent
    "cursor",          # Cursor IDE
    "openclaw_gateway",# OpenClaw gateway (Sophie/Hermes)
    "hermes_local",    # Hermes local
]


@agent.command("create")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--name", required=True, help="Agent name")
@click.option("--role", default="general", type=click.Choice(["general", "ceo"]), help="Agent role")
@click.option("--title", default="", help="Agent title")
@click.option("--adapter", "adapter_type", default="claude_local",
              type=click.Choice(ADAPTER_CHOICES),
              help="Agent adapter/runtime (default: claude_local = Claude Code CLI)")
@click.option("--model", default="claude-sonnet-4-6",
              type=click.Choice(["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-6"]),
              help="Claude model — only applies to claude_local adapter (CEO defaults to opus)")
@click.option("--max-turns", default=50, type=int, help="Max turns per run (default: 50)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def agent_create(ctx, company_id, name, role, title, adapter_type, model, max_turns, as_json):
    """Create (hire) an agent for a company.

    \b
    Available adapters:
      claude_local     — Claude Code CLI (default, recommended)
      codex_local      — OpenAI Codex CLI
      opencode_local   — OpenCode CLI
      pi_local         — Pi coding agent
      cursor           — Cursor IDE
      openclaw_gateway — OpenClaw / Sophie
      hermes_local     — Hermes local agent

    \b
    Examples:
      paperclip-cli agent create --company <id> --name "CEO" --role ceo
      paperclip-cli agent create --company <id> --name "Engineer" --role general --model claude-opus-4-6
      paperclip-cli agent create --company <id> --name "Codex Worker" --adapter codex_local
    """
    client: PaperclipClient = ctx.obj
    # Default CEOs to opus for strategic reasoning
    if role == "ceo" and model == "claude-sonnet-4-6":
        model = "claude-opus-4-6"
    try:
        runtime_config = {}
        if adapter_type == "claude_local":
            runtime_config = {
                "model": model,
                "dangerouslySkipPermissions": True,
                "maxTurnsPerRun": max_turns,
            }
        payload = {
            "name": name,
            "role": role,
            "adapterType": adapter_type,
            "adapterConfig": {},
            "runtimeConfig": runtime_config,
        }
        if title:
            payload["title"] = title
        result = client.post(f"/companies/{company_id}/agents", payload)
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


@agent.command("update")
@click.argument("agent_id")
@click.option("--name", default=None, help="New name")
@click.option("--title", default=None, help="New title")
@click.option("--role", default=None, type=click.Choice(["general", "ceo"]), help="New role")
@click.option("--reports-to", default=None, help="Agent ID this agent reports to")
@click.option("--budget", default=None, type=int, help="Monthly budget in cents")
@click.option("--model", default=None,
              type=click.Choice(["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-6"]),
              help="Claude model override")
@click.option("--max-turns", default=None, type=int, help="Max turns per run")
@click.option("--adapter", "adapter_type", default=None,
              type=click.Choice(ADAPTER_CHOICES),
              help="Adapter/runtime (claude_local, codex_local, opencode_local, pi_local, cursor, openclaw_gateway, hermes_local)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def agent_update(ctx, agent_id, name, title, role, reports_to, budget, model, max_turns, adapter_type, as_json):
    """Update an agent."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {}
        if name is not None:
            payload["name"] = name
        if title is not None:
            payload["title"] = title
        if role is not None:
            payload["role"] = role
        if reports_to is not None:
            payload["reportsTo"] = reports_to
        if budget is not None:
            payload["budgetMonthlyCents"] = budget
        if adapter_type is not None:
            payload["adapterType"] = adapter_type
        # Handle model/maxTurns via runtimeConfig
        if model is not None or max_turns is not None:
            runtime = {}
            if model is not None:
                runtime["model"] = model
            if max_turns is not None:
                runtime["maxTurnsPerRun"] = max_turns
            payload["runtimeConfig"] = runtime
        result = client.patch(f"/agents/{agent_id}", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Updated agent {agent_id}")
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@agent.command("delete")
@click.argument("agent_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def agent_delete(ctx, agent_id, yes):
    """Delete an agent."""
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Delete agent {agent_id}?", abort=True)
    try:
        client.delete(f"/agents/{agent_id}")
        console.print(f"[green]✓[/green] Deleted agent {agent_id}")
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
        client.post(f"/agents/{agent_id}/wakeup")
        console.print(f"[green]✓[/green] Woke up agent {agent_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
