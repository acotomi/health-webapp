# Dnevnik razvojnih odločitev

## 2026-08-18 — Obveznost polj terapije, CHECK omejitve in vklop tujih ključev

**Vprašanje:** Ali naj bosta `odmerek` in `pogostost` pri terapiji obvezna
(`NOT NULL`)? Ali naj bodo omejitve vrednosti (jakost 0–10, aktivna 0/1)
uveljavljene v bazi, ne le v obrazcu? Ali naj SQLite preverja tuje ključe?

**Odločitev:** `odmerek` in `pogostost` sta v `schema.sql` dovoljena kot
`NULL` (neobvezna). `zapis_simptoma.jakost` ima `CHECK (jakost BETWEEN 0 AND
10)`, `terapija.aktivna` ima `CHECK (aktivna IN (0, 1))`. V `db.py` funkcija
`get_db()` ob vsaki povezavi izvede `PRAGMA foreign_keys = ON`.

**Utemeljitev:**
- Obvezen `odmerek`/`pogostost` bi bil v nasprotju z ER-diagramom v
  diplomskem delu (slika 3), kjer sta polji brez zvezdice. Tabela je
  poimenovana `terapija`, ne `zdravilo` — vključuje tudi terapije brez
  jasnega odmerka (fizioterapija, dihalne vaje, dieta). Obvezno polje bi v
  teh primerih uporabnika silila v vnos nesmiselne vrednosti, kar je v
  nasprotju z ugotovitvijo iz 3.2.2 (obremenjujoč vnos je glavna ovira) in z
  N6 (zbiraj le nujne podatke).
- CHECK omejitve v bazi so neodvisne od preverjanja na obrazcu (F2, N3): prvo
  je uporabniška izkušnja, drugo zagotavlja celovitost podatkov, tudi ob
  napaki v kodi vmesnika ali ročnem posegu v bazo. Povezano z načelom
  celovitosti podatkov (GDPR, člen 5).
- SQLite privzeto ne uveljavlja tujih ključev, ne glede na to, da so
  deklarirani v shemi. Brez `PRAGMA foreign_keys = ON` bi baza tiho sprejela
  npr. zapis simptoma, ki kaže na neobstoječ simptom, kar bi ogrozilo
  zanesljivost podatkov, na katerih temelji prikaz (F6). Pragma je
  nastavljena v `get_db()`, ker jo je treba izvesti ob vsaki novi povezavi,
  ne le enkrat ob ustvarjanju baze.

**Zavrnjene možnosti:** Prvotno sem `odmerek` in `pogostost` označil kot
`NOT NULL`, ker ju F3 navaja kot del vnosa terapije. Zavrnjeno po pregledu
ER-diagrama in ponovnem premisleku o vrstah terapij, ki jih tabela mora
zajeti.

**Za katero poglavje:** 4.3 (tehnološka zasnova), 5 (razprava — omejitve
privzetega vedenja SQLite pri tujih ključih).

## 2026-08-18 — Samodejni datum pri novem zapisu simptoma in pravilo brisanja simptoma

**Vprašanje:** Ali naj obrazec "Nov zapis simptoma" vključuje polje za datum? Kaj
se zgodi, če uporabnik poskuša izbrisati vrsto simptoma, ki že ima shranjene
zapise jakosti?

**Odločitev:** Obrazec za nov zapis nima polja za datum — datum se samodejno
nastavi na današnji dan (`date.today()`). Vrste simptoma z obstoječimi zapisi
ni mogoče izbrisati; aplikacija to prepreči s preverjanjem v kodi (uporabniku
pojasni zakaj), ne šele s tem, da baza vrže napako.

**Utemeljitev:**
- Zaslon "Nov zapis simptoma" v specifikaciji (poglavje 4) navaja natanko tri
  elemente: izbira simptoma, drsnik jakosti, opomba — brez datuma. To se sklada
  z N3 (vnos v največ treh korakih) in ugotovitvijo 3.2.2 o obremenjujočem
  vnosu: dodatno polje bi korak podaljšalo. Vnos za pretekle dni bo mogoč
  kasneje prek urejanja v Zgodovini (F8), ne prek hitrega dnevnega vnosa.
- Ker so tuji ključi v SQLite vklopljeni (glej prejšnji vnos), bi poskus
  izbrisa simptoma z obstoječimi zapisi tako ali tako povzročil napako baze.
  Preverjanje v kodi pred izbrisom uporabniku pove razlog v razumljivem jeziku,
  namesto da bi videl surovo napako — skladno z N2 (razumljiv vmesnik).

**Zavrnjene možnosti:** Kaskadno brisanje (izbris simptoma bi samodejno
izbrisal tudi vse njegove zapise) je bilo zavrnjeno — pri zdravstvenih podatkih
tiho izgubljanje zgodovine ni sprejemljivo (F8: uporabnik ima nadzor nad
lastnimi podatki, izbris mora biti nameren in eksploziten, ne stranski učinek).

**Za katero poglavje:** 4.3 (tehnološka zasnova), 4.4 (vmesnik — utemeljitev
treh korakov).
