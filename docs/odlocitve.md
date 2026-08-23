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
- Varstvo osebnih podatkov: pri nalaganju skripte s CDN bi ponudnik ob vsakem
  obisku strani prejel IP naslov uporabnika, čas dostopa in glavo referer,
  torej podatek o tem, katero stran obiskuje. Ker gre za aplikacijo za
  spremljanje zdravstvenega stanja, bi to tretji osebi razkrilo dejstvo, da
  uporabnik tako aplikacijo uporablja. To ni skladno z zahtevo po vgrajenem
  varstvu podatkov (Uredba (EU) 2016/679, člen 25).
- Zanesljivost: zunanji strežnik je dodatna točka odpovedi, neodvisna od
  strežnika aplikacije. Dostop do zunanjih domen je v zdravstvenih ustanovah
  pogosto omejen, kar bi pomenilo okrnjeno delovanje kljub delujočemu
  strežniku.
- Varnost dobavne verige: sprememba datoteke na tujem strežniku bi pomenila
  spremembo kode, ki se izvede v uporabnikovem brskalniku, brez vednosti
  razvijalca.
- Praktični razlog pri prototipu: ker prototip deluje lokalno, lokalno
  shranjene datoteke omogočajo predstavitev brez internetne povezave.

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

## 2026-08-20 — Barvna paleta grafa popravljena po mentorjevi pripombi

**Vprašanje:** Mentor je pri pregledu vmesnika opozoril, da sta modra in
vijolična v paleti črt grafa (izbrani 2026-08-19) preveč podobni, in
predlagal paleto z močnejšim medsebojnim kontrastom ter preverbo za barvno
slepoto.

**Odločitev:** Paleta črt (`static/graf.js`) je zamenjana s temno modro,
svetlo zelano, oranžno, rjavo in temno sivo — brez vijolične. Vsak niz ima
poleg barve tudi svojo obliko točke (krog, kvadrat, trikotnik, zasukan
kvadrat, zasukan križec; vgrajeni stili Chart.js).

**Utemeljitev:** Izhaja iz mentorjeve pripombe pri pregledu vmesnika (slika
1). Ločevanje po barvi in obliki hkrati je standardna praksa za dostopnost
pri barvni slepoti — če se dve barvi zlijeta, oblika točke ostane
razločljiva. Povezano z N2 in F6.

**Zavrnjene možnosti:** Prejšnja paleta z modro/vijolično (zavrnjena, ker sta
si preblizu, tudi ne le pri barvni slepoti).

**Za katero poglavje:** 4.4 (vmesnik).

## 2026-08-20 — Dosledna slovenska oblika datuma, dopolnjeno po mentorjevi pripombi

**Vprašanje:** Mentor je pri pregledu (sliki 1 in 5) preveril, ali so vsi
izpisi datumov v slovenski obliki, ne le tisti, popravljeni 2026-08-19.

**Odločitev:** Po ponovnem pregledu vse kode je potrjeno, da so vsi izpisi
uporabniku (tabele, naslovi, oznake grafa, sporočila) že dosledno v obliki
"19. 8. 2026" prek `oblikuj_datum_sl`. Edina mesta s surovo ISO obliko so
`value` atributi `<input type="date">` polj, kar je pravilno in namerno (glej
naslednji vnos).

**Utemeljitev:** Izhaja iz mentorjeve pripombe pri pregledu vmesnika.
Potrditev obstoječe rešitve po neodvisnem pregledu je vredna zapisa, ker
dokazuje, da je bila prvotna odločitev (2026-08-19) dosledno izvedena, ne le
deklarirana.

**Za katero poglavje:** 4.4 (vmesnik).

## 2026-08-20 — Polja `<input type="date">` ostanejo native, brez jQuery UI

**Vprašanje:** Mentor je opozoril, da `<input type="date">` prikaže datum v
obliki, ki jo določa jezik brskalnika, ne aplikacija, in predlagal jQuery UI
za enoten videz.

**Odločitev:** Native `<input type="date">` ostaja nespremenjen. jQuery UI ni
uveden.

**Utemeljitev:** Izhaja iz mentorjeve pripombe pri pregledu vmesnika. Enaka
logika kot pri odločitvi o Chart.js (2026-08-18): jQuery UI bi pomenil dve
novi zunanji odvisnosti (jQuery + jQuery UI), dodatno površino za varnostne
ranljivosti v dobavni verigi in vzdrževalno breme, ki presega korist v
prototipu enega polja. Native element je preizkušen, dostopen (tipkovnica,
bralniki zaslona, mobilni koledarski vnosnik) in ne zahteva lastne
JavaScript kode. Omejitev (prikaz odvisen od jezika brskalnika/OS) je
sprejeta kot znana pomanjkljivost, ne prikrita.

**Zavrnjene možnosti:**
- jQuery UI Datepicker (mentorjev predlog) — zavrnjen zaradi novih zunanjih
  odvisnosti, v nasprotju z "novih odvisnosti ne dodajaj brez dogovora".
- Lastna izbira datuma v čistem JavaScriptu, brez knjižnic — zavrnjena kot
  nesorazmerno velik poseg (nova, netrivialna komponenta za vzdrževanje) za
  korist, ki je zgolj kozmetična.
- Besedilno polje z masko `dd. mm. llll` — zavrnjeno, ker bi izgubili native
  mobilni koledarski vnosnik in del vgrajene dostopnosti, spet za zgolj
  kozmetično korist.

**Za katero poglavje:** 4.3 (tehnološka zasnova), 4.5 (varstvo podatkov — brez
nepotrebnih zunanjih odvisnosti), 5 (razprava, omejitve).

## 2026-08-20 — Ikonska dejanja v tabelah po mentorjevi pripombi

**Vprašanje:** Mentor je predlagal, naj bodo dejanja v tabelah (Vzeto, Uredi,
Izbriši/Ukini) ikone z besedilnim namigom, dostopne tudi s tipkovnico, brez
ikonskih pisav ali CDN.

**Odločitev:** Dodane so štiri ročno izdelane vgrajene SVG ikone (kapsula,
svinčnik, koš, obnovi) prek Jinja makrov (`templates/_ikone.html`). Vsak
ikonski gumb ima `aria-label` in CSS namig, ki se prikaže na `:hover` in
`:focus-visible` (torej tudi pri navigaciji s tipkovnico). Vsi ikonski gumbi
so veliki 44×44 px.

**Utemeljitev:** Izhaja iz mentorjeve pripombe pri pregledu vmesnika (sliki 2
in 4). Koš je uporabljen tako za "Izbriši" kot za "Ukini" (mentor ju je v
pripombi združil), za "Ponovno aktiviraj" pa ločena ikona za obnovitev, ker
bi koš pri tem dejanju zavajal (ne gre za uničenje podatkov). Velikost 44×44
px sledi splošnemu priporočilu za najmanjšo dotikalno površino na mobilnih
napravah.

**Zavrnjene možnosti:** Ikonska pisava (npr. Font Awesome) — zavrnjena, ker
bi pomenila novo zunanjo odvisnost (ali lokalno datoteko s celotnim naborom
neuporabljenih ikon). Zunanja SVG ikonska knjižnica prek CDN — zavrnjena iz
istega razloga kot pri Chart.js (brez zunanjih storitev).

**Za katero poglavje:** 4.4 (vmesnik).

## 2026-08-20 — Beleženje časa (ne le datuma) pri jemanju terapije

**Vprašanje:** Mentor je predlagal, naj se namesto gumba "Vzeto" uporabi
vnosno polje s številom vzetih odmerkov na dan, shranjeno ob dogodku `blur`.
Po analizi (glej razpravo v seji) je bilo namesto tega odločeno, da se ob
kliku na "Vzeto" poleg datuma zabeleži tudi ura.

**Odločitev:** `zapis_terapije.datum` (TEXT, samo datum) je zamenjan z
`zapis_terapije.casovna_znacka` (TEXT, oblika `YYYY-MM-DD HH:MM`), zajeto na
strežniku (`datetime.now()`), ne v brskalniku. Uporabnik lahko uro
posameznega zapisa naknadno uredi ali zapis izbriše na strani "Zgodovina
jemanja terapije". Poizvedbi za "danes vzeto" (nadzorna plošča, seznam
terapij) filtrirata po datumskem delu časovne znamke (`substr(...,1,10)`), ne
po celotni vrednosti. Ker je šlo za spremembo podatkovnega modela na
razvojni bazi brez pravih uporabniških podatkov, je bila baza ponovno
zgrajena, namesto pisanja enkratnega migracijskega skripta.

**Utemeljitev:** Izhaja iz mentorjeve pripombe o vnosu jemanja terapije.
Mentorjev predlog (število odmerkov na dan) bi spremenil pomen podatka iz
dnevnika posameznih dogodkov jemanja v dnevni seštevek — izgubila bi se
granularnost (točen čas vsakega odmerka) in zanesljivost shranjevanja (dogodek
`blur` je na mobilnih napravah manj zanesljiv kot potrditev s klikom, ki takoj
vrne povratno informacijo o uspehu). Beleženje ure namesto tega ohrani obstoječ
enostaven vzorec (en klik, en zapis), hkrati pa doda natančnejši podatek, ki je
pri terapijah pogosto pomemben (npr. odmerek pred obrokom, na določen
interval) — povezano z razširjeno F4.

**Izbira polja — `casovna_znacka` proti ločenima `datum` in `cas`:** Izbran
je en sam stolpec `casovna_znacka`, ne dva ločena. SQLite shrani TEXT kot
niz ne glede na "tip" stolpca, zato ločena stolpca ne bi prinesla nobene
prednosti pri preverjanju veljavnosti. En sam stolpec z obliko, ki se
leksikografsko razvršča enako kot kronološko (`YYYY-MM-DD HH:MM`), poenostavi
`ORDER BY` (eno polje namesto dveh) in shranjevanje/branje (en `datetime`
objekt na strežniku, brez ročnega sestavljanja/razstavljanja dveh nizov ob
vsaki poizvedbi). Cena je nekoliko manj berljiva poizvedba pri filtriranju
samo po datumskem delu (`substr`), kar je sprejemljivo, ker se to zgodi na
dveh mestih v kodi, dokumentiranih s komentarjem.

**Zavrnjene možnosti:**
- Obstoječe beleženje samo datuma (`datum`, brez ure) — zavrnjeno, ker ne
  zadosti mentorjevi zahtevi po natančnejšem podatku o času jemanja.
- Mentorjev predlog vnosnega polja s številom odmerkov na dan, shranjeno ob
  `blur` — zavrnjen, ker bi spremenil pomen podatka (dogodek → dnevni
  seštevek) in zmanjšal zanesljivost vnosa na mobilnih napravah.
- Ločena stolpca `datum` in `cas` namesto enotne `casovna_znacka` — zavrnjena
  zaradi nepotrebne dodatne kompleksnosti pri razvrščanju in sestavljanju
  vrednosti, brez jasne koristi v SQLite.

**Za katero poglavje:** 4.3.2 (podatkovni model), 4.4 (vmesnik), 5 (razprava
— utemeljitev odstopanja od mentorjevega prvotnega predloga).

## 2026-08-21 — Prikaz datumov poenoten z vnosnim poljem prek Intl.DateTimeFormat

**Vprašanje:** Naši lastni izpisi datumov (tabele, povzetek, graf) so bili
fiksno v slovenski obliki, medtem ko `<input type="date">` prikaže obliko
glede na jezik/OS brskalnika (odločitev 2026-08-20). Avtor je želel, da so
vsi izpisi na strani medsebojno usklajeni z isto (brskalnikovo) obliko, ne
da je en del strani fiksno slovenski, drugi pa prilagodljiv.

**Odločitev:** Strežnik še vedno izriše privzeto slovensko obliko (deluje
brez JavaScripta). Nova skripta `static/datumi.js` ob nalaganju strani
prepiše elemente z atributom `data-datum`/`data-casovna-znacka` v obliko, ki
jo vrne `Intl.DateTimeFormat()` brez izrecne lokacije (uporabi privzeto
jezikovno/sistemsko nastavitev brskalnika — enako, kar uporablja
`<input type="date">`). Enaka logika je vgrajena v `static/graf.js` za
oznake na osi x grafa (Chart.js tako ali tako zahteva JavaScript, zato tam
ni potrebe po ne-JS različici). Logika "letnica samo na prvi oznaki/ob
spremembi leta" (odločitev 2026-08-20) je ohranjena, le prestavljena iz
Pythona v JavaScript.

**Utemeljitev:** N2 (razumljiv, dosleden vmesnik) — če je vnosno polje
prikazano npr. v ameriški obliki (7/22/2026), a preostale tabele v slovenski
(22. 7. 2026), je to znotraj iste strani neskladno in zavajajoče. `Intl`
je vgrajen del JavaScripta v vseh sodobnih brskalnikih, zato ne uvaja nove
zunanje odvisnosti. Postopno izboljšanje (progressive enhancement) —
osnovna, vedno berljiva slovenska oblika ostane brez JavaScripta, prilagojena
oblika se doda le, če je JavaScript na voljo — zato stran ne postane
neuporabna, če je JavaScript izklopljen.

**Zavrnjene možnosti:**
- Fiksna slovenska oblika povsod, vključno z vnosnim poljem (zahtevalo bi
  zamenjavo native `<input type="date">` z lastnim poljem — možnost, ki je
  bila pri odločitvi 2026-08-20 že enkrat zavrnjena).
- Zaznavanje jezika na strežniku prek glave `Accept-Language` — zavrnjeno,
  ker ne odraža nujno enake nastavitve, kot jo za prikaz uporablja
  `<input type="date">` (ta sledi jeziku/regiji operacijskega sistema, ne
  nujno jeziku brskalnika).

**Za katero poglavje:** 4.4 (vmesnik).

## 2026-08-24 — Povzetek vključuje tudi zgodovino jemanja terapij

**Vprašanje:** Ali sodi prikaz zgodovine jemanja terapij (datum, ura, naziv)
za izbrano obdobje v zaslon "Povzetek", ali bi to že pomenilo razširitev
zahteve F7?

**Odločitev:** Na zaslon Povzetek je dodana tabela "Zapisi jemanja terapij"
za izbrano obdobje — enak vzorec (tabela, tiskalni slog, prilagodljiva
oblika datuma) kot že obstoječa tabela "Zapisi simptomov".

**Utemeljitev:** F7 se glasi "uporabnik prikaže povzetek podatkov za izbrano
obdobje" — ne določa, katerih podatkov. Podatek (`zapis_terapije`) že
obstaja in se že zbira (F4); Povzetek že združuje več vrst podatkov
(simptomi, trenutne terapije), zato je dodatek dosleden z obstoječim
namenom zaslona, ne nova zmožnost. Zdravniku omogoča primerjavo poteka
simptomov z dejanskim jemanjem terapij v istem obdobju (F7 — "potreba po
komunikaciji z zdravstvenim osebjem").

**Zavrnjene možnosti:** Prekrivanje oznak jemanja neposredno na grafu
jakosti simptomov — zavrnjeno, ker bi zahtevalo dodaten Chart.js vtičnik in
bi pri več terapijah/odmerkih na dan graf hitro postal vizualno natrpan (v
nasprotju z N2). Ločena tabela doseže enak namen brez tega tveganja.

**Za katero poglavje:** 4.3.2 (obseg zahteve F7), 4.4 (vmesnik).
