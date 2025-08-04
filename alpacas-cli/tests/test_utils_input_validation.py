"""
Tests for the utils.input_validation module.
"""

import datetime as dt
from dateutil.parser import parse
from pytz import UTC

# Import the functions from the input_validation file
from utils.input_validation import (
    is_valid_identifier_analysis,
    is_valid_ticker_set_choice,
    is_valid_date,
    is_valid_frequency,
    is_valid_float,
    is_valid_alias_subcommand,
    is_valid_analysis_subcommand,
    get_validated_input,
    is_non_empty_string,
    is_valid_number,
    is_yes_or_no,
    is_buy_or_sell,
    is_positive_number,
    is_valid_order_type,
    is_valid_time_in_force,
    is_valid_ticker,
    _validate_url_input,
    _validate_history_input,
)


def test_is_valid_identifier_analysis():
    assert is_valid_identifier_analysis("1234") == True
    assert is_valid_identifier_analysis("123") == False
    assert is_valid_identifier_analysis("abcd") == False


def test_is_valid_ticker_set_choice():
    assert is_valid_ticker_set_choice("3", 5) == True
    assert is_valid_ticker_set_choice("6", 5) == False
    assert is_valid_ticker_set_choice("abc", 5) == False


def test_is_valid_date():
    assert is_valid_date("2023-06-13") == True
    assert is_valid_date("2023-13-06") == False
    assert is_valid_date("invalid-date") == False


def test_is_valid_frequency():
    assert is_valid_frequency("1d") == True
    assert is_valid_frequency("1h") == True
    assert is_valid_frequency("10x") == False


def test_is_valid_float():
    assert is_valid_float("3.14") == True
    assert is_valid_float("abc") == False
    assert is_valid_float("123") == True


def test_is_valid_alias_subcommand():
    alias_subcommands = ["set", "remove", "list", "help"]
    assert is_valid_alias_subcommand("set", alias_subcommands) == True
    assert is_valid_alias_subcommand("delete", alias_subcommands) == False


def test_is_valid_analysis_subcommand():
    analysis_subcommands = ["status", "stop <id>"]
    assert is_valid_analysis_subcommand("status", analysis_subcommands) == True
    assert is_valid_analysis_subcommand("start", analysis_subcommands) == False


def test_get_validated_input(mocker):
    mocker.patch("builtins.input", return_value="status")
    choice = get_validated_input(
        "\nEnter analysis name ('status', 'stop <id>'): ",
        [is_non_empty_string],  # type: ignore
    )
    assert choice == "status"


def test_is_non_empty_string():
    assert is_non_empty_string("hello") == True
    assert is_non_empty_string("   ") == False
    assert is_non_empty_string("") == False


def test_is_valid_number():
    assert is_valid_number("3.14") == True
    assert is_valid_number("abc") == False
    assert is_valid_number("123") == True


def test_is_yes_or_no():
    assert is_yes_or_no("yes") == True
    assert is_yes_or_no("no") == True
    assert is_yes_or_no("y") == True
    assert is_yes_or_no("n") == True
    assert is_yes_or_no("maybe") == False


def test_is_buy_or_sell():
    assert is_buy_or_sell("buy") == True
    assert is_buy_or_sell("sell") == True
    assert is_buy_or_sell("hold") == False


def test_is_positive_number():
    assert is_positive_number("3.14") == True
    assert is_positive_number("-3.14") == False
    assert is_positive_number("abc") == False


def test_is_valid_order_type():
    valid_order_types = ["1", "2", "3", "4"]
    assert is_valid_order_type("1", valid_order_types) == True
    assert is_valid_order_type("5", valid_order_types) == False


def test_is_valid_time_in_force():
    assert is_valid_time_in_force("day") == True
    assert is_valid_time_in_force("gtc") == True
    assert is_valid_time_in_force("invalid") == False


def test_is_valid_ticker():
    assert is_valid_ticker("AAPL") == True
    assert is_valid_ticker("GOOGL") == True
    assert is_valid_ticker("INVALIDTICKER") == False


def test_validate_url_input():
    assert _validate_url_input("https://www.example.com") == True
    assert _validate_url_input("invalid-url") == False


def test_validate_history_input():
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

    # Test valid duration-based query
    result = _validate_history_input(duration="1d", interval="1m")
    assert result == (True, None, None, "1d", "1m")

    # Test invalid duration
    result = _validate_history_input(duration="invalid", interval="1m")
    assert result == (False, None, None, None, None)

    # Test valid date-based query
    result = _validate_history_input(
        start_date="2023-06-01", end_date="2023-06-10", interval="1d"
    )
    assert result == (
        True,
        dt.datetime(2023, 6, 1, tzinfo=UTC),
        dt.datetime(2023, 6, 10, tzinfo=UTC),
        None,
        "1d",
    )

    # Test invalid start date
    result = _validate_history_input(
        start_date="invalid-date", end_date="2023-06-10", interval="1d"
    )
    assert result == (False, None, None, None, None)

    # Test invalid end date
    result = _validate_history_input(
        start_date="2023-06-01", end_date="invalid-date", interval="1d"
    )
    assert result == (False, None, None, None, None)

    # Test end date before start date
    result = _validate_history_input(
        start_date="2023-06-10", end_date="2023-06-01", interval="1d"
    )
    assert result == (False, None, None, None, None)

    # Test end date in the future
    future_date = (dt.datetime.now(UTC) + dt.timedelta(days=1)).strftime("%Y-%m-%d")
    result = _validate_history_input(
        start_date="2023-06-01", end_date=future_date, interval="1d"
    )
    assert result == (False, None, None, None, None)
