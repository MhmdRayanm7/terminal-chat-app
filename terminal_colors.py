# ANSI colors used only when display messages
RESET = "\033[0m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
GRAY = "\033[90m"


def color_text(message, color):
    # add color before message and reset color after it
    return f"{color}{message}{RESET}"
