import json
import os
import sys

import typer
from rich.traceback import install as install_traceback_handler

from roastery.config import Config
from roastery.edit import main as edit_main

__all__ = [
    "make_cli",
]


def make_cli(config: Config) -> typer.Typer:
    install_traceback_handler(show_locals=True)
    cli = typer.Typer(no_args_is_help=True, add_completion=False)

    @cli.command(name="edit")
    def edit_cmd() -> None:
        edit_main(config)

    @cli.command(name="fava")
    def fava_cmd() -> None:
        typer.launch(
            "http://localhost:5000/",
        )
        os.execvp("fava", ["fava", config.journal_path])

    @cli.command(name="flag")
    def flag_cmd(digest: str) -> None:
        if len(digest) != 32:
            print("Digest should be a 32 character md5 hash")
            sys.exit(1)

        try:
            flags = set(json.loads(config.flags_path.read_text()))
        except Exception:
            flags = set()

        flags.add(digest)
        config.flags_path.parent.mkdir(exist_ok=True)
        config.flags_path.write_text(json.dumps(sorted(flags), indent=4) + "\n")

    return cli
