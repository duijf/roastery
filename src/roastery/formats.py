import datetime
import hashlib

from typing import TypedDict, NotRequired

from beancount.core.data import Amount
from beancount.core.number import D

from roastery.importer import Entry


DemoCsvRow = TypedDict(
    "DemoCsvRow",
    {
        "date": str,
        "payee": str,
        "description": str,
        "amount": str,
        "type": str,
        "balance_after": str,
    },
)


def extract_demo(row: DemoCsvRow) -> Entry:
    # TODO: Extract `Assets:Bank` and `EUR`
    return Entry.from_row(
        digest=hashlib.md5(str(row).encode("utf-8")).hexdigest(),
        asset_account="Assets:Bank",
        date=parse_date(row["date"]),
        amount=Amount(D(row["amount"]), "EUR"),
        original_payee=row["payee"],
        original_narration=row["description"],
        meta={"balance_after": row["balance_after"], "type": row["type"]},
    )


def parse_date(val: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(val)
    except ValueError:
        pass

    # This can also raise
    day, month, year = val.split("-")
    return datetime.date(int(year), int(month), int(day))
