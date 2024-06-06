"""
Variables and settings for Roastery. Many functions in Roastery's Python API
take an instance of the :py:class:`roastery.config.Config`.

Environment variables
---------------------

.. envvar:: PROJECT_ROOT

   Path to a directory containing the root of your financial statements.
   Used as the base path for all other Paths in :py:func:`roastery.config.Config.defaults`.

API
---

.. autoclass:: Config
   :members:
"""

import dataclasses
import datetime
import os
import sys
from pathlib import Path


@dataclasses.dataclass
class Config:
    """
    Variables and settings for ``roastery``.

    Convenience constructor: :py:obj:`roastery.config.Config.defaults()`
    """

    statements_dir: Path
    """Directory of statements"""

    journal_path: Path
    """Location of the main journal."""

    manual_edits_path: Path
    """Filepath to store end user manual edits."""

    skip_path: Path
    """File containing digests of transactions to skip while editing. See :py:mod:`roastery.edit`."""

    flags_path: Path
    """File containing digests of transactions that have been flagged for later review."""

    default_account_name_suffix: str = "Unknown"
    """Income/Expenses account name suffix to use when no better one is available in
    :py:obj:`roastery.importer.Entry.as_transaction`

    ``"Expenses:Unknown"``
      When :py:obj:`roastery.importer.Entry.is_expense` returns ``True``.

    ``"Income:Unknown"``
      When :py:obj:`roastery.importer.Entry.is_income` returns ``True``.
     """

    do_not_import_before: datetime.date = None
    """Date before which to skip importing transactions.

    This is useful if you want to keep a your entire history of financial statements and
    gradually import / classify them."""

    @classmethod
    def defaults(cls, project_root: Path = None) -> "Config":
        """
        Create a :py:class:`Config` with default values.

        This is a convenience method that allows users to quickly instantiate a
        :class:`~roastery.config.Config` object. If you want to use different
        settings you can either mutate the return value of this method or
        instantiate :py:class:`Config` directly.

        The ``project_root`` parameter or ``PROJECT_ROOT`` environment variable
        is used as a base path for all filesystem related settings.

        :param project_root: Base path to use for all filesystem paths instead
          of the ``PROJECT_ROOT`` environment variable.
        :return: A new :class:`~roastery.config.Config` instance.
        :raises SystemExit: If the ``PROJECT_ROOT`` environment variable is not
          set and ``project_root`` is not provided.
        """
        try:
            if project_root is None:
                root = Path(os.environ["PROJECT_ROOT"])
            else:
                root = project_root
        except KeyError:
            print(
                "Please pass the `project_root` parameter or set the `PROJECT_ROOT` env "
                + "var to use `Config.defaults()`"
            )
            sys.exit(1)

        return cls(
            statements_dir=root / "statements",
            journal_path=root / "journal/main.beancount",
            manual_edits_path=root / ".roastery/manual-edits.json",
            skip_path=root / ".roastery/skip.json",
            flags_path=root / ".roastery/flags.json",
        )
