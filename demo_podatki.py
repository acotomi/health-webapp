"""Demonstracijski uporabniki z izmišljenimi, a značilnimi kroničnimi stanji.

Namenjeno posnetkom zaslona (poglavje 4.4) — podatki niso pravi bolniški
podatki, samo verjetnostno oblikovani zaradi boljše ponazoritve grafa in
tabel. Zahteva, da baza že obstaja (glej pripravi_bazo.py). Če poženeš
dvakrat, spodleti pri podvojenem uporabniškem imenu (namerno).
"""

import random
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from app import app
from db import get_db

GESLO = "demo1234"


def ustvari_uporabnika(baza, uporabnisko_ime):
    baza.execute(
        "INSERT INTO uporabnik (uporabnisko_ime, geslo_zgostitev, ustvarjen) VALUES (?, ?, ?)",
        (uporabnisko_ime, generate_password_hash(GESLO), date.today().isoformat()),
    )
    return baza.execute(
        "SELECT id FROM uporabnik WHERE uporabnisko_ime = ?", (uporabnisko_ime,)
    ).fetchone()["id"]


def dodaj_simptom(baza, uporabnik_id, naziv):
    cur = baza.execute(
        "INSERT INTO simptom (uporabnik_id, naziv) VALUES (?, ?)", (uporabnik_id, naziv)
    )
    return cur.lastrowid


def dodaj_zapis_simptoma(baza, simptom_id, datum, jakost, opomba=None):
    baza.execute(
        "INSERT INTO zapis_simptoma (simptom_id, datum, jakost, opomba) VALUES (?, ?, ?, ?)",
        (simptom_id, datum, jakost, opomba),
    )


def dodaj_terapijo(baza, uporabnik_id, naziv, odmerek, pogostost):
    cur = baza.execute(
        "INSERT INTO terapija (uporabnik_id, naziv, odmerek, pogostost, aktivna) VALUES (?, ?, ?, ?, 1)",
        (uporabnik_id, naziv, odmerek, pogostost),
    )
    return cur.lastrowid


def dodaj_zapis_terapije(baza, terapija_id, datum):
    baza.execute(
        "INSERT INTO zapis_terapije (terapija_id, datum) VALUES (?, ?)", (terapija_id, datum)
    )


def zadnjih_n_dni(stevilo_dni):
    danes = date.today()
    return [(danes - timedelta(days=i)).isoformat() for i in range(stevilo_dni - 1, -1, -1)]


def ustvari_sladkorno_bolezen(baza):
    uporabnik_id = ustvari_uporabnika(baza, "demo1")
    utrujenost_id = dodaj_simptom(baza, uporabnik_id, "utrujenost")
    zeja_id = dodaj_simptom(baza, uporabnik_id, "žeja")
    omotica_id = dodaj_simptom(baza, uporabnik_id, "omotica")

    for datum in zadnjih_n_dni(45):
        slab_dan = random.random() < 0.2
        dodaj_zapis_simptoma(
            baza, utrujenost_id, datum, random.randint(5, 7) if slab_dan else random.randint(2, 4)
        )
        dodaj_zapis_simptoma(
            baza, zeja_id, datum, random.randint(5, 7) if slab_dan else random.randint(1, 3)
        )
        if random.random() < 0.15:
            dodaj_zapis_simptoma(baza, omotica_id, datum, random.randint(2, 5))

    metformin_id = dodaj_terapijo(baza, uporabnik_id, "Metformin", "500 mg", "2-krat dnevno")
    for datum in zadnjih_n_dni(20):
        dodaj_zapis_terapije(baza, metformin_id, datum)
        dodaj_zapis_terapije(baza, metformin_id, datum)

    dodaj_terapijo(baza, uporabnik_id, "Inzulin (hitro delujoč)", "10 enot", "pred obroki")


def ustvari_migreno(baza):
    uporabnik_id = ustvari_uporabnika(baza, "demo2")
    glavobol_id = dodaj_simptom(baza, uporabnik_id, "glavobol")
    slabost_id = dodaj_simptom(baza, uporabnik_id, "slabost")
    svetloba_id = dodaj_simptom(baza, uporabnik_id, "preobčutljivost na svetlobo")

    sumatriptan_id = dodaj_terapijo(baza, uporabnik_id, "Sumatriptan", "50 mg", "po potrebi")
    propranolol_id = dodaj_terapijo(baza, uporabnik_id, "Propranolol", "40 mg", "1-krat dnevno")

    preostali_dnevi_napada = 0
    for datum in zadnjih_n_dni(45):
        if preostali_dnevi_napada == 0 and random.random() < 0.12:
            preostali_dnevi_napada = random.choice([1, 2])

        if preostali_dnevi_napada > 0:
            dodaj_zapis_simptoma(baza, glavobol_id, datum, random.randint(7, 9), "hujši napad")
            dodaj_zapis_simptoma(baza, slabost_id, datum, random.randint(4, 6))
            dodaj_zapis_simptoma(baza, svetloba_id, datum, random.randint(5, 7))
            dodaj_zapis_terapije(baza, sumatriptan_id, datum)
            preostali_dnevi_napada -= 1
        else:
            dodaj_zapis_simptoma(baza, glavobol_id, datum, random.randint(0, 2))

        dodaj_zapis_terapije(baza, propranolol_id, datum)


def ustvari_revmatoidni_artritis(baza):
    uporabnik_id = ustvari_uporabnika(baza, "demo3")
    bolecine_id = dodaj_simptom(baza, uporabnik_id, "bolečine v sklepih")
    okorelost_id = dodaj_simptom(baza, uporabnik_id, "jutranja okorelost")
    utrujenost_id = dodaj_simptom(baza, uporabnik_id, "utrujenost")

    metotreksat_id = dodaj_terapijo(baza, uporabnik_id, "Metotreksat", "15 mg", "1-krat tedensko")
    ibuprofen_id = dodaj_terapijo(baza, uporabnik_id, "Ibuprofen", "400 mg", "po potrebi")

    for i, datum in enumerate(zadnjih_n_dni(45)):
        poslabsanje = random.random() < 0.15
        dodaj_zapis_simptoma(
            baza, bolecine_id, datum, random.randint(6, 8) if poslabsanje else random.randint(3, 5)
        )
        dodaj_zapis_simptoma(baza, okorelost_id, datum, random.randint(4, 6))
        dodaj_zapis_simptoma(baza, utrujenost_id, datum, random.randint(3, 6))

        if poslabsanje:
            dodaj_zapis_terapije(baza, ibuprofen_id, datum)
        if i % 7 == 0:
            dodaj_zapis_terapije(baza, metotreksat_id, datum)


with app.app_context():
    random.seed(42)
    baza = get_db()

    ustvari_sladkorno_bolezen(baza)
    ustvari_migreno(baza)
    ustvari_revmatoidni_artritis(baza)

    baza.commit()

print("Demonstracijski uporabniki ustvarjeni: demo1, demo2, demo3")
print(f"Geslo za vse: {GESLO}")
