"""Secret management commands.

Secrets are encrypted credentials stored per-company for agent use.
In local_trusted mode the list will be empty — secrets are used in
authenticated/production deployments where agents need API keys etc.
"""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def secret(ctx):
    """Manage company secrets (encrypted agent credentials).

    \b
    Secrets are encrypted key-value pairs that agents can access at runtime.
    In local_trusted mode (default dev setup) secrets are not required.
    In production authenticated mode, secrets store API keys, tokens, etc.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@secret.command("list")
@click.option("--company", "company_id", required=True, help="Company ID")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def secret_list(ctx, company_id, as_json):
    """List secrets for a company (names only, values never returned by API)."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}/secrets")
        secrets = result if isinstance(result, list) else result.get("secrets", [])
        if as_json:
            click.echo(json.dumps(secrets, indent=2))
            return
        if not secrets:
            console.print("[yellow]No secrets found.[/yellow]")
            console.print("[dim]Note: In local_trusted mode, secrets are not required.[/dim]")
            return
        table = Table(title=f"Secrets (Company: {company_id})")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Created At")
        for s in secrets:
            table.add_row(
                str(s.get("id", "")),
                s.get("name", ""),
                str(s.get("createdAt", ""))[:19],
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
