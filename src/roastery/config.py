"""
Variables and settings for Roastery. Many functions in Roastery's Python API
take an instance of the :py:class:`roastery.config.Config`.

Environment variables
---------------------

.. envvar:: PROJECT_ROOT

   Path to a directory containing the root of your financial statements.
   Used as the base path for all other Paths in :py:func:`roastery.config.Config.from_env`.

API
---

.. autoclass:: Config
   :members:
"""
import dataclasses
import os
import sys
from pathlib import Path


@dataclasses.dataclass
class Config:
    """
    Variables and settings for ``roastery``.

    Convenience constructor: :py:obj:`roastery.config.Config.from_env()`
    """

    statements_dir: Path
    """Directory of statements"""

    journal_path: Path
    """Location of the main journal."""

    manual_edits_path: Path
    """Filepath to store end user manual edits."""

    skip_path: Path
    """File containing digests of transactions to skip while editing . See :py:mod:`roastery.edit`."""

    default_account_name_suffix: str = "Unknown"
    """Income/Expenses account name suffix to use when no better one is available in
    :py:obj:`roastery.importer.Entry.as_transaction`

    ``"Expenses:Unknown"``
      When :py:obj:`roastery.importer.Entry.is_expense` returns ``True``.

    ``"Income:Unknown"``
      When :py:obj:`roastery.importer.Entry.is_income` returns ``True``.
     """

    @classmethod
    def from_env(cls, project_root: Path = None) -> 'Config':
        """
        Create a :py:class:`Config` based on the `Environment variables`_ that are set.

        This is a convenience method. If you want different defaults you can instantiate
        this class yourself.
        """
        try:
            if project_root is None:
                root = Path(os.environ["PROJECT_ROOT"])
            else:
                root = project_root
        except KeyError:
            print("Please set the `PROJECT_ROOT` env var to use `Config.from_env()`.")
            sys.exit(1)

        return cls(
            statements_dir=root / "statements",
            journal_path=root / "journal/main.beancount",
            manual_edits_path=root / "data/manual-edits.json",
            skip_path=root / "data/skip.json",
        )
