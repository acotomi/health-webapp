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
python app.py
```

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