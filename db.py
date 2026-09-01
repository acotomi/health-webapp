import sqlite3

from flask import current_app, g

# Povezava z bazo in vklop tujih ključev
def get_db():
    """Vrne povezavo z bazo za trenutno zahtevo; ustvari jo, če še ne obstaja."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    """Zapre povezavo z bazo ob koncu zahteve."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Ustvari tabele iz schema.sql. Obstoječe tabele s podatki izbriše in ustvari na novo."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def init_app(app):
    """Registrira funkcije iz tega modula pri aplikaciji."""
    app.teardown_appcontext(close_db)
