from collections.abc import Generator

import pytest

from jlatrading.database.db import Db
from jlatrading.database.duck_db import DuckDb


@pytest.fixture
def db() -> Generator[Db, None, None]:
    db = DuckDb(None)
    db.connect()

    yield db

    if db.is_connected():
        db.disconnect()
