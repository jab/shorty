from flask.testing import FlaskClient


def test_get_root(client: FlaskClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"form" in resp.data
