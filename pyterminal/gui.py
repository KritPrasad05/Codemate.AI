import tkinter as tk
from tkinter import scrolledtext, Menu
import os, re
from core.parser import CommandParser
from core.executor import CommandExecutor

class PyTerminalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTerminal Emulator")
        self.root.geometry("1000x600")
        self.root.configure(bg="black")

        # --- Menu Bar ---
        menu_bar = Menu(root, bg="black", fg="white", tearoff=0)
        root.config(menu=menu_bar)
        file_menu = Menu(menu_bar, tearoff=0, bg="black", fg="white")
        file_menu.add_command(label="Clear", command=self.clear_output)
        file_menu.add_command(label="Exit", command=root.destroy)
        menu_bar.add_cascade(label="Menu", menu=file_menu)

        # --- Output Area ---
        self.output_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, bg="black", fg="white",
            insertbackground="white", font=("Consolas", 12)
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.output_area.config(state=tk.DISABLED)

        # Syntax highlighting tags
        self.output_area.tag_config("error", foreground="red")
        self.output_area.tag_config("success", foreground="green")
        self.output_area.tag_config("dir", foreground="cyan")
        self.output_area.tag_config("info", foreground="yellow")
        self.output_area.tag_config("prompt", foreground="magenta")

        # --- Input Area ---
        self.input_var = tk.StringVar()
        self.input_field = tk.Entry(
            root, textvariable=self.input_var, bg="black",
            fg="cyan", insertbackground="cyan", font=("Consolas", 12)
        )
        self.input_field.pack(fill=tk.X, padx=10, pady=5)
        self.input_field.bind("<Return>", self.execute_command)
        self.input_field.bind("<Up>", self.show_prev_command)
        self.input_field.bind("<Down>", self.show_next_command)

        # Command history
        self.history = []
        self.history_index = -1

        # Core components
        self.executor = CommandExecutor()
        self.print_banner()

    def print_banner(self):
        banner = """
██████╗ ██╗   ██╗████████╗████████╗███████╗██████╗ ███╗   ███╗ █████╗ ██╗     
██╔══██╗██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     
██████╔╝██║   ██║   ██║      ██║   █████╗  ██████╔╝██╔████╔██║███████║██║     
██╔═══╝ ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║██║     
██║     ╚██████╔╝   ██║      ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║███████╗
╚═╝      ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
                            Python Terminal Emulator
        """
        self.write_output(banner, "info")
        self.write_output("Type 'help' for available commands.\n", "success")

    def clear_output(self):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state=tk.DISABLED)

    def write_output(self, text, tag=None):
        self.output_area.config(state=tk.NORMAL)
        clean_text = re.sub(r"\x1b\[[0-9;]*m", "", text)  # remove ANSI codes
        self.output_area.insert(tk.END, clean_text + "\n", tag)
        self.output_area.config(state=tk.DISABLED)
        self.output_area.see(tk.END)

    # --- Command History Navigation ---
    def show_prev_command(self, event=None):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            self.input_var.set(self.history[self.history_index])
        return "break"

    def show_next_command(self, event=None):
        if self.history:
            self.history_index = min(len(self.history) - 1, self.history_index + 1)
            self.input_var.set(self.history[self.history_index])
        return "break"

    def execute_command(self, event=None):
        command_input = self.input_var.get().strip()

        # Fix cd.. to cd ..
        if command_input.startswith("cd.."):
            command_input = command_input.replace("cd..", "cd ..")

        self.input_var.set("")  # clear input
        if not command_input:
            return

        # Save to history
        self.history.append(command_input)
        self.history_index = len(self.history)

        # Show command prompt
        cwd = os.getcwd()
        prompt = f"{os.getenv('USERNAME') or 'user'}@pyterminal:{cwd}$ {command_input}"
        self.write_output(prompt, "prompt")

        # Special case: clear
        if command_input.lower() == "clear":
            self.clear_output()
            return

        # Exit command
        if command_input.lower() in ["exit", "quit"]:
            self.write_output("Exiting PyTerminal... Goodbye!", "error")
            self.root.after(1000, self.root.destroy)
            return

        # Parse + Execute
        parsed_commands = CommandParser.parse(command_input)
        self.capture_execution(parsed_commands)

    def capture_execution(self, parsed_commands):
        from io import StringIO
        import sys

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        self.executor.execute(parsed_commands)

        sys.stdout = old_stdout
        output = mystdout.getvalue().strip()

        if output:
            if "error" in output.lower() or "not found" in output.lower():
                self.write_output(output, "error")
            elif "dir" in output.lower() or "\\" in output or "/" in output:
                self.write_output(output, "dir")
            else:
                self.write_output(output, "success")


if __name__ == "__main__":
    root = tk.Tk()
    app = PyTerminalGUI(root)
    root.mainloop()
