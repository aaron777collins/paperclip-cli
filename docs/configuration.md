# Configuration

Configure the CLI to point at your Paperclip server. Configuration is stored in `~/.config/paperclip-cli/config.json`.

## Quick Example

```bash
paperclip-cli configure --url http://localhost:3100
paperclip-cli status
```

---

## configure

Set the server URL and optional auth token. Only needs to be run once per environment.

```bash
paperclip-cli configure --url http://localhost:3100
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--url` | Yes | — | Paperclip server URL (e.g. `http://localhost:3100` or `https://paperclip.example.com`) |
| `--token` | No | — | Bearer token for authenticated/private servers |

### Examples

```bash
# Local dev server (no auth)
paperclip-cli configure --url http://localhost:3100

# Remote server with token auth
paperclip-cli configure --url https://paperclip.example.com --token my-secret-token
```

### Example Output

```
✓ Config saved to /home/user/.config/paperclip-cli/config.json
  URL:   http://localhost:3100
  Token: (not set)
```

### Config File Format

Stored at `~/.config/paperclip-cli/config.json`:

```json
{
  "url": "http://localhost:3100",
  "token": null
}
```

---

## status

Check that the Paperclip server is reachable and view version/mode info.

```bash
paperclip-cli status
paperclip-cli status --json
```

### Example Output

```
✓ Paperclip is running at http://localhost:3100
{
  "status": "ok",
  "version": "2026.325.0",
  "deploymentMode": "local_trusted",
  "deploymentExposure": "private",
  "authReady": true,
  "bootstrapStatus": "ready"
}
```

### JSON Output Fields

| Field | Description |
|-------|-------------|
| `status` | `"ok"` when healthy |
| `version` | Server version string |
| `deploymentMode` | `local_trusted` (dev) or `authenticated` (production) |
| `deploymentExposure` | `private` or `public` |
| `authReady` | Whether auth system is initialized |
| `bootstrapStatus` | `ready` once initial setup is complete |

### Error Cases

| Error | Cause |
|-------|-------|
| `Connection refused` | Server is not running at the configured URL |
| `Could not connect to ...` | Wrong URL in config — run `configure` again |

---

## Environment Variables

Environment variables override the saved config file for that invocation:

| Variable | Description |
|----------|-------------|
| `PAPERCLIP_URL` | Server URL |
| `PAPERCLIP_TOKEN` | Auth token |

```bash
# One-off override
PAPERCLIP_URL=http://localhost:3100 paperclip-cli company list

# Or export for the session
export PAPERCLIP_URL=http://localhost:3100
export PAPERCLIP_TOKEN=your-token
```

---

## Per-command URL override

Pass `--url` and/or `--token` directly before any subcommand:

```bash
paperclip-cli --url http://localhost:3100 company list
paperclip-cli --url https://prod.example.com --token abc123 agent list --company <id>
```

---

## API Gotchas

- **`local_trusted` mode**: No token required. The server trusts all requests. This is the default for local dev.
- **`authenticated` mode**: All requests need a `Bearer` token via `--token` or `PAPERCLIP_TOKEN`. Without it, you'll get `401 Unauthorized`.
- The config file is created automatically on first `configure` run. If `~/.config/paperclip-cli/` doesn't exist, it is created.
