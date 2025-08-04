"""
User input validation functions.
"""

from dateutil.parser import parse
import datetime as dt
from pytz import UTC
from typing import Optional, Tuple, List, Callable, Any
import validators
import re
import getpass


def is_valid_identifier_analysis(value: str) -> bool:
    """
    Check if the input is a valid identifier.

    An identifier is considered valid if it consists of exactly four digits.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a valid identifier, False otherwise.
    """
    return value.isdigit() and len(value) == 4


def is_valid_ticker_set_choice(value: str, max_choice: int) -> bool:
    """
    Check if the input is a valid ticker set choice.

    A ticker set choice is considered valid if it is a digit and falls within the range of 1 to max_choice (inclusive).

    Args:
        value (str): The input string to be checked.
        max_choice (int): The maximum valid choice value.

    Returns:
        bool: True if the input is a valid ticker set choice, False otherwise.
    """
    return value.isdigit() and 1 <= int(value) <= max_choice


def is_valid_date(value: str) -> bool:
    """
    Check if the input is a valid date in YYYY-MM-DD format.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a valid date, False otherwise.
    """
    try:
        dt.datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_frequency(value: str) -> bool:
    """
    Check if the input is a valid frequency.

    A frequency is considered valid if it matches the pattern of one or more digits followed by either 'd' (days) or 'h' (hours).

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a valid frequency, False otherwise.
    """
    return re.match(r"^\d+[dh]$", value) is not None


def is_valid_float(value: str) -> bool:
    """
    Check if the input is a valid float.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input can be converted to a float, False otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_valid_alias_subcommand(value: str, alias_subcommands: List[str]) -> bool:
    """
    Check if the input is a valid subcommand.

    A subcommand is considered valid if it is one of the following: 'set', 'remove', 'list', 'help'.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a valid subcommand, False otherwise.
    """
    return value in alias_subcommands


def get_validated_input(
    prompt: str, validators: List[Callable[[str, Any], bool]], *args: Any
) -> str:
    """
    Prompt the user for input and validate it using the provided validators.

    Args:
        prompt (str): The prompt to display to the user.
        validators (List[Callable[[str, Any], bool]]): A list of validation functions.
        *args (Any): Additional arguments to pass to the validation functions.

    Returns:
        str: The validated input from the user.
    """
    while True:
        # Make the input hidden if the prompt is for a password
        value = input(prompt)
        if all(
            (
                validator(value, *args)
                if validator.__code__.co_argcount > 1
                else validator(value)  # type: ignore
            )
            for validator in validators
        ):
            return value
        print("Invalid input. Please try again.")


def get_password(prompt: str = "Enter password: ") -> str:
    """
    Prompt the user for a password without echoing the input.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The password entered by the user.
    """
    return getpass.getpass(prompt=prompt)


def is_valid_analysis_subcommand(value: str, valid_choices: List[str]) -> bool:
    """
    Check if the input is a valid analysis subcommand.

    Args:
        value (str): The input string to be checked.
        valid_choices (List[str]): A list of valid choices.

    Returns:
        bool: True if the input is a valid analysis subcommand, False otherwise.
    """
    return value in valid_choices


def is_non_empty_string(value: str) -> bool:
    """
    Check if the input is a non-empty string.
    A non-empty string is considered valid if it is a string and contains at least one non-whitespace character.
    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a non-empty string, False otherwise.
    """
    return isinstance(value, str) and bool(value.strip())


def is_valid_number(value: str) -> bool:
    """
    Check if the input is a valid number.

    This function attempts to convert the input string to a float. If successful, the input is considered a valid number.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input can be converted to a float, False otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_yes_or_no(value: str) -> bool:
    """
    Check if the input is 'yes' or 'no'.

    This function checks if the input string is one of the following: 'yes', 'no', 'y', 'n', regardless of case.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is 'yes', 'no', 'y', or 'n', False otherwise.
    """
    return value.lower() in ["yes", "no", "y", "n"]


def is_buy_or_sell(value: str) -> bool:
    """
    Check if the input is 'buy' or 'sell'.

    This function checks if the input string is either 'buy' or 'sell'.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is 'buy' or 'sell', False otherwise.
    """
    return value in ["buy", "sell"]


def is_positive_number(value: str) -> bool:
    """
    Check if the input is a positive number.

    This function first checks if the input is a valid number using the is_valid_number function. If it is, it then checks if the number is greater than zero.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a valid number and greater than zero, False otherwise.
    """
    return is_valid_number(value) and float(value) > 0


def is_valid_order_type(value: str, valid_order_types: List[str]) -> bool:
    """
    Check if the input is a valid order type.

    This function checks if the input string is one of the valid order types provided in the list.

    Args:
        value (str): The input string to be checked.
        valid_order_types (List[str]): A list of valid order types.

    Returns:
        bool: True if the input is a valid order type, False otherwise.
    """
    return value in valid_order_types


def is_valid_time_in_force(value: str) -> bool:
    """
    Check if the input is a valid time in force.

    This function checks if the input string is one of the following: 'day', 'gtc', 'opg', 'cls', 'ioc', 'fok'.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input is a valid time in force, False otherwise.
    """
    return value in ["day", "gtc", "opg", "cls", "ioc", "fok"]


def is_valid_ticker(value: str) -> bool:
    """
    Check if the input is a valid ticker.

    This function checks if the input string consists of 1 to 5 uppercase letters.

    Args:
        value (str): The input string to be checked.

    Returns:
        bool: True if the input matches the pattern of 1 to 5 uppercase letters, False otherwise.
    """
    return re.match(r"^[A-Z]{1,5}$", value) is not None


def _validate_url_input(url: str) -> bool:
    """
    Validate the input URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    if not validators.url(url):
        print("Invalid URL.")
        return False
    return True


def _validate_history_input(
    duration: Optional[str] = None,
    interval: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[
    bool, Optional[dt.datetime], Optional[dt.datetime], Optional[str], Optional[str]
]:
    """
    Validate the input for the history function. Accepts either duration-based or date-based queries.

    Args:
        duration (str, optional): The duration of the history (e.g., '1d', '1mo', '1y')
        interval (str, optional): The interval of the history (e.g., '1m', '5m', '1h')
        start_date (str, optional): Start date in format 'YYYY-MM-DD' or None
        end_date (str, optional): End date in format 'YYYY-MM-DD', 'now', or None

    Returns:
        Tuple[bool, dt.datetime, dt.datetime, str, str]: Validation result, start_date, end_date, duration, interval
    """
    # Valid intervals
    valid_intervals = [
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1wk",
        "1mo",
        "3mo",
    ]

    # Valid durations
    valid_durations = [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max",
    ]

    # Check if the interval is valid
    if interval not in valid_intervals:
        print(
            "Invalid interval. Please enter 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo or 3mo."
        )
        return False, None, None, None, None

    # Duration-based query
    if duration is not None:
        if duration not in valid_durations:
            print(
                "Invalid duration. Please enter 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd or max."
            )
            return False, None, None, None, None
        return True, None, None, duration, interval

    # Date-based query
    else:
        current_date = dt.datetime.now(UTC)

        # Handle 'now' as end_date
        if end_date and end_date.lower() == "now":
            end_datetime = current_date
        else:
            try:
                end_datetime = parse(end_date) if end_date else current_date
                end_datetime = end_datetime.replace(tzinfo=UTC)
            except (ValueError, TypeError):
                print("Invalid end date format. Please use YYYY-MM-DD format or 'now'.")
                return False, None, None, None, None

        try:
            start_datetime = parse(start_date) if start_date else None
            if start_datetime:
                start_datetime = start_datetime.replace(tzinfo=UTC)
        except (ValueError, TypeError):
            print("Invalid start date format. Please use YYYY-MM-DD format.")
            return False, None, None, None, None

        # Check if end date is after start date
        if start_datetime and end_datetime <= start_datetime:
            print("End date must be after start date.")
            return False, None, None, None, None

        # Check if dates are not in the future
        if end_datetime > current_date:
            print("End date cannot be in the future.")
            return False, None, None, None, None

        return True, start_datetime, end_datetime, None, interval
