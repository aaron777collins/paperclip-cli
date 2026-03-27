"""Main CLI entry point for paperclip-cli."""
import json
from pathlib import Path

import click
from rich.console import Console

from .client import PaperclipClient
from .commands.company import company
from .commands.agent import agent
from .commands.goal import goal
from .commands.issue import issue
from .commands.status import status
from .commands.approval import approval
from .commands.plugin import plugin
from .commands.project import project
from .commands.routine import routine
from .commands.heartbeat import heartbeat
from .commands.secret import secret

CONFIG_PATH = Path.home() / ".config" / "paperclip-cli" / "config.json"
console = Console()

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option("--url", envvar="PAPERCLIP_URL", default=None, help="Paperclip server URL")
@click.option("--token", envvar="PAPERCLIP_TOKEN", default=None, help="Auth token")
@click.version_option(package_name="paperclip-cli")
@click.pass_context
def cli(ctx, url, token):
    """paperclip-cli — manage your Paperclip AI company from the terminal.

    Configure once with: paperclip-cli configure --url http://localhost:3100

    \b
    Quick start:
      paperclip-cli status
      paperclip-cli company list
      paperclip-cli company create --name "My Company"
      paperclip-cli agent list --company <id>
    """
    ctx.ensure_object(dict)
    ctx.obj = PaperclipClient(base_url=url, token=token)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option("--url", required=True, help="Paperclip server URL (e.g. http://localhost:3100)")
@click.option("--token", default="", help="Auth token (if server requires authentication)")
def configure(url, token):
    """Configure the CLI with server URL and auth token."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = {}
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    config["base_url"] = url.rstrip("/")
    if token:
        config["token"] = token
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    console.print(f"[green]✓[/green] Configuration saved to {CONFIG_PATH}")
    console.print(f"  URL: {url}")
    if token:
        console.print("  Token: ****")


# Register command groups
cli.add_command(company)
cli.add_command(agent)
cli.add_command(goal)
cli.add_command(issue)
cli.add_command(status)
cli.add_command(approval)
cli.add_command(plugin)
cli.add_command(project)
cli.add_command(routine)
cli.add_command(heartbeat)
cli.add_command(secret)

# Alias: paperclip-cli without arguments → help
cli.add_command(status, name="health")


if __name__ == "__main__":
    cli()
