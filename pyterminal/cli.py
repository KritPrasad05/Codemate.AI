import os
import readline

from parser import CommandParser
from executor import CommandExecutor
from completer import AutoCompleter

from colorama import Fore, Style

class CommandLineInterface:
    def __init__(self):
        self.running = True
        self.prompt = self._build_prompt()
        self.executor = CommandExecutor()

        # --- NEW: history + autocomplete ---
        self.history_file = os.path.expanduser("~/.pyterminal_history")
        self._setup_history()
        self._setup_autocomplete()

    def _build_prompt(self):
        user = os.getenv("USERNAME") or os.getenv("USER") or "user"
        cwd = os.getcwd()
        return f"{Fore.GREEN}{user}{Style.RESET_ALL}@{Fore.CYAN}pyterminal{Style.RESET_ALL}:{Fore.YELLOW}{cwd}{Style.RESET_ALL}$ "

    # -------- History --------
    def _setup_history(self):
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            open(self.history_file, "wb").close()

    def _save_history(self):
        readline.write_history_file(self.history_file)

    # -------- Autocomplete --------
    def _setup_autocomplete(self):
        completer = AutoCompleter(list(self.executor.builtins.keys()))
        readline.set_completer(completer.complete)
        readline.parse_and_bind("tab: complete")

    def run(self):
        while self.running:
            try:
                command_input = input(self.prompt).strip()
                if not command_input:
                    continue

                if command_input.lower() in ["exit", "quit"]:
                    print("Exiting PyTerminal... Goodbye!")
                    self._save_history()
                    self.running = False
                    continue

                parsed_commands = CommandParser.parse(command_input)
                self.executor.execute(parsed_commands)

                self.prompt = self._build_prompt()

            except (EOFError, KeyboardInterrupt):
                print("\nExiting PyTerminal... Goodbye!")
                self._save_history()
                self.running = False


