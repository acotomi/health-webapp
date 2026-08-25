import os
import secrets
import sqlite3
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash

import db

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "zdravje.db")
app.config["SECRET_KEY"] = "razvojni-skrivni-kljuc-samo-za-lokalni-prototip"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
os.makedirs(app.instance_path, exist_ok=True)
db.init_app(app)


def oblikuj_datum_sl(datum_iso):
    """Datum iz oblike YYYY-MM-DD v slovensko obliko, npr. '19. 8. 2026'."""
    d = datetime.strptime(datum_iso, "%Y-%m-%d").date()
    return f"{d.day}. {d.month}. {d.year}"


app.jinja_env.filters["datum_sl"] = oblikuj_datum_sl


def oblikuj_casovno_znacko_sl(casovna_znacka):
    """Datum in ura iz oblike 'YYYY-MM-DD HH:MM' v slovensko obliko,
    npr. '19. 8. 2026 ob 14:30'."""
    t = datetime.strptime(casovna_znacka, "%Y-%m-%d %H:%M")
    return f"{t.day}. {t.month}. {t.year} ob {t.strftime('%H:%M')}"


app.jinja_env.filters["casovna_znacka_sl"] = oblikuj_casovno_znacko_sl


def pridobi_csrf_zeton():
    """Vrne CSRF žeton trenutne seje; ob prvem klicu ga ustvari."""
    if "csrf_zeton" not in session:
        session["csrf_zeton"] = secrets.token_hex(32)
    return session["csrf_zeton"]


app.jinja_env.globals["csrf_zeton"] = pridobi_csrf_zeton

PRIMER_VELJAVNEGA_GESLA = "Geslo123!"


def geslo_ustreza_zahtevam(geslo):
    """Vsaj 8 znakov, vsaj ena velika črka in vsaj en poseben znak."""
    if len(geslo) < 8:
        return False
    if not any(znak.isupper() for znak in geslo):
        return False
    if not any(not znak.isalnum() for znak in geslo):
        return False
    return True


@app.before_request
def preveri_csrf_zeton():
    """Vsaka POST zahteva mora prinesti isti žeton, ki je bil izdan tej seji.
    Prepreči, da bi tuja stran v imenu prijavljenega uporabnika sprožila
    akcijo (npr. izbris zapisa) prek skritega obrazca (CSRF)."""
    if request.method == "POST":
        poslani_zeton = request.form.get("csrf_zeton", "")
        pravi_zeton = session.get("csrf_zeton", "")
        if not poslani_zeton or not secrets.compare_digest(poslani_zeton, pravi_zeton):
            abort(400)


@app.before_request
def nalozi_prijavljenega_uporabnika():
    uporabnik_id = session.get("uporabnik_id")
    if uporabnik_id is None:
        g.uporabnik = None
    else:
        g.uporabnik = db.get_db().execute(
            "SELECT id, uporabnisko_ime FROM uporabnik WHERE id = ?", (uporabnik_id,)
        ).fetchone()


def stevilo_zapisov_besedilo(stevilo):
    """Slovnično pravilna oblika '<število> shranjen(a/e/ih) zapis(a/e/ov)'."""
    if stevilo == 1:
        return "1 shranjen zapis"
    if stevilo == 2:
        return "2 shranjena zapisa"
    if stevilo in (3, 4):
        return f"{stevilo} shranjene zapise"
    return f"{stevilo} shranjenih zapisov"


def stevilka_zapisov(stevilo):
    """Slovnično pravilna oblika '<število> zapis(a/e/ov)', brez pridevnika."""
    if stevilo == 1:
        return f"{stevilo} zapis"
    if stevilo == 2:
        return f"{stevilo} zapisa"
    if stevilo in (3, 4):
        return f"{stevilo} zapise"
    return f"{stevilo} zapisov"


def prijava_zahtevana(pogled):
    @wraps(pogled)
    def ovita_funkcija(*args, **kwargs):
        if g.uporabnik is None:
            return redirect(url_for("prijava"))
        return pogled(*args, **kwargs)

    return ovita_funkcija


@app.route("/")
@prijava_zahtevana
def domov():
    baza = db.get_db()
    danes = date.today()

    zacetek = danes - timedelta(days=29)
    seznam_datumov = [(zacetek + timedelta(days=i)).isoformat() for i in range(30)]

    vrstice = baza.execute(
        """
        SELECT s.naziv AS simptom_naziv, z.datum, z.jakost
        FROM zapis_simptoma z
        JOIN simptom s ON z.simptom_id = s.id
        WHERE s.uporabnik_id = ? AND z.datum >= ?
        ORDER BY s.naziv, z.datum
        """,
        (g.uporabnik["id"], zacetek.isoformat()),
    ).fetchall()

    jakosti_po_simptomu = {}
    for vrstica in vrstice:
        jakosti_po_simptomu.setdefault(vrstica["simptom_naziv"], {})[vrstica["datum"]] = vrstica["jakost"]

    nizi = [
        {
            "naziv": naziv,
            "vrednosti": [vrednosti_po_datumu.get(datum) for datum in seznam_datumov],
        }
        for naziv, vrednosti_po_datumu in jakosti_po_simptomu.items()
    ]

    podatki_grafa = {"datumi": seznam_datumov, "nizi": nizi}

    aktivne_terapije = baza.execute(
        "SELECT id, naziv, odmerek, pogostost FROM terapija WHERE uporabnik_id = ? AND aktivna = 1 ORDER BY naziv",
        (g.uporabnik["id"],),
    ).fetchall()

    danasnje_terapije = []
    for terapija in aktivne_terapije:
        ure_danes = [
            vrstica["casovna_znacka"][11:16]
            for vrstica in baza.execute(
                """
                SELECT casovna_znacka FROM zapis_terapije
                WHERE terapija_id = ? AND substr(casovna_znacka, 1, 10) = ?
                ORDER BY casovna_znacka
                """,
                (terapija["id"], danes.isoformat()),
            ).fetchall()
        ]
        danasnje_terapije.append(
            {
                "id": terapija["id"],
                "naziv": terapija["naziv"],
                "odmerek": terapija["odmerek"],
                "pogostost": terapija["pogostost"],
                "ure_danes": ure_danes,
            }
        )

    return render_template("domov.html", podatki_grafa=podatki_grafa, terapije=danasnje_terapije)


@app.route("/prijava", methods=("GET", "POST"))
def prijava():
    if request.method == "POST":
        uporabnisko_ime = request.form["uporabnisko_ime"].strip()
        geslo = request.form["geslo"]

        baza = db.get_db()
        uporabnik = baza.execute(
            "SELECT * FROM uporabnik WHERE uporabnisko_ime = ?", (uporabnisko_ime,)
        ).fetchone()

        napaka = None
        if uporabnik is None or not check_password_hash(uporabnik["geslo_zgostitev"], geslo):
            napaka = "Napačno uporabniško ime ali geslo."

        if napaka is None:
            session.clear()
            session["uporabnik_id"] = uporabnik["id"]
            return redirect(url_for("domov"))

        flash(napaka, "napaka")

    return render_template("prijava.html")


@app.route("/odjava", methods=("POST",))
def odjava():
    session.clear()
    return redirect(url_for("prijava"))


@app.route("/registracija", methods=("GET", "POST"))
def registracija():
    if request.method == "POST":
        uporabnisko_ime = request.form["uporabnisko_ime"].strip()
        geslo = request.form["geslo"]
        potrdi_geslo = request.form["potrdi_geslo"]

        napaka = None
        if not uporabnisko_ime:
            napaka = "Uporabniško ime je obvezno."
        elif not geslo_ustreza_zahtevam(geslo):
            napaka = (
                "Geslo mora imeti vsaj 8 znakov, eno veliko črko in en poseben "
                f"znak (npr. {PRIMER_VELJAVNEGA_GESLA})."
            )
        elif geslo != potrdi_geslo:
            napaka = "Gesli se ne ujemata."

        if napaka is None:
            baza = db.get_db()
            try:
                baza.execute(
                    "INSERT INTO uporabnik (uporabnisko_ime, geslo_zgostitev, ustvarjen) VALUES (?, ?, ?)",
                    (uporabnisko_ime, generate_password_hash(geslo), datetime.now().isoformat()),
                )
                baza.commit()
            except sqlite3.IntegrityError:
                napaka = f"Uporabniško ime '{uporabnisko_ime}' je že zasedeno."
            else:
                flash("Račun je bil uspešno ustvarjen. Zdaj se lahko prijavite.", "uspeh")
                return redirect(url_for("prijava"))

        flash(napaka, "napaka")

    return render_template("registracija.html")


@app.route("/simptomi", methods=("GET", "POST"))
@prijava_zahtevana
def simptomi():
    baza = db.get_db()

    if request.method == "POST":
        naziv = request.form["naziv"].strip()

        if not naziv:
            flash("Naziv simptoma je obvezen.", "napaka")
        elif baza.execute(
            "SELECT id FROM simptom WHERE uporabnik_id = ? AND naziv = ?",
            (g.uporabnik["id"], naziv),
        ).fetchone():
            flash(f"Simptom '{naziv}' že obstaja.", "napaka")
        else:
            baza.execute(
                "INSERT INTO simptom (uporabnik_id, naziv) VALUES (?, ?)",
                (g.uporabnik["id"], naziv),
            )
            baza.commit()
            flash(f"Simptom '{naziv}' je dodan.", "uspeh")

        return redirect(url_for("simptomi"))

    seznam_simptomov = baza.execute(
        "SELECT id, naziv FROM simptom WHERE uporabnik_id = ? ORDER BY naziv",
        (g.uporabnik["id"],),
    ).fetchall()

    return render_template("simptomi.html", simptomi=seznam_simptomov)


@app.route("/simptomi/<int:simptom_id>/uredi", methods=("GET", "POST"))
@prijava_zahtevana
def uredi_simptom(simptom_id):
    baza = db.get_db()
    simptom = baza.execute(
        "SELECT id, naziv FROM simptom WHERE id = ? AND uporabnik_id = ?",
        (simptom_id, g.uporabnik["id"]),
    ).fetchone()

    if simptom is None:
        flash("Simptom ne obstaja.", "napaka")
        return redirect(url_for("simptomi"))

    if request.method == "POST":
        naziv = request.form["naziv"].strip()

        if not naziv:
            flash("Naziv simptoma je obvezen.", "napaka")
        elif baza.execute(
            "SELECT id FROM simptom WHERE uporabnik_id = ? AND naziv = ? AND id != ?",
            (g.uporabnik["id"], naziv, simptom_id),
        ).fetchone():
            flash(f"Simptom '{naziv}' že obstaja.", "napaka")
        else:
            baza.execute(
                "UPDATE simptom SET naziv = ? WHERE id = ? AND uporabnik_id = ?",
                (naziv, simptom_id, g.uporabnik["id"]),
            )
            baza.commit()
            flash("Naziv simptoma je posodobljen.", "uspeh")
            return redirect(url_for("simptomi"))

    return render_template("uredi_simptom.html", simptom=simptom)


@app.route("/simptomi/<int:simptom_id>/izbrisi", methods=("POST",))
@prijava_zahtevana
def izbrisi_simptom(simptom_id):
    baza = db.get_db()
    simptom = baza.execute(
        "SELECT id FROM simptom WHERE id = ? AND uporabnik_id = ?",
        (simptom_id, g.uporabnik["id"]),
    ).fetchone()

    if simptom is None:
        flash("Simptom ne obstaja.", "napaka")
    else:
        stevilo_zapisov = baza.execute(
            "SELECT COUNT(*) FROM zapis_simptoma WHERE simptom_id = ?", (simptom_id,)
        ).fetchone()[0]

        if stevilo_zapisov > 0:
            # Markup: samo ta niz nima uporabniško vnesene vsebine (naziv
            # simptoma tu ni vključen), zato je varno vsebuje pravo <a>
            # povezavo brez pobega HTML - drugje flash sporočila ostanejo
            # samodejno pobegnjena.
            flash(
                Markup(
                    f"Simptoma ni mogoče izbrisati, ker ima {stevilo_zapisov_besedilo(stevilo_zapisov)}. "
                    f'Najprej izbrišite njegove zapise v <a href="{url_for("zgodovina", simptom_id=simptom_id)}">Zgodovini</a>.'
                ),
                "napaka",
            )
        else:
            baza.execute(
                "DELETE FROM simptom WHERE id = ? AND uporabnik_id = ?",
                (simptom_id, g.uporabnik["id"]),
            )
            baza.commit()
            flash("Simptom je izbrisan.", "uspeh")

    return redirect(url_for("simptomi"))


@app.route("/nov-zapis-simptoma", methods=("GET", "POST"))
@prijava_zahtevana
def nov_zapis_simptoma():
    baza = db.get_db()
    seznam_simptomov = baza.execute(
        "SELECT id, naziv FROM simptom WHERE uporabnik_id = ? ORDER BY naziv",
        (g.uporabnik["id"],),
    ).fetchall()

    if not seznam_simptomov:
        flash("Najprej dodajte vsaj eno vrsto simptoma.", "napaka")
        return redirect(url_for("simptomi"))

    danes = date.today()

    if request.method == "POST":
        simptom_id = request.form.get("simptom_id", type=int)
        jakost = request.form.get("jakost", type=int)
        opomba = request.form.get("opomba", "").strip() or None
        vnesen_datum = request.form.get("datum", "")

        veljaven_simptom = any(s["id"] == simptom_id for s in seznam_simptomov)

        napaka = None
        izbran_datum = None
        if not veljaven_simptom:
            napaka = "Izberite veljaven simptom."
        elif jakost is None or not (0 <= jakost <= 10):
            napaka = "Jakost mora biti med 0 in 10."
        else:
            try:
                izbran_datum = datetime.strptime(vnesen_datum, "%Y-%m-%d").date()
            except ValueError:
                napaka = "Vnesite veljaven datum."
            else:
                if izbran_datum > danes:
                    napaka = "Datum ne sme biti v prihodnosti."

        if napaka is None:
            baza.execute(
                "INSERT INTO zapis_simptoma (simptom_id, datum, jakost, opomba) VALUES (?, ?, ?, ?)",
                (simptom_id, izbran_datum.isoformat(), jakost, opomba),
            )
            baza.commit()
            flash("Zapis je shranjen.", "uspeh")
            return redirect(url_for("domov"))

        flash(napaka, "napaka")

    return render_template("nov_zapis_simptoma.html", simptomi=seznam_simptomov, danes=danes.isoformat())


@app.route("/terapije", methods=("GET", "POST"))
@prijava_zahtevana
def terapije():
    baza = db.get_db()

    if request.method == "POST":
        naziv = request.form["naziv"].strip()
        odmerek = request.form.get("odmerek", "").strip() or None
        pogostost = request.form.get("pogostost", "").strip() or None

        if not naziv:
            flash("Naziv terapije je obvezen.", "napaka")
        else:
            baza.execute(
                "INSERT INTO terapija (uporabnik_id, naziv, odmerek, pogostost, aktivna) VALUES (?, ?, ?, ?, 1)",
                (g.uporabnik["id"], naziv, odmerek, pogostost),
            )
            baza.commit()
            flash(f"Terapija '{naziv}' je dodana.", "uspeh")

        return redirect(url_for("terapije"))

    danes = date.today().isoformat()
    seznam_terapij = baza.execute(
        """
        SELECT t.id, t.naziv, t.odmerek, t.pogostost, t.aktivna,
               (SELECT COUNT(*) FROM zapis_terapije z
                WHERE z.terapija_id = t.id AND substr(z.casovna_znacka, 1, 10) = ?) AS vzeto_danes
        FROM terapija t
        WHERE t.uporabnik_id = ?
        ORDER BY t.aktivna DESC, t.naziv
        """,
        (danes, g.uporabnik["id"]),
    ).fetchall()

    return render_template("terapije.html", terapije=seznam_terapij)


@app.route("/terapije/<int:terapija_id>/uredi", methods=("GET", "POST"))
@prijava_zahtevana
def uredi_terapijo(terapija_id):
    baza = db.get_db()
    terapija = baza.execute(
        "SELECT * FROM terapija WHERE id = ? AND uporabnik_id = ?",
        (terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if terapija is None:
        flash("Terapija ne obstaja.", "napaka")
        return redirect(url_for("terapije"))

    if request.method == "POST":
        naziv = request.form["naziv"].strip()
        odmerek = request.form.get("odmerek", "").strip() or None
        pogostost = request.form.get("pogostost", "").strip() or None

        if not naziv:
            flash("Naziv terapije je obvezen.", "napaka")
        else:
            baza.execute(
                "UPDATE terapija SET naziv = ?, odmerek = ?, pogostost = ? WHERE id = ? AND uporabnik_id = ?",
                (naziv, odmerek, pogostost, terapija_id, g.uporabnik["id"]),
            )
            baza.commit()
            flash("Terapija je posodobljena.", "uspeh")
            return redirect(url_for("terapije"))

    return render_template("uredi_terapijo.html", terapija=terapija)


@app.route("/terapije/<int:terapija_id>/izbrisi", methods=("POST",))
@prijava_zahtevana
def izbrisi_terapijo(terapija_id):
    baza = db.get_db()
    terapija = baza.execute(
        "SELECT id FROM terapija WHERE id = ? AND uporabnik_id = ?",
        (terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if terapija is None:
        flash("Terapija ne obstaja.", "napaka")
    else:
        stevilo_zapisov = baza.execute(
            "SELECT COUNT(*) FROM zapis_terapije WHERE terapija_id = ?", (terapija_id,)
        ).fetchone()[0]

        if stevilo_zapisov > 0:
            flash(
                f"Terapije ni mogoče izbrisati, ker ima {stevilo_zapisov_besedilo(stevilo_zapisov)} "
                "o jemanju. Najprej jih izbrišite v Zgodovini jemanja ali terapijo ukinite.",
                "napaka",
            )
        else:
            baza.execute(
                "DELETE FROM terapija WHERE id = ? AND uporabnik_id = ?",
                (terapija_id, g.uporabnik["id"]),
            )
            baza.commit()
            flash("Terapija je izbrisana.", "uspeh")

    return redirect(url_for("terapije"))


@app.route("/terapije/<int:terapija_id>/preklopi", methods=("POST",))
@prijava_zahtevana
def preklopi_terapijo(terapija_id):
    baza = db.get_db()
    terapija = baza.execute(
        "SELECT aktivna FROM terapija WHERE id = ? AND uporabnik_id = ?",
        (terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if terapija is None:
        flash("Terapija ne obstaja.", "napaka")
    else:
        nova_vrednost = 0 if terapija["aktivna"] else 1
        baza.execute(
            "UPDATE terapija SET aktivna = ? WHERE id = ? AND uporabnik_id = ?",
            (nova_vrednost, terapija_id, g.uporabnik["id"]),
        )
        baza.commit()
        sporocilo = "Terapija je ukinjena." if nova_vrednost == 0 else "Terapija je ponovno aktivna."
        flash(sporocilo, "uspeh")

    return redirect(url_for("terapije"))


@app.route("/terapije/<int:terapija_id>/vzeto", methods=("POST",))
@prijava_zahtevana
def oznaci_vzeto(terapija_id):
    baza = db.get_db()
    terapija = baza.execute(
        "SELECT id FROM terapija WHERE id = ? AND uporabnik_id = ? AND aktivna = 1",
        (terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if terapija is None:
        flash("Terapija ne obstaja ali ni aktivna.", "napaka")
    else:
        baza.execute(
            "INSERT INTO zapis_terapije (terapija_id, casovna_znacka) VALUES (?, ?)",
            (terapija_id, datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        baza.commit()
        flash("Jemanje terapije je zabeleženo.", "uspeh")

    if request.form.get("naslednja") == "domov":
        return redirect(url_for("domov") + "#danes-terapije")
    return redirect(url_for("terapije"))


@app.route("/terapije/<int:terapija_id>/zgodovina")
@prijava_zahtevana
def zgodovina_terapije(terapija_id):
    baza = db.get_db()
    terapija = baza.execute(
        "SELECT id, naziv FROM terapija WHERE id = ? AND uporabnik_id = ?",
        (terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if terapija is None:
        flash("Terapija ne obstaja.", "napaka")
        return redirect(url_for("terapije"))

    zapisi = baza.execute(
        "SELECT id, casovna_znacka FROM zapis_terapije WHERE terapija_id = ? ORDER BY casovna_znacka DESC, id DESC",
        (terapija_id,),
    ).fetchall()

    return render_template("zgodovina_terapije.html", terapija=terapija, zapisi=zapisi)


@app.route("/terapije/<int:terapija_id>/zgodovina/<int:zapis_id>/uredi", methods=("GET", "POST"))
@prijava_zahtevana
def uredi_zapis_terapije(terapija_id, zapis_id):
    baza = db.get_db()
    zapis = baza.execute(
        """
        SELECT z.id, z.casovna_znacka FROM zapis_terapije z
        JOIN terapija t ON z.terapija_id = t.id
        WHERE z.id = ? AND z.terapija_id = ? AND t.uporabnik_id = ?
        """,
        (zapis_id, terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if zapis is None:
        flash("Zapis ne obstaja.", "napaka")
        return redirect(url_for("zgodovina_terapije", terapija_id=terapija_id))

    if request.method == "POST":
        vnos = request.form.get("casovna_znacka", "")

        try:
            razclenjeno = datetime.strptime(vnos, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Vnesi veljaven datum in uro.", "napaka")
        else:
            baza.execute(
                "UPDATE zapis_terapije SET casovna_znacka = ? WHERE id = ? AND terapija_id = ?",
                (razclenjeno.strftime("%Y-%m-%d %H:%M"), zapis_id, terapija_id),
            )
            baza.commit()
            flash("Zapis o jemanju je posodobljen.", "uspeh")
            return redirect(url_for("zgodovina_terapije", terapija_id=terapija_id))

    vrednost_polja = zapis["casovna_znacka"].replace(" ", "T")
    return render_template(
        "uredi_zapis_terapije.html", terapija_id=terapija_id, vrednost_polja=vrednost_polja
    )


@app.route("/terapije/<int:terapija_id>/zgodovina/<int:zapis_id>/izbrisi", methods=("POST",))
@prijava_zahtevana
def izbrisi_zapis_terapije(terapija_id, zapis_id):
    baza = db.get_db()
    zapis = baza.execute(
        """
        SELECT z.id FROM zapis_terapije z
        JOIN terapija t ON z.terapija_id = t.id
        WHERE z.id = ? AND z.terapija_id = ? AND t.uporabnik_id = ?
        """,
        (zapis_id, terapija_id, g.uporabnik["id"]),
    ).fetchone()

    if zapis is None:
        flash("Zapis ne obstaja.", "napaka")
    else:
        baza.execute("DELETE FROM zapis_terapije WHERE id = ?", (zapis_id,))
        baza.commit()
        flash("Zapis o jemanju je izbrisan.", "uspeh")

    return redirect(url_for("zgodovina_terapije", terapija_id=terapija_id))


@app.route("/terapije/<int:terapija_id>/zgodovina/izbrisi-vec", methods=("POST",))
@prijava_zahtevana
def izbrisi_vec_zapisov_terapije(terapija_id):
    id_seznam = request.form.getlist("zapis_id", type=int)

    if not id_seznam:
        flash("Nobenega zapisa nisi izbral.", "napaka")
        return redirect(url_for("zgodovina_terapije", terapija_id=terapija_id))

    baza = db.get_db()
    placeholderji = ",".join("?" * len(id_seznam))
    stevilo_izbrisanih = baza.execute(
        f"""
        DELETE FROM zapis_terapije
        WHERE id IN ({placeholderji})
          AND terapija_id = (
              SELECT id FROM terapija WHERE id = ? AND uporabnik_id = ?
          )
        """,
        (*id_seznam, terapija_id, g.uporabnik["id"]),
    ).rowcount
    baza.commit()

    flash(f"Izbrisanih {stevilka_zapisov(stevilo_izbrisanih)}.", "uspeh")
    return redirect(url_for("zgodovina_terapije", terapija_id=terapija_id))


@app.route("/zgodovina")
@prijava_zahtevana
def zgodovina():
    baza = db.get_db()

    danes = date.today()
    zacetek = request.args.get("od", (danes - timedelta(days=30)).isoformat())
    konec = request.args.get("do", danes.isoformat())
    izbrani_simptom_id = request.args.get("simptom_id", type=int)

    seznam_simptomov = baza.execute(
        "SELECT id, naziv FROM simptom WHERE uporabnik_id = ? ORDER BY naziv",
        (g.uporabnik["id"],),
    ).fetchall()

    poizvedba = """
        SELECT z.id, z.datum, z.jakost, z.opomba, s.naziv AS simptom_naziv
        FROM zapis_simptoma z
        JOIN simptom s ON z.simptom_id = s.id
        WHERE s.uporabnik_id = ? AND z.datum BETWEEN ? AND ?
    """
    parametri = [g.uporabnik["id"], zacetek, konec]

    if izbrani_simptom_id is not None:
        poizvedba += " AND s.id = ?"
        parametri.append(izbrani_simptom_id)

    poizvedba += " ORDER BY z.datum DESC, z.id DESC"

    zapisi = baza.execute(poizvedba, parametri).fetchall()

    return render_template(
        "zgodovina.html",
        zapisi=zapisi,
        zacetek=zacetek,
        konec=konec,
        simptomi=seznam_simptomov,
        izbrani_simptom_id=izbrani_simptom_id,
    )


@app.route("/zgodovina/<int:zapis_id>/uredi", methods=("GET", "POST"))
@prijava_zahtevana
def uredi_zapis_simptoma(zapis_id):
    baza = db.get_db()
    zapis = baza.execute(
        """
        SELECT z.id, z.simptom_id, z.datum, z.jakost, z.opomba
        FROM zapis_simptoma z
        JOIN simptom s ON z.simptom_id = s.id
        WHERE z.id = ? AND s.uporabnik_id = ?
        """,
        (zapis_id, g.uporabnik["id"]),
    ).fetchone()

    if zapis is None:
        flash("Zapis ne obstaja.", "napaka")
        return redirect(url_for("zgodovina"))

    seznam_simptomov = baza.execute(
        "SELECT id, naziv FROM simptom WHERE uporabnik_id = ? ORDER BY naziv",
        (g.uporabnik["id"],),
    ).fetchall()

    if request.method == "POST":
        simptom_id = request.form.get("simptom_id", type=int)
        datum = request.form["datum"]
        jakost = request.form.get("jakost", type=int)
        opomba = request.form.get("opomba", "").strip() or None

        veljaven_simptom = any(s["id"] == simptom_id for s in seznam_simptomov)

        napaka = None
        if not veljaven_simptom:
            napaka = "Izberite veljaven simptom."
        elif jakost is None or not (0 <= jakost <= 10):
            napaka = "Jakost mora biti med 0 in 10."
        else:
            try:
                datetime.strptime(datum, "%Y-%m-%d")
            except ValueError:
                napaka = "Vnesite veljaven datum."

        if napaka is None:
            baza.execute(
                """
                UPDATE zapis_simptoma
                SET simptom_id = ?, datum = ?, jakost = ?, opomba = ?
                WHERE id = ?
                """,
                (simptom_id, datum, jakost, opomba, zapis_id),
            )
            baza.commit()
            flash("Zapis je posodobljen.", "uspeh")
            return redirect(url_for("zgodovina"))

        flash(napaka, "napaka")

    return render_template("uredi_zapis_simptoma.html", zapis=zapis, simptomi=seznam_simptomov)


@app.route("/zgodovina/<int:zapis_id>/izbrisi", methods=("POST",))
@prijava_zahtevana
def izbrisi_zapis_simptoma(zapis_id):
    baza = db.get_db()
    zapis = baza.execute(
        """
        SELECT z.id FROM zapis_simptoma z
        JOIN simptom s ON z.simptom_id = s.id
        WHERE z.id = ? AND s.uporabnik_id = ?
        """,
        (zapis_id, g.uporabnik["id"]),
    ).fetchone()

    if zapis is None:
        flash("Zapis ne obstaja.", "napaka")
    else:
        baza.execute("DELETE FROM zapis_simptoma WHERE id = ?", (zapis_id,))
        baza.commit()
        flash("Zapis je izbrisan.", "uspeh")

    return redirect(url_for("zgodovina"))


@app.route("/zgodovina/izbrisi-vec", methods=("POST",))
@prijava_zahtevana
def izbrisi_vec_zapisov_simptoma():
    id_seznam = request.form.getlist("zapis_id", type=int)

    if not id_seznam:
        flash("Nobenega zapisa nisi izbral.", "napaka")
        return redirect(url_for("zgodovina"))

    baza = db.get_db()
    placeholderji = ",".join("?" * len(id_seznam))
    stevilo_izbrisanih = baza.execute(
        f"""
        DELETE FROM zapis_simptoma
        WHERE id IN ({placeholderji})
          AND simptom_id IN (SELECT id FROM simptom WHERE uporabnik_id = ?)
        """,
        (*id_seznam, g.uporabnik["id"]),
    ).rowcount
    baza.commit()

    flash(f"Izbrisanih {stevilka_zapisov(stevilo_izbrisanih)}.", "uspeh")
    return redirect(url_for("zgodovina"))


@app.route("/povzetek")
@prijava_zahtevana
def povzetek():
    baza = db.get_db()
    danes = date.today()

    try:
        zacetni_datum = datetime.strptime(request.args.get("od", ""), "%Y-%m-%d").date()
        koncni_datum = datetime.strptime(request.args.get("do", ""), "%Y-%m-%d").date()
        stevilo_dni = (koncni_datum - zacetni_datum).days + 1
        if not (0 < stevilo_dni <= 366):
            raise ValueError
    except ValueError:
        koncni_datum = danes
        zacetni_datum = danes - timedelta(days=30)
        stevilo_dni = 31

    zacetek = zacetni_datum.isoformat()
    konec = koncni_datum.isoformat()
    seznam_datumov = [(zacetni_datum + timedelta(days=i)).isoformat() for i in range(stevilo_dni)]

    zapisi = baza.execute(
        """
        SELECT z.datum, z.jakost, z.opomba, s.naziv AS simptom_naziv
        FROM zapis_simptoma z
        JOIN simptom s ON z.simptom_id = s.id
        WHERE s.uporabnik_id = ? AND z.datum BETWEEN ? AND ?
        ORDER BY z.datum, s.naziv
        """,
        (g.uporabnik["id"], zacetek, konec),
    ).fetchall()

    jakosti_po_simptomu = {}
    for zapis in zapisi:
        jakosti_po_simptomu.setdefault(zapis["simptom_naziv"], {})[zapis["datum"]] = zapis["jakost"]

    nizi = [
        {"naziv": naziv, "vrednosti": [vrednosti.get(d) for d in seznam_datumov]}
        for naziv, vrednosti in jakosti_po_simptomu.items()
    ]

    podatki_grafa = {"datumi": seznam_datumov, "nizi": nizi}

    aktivne_terapije = baza.execute(
        "SELECT naziv, odmerek, pogostost FROM terapija WHERE uporabnik_id = ? AND aktivna = 1 ORDER BY naziv",
        (g.uporabnik["id"],),
    ).fetchall()

    zapisi_jemanja = baza.execute(
        """
        SELECT z.casovna_znacka, t.naziv AS terapija_naziv
        FROM zapis_terapije z
        JOIN terapija t ON z.terapija_id = t.id
        WHERE t.uporabnik_id = ? AND substr(z.casovna_znacka, 1, 10) BETWEEN ? AND ?
        ORDER BY z.casovna_znacka
        """,
        (g.uporabnik["id"], zacetek, konec),
    ).fetchall()

    jemanja_po_terapiji = {}
    for zapis in zapisi_jemanja:
        dan = zapis["casovna_znacka"][:10]
        dnevi = jemanja_po_terapiji.setdefault(zapis["terapija_naziv"], {})
        dnevi[dan] = dnevi.get(dan, 0) + 1

    nizi_terapij = [
        {"naziv": naziv, "vrednosti": [dnevi.get(d, 0) for d in seznam_datumov]}
        for naziv, dnevi in jemanja_po_terapiji.items()
    ]
    podatki_grafa_terapij = {"datumi": seznam_datumov, "nizi": nizi_terapij}

    return render_template(
        "povzetek.html",
        zapisi=zapisi,
        podatki_grafa=podatki_grafa,
        terapije=aktivne_terapije,
        zapisi_jemanja=zapisi_jemanja,
        podatki_grafa_terapij=podatki_grafa_terapij,
        zacetek=zacetek,
        konec=konec,
    )


@app.errorhandler(404)
def stran_ne_obstaja(napaka):
    return render_template("napaka.html", sporocilo="Te strani ni mogoče najti."), 404


@app.errorhandler(400)
def neveljavna_zahteva(napaka):
    return render_template("napaka.html", sporocilo="Zahteva ni veljavna. Poskusite znova."), 400


if __name__ == "__main__":
    app.run(debug=True)
