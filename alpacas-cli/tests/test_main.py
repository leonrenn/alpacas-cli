"""Tests for the main module of the Alpacas CLI application."""

import sys
import os

# Füge den Pfad zu main.py hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import main


def test_main_success(mocker):
    # Mock the CommandManager and its methods
    mock_manager = mocker.patch("main.CommandManager")
    mock_manager.return_value.run_command_loop.return_value = None
    mock_manager.return_value.print_banner.return_value = None

    # Mock the check_internet_connection function
    mocker.patch("main.check_internet_connection", return_value=True)

    # Call the main function and assert the exit code
    assert main() == 0


def test_main_no_internet(mocker):
    # Mock the CommandManager and its methods
    mock_manager = mocker.patch("main.CommandManager")
    mock_manager.return_value.run_command_loop.return_value = None
    mock_manager.return_value.print_banner.return_value = None

    # Mock the check_internet_connection function
    mocker.patch("main.check_internet_connection", return_value=False)

    # Call the main function and assert the exit code
    assert main() == 1


def test_main_keyboard_interrupt(mocker):
    # Mock the CommandManager and its methods
    mock_manager = mocker.patch("main.CommandManager")
    mock_manager.return_value.run_command_loop.side_effect = KeyboardInterrupt

    # Mock the check_internet_connection function
    mocker.patch("main.check_internet_connection", return_value=True)

    # Call the main function and assert the exit code
    assert main() == 130


def test_main_unexpected_error(mocker):
    # Mock the CommandManager and its methods
    mock_manager = mocker.patch("main.CommandManager")
    mock_manager.return_value.run_command_loop.side_effect = Exception(
        "Unexpected error"
    )

    # Mock the check_internet_connection function
    mocker.patch("main.check_internet_connection", return_value=True)

    # Call the main function and assert the exit code
    assert main() == 1
