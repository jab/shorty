"""Shorty: A minimal link shortener."""

import asyncio
import os
import sqlite3

from flask import Blueprint
from flask import Flask
from flask import current_app as app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask.typing import ResponseReturnValue
import hypercorn.asyncio
import hypercorn.config


DEFAULT_CONFIG = {
    "SQLITE_DB_URI": "file:/tmp/shorty.db",
}


def init_db(dbcon: sqlite3.Connection) -> None:
    dbcon.execute("CREATE TABLE IF NOT EXISTS shortlink(key TEXT PRIMARY KEY, target TEXT)")


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


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping({k: os.getenv(k, v) for (k, v) in DEFAULT_CONFIG.items()})
    app.register_blueprint(bp)
    with app.app_context():
        init_db(dbcon())
    return app


@bp.route("/")
@bp.route("/<key>")
def redirect_or_render_create_form(key: str = "") -> ResponseReturnValue:
    if key and (target := target_for(key)):
        return redirect(target)
    return _render_create_page(key=key)


@bp.route("/", methods=["POST"])
def create() -> ResponseReturnValue:
    key = request.form.get("key", "")
    target = request.form.get("target", "")
    if not key or not target:
        flashmsg = "Error: Key or target missing for short link"
        return _render_create_page(flashmsg=flashmsg, key=key), 400
    try:
        insert(key, target)
    except sqlite3.IntegrityError:
        flashmsg = f"Error: Short link '{key}' already exists. Try another."
        return _render_create_page(flashmsg=flashmsg, target=target), 400
    else:
        msg = f"<p>Short link created: <a href='{target}'>{request.url_root}{key}</a></p>"
        msg += f"<p><a href='{request.url_root}'>home</a></p>"
        return f"<center>{msg}</center>", 201


def _render_create_page(flashmsg: str = "", key: str = "", target: str = "") -> str:
    # Flask provides the flask.flash(..) helper for setting flash messages using a session cookie
    # (so they can accumulate until displayed, survive redirects, etc.), but this is overkill:
    # We only ever display at most one flash message immediately when rendering our sole template.
    # So we use a simple template variable instead.
    return render_template("create.html.j2", flashmsg=flashmsg, key=key, target=target)


def main() -> None:
    DEFAULT_PORT = 8675
    app = create_app()
    if app.debug:  # True if the FLASK_DEBUG env var is set
        # In debug mode, use Flask's single-threaded dev server, which will have its
        # through-the-web debugger middleware enabled, instead of hypercorn.
        app.run(port=DEFAULT_PORT, use_reloader=False)  # prefer ibazel's reloader
        raise SystemExit
    config = hypercorn.config.Config()
    config.accesslog = "-"
    config.bind = [os.getenv("BIND", f":{DEFAULT_PORT}")]
    asyncio.run(hypercorn.asyncio.serve(app, config))


if __name__ == "__main__":  # pragma: no cover
    main()
