import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        from gui import PyTerminalGUI
        import tkinter as tk
        root = tk.Tk()
        app = PyTerminalGUI(root)
        root.mainloop()
    else:
        from cli import CommandLineInterface
        cli = CommandLineInterface()
        cli.run()
