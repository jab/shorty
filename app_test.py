# https://flask.palletsprojects.com/en/3.0.x/testing/

import os
import sys
import typing as t
from unittest.mock import patch

from flask import Flask
from flask.testing import FlaskClient
import pytest

from app import create_app


@pytest.fixture(scope="function")
def app() -> t.Generator[Flask, None, None]:
    with patch.dict(os.environ, {"SQLITE_DB_URI": "file:memory?mode=memory&cache=shared"}):
        app = create_app()
        app.config.update(TESTING=True)
        yield app


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_get_root(client: FlaskClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"form" in resp.data


def test_create_short_link(client: FlaskClient) -> None:
    resp = client.post("/", data={"key": "foo", "target": "http://bar"})
    assert resp.status_code == 201
    assert b"Short link created" in resp.data
    resp = client.get("/foo")
    assert resp.status_code == 302
    assert resp.headers.get("location") == "http://bar"
