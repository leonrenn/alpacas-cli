from textwrap import TextWrapper

TERMINAL_WIDTH: int = 80  # Default terminal width for pretty printing
WRAPPER: TextWrapper = TextWrapper(width=TERMINAL_WIDTH - 4)  # -4 for margin
