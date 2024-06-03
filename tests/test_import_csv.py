import datetime
from pathlib import Path
from typing import Iterator

import pytest
from beancount import loader
from beancount.query.query import run_query

from roastery import import_csv, Config, formats


def test_import_demo_csv(config: Config, demo_csv: Path) -> None:
    beancount_file = demo_csv.with_suffix(".beancount")
    import_csv(
        config=config,
        csv_file=demo_csv,
        extract=formats.extract_demo,
        csv_args=dict(delimiter=";"),
    )
    assert beancount_file.exists()
    entries, errors, options = loader.load_file(beancount_file)
    assert len(entries) == 3


def test_import_cutoff(config: Config, demo_csv: Path) -> None:
    config.do_not_import_before = datetime.date(2024, 5, 28)
    beancount_file = demo_csv.with_suffix(".beancount")
    import_csv(
        config=config,
        csv_file=demo_csv,
        extract=formats.extract_demo,
        csv_args=dict(delimiter=";"),
    )
    assert beancount_file.exists()
    entries, errors, options = loader.load_file(beancount_file)
    assert len(entries) == 2


def test_import_flags(config: Config, demo_csv: Path) -> None:
    config.flags_path.parent.mkdir(exist_ok=True)
    md5 = "08f11d07d99ede2c9cb385b77ba5d203"
    config.flags_path.write_text(f'["{md5}"]')
    beancount_file = demo_csv.with_suffix(".beancount")
    import_csv(
        config=config,
        csv_file=demo_csv,
        extract=formats.extract_demo,
        csv_args=dict(delimiter=";"),
    )
    print(beancount_file.read_text())
    entries, errors, options = loader.load_file(beancount_file)
    assert len(entries) == 3

    query = """
    select distinct(any_meta("digest")) where flag = "!"
    """
    res_type, res_rows = run_query(entries, options, query)
    assert len(res_rows) == 1
    assert res_rows[0][0] == md5


@pytest.fixture
def demo_csv(config: Config) -> Iterator[Path]:
    config.statements_dir.mkdir(exist_ok=True)
    csv_file = config.statements_dir / "test.csv"

    csv_file.write_text("""\
"date";"payee";"description";"amount";"type";"balance_after"
"2024-05-28";"Employer";"Salary May";"3500.00";"TSFR";"4743.12"
"2024-05-29";"Supermarket Inc.";"Card No: 1923; Transaction ID: 128938958283801";"-42.32";"CARD";"4700.80"
"2024-05-30";"Housing Inc.";"Rent June";"-1000.00";"SEPA";"3700.80"
""")

    yield csv_file
