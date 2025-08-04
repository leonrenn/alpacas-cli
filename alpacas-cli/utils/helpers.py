"""
Different helper functions, classes and decorators for the project.
"""

import yfinance as yf
from typing import Tuple, Callable, Any, Dict, List
from functools import wraps
from .pretty_printing import header, footer
from .input_validation import (
    _validate_url_input,
    get_validated_input,
    is_non_empty_string,
    get_password,
)
import requests
from colorama import Fore
import datetime as dt
import pytz
from forex_python.converter import CurrencyCodes
import json
import os
from alpaca.trading.client import TradingClient
import sys
from pathlib import Path

STOCK_EXCHANGES: Dict[str, Dict] = {
    "NYSE": {  # New York Stock Exchange
        "country": "United States",
        "city": "New York",
        "timezone": "America/New_York",  # UTC-4/UTC-5
        "trading_hours": {
            "regular": {"open": "09:30", "close": "16:00"},
            "pre_market": {"open": "04:00", "close": "09:30"},
            "after_hours": {"open": "16:00", "close": "20:00"},
        },
    },
    "NASDAQ": {
        "country": "United States",
        "city": "New York",
        "timezone": "America/New_York",  # UTC-4/UTC-5
        "trading_hours": {
            "regular": {"open": "09:30", "close": "16:00"},
            "pre_market": {"open": "04:00", "close": "09:30"},
            "after_hours": {"open": "16:00", "close": "20:00"},
        },
    },
    "LSE": {  # London Stock Exchange
        "country": "United Kingdom",
        "city": "London",
        "timezone": "Europe/London",  # UTC+0/UTC+1
        "trading_hours": {"regular": {"open": "08:00", "close": "16:30"}},
    },
    "TSE": {  # Tokyo Stock Exchange
        "country": "Japan",
        "city": "Tokyo",
        "timezone": "Asia/Tokyo",  # UTC+9
        "trading_hours": {"regular": {"open": "09:00", "close": "15:15"}},
    },
    "SSE": {  # Shanghai Stock Exchange
        "country": "China",
        "city": "Shanghai",
        "timezone": "Asia/Shanghai",  # UTC+8
        "trading_hours": {
            "regular": {"open": "09:30", "close": "15:00"},
            "lunch_break": {"start": "11:30", "end": "13:00"},
        },
    },
    "HKEX": {  # Hong Kong Stock Exchange
        "country": "Hong Kong",
        "city": "Hong Kong",
        "timezone": "Asia/Hong_Kong",  # UTC+8
        "trading_hours": {
            "regular": {"open": "09:30", "close": "16:00"},
            "lunch_break": {"start": "12:00", "end": "13:00"},
        },
    },
    "FRA": {  # Frankfurt Stock Exchange
        "country": "Germany",
        "city": "Frankfurt",
        "timezone": "Europe/Berlin",  # UTC+1/UTC+2
        "trading_hours": {"regular": {"open": "09:00", "close": "17:30"}},
    },
}


def check_internet_connection(
    verbose: bool = True, check_url: str = "https://www.google.com/"
) -> bool:
    """
    Checks if an internet connection is available.

    Args:
        verbose (bool): If True, prints a message to the console.

    Returns:
        bool: True if an internet connection is available, False otherwise.
    """
    # # Check if url is valid
    if not _validate_url_input(url=check_url):
        return False
    try:
        # Send a GET request to a reliable website
        response: requests.Response = requests.get(url=check_url, timeout=5)
        # Check if the response status code is 200, which indicates success
        if response.status_code == 200:
            if verbose:
                print(Fore.GREEN + "Internet connection is available." + Fore.RESET)
            return True
    except requests.ConnectionError:
        pass
    if verbose:
        print(Fore.RED + "No internet connection." + Fore.RESET)
    return False


def require_internet(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not check_internet_connection(verbose=False):
            print("Only possible with an internet connection.")
            return None
        return func(*args, **kwargs)

    return wrapper


def _ask_for_ticker() -> Tuple[str, yf.Ticker]:
    """
    Ask for the ticker and return the yfinance object.

    Returns:
        Optional[Tuple[str, yf.Ticker]]: The stock name and the yfinance object.

    """
    # Ask the user for the ticker
    stock: str = input("Enter the ticker: ").strip().upper()

    # Check if the ticker is valid
    try:
        ticker: yf.Ticker = yf.Ticker(stock)
    except:
        print("Invalid ticker.")
        raise Exception
    return stock, ticker


from typing import List, Dict, Any
import json


def read_available_portfolios(filepath: str) -> List[str]:
    """
    Read available portfolios from the 'portfolios.json' file.

    Args:
        filepath (str): Path to the JSON file containing portfolio names.

    Returns:
        List[str]: A list of portfolio names.
    """
    try:
        with open(filepath, "r") as file:
            portfolios_alpaca: Dict[str, Any] = json.load(file)
        # Extract portfolio names
        portfolio_names: List[str] = [
            portfolios["name"] for portfolios in portfolios_alpaca["portfolios"]
        ]
        return portfolio_names
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return []


def read_portfolio_keys(filepath: str, portfolio_name: str) -> Dict[str, str]:
    """
    Read portfolio key and secret key from the JSON file for the given portfolio name.

    Args:
        filepath (str): Path to the JSON file containing portfolio keys.
        portfolio_name (str): The name of the portfolio to retrieve keys for.

    Returns:
        Dict[str, str]: A dictionary containing the portfolio key and secret key.
    """
    try:
        with open(filepath, "r") as file:
            portfolios_alpaca: Dict[str, Any] = json.load(file)
        # Extract keys for the specified portfolio
        for portfolio in portfolios_alpaca["portfolios"]:
            if portfolio["name"] == portfolio_name:
                return {
                    "key": portfolio["key"],
                    "secret_key": portfolio["secret_key"],
                }
        print(f"Portfolio '{portfolio_name}' not found in {filepath}.")
        return {}
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return {}


def _is_exchange_open(exchange_code: str) -> Tuple[bool, str]:
    """
    Check if a given stock exchange is currently open.

    Args:
        exchange_code (str): The stock exchange code (e.g., 'NYSE', 'LSE')

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating if the exchange is open,
                          and a message with the status.
    """
    try:
        # Get exchange info
        exchange = STOCK_EXCHANGES[exchange_code.upper()]

        # Get current time in exchange's timezone
        exchange_tz = pytz.timezone(exchange["timezone"])
        current_time = dt.datetime.now(exchange_tz)

        # Convert current time to HH:MM format for comparison
        current_time_str = current_time.strftime("%H:%M")

        # Get weekday (0 = Monday, 6 = Sunday)
        weekday = current_time.weekday()

        # Check if it's weekend
        if weekday >= 5:  # Saturday or Sunday
            return False, f"{exchange_code} is closed (Weekend)"

        # Get trading hours
        trading_hours = exchange["trading_hours"]

        # Check regular trading hours
        regular_open = trading_hours["regular"]["open"]
        regular_close = trading_hours["regular"]["close"]

        # Check for lunch break (common in Asian markets)
        if "lunch_break" in trading_hours:
            lunch_start = trading_hours["lunch_break"]["start"]
            lunch_end = trading_hours["lunch_break"]["end"]

            # During lunch break
            if lunch_start <= current_time_str <= lunch_end:
                return False, f"{exchange_code} is in lunch break"

        # Check pre-market if available
        if "pre_market" in trading_hours and current_time_str < regular_open:
            pre_open = trading_hours["pre_market"]["open"]
            pre_close = trading_hours["pre_market"]["close"]
            if pre_open <= current_time_str <= pre_close:
                return True, f"{exchange_code} is open (Pre-market)"

        # Check after-hours if available
        if "after_hours" in trading_hours and current_time_str > regular_close:
            after_open = trading_hours["after_hours"]["open"]
            after_close = trading_hours["after_hours"]["close"]
            if after_open <= current_time_str <= after_close:
                return True, f"{exchange_code} is open (After-hours)"

        # Check regular hours
        if regular_open <= current_time_str <= regular_close:
            return True, f"{exchange_code} is open (Regular hours)"

        return False, f"{exchange_code} is closed"

    except KeyError:
        return False, f"Exchange code '{exchange_code}' not found"


class ExchangeService:
    """Service class for exchange-related operations"""

    STOCK_EXCHANGES = {
        "NYSE": {
            "timezone": "America/New_York",
            "open_time": "09:30",
            "close_time": "16:00",
            "weekdays": range(0, 5),  # Monday = 0, Friday = 4
        },
        "NASDAQ": {
            "timezone": "America/New_York",
            "open_time": "09:30",
            "close_time": "16:00",
            "weekdays": range(0, 5),  # Monday = 0, Friday = 4
        },
        "NMS": {
            "timezone": "America/New_York",
            "open_time": "09:30",
            "close_time": "16:00",
            "weekdays": range(0, 5),
        },
        "LSE": {
            "timezone": "Europe/London",
            "open_time": "08:00",
            "close_time": "16:30",
            "weekdays": range(0, 5),
        },
        "TSE": {
            "timezone": "Asia/Tokyo",
            "open_time": "09:00",
            "close_time": "15:30",
            "weekdays": range(0, 5),
        },
        "GER": {
            "timezone": "Europe/Berlin",
            "open_time": "09:00",
            "close_time": "17:30",
            "weekdays": range(0, 5),
        },
        "FRA": {
            "timezone": "Europe/Berlin",
            "open_time": "09:00",
            "close_time": "17:30",
            "weekdays": range(0, 5),
        },
        "HKEX": {
            "timezone": "Asia/Hong_Kong",
            "open_time": "09:30",
            "close_time": "16:00",
            "weekdays": range(0, 5),
        },
    }

    @staticmethod
    def is_exchange_open(exchange: str) -> Tuple[bool, str]:
        """
        Check if a given exchange is currently open.

        Args:
            exchange (str): Exchange code (NYSE, LSE, etc.)

        Returns:
            Tuple[bool, str]: (is_open, status_message)
        """
        if exchange not in list(ExchangeService.STOCK_EXCHANGES.keys()):
            return False, f"Unknown exchange: {exchange}"

        exchange_info = ExchangeService.STOCK_EXCHANGES[exchange]
        timezone = pytz.timezone(exchange_info["timezone"])
        current_time = dt.datetime.now(timezone)

        # Check if it's a weekday
        if current_time.weekday() not in exchange_info["weekdays"]:
            return False, f"{exchange} CLOSED (Weekend)"

        # Convert current time to HH:MM format
        current_time_str = current_time.strftime("%H:%M")

        # Check if within trading hours
        if (
            exchange_info["open_time"]
            <= current_time_str
            <= exchange_info["close_time"]
        ):
            return True, f"{exchange} OPEN"
        else:
            return False, f"{exchange} CLOSED"


class CurrencyFormatter:
    def __init__(self):
        self.currency_codes = CurrencyCodes()
        self._symbol_map = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CNY": "¥",
            "HKD": "HK$",
            "CHF": "CHF",
            "CAD": "C$",
            "AUD": "A$",
            # Add more currencies as needed
        }

    def get_symbol(self, currency_code: str) -> str:
        """
        Get the symbol for a currency code.

        Args:
            currency_code (str): The currency code (e.g., 'USD', 'EUR').

        Returns:
            str: The currency symbol if available, otherwise the currency code with a space.
        """
        return self._symbol_map.get(currency_code, currency_code + " ")


def first_login_session(func: Callable) -> Callable:
    """
    Decorator to check if this is the first login session.
    If it is, perform the first login tasks.
    Args:
        func (Callable): The function to decorate.
    Returns:
        Callable: The wrapped function that checks for first login.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.getenv("SKIP_FIRST_LOGIN") != "1" and check_first_login():
            perform_first_login_tasks()
        return func(*args, **kwargs)

    return wrapper


def check_first_login() -> bool:
    """
    Check if this is the first login session by verifying the existence and size of the configuration file.

    Returns:
        bool: True if this is the first login session (config file does not exist or is empty), False otherwise.
    """
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "configs", "alpaca.json"
    )
    return not os.path.exists(config_path) or os.path.getsize(config_path) == 0


@header("First Login Session")
@footer()
def perform_first_login_tasks() -> None:
    """
    Perform tasks required for the first login session.
    This includes collecting user input, validating credentials, and saving configuration.
    """
    config_dir = Path(__file__).resolve().parent.parent.parent / "configs"
    config_path = config_dir / "alpaca.json"

    # Collect user input
    portfolio_name = get_validated_input(
        "Enter the name of the portfolio: ", [is_non_empty_string]  # type: ignore
    )
    key = get_validated_input("Enter your Alpaca API key: ", [is_non_empty_string])  # type: ignore
    secret = get_password(
        "Enter your Alpaca secret key (input will be hidden): "
    ).strip()

    # Validate credentials before saving
    try:
        trading_client = TradingClient(api_key=key, secret_key=secret, paper=True)
        _ = trading_client.get_account()
    except Exception:
        print(
            "Invalid Alpaca API key or secret. Please check your credentials and try again."
        )
        sys.exit(1)

    # Prepare portfolio data
    portfolio_data = {
        "portfolios": [
            {
                "name": portfolio_name,
                "key": key,
                "secret_key": secret,
            }
        ]
    }

    # Save to config
    config_dir.mkdir(parents=True, exist_ok=True)
    with config_path.open("w") as f:
        json.dump(portfolio_data, f, indent=4)

    print(f"Portfolio '{portfolio_name}' added successfully.")
