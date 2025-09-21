import os
import readline

class AutoCompleter:
    def __init__(self, commands):
        self.commands = commands

    def complete(self, text, state):
        """Tab completion logic"""
        # List of suggestions (commands + files/dirs)
        options = [cmd for cmd in self.commands if cmd.startswith(text)]

        # Add filesystem matches
        options.extend(f for f in os.listdir('.') if f.startswith(text))

        # Remove duplicates
        options = sorted(set(options))

        # Return the state-th option, or None if out of range
        if state < len(options):
            return options[state]
        return None
