"""
Tests for the utils.helpers module.
"""

import pytest
import requests
from utils.helpers import (
    _ask_for_ticker,
    check_internet_connection,
    require_internet,
    read_portfolio_keys,
    CurrencyFormatter,  # type: ignore
    ExchangeService,
    check_first_login,
    perform_first_login_tasks,
    first_login_session,
)
import json
import yfinance as yf
import datetime as dt
import pytz

from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import os

os.environ["SKIP_FIRST_LOGIN"] = "1"


def test_check_internet_connection_success(mocker):
    # Mock the requests.get method to simulate a successful response
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200

    # Call the function and assert the result
    assert check_internet_connection(verbose=False) == True


def test_check_internet_connection_no_connection(mocker):
    # Mock the requests.get method to simulate a connection error
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.ConnectionError

    # Call the function and assert the result
    assert check_internet_connection(verbose=False) == False


@require_internet
def dummy_function():
    return "Success"


def test_require_internet_success(mocker):
    # Mock the check_internet_connection function to return True
    mocker.patch("utils.helpers.check_internet_connection", return_value=True)

    # Call the decorated function and assert the result
    assert dummy_function() == "Success"


def test_require_internet_no_connection(mocker):
    # Mock the check_internet_connection function to return False
    mocker.patch("utils.helpers.check_internet_connection", return_value=False)

    # Call the decorated function and assert the result
    assert dummy_function() == None


def test_ask_for_ticker_valid(mocker):
    # Mock the input function to return a valid ticker
    mocker.patch("builtins.input", return_value="AAPL")

    # Mock the yfinance.Ticker class
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.return_value = yf.Ticker("AAPL")

    # Call the function and assert the result
    stock, ticker = _ask_for_ticker()
    assert stock == "AAPL"
    # do not check the ticker object
    # assert isinstance(ticker, yf.Ticker)


def test_ask_for_ticker_invalid(mocker):
    # Mock the input function to return an invalid ticker
    mocker.patch("builtins.input", return_value="INVALID")

    # Mock the yfinance.Ticker class to raise an exception
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.side_effect = Exception

    # Call the function and assert that it raises an exception
    with pytest.raises(Exception):
        _ask_for_ticker()


def test_read_portfolio_keys(mocker):
    # Mock the content of the JSON file
    mock_file_content = {
        "portfolios": [
            {"name": "Portfolio1", "key": "key1", "secret_key": "secret1"},
            {"name": "Portfolio2", "key": "key2", "secret_key": "secret2"},
        ]
    }
    # Mock the open function to return the mock file content
    mocker.patch(
        "builtins.open", mocker.mock_open(read_data=json.dumps(mock_file_content))
    )

    # Call the function and assert the result
    result = read_portfolio_keys("dummy_path", "Portfolio1")
    assert result == {"key": "key1", "secret_key": "secret1"}


def test_read_portfolio_keys_not_found(mocker):
    # Mock the content of the JSON file
    mock_file_content = {
        "portfolios": [
            {"name": "Portfolio1", "key": "key1", "secret_key": "secret1"},
            {"name": "Portfolio2", "key": "key2", "secret_key": "secret2"},
        ]
    }
    # Mock the open function to return the mock file content
    mocker.patch(
        "builtins.open", mocker.mock_open(read_data=json.dumps(mock_file_content))
    )

    # Call the function and assert the result
    result = read_portfolio_keys("dummy_path", "Portfolio3")
    assert result == {}


def test_read_portfolio_keys_file_not_found(mocker):
    # Mock the open function to raise a FileNotFoundError
    mocker.patch("builtins.open", side_effect=FileNotFoundError)

    # Call the function and assert the result
    result = read_portfolio_keys("dummy_path", "Portfolio1")
    assert result == {}


def test_get_symbol():
    formatter = CurrencyFormatter()

    # Test known currency codes
    assert formatter.get_symbol("USD") == "$"
    assert formatter.get_symbol("EUR") == "€"
    assert formatter.get_symbol("GBP") == "£"
    assert formatter.get_symbol("JPY") == "¥"
    assert formatter.get_symbol("CNY") == "¥"
    assert formatter.get_symbol("HKD") == "HK$"
    assert formatter.get_symbol("CHF") == "CHF"
    assert formatter.get_symbol("CAD") == "C$"
    assert formatter.get_symbol("AUD") == "A$"

    # Test unknown currency code
    assert formatter.get_symbol("XYZ") == "XYZ "


# TODO: Does not work currently
@pytest.mark.skip(reason="Requires pytz and datetime to be properly mocked.")
def test_is_exchange_open(mocker):
    # Mock the current time and timezone
    mock_timezone = mocker.patch(
        "pytz.timezone", return_value=pytz.timezone("America/New_York")
    )
    mock_datetime = mocker.patch("datetime.datetime")
    mock_datetime.now.return_value = dt.datetime(
        2023, 6, 13, 10, 0, tzinfo=pytz.timezone("America/New_York")
    )

    # Test NYSE open
    is_open, status = ExchangeService.is_exchange_open("NYSE")
    assert is_open == True
    assert status == "NYSE OPEN"

    # Test NYSE closed (before open time)
    mock_datetime.now.return_value = dt.datetime(
        2023, 6, 13, 9, 0, tzinfo=pytz.timezone("America/New_York")
    )
    is_open, status = ExchangeService.is_exchange_open("NYSE")
    assert is_open == False
    assert status == "NYSE CLOSED"

    # Test NYSE closed (after close time)
    mock_datetime.now.return_value = dt.datetime(
        2023, 6, 13, 17, 0, tzinfo=pytz.timezone("America/New_York")
    )
    is_open, status = ExchangeService.is_exchange_open("NYSE")
    assert is_open == False
    assert status == "NYSE CLOSED"

    # Test NYSE closed (weekend)
    mock_datetime.now.return_value = dt.datetime(
        2023, 6, 10, 10, 0, tzinfo=pytz.timezone("America/New_York")
    )  # Saturday
    is_open, status = ExchangeService.is_exchange_open("NYSE")
    assert is_open == False
    assert status == "NYSE CLOSED (Weekend)"

    # Test unknown exchange
    is_open, status = ExchangeService.is_exchange_open("UNKNOWN")
    assert is_open == False
    assert status == "Unknown exchange: UNKNOWN"


@pytest.fixture
def mock_config_path():
    return Path(__file__).resolve().parent / "configs" / "alpaca.json"


@pytest.fixture
def mock_config_dir():
    return Path(__file__).resolve().parent / "configs"


@pytest.fixture
def mock_portfolio_data():
    return {
        "portfolios": [
            {
                "name": "Test Portfolio",
                "key": "test_key",
                "secret_key": "test_secret",
            }
        ]
    }


def test_check_first_login(mock_config_path):
    os.environ["SKIP_FIRST_LOGIN"] = "0"
    with patch("os.path.exists") as mock_exists, patch(
        "os.path.getsize"
    ) as mock_getsize:
        # Test when file does not exist
        mock_exists.return_value = False
        assert check_first_login() == True

        # Test when file exists but is empty
        mock_exists.return_value = True
        mock_getsize.return_value = 0
        assert check_first_login() == True

        # Test when file exists and is not empty
        mock_getsize.return_value = 100
        assert check_first_login() == False
    os.environ["SKIP_FIRST_LOGIN"] = "1"


def test_first_login_session_decorator(mock_config_path):
    os.environ["SKIP_FIRST_LOGIN"] = "0"

    @first_login_session
    def dummy_function():
        return "Function Executed"

    with patch("utils.helpers.check_first_login", return_value=True), patch(
        "utils.helpers.perform_first_login_tasks"
    ) as mock_perform_first_login_tasks:
        result = dummy_function()
        mock_perform_first_login_tasks.assert_called_once()
        assert result == "Function Executed"

    with patch("utils.helpers.check_first_login", return_value=False), patch(
        "utils.helpers.perform_first_login_tasks"
    ) as mock_perform_first_login_tasks:
        result = dummy_function()
        mock_perform_first_login_tasks.assert_not_called()
        assert result == "Function Executed"

    os.environ["SKIP_FIRST_LOGIN"] = "1"
