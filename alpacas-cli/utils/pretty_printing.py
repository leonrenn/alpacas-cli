"""
Pretty printing utilities for Alpaca portfolio management commands.
"""

from typing import Dict, List, Optional, Union
from alpaca.trading.models import TradeAccount, Position
from commands.core import Command, ExchangeStatus, Analysis
from analysis.core import AsyncAnalysisRunner
from utils.terminal import WRAPPER, TERMINAL_WIDTH
from utils.colors import HIGHLIGHT, SUCCESS, WARNING, ERROR, RESET, HEADERS, SUBHEADERS
from functools import wraps


def header(text: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"{HEADERS}{'=' * TERMINAL_WIDTH}")
            print(f"{HEADERS}{text.center(TERMINAL_WIDTH)}")
            print(f"{HEADERS}{'=' * TERMINAL_WIDTH}{RESET}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def footer():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(f"{HEADERS}{'=' * TERMINAL_WIDTH}{RESET}")
            return result

        return wrapper

    return decorator


def _subheaders(text: str) -> None:
    """
    Formats the text as a subheader with color and padding.

    Args:
        text (str): The text to format as a subheader.

    Returns:
        str: The formatted subheader string.
    """
    print(f"{SUBHEADERS}{'-' * TERMINAL_WIDTH}")
    print(f"{SUBHEADERS}{text.center(TERMINAL_WIDTH)}")
    print(f"{SUBHEADERS}{'-' * TERMINAL_WIDTH}{RESET}")
    return


@header("Command Information")
@footer()
def pretty_print_info_text(commands: Dict[str, Command]) -> None:
    # Sort commands alphabetically
    sorted_commands = sorted(commands.items(), key=lambda x: x)

    max_command_length = max(len(cmd_name) for cmd_name, _ in sorted_commands)

    for cmd_name, cmd in sorted_commands:
        # Format command name with padding
        formatted_cmd = f"{HIGHLIGHT}{cmd_name:<{max_command_length}}{RESET}"

        # Wrap description text
        description = cmd.description()
        wrapped_description = WRAPPER.fill(description)

        # Handle multi-line descriptions
        lines = wrapped_description.split("\n")
        print(f"  {formatted_cmd}  {lines[0]}")
        for line in lines[1:]:
            print(f"  {' ' * max_command_length}  {line}")


@header("Account Information")
@footer()
def pretty_print_portfolio_info(
    account_info: TradeAccount, positions: List[Position], detailed: bool = False
) -> None:
    """
    Prints the portfolio information including account details and positions.

    Args:
        account_info (TradeAccount): The account information.
        positions (List[Position]): List of positions in the portfolio.
        detailed (bool): If True, prints all account details in a formatted way.

    Returns:
        None
    """
    if detailed:
        for field, value in vars(account_info).items():
            print(f"{field.replace('_', ' ').title():<30}: {value}")
    else:
        # Account Summary
        print(f"{HIGHLIGHT}{'Cash Balance:':<20} ${account_info.cash}{RESET}")
        print(
            f"{HIGHLIGHT}{'Portfolio Value:':<20} ${account_info.portfolio_value}{RESET}\n"
        )

    # Positions
    if positions:
        _subheaders(text="Current Positions")
        for position in positions:
            print(
                f"{HIGHLIGHT}{position.symbol:<10} | Qty: {position.qty:<10} | Side: {position.side}{RESET}"
            )
    else:
        print(f"{HIGHLIGHT}No positions found.{RESET}")


@header("Exchange Status")
@footer()
def pretty_print_exchange_status(status_results: List[ExchangeStatus]) -> None:
    """
    Prints the status of major stock exchanges.
    Args:
        status_results (List[ExchangeStatus]): List of exchange status results.
    Returns:
        None
    """
    for result in status_results:
        status_color = SUCCESS if result.is_open else HIGHLIGHT
        print(
            f"{status_color}{result.status_message}{RESET} - "
            f"Current time in {result.name}: {result.current_time}"
        )


@header("Alias Commands")
@footer()
def pretty_print_alias_help_text() -> None:
    help_text = f"""
    alias set    : Create a new alias for a command
    alias remove : Remove an existing alias
    alias list   : Show all current aliases
    alias help   : Show this help message

    Examples:
    alias set    -> Follow prompts to create alias 'b' for 'buy_asset'
    alias remove -> Follow prompts to remove an alias
    alias list   -> Show all current aliases
    """
    print(help_text)


@header("Current Aliases")
@footer()
def pretty_print_current_aliases(aliases: Dict[str, str]) -> None:
    """
    Prints the current aliases in a formatted way.

    Args:
        aliases (Dict[str, str]): Dictionary of aliases where keys are alias names and values are command names.
    """
    for alias, cmd in aliases.items():
        print(f"  {HIGHLIGHT}{alias} -> {cmd}{RESET}")


@header("Running Analyses")
@footer()
def pretty_print_running_analyses(
    running_analyses: Dict[str, AsyncAnalysisRunner],
) -> None:
    """
    Prints the status of running analyses.
    Args:
        running_analyses (Dict[str, Any]): The running analyses to print.
    Returns:
        None
    """
    for analysis_id, runner in running_analyses.items():
        status = "running" if runner.is_running() else "completed"
        print(f"{HIGHLIGHT}ID {analysis_id} -> {status}{RESET}")


@header("Available Analyses")
@footer()
def pretty_print_available_analyses(analyses: Dict[str, Analysis]) -> None:
    """
    Prints the available portfolio analyses.
    Args:
        analyses (Dict[str, Any]): The available analyses to print.
    Returns:
        None
    """
    for name, analysis in analyses.items():
        print(f"{HIGHLIGHT}{name:15} -> {analysis.get_description()}{RESET}")


def pretty_print_internet_required() -> None:
    """
    Prints a message indicating that internet access is required for certain commands.
    """
    print(f"{ERROR}No internet connection available. Trading is not possible.{RESET}")


@header("Available Portfolios")
@footer()
def pretty_print_portfolios(
    portfolios: List[str], active_portfolio: Optional[str]
) -> None:
    """
    Prints the list of portfolios with formatting.
    Args:
        portfolios: List of portfolio names
        active_portfolio: Currently loaded portfolio name (if any)
    Returns:
        None
    """
    if not portfolios:
        print(f"{WARNING}No portfolios found.{RESET}")
        return

    for portfolio in portfolios:
        if portfolio == active_portfolio:
            print(f"{SUCCESS}* {portfolio} (ACTIVE){RESET}")
        else:
            print(f"{HIGHLIGHT}  {portfolio}{RESET}")

    print(f"\n{HIGHLIGHT}Total portfolios: {len(portfolios)}{RESET}")


@header("Available Ticker Sets")
@footer()
def pretty_print_available_ticker_sets(
    ticker_sets: Dict[str, Union[str, List[str]]],
) -> None:
    """
    Prints the available ticker sets in a formatted way.
    Args:
        ticker_sets (List[str]): List of available ticker sets.
    Returns:
        None
    """
    for ticker_set in ticker_sets:
        print(f"Identifier: {ticker_set['identifier']}")  # type: ignore
        print(f"Description: {ticker_set['description']}")  # type: ignore
        print(f"Tickers: {', '.join(ticker_set['tickers'])}")  # type: ignore


def pretty_print_banner(author: str, version: str) -> None:
    """
    Prints the banner.
    """
    banner = f"""{HIGHLIGHT}      
                ╔══════════════════════════════════════════╗
                ║     Portfolio Management System          ║
                ║     Version: {version:<24}    ║
                ║     Author: {author:<25}    ║
                ╚══════════════════════════════════════════╝{RESET}
                """
    print(banner)
