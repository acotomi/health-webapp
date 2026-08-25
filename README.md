# health-webapp

Prototip spletne aplikacije za spremljanje simptomov in terapij. Diplomsko delo,
Fakulteta za upravo UL. Podrobnosti glej `SPECIFIKACIJA.md` in `CLAUDE.md`.

## Zagon (prvič, na novem računalniku)

```powershell
git clone <naslov repozitorija>
cd health-webapp
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python pripravi_bazo.py
python app.py
```

Baza (`instance/zdravje.db`) ni v repozitoriju (glej `.gitignore`), zato jo
`pripravi_bazo.py` ustvari iz `schema.sql`. Poženeš jo samo enkrat — če jo
poženeš znova na obstoječi bazi, javi napako (tabele že obstajajo), kar je
namerna zaščita pred izgubo podatkov.

Za testne/demonstracijske podatke (neobvezno, priporočeno za razvoj):

```powershell
python testni_podatki.py
python demo_podatki.py
```

`demo_podatki.py` ustvari tri uporabnike (`Demo1`, `Demo2`, `Demo3`, geslo
`demo1234`) z izmišljenimi, a značilnimi kroničnimi profili — uporabno za
posnetke zaslona.

Aplikacija je nato dosegljiva na `http://127.0.0.1:5000/`. Strežnik ustaviš z
`Ctrl+C` v terminalu.

## Nadaljevanje razvoja (že klonirano)

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

Če si po zadnjem `git pull` dobil nove odvisnosti, pred zagonom še:

```powershell
pip install -r requirements.txt
```