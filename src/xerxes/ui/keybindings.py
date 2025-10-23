from prompt_toolkit.key_binding import KeyBindings


def create_cancellation_bindings() -> tuple[KeyBindings, dict]:
    bindings = KeyBindings()
    state = {"cancelled": False}

    @bindings.add("escape")
    def cancel_execution(event):
        state["cancelled"] = True
        event.app.exit()

    return bindings, state


def create_command_preview_bindings() -> tuple[KeyBindings, dict]:
    bindings = KeyBindings()
    state = {"choice": "run"}

    @bindings.add("r")
    @bindings.add("R")
    def run_command(event):
        state["choice"] = "run"
        event.app.exit()

    @bindings.add("s")
    @bindings.add("S")
    def skip_command(event):
        state["choice"] = "skip"
        event.app.exit()

    @bindings.add("a")
    @bindings.add("A")
    def always_run(event):
        state["choice"] = "always"
        event.app.exit()

    @bindings.add("c-c")
    def cancel(event):
        state["choice"] = "skip"
        event.app.exit()

    return bindings, state


def create_output_expansion_bindings() -> tuple[KeyBindings, dict]:
    bindings = KeyBindings()
    state = {"expand": False}

    @bindings.add("c-o")
    def expand_output(event):
        state["expand"] = True
        event.app.exit()

    @bindings.add("enter")
    @bindings.add("c-c")
    def continue_without_expand(event):
        state["expand"] = False
        event.app.exit()

    return bindings, state
