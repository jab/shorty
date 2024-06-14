# https://flask.palletsprojects.com/en/3.0.x/testing/

import importlib
import os
import sys
from unittest.mock import patch

import pytest


@pytest.fixture()
def app():
    with patch.dict(os.environ, {"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}):
        import app
        importlib.reload(app)
        app.app.config.update(TESTING=True)
        yield app.app
        with app.app.app_context():
            app.db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_get_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"form" in resp.data


def test_create_short_link(client):
    resp = client.post("/", data={"key": "foo", "target": "http://bar"})
    assert resp.status_code == 201
    assert b"Short link created" in resp.data
    resp = client.get("/foo")
    assert resp.status_code == 302
    assert resp.headers.get("location") == "http://bar"


if __name__ == "__main__":
    sys.exit(pytest.main(["--verbose", "--ignore=external", "-p", "no:cacheprovider", __file__]))
