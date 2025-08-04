"""
Commands available via the command manager.
"""

from .core import (
    Command,
    CommandResult,
    ExchangeStatus,
)
from typing import List
from utils.pretty_printing import (
    pretty_print_exchange_status,
    pretty_print_info_text,
    pretty_print_available_ticker_sets,
    pretty_print_banner,
)
from utils.helpers import ExchangeService
from pytz import timezone
import datetime as dt
import os
import json
from utils.input_validation import (
    get_validated_input,
    is_non_empty_string,
    is_valid_ticker,
)


class ClearScreenCommand(Command):
    """
    Command to clear the terminal screen.
    This command uses the system's clear command to clear the terminal.
    """

    def execute(self, context) -> CommandResult:
        os.system("cls" if os.name == "nt" else "clear")
        return CommandResult(success=True)

    def description(self) -> str:
        return "Clears the terminal screen."


class BannerCommand(Command):
    """
    Command to display the banner of the application.
    This command prints the banner with version and author information.
    """

    def execute(self, context) -> CommandResult:
        pretty_print_banner(version=context.version, author=context.author)
        return CommandResult(success=True)

    def description(self) -> str:
        return "Displays the application banner with version and author information."


class InfoCommand(Command):
    """
    Command to display information about available commands.
    """

    def execute(self, context) -> CommandResult:
        pretty_print_info_text(commands=context.commands)
        return CommandResult(success=True)

    def description(self) -> str:
        return "Displays information about available commands."


class ExchangeStatusCommand(Command):
    """
    Command to check the status of major stock exchanges.
    """

    def __init__(self, exchange_service: ExchangeService):
        self.exchange_service: ExchangeService = exchange_service

    def execute(self, context) -> CommandResult:
        status_results: List[ExchangeStatus] = []
        is_open: bool
        status: str
        for exchange in self.exchange_service.STOCK_EXCHANGES.keys():
            is_open, status = self.exchange_service.is_exchange_open(exchange)
            current_time = dt.datetime.now(
                timezone(self.exchange_service.STOCK_EXCHANGES[exchange]["timezone"])
            ).strftime("%H:%M:%S")
            status_results.append(
                ExchangeStatus(
                    is_open=is_open,
                    name=exchange,
                    current_time=current_time,
                    status_message=status,
                )
            )
        pretty_print_exchange_status(status_results=status_results)
        return CommandResult(success=True, data=status_results)

    def description(self) -> str:
        return "Displays the current status of major stock exchanges."


class ExitCommand(Command):
    """
    Command to exit the program.
    """

    def execute(self, context) -> CommandResult:
        print("Exiting the program...")
        return CommandResult(
            success=True, message="exit", should_exit=True  # Explicitly indicate exit
        )

    def description(self) -> str:
        return "Exits the program."


class ListAvailableTickersCommand(Command):
    """
    Command to list all available ticker sets from the tickers.json file.
    """

    def execute(self, context) -> CommandResult:
        ticker_file = context.config_folder / "tickers.json"
        if not ticker_file.exists():
            return CommandResult(success=False, message="Ticker file not found.")
        try:
            with ticker_file.open("r") as f:
                data = json.load(f)
            ticker_sets = data.get("list_of_tickers", [])
            if not ticker_sets:
                return CommandResult(success=True, message="No ticker sets found.")
            pretty_print_available_ticker_sets(ticker_sets=ticker_sets)
            return CommandResult(success=True)
        except Exception as e:
            return CommandResult(
                success=False, message=f"Error reading ticker file: {str(e)}"
            )

    def description(self) -> str:
        return "Lists all available ticker sets from the configuration file."


class AddCustomTickersCommand(Command):
    """
    Command to add a custom collection of tickers to the tickers.json file.
    """

    def execute(self, context) -> CommandResult:
        ticker_file = context.config_folder / "tickers.json"
        if not ticker_file.exists():
            ticker_file.parent.mkdir(parents=True, exist_ok=True)
            with ticker_file.open("w") as f:
                json.dump({"list_of_tickers": []}, f, indent=4)

        try:
            with ticker_file.open("r") as f:
                data = json.load(f)

            identifier = get_validated_input(
                "Enter a unique identifier for the ticker set: ", [is_non_empty_string]  # type: ignore
            )
            if any(ts["identifier"] == identifier for ts in data["list_of_tickers"]):
                return CommandResult(
                    success=False, message="Identifier already exists."
                )

            description = get_validated_input(
                "Enter a description for the ticker set: ", [is_non_empty_string]  # type: ignore
            )
            tickers_input = get_validated_input(
                "Enter tickers separated by commas (e.g., AAPL,MSFT,GOOGL): ",
                [is_non_empty_string],  # type: ignore
            )
            tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

            if not tickers:
                return CommandResult(success=False, message="No tickers provided.")

            invalid_tickers = [t for t in tickers if not is_valid_ticker(t)]
            if invalid_tickers:
                return CommandResult(
                    success=False,
                    message=f"Invalid tickers found: {', '.join(invalid_tickers)}. Only uppercase letters allowed (1-5 characters).",
                )

            new_entry = {
                "identifier": identifier,
                "description": description,
                "tickers": tickers,
            }

            data["list_of_tickers"].append(new_entry)

            with ticker_file.open("w") as f:
                json.dump(data, f, indent=4)

            return CommandResult(
                success=True, message=f"Ticker set '{identifier}' added successfully."
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Error updating ticker file: {str(e)}"
            )

    def description(self) -> str:
        return "Adds a custom collection of tickers to the configuration file."
