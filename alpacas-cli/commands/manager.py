"""
Portfolio manager module for managing actions and command execution.
"""

from typing import Optional, Dict, List
import os
import json
from pathlib import Path
from analysis.core import AsyncAnalysisRunner
from .core import Command, CommandResult
from utils.pretty_printing import (
    pretty_print_portfolio_info,
    pretty_print_portfolios,
    pretty_print_banner,
)
from utils.helpers import ExchangeService
from .alias import AliasCommand
from .general import (
    ClearScreenCommand,
    InfoCommand,
    ExchangeStatusCommand,
    ExitCommand,
    ListAvailableTickersCommand,
    AddCustomTickersCommand,
    BannerCommand,
)
from .portfolio import (
    LoadLastPortfolioCommand,
    LoadPortfolioCommand,
    UnloadPortfolioCommand,
    InitPortfolioCommand,
    ListPortfoliosCommand,
    PortfolioOverviewCommand,
    TradeAssetCommand,
    TradeCryptoCommand,
    PortfolioPerformanceCommand,
)
from .analysis import AnalysisCommand

from colorama import Fore
from alpaca.trading.models import TradeAccount, Position


class CommandManager:
    def __init__(self, version: str = "1.0", author: str = "Leon Renn"):
        """
        Initialize the CommandManager.

        Args:
            version (str): The version of the application.
            author (str): The author of the application.
        """
        self.version: str = version
        self.author: str = author
        self.loaded_portfolio_name: Optional[str] = None
        self.keys: Dict[str, str] = {}
        self.analysis_runners: List[AsyncAnalysisRunner] = []
        self.client = None
        self.exchange_service: ExchangeService = ExchangeService()

        # Paths setup
        self.base_path: Path = Path(os.path.dirname(__file__)).parent.parent
        self.config_folder: Path = self.base_path / "configs"

        # Ensure the config folder exists
        self.config_folder.mkdir(parents=True, exist_ok=True)

        self.commands: Optional[Dict[str, Command]] = None
        self.alias_file: Path = self.config_folder / "aliases.json"
        self.aliases: Optional[Dict[str, str]] = None

    def set_client(self) -> None:
        """
        Set API keys for the Alpaca client.
        """
        pass

    def _init_commands(self) -> Dict[str, Command]:
        """
        Initialize the commands.

        Returns:
            Dict[str, Command]: A dictionary of command names and their corresponding Command objects.
        """
        return {
            "clear": ClearScreenCommand(),
            "init": InitPortfolioCommand(),
            "load": LoadPortfolioCommand(),
            "unload": UnloadPortfolioCommand(),
            "alias": AliasCommand(),
            "list": ListPortfoliosCommand(),
            "help": InfoCommand(),
            "overview": PortfolioOverviewCommand(),
            "info": InfoCommand(),
            "exchanges": ExchangeStatusCommand(self.exchange_service),
            "exit": ExitCommand(),
            # "plot_history": PlotHistoryCommand(),
            "trade_asset": TradeAssetCommand(),
            "trade_crypto": TradeCryptoCommand(),
            "load_last": LoadLastPortfolioCommand(),
            "performance": PortfolioPerformanceCommand(),
            "analysis": AnalysisCommand(context=self),
            "list_tickers": ListAvailableTickersCommand(),
            "add_tickers": AddCustomTickersCommand(),
            "banner": BannerCommand(),
        }

    def _load_aliases(self) -> None:
        """
        Load aliases from config file.
        """
        if self.aliases is None:
            self.aliases = {}

            try:
                self.config_folder.mkdir(parents=True, exist_ok=True)

                if self.alias_file.exists():
                    with self.alias_file.open("r") as f:
                        self.aliases = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load aliases: {e}")

    def _save_aliases(self) -> None:
        """
        Save aliases to config file.
        """
        try:
            with self.alias_file.open("w") as f:
                json.dump(self.aliases, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save aliases: {e}")

    def add_alias(self, alias: str, command: str) -> None:
        """
        Add a new alias and save to config.

        Args:
            alias (str): The alias to add.
            command (str): The command associated with the alias.
        """
        self._load_aliases()
        [alias] = command
        self._save_aliases()

    def remove_alias(self, alias: str) -> None:
        """
        Remove an alias and save to config.

        Args:
            alias (str): The alias to remove.
        """
        self._load_aliases()
        if alias in self.aliases:  # type: ignore
            del self.aliases[alias]  # type: ignore
            self._save_aliases()

    def get_aliases(self) -> Dict[str, str]:
        """
        Get all current aliases.

        Returns:
            Dict[str, str]: A dictionary of aliases and their corresponding commands.
        """
        self._load_aliases()
        return self.aliases.copy()  # type: ignore

    def execute_command(self, command_name: str) -> CommandResult:
        """
        Execute a command by name or alias.

        Args:
            command_name (str): The name of the command to execute.

        Returns:
            CommandResult: The result of the command execution.
        """
        self._load_aliases()
        if self.commands is None:
            self.commands = self._init_commands()

        # Check if it's an alias
        actual_command = self.aliases.get(command_name, command_name)  # type: ignore

        if actual_command in self.commands:
            return self.commands[actual_command].execute(self)
        else:
            return CommandResult(
                success=False,
                message=f"Unknown command: {command_name}\n"
                f"Type 'help' for available commands.",
            )

    def print_banner(self) -> None:
        """
        Print the application banner with styling.
        """
        pretty_print_banner(version=self.version, author=self.author)

    def run_command_loop(self) -> None:
        """
        Main command loop.
        """
        while True:
            try:
                # Get command with proper portfolio name display
                if self.loaded_portfolio_name is None:
                    command = input(">>> ").strip().lower()
                else:
                    command = (
                        input(
                            f"{Fore.GREEN}{self.loaded_portfolio_name}{Fore.RESET} >>> "
                        )
                        .strip()
                        .lower()
                    )

                # Execute command
                result = self.execute_command(command)

                # Check for exit command
                if result.should_exit:
                    self.stop_all_analyses()
                    return  # Exit the command loop

                # Handle other results
                if not result.success and result.message:
                    print(f"\n{result.message}\n")

                print()  # Empty line for better readability

            except KeyboardInterrupt:
                self.stop_all_analyses()
                print("\nExiting...")
                break
            except Exception as e:
                self.stop_all_analyses()
                print(f"\nAn error occurred: {str(e)}\n")

    def print_portfolios(self, portfolios: List[str]) -> None:
        """
        Print available portfolios in a formatted way.

        Args:
            portfolios (List[str]): A list of portfolio names.
        """
        pretty_print_portfolios(
            portfolios=portfolios, active_portfolio=self.loaded_portfolio_name
        )

    def get_overview(self, detailed: bool = False) -> None:
        """
        Get a brief overview of the current portfolio.

        Args:
            detailed (bool): Whether to include detailed information.
        """
        account_info: TradeAccount = self.client.get_account()  # type: ignore
        positions: List[Position] = self.client.get_all_positions()  # type: ignore
        pretty_print_portfolio_info(
            account_info=account_info, positions=positions, detailed=detailed
        )

    def stop_all_analyses(self) -> None:
        """
        Stop all running analyses.
        """
        for runner in getattr(self, "analysis_runners", []):
            if runner.is_running():
                runner.stop()
