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
    def with_defaults(
        cls,
        *,
        project_root: Path = None,
        statements_dir: Path = None,
        journal_path: Path = None,
        manual_edits_path: Path = None,
        skip_path: Path = None,
        flags_path: Path = None,
        default_account_name_suffix: str = "Unknown",
        do_not_import_before: datetime.date = None,
    ) -> "Config":
        """
        Create a :py:class:`Config` with default values.

        This is a convenience method that allows users to quickly instantiate
        :class:`~roastery.config.Config`. You can override the default values
        by passing in different parameters.

        The ``project_root`` parameter or ``PROJECT_ROOT`` environment variable
        is used as a base path for all filesystem related settings.

        :param project_root: Base path to use for all filesystem paths. If not
          provided, the ``PROJECT_ROOT`` environment variable is used.
        :param statements_dir: See :py:obj:`Config.statements_dir`
        :param journal_path: See :py:obj:`Config.journal_path`
        :param manual_edits_path: See :py:obj:`Config.manual_edits_path`
        :param skip_path: See :py:obj:`Config.skip_path`
        :param flags_path: See :py:obj:`Config.flags_path`
        :param default_account_name_suffix: See :py:obj:`Config.default_account_name_suffix`
        :param do_not_import_before: See :py:obj:`Config.do_not_import_before`

        :return: A new :class:`~roastery.config.Config` instance.
        :raises SystemExit: If one of the filesystem paths cannot be inferred
          from the ``project_root`` parameter or the ``PROJECT_ROOT`` environment
          variable.
        """

        should_infer_from_env_var = any(
            [
                statements_dir is None,
                journal_path is None,
                manual_edits_path is None,
                skip_path is None,
                flags_path is None,
            ]
        )

        if project_root is None and should_infer_from_env_var:
            try:
                project_root = Path(os.environ["PROJECT_ROOT"])
            except KeyError:
                print(
                    "Please pass the `project_root` parameter or set the `PROJECT_ROOT` env "
                    + "var to use `Config.defaults()`"
                )
                sys.exit(1)

        return cls(
            statements_dir=statements_dir or (project_root / "statements"),
            journal_path=journal_path or (project_root / "journal/main.beancount"),
            manual_edits_path=manual_edits_path
            or (project_root / ".roastery/manual-edits.json"),
            skip_path=skip_path or (project_root / ".roastery/skip.json"),
            flags_path=flags_path or (project_root / ".roastery/flags.json"),
            default_account_name_suffix=default_account_name_suffix,
            do_not_import_before=do_not_import_before,
        )
