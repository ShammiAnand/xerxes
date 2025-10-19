from ..llm.base import Message


class ChatSession:
    def __init__(self, max_history: int = 20):
        self.messages: list[Message] = []
        self.max_history = max_history

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        self._trim_history()

    def add_system_message(self, content: str) -> None:
        if self.messages and self.messages[0].role == "system":
            self.messages[0] = Message(role="system", content=content)
        else:
            self.messages.insert(0, Message(role="system", content=content))

    def get_messages(self) -> list[Message]:
        return self.messages

    def clear(self) -> None:
        system_msg = None
        if self.messages and self.messages[0].role == "system":
            system_msg = self.messages[0]

        self.messages = []
        if system_msg:
            self.messages.append(system_msg)

    def _trim_history(self) -> None:
        if len(self.messages) <= self.max_history:
            return

        system_msg = None
        if self.messages and self.messages[0].role == "system":
            system_msg = self.messages[0]
            remaining = self.messages[1:]
        else:
            remaining = self.messages

        trimmed = remaining[-(self.max_history - 1) :]

        self.messages = []
        if system_msg:
            self.messages.append(system_msg)
        self.messages.extend(trimmed)
