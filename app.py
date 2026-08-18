import os
import sqlite3
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import db

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "zdravje.db")
app.config["SECRET_KEY"] = "razvojni-skrivni-kljuc-samo-za-lokalni-prototip"
os.makedirs(app.instance_path, exist_ok=True)
db.init_app(app)


@app.before_request
def nalozi_prijavljenega_uporabnika():
    uporabnik_id = session.get("uporabnik_id")
    if uporabnik_id is None:
        g.uporabnik = None
    else:
        g.uporabnik = db.get_db().execute(
            "SELECT id, uporabnisko_ime FROM uporabnik WHERE id = ?", (uporabnik_id,)
        ).fetchone()


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
    return render_template("domov.html")


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


@app.route("/odjava")
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
        elif not geslo or len(geslo) < 6:
            napaka = "Geslo mora imeti vsaj 6 znakov."
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
                flash("Račun je bil uspešno ustvarjen. Zdaj se lahko prijaviš.", "uspeh")
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
            flash(
                "Simptoma ni mogoče izbrisati, ker ima shranjene zapise. "
                "Najprej izbriši njegove zapise v Zgodovini.",
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
        flash("Najprej dodaj vsaj eno vrsto simptoma.", "napaka")
        return redirect(url_for("simptomi"))

    if request.method == "POST":
        simptom_id = request.form.get("simptom_id", type=int)
        jakost = request.form.get("jakost", type=int)
        opomba = request.form.get("opomba", "").strip() or None

        veljaven_simptom = any(s["id"] == simptom_id for s in seznam_simptomov)

        napaka = None
        if not veljaven_simptom:
            napaka = "Izberi veljaven simptom."
        elif jakost is None or not (0 <= jakost <= 10):
            napaka = "Jakost mora biti med 0 in 10."

        if napaka is None:
            baza.execute(
                "INSERT INTO zapis_simptoma (simptom_id, datum, jakost, opomba) VALUES (?, ?, ?, ?)",
                (simptom_id, date.today().isoformat(), jakost, opomba),
            )
            baza.commit()
            flash("Zapis je shranjen.", "uspeh")
            return redirect(url_for("domov"))

        flash(napaka, "napaka")

    return render_template("nov_zapis_simptoma.html", simptomi=seznam_simptomov)


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
                WHERE z.terapija_id = t.id AND z.datum = ?) AS vzeto_danes
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
            "INSERT INTO zapis_terapije (terapija_id, datum) VALUES (?, ?)",
            (terapija_id, date.today().isoformat()),
        )
        baza.commit()
        flash("Zabeleženo, da si vzel terapijo.", "uspeh")

    return redirect(url_for("terapije"))


@app.route("/zgodovina")
@prijava_zahtevana
def zgodovina():
    baza = db.get_db()

    danes = date.today()
    zacetek = request.args.get("od", (danes - timedelta(days=30)).isoformat())
    konec = request.args.get("do", danes.isoformat())

    zapisi = baza.execute(
        """
        SELECT z.id, z.datum, z.jakost, z.opomba, s.naziv AS simptom_naziv
        FROM zapis_simptoma z
        JOIN simptom s ON z.simptom_id = s.id
        WHERE s.uporabnik_id = ? AND z.datum BETWEEN ? AND ?
        ORDER BY z.datum DESC, z.id DESC
        """,
        (g.uporabnik["id"], zacetek, konec),
    ).fetchall()

    return render_template("zgodovina.html", zapisi=zapisi, zacetek=zacetek, konec=konec)


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
            napaka = "Izberi veljaven simptom."
        elif jakost is None or not (0 <= jakost <= 10):
            napaka = "Jakost mora biti med 0 in 10."
        else:
            try:
                datetime.strptime(datum, "%Y-%m-%d")
            except ValueError:
                napaka = "Vnesi veljaven datum."

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


if __name__ == "__main__":
    app.run(debug=True)
