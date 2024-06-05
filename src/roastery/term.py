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
    log(*contents, header="error", style="red bold")


def warn(*contents: str):
    log(*contents, header="warning", style="yellow bold")


def hint(*contents: str):
    log(*contents, header="hint", style="blue bold")


def info(*contents: str):
    # We don't prefix these messages with `INFO`. That's a little noisy.
    log(*contents, style="bold")


def executing(command: list[str]):
    log(" ".join(command), header="executing", style="bold")


def log(*contents: str, style: str | None = None, header: str | None = None):
    if header:
        rprint(Text(f"| {header}", style=style))

    for item in contents:
        rprint(Text.assemble(Text("| ", style=style), Text.from_markup(item)))
    print()


def ask(question: str, *, default: str = None) -> str:
    display = FormattedText(
        [
            (
                "bold blue",
                f"| {question} > ",
            )
        ]
    )
    # The color depth is so that `blue` refers to the color scheme in
    # use by the terminal. This means we respect the theme that was set
    # by the user.
    res = prompt(
        display,
        editing_mode=EditingMode.VI,
        default=default,
        color_depth=ColorDepth.ANSI_COLORS_ONLY,
    )
    print()
    return res


def select_fuzzy_search(
    prompt: str,
    *,
    options: list[str],
) -> str:
    fzf_input = "\n".join(options)
    fzf_cmd = ["fzf", "--height", "~30%", f"--prompt=| {prompt} > "]

    fzf_proc = subprocess.run(
        fzf_cmd, input=fzf_input, text=True, stdout=subprocess.PIPE
    )
    fzf_choice = fzf_proc.stdout.strip()

    if fzf_choice == "":
        error("User aborted selection")
        raise KeyboardInterrupt

    # Log the users choice in the same style as the FZF prompt.
    log(
        f"[bold blue]{prompt} >[/bold blue] [bold]{fzf_choice}[/bold]",
        style="bold blue",
    )

    assert fzf_choice in options
    return fzf_choice
