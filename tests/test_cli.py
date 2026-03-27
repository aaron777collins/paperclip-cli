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
