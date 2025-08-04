"""
Commands with respect to setting or deleting aliases available via the command manager.
"""

from typing import List
from .core import (
    Command,
    CommandResult,
)
from utils.pretty_printing import (
    pretty_print_alias_help_text,
    pretty_print_info_text,
    pretty_print_current_aliases,
)
from utils.input_validation import (
    get_validated_input,
    is_non_empty_string,
    is_valid_alias_subcommand,
)


class AliasCommand(Command):
    """
    Command to manage command aliases/shortcuts.
    """

    def execute(self, context) -> CommandResult:
        try:
            valid_alias_subcommands: List[str] = [
                "set",
                "remove",
                "list",
                "help",
            ]
            subcommand = get_validated_input(
                "Enter subcommand (set/remove/list/help): ",
                [is_non_empty_string, is_valid_alias_subcommand],  # type: ignore
                valid_alias_subcommands,
            )

            if subcommand == "help":
                return self._show_help()
            elif subcommand == "list":
                return self._list_aliases(context)
            elif subcommand == "set":
                return self._set_alias(context)
            elif subcommand == "remove":
                return self._remove_alias(context)
            else:
                return CommandResult(
                    success=False,
                    message="Invalid subcommand. Use 'alias help' for usage information.",
                )

        except Exception as e:
            return CommandResult(
                success=False, message=f"Error managing aliases: {str(e)}"
            )

    def description(self) -> str:
        return "Manage command aliases/shortcuts"

    def _show_help(self) -> CommandResult:
        pretty_print_alias_help_text()
        return CommandResult(success=True)

    def _set_alias(self, context) -> CommandResult:
        pretty_print_info_text(context.commands)

        # Get alias details
        cmd_name = get_validated_input(
            "\nEnter command name: ", [is_non_empty_string]  # type: ignore
        )
        if cmd_name not in context.commands:
            return CommandResult(
                success=False, message=f"Command '{cmd_name}' does not exist."
            )

        # NOTE: Could check here not to conflict with existing command names
        alias = get_validated_input(
            "Enter alias (shortcut): ", [is_non_empty_string]  # type: ignore
        )
        if alias in context.commands or alias in context.get_aliases():
            return CommandResult(
                success=False,
                message=f"Alias '{alias}' already exists or conflicts with a command name.",
            )

        # Add alias and save
        context.add_alias(alias, cmd_name)
        return CommandResult(
            success=True, message=f"Alias '{alias}' created for command '{cmd_name}'"
        )

    def _remove_alias(self, context) -> CommandResult:
        aliases = context.get_aliases()
        if not aliases:
            return CommandResult(success=False, message="No aliases defined.")

        pretty_print_current_aliases(aliases)

        alias = get_validated_input("\nEnter alias to remove: ", [is_non_empty_string])  # type: ignore
        if alias not in aliases:
            return CommandResult(
                success=False, message=f"Alias '{alias}' does not exist."
            )

        context.remove_alias(alias)
        return CommandResult(success=True, message=f"Alias '{alias}' removed.")

    def _list_aliases(self, context) -> CommandResult:
        aliases = context.get_aliases()
        if not aliases:
            return CommandResult(success=True, message="No aliases defined.")

        pretty_print_current_aliases(aliases)

        return CommandResult(success=True)
