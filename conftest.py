import os
import tempfile
import typing as t
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture()
def app() -> t.Generator[Flask, None, None]:
    with (
        tempfile.NamedTemporaryFile(suffix="shorty.db") as tmpfd,
        patch.dict(os.environ, {"SQLITE_DB_URI": f"file:{tmpfd.name}"}),
    ):
        app = create_app()
        app.config.update(TESTING=True)
        yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
