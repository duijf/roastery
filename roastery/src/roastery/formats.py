import datetime
import hashlib

from typing import TypedDict, NotRequired

from beancount.core.data import Amount
from beancount.core.number import D

from roastery.importer import Entry


DemoCsvRow = TypedDict("DemoCsvRow", {
    "date": str,
    "payee": str,
    "description": str,
    "amount": str,
    "type": str,
    "balance_after": str,
})


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


# CSV columns of the
AsnCsvRow = TypedDict("AsnCsvRow", {
    "Boekingsdatum": str,
    "Opdrachtgeversrekening": str,
    "Tegenrekeningnummer": str,
    "Naam tegenrekening": str,
    # Begin: unused
    "Adres": str,
    "Postcode": str,
    "Plaats": str,
    # End: unused
    "Valutasoort rekening": str,
    "Saldo rekening voor mutatie": str,
    "Valutasoort mutatie": str,
    "Transactiebedrag": str,
    "Journaaldatum": str,
    "Valutadatum": str,
    "Interne transactiecode": str,
    "Globale transactiecode": str,
    "Volgnummer transactie": str,
    "Betalingskenmerk": str,
    "Omschrijving": str,
    "Afschriftnummer": str,
})


class AsnMeta(TypedDict):
    digest: str
    type: str
    tegenrekening: NotRequired[str]
    volgnummer: NotRequired[str]


def extract_asn(row: AsnCsvRow) -> Entry[AsnMeta]:
    amount = Amount(D(row["Transactiebedrag"]), "EUR")
    transaction_type = row["Globale transactiecode"]
    date = parse_date(row["Boekingsdatum"])

    original_narration = row["Omschrijving"]
    digest = hashlib.md5(row["Volgnummer transactie"].encode("utf-8")).hexdigest()

    meta = {"type": transaction_type, "digest": digest}

    if row["Tegenrekeningnummer"] != "":
        meta |= {"tegenrekening": row["Tegenrekeningnummer"]}

    if row["Volgnummer transactie"] != "":
        meta |= {"volgnummer": row["Volgnummer transactie"]}

    return Entry.from_row(
        digest=digest,
        date=date,
        amount=amount,
        meta=meta,
        # TODO: Generalise
        asset_account="Assets:ASN",
        original_payee=row["Naam tegenrekening"],
        original_narration=original_narration,
    )


def parse_date(val: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(val)
    except ValueError:
        pass

    # This can also raise
    day, month, year = val.split("-")
    return datetime.date(int(year), int(month), int(day))
