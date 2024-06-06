from pathlib import Path
from typing import Iterator

import pytest

from roastery import Config


@pytest.fixture()
def config(tmp_path: Path) -> Iterator[Config]:
    yield Config.with_defaults(project_root=tmp_path)
