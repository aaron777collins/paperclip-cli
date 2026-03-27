"""Company management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def company(ctx):
    """Manage Paperclip companies."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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


@company.command("update")
@click.argument("company_id")
@click.option("--name", default=None, help="New name")
@click.option("--description", default=None, help="New description")
@click.option("--mission", default=None, help="New mission statement")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def company_update(ctx, company_id, name, description, mission, as_json):
    """Update a company."""
    client: PaperclipClient = ctx.obj
    try:
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if mission is not None:
            payload["mission"] = mission
        result = client.patch(f"/companies/{company_id}", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Updated company {company_id}")
        console.print_json(json.dumps(result))
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@company.command("delete")
@click.argument("company_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.option("--force", is_flag=True, help="Attempt hard delete (may fail if company has skills attached)")
@click.pass_context
def company_delete(ctx, company_id, yes, force):
    """Delete or archive a company.

    \b
    ⚠️  Paperclip cannot hard-delete companies that have default skills
    attached (FK constraint). This command archives instead of deletes by
    default — archived companies are hidden from the sidebar and stop scheduling.

    Use --force to attempt a hard delete (only works on companies without skills).
    Use 'company archive' directly for the recommended workflow.
    """
    client: PaperclipClient = ctx.obj
    if not yes:
        click.confirm(f"Archive company {company_id}? (use --force for hard delete)", abort=True)
    try:
        if force:
            client.delete(f"/companies/{company_id}")
            console.print(f"[green]✓[/green] Deleted company {company_id}")
        else:
            client.post(f"/companies/{company_id}/archive")
            console.print(f"[green]✓[/green] Archived company {company_id} (hidden from sidebar)")
            console.print(f"[dim]  Use 'company unarchive {company_id}' to restore, or --force to attempt hard delete[/dim]")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@company.command("archive")
@click.argument("company_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def company_archive(ctx, company_id, as_json):
    """Archive a company (hides from sidebar, stops all agent scheduling).

    \b
    Prefer archive over delete — Paperclip cannot hard-delete companies that
    have default skills attached. Archive is safe and reversible.

    Use 'company unarchive <id>' to restore.
    """
    client: PaperclipClient = ctx.obj
    try:
        result = client.post(f"/companies/{company_id}/archive")
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Archived company {company_id} — hidden from sidebar")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@company.command("unarchive")
@click.argument("company_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def company_unarchive(ctx, company_id, as_json):
    """Restore an archived company (sets status back to active)."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.patch(f"/companies/{company_id}", {"status": "active"})
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Unarchived company {company_id} — status: active")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
