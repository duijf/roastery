from __future__ import annotations

import csv
import dataclasses
import datetime
import json
from pathlib import Path
from typing import TypeVar, Callable, Generic, TypeAlias

from beancount.core import data
from beancount.parser import printer

from roastery.config import Config
from roastery.edit import ManualEdits

__all__ = [
    "import_csv",
    "CleanFn",
    "ExtractFn",
    "Entry",
    "EntryMeta",
    "Digest",
    "Cleanable",
]


@dataclasses.dataclass
class Cleanable:
    """
    A string field which can store three variants: the original value, the automatically cleaned value,
    and the value manually edited by the end user.

    The value property will return the first non-None value among the edited, cleaned, and original values.

    Examples:

        >>> Cleanable(original="foo").value
        'foo'

        >>> Cleanable(original="foo", cleaned="bar").value
        'bar'

        >>> Cleanable(original="foo", cleaned="bar", edited="baz").value
        'baz'
    """
    original: str | None = None
    cleaned: str | None = None
    edited: str | None = None

    @property
    def value(self) -> str:
        """The first not-None value :py:attr:`~edited`, :py:attr:`~cleaned`, and :py:attr:`~original`"""
        vals = (self.edited, self.cleaned, self.original)
        return next(arg for arg in vals if arg is not None)


Digest: TypeAlias = str
"""Hash digest of an :class:`Entry`, as a string."""

EntryMeta: TypeAlias = TypeVar("EntryMeta", bound=dict)
"""Type annotation for the metadata dictionary in Entry. 

Import formats can define their own institution specific metadata type if they want
users to be able to benefit from autocomplete, and things like that."""


@dataclasses.dataclass
class Entry(Generic[EntryMeta]):
    """
    :py:class:`Entry` represents a row of transaction data from a financial institution.

    Entries are constructed during the import process. For example by
    :py:func:`roastery.importer.import_csv`.

    Entry does not aim to abstract all of beancount's features. For example,
    :py:obj:`~Entry.as_transaction` always generates two postings. That makes this
    abstraction well-suited for transactions from bank accounts or credit cards. It
    is less applicable to model transactions involving investments or salary.
    """

    digest: Digest
    """
    Computed digest of this entry.
    
    Some banks / data sources do not provide a reliable number / ID for
    a given entry (in e.g. a CSV file). Therefore, implementors of this class
    will have to provide a way to compute a digest.
   
    This digest is used when storing the user's manual edits. See also 
    :py:mod:`roastery.edit`.
    """

    date: datetime.date
    """Booking date of the entry."""

    amount: data.Amount
    """Amount of the entry."""

    account: Cleanable
    """Account name to associate this transaction with. For example: ``Expenses:Pub``."""

    asset_account: str
    """Asset account to associate this transaction with. For example: ``Assets:Checking``"""

    payee: Cleanable
    """Payee to add to this transaction. For example: ``Rob de Wit``."""

    narration: Cleanable
    """Narration to add to this transaction. For example: `Settle the tab at 't Neutje.`"""

    meta: EntryMeta = dataclasses.field(default_factory=dict)
    """
    Dictionary of arbitrary data to attach to the transaction. 
    
    Users can instantiate Entry with a :py:obj:`TypedDict` to get type safety for any extra
    fields they might want to store.
    """

    tags: set[str] = dataclasses.field(default_factory=set)
    """
    Set of arbitrary strings to tag this transaction with.
    
    See https://beancount.github.io/docs/beancount_language_syntax.html#tags
    """

    links: set[str] = dataclasses.field(default_factory=set)
    """
    Set of arbitrary strings to link this transaction with.
    
    See https://beancount.github.io/docs/beancount_language_syntax.html#tags
    """

    flag: str = "*"
    """
    One of the strings ``*`` or ``!``.
   
    ``*`` 
      denotes a 'normal' transaction. 
      
    ``!`` 
      means there is something special / that requires attention about this entry. ``!`` transactions 
      are highlighted in red in Fava.
    """

    @classmethod
    def from_row(
        cls,
        *,
        digest: str,
        date: datetime.date,
        amount: data.Amount,
        asset_account: str,
        meta: EntryMeta | None = None,
        original_payee: str | None = None,
        original_narration: str | None = None
    ) -> 'Entry':
        """Convenience constructor that can be called by integrators of a new source data type."""
        return cls(
            digest=digest,
            date=date,
            amount=amount,
            meta=meta or {},
            asset_account=asset_account,
            account=Cleanable(),
            payee=Cleanable(original=original_payee),
            narration=Cleanable(original=original_narration),
        )

    @property
    def is_income(self) -> bool:
        """Does this entry represent income?"""
        return self.amount.number > 0

    @property
    def is_expense(self) -> bool:
        """Does this entry represent an expense?"""
        return not self.is_income

    def as_transaction(self) -> data.Transaction:
        """Turn this entry into a beancount ``Transaction``."""
        def _p(account, amount=None):
            return data.Posting(account=account, units=amount, cost=None, price=None, flag=None, meta={})

        self.account.original = "Income:Unknown" if self.is_income else "Expenses:Unknown"

        postings = [
            _p(self.asset_account, self.amount),
            _p(self.account.value),  # beancount will infer the inverse amount automatically.
        ]

        return data.Transaction(
            date=self.date,
            postings=postings,
            payee=self.payee.value,
            narration=self.narration.value,
            meta={k: str(v) for k, v in self.meta.items()},
            tags=self.tags,
            links=self.links,
            flag=self.flag,
        )

    def apply_manual_edits(self, edits: dict[Digest, ManualEdits]):
        """Apply a user's manual edits to this entry."""
        if o := edits.get(self.digest):
            self.payee.edited = o.get("payee")
            self.account.edited = o.get("account")
            self.narration.edited = o.get("narration")
            self.tags = set(o.get("tags", []))
            self.links = set(o.get("links", []))


CleanFn: TypeAlias = Callable[[Entry], None]
"""Receives a :py:class:`Entry` and can mutate it as desired to classify / clean up the transaction.

For example:

.. code-block:: python

   def my_clean(entry: Entry) -> None:
       payee = entry.payee.lower()
      
       if payee == "irs":
           entry.account.cleaned = "Expenses:Tax"
           
       elif payee in {"chipotle", "mcdonalds", "five guys"}:
           entry.account.cleaned = "Expenses:FastFood"
"""


ExtractFn: TypeAlias = Callable[[dict], Entry]
"""Turns a row of CSV data into an :py:class:`Entry`."""


def import_csv(
    *,
    csv_file: Path,
    config: Config,
    extract: ExtractFn,
    beancount_file: Path = None,
    clean: CleanFn = None,
    csv_args: dict[str, any] = None
) -> None:
    """
    Import a CSV file and write a beancount file.

    For each row of the CSV file:

    - Create an :class:`Entry` using the ``extract`` function.
    - Apply manual edits from :obj:`roastery.config.Config.manual_edits_path`.
    - Clean the entry using the ``clean`` function, if provided.
    - Write the entry to disk as a Beancount transaction.

    The resulting Beancount file is created in the same directory as the CSV file, but with
    the extension changed to ``.beancount``. So: ``statements/foo.csv`` -> ``statements/foo.beancount``
    You can specify a different path with the ``beancount_file`` parameter.

    :param csv_file: Path of the CSV file to import.
    :param config: Configuration to use.
    :param csv_args: Arguments to forward to :py:class:`csv.DictReader`.
    :param extract: How to extract an :class:`Entry` from a row of CSV data. See :py:class:`~ExtractFn`.
    :param clean: User-implemented cleaning function. See :py:class:`~CleanFn`.
    :param beancount_file: Path of the beancount file to write to.
    """
    beancount_file = csv_file.with_suffix(".beancount") if beancount_file is None else beancount_file
    try:
        manual_edits = json.loads(config.manual_edits_path.read_text())
    except FileNotFoundError:
        manual_edits = {}

    _csv_args = {} if csv_args is None else csv_args
    _clean = (lambda x: None) if clean is None else clean

    with csv_file.open() as f_csv, beancount_file.open(mode="w", encoding="utf-8") as f_journal:
        reader = csv.DictReader(f_csv, **_csv_args)
        for row in reader:
            entry = extract(row)
            entry.apply_manual_edits(manual_edits)
            _clean(entry)
            printer.print_entry(entry.as_transaction(), file=f_journal)
