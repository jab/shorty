import asyncio
import os

from flask import Blueprint
from flask import Flask

import hypercorn.asyncio
import hypercorn.config


DEFAULT_CONFIG = {}


bp = Blueprint("shorty", __name__)


@bp.route("/")
def home():
    return "it works"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping({k: os.getenv(k, v) for (k, v) in DEFAULT_CONFIG.items()})
    app.register_blueprint(bp)
    return app


def main() -> None:
    DEFAULT_PORT = 8675
    app = create_app()
    config = hypercorn.config.Config()
    config.bind = [os.getenv("BIND", f":{DEFAULT_PORT}")]
    asyncio.run(hypercorn.asyncio.serve(app, config))


if __name__ == "__main__":  # pragma: no cover
    main()
