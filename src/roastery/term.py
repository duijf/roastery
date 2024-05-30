"""
Utilities for logging and asking for user input.

Logging
-------

.. autofunction:: roastery.term.log
.. autofunction:: roastery.term.info
.. autofunction:: roastery.term.error
.. autofunction:: roastery.term.warn
.. autofunction:: roastery.term.hint
.. autofunction:: roastery.term.executing

User input
----------

.. autofunction:: roastery.term.ask
.. autofunction:: roastery.term.select_fuzzy_search
"""
import subprocess

from prompt_toolkit import prompt
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.output.color_depth import ColorDepth
from rich import print as rprint
from rich.text import Text

__all__ = [
    "log",
    "info",
    "error",
    "warn",
    "hint",
    "executing",
    "ask",
    "select_fuzzy_search",
]


def error(*contents: str):
    """Log the `contents` to the terminal as an error.

    :param contents: String containing the log message in Rich Markup."""
    log(*contents, header="error", style="red bold")


def warn(*contents: str):
    """Log the `contents` to the terminal as a warning.

    :param contents: String containing the log message in Rich Markup."""
    log(*contents, header="warning", style="yellow bold")


def hint(*contents: str):
    """Log the `contents` to the terminal as a hint.

    :param contents: String containing the log message in Rich Markup."""
    log(*contents, header="hint", style="blue bold")


def info(*contents: str):
    """Log the `contents` to the terminal in informational style.

    :param contents: String containing the log message in Rich Markup."""
    # We don't prefix these messages with `INFO`. That's a little noisy.
    log(*contents, style="bold")


def executing(command: list[str]):
    """Log that the program is executing a command

    :param command: The command that the program is executing. This is a list,
      to allow easy integration with `subprocess.run()`.
    """
    log(" ".join(command), header="executing", style="bold")


def log(*contents: str, style: str | None = None, header: str | None = None):
    """Log `contents` to the terminal in a given style.

    :param contents: String containing the log message in Rich Markup.
    :param style: Style to forward to `rich.Text`
    :param header: Header text to preface the log message with.
    """
    if header:
        rprint(Text(f"| {header}", style=style))

    for item in contents:
        rprint(Text.assemble(Text("| ", style=style), Text.from_markup(item)))
    print()


def ask(question: str, *, default: str = None) -> str:
    """Ask the user a `question`, returning their answer.

    Users will be able to enter their answer in a readline-style environment with
    vi-style keybindings.

    :param question: Question to prompt the user with.
    :param default: Default to pre-populate the readline env
    """
    display = FormattedText([("bold blue", f"| {question} > ",)])
    # The color depth is so that `blue` refers to the color scheme in
    # use by the terminal. This means we respect the theme that was set
    # by the user.
    res = prompt(display, editing_mode=EditingMode.VI, default=default,
                 color_depth=ColorDepth.ANSI_COLORS_ONLY)
    print()
    return res


def select_fuzzy_search(
    prompt: str,
    *,
    options: list[str],
) -> str:
    """Prompt the user to choose from a set of `options` using fuzzy search.

    Fuzzy search is implemented by `fzf`.

    :param prompt: Search prompt to set in `fzf`.
    :param options: List of options that the user can choose from.

    :raises KeyboardInterrupt: If the user did not confirm the selection.
    """
    fzf_input = "\n".join(options)
    fzf_cmd = ["fzf", "--height", "~30%", f"--prompt=| {prompt} > "]

    fzf_proc = subprocess.run(fzf_cmd, input=fzf_input, text=True, stdout=subprocess.PIPE)
    fzf_choice = fzf_proc.stdout.strip()

    if fzf_choice == "":
        error("User aborted selection")
        raise KeyboardInterrupt

    # Log the users choice in the same style as the FZF prompt.
    log(f"[bold blue]{prompt} >[/bold blue] [bold]{fzf_choice}[/bold]", style="bold blue")

    assert fzf_choice in options
    return fzf_choice
