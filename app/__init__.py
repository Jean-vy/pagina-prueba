"""Biblioteca TAIS: web Flask sencilla para probar secfix.

Cada archivo de `app/routes/` define un Blueprint llamado `bp` y se registra
solo. Así, el pull request de prueba únicamente agrega un archivo nuevo.
"""
import importlib
import os
import pathlib

from flask import Flask

from app.db import close_db, init_db

ROUTES_DIR = pathlib.Path(__file__).parent / "routes"


def create_app(db_path=None, upload_dir=None) -> Flask:
    app = Flask(__name__)
    base = os.environ.get("APP_DATA", "/tmp/biblioteca")
    app.config.update(
        DB_PATH=db_path or os.path.join(base, "biblioteca.db"),
        UPLOAD_DIR=upload_dir or os.path.join(base, "uploads"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )
    os.makedirs(os.path.dirname(app.config["DB_PATH"]), exist_ok=True)
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)
    init_db(app.config["DB_PATH"])
    app.teardown_appcontext(close_db)

    for path in sorted(ROUTES_DIR.glob("*.py")):
        if path.name != "__init__.py":
            app.register_blueprint(importlib.import_module(f"app.routes.{path.stem}").bp)
    return app
