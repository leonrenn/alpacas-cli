"""
Leave empty for now.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from commands.alias import AliasCommand
from commands.core import CommandResult, Command


class MockCommand(Command):
    def execute(self, context) -> CommandResult:
        return CommandResult(success=True)

    def description(self) -> str:
        return "Mock command description"


class MockContext:
    def __init__(self):
        self.commands = {"test_command": MockCommand()}
        self.aliases = {}

    def add_alias(self, alias, command):
        self.aliases[alias] = command

    def remove_alias(self, alias):
        if alias in self.aliases:
            del self.aliases[alias]

    def get_aliases(self):
        return self.aliases


@pytest.fixture
def alias_command():
    return AliasCommand()


@pytest.fixture
def context():
    return MockContext()


@pytest.mark.skip(reason="This test is not implemented yet")
def test_set_alias():
    pass


@pytest.mark.skip(reason="This test is not implemented yet")
def test_remove_alias():
    pass


def test_list_aliases(alias_command, context):
    result = alias_command._list_aliases(context)
    assert result.success


def test_show_help(alias_command):
    result = alias_command._show_help()
    assert result.success
