from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from rich.console import Console

from .keybindings import create_output_expansion_bindings

console = Console()


def show_condensed_output_with_expand(output: str, title: str, lines: list[str], total_lines: int, output_size_kb: float) -> bool:
    preview_lines = lines[:5] + [
        "",
        f"... ({total_lines - 10} lines hidden, {output_size_kb:.1f} KB total) ...",
        ""
    ] + lines[-5:]
    preview = '\n'.join(preview_lines)

    from rich.panel import Panel
    console.print(Panel(
        preview,
        title=f"{title} (condensed - {total_lines} lines)",
        border_style="green"
    ))

    console.print("\n[dim]Press [bold cyan]Ctrl+O[/bold cyan] to expand full output, [bold green]Enter[/bold green] to continue[/dim]")

    bindings, state = create_output_expansion_bindings()

    layout = Layout(Window(FormattedTextControl(text="")))
    app = Application(layout=layout, key_bindings=bindings, full_screen=False)

    app.run()

    return state["expand"]
