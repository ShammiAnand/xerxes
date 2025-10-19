DESTRUCTIVE_KEYWORDS = {
    "delete",
    "remove",
    "destroy",
    "terminate",
    "kill",
    "stop",
    "rm",
    "prune",
    "drop",
    "truncate",
    "purge",
}


def is_command_destructive(command: str) -> bool:
    command_lower = command.lower()
    return any(keyword in command_lower for keyword in DESTRUCTIVE_KEYWORDS)
