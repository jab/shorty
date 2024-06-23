from flask.testing import FlaskClient


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
