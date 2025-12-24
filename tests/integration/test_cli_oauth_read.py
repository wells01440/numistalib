"""Integration tests for OAuth CLI commands (READ operations).

Tests:
- oauth --help
- oauth token --help
- oauth exchange-code --help
"""

from click.testing import CliRunner


class TestOAuthHelp:
    """Integration tests for OAuth CLI help output."""

    def test_oauth_help(self, cli_runner: CliRunner, cli) -> None:
        result = cli_runner.invoke(cli, ["oauth", "--help"])
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_oauth_token_help(self, cli_runner: CliRunner, cli) -> None:
        result = cli_runner.invoke(cli, ["oauth", "token", "--help"])
        assert result.exit_code == 0, f"Command failed: {result.output}"

    def test_oauth_exchange_code_help(self, cli_runner: CliRunner, cli) -> None:
        result = cli_runner.invoke(cli, ["oauth", "exchange-code", "--help"])
        assert result.exit_code == 0, f"Command failed: {result.output}"
