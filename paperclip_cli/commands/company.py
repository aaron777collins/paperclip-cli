"""Company management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group()
def company():
    """Manage Paperclip companies."""


@company.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def company_list(ctx, as_json):
    """List all companies."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get("/companies")
        companies = result if isinstance(result, list) else result.get("companies", result.get("data", [result]))
        if as_json:
            click.echo(json.dumps(companies, indent=2))
            return
        if not companies:
            console.print("[yellow]No companies found.[/yellow]")
            return
        table = Table(title="Companies")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Description")
        for c in companies:
            table.add_row(str(c.get("id", "")), c.get("name", ""), c.get("description", ""))
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@company.command("create")
@click.option("--name", required=True, help="Company name")
@click.option("--description", default="", help="Company description")
@click.option("--mission", default="", help="Company mission statement")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def company_create(ctx, name, description, mission, as_json):
    """Create a new company."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {"name": name}
        if description:
            payload["description"] = description
        if mission:
            payload["mission"] = mission
        result = client.post("/companies", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        company_id = result.get("id", "?")
        console.print(f"[green]✓[/green] Created company [bold]{name}[/bold] (ID: {company_id})")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@company.command("get")
@click.argument("company_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def company_get(ctx, company_id, as_json):
    """Get company details."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get(f"/companies/{company_id}")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@company.command("delete")
@click.argument("company_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def company_delete(ctx, company_id, yes):
    """Delete a company."""
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Delete company {company_id}?", abort=True)
    try:
        client.delete(f"/companies/{company_id}")
        console.print(f"[green]✓[/green] Deleted company {company_id}")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
