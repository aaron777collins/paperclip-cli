# secret

Secrets are encrypted key-value pairs stored per-company. Agents can access secrets at runtime for API keys, tokens, and other credentials.

## Quick Example

```bash
# List secrets for a company
paperclip-cli secret list --company "$CO"
paperclip-cli secret list --company "$CO" --json
```

> **Note:** Secrets are read-only via the CLI. Creating/updating/deleting secrets requires direct API calls or the Paperclip web UI. The CLI only supports listing (names only — values are never returned).

---

## secret list

List secrets for a company. Only names and metadata are returned — secret values are never exposed by the API.

```bash
paperclip-cli secret list --company <company-id>
paperclip-cli secret list --company <company-id> --json
```

### Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | — | Company ID |
| `--json` | No | false | Output raw JSON array |

### Example Output

```
         Secrets (Company: 6ef9c662-…)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                   ┃ Name                   ┃ Created At          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ l2m3n4o5-p6q7-8901-2345-678901234567 │ OPENAI_API_KEY         │ 2026-03-01T12:00:00 │
│ m3n4o5p6-q7r8-9012-3456-789012345678 │ SLACK_WEBHOOK_URL      │ 2026-03-10T09:30:00 │
└──────────────────────────────────────┴────────────────────────┴─────────────────────┘
```

### JSON Output Fields

```json
[
  {
    "id": "l2m3n4o5-p6q7-8901-2345-678901234567",
    "name": "OPENAI_API_KEY",
    "companyId": "6ef9c662-776f-43e0-8e7e-55f36c309edb",
    "createdAt": "2026-03-01T12:00:00.000Z"
  }
]
```

> The `value` field is never included in any API response. Secrets are write-only — once set, you can only see the name.

---

## local_trusted Mode vs Production

### local_trusted mode (default dev setup)

In `local_trusted` mode (the default when running Paperclip locally), secrets are typically not used. The `secret list` command will return an empty list:

```
No secrets found.
Note: In local_trusted mode, secrets are not required.
```

This is expected behavior. Agents in local dev mode don't need credentials because the server trusts all requests.

### Production (authenticated mode)

In a production deployment with `deploymentMode: authenticated`:

- Agents look up secrets by name at runtime (e.g. `OPENAI_API_KEY`)
- Secrets are encrypted at rest
- Only the names are returned by the API — values are stored encrypted and only decrypted inside the agent runtime

To create secrets, use the Paperclip web UI or make a direct `POST /companies/:id/secrets` API call with `{"name": "...", "value": "..."}`.

---

## API Gotchas

- **Values are never returned.** The API is designed so secret values can never be read back once set. If you lose a secret value, you must re-set it.
- **local_trusted = no secrets needed.** In dev mode, agents run without credentials. Don't be alarmed if `secret list` is empty.
- **No CLI create/update/delete.** The current CLI only supports `list`. Use the web UI or API directly to manage secret values.
- **Scoped per company.** Secrets set in one company are not visible to another.
