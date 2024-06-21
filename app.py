"""Shorty: A minimal link shortener."""

from __future__ import annotations

import os
import sqlite3

import flask
import werkzeug
from flask import Blueprint
from flask import Flask
from flask import current_app as app
from flask import g
from flask import redirect
from flask import render_template
from flask import request


DEFAULT_CONFIG = {
    "SQLITE_DB_URI": "file:/tmp/shorty.db",
}


def init_db(dbcon: sqlite3.Connection) -> None:
    dbcon.execute("CREATE TABLE IF NOT EXISTS shortlink(key TEXT PRIMARY KEY, target TEXT)")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping({k: os.getenv(k, v) for (k, v) in DEFAULT_CONFIG.items()})
    app.register_blueprint(bp)
    with app.app_context():
        init_db(dbcon())
    return app


def dbcon() -> sqlite3.Connection:
    if not (db := getattr(g, "_db", None)):
        db = g._db = sqlite3.connect(app.config["SQLITE_DB_URI"], uri=True, autocommit=True)
    return db


def target_for(key: str) -> str | None:
    query = ("SELECT target FROM shortlink WHERE key = ?", (key,))
    row = dbcon().execute(*query).fetchone()
    return row[0] if row else None


def insert(key: str, target: str) -> None:
    query = ("INSERT INTO shortlink VALUES (?, ?)", (key, target))
    dbcon().execute(*query)


bp = Blueprint("shorty", __name__)


Response = str | tuple[str, int] | flask.Response | werkzeug.Response


@bp.route("/")
@bp.route("/<key>")
def redirect_or_render_create_form(key: str = "") -> Response:
    if key:
        if target := target_for(key):
            return redirect(target)
    return _render_create_page(key=key)


@bp.route("/", methods=["POST"])
def create() -> Response:
    key = request.form.get("key", "")
    target = request.form.get("target", "")
    if not key or not target:
        flashmsg = "Error: Key or target missing for short link"
        return _render_create_page(flashmsg=flashmsg, key=key)
    try:
        insert(key, target)
    except sqlite3.IntegrityError:
        flashmsg = f"Error: Short link '{key}' already exists. Try another."
        return _render_create_page(flashmsg=flashmsg, target=target)
    else:
        msg = f"<p>Short link created: <a href='{target}'>{request.url_root}{key}</a></p>"
        msg += f"<p><a href='{request.url_root}'>Home</a></p>"
        return f"<center>{msg}</center>", 201


def _render_create_page(flashmsg: str = "", key: str = "", target: str = "") -> str:
    # Flask provides the flask.flash(..) helper for setting flash messages using a session cookie
    # (so they can accumulate until displayed, survive redirects, etc.), but this is overkill:
    # We only ever display at most one flash message immediately when rendering our sole template.
    # So we use a simple template variable instead.
    return render_template("create.html.jinja", flashmsg=flashmsg, key=key, target=target)


if __name__ == "__main__":
    DEFAULT_PORT = 8675
    app = create_app()
    try:
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
    except ImportError:
        app.run(port=DEFAULT_PORT)
    else:
        import asyncio

        config = Config()
        config.bind = [os.getenv("BIND", f":{DEFAULT_PORT}")]
        asyncio.run(serve(app, config))
