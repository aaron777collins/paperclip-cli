"""Approval (board) management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def approval(ctx):
    """Manage pending approvals (board)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@approval.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def approval_list(ctx, company_id, as_json):
    """List pending approvals for a company."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/approvals")
        approvals = result if isinstance(result, list) else result.get("approvals", result.get("data", []))
        if as_json:
            click.echo(json.dumps(approvals, indent=2))
            return
        if not approvals:
            console.print("[yellow]No approvals found.[/yellow]")
            return
        table = Table(title=f"Approvals (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Type", style="bold")
        table.add_column("Status")
        table.add_column("Requested By")
        for a in approvals:
            table.add_row(
                str(a.get("id", "")),
                a.get("type", ""),
                a.get("status", ""),
                str(a.get("requestedByAgentId", "")),
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@approval.command("approve")
@click.argument("approval_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def approval_approve(ctx, approval_id, as_json):
    """Approve a pending approval."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.post(f"/approvals/{approval_id}/approve")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Approved {approval_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@approval.command("reject")
@click.argument("approval_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def approval_reject(ctx, approval_id, as_json):
    """Reject a pending approval."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.post(f"/approvals/{approval_id}/reject")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Rejected {approval_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
