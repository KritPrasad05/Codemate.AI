import os
import psutil
import zipfile
import subprocess

from colorama import Fore, Style, init
init(autoreset=True)

class CommandExecutor:
    def __init__(self):
        self.builtins = {
            "cd": self.change_directory,
            "pwd": self.print_working_directory,
            "ls": self.list_directory,
            "echo": self.echo,
            "cpu": self.cpu_usage,
            "mem": self.memory_usage,
            "ps": self.list_processes,
            "kill": self.kill_process,
            "touch": self.touch,
            "mkdir": self.make_directory,
            "rm": self.remove_file,
            "rmdir": self.remove_directory,
            "find": self.find_files,
            "zip": self.zip_files,
            "unzip": self.unzip_file,
            "clear": self.clear_screen,
            "help": self.help_menu
        }

        # Command descriptions for 'help'
        self.command_help = {
            "cd": "Change directory",
            "pwd": "Print working directory",
            "ls": "List files in directory",
            "echo": "Print text to terminal",
            "cpu": "Show CPU usage",
            "mem": "Show memory usage",
            "ps": "List running processes",
            "kill": "Terminate process by PID",
            "touch": "Create empty file",
            "mkdir": "Create directory",
            "rm": "Remove file (or use -r for dir)",
            "rmdir": "Remove empty directory",
            "find": "Find files/directories",
            "zip": "Create zip archive",
            "unzip": "Extract zip archive",
            "clear": "Clear the terminal screen",
            "help": "Show available commands"
        }

    def execute(self, parsed_commands):
        """Executes a list of parsed commands (with chaining + pipes)."""
        last_status = 0  # track success/failure

        for command in parsed_commands:
            pipe_chain = command["pipe_chain"]
            must_succeed = command["must_succeed"]

            if must_succeed and last_status != 0:
                # Skip if previous failed
                continue

            last_status = self._execute_pipe_chain(pipe_chain)

    def _execute_pipe_chain(self, pipe_chain):
        """Handles piping between commands."""
        prev_proc = None
        processes = []

        for i, cmd_parts in enumerate(pipe_chain):
            cmd = cmd_parts[0]
            args = cmd_parts[1:]

            # Builtin commands only work standalone (not in middle of pipe)
            if cmd in self.builtins and len(pipe_chain) == 1:
                self.builtins[cmd](args)
                return 0

            try:
                if prev_proc is None:
                    proc = subprocess.Popen(
                        cmd_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                else:
                    proc = subprocess.Popen(
                        cmd_parts, stdin=prev_proc.stdout,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                processes.append(proc)
                prev_proc = proc
            except FileNotFoundError:
                print(f"Command not found: {cmd}")
                return 1
            except Exception as e:
                print(f"Error running command {cmd}: {e}")
                return 1

        # Collect output from last process in the pipe
        if processes:
            out, err = processes[-1].communicate()
            if out:
                print(out.strip())
            if err:
                print(err.strip())
            return processes[-1].returncode
        return 0

    # -------- Built-ins --------
    def change_directory(self, args):
        try:
            if args:
                os.chdir(args[0])
            else:
                os.chdir(os.path.expanduser("~"))
        except Exception as e:
            print(f"cd: {e}")

    def print_working_directory(self, args):
        print(os.getcwd())

    def list_directory(self, args):
        try:
            path = args[0] if args else os.getcwd()
            entries = os.listdir(path)
            for entry in entries:
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    print(f"[DIR]  {entry}")
                else:
                    print(f"       {entry}")
        except Exception as e:
            print(f"ls: {e}")

    def echo(self, args):
        """Implements 'echo' command"""
        print(" ".join(args))

    # -------- New System Monitoring Commands --------
    def cpu_usage(self, args):
        """Show CPU usage percentage"""
        print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")

    def memory_usage(self, args):
        """Show memory usage stats"""
        mem = psutil.virtual_memory()
        print(f"Memory Used: {mem.percent}% ({mem.used // (1024 ** 2)} MB / {mem.total // (1024 ** 2)} MB)")

    def list_processes(self, args):
        """List running processes"""
        print(f"{'PID':<10} {'Name':<25} {'Status':<10}")
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                print(f"{proc.info['pid']:<10} {proc.info['name']:<25} {proc.info['status']:<10}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def kill_process(self, args):
        """Kill process by PID"""
        if not args:
            print("Usage: kill <pid>")
            return
        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            proc.terminate()
            print(f"Process {pid} terminated.")
        except Exception as e:
            print(f"kill: {e}")

    # -------- File/Directory Operations --------
    def touch(self, args):
        """Create an empty file"""
        if not args:
            print("Usage: touch <filename>")
            return
        try:
            open(args[0], 'a').close()
            print(f"Created file: {args[0]}")
        except Exception as e:
            print(f"touch: {e}")

    def make_directory(self, args):
        """Create a directory"""
        if not args:
            print("Usage: mkdir <dirname>")
            return
        try:
            os.makedirs(args[0], exist_ok=True)
            print(f"Created directory: {args[0]}")
        except Exception as e:
            print(f"mkdir: {e}")

    def remove_file(self, args):
        """Delete a file or directory recursively"""
        if not args:
            print("Usage: rm <file>")
            return
        target = args[0]
        try:
            if os.path.isdir(target):
                if len(args) > 1 and args[1] == "-r":
                    shutil.rmtree(target)
                    print(f"Removed directory recursively: {target}")
                else:
                    print(f"rm: cannot remove '{target}': Is a directory (use rm -r)")
            else:
                os.remove(target)
                print(f"Removed file: {target}")
        except Exception as e:
            print(f"rm: {e}")

    def remove_directory(self, args):
        """Remove empty directory"""
        if not args:
            print("Usage: rmdir <dirname>")
            return
        try:
            os.rmdir(args[0])
            print(f"Removed directory: {args[0]}")
        except Exception as e:
            print(f"rmdir: {e}")

    # -------- Finding Files --------
    def find_files(self, args):
        """Find files/directories by name"""
        if not args:
            print("Usage: find <name>")
            return
        target = args[0].lower()
        for root, dirs, files in os.walk("."):
            for name in files + dirs:
                if target in name.lower():
                    print(os.path.join(root, name))

    # -------- Archiving --------
    def zip_files(self, args):
        """Create a zip archive"""
        if len(args) < 2:
            print("Usage: zip <archive.zip> <file1> <file2> ...")
            return
        archive_name = args[0]
        try:
            with zipfile.ZipFile(archive_name, 'w') as zipf:
                for f in args[1:]:
                    zipf.write(f)
            print(f"Created archive: {archive_name}")
        except Exception as e:
            print(f"zip: {e}")

    def unzip_file(self, args):
        """Extract zip archive"""
        if not args:
            print("Usage: unzip <archive.zip>")
            return
        try:
            with zipfile.ZipFile(args[0], 'r') as zipf:
                zipf.extractall()
            print(f"Extracted: {args[0]}")
        except Exception as e:
            print(f"unzip: {e}")

    # -------- Enhancements --------
    def clear_screen(self, args):
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def help_menu(self, args):
        """Display all commands with one-line description"""
        print(Fore.YELLOW + "Available Commands:\n" + Style.RESET_ALL)
        for cmd, desc in sorted(self.command_help.items()):
            print(f"{Fore.CYAN}{cmd:<10}{Style.RESET_ALL} - {desc}")

    # -------- Enhanced List Directory --------
    def list_directory(self, args):
        """Colored ls output"""
        try:
            path = args[0] if args else os.getcwd()
            entries = os.listdir(path)
            for entry in entries:
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    print(Fore.BLUE + entry + Style.RESET_ALL)
                else:
                    print(entry)
        except Exception as e:
            print(Fore.RED + f"ls: {e}" + Style.RESET_ALL)

    # -------- Error Example Update --------
    def change_directory(self, args):
        try:
            if args:
                os.chdir(args[0])
            else:
                os.chdir(os.path.expanduser("~"))
        except Exception as e:
            print(Fore.RED + f"cd: {e}" + Style.RESET_ALL)