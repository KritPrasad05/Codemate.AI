# 🖥️ PyTerminal Emulator

A full-featured **Python-based terminal emulator** built for the **CodeMate Hackathon 2025 @ SRMIST** 🚀.  
This project mimics a real-world command-line environment, supporting **command execution, file operations, process management, pipes, chaining, and even a GUI mode**.

---

## ✨ Features

- **Custom Shell** with support for:
  - `ls`, `cd`, `pwd`, `echo`, `clear`
  - `cpu`, `mem`, `ps`, `kill`
  - File ops → `touch`, `mkdir`, `rm`, `rmdir`
  - Archiving → `zip`, `unzip`
  - Search → `find`
- **Command chaining & pipes**
  - `ls && pwd`
  - `ls ; pwd ; echo Done`
  - `cat file.txt | more`
- **Process Management**
  - `ps` → list processes  
  - `kill <pid>` → terminate process
- **System Monitoring**
  - `cpu` → show CPU usage  
  - `mem` → show memory usage
- **File System Operations**
  - Create/remove files & directories  
  - Zip/unzip archives
- **Cross-platform** (Windows, Linux, macOS)
- **Dual Modes**
  - CLI Mode → `python main.py`
  - GUI Mode → `python main.py gui`
- **Polished GUI**
  - Tkinter-powered terminal window  
  - Syntax highlighting (errors red, dirs cyan, info yellow)  
  - Menu bar (Clear / Exit)  
  - Scrollable history & command recall ('' / `↓`)

---

## 📂 Project Structure

