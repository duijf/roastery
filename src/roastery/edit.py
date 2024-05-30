"""
Find all unclassified / unprocessed transactions and prompt the user to classify
and edit them.

This is one of the nice tools that Roastery has on offer and is what allows you to
easily and quickly edit large amounts of transaction data. Any edits made by the
end user are saved in a JSON file that can be version controlled with git.
"""
import datetime
import json
import typing
from collections import defaultdict

from beancount import loader
from beancount.core import data
from beancount.core.number import D
from beancount.core.position import Position
from beancount.query.query import run_query

from roastery import term
from roastery.config import Config


__all__ = [
    "main",
    "ManualEdits",
]


class ManualEdits(typing.TypedDict):
    """
    Manually edits applied to an :py:class:`roastery.importer.Entry` by a user.

    User-overridden data is stored in a JSON file that is indexed by the
    :py:obj:`roastery.importer.Entry.digest`. Roastery loads these manual edits from
    :py:obj:`roastery.config.Config.manual_edits_path`.
    """

    payee: str
    account: str
    narration: str
    tags: list[str]
    links: list[str]


class Unprocessed(typing.Protocol):
    """Utility type representing an unprocessed entry."""
    date: datetime.date
    position: Position
    payee: str
    narration: str
    digest: str
    type: str


def display(item) -> None:
    amount = item.position.units.number
    currency = item.position.units.currency

    if item.position.units <= data.Amount(D("0"), "EUR"):
        color = "green"
        amount = amount * -1
    else:
        color = "red"

    message = f"[bold blue]{item.date}[/bold blue] {item.payee} [bold {color}]{amount} {currency}[/bold {color}]"
    to_log = [message, item.narration] if item.narration else [message]
    term.log(*to_log, style="bold blue")


def get_unprocessed(entries, options) -> list[Unprocessed]:
    query = """
        select
            date,
            position,
            payee,
            narration,
            any_meta("digest") as digest,
            any_meta("type") as type
        where account ~ "Unknown"
    """
    res_type, res_rows = run_query(entries, options, query)
    return res_rows


def main(config: Config) -> None:
    """
    Find all unclassified transactions and prompt the user to assign them to a category.

    This function depends on FZF to provide the interactive prompt that allows the user to
    select their preferred category. This function assumes that ``fzf`` is installed and
    available on ``PATH``.

    :param config: The configuration to use to find files on disk.
    """
    entries, errors, options = loader.load_file(config.journal_path)

    accounts = {entry.account for entry in entries if isinstance(entry, data.Open)}
    accounts = [
        account for account in accounts
        if "Assets:Bank" not in account
            and "Equity:Opening-Balances" not in account
    ]

    to_save = defaultdict(dict)
    to_skip = set(json.loads(config.skip_path.read_text()))

    try:
        for item in get_unprocessed(entries, options):
            if item.digest in to_skip:
                continue

            display(item)
            account_or_skip = term.select_fuzzy_search("Select account", options=accounts + ["Skip"])

            if account_or_skip == "Skip":
                to_skip.add(item.digest)
            else:
                payee_pretty = item.payee.title() if item.payee.isupper() else item.payee
                item_edits = {
                    "account": account_or_skip,
                    "payee": term.ask("Payee", default=payee_pretty),
                    "narration": term.ask("Narration", default=item.narration),
                }
                to_save[item.digest] = item_edits
    except KeyboardInterrupt:
        pass

    try:
        prev = json.loads(config.manual_edits_path.read_text())
    except (ValueError, FileNotFoundError):
        prev = {}

    config.manual_edits_path.write_text(json.dumps(prev | to_save, indent=4) + "\n")
    config.skip_path.write_text(json.dumps(sorted(to_skip), indent=4) + "\n")
