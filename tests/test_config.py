import os
from pathlib import Path

import pytest

from roastery import Config


def test_with_defaults_exit_behaviour() -> None:
    # Preserve the previous setting and restore it later.
    prev_val = os.environ.pop("PROJECT_ROOT")

    # Without `PROJECT_ROOT` or an explicit choice, the program should exit.
    with pytest.raises(SystemExit):
        Config.with_defaults()

    # with_defaults() shouldn't raise if a root is passed explicitly
    c = Config.with_defaults(project_root=Path("foo"))
    assert c.statements_dir == Path("foo/statements")

    # `with_defaults()` also shouldn't raise if all filesystem Path vars
    # are passed in explicitly while project root isn't set.
    d = Path("dummy")
    Config.with_defaults(
        statements_dir=d, journal_path=d, manual_edits_path=d, skip_path=d, flags_path=d
    )

    os.environ["PROJECT_ROOT"] = prev_val


def test_project_root_precedes_env_var() -> None:
    # Check the var was succesfully restored in the previous test.
    # (os.environ is global state unfortunately)
    assert "PROJECT_ROOT" in os.environ

    # Project root passed by the user takes precedence over env vars
    c = Config.with_defaults(project_root=Path("foo"))
    assert c.statements_dir == Path("foo/statements")


def test_defaults() -> None:
    d = Path("dummy")
    c = Config.with_defaults(project_root=d)

    assert c.statements_dir == d / "statements"
    assert c.journal_path == d / "journal/main.beancount"
    assert c.manual_edits_path == d / ".roastery/manual-edits.json"
    assert c.skip_path == d / ".roastery/skip.json"
    assert c.do_not_import_before is None
    assert c.default_account_name_suffix == "Unknown"


def test_specify_different_defaults() -> None:
    d = Path("dummy")
    c = Config.with_defaults(
        project_root=d,
        manual_edits_path=Path("edits.json"),
    )

    assert c.statements_dir == d / "statements"
    assert c.manual_edits_path == Path("edits.json")
