# paperclip-cli

Python CLI for [Paperclip](https://github.com/paperclipai/paperclip) — the open-source AI agent orchestration platform.

Manage your AI companies, agents, goals, and tasks from the terminal.

## Installation

```bash
pip install paperclip-cli
```

Or from source:
```bash
git clone https://github.com/aaron777collins/paperclip-cli.git
cd paperclip-cli
pip install -e .
```

## Quick Start

```bash
# Configure (one-time)
paperclip-cli configure --url http://localhost:3100

# Check server health
paperclip-cli status

# Create a company
paperclip-cli company create --name "TenantHelper" --description "AI property management"

# List companies
paperclip-cli company list

# Add an agent
paperclip-cli agent create --company <company-id> --name "Coordinator" --role "Project Coordinator"

# List agents
paperclip-cli agent list --company <company-id>

# Create a goal
paperclip-cli goal create --company <company-id> --title "Build MVP"

# Create an issue/task
paperclip-cli issue create --company <company-id> --title "Implement login page"

# Wake up an agent
paperclip-cli agent wakeup <agent-id>
```

## JSON Output

Every command supports `--json` for machine-readable output:

```bash
paperclip-cli company list --json
paperclip-cli status --json
```

## Environment Variables

```bash
export PAPERCLIP_URL=http://localhost:3100
export PAPERCLIP_TOKEN=your-token
```

## All Commands

```
paperclip-cli configure    Configure server URL and token
paperclip-cli status       Check server health

paperclip-cli company
  list                     List all companies
  create --name X          Create a company
  get <id>                 Get company details
  delete <id>              Delete a company

paperclip-cli agent
  list --company X         List agents for a company
  create --company X       Hire an agent
  get <id>                 Get agent details
  wakeup <id>              Wake up an agent

paperclip-cli goal
  list --company X         List goals
  create --company X       Create a goal

paperclip-cli issue
  list --company X         List issues/tasks
  create --company X       Create an issue
```

## Running Paperclip

```bash
# Clone and start Paperclip
git clone https://github.com/paperclipai/paperclip.git
cd paperclip
pnpm install
pnpm dev
# Server at http://localhost:3100
```

## License

MIT
