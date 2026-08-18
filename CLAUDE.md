# Prototip: Spletna aplikacija za spremljanje simptomov in terapij

Prototip za diplomsko delo na Fakulteti za upravo UL (program Upravna informatika).
Mentor: doc. dr. Aleš Smrdel.

**Namen:** ponazoriti, kako je mogoče nasloviti pomanjkljivosti obstoječih digitalnih
rešitev, ugotovljene v teoretičnem delu. Ni izdelek za uvedbo v prakso.

## Ključno pravilo

To je **avtorsko delo študenta**. Tvoja vloga je razlaga, pregled in pomoč pri
odpravljanju napak — ne pisanje celotnih delov namesto avtorja.

- Kodo razlagaj, preden jo predlagaš.
- Predlagaj manjše korake, ne celotnih datotek naenkrat.
- Če avtor nečesa ne razume, razloži, ne obidi.
- Vsak nasvet mora biti tak, da ga zna avtor zagovarjati pri zagovoru.

## Kaj prototip NI

- ni medicinski pripomoček
- ne postavlja diagnoz in ne daje priporočil o terapiji
- ne razlaga vnesenih podatkov z algoritmi
- ni klinično preverjen, ni testiran na bolnikih

Nikoli ne dodajaj funkcij, ki bi to presegale (ocene tveganja, opozorila o
zdravstvenem stanju, priporočila odmerkov, napovedovanje poslabšanj).

## Tehnologije

- Python 3, Flask
- SQLite (datotečna baza)
- Jinja2 predloge, običajen HTML/CSS
- Chart.js za grafični prikaz
- Brez zunanjih storitev, brez prijave prek tretjih ponudnikov

Novih odvisnosti ne dodajaj brez izrecnega dogovora. Vsaka knjižnica je nekaj,
kar mora avtor znati pojasniti.

## Obseg

Ena vrsta uporabnika (bolnik). Podatke vnaša in pregleduje zase.

Zunaj obsega: dostop zdravstvenih delavcev, povezovanje z zVEM ali CRPP,
nosljive naprave, samodejni zajem podatkov, obveščanje po e-pošti,
obnovitev gesla, mobilna aplikacija.

## Načela iz teoretičnega dela

Vsaka odločitev pri razvoju naj izhaja iz ugotovitev poglavja 3:

- **Vnos mora biti hiter** — dnevni zapis v največ treh korakih.
- **Prikaz mora biti razumljiv** — graf z označenimi območji jakosti in kratkim
  pojasnilom, ne surova tabela.
- **Osnova naj ostane preprosta** — dodatne možnosti so izbira, ne privzeto stanje.
- **Zbiraj čim manj podatkov** — vsako novo polje mora imeti utemeljitev.

## Varstvo osebnih podatkov

Zdravstveni podatki so posebna vrsta osebnih podatkov (člen 9 GDPR).

- Gesla shranjuj izključno zgoščena (werkzeug.security).
- Uporabnik dostopa samo do svojih zapisov — preveri lastništvo pri vsaki poizvedbi.
- Ne zbiraj imena, priimka, e-naslova, datuma rojstva, spola ali diagnoze.
- Ne beleži dostopov v dnevnike več, kot je nujno za delovanje.
- V repozitorij ne shranjuj datoteke baze s podatki (glej .gitignore).

## Jezik

- Uporabniški vmesnik: **slovenščina**
- Imena tabel in polj v bazi: **slovenščina brez šumnikov** (glej SPECIFIKACIJA.md)
- Imena funkcij in spremenljivk v kodi: **angleščina**
- Komentarji: slovenščina

## Delovni tok

- Veja `main` naj ostane delujoča.
- Sporočila commitov v slovenščini, kratka in opisna.
- Po vsaki zaključeni funkcionalnosti zabeleži odločitve — glej veščino
  `zabelezi-odlocitev`. Te zapiske avtor potrebuje za poglavja 4.3–4.5 in 5.

## Datoteke

- `SPECIFIKACIJA.md` — zahteve, podatkovni model, seznam nalog
- `docs/odlocitve.md` — dnevnik razvojnih odločitev (nastaja sproti)
