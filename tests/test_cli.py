"""Tests for CLI commands."""
import json
import pytest
from click.testing import CliRunner
import responses as rsps
from paperclip_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "paperclip-cli" in result.output


def test_status_command_help(runner):
    result = runner.invoke(cli, ["status", "--help"])
    assert result.exit_code == 0


def test_company_list_help(runner):
    result = runner.invoke(cli, ["company", "list", "--help"])
    assert result.exit_code == 0


def test_company_create_help(runner):
    result = runner.invoke(cli, ["company", "create", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output


def test_agent_list_help(runner):
    result = runner.invoke(cli, ["agent", "list", "--help"])
    assert result.exit_code == 0
    assert "--company" in result.output


def test_goal_create_help(runner):
    result = runner.invoke(cli, ["goal", "create", "--help"])
    assert result.exit_code == 0


def test_approval_help(runner):
    result = runner.invoke(cli, ["approval", "--help"])
    assert result.exit_code == 0


def test_plugin_help(runner):
    result = runner.invoke(cli, ["plugin", "--help"])
    assert result.exit_code == 0


@rsps.activate
def test_status_json(runner):
    rsps.add(rsps.GET, "http://localhost:3100/api/health", json={"status": "ok", "version": "1.0"})
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "status", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"


@rsps.activate
def test_company_list_json(runner):
    rsps.add(
        rsps.GET,
        "http://localhost:3100/api/companies",
        json=[{"id": "1", "name": "TenantHelper", "description": "AI property management"}],
    )
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "company", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["name"] == "TenantHelper"


@rsps.activate
def test_company_create_json(runner):
    rsps.add(rsps.POST, "http://localhost:3100/api/companies", json={"id": "new-1", "name": "CashClaw"}, status=201)
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "company", "create", "--name", "CashClaw", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "CashClaw"


@rsps.activate
def test_company_update_json(runner):
    rsps.add(rsps.PATCH, "http://localhost:3100/api/companies/1", json={"id": "1", "name": "Updated"})
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "company", "update", "1", "--name", "Updated", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "Updated"


@rsps.activate
def test_company_delete_yes(runner):
    rsps.add(rsps.DELETE, "http://localhost:3100/api/companies/1", status=204)
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "company", "delete", "1", "--yes"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


@rsps.activate
def test_agent_create_json(runner):
    rsps.add(
        rsps.POST,
        "http://localhost:3100/api/companies/1/agents",
        json={"id": "agent-1", "name": "Bob"},
        status=201,
    )
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "agent", "create", "--company", "1", "--name", "Bob", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "Bob"


@rsps.activate
def test_agent_create_uses_correct_endpoint(runner):
    """Ensure agent create hits /companies/:id/agents not /agent-hires."""
    rsps.add(
        rsps.POST,
        "http://localhost:3100/api/companies/42/agents",
        json={"id": "a1", "name": "Alice"},
        status=201,
    )
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "agent", "create", "--company", "42", "--name", "Alice", "--json"],
    )
    assert result.exit_code == 0
    assert len(rsps.calls) == 1
    assert "/api/companies/42/agents" in rsps.calls[0].request.url


@rsps.activate
def test_agent_update_json(runner):
    rsps.add(rsps.PATCH, "http://localhost:3100/api/agents/a1", json={"id": "a1", "name": "Updated"})
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "agent", "update", "a1", "--name", "Updated", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "Updated"


@rsps.activate
def test_agent_delete_yes(runner):
    rsps.add(rsps.DELETE, "http://localhost:3100/api/agents/a1", json={"ok": True})
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "agent", "delete", "a1", "--yes"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


@rsps.activate
def test_goal_update_json(runner):
    rsps.add(rsps.PATCH, "http://localhost:3100/api/goals/g1", json={"id": "g1", "title": "New Title"})
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "goal", "update", "g1", "--title", "New Title", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["title"] == "New Title"


@rsps.activate
def test_goal_delete_yes(runner):
    rsps.add(rsps.DELETE, "http://localhost:3100/api/goals/g1", status=204)
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "goal", "delete", "g1", "--yes"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


@rsps.activate
def test_issue_update_json(runner):
    rsps.add(rsps.PATCH, "http://localhost:3100/api/issues/i1", json={"id": "i1", "status": "done"})
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "issue", "update", "i1", "--status", "done", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "done"


@rsps.activate
def test_issue_delete_yes(runner):
    rsps.add(rsps.DELETE, "http://localhost:3100/api/issues/i1", status=204)
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "issue", "delete", "i1", "--yes"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


@rsps.activate
def test_approval_list_json(runner):
    rsps.add(
        rsps.GET,
        "http://localhost:3100/api/companies/1/approvals",
        json=[{"id": "ap1", "type": "budget", "status": "pending", "requestedByAgentId": "a1"}],
    )
    result = runner.invoke(
        cli,
        ["--url", "http://localhost:3100", "approval", "list", "--company", "1", "--json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["id"] == "ap1"


@rsps.activate
def test_approval_approve(runner):
    rsps.add(rsps.POST, "http://localhost:3100/api/approvals/ap1/approve", json={"ok": True})
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "approval", "approve", "ap1"])
    assert result.exit_code == 0
    assert "Approved" in result.output


@rsps.activate
def test_approval_reject(runner):
    rsps.add(rsps.POST, "http://localhost:3100/api/approvals/ap1/reject", json={"ok": True})
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "approval", "reject", "ap1"])
    assert result.exit_code == 0
    assert "Rejected" in result.output


@rsps.activate
def test_plugin_list_json(runner):
    rsps.add(rsps.GET, "http://localhost:3100/api/plugins", json=[])
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "plugin", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)


@rsps.activate
def test_plugin_examples_json(runner):
    rsps.add(
        rsps.GET,
        "http://localhost:3100/api/plugins/examples",
        json=[{"name": "example-plugin", "description": "An example"}],
    )
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "plugin", "examples", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["name"] == "example-plugin"


@rsps.activate
def test_plugin_install(runner):
    rsps.add(rsps.POST, "http://localhost:3100/api/plugins/install", json={"ok": True})
    result = runner.invoke(cli, ["--url", "http://localhost:3100", "plugin", "install", "my-plugin"])
    assert result.exit_code == 0
    assert "Installed" in result.output
