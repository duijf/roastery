import dataclasses
import datetime
import os
import sys
from pathlib import Path


@dataclasses.dataclass
class Config:
    statements_dir: Path
    journal_path: Path
    manual_edits_path: Path
    skip_path: Path
    flags_path: Path

    default_account_name_suffix: str = "Unknown"

    do_not_import_before: datetime.date = None

    @classmethod
    def from_env(cls, project_root: Path = None) -> "Config":
        try:
            if project_root is None:
                root = Path(os.environ["PROJECT_ROOT"])
            else:
                root = project_root
        except KeyError:
            print("Please set the `PROJECT_ROOT` env var to use `Config.from_env()`.")
            sys.exit(1)

        return cls(
            statements_dir=root / "statements",
            journal_path=root / "journal/main.beancount",
            manual_edits_path=root / ".roastery/manual-edits.json",
            skip_path=root / ".roastery/skip.json",
            flags_path=root / ".roastery/flags.json",
        )
