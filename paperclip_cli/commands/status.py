"""Status / health check commands."""
import json
import click
from rich.console import Console
from ..client import PaperclipClient, PaperclipError

console = Console()


@click.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def status(ctx, as_json):
    """Check Paperclip server health."""
    client: PaperclipClient = ctx.obj
    try:
        result = client.health()
        if as_json:
            click.echo(json.dumps({"status": "ok", "url": client.base_url, **result}, indent=2))
            return
        console.print(f"[green]✓[/green] Paperclip is running at [bold]{client.base_url}[/bold]")
        if result:
            console.print_json(json.dumps(result))
    except PaperclipError as e:
        if as_json:
            click.echo(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            console.print(f"[red]✗[/red] Paperclip is not reachable at {client.base_url}")
            console.print(f"  {e}")
        raise SystemExit(1)
    except Exception as e:
        if as_json:
            click.echo(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            console.print(f"[red]✗[/red] Could not connect to {client.base_url}: {e}")
        raise SystemExit(1)
