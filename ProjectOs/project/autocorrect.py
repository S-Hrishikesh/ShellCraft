# autocorrect.py
import json
import os

# Base list of valid commands
COMMON_COMMANDS = [
    "ls", "cat", "grep", "cd", "echo", "pwd", "mkdir", "rmdir",
    "rm", "cp", "mv", "touch", "clear", "exit", "find", "head",
    "tail", "sort", "chmod", "chown", "man", "less", "more"
]

LEARN_FILE = "learned_cmds.json"

# ---------------------------------------------------------------------
# Predefined typo map: most common real-world misspellings per command
# ---------------------------------------------------------------------
COMMON_TYPOS = {
    "ls": ["sl", "lp", "lz", "lx", "lz"],
    "cat": ["cta", "ct", "act", "cqt", "cst"],
    "grep": ["gtep", "gerp", "grp", "greo", "geep"],
    "cd": ["dc", "vd", "xd", "cs", "xv"],
    "echo": ["ehco", "eho", "eco", "ecco", "ech"],
    "pwd": ["pdw", "pdd", "pw", "pwf"],
    "mkdir": ["mdkir", "mkidr", "mkdr", "mkr", "mkkir"],
    "rmdir": ["rdmir", "rmidr", "rmdr", "rmir"],
    "rm": ["mr", "rn", "rmm", "rmmr"],
    "cp": ["pc", "cpo", "cpp", "cpq"],
    "mv": ["vm", "mn", "mvb", "mvv"],
    "touch": ["tuch", "touc", "touhc", "tuchh", "toch"],
    "clear": ["cler", "claer", "clera", "cear", "cla"],
    "exit": ["exot", "exiy", "exut", "exif", "eixt"],
    "find": ["fnid", "fidn", "fnd", "findd", "finn"],
    "head": ["haed", "hed", "headd", "hrad", "hade"],
    "tail": ["tali", "tial", "taol", "tall", "tiall"],
    "sort": ["srot", "sotr", "sor", "soet", "sot"],
    "chmod": ["chomd", "chmd", "chdmo", "chdm", "chd"],
    "chown": ["chonw", "chowm", "choen", "chwon", "chwonw"],
    "man": ["amn", "mna", "maan", "mamn"],
    "less": ["lses", "les", "leess", "lss"],
    "more": ["mroe", "mre", "moer", "moee"]
}

# Reverse mapping for O(1) correction lookup
TYPO_CORRECTIONS = {typo: cmd for cmd, typos in COMMON_TYPOS.items() for typo in typos}

# ---------------------------------------------------------------------
# Persistent learning system (optional)
# ---------------------------------------------------------------------
def load_learned_commands():
    if os.path.exists(LEARN_FILE):
        try:
            with open(LEARN_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_learned_commands(commands):
    with open(LEARN_FILE, "w") as f:
        json.dump(commands, f, indent=2)

def learn_command(command):
    learned = load_learned_commands()
    if command not in COMMON_COMMANDS and command not in learned:
        learned.append(command)
        save_learned_commands(learned)

# ---------------------------------------------------------------------
# Core autocorrect
# ---------------------------------------------------------------------
def autocorrect_command(command):
    """
    Fast and reliable autocorrect:
    1. Checks against predefined typo list.
    2. Falls back to learned commands (case-insensitive match).
    """
    cmd_lower = command.lower()

    # Step 1: direct typo correction
    if cmd_lower in TYPO_CORRECTIONS:
        return TYPO_CORRECTIONS[cmd_lower]

    # Step 2: check learned commands
    learned = load_learned_commands()
    for learned_cmd in learned:
        if cmd_lower == learned_cmd.lower():
            return learned_cmd

    # Step 3: no correction — return as is
    return command
