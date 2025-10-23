from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory


def create_input_session() -> PromptSession:
    history = InMemoryHistory()
    return PromptSession(
        history=history,
        enable_history_search=True,
        multiline=False,
    )


def get_user_input(session: PromptSession) -> str:
    return session.prompt(HTML("<b><ansicyan>You:</ansicyan></b> "))
