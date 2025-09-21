import shlex

class CommandParser:
    @staticmethod
    def parse(command_input: str):
        # Special shorthand fix (Windows)
        if command_input.strip().lower() == "cd..":
            command_input = "cd .."

        # Split chaining first
        # e.g. "ls && pwd; echo hi" → ["ls && pwd", "echo hi"]
        chain_parts = command_input.split(";")

        commands = []
        for part in chain_parts:
            # Split "&&" → must succeed before next
            subparts = part.split("&&")
            for sub in subparts:
                sub = sub.strip()
                if not sub:
                    continue

                # Split pipes
                pipe_parts = [shlex.split(p.strip()) for p in sub.split("|")]
                commands.append({
                    "pipe_chain": pipe_parts,
                    "must_succeed": True if "&&" in part else False
                })

        return commands
