"""Heartbeat run commands.

Heartbeat runs are records of agent activations — when an agent was woken up,
why (invocationSource), and whether it succeeded or failed.
"""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def heartbeat(ctx):
    """View agent heartbeat run history.

    Heartbeat runs show when agents were activated, the source of activation,
    and whether the run succeeded or failed.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@heartbeat.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--limit", default=None, type=int, help="Max number of results to show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def heartbeat_list(ctx, company_id, limit, as_json):
    """List recent agent heartbeat runs for a company.

    Shows when agents were activated, the trigger source, and run status.
    Useful for debugging agent activity and diagnosing failures.
    """
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/heartbeat-runs")
        runs = result if isinstance(result, list) else result.get("runs", [])
        if limit:
            runs = runs[:limit]
        if as_json:
            click.echo(json.dumps(runs, indent=2))
            return
        if not runs:
            console.print("[yellow]No heartbeat runs found.[/yellow]")
            return
        table = Table(title=f"Heartbeat Runs (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Agent ID", style="dim")
        table.add_column("Status")
        table.add_column("Source")
        table.add_column("Trigger")
        table.add_column("Started At")
        for r in runs:
            status = r.get("status", "")
            status_color = "green" if status == "success" else ("red" if status == "failed" else "yellow")
            table.add_row(
                str(r.get("id", ""))[:8] + "…",
                str(r.get("agentId", ""))[:8] + "…",
                f"[{status_color}]{status}[/{status_color}]",
                r.get("invocationSource", ""),
                r.get("triggerDetail", ""),
                str(r.get("startedAt", ""))[:19],
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
