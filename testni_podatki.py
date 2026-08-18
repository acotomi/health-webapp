"""Enkratna skripta: napolni bazo s testnimi podatki za razvoj.

Zahteva, da baza že obstaja (glej pripravi_bazo.py). Če jo poženeš dvakrat,
bo vstavljanje uporabnika spodletelo (uporabnisko_ime je UNIQUE) — to je
namerno, da po nesreči ne podvojiš podatkov. Za ponovno polnjenje najprej
izbriši instance/zdravje.db in znova poženi pripravi_bazo.py.
"""

from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from app import app
from db import get_db

with app.app_context():
    db = get_db()

    db.execute(
        "INSERT INTO uporabnik (uporabnisko_ime, geslo_zgostitev, ustvarjen) VALUES (?, ?, ?)",
        ("testni", generate_password_hash("geslo123"), date.today().isoformat()),
    )
    uporabnik_id = db.execute(
        "SELECT id FROM uporabnik WHERE uporabnisko_ime = ?", ("testni",)
    ).fetchone()["id"]

    simptom_id = {}
    for naziv in ("glavobol", "utrujenost"):
        cur = db.execute(
            "INSERT INTO simptom (uporabnik_id, naziv) VALUES (?, ?)",
            (uporabnik_id, naziv),
        )
        simptom_id[naziv] = cur.lastrowid

    jakosti = {
        "glavobol": [3, 4, 2, 0, 5, 6, 3, 2, 0, 0, 4, 5, 3, 2],
        "utrujenost": [5, 6, 5, 4, 7, 6, 5],
    }
    for naziv, vrednosti in jakosti.items():
        for i, jakost in enumerate(vrednosti):
            datum = (date.today() - timedelta(days=len(vrednosti) - i)).isoformat()
            db.execute(
                "INSERT INTO zapis_simptoma (simptom_id, datum, jakost, opomba) VALUES (?, ?, ?, ?)",
                (simptom_id[naziv], datum, jakost, None),
            )

    cur = db.execute(
        "INSERT INTO terapija (uporabnik_id, naziv, odmerek, pogostost, aktivna) VALUES (?, ?, ?, ?, ?)",
        (uporabnik_id, "Ibuprofen", "400 mg", "2-krat dnevno", 1),
    )
    terapija_id = cur.lastrowid

    db.execute(
        "INSERT INTO terapija (uporabnik_id, naziv, odmerek, pogostost, aktivna) VALUES (?, ?, ?, ?, ?)",
        (uporabnik_id, "Dihalne vaje", None, None, 1),
    )

    for i in range(5):
        datum = (date.today() - timedelta(days=i)).isoformat()
        db.execute(
            "INSERT INTO zapis_terapije (terapija_id, datum) VALUES (?, ?)",
            (terapija_id, datum),
        )

    db.commit()

print("Testni podatki so vstavljeni.")
