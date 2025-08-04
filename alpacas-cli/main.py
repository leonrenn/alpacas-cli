"""
Main entry point.
"""

from commands.manager import CommandManager
from utils.helpers import check_internet_connection, first_login_session
from utils.pretty_printing import pretty_print_internet_required


@first_login_session
def main() -> int:
    """
    Main function that initializes and runs the Portfolio Management.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Initialize the portfolio manager
        manager: CommandManager = CommandManager()

        # Print the banner first
        manager.print_banner()

        # Check if internet connection is available
        if not check_internet_connection(verbose=False):
            pretty_print_internet_required()
            return 1

        # Start the command loop
        manager.run_command_loop()
        return 0

    except KeyboardInterrupt:
        print("\n\nKeyboardInterrupt. Exiting...")
        return 130
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return 1


if __name__ == "__main__":
    exit_code: int = main()
    exit(exit_code)
