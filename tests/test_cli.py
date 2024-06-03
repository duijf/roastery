import json
from pathlib import Path
from typing import Iterator

import pytest
from typer import Typer
from typer.testing import CliRunner
from roastery import make_cli, Config


runner = CliRunner()


def test_cli_initialisation(cli: Typer) -> None:
    assert {c.name for c in cli.registered_commands} == {"fava", "flag", "edit"}


def test_flag_cmd_invalid_hash(cli: Typer) -> None:
    res = runner.invoke(cli, ["flag", "foo"])
    assert res.exit_code == 1
    assert "Digest should be a 32 character md5 hash" in res.stdout


def test_flag_cmd_valid_hash(config: Config, cli: Typer) -> None:
    assert not config.flags_path.exists()
    hash = "31e42bdc9c1b2d7467ed6099b99baca7"
    res = runner.invoke(cli, ["flag", hash])
    assert res.exit_code == 0
    assert config.flags_path.exists()
    assert json.loads(config.flags_path.read_text()) == [hash]


def test_flag_cmd_update_in_place(config: Config, cli: Typer) -> None:
    config.flags_path.parent.mkdir(exist_ok=True)
    config.flags_path.write_text(json.dumps(["foo"]))

    hash = "31e42bdc9c1b2d7467ed6099b99baca7"
    res = runner.invoke(cli, ["flag", hash])
    assert res.exit_code == 0
    assert config.flags_path.exists()
    assert json.loads(config.flags_path.read_text()) == [hash, "foo"]


@pytest.fixture()
def config(tmp_path: Path) -> Iterator[Config]:
    yield Config.from_env(project_root=tmp_path)


@pytest.fixture()
def cli(config: Config) -> Iterator[Typer]:
    yield make_cli(config)
