# smart_insights.py
"""
Smart Command Insights module for ShellCraft.
Provides human-friendly error explanations and colored tips.
"""

import re
import difflib
import os
from colorama import Fore, Style, init

# Initialize colorama for colored output (works on Windows too)
init(autoreset=True)

# --- Helper: Closest command suggestion ---
from autocorrect import COMMON_COMMANDS, load_learned_commands

def closest_command(cmd):
    """Suggest the closest known or learned command."""
    all_cmds = COMMON_COMMANDS + load_learned_commands()
    matches = difflib.get_close_matches(cmd, all_cmds, n=1, cutoff=0.6)
    return matches[0] if matches else "help"

# --- Helper: Suggest closest filename ---
def suggest_similar_file(filename):
    """If a file is missing, suggest similar existing files in the directory."""
    try:
        dirname = os.path.dirname(filename) or "."
        basename = os.path.basename(filename)
        if not os.path.exists(dirname):
            return None
        files = os.listdir(dirname)
        matches = difflib.get_close_matches(basename, files, n=1, cutoff=0.6)
        if matches:
            return os.path.join(dirname, matches[0])
    except Exception:
        return None
    return None


# --- Core analyzer ---
def analyze_error(command, stderr_output):
    """
    Analyze command errors and return a friendly message with colored hints.
    """
    msg = stderr_output.lower()
    base_cmd = command.split()[0] if command else "command"

    # Large set of pattern-suggestion pairs
    error_patterns = [
        # File-related
        (r"no such file or directory",
         f"{Fore.YELLOW}File not found.{Style.RESET_ALL} 💡 Try creating it using → {Fore.CYAN}touch <filename>{Style.RESET_ALL}"),

        (r"file exists",
         f"{Fore.YELLOW}File or directory already exists.{Style.RESET_ALL} 💡 Try using a different name or remove the existing one."),

        (r"is a directory",
         f"{Fore.YELLOW}You’re trying to use a directory as a file.{Style.RESET_ALL} 💡 Use {Fore.CYAN}cd <dir>{Style.RESET_ALL} or specify a file path."),

        (r"not a directory",
         f"{Fore.YELLOW}You’re trying to access a file as a directory.{Style.RESET_ALL} 💡 Check your path or file extension."),

        # Permission-related
        (r"permission denied",
         f"{Fore.YELLOW}Permission denied.{Style.RESET_ALL} 💡 Try running with elevated privileges or fix ownership using {Fore.CYAN}chmod/chown{Style.RESET_ALL}."),

        # Command-related
        (r"command not found",
         f"{Fore.YELLOW}Unknown command.{Style.RESET_ALL} 💡 Did you mean → {Fore.CYAN}{closest_command(base_cmd)}{Style.RESET_ALL}?"),

        (r"not recognized as an internal or external command",
         f"{Fore.YELLOW}Unrecognized command on Windows.{Style.RESET_ALL} 💡 Did you mean → {Fore.CYAN}{closest_command(base_cmd)}{Style.RESET_ALL}?"),

        # Syntax / invalid option
        (r"invalid option",
         f"{Fore.YELLOW}Invalid option used.{Style.RESET_ALL} 💡 Try {Fore.CYAN}man {base_cmd}{Style.RESET_ALL} or {Fore.CYAN}{base_cmd} --help{Style.RESET_ALL}."),

        (r"invalid argument",
         f"{Fore.YELLOW}Invalid argument provided.{Style.RESET_ALL} 💡 Check command usage with {Fore.CYAN}{base_cmd} --help{Style.RESET_ALL}."),

        (r"syntax error",
         f"{Fore.YELLOW}Syntax error detected.{Style.RESET_ALL} 💡 Verify your command format or quotes."),

        # Disk / IO errors
        (r"no space left on device",
         f"{Fore.YELLOW}Disk is full.{Style.RESET_ALL} 💡 Clear space or delete unnecessary files."),

        (r"input/output error",
         f"{Fore.YELLOW}I/O Error encountered.{Style.RESET_ALL} 💡 Check device or disk health."),

        # Network
        (r"network is unreachable",
         f"{Fore.YELLOW}Network unreachable.{Style.RESET_ALL} 💡 Check your internet connection or VPN."),

        (r"connection refused",
         f"{Fore.YELLOW}Connection refused.{Style.RESET_ALL} 💡 Ensure the target service is running and reachable."),

        (r"temporary failure in name resolution",
         f"{Fore.YELLOW}DNS issue.{Style.RESET_ALL} 💡 Check your network configuration or try again later."),

        # Process / memory
        (r"cannot allocate memory",
         f"{Fore.YELLOW}Out of memory.{Style.RESET_ALL} 💡 Close other programs or increase system memory."),

        # Miscellaneous
        (r"bad interpreter",
         f"{Fore.YELLOW}Bad interpreter path in script.{Style.RESET_ALL} 💡 Check the shebang (#!) line in your script."),

        (r"operation not permitted",
         f"{Fore.YELLOW}Operation not permitted.{Style.RESET_ALL} 💡 You may need admin/root privileges."),
    ]

    # Pattern matching
    for pattern, suggestion in error_patterns:
        if re.search(pattern, msg):
            # Special case: file not found — suggest similar
            if "no such file" in msg:
                match = re.search(r"['\"]?([^'\"]+)['\"]?", stderr_output)
                if match:
                    filename = match.group(1)
                    alt = suggest_similar_file(filename)
                    if alt:
                        suggestion += f"\n{Fore.YELLOW}💡 Did you mean: {Fore.CYAN}{alt}{Style.RESET_ALL}?"
            return suggestion

    # No known pattern matched
    return f"{Fore.YELLOW}Unrecognized error.{Style.RESET_ALL} 💡 Try checking the command syntax or path."


def display_error(command, stderr_output):
    """Prints the error and friendly insights in color."""
    print(f"{Fore.RED}[!] Error running command: {command}{Style.RESET_ALL}")
    print(stderr_output.strip())
    insight = analyze_error(command, stderr_output)
    if insight:
        print(insight)