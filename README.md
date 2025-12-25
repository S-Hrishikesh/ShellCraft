# 🐚 ShellCraft – Build Your Own Command Line

**Developed by Team "Kernel Conquerers" during the Kernel Quest Hackathon.**

ShellCraft is an intelligent, cross-platform command-line interpreter (shell) built to bridge the gap between low-level system programming and modern user experience. While traditional shells often obscure process control and command execution flow, ShellCraft illuminates them with smart features like real-time autocorrect and dynamic autocompletion.

## 🚀 Key Features

* *️⃣ **Intelligent Autocomplete:** Powered by `prompt-toolkit`, ShellCraft scans your system's `PATH` and local directories to provide real-time command and file suggestions via the Tab key.
* *️⃣ **Smart Autocorrect:** Uses a custom typo-tolerance algorithm to detect and execute the intended command even if you make a mistake (e.g., `ehoh` becomes `echo`).
* *️⃣ **Cross-Platform Compatibility:** Designed to be platform-agnostic, running seamlessly on **Windows (PowerShell/CMD)**, **macOS**, and **Linux**.
* *️⃣ **Advanced Process Control:** Supports standard Unix-style features including:
* **I/O Redirection:** Use `>` to save output to a file or `<` to read input from one.
* **Pipes (`|`):** Chain multiple commands together to create powerful data pipelines.


* *️⃣ **Dynamic Contextual Prompt:** The prompt automatically updates to show your current working directory, ensuring you always know where you are in the filesystem.

---

## 🏗️ Technical Architecture

ShellCraft is built on a robust **Read-Eval-Print Loop (REPL)** architecture. It treats the shell as a "General Contractor" for the operating system, delegating tasks to external binaries while managing the environment internally.

### Core Components:

1. **The Parser:** Uses `shlex` to handle complex shell-like syntax, ensuring that quotes, spaces, and special characters are tokenized safely.
2. **The Executor:** Leverages the `subprocess` module to manage process lifecycles.
* On **Unix/macOS**, it executes binaries directly.
* On **Windows**, it intelligently invokes the shell environment (`shell=True`) to handle built-in commands like `echo` and `dir`.


3. **Built-in Logic:** Certain commands (like `cd` and `exit`) are handled within the parent process to ensure environment state (like the Current Working Directory) persists correctly.

---

## 🛠️ Installation & Setup

### Prerequisites

* **Python 3.9+**
* **Dependencies:**
```bash
pip install prompt-toolkit

```



### Running the Shell

1. Clone the repository:
```bash
git clone https://github.com/your-repo/ShellCraft.git
cd ShellCraft/project

```


2. Start the application:
```bash
python ShellCraft.py

```



---

## 🏆 Hackathon Journey: Kernel Quest

ShellCraft was developed through a high-pressure, two-round evaluation process:

* **Round 1:** We established the core REPL loop, process management, and the `shlex` parsing logic. We successfully passed the 3:00 PM evaluation to move to the finals.
* **Round 2:** We integrated the "Intelligence Layer," implementing the `ShellCompleter` class and smoothing out the autocorrect logic to ensure a "forgiving" user environment.

---

## 👥 The Team: Kernel Conquerers

* **S Hrishikesh** - Core Logic & Process Management
* **Vishal Narayan** - Autocomplete & Autocorrect Implementation
* **Graceson B** - System Integration & Architecture

---
