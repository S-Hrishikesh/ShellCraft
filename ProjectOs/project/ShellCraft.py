import sys
import os
import subprocess
import shlex
from smart_insights import display_error

# --- Autocorrect + learning system ---
from autocorrect import (
    autocorrect_command,
    learn_command,
    load_learned_commands,
    COMMON_COMMANDS
)

# --- Autocomplete system ---
from autocomplete import setup_autocomplete


# --- Built-in Commands ---

def shell_cd(args):
    """Built-in 'cd' command."""
    # Go to the home directory if 'cd' is called without an argument
    target_dir = os.path.expanduser("~") if len(args) < 2 else args[1]

    try:
        os.chdir(target_dir)
    except FileNotFoundError:
        print(f"shellcraft: cd: no such file or directory: {target_dir}", file=sys.stderr)
    return 1  # Return 1 to continue the shell loop


def shell_exit(args):
    """Built-in 'exit' command."""
    return 0  # Return 0 to terminate the shell loop


BUILTIN_COMMANDS = {
    "cd": shell_cd,
    "exit": shell_exit,
}
# --- Cross-Platform Command Aliases ---
# This layer makes ShellCraft feel consistent across Windows, Linux, and macOS.

if sys.platform == "win32":
    ALIASES = {
        "ls": "dir",
        "clear": "cls",
        "cp": "copy",
        "mv": "move",
        "rm": "del",
        "rmdir": "rmdir",
        "cat": "type",
        "pwd": "cd",
        "grep": "findstr",
        "touch": "type nul >",
        "man": "help",
    }
else:
    ALIASES = {}


# --- Core Execution Logic ---

def execute_commands(commands):
    """Executes a list of commands, handling pipes and I/O redirection."""
    stdin_fd = sys.stdin
    stdout_fd = sys.stdout

    # Handle input redirection '<'
    if '<' in commands[0]:
        index = commands[0].index('<')
        filename = commands[0][index + 1]
        try:
            stdin_fd = open(filename, 'r')
        except FileNotFoundError:
            print(f"shellcraft: no such file or directory: {filename}", file=sys.stderr)
            return 1
        commands[0] = commands[0][:index]

    # Handle output redirection '>'
    if '>' in commands[-1]:
        index = commands[-1].index('>')
        filename = commands[-1][index + 1]
        stdout_fd = open(filename, 'w')
        commands[-1] = commands[-1][:index]

    processes = []
    prev_pipe = stdin_fd

    for i, command_args in enumerate(commands):
        if not command_args:
            continue

        # --- Inline autocorrect ---
        command_args[0] = autocorrect_command(command_args[0])
        # --------------------------

        # Handle built-in commands
        if command_args[0] in BUILTIN_COMMANDS:
            if i > 0:  # Built-ins cannot be on the receiving end of a pipe
                print("shellcraft: built-in commands cannot be piped.", file=sys.stderr)
                return 1
            return BUILTIN_COMMANDS[command_args[0]](command_args)

        is_last_command = (i == len(commands) - 1)
        use_shell = sys.platform == "win32"

        try:
            result = subprocess.run(
                command_args,
                stdin=prev_pipe,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=use_shell
            )

            # Print output normally
            if result.stdout:
                print(result.stdout, end="")

            # Handle errors with smart insights
            if result.returncode != 0 and result.stderr:
                display_error(" ".join(command_args), result.stderr)

            learn_command(command_args[0])

            # Manage pipes
            if prev_pipe != sys.stdin:
                prev_pipe.close()

            prev_pipe = result.stdout

        except FileNotFoundError:
            display_error(" ".join(command_args), f"Command not found: {command_args[0]}")
            return 1

        except Exception as e:
            display_error(" ".join(command_args), str(e))
            return 1

    # Wait for all child processes to complete
    for proc in processes:
        proc.wait()

    # Clean up the file descriptor if we redirected output
    if stdout_fd != sys.stdout:
        stdout_fd.close()

    return 1


# --- Main Shell Loop ---

def shell_loop():
    """The main loop of the shell: read, parse, execute."""
    status = 1
    while status:
        try:
            # Create a prompt that shows the current directory
            current_dir = os.getcwd()
            prompt = f"shellcraft:{current_dir}> "
            line = input(prompt)

            if not line.strip():
                continue

            # Parse the line into commands, splitting by pipes
            command_strings = line.split('|')
            commands = [shlex.split(cmd) for cmd in command_strings]

            status = execute_commands(commands)

        except EOFError:  # User pressed Ctrl+D
            print("\nExiting ShellCraft.")
            break
        except KeyboardInterrupt:  # User pressed Ctrl+C
            print()  # Move to a new line
            continue


def main():
    """Main entry point for the shell."""
    setup_autocomplete(command_list_getter=lambda: load_learned_commands() + COMMON_COMMANDS)
    shell_loop()


if __name__ == "__main__":
    main()
