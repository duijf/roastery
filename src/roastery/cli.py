import os

import typer
from rich.traceback import install as install_traceback_handler

from roastery.config import Config
from roastery.edit import main as edit_main

__all__ = [
    "make_cli",
]


def make_cli(config: Config) -> typer.Typer:
    """Create a roastery CLI application from the given config."""
    install_traceback_handler(show_locals=True)
    cli = typer.Typer(no_args_is_help=True, add_completion=False)

    @cli.command(name="edit")
    def edit_cmd() -> None:
        """Edit transactions that haven't been classified yet."""
        edit_main(config)

    @cli.command(name="fava")
    def fava_cmd() -> None:
        """Start fava, the beancount web UI."""
        typer.launch("http://localhost:5000/", )
        os.execvp("fava", ["fava", config.journal_path])

    return cli
