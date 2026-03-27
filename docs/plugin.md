# plugin

Manage Paperclip plugins that extend agent capabilities. Plugins add new tools and integrations that agents can use during task execution.

## Quick Example

```bash
# Browse available example plugins
paperclip-cli plugin examples

# Install a plugin
paperclip-cli plugin install my-plugin-name
paperclip-cli plugin install https://registry.example.com/plugins/my-plugin

# List installed plugins
paperclip-cli plugin list
```

---

## plugin list

List all currently installed plugins on the server.

```bash
paperclip-cli plugin list
paperclip-cli plugin list --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output raw JSON array |

### Example Output

```
             Plugins
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                 ┃ Version   ┃ Description                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ file-manager         │ 1.2.0     │ Read and write files from agent tasks   │
│ http-client          │ 0.9.3     │ Make HTTP requests from agent tasks     │
└──────────────────────┴───────────┴─────────────────────────────────────────┘
```

### JSON Output Fields

```json
[
  {
    "name": "file-manager",
    "version": "1.2.0",
    "description": "Read and write files from agent tasks",
    "installedAt": "2026-03-01T12:00:00.000Z"
  }
]
```

---

## plugin examples

Browse example plugins available from the Paperclip plugin registry.

```bash
paperclip-cli plugin examples
paperclip-cli plugin examples --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output raw JSON array |

### Example Output

```
          Example Plugins
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                 ┃ Description                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ file-manager         │ Read and write files from agent tasks                 │
│ http-client          │ Make HTTP requests from agent tasks                   │
│ database-query       │ Run SQL queries from agent tasks                      │
│ slack-notifier       │ Post messages to Slack from agent tasks               │
└──────────────────────┴───────────────────────────────────────────────────────┘
```

---

## plugin install

Install a plugin by name (looks up the registry) or by full URL.

```bash
# Install by name
paperclip-cli plugin install file-manager

# Install from URL
paperclip-cli plugin install https://registry.paperclip.ai/plugins/http-client
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name-or-url` | Yes | Plugin name (for registry lookup) or full HTTP/HTTPS URL |

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--json` | No | false | Output installation result as JSON |

### Example Output

```
✓ Installed plugin file-manager
```

### How it Works

- If the argument starts with `http://` or `https://`, it is treated as a direct URL (`{"url": ...}` payload).
- Otherwise it is treated as a plugin name (`{"name": ...}` payload) and the server resolves it from the registry.

### Error Cases

| Error | Cause |
|-------|-------|
| `404 Not Found` | Plugin name not found in registry |
| `400 Bad Request` | Invalid URL format |
| `409 Conflict` | Plugin already installed |

---

## API Gotchas

- Plugin availability depends on what is in the Paperclip server's registry. On a fresh local server, `plugin examples` may return an empty list.
- Plugin installation is global on the server — plugins are not scoped per company.
- Installed plugins are available to all agents on the server.
- There is no `plugin uninstall` command in the current CLI version.
