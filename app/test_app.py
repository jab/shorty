import os
import tempfile
import typing as t
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.__main__ import create_app


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


def test_get_root(client: FlaskClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"form" in resp.data


def test_create_short_link(client: FlaskClient) -> None:
    resp = client.post("/", data={"key": "foo"})
    assert resp.status_code == 400
    assert b"target missing" in resp.data
    resp = client.post("/", data={"key": "foo", "target": "http://bar"})
    assert resp.status_code == 201
    assert b"Short link created" in resp.data
    resp = client.get("/foo")
    assert resp.status_code == 302
    assert resp.headers.get("location") == "http://bar"
    resp = client.post("/", data={"key": "foo", "target": "http://baz"})
    assert resp.status_code == 400
    assert b"already exists" in resp.data
