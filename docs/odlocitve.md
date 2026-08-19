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

## 2026-08-18 — Chart.js shranjen lokalno, ne prek CDN

**Vprašanje:** Ali naj se Chart.js (za graf gibanja jakosti simptomov, F6) naloži
prek CDN povezave ali naj bo shranjen lokalno v `static/`?

**Odločitev:** Chart.js je prenesen in shranjen lokalno v `static/`, brez
povezave na CDN.

**Utemeljitev:**
- Neodvisnost od omrežja: aplikacija mora delovati brez internetne povezave —
  tudi na dan zagovora, kjer internetna povezava ni zagotovljena.
- Preprečitev razkritja podatkov o uporabi tretji osebi: pri nalaganju skripte
  s CDN bi ponudnik CDN ob vsakem obisku strani videl IP naslov in čas dostopa
  uporabnika, kar je v nasprotju z načelom "brez zunanjih storitev" iz
  CLAUDE.md in z načelom minimizacije razkritja osebnih podatkov (GDPR, člen
  5). Ker gre za aplikacijo, ki obravnava zdravstvene podatke (posebna vrsta
  osebnih podatkov, člen 9 GDPR), je ta razlog pri zagovoru tehtnejši od
  praktičnega razloga neodvisnosti od omrežja.

**Zavrnjene možnosti:** Nalaganje Chart.js prek javnega CDN (npr.
cdn.jsdelivr.net) — zavrnjeno iz obeh zgornjih razlogov.

**Za katero poglavje:** 4.3 (tehnološka zasnova), 4.5 (varstvo podatkov).

## 2026-08-18 — Varnostni pregled: CSRF zaščita, odjava kot POST, opuščen zaklep prijave

**Vprašanje:** Ali aplikacija potrebuje CSRF zaščito, ali je odjava prek GET
povezave ustrezna, in ali naj se doda zaščita pred grobo silo (brute-force)
pri prijavi?

**Odločitev:** Dodana je ročna CSRF zaščita (žeton, shranjen v seji, preverjen
pri vsaki POST zahtevi prek `secrets.compare_digest`) — brez nove knjižnice.
`/odjava` je spremenjena iz GET v POST pot. Eksplicitno sta nastavljena
`SESSION_COOKIE_HTTPONLY` in `SESSION_COOKIE_SAMESITE=Lax`. Zaklep prijave po
več neuspešnih poskusih (brute-force zaščita) ni bil dodan.

**Utemeljitev:**
- Brez CSRF zaščite bi tuja spletna stran lahko prek skritega obrazca v imenu
  prijavljenega uporabnika sprožila akcijo (npr. izbris zapisa) — nesprejemljivo
  tveganje pri aplikaciji, ki obravnava zdravstvene podatke (člen 9 GDPR).
  Ročna implementacija (žeton + primerjava v konstantnem času) je zadostna za
  enouporabniški prototip in ne zahteva dodatne odvisnosti (Flask-WTF), kar je
  skladno z načelom "novih odvisnosti ne dodajaj brez dogovora".
- Odjava (sprememba stanja) prek GET zahteve je splošno znana slaba praksa —
  GET zahteve lahko sprožijo tudi povezave, predpomnjenje brskalnika ali
  vnaprejšnje nalaganje, ne le namerna uporabnikova akcija.
- Zaklep prijave po neuspelih poskusih je bil namenoma izpuščen: aplikacija je
  lokalen enouporabniški prototip brez javne izpostavljenosti, dodatna logika
  (števec, časovna omejitev, hramba stanja) pa poveča kompleksnost brez jasne
  koristi za trenuten obseg. To je omejitev, ki jo je vredno omeniti v
  poglavju 5, ne prikrita pomanjkljivost.

**Zavrnjene možnosti:** Flask-WTF za CSRF (zavrnjeno — nova odvisnost za
funkcionalnost, ki jo je mogoče doseči v ducatu vrstic). Zaklep prijave po
neuspelih poskusih (zavrnjeno za zdaj, glej utemeljitev).

**Za katero poglavje:** 4.5 (varstvo podatkov), 5 (razprava, omejitve).

## 2026-08-19 — Enotna oblika izpisa datuma

**Vprašanje:** Datumi so bili v tabeli zgodovine, povzetka in na oznakah grafa
izpisani v surovi obliki ISO (YYYY-MM-DD), kar ni domača slovenska oblika.

**Odločitev:** Dodana je ena pomožna funkcija `oblikuj_datum_sl()` v `app.py`,
registrirana kot Jinja filter `datum_sl`. Uporablja se v tabeli zgodovine,
tabeli povzetka, naslovu obdobja povzetka in pri pripravi oznak na osi x
grafa — vsi izpišejo datum v obliki „19. 8. 2026". Polja `<input type="date">`
niso spremenjena, ker njihov prikaz nadzoruje brskalnik glede na jezik
sistema.

**Utemeljitev:** N2 (razumljiv vmesnik, brez nepotrebnih elementov) — domača
oblika datuma je berljivejša od ISO zapisa za končnega uporabnika. Ena sama
pomožna funkcija namesto ponavljanja oblikovanja v vsaki predlogi posebej
zmanjšuje tveganje, da bi bila kdaj oblika neusklajena med zasloni.

**Zavrnjene možnosti:** Oblikovanje datuma neposredno v vsaki predlogi
(zavrnjeno — podvajanje kode, tvegano za neskladnost).

**Za katero poglavje:** 4.4 (vmesnik).

## 2026-08-19 — Barvna paleta grafa (črte simptomov)

**Vprašanje:** Prvotna paleta barv za črte posameznih simptomov je vključevala
oranžno-rdečo in rožnato, ki sta se vizualno prekrivali z rdečim ozadjem
območja "huda (7–10)" jakosti.

**Odločitev:** Paleta črt je zamenjana z modro, vijolično, oranžno, temno
zeleno in rjavo (`static/graf.js`) — namenoma brez rdeče/rožnate odtenkov.
Dodana je tudi oznaka osi y "Jakost (0–10)".

**Utemeljitev:** N2 in F6 (razumljiv prikaz z označenimi območji jakosti) —
če se barva črte in barva ozadja ujemata, uporabnik ne more zanesljivo
razbrati, kje je meja območja in kje poteka črta simptoma. Ločena barvna
skupina za črte je nujna za berljivost grafa.

**Zavrnjene možnosti:** Obdržati prvotno paleto (zavrnjeno zaradi vizualnega
prekrivanja z ozadjem, opaženega pri pregledu vmesnika).

**Za katero poglavje:** 4.4 (vmesnik).

## 2026-08-19 — Brisanje vrste simptoma in terapije je RESTRICT, ne kaskadno

**Vprašanje:** kaj je bilo treba odločiti

Kako naj se aplikacija odzove, če uporabnik poskuša izbrisati vrsto simptoma
(ali terapijo), ki ima obstoječe zapise?

**Odločitev:** kaj je bilo izbrano

Brisanje vrste simptoma z obstoječimi zapisi je zavrnjeno (RESTRICT), ne
kaskadno. Enako pravilo velja za terapijo z obstoječimi zapisi jemanja —
brisanje je dodano kot pravo brisanje (ne le "Ukini"), a prav tako zavrnjeno,
če terapija ima zapise v `zapis_terapije`. Sporočilo o zavrnitvi navede točno
število obstoječih zapisov.

**Utemeljitev:** zakaj; kadar je mogoče, poveži z zahtevo (F1–F8, N1–N6) ali
z ugotovitvijo iz poglavja 3

Preprečitev nenamerne izgube zdravstvenih podatkov; izguba mora biti
posledica zavestnega dejanja uporabnika. Povezano z N6 in z načelom
privzetega varstva podatkov (člen 25 GDPR).

**Zavrnjene možnosti:** kaj še je bilo v igri in zakaj ni bilo izbrano

ON DELETE CASCADE — zavrnjena, ker bi uporabnik lahko tiho izgubil mesece
zapisov.

**Za katero poglavje:** 4.3.2 in 4.5.
