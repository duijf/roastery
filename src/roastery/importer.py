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
    original: str | None = None
    cleaned: str | None = None
    edited: str | None = None

    @property
    def value(self) -> str | None:
        vals = (self.edited, self.cleaned, self.original)
        return next((arg for arg in vals if arg is not None), None)


Digest: TypeAlias = str

EntryMeta: TypeAlias = TypeVar("EntryMeta", bound=dict)


@dataclasses.dataclass
class Entry(Generic[EntryMeta]):
    digest: Digest

    date: datetime.date

    amount: data.Amount

    account: Cleanable

    asset_account: str

    payee: Cleanable

    narration: Cleanable

    meta: EntryMeta = dataclasses.field(default_factory=dict)

    tags: set[str] = dataclasses.field(default_factory=set)

    links: set[str] = dataclasses.field(default_factory=set)

    flag: str = "*"

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
        original_narration: str | None = None,
    ) -> "Entry":
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
        return self.amount.number > 0

    @property
    def is_expense(self) -> bool:
        return not self.is_income

    def as_transaction(self) -> data.Transaction:
        def _p(account, amount=None):
            return data.Posting(
                account=account, units=amount, cost=None, price=None, flag=None, meta={}
            )

        self.account.original = (
            "Income:Unknown" if self.is_income else "Expenses:Unknown"
        )

        postings = [
            _p(self.asset_account, self.amount),
            _p(
                self.account.value
            ),  # beancount will infer the inverse amount automatically.
        ]

        meta = {k: str(v) for k, v in self.meta.items()}
        meta |= {"digest": self.digest}

        return data.Transaction(
            date=self.date,
            postings=postings,
            payee=self.payee.value,
            narration=self.narration.value,
            meta=meta,
            tags=self.tags,
            links=self.links,
            flag=self.flag,
        )

    def apply_manual_edits(self, edits: dict[Digest, ManualEdits]) -> None:
        if o := edits.get(self.digest):
            self.payee.edited = o.get("payee")
            self.account.edited = o.get("account")
            self.narration.edited = o.get("narration")
            self.tags = set(o.get("tags", []))
            self.links = set(o.get("links", []))


CleanFn: TypeAlias = Callable[[Entry], None]


ExtractFn: TypeAlias = Callable[[dict], Entry]


def import_csv(
    *,
    csv_file: Path,
    config: Config,
    extract: ExtractFn,
    beancount_file: Path = None,
    clean: CleanFn = None,
    csv_args: dict[str, any] = None,
) -> None:
    beancount_file = (
        csv_file.with_suffix(".beancount") if beancount_file is None else beancount_file
    )
    try:
        manual_edits = json.loads(config.manual_edits_path.read_text())
    except FileNotFoundError:
        manual_edits = {}

    try:
        flags = json.loads(config.flags_path.read_text())
    except FileNotFoundError:
        flags = {}

    _csv_args = {} if csv_args is None else csv_args
    _clean = (lambda x: None) if clean is None else clean

    with csv_file.open() as f_csv, beancount_file.open(
        mode="w", encoding="utf-8"
    ) as f_journal:
        reader = csv.DictReader(f_csv, **_csv_args)
        for row in reader:
            entry = extract(row)

            if entry.digest in flags:
                entry.flag = "!"

            if (config.do_not_import_before is not None) and (
                entry.date <= config.do_not_import_before
            ):
                continue

            entry.apply_manual_edits(manual_edits)
            _clean(entry)
            printer.print_entry(entry.as_transaction(), file=f_journal)
