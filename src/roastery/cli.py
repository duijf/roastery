"""
This module provides you with a common starter kit of commands that are useful in Beancount projects.

.. code-block:: python

   # cli.py
   from roastery import make_cli, Config

   config = Config.with_defaults()
   roastery_cli = make_cli(config)
   roastery_cli()

This will result in the following CLI:

.. code-block::

   $ ./cli.py

    Usage: ./cli.py [OPTIONS] COMMAND [ARGS]...

   ╭─ Options ───────────────────────────────────────────────────────────╮
   │ --help          Show this message and exit.                         │
   ╰─────────────────────────────────────────────────────────────────────╯
   ╭─ Commands ──────────────────────────────────────────────────────────╮
   │ edit     Edit transactions that haven't been classified yet.        │
   │ fava     Start fava, the beancount web UI.                          │
   │ flag     Flag an entry for later review, based on digest.           │
   ╰─────────────────────────────────────────────────────────────────────╯

Command reference
-----------------

.. todo:: Reference for the default commands

API
---

.. autofunction:: make_cli
"""

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
    """Create a roastery CLI application from the given config.

    This function returns a Typer instance. You can customize the the instance with
    your own commands. See :doc:`/getting-started/index` for more information.
    """
    install_traceback_handler(show_locals=True)
    cli = typer.Typer(no_args_is_help=True, add_completion=False)

    @cli.command(name="edit")
    def edit_cmd() -> None:
        """Edit transactions that haven't been classified yet."""
        edit_main(config)

    @cli.command(name="fava")
    def fava_cmd() -> None:
        """Start fava, the beancount web UI."""
        typer.launch(
            "http://localhost:5000/",
        )
        os.execvp("fava", ["fava", config.journal_path])

    @cli.command(name="flag")
    def flag_cmd(digest: str) -> None:
        """Flag an entry for later review, based on digest."""
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
