"""Shorty: A minimal link shortener."""

from __future__ import annotations

import os

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func


class ModelBase(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=ModelBase)


class ShortLink(db.Model):
    key: Mapped[str] = mapped_column(primary_key=True)
    target: Mapped[str] = mapped_column()
    created_by: Mapped[str | None] = mapped_column()
    created_at: Mapped[int] = mapped_column(server_default=func.now())


DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URI":  "sqlite:////tmp/shorty.db",
}
app = Flask(__name__)
app.config.from_mapping({k: os.getenv(k, v) for (k, v) in DEFAULT_CONFIG.items()})

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/<key>")
def redirect_or_render_create_form(key: str = ""):
    if key:
        link = db.session.execute(db.select(ShortLink).filter_by(key=key)).scalar_one_or_none()
        if link:
            return redirect(link.target)
    return _render_create_page(key=key)


@app.route("/", methods=["POST"])
def create():
    key = request.form.get("key")
    target = request.form.get("target")
    if not key or not target:
        flashmsg = "Error: Key or target missing for short link"
        return _render_create_page(flashmsg=flashmsg, key=key)
    existing = db.session.execute(db.select(ShortLink).filter_by(key=key)).one_or_none()
    if existing:
        flashmsg = f"Error: Short link '{key}' already exists. Try another."
        return _render_create_page(flashmsg=flashmsg, target=target)
    try:
        short_link = ShortLink(key=key, target=target, created_by=request.remote_user)
        db.session.add(short_link)
        db.session.commit()
    except SQLAlchemyError as exc:
        flashmsg = f"Error creating short link: {exc}"
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
    # Enable running directly (without Bazel), in case the user wants to Bring Their Own Environment.
    app.run()
