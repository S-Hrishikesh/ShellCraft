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
    "ls": [
        "sl", "lz", "lx", "lp", "ld", "la", "lss", "lsz", "lsx", "lsq", "lsw",
        "lzs", "lsd", "ls1", "ls;", "l.s", "l-s"
    ],
    "cat": [
        "cta", "ct", "act", "cqt", "cst", "czt", "cag", "catt", "caa", "cwt",
        "ctt", "car", "catr", "ctq", "caat", "cay", "caz"
    ],
    "grep": [
        "gtep", "gerp", "grp", "greo", "geep", "grpe", "gref", "grepp", "grrp",
        "gtrep", "gre;", "grwp", "greo", "grfp", "gre0", "grdp", "greop"
    ],
    "cd": [
        "dc", "vd", "xd", "cs", "xv", "sd", "cz", "cf", "cx", "cds", "cdd", "cfd",
        "ccd", "cvd", "xd", "cd.", "cd/"
    ],
    "echo": [
        "ehco", "eho", "eco", "ecco", "ech", "ehoh", "echp", "echi", "ehoh", 
        "ech0", "echp", "echu", "eho0", "ech9", "ehc", "echy", "echp"
    ],
    "pwd": [
        "pdw", "pdd", "pw", "pwf", "pwr", "pwq", "pwe", "pww", "pwdc", "pwdx", 
        "pwd1", "pwx", "pwdd", "pwde", "pwv", "ppwd"
    ],
    "mkdir": [
        "mdkir", "mkidr", "mkdr", "mkr", "mkkir", "mkdirr", "mkdir1", "mkid", 
        "mkidr", "mkdirr", "mkrd", "mkidr", "mkdir2", "mkrir", "mkrdr", "mkkdir"
    ],
    "rmdir": [
        "rdmir", "rmidr", "rmdr", "rmir", "rmdr", "rmdirr", "rmder", "rmidr", 
        "rmdir1", "rmdirr", "rmdir2", "rmddr", "rmdor", "rmdjr"
    ],
    "rm": [
        "mr", "rn", "rmm", "rmmr", "rjm", "rwm", "rkm", "rvm", "rrm", "rmn",
        "r.m", "r;m", "rm,", "rmmn", "rmk"
    ],
    "cp": [
        "pc", "cpo", "cpp", "cpq", "c0p", "cpl", "cpi", "cpz", "cp;", "cpm", 
        "cpx", "cp,", "cp1", "ccp", "cp2"
    ],
    "mv": [
        "vm", "mn", "mvb", "mvv", "mvvv", "mvf", "mvc", "mvg", "mvd", "mvn", 
        "mvx", "mv;", "mv,", "mv1", "mvvb"
    ],
    "touch": [
        "tuch", "touc", "touhc", "tuchh", "toch", "toucj", "touvh", "tuchc", 
        "touchh", "toucx", "toucg", "toucq", "touh", "touhch", "tuchj"
    ],
    "clear": [
        "cler", "claer", "clera", "cear", "cla", "clea", "clrar", "clrar", "cleear", 
        "cleer", "clwar", "cldar", "clqar", "c;ear", "c,lear", "cleaf"
    ],
    "exit": [
        "exot", "exiy", "exut", "exif", "eixt", "exiit", "exi", "exot", "exitx", 
        "exot", "exotx", "exkt", "exotq", "exiot", "exutx", "exkt"
    ],
    "find": [
        "fnid", "fidn", "fnd", "findd", "finn", "fihd", "fiod", "finf", "fijd", 
        "fndd", "f8nd", "fjnd", "findf", "fins", "finds"
    ],
    "head": [
        "haed", "hed", "headd", "hrad", "hade", "heda", "hedd", "heaad", "hwad", 
        "heqd", "heasd", "hesd", "hrsd", "hedr", "hwad"
    ],
    "tail": [
        "tali", "tial", "taol", "tall", "tiall", "talii", "taik", "taik", "tiall", 
        "taill", "taol", "taliq", "tauk", "tqil", "tazl"
    ],
    "sort": [
        "srot", "sotr", "sor", "soet", "sot", "sory", "sor5", "sortt", "soort", 
        "sirt", "sotr", "so4t", "s0rt", "soert", "sart"
    ],
    "chmod": [
        "chomd", "chmd", "chdmo", "chdm", "chd", "chmdo", "chmdd", "chmof", "chmld", 
        "chdmo", "chmdo", "chmxd", "chm0d", "chjmd", "chmop"
    ],
    "chown": [
        "chonw", "chowm", "choen", "chwon", "chwonw", "chownn", "chowb", "chowq", 
        "ch0wn", "chawn", "chown1", "chownr", "chownu", "chownx", "chownm"
    ],
    "man": [
        "amn", "mna", "maan", "mamn", "mn", "mann", "manb", "manm", "mwn", 
        "mzn", "mqn", "mab", "mnan", "man1", "manq"
    ],
    "less": [
        "lses", "les", "leess", "lss", "lesss", "lezs", "l3ss", "lews", "lsss", 
        "lesx", "lessx", "lezs", "lqss", "leas", "lesz"
    ],
    "more": [
        "mroe", "mre", "moer", "moee", "mor", "moree", "moore", "morf", "morz", 
        "mo4e", "m0re", "mire", "mkre", "mire", "miree"
    ]
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
