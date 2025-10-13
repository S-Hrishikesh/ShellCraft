# autocomplete.py
"""
Tab-completion helper for ShellCraft.

Features:
- Completes the first word (command) from:
    COMMON_COMMANDS + learned commands (dynamically)
- Completes file and directory names for subsequent arguments
- Works with readline on Unix-like systems. On Windows it will try
  to use pyreadline if available; otherwise it silently no-ops.
- Avoids ambiguous cross-command collisions by matching the longest
  unique prefix and letting readline cycle through alternatives.
"""

import sys
import os
import glob

# Try to use the same COMMON_COMMANDS and loader from your autocorrect module.
# If you named it differently, change the import accordingly.
try:
    from autocorrect import COMMON_COMMANDS, load_learned_commands
except Exception:
    # Fallback if module layout differs; user can provide list via setup function
    COMMON_COMMANDS = []
    def load_learned_commands():
        return []

# readline may not be available on some Windows installs; handle gracefully.
try:
    import readline
except Exception:
    readline = None

# Keep an internal cache of the dynamic command list (COMMON + learned)
def _get_dynamic_commands():
    """Return the up-to-date list of commands used for completion."""
    learned = []
    try:
        learned = load_learned_commands() or []
    except Exception:
        learned = []
    # Ensure uniqueness and preserve COMMON_COMMANDS order first
    seen = set()
    result = []
    for c in COMMON_COMMANDS + learned:
        if not isinstance(c, str):
            continue
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result

# Completer factory returns a function suitable for readline.set_completer()
def make_completer(command_list_getter=_get_dynamic_commands):
    """
    Returns a completer(text, state) using `command_list_getter()` to fetch commands.
    - If completing first word -> use commands list (prefix match).
    - Else -> filename completion (glob + os.listdir).
    """
    def completer(text, state):
        # If readline not available, can't do completions
        if readline is None:
            return None

        # Determine buffer and current word index
        buf = readline.get_line_buffer()
        begidx = readline.get_begidx()
        endidx = readline.get_endidx()
        # Extract everything typed up to cursor
        before_cursor = buf[:begidx]
        words = before_cursor.split()

        # If we are completing the first word (command)
        if len(words) == 0:
            # cursor is at first word (no preceding words)
            candidates = _command_candidates(text, command_list_getter)
        elif begidx == 0 and buf.strip() == "":  # starting first word but no words yet
            candidates = _command_candidates(text, command_list_getter)
        elif len(words) == 1 and begidx <= len(words[0]):
            # completing the first word (partial)
            candidates = _command_candidates(text, command_list_getter)
        else:
            # Completing an argument -> filename completion
            candidates = _filename_candidates(text)

        # Sort for determinism; readline will iterate by state index
        candidates = sorted(candidates)
        try:
            return candidates[state]
        except IndexError:
            return None

    return completer

def _command_candidates(text, command_list_getter):
    """Return list of commands that start with text (case-sensitive)."""
    commands = command_list_getter()
    if not text:
        return commands[:]
    return [c for c in commands if c.startswith(text)]

def _filename_candidates(text):
    """
    Return file/directory completions. Supports:
    - Relative and absolute paths
    - Quotes are not removed here — readline gives raw text.
    """
    if text == "":
        prefix = "."
    else:
        prefix = text

    # Expand ~ and variables
    prefix = os.path.expanduser(os.path.expandvars(prefix))

    # If prefix ends with a slash, glob everything inside
    if prefix.endswith(os.sep):
        pattern = prefix + "*"
    else:
        pattern = prefix + "*"

    matches = glob.glob(pattern)
    # Add trailing slash for directories to signal completion
    out = []
    for m in matches:
        if os.path.isdir(m):
            out.append(m + os.sep)
        else:
            out.append(m)
    return out

def setup_autocomplete(bind_tab=True, command_list_getter=_get_dynamic_commands):
    """
    Install the completer into readline.

    Parameters:
    - bind_tab: if True, pressing TAB invokes completion (default True)
    - command_list_getter: function returning the list of commands; used to keep
      the completions dynamic (pass a lambda that calls load_learned_commands()).
    """
    global readline  # <-- important fix: we now modify the global variable

    # If readline is missing, attempt to import a Windows fallback
    if readline is None:
        if sys.platform == "win32":
            try:
                import pyreadline as pyreadline_module  # type: ignore
                readline = pyreadline_module
            except Exception:
                print("⚠️  Autocomplete disabled (no readline or pyreadline found).")
                return
        else:
            print("⚠️  Autocomplete disabled (readline not available).")
            return

    # Configure delimiters: we want space, tab and newline to separate words,
    # but keep characters like '/' in filenames.
    try:
        delims = readline.get_completer_delims()
        delims = delims.replace('/', '')  # keep '/' in filenames
        readline.set_completer_delims(delims)
    except Exception:
        pass

    completer = make_completer(command_list_getter)
    readline.set_completer(completer)

    # Bind TAB key
    if bind_tab:
        try:
            readline.parse_and_bind("tab: complete")
        except Exception:
            try:
                readline.parse_and_bind("bind ^I rl_complete")
            except Exception:
                pass

    # Optional: make completion case-insensitive
    try:
        readline.parse_and_bind("set completion-ignore-case on")
    except Exception:
        pass

