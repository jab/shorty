import os

from absl.testing import absltest
from unittest.mock import patch


class AppTest(absltest.TestCase):
    def setUp(self):
        self.environ_patch = patch.dict(os.environ, {"SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.environ_patch.__enter__()
        from app import app
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def tearDown(self):
        self.environ_patch.__exit__()
        from app import app, db
        with app.app_context():
            db.drop_all()

    def test_get_root(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"form", resp.data)

    def test_create_short_link(self):
        resp = self.client.post("/", data={"key": "foo", "target": "bar"})
        self.assertEqual(resp.status_code, 201)
        self.assertIn(b"Short link created", resp.data)
        resp = self.client.get("/foo")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("location"), "bar")


if __name__ == "__main__":
    absltest.main()
