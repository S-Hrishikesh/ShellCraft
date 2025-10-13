import sys
import os
import subprocess
import shlex

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
    return 1 # Return 1 to continue the shell loop

def shell_exit(args):
    """Built-in 'exit' command."""
    return 0 # Return 0 to terminate the shell loop

BUILTIN_COMMANDS = {
    "cd": shell_cd,
    "exit": shell_exit,
}

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
            if i > 0: # Built-ins cannot be on the receiving end of a pipe
                print("shellcraft: built-in commands cannot be piped.", file=sys.stderr)
                return 1
            return BUILTIN_COMMANDS[command_args[0]](command_args)

        is_last_command = (i == len(commands) - 1)
        current_stdout = stdout_fd if is_last_command else subprocess.PIPE

        try:
            # --- THIS IS THE COMBINED PART FOR WINDOWS COMPATIBILITY ---
            # On Windows, built-in commands need to be run through the shell.
            # We check the OS and set shell=True only for Windows.
            use_shell = sys.platform == "win32"
            
            print(f"--- ShellCraft is executing: {command_args} ---")
            proc = subprocess.Popen(
                command_args,
                stdin=prev_pipe,
                stdout=current_stdout,
                stderr=sys.stderr,
                shell=use_shell  # This enables Windows compatibility
            )
            # -----------------------------------------------------------
            learn_command(command_args[0])

            processes.append(proc)
            
            # If the previous command's output was piped, close that pipe
            if prev_pipe != sys.stdin:
                prev_pipe.close()
            
            # The next command's input is the current command's output
            prev_pipe = proc.stdout

        except FileNotFoundError:
            print(f"shellcraft: command not found: {command_args[0]}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"shellcraft: error: {e}", file=sys.stderr)
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

        except EOFError: # User pressed Ctrl+D
            print("\nExiting ShellCraft.")
            break
        except KeyboardInterrupt: # User pressed Ctrl+C
            print() # Move to a new line
            continue

def main():
    """Main entry point for the shell."""
    setup_autocomplete(command_list_getter=lambda: load_learned_commands() + COMMON_COMMANDS)
    shell_loop()

if __name__ == "__main__":
    main()