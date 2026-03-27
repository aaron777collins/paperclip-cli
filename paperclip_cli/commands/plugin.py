"""Plugin management commands."""
import json
import click
from rich.console import Console
from rich.table import Table
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def plugin(ctx):
    """Manage Paperclip plugins."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@plugin.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def plugin_list(ctx, as_json):
    """List installed plugins."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get("/plugins")
        plugins = result if isinstance(result, list) else result.get("plugins", result.get("data", []))
        if as_json:
            click.echo(json.dumps(plugins, indent=2))
            return
        if not plugins:
            console.print("[yellow]No plugins installed.[/yellow]")
            return
        table = Table(title="Plugins")
        table.add_column("Name", style="bold")
        table.add_column("Version")
        table.add_column("Description")
        for p in plugins:
            table.add_row(
                p.get("name", ""),
                p.get("version", ""),
                p.get("description", ""),
            )
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@plugin.command("examples")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def plugin_examples(ctx, as_json):
    """List example plugins."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.get("/plugins/examples")
        plugins = result if isinstance(result, list) else result.get("plugins", result.get("data", []))
        if as_json:
            click.echo(json.dumps(plugins, indent=2))
            return
        if not plugins:
            console.print("[yellow]No example plugins found.[/yellow]")
            return
        table = Table(title="Example Plugins")
        table.add_column("Name", style="bold")
        table.add_column("Description")
        for p in plugins:
            table.add_row(p.get("name", ""), p.get("description", ""))
        console.print(table)
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@plugin.command("install")
@click.argument("name_or_url")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def plugin_install(ctx, name_or_url, as_json):
    """Install a plugin by name or URL."""
    client: PaperclipClient = ctx.obj
    try:
        if name_or_url.startswith("http://") or name_or_url.startswith("https://"):
            payload = {"url": name_or_url}
        else:
            payload = {"name": name_or_url}
        result = client.post("/plugins/install", payload)
        if as_json:
            click.echo(json.dumps(result, indent=2))
            return
        console.print(f"[green]✓[/green] Installed plugin [bold]{name_or_url}[/bold]")
    except PaperclipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
