"""
Commands available via the command manager.
"""

from .core import Command, CommandResult
from typing import Dict, List, Optional, Callable, Union, Any
from colorama import Fore
from utils.helpers import (
    read_available_portfolios,
    read_portfolio_keys,
    require_internet,
)
from datetime import datetime
import os
from pathlib import Path
import json

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, CryptoLatestQuoteRequest
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    StopLimitOrderRequest,
    GetPortfolioHistoryRequest,
)
from alpaca.trading.models import Asset

from tabulate import tabulate
import matplotlib.pyplot as plt
from utils.pretty_printing import pretty_print_portfolios
from utils.input_validation import (
    get_validated_input,
    is_non_empty_string,
    is_valid_number,
    is_yes_or_no,
    is_buy_or_sell,
    is_positive_number,
    is_valid_order_type,
    is_valid_time_in_force,
    is_valid_ticker,
    get_password,
)


class LoadPortfolioCommand(Command):
    def execute(self, context) -> CommandResult:
        # Check if there's already an active portfolio
        if context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message=f"Portfolio '{context.loaded_portfolio_name}' is currently active. "
                "Please unload the current portfolio before loading a new one.",
            )

        try:
            # TODO: Think about restrictions on portfolio names
            portfolio_name = get_validated_input(
                "Enter the name of the portfolio: ", [is_non_empty_string]  # type: ignore
            )
            result = self._load_portfolio(portfolio_name, context)

            if not result.success:
                return result

            # Update config with last loaded portfolio
            self._update_portfolio_config(portfolio_name, context)

            return CommandResult(
                success=True,
                message=f"Successfully loaded portfolio: {portfolio_name}",
                data=result.data,
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Failed to load portfolio: {str(e)}"
            )

    def description(self) -> str:
        return "Loads an existing portfolio from storage. Requires no active portfolio."

    def _load_portfolio(self, portfolio_name: str, context) -> CommandResult:
        """Attempts to load the specified portfolio."""
        if not os.path.exists(context.config_folder):
            return CommandResult(success=False, message="No portfolios found.")

        portfolio_path = os.path.join(context.config_folder, "alpaca.json")
        available_portfolios: List[str] = read_available_portfolios(portfolio_path)
        if portfolio_name not in available_portfolios:
            return CommandResult(
                success=False,
                message=f"Portfolio '{portfolio_name}' does not exist. Available portfolios: {' - '.join(available_portfolios)}",
            )

        # Update command manager state
        context.loaded_portfolio_name = portfolio_name
        context.keys = read_portfolio_keys(portfolio_path, portfolio_name)
        context.set_client()

        return CommandResult(success=True)

    def _update_portfolio_config(self, portfolio_name: str, context) -> None:
        """Updates the portfolio configuration file."""
        # Write the loaded portfolio name into the last loaded portfolio of the config
        config_path = Path(context.config_folder)
        portfolio_path = config_path / "alpaca.json"
        if not portfolio_path.exists():
            portfolio_path.parent.mkdir(parents=True, exist_ok=True)
            portfolio_path.touch()
        with open(portfolio_path, "r+") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}

            config["last_used"] = portfolio_name
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()


class ListPortfoliosCommand(Command):
    def execute(self, context) -> CommandResult:
        try:
            portfolios = read_available_portfolios(
                os.path.join(context.config_folder, "alpaca.json")
            )
            if not portfolios:
                return CommandResult(success=True, message="No portfolios found.")

            self._print_portfolios(portfolios, context.loaded_portfolio_name)
            return CommandResult(success=True, data=portfolios)

        except Exception as e:
            return CommandResult(
                success=False, message=f"Failed to list portfolios: {str(e)}"
            )

    def description(self) -> str:
        return "Lists all available portfolios, highlighting the currently loaded one."

    def _print_portfolios(
        self, portfolios: List[str], active_portfolio: Optional[str]
    ) -> None:
        """
        Prints the list of portfolios with formatting.

        Args:
            portfolios: List of portfolio names
            active_portfolio: Currently loaded portfolio name (if any)
        """
        pretty_print_portfolios(
            portfolios=portfolios, active_portfolio=active_portfolio
        )
        return None


class InitPortfolioCommand(Command):
    def execute(
        self,
        context=None,  # type: ignore
    ) -> CommandResult:
        try:
            portfolio_data = self._collect_portfolio_data()
            self._save_portfolio(
                portfolio_data=portfolio_data, config_folder=context.config_folder  # type: ignore
            )
            return CommandResult(
                success=True,
                message="Portfolio created successfully!",
                data=portfolio_data,
            )
        except Exception as e:
            return CommandResult(
                success=False, message=f"Failed to create portfolio: {str(e)}"
            )

    def description(self) -> str:
        return "Initializes a new portfolio with user-provided details."

    def _collect_portfolio_data(self) -> Dict[str, str]:
        """Collects all necessary portfolio data from user input."""
        # Ask for portfolio name
        portfolio_name = get_validated_input(
            "Enter the name of the portfolio: ", [is_non_empty_string]  # type: ignore
        )

        # Ask for the key and secret
        # TODO: Could be more specific since ALPACA use always the same key types
        key = get_validated_input("Enter your Alpaca API key: ", [is_non_empty_string])  # type: ignore
        secret = get_password("Enter your Alpaca secret key (input will be hidden): ")

        return {"name": portfolio_name, "key": key, "secret_key": secret}

    def _save_portfolio(
        self, portfolio_data: Dict[str, str], portfolio_folder: str
    ) -> None:
        """Saves the portfolio data to a JSON file."""
        if not os.path.exists(portfolio_folder):
            os.makedirs(portfolio_folder)

        portfolio_path = os.path.join(portfolio_folder, "alpaca.json")
        available_portfolios = read_available_portfolios(portfolio_path)

        # Check if portfolio already exists
        if portfolio_data["name"] in available_portfolios:
            raise ValueError(f"Portfolio '{portfolio_data['name']}' already exists.")

        # Save the new portfolio
        with open(portfolio_path, "r+") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}

            config["portfolios"].append(
                {
                    "name": portfolio_data["name"],
                    "key": portfolio_data["key"],
                    "secret_key": portfolio_data["secret_key"],
                }
            )

            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()


class UnloadPortfolioCommand(Command):
    def execute(self, context) -> CommandResult:
        context.loaded_portfolio_name = None
        context.keys = {}
        context.client = None  # Reset the client
        return CommandResult(success=True, message="Portfolio unloaded successfully.")

    def description(self) -> str:
        return "Unloads the currently active portfolio."


class LoadLastPortfolioCommand(Command):
    """
    Command to load the most recently used portfolio.
    """

    def execute(self, context) -> CommandResult:
        # Check if there's already an active portfolio
        if context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message=f"Portfolio '{context.loaded_portfolio_name}' is currently active. "
                "Please unload the current portfolio before loading a new one.",
            )

        try:
            config_path = Path(context.config_folder) / "alpaca.json"
            result = self._load_last_portfolio(config_path, context)

            if not result.success:
                if "No last portfolio" in result.message:  # type: ignore
                    # If no last portfolio, try to load a new one
                    return context.execute_command("load_portfolio")
                return result

            return CommandResult(
                success=True,
                message=f"Successfully loaded last portfolio: {context.loaded_portfolio_name}",
                data=result.data,
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Failed to load last portfolio: {str(e)}"
            )

    def description(self) -> str:
        return "Loads the most recently used portfolio."

    def _load_last_portfolio(self, config_path: Path, context) -> CommandResult:
        """Attempts to load the last used portfolio."""

        # Load config data
        try:
            with config_path.open("r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return CommandResult(
                success=False,
                message="Config file is corrupted. Please select a portfolio to load.",
            )

        # Check for last loaded portfolio
        if not data.get("last_used"):
            return CommandResult(
                success=False,
                message="No last portfolio found. Please select a portfolio to load.",
            )

        # Try to load the portfolio
        portfolio_name = data["last_used"]

        try:
            # Update portfolio manager state
            context.loaded_portfolio_name = portfolio_name
            context.keys = read_portfolio_keys(str(config_path), portfolio_name)
            context.set_client()

            return CommandResult(success=True)

        except Exception as e:
            return CommandResult(
                success=False, message=f"Error loading portfolio: {str(e)}"
            )


class PortfolioOverviewCommand(Command):
    @require_internet
    def execute(self, context) -> CommandResult:
        if not context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message="No portfolio loaded. Please load or create a portfolio first.",
            )
        # Set the client
        context.client = TradingClient(context.keys["key"], context.keys["secret_key"])
        # ask the user if they want the detailed overview
        validation_funcs: List[Callable] = [is_yes_or_no, is_non_empty_string]
        input_value = get_validated_input(
            "Do you want a detailed overview? (yes/no, default: no): ", validation_funcs
        )
        detailed: bool = input_value in ["yes", "y"]
        context.get_overview(detailed=detailed)
        return CommandResult(success=True)

    def description(self) -> str:
        return "Prints the portfolio overview."


class TradeAssetCommand(Command):
    def execute(self, context) -> CommandResult:
        if not context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message="No portfolio loaded. Please load or create a portfolio first.",
            )

        # Set the Alpaca trading client
        context.client = TradingClient(context.keys["key"], context.keys["secret_key"])
        data_client = StockHistoricalDataClient(
            context.keys["key"], context.keys["secret_key"]
        )

        print("\nAvailable Order Types:\n1. market\n2. limit\n3. stop\n4. stop_limit")
        action = get_validated_input(
            "Do you want to buy or sell? (buy/sell): ",
            [is_non_empty_string, is_buy_or_sell],  # type: ignore
        )

        symbol = get_validated_input(
            f"Enter the asset symbol to {action.upper()}: ", [is_valid_ticker]  # type: ignore
        )

        # Validate symbol and tradability
        try:
            asset: Union[Asset, Dict] = context.client.get_asset(symbol)
            if not asset.tradable:  # type: ignore
                return CommandResult(
                    success=False, message=f"{symbol} is not tradable."
                )
            if not asset.exchange:  # type: ignore
                return CommandResult(
                    success=False, message=f"{symbol} has no associated exchange."
                )
        except Exception as e:
            return CommandResult(
                success=False, message=f"Symbol validation failed: {str(e)}"
            )

        # Check if exchange is open
        exchange = asset.exchange  # type: ignore
        is_open, status_msg = context.exchange_service.is_exchange_open(exchange.value)
        if not is_open:
            return CommandResult(
                success=False,
                message=f"Exchange '{exchange}' is currently closed: {status_msg}",
            )

        # Print last available price
        try:
            quote = data_client.get_stock_latest_quote(
                StockLatestQuoteRequest(symbol_or_symbols=symbol)
            )
            last_price = quote[symbol].ask_price
            print(
                f"{Fore.YELLOW}Last available price for {symbol}: ${last_price:.2f}{Fore.RESET}"
            )
        except Exception as e:
            print(f"{Fore.RED}Could not fetch latest price: {str(e)}{Fore.RESET}")

        # Get quantity
        qty = float(
            get_validated_input(
                "Enter quantity: ",
                [is_non_empty_string, is_positive_number],  # type: ignore
            )
        )

        # Order type selection
        order_type_map = {"1": "market", "2": "limit", "3": "stop", "4": "stop_limit"}
        valid_order_types: List[str] = list(order_type_map.keys())
        order_type_input = get_validated_input(
            "Select order type (1-4): ",
            [is_non_empty_string, is_valid_order_type],  # type: ignore
            valid_order_types,
        )
        order_type = order_type_map[order_type_input]

        # Time in force validation
        time_in_force = get_validated_input(
            "Enter time in force (e.g., day, gtc): ",
            [is_non_empty_string, is_valid_time_in_force],  # type: ignore
        )

        # Ask if this is a short sale
        is_short = False
        if action == "sell":
            short_input = get_validated_input(
                "Is this a short sale? (yes/no): ", [is_non_empty_string, is_yes_or_no]  # type: ignore
            )
            is_short = short_input in ["yes", "y"]
            if is_short and not asset.shortable:  # type: ignore
                return CommandResult(
                    success=False, message=f"{symbol} is not shortable."
                )

        # Prepare order
        order_classes: Dict[str, Any] = {
            "market": MarketOrderRequest,
            "limit": LimitOrderRequest,
            "stop": StopOrderRequest,
            "stop_limit": StopLimitOrderRequest,
        }
        order_class = order_classes[order_type]

        order_kwargs = {
            "symbol": symbol,
            "qty": qty,
            "side": OrderSide.BUY if action == "buy" else OrderSide.SELL,
            "time_in_force": TimeInForce(time_in_force),
        }

        if order_type in ["limit", "stop", "stop_limit"]:
            price = float(
                get_validated_input(
                    "Enter limit/stop price: ", [is_non_empty_string, is_valid_number]  # type: ignore
                )
            )
            order_kwargs["limit_price"] = price
            if order_type == "stop_limit":
                stop_price = float(
                    get_validated_input(
                        "Enter stop price: ", [is_non_empty_string, is_valid_number]  # type: ignore
                    )
                )
                order_kwargs["stop_price"] = stop_price

        # Confirm order
        confirm = get_validated_input(
            f"Submit {action.upper()}{' SHORT' if is_short else ''} order for {qty} shares of {symbol}? (yes/no): ",
            [is_non_empty_string, is_yes_or_no],  # type: ignore
        )
        if confirm not in ["yes", "y"]:
            return CommandResult(success=False, message="Order cancelled by user.")

        # Submit order
        try:
            order = context.client.submit_order(order_class(**order_kwargs))
            return CommandResult(
                success=True,
                message=f"{action.capitalize()} order submitted: {order.id}",  # type: ignore
            )
        except Exception as e:
            return CommandResult(
                success=False, message=f"Error placing {action} order: {str(e)}"
            )

    def description(self) -> str:
        return "Places a buy, sell, or short order for a specified asset using the Alpaca API."


class TradeCryptoCommand(Command):
    def execute(self, context) -> CommandResult:
        if not context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message="No portfolio loaded. Please load or create a portfolio first.",
            )

        # Set the Alpaca crypto trading client
        context.client = TradingClient(context.keys["key"], context.keys["secret_key"])
        data_client = CryptoHistoricalDataClient(
            context.keys["key"], context.keys["secret_key"]
        )

        print("\nAvailable Order Types:\n1. market\n2. limit")
        action = get_validated_input(
            "Do you want to buy or sell crypto? (buy/sell): ",
            [is_non_empty_string, is_buy_or_sell],  # type: ignore
        )

        symbol = get_validated_input(
            "Enter the crypto symbol (e.g., BTC/USD): ", [is_valid_ticker]  # type: ignore
        )

        # Print last available price
        try:
            quote = data_client.get_crypto_latest_quote(
                CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
            )
            last_price = quote[symbol].ask_price
            print(
                f"{Fore.YELLOW}Last available price for {symbol}: ${last_price:.2f}{Fore.RESET}"
            )
        except Exception as e:
            print(f"{Fore.RED}Could not fetch latest price: {str(e)}{Fore.RESET}")

        # Validate quantity
        qty = float(
            get_validated_input(
                "Enter quantity: ",
                [is_non_empty_string, is_positive_number],  # type: ignore
            )
        )

        # Order type selection
        order_type_map = {"1": "market", "2": "limit"}
        valid_order_type: List[str] = list(order_type_map.keys())
        order_type_input = get_validated_input(
            "Select order type (1-2): ",
            [is_non_empty_string, is_valid_order_type],  # type: ignore
            valid_order_type,
        )
        order_type = order_type_map[order_type_input]

        # Time in force validation
        time_in_force = get_validated_input(
            "Enter time in force (e.g., gtc, ioc): ",
            [is_non_empty_string, is_valid_time_in_force],  # type: ignore
        )

        # Prepare order
        order_classes: Dict[str, Any] = {
            "market": MarketOrderRequest,
            "limit": LimitOrderRequest,
        }
        order_class = order_classes[order_type]

        order_kwargs = {
            "symbol": symbol,
            "qty": qty,
            "side": OrderSide.BUY if action == "buy" else OrderSide.SELL,
            "time_in_force": TimeInForce(time_in_force),
        }

        if order_type == "limit":
            price = float(
                get_validated_input(
                    "Enter limit price: ", [is_non_empty_string, is_positive_number]  # type: ignore
                )
            )
            order_kwargs["limit_price"] = price

        # Confirm order
        confirm = get_validated_input(
            f"Submit {action.upper()} order for {qty} {symbol}? (yes/no): ",
            [is_non_empty_string, is_yes_or_no],  # type: ignore
        )
        if confirm not in ["yes", "y"]:
            return CommandResult(success=False, message="Order cancelled by user.")

        # Submit order
        try:
            order = context.client.submit_order(order_class(**order_kwargs))
            return CommandResult(
                success=True,
                message=f"{action.capitalize()} crypto order submitted: {order.id}",  # type: ignore
            )
        except Exception as e:
            return CommandResult(
                success=False, message=f"Error placing crypto order: {str(e)}"
            )

    def description(self) -> str:
        return "Places a buy or sell order for a cryptocurrency using the Alpaca Crypto API."


class PortfolioPerformanceCommand(Command):
    def execute(self, context) -> CommandResult:
        if not context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message="No portfolio loaded. Please load or create a portfolio first.",
            )
        client: TradingClient = TradingClient(
            context.keys["key"], context.keys["secret_key"]
        )

        try:
            history = client.get_portfolio_history(
                history_filter=GetPortfolioHistoryRequest(period="1M", timeframe="1D"),
            )
        except Exception as e:
            return CommandResult(
                success=False, message=f"Error fetching portfolio history: {str(e)}"
            )

        dates = [datetime.fromtimestamp(ts) for ts in history.timestamp]  # type: ignore
        equity = history.equity  # type: ignore

        print(
            tabulate(zip(dates, equity), headers=["Date", "Equity"], tablefmt="pretty")
        )

        plt.figure(figsize=(10, 6))
        plt.plot(dates, equity, marker="o", linestyle="-", color="blue")  # type: ignore
        plt.title("Portfolio Equity Over Time")
        plt.xlabel("Date")
        plt.ylabel("Equity ($)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        return CommandResult(
            success=True, message="Portfolio performance displayed successfully."
        )

    def description(self) -> str:
        return "Displays the historical portfolio performance using Alpaca's API."
