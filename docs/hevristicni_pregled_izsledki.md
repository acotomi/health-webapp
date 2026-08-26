# Sistematičen pregled vmesnika — gradivo za hevristično vrednotenje

Pregledana različica: `4578b25`, 2026-08-26
Pregled opravil: Claude Code (statični pregled kode in predlog)
Namen: gradivo za hevristično vrednotenje, ki ga opravi avtor

## Povzetek

Pregledanih je bilo `app.py` (vse poti), vseh 17 predlog v `templates/`,
`static/style.css`, vse ročno pisane skripte v `static/` (`datumi.js`,
`geslo.js`, `graf.js`, `vec-izbor.js`; `chart.js` je nespremenjena knjižnica
in ni bila vsebinsko pregledana), `SPECIFIKACIJA.md` in `docs/odlocitve.md`.
Pregled je izključno statičen — ničesar v aplikaciji nisem zagnal.

Najdenih je **21 kandidatov za ugotovitev**, razporejenih po vseh osmih
hevristikah (2–4 na hevristiko). Največ jih je pri **H5 (preprečevanje
napak)** in **H8 (pomoč in navodila)** — predvsem zato, ker je aplikacija na
več mestih zgradila dvojno zaščito (odjemalec + strežnik) za en tok podatkov
(nov zapis simptoma), enake zaščite pa ni dosledno ponovila pri sorodnem toku
(urejanje obstoječega zapisa). En sam konkreten vzorec — nadzorna plošča
(`domov.html`) ima drugačno mesto izpisa obvestil kot vsi drugi zasloni — se
ponovi pri dveh hevristikah (H1 in H4), ker gre hkrati za vprašanje vidnosti
stanja in za vprašanje doslednosti.

Precej pregledane kode kaže namerno, dokumentirano odločanje (`docs/odlocitve.md`
ima 14 vnosov) — več kandidatov spodaj je zato označenih kot "zahteva
človekovo presojo, ali je odstopanje namerno", ne kot očitna napaka. Nobenega
mesta z odvečnim poljem glede na `SPECIFIKACIJA.md` nisem našel, razen enega
mejnega primera (`potrdi_geslo`, glej H7). Varnostni mehanizmi (CSRF, lastništvo
pri vsaki poizvedbi, zgoščena gesla) so bili pri statičnem branju dosledni na
vseh preverjenih mestih.

## Hevristika 1 — Prikaz stanja sistema

**Kaj je bilo preverjeno:** ali uporabnik po dejanju (dodajanje, urejanje,
brisanje, "vzeto") dobi vidno povratno informacijo; ali je razvidno, kje v
aplikaciji je uporabnik; ali je stanje podatkov (npr. terapija vzeta danes)
jasno prikazano.

**Dokazi:**
- Flash sporočila se privzeto izpišejo na vrhu vsebine vsake strani prek
  `{% block obvestila %}{{ prikazi_obvestila() }}{% endblock %}`
  (`templates/base.html:55`).
- Vsaka akcija v `app.py`, ki spremeni podatke, pokliče `flash(..., "uspeh")`
  ali `flash(..., "napaka")` pred preusmeritvijo, npr. `app.py:273` (dodan
  simptom), `app.py:403` (shranjen zapis), `app.py:555` (zabeleženo jemanje),
  `app.py:668`/`app.py:817` (množično brisanje).
- Trenutna razdelek v navigaciji je označen z razredom `aktivna` in
  `aria-current="page"` glede na `request.endpoint` (`templates/base.html:15-49`).
- Stanje jemanja terapije za danes je neposredno prikazano na dveh mestih:
  stolpec "Danes vzeto" na nadzorni plošči (`templates/domov.html:50-54`,
  z urami jemanja) in na seznamu terapij (`templates/terapije.html:29`).
- Prijavljeno uporabniško ime je stalno vidno v glavi strani
  (`templates/base.html:31-34`).

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 1.1 | Nadzorna plošča prepiše `block obvestila` na prazno vsebino in obvestila izriše ročno šele znotraj razdelka "Današnje terapije", pod grafom — ne na vrhu strani kot povsod drugod. Uporabnik, ki doda zapis simptoma (preusmeritev nazaj na `domov`), lahko sporočilo "Zapis je shranjen" spregleda, če razdelka ne skrola do njega. | Nadzorna plošča | `templates/domov.html:7`, `templates/domov.html:34` (proti `templates/base.html:55`) | da |
| 1.2 | Isto dejanje ("Vzeto") ima dve različni mesti prikaza povratne informacije, odvisno od tega, s katerega zaslona je bilo sproženo: iz nadzorne plošče se sporočilo izriše znotraj razdelka (glej 1.1), iz seznama Terapij pa na vrhu strani (privzeti blok). | Nadzorna plošča / Seznam terapij | `app.py:557-559` (dve preusmeritveni tarči), `templates/domov.html:34` proti `templates/base.html:55` | da |
| 1.3 | Sporočilo "Izbrisanih 0 zapisov." pri množičnem brisanju (če noben izbran ID po strežniškem preverjanju lastništva ne ustreza) ne pojasni, zakaj je bilo izbrisanih manj zapisov, kot jih je uporabnik označil. | Zgodovina / Zgodovina jemanja terapije | `app.py:656-668`, `app.py:807-817`, funkcija `stevilka_zapisov` (`app.py:98-106`) | da (nejasno, ali je ta primer prek vmesnika sploh dosegljiv, ker checkboxi kažejo le lastne zapise) |

**Česa iz kode ni mogoče presoditi:** ali je sporočilo na nadzorni plošči (1.1)
v resnici pogosto zunaj vidnega polja brez skrolanja (odvisno od velikosti
zaslona in dolžine grafa) — to zahteva dejanski preizkus na namiznem in
mobilnem zaslonu.

## Hevristika 2 — Skladnost z resničnim svetom

**Kaj je bilo preverjeno:** ali so izrazi razumljivi bolniku brez računalniškega
predznanja; ali so lestvice in enote pojasnjene; ali so datumi in ure v domači
obliki.

**Dokazi:**
- Barvna območja jakosti so pojasnjena z besedilom v naravnem jeziku: "zeleno
  = blaga (0–3), rumeno = zmerna (4–6), rdeče = huda (7–10)"
  (`templates/domov.html:24-26`, ponovljeno na `templates/povzetek.html:37-39`).
- Datumi se prikažejo v slovenski obliki "19. 8. 2026" prek filtra `datum_sl`
  (`app.py:22-28`), časovne značke kot "19. 8. 2026 ob 14:30" prek
  `casovna_znacka_sl` (`app.py:31-38`) — dokumentirano v
  `docs/odlocitve.md:135-155` in `docs/odlocitve.md:228-244`.
- Zahteve za geslo so opisane v razumljivem jeziku s primerom: "Vsaj 8 znakov,
  ena velika črka in en poseben znak (npr. Geslo123!)."
  (`templates/registracija.html:24`, ujema se z `app.py:226-229`).
- Slovnično pravilne oblike besedil glede na število zapisov
  (`stevilo_zapisov_besedilo`, `app.py:87-95`; `stevilka_zapisov`,
  `app.py:98-106`) namesto generičnega "X zapis(ov)".

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 2.1 | Oznaka polja "Jakost" na obrazcu za nov zapis pojasni pomen skrajnih vrednosti ("0 = brez, 10 = najhujša"), na obrazcu za urejanje istega podatka pa je skrajšana na "Jakost (0–10)" brez pojasnila pomena. | Nov zapis simptoma / Urejanje zapisa simptoma | `templates/nov_zapis_simptoma.html:22` proti `templates/uredi_zapis_simptoma.html:22` | ne (razvidno iz kode) |
| 2.2 | Napaka pri prijavi ("Napačno uporabniško ime ali geslo.") namerno ne razkrije, kateri del je napačen. | Prijava | `app.py:196-197` | da (varnostno utemeljeno, a nejasno, ali je za ciljno skupino dovolj razumljivo) |
| 2.3 | Polje "Odmerek" nima enote v oznaki, enota je nakazana le v placeholderju ("npr. 400 mg"), ki izgine, ko uporabnik začne tipkati. | Seznam terapij (dodajanje), Urejanje terapije | `templates/terapije.html:85-86` | da |

**Česa iz kode ni mogoče presoditi:** ali so izrazi "jakost", "opomba",
"pogostost", "aktivna/ukinjena" dejansko razumljivi bolniku brez
računalniškega predznanja — to je vprašanje za uporabniško testiranje, ne za
statičen pregled kode.

## Hevristika 3 — Nadzor uporabnika nad postopkom

**Kaj je bilo preverjeno:** ali lahko uporabnik vnos popravi ali izbriše; ali
lahko iz obrazca izstopi brez shranjevanja; ali obstaja možnost razveljavitve
dejanja.

**Dokazi:**
- Vsi zapisi (simptom, terapija, zapis simptoma, zapis jemanja) imajo
  ločeno pot za urejanje in za brisanje: `app.py:285-317` (uredi simptom),
  `app.py:449-478` (uredi terapijo), `app.py:583-619` (uredi zapis jemanja),
  `app.py:713-770` (uredi zapis simptoma).
- Vsi obrazci za urejanje vsebujejo povezavo "Nazaj na ..." za izhod brez
  shranjevanja: `templates/uredi_simptom.html:18`,
  `templates/uredi_terapijo.html:24`, `templates/uredi_zapis_terapije.html:18`,
  `templates/uredi_zapis_simptoma.html:41`.
- Vsako nepovratno dejanje (izbris) zahteva potrditev prek `confirm()`:
  `templates/simptomi.html:27`, `templates/terapije.html:56`,
  `templates/zgodovina_terapije.html:13,43`, `templates/zgodovina.html:33,66`.
- Brisanje vrste simptoma/terapije z obstoječimi zapisi je zavrnjeno
  (RESTRICT), da uporabnik nehote ne izgubi zgodovine —
  `app.py:332-347`, `app.py:493-502`, utemeljeno v
  `docs/odlocitve.md:177-204`.

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 3.1 | Obrazec "Nov zapis simptoma" nima povezave za izstop brez shranjevanja, v nasprotju z vsemi drugimi obrazci za urejanje (glej Dokazi zgoraj), ki tako povezavo imajo. | Nov zapis simptoma | `templates/nov_zapis_simptoma.html:9-39` (ni povezave "Nazaj") | ne (razvidno iz kode) |
| 3.2 | Dejanje "Vzeto" nima ne potrditve ne neposredne povezave do mesta, kjer bi uporabnik napačen klik takoj popravil (izbris zapisa je mogoč šele prek ločenega obiska Zgodovine jemanja terapije). | Nadzorna plošča / Seznam terapij | `app.py:538-559` (ni potrditve, ni povezave na `zgodovina_terapije` v sporočilu) | da (dejanje je namenoma enokliktno; vprašanje je, ali je odsotnost neposredne poti do popravka sprejemljiva) |

**Česa iz kode ni mogoče presoditi:** ali uporabnik dejansko ve, da lahko
napačen klik "Vzeto" popravi prek "Zgodovina" pri terapiji — to je vprašanje
razpoznavnosti povezave "Zgodovina" (`templates/terapije.html:46`), kar
zahteva preizkus z uporabnikom.

## Hevristika 4 — Doslednost

**Kaj je bilo preverjeno:** ali je isto dejanje na vseh zaslonih predstavljeno
enako (ikone, gumbi, poimenovanja, razporeditev stolpcev, oblika sporočil).

**Dokazi:**
- Ikone dejanj so izločene v skupne makre in dosledno ponovno uporabljene:
  `templates/_ikone.html` (svinčnik = uredi, koš = izbriši/ukini, kapsula =
  vzeto, obnovi = ponovno aktiviraj), uporabljene na
  `templates/domov.html:62`, `templates/simptomi.html:23,30`,
  `templates/terapije.html:37,43,51,59`,
  `templates/zgodovina_terapije.html:38,46`, `templates/zgodovina.html:62,69`.
  Odločitev dokumentirana v `docs/odlocitve.md:277-301`.
- Poimenovanje gumbov je dosledno ločeno: "Dodaj" za nov vnos vrste
  (`templates/simptomi.html:53`, `templates/terapije.html:94`), "Shrani" za
  urejanje obstoječega zapisa (`templates/uredi_simptom.html:15`,
  `templates/uredi_terapijo.html:21`, `templates/uredi_zapis_terapije.html:15`,
  `templates/uredi_zapis_simptoma.html:38`, `templates/nov_zapis_simptoma.html:38`).
- Besedilo potrditvenega okna sledi enakemu vzorcu "Izbrišete ... ?" na vseh
  štirih mestih brisanja (glej Dokazi pri H3).

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 4.1 | Mesto izpisa obvestil na nadzorni plošči odstopa od vseh drugih zaslonov (isto kot 1.1, tu z vidika doslednosti, ne vidnosti). | Nadzorna plošča | `templates/domov.html:7,34` proti `templates/base.html:55` | ne (odstopanje je v kodi nedvoumno) |
| 4.2 | Besedilo oznake polja "Jakost" ni dosledno med obrazcem za nov vnos in obrazcem za urejanje (isto kot 2.1, tu z vidika doslednosti). | Nov zapis simptoma / Urejanje zapisa simptoma | `templates/nov_zapis_simptoma.html:22` proti `templates/uredi_zapis_simptoma.html:22` | ne |
| 4.3 | Dve prazni stanji na isti strani (nadzorna plošča) sta obravnavani različno: prazno stanje za simptome je nad njim opremljeno z vidnim gumbom "Nov zapis simptoma" (velja ne glede na prazno stanje), prazno stanje za terapije pa nima nobenega enakovrednega gumba ali povezave v svoji bližini. | Nadzorna plošča | `templates/domov.html:13-15` (gumb, ločen od pogojnega bloka), `templates/domov.html:28` proti `templates/domov.html:74` | da |

**Česa iz kode ni mogoče presoditi:** ali sta dve različni obliki prikaza
terapij (polna tabela na `templates/terapije.html:11-21` s 6 stolpci proti
skrajšani tabeli na `templates/domov.html:37-39` z 2 stolpcema + podrobnostjo
v celici) v praksi zaznani kot dosledni ali kot dve različni komponenti — to
je vprašanje vizualne presoje.

## Hevristika 5 — Preprečevanje napak

**Kaj je bilo preverjeno:** ali aplikacija neveljaven vnos prepreči, preden se
zgodi; ali zahteva potrditev pred nepovratnimi dejanji; ali preverjanje poteka
tudi na strežniku.

**Dokazi:**
- Jakost simptoma je omejena na treh ravneh: drsnik `min="0" max="10"` na
  odjemalcu (`templates/nov_zapis_simptoma.html:23`), strežniško preverjanje
  `0 <= jakost <= 10` (`app.py:386`, `app.py:747`) in `CHECK` v shemi baze
  (`schema.sql:22`).
- Datum novega zapisa simptoma je omejen na treh ravneh: `max="{{ danes }}"`
  na odjemalcu (`templates/nov_zapis_simptoma.html:13`), strežniško
  preverjanje `izbran_datum > danes` (`app.py:394-395`).
- CSRF žeton je zahtevan pri vsaki POST zahtevi prek `before_request`
  (`app.py:64-73`) in prisoten kot skrito polje v vsakem `<form method="post">`
  po celotni aplikaciji.
- Podvojen naziv simptoma je preprečen ob dodajanju (`app.py:262-266`) in
  urejanju (`app.py:303-307`).
- Uporabniško ime mora biti edinstveno na dveh ravneh: predhodna poizvedba
  (`app.py:262-266` za simptom, analogno za uporabnika `app.py:191-193` prek
  `UNIQUE` v `schema.sql:6`) in prestrezanje `sqlite3.IntegrityError`
  (`app.py:241-242`).
- Lastništvo se preveri pri prav vsaki poizvedbi, ki bere ali spreminja
  zapis (preverjeno na vseh 13 poteh v `app.py`, ki dostopajo do podatkov
  posameznega uporabnika, npr. `app.py:289-292`, `app.py:453-456`,
  `app.py:589-593`, `app.py:717-724`); množično brisanje ponovno preveri
  lastništvo znotraj same `DELETE` poizvedbe (`app.py:656-665`,
  `app.py:806-813`), ne zaupa seznamu ID-jev iz obrazca.

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 5.1 | Pri urejanju obstoječega zapisa simptoma zaščita pred prihodnjim datumom ne obstaja — ne kot `max` na vnosnem polju, ne kot strežniško preverjanje (za razliko od novega zapisa, glej Dokazi zgoraj). | Urejanje zapisa simptoma | `templates/uredi_zapis_simptoma.html:20` (brez `max`), `app.py:750-753` (preveri le veljavnost oblike datuma, ne zgornje meje) | ne (odsotnost je razvidna iz kode; namernost odločitve zahteva avtorja) |
| 5.2 | Pri urejanju zapisa jemanja terapije ni nobene zaščite pred vnosom prihodnjega datuma/ure — niti na odjemalcu niti na strežniku — medtem ko je izvirni zapis "Vzeto" vedno zajet s strežniškim časom. | Urejanje zapisa jemanja | `templates/uredi_zapis_terapije.html:13` (brez `max`), `app.py:600-614` (preveri le obliko vnosa), proti `app.py:552` (`datetime.now()` pri izvirnem zapisu) | ne |
| 5.3 | Preverjanje podvojenega naziva obstaja pri simptomih (dodajanje in urejanje), ne pa pri terapijah — dve terapiji z enakim nazivom je mogoče ustvariti brez opozorila. | Seznam terapij (dodajanje), Urejanje terapije | `app.py:416-431` (dodajanje terapije, brez preverjanja podvojenosti), `app.py:462-478` (urejanje terapije, brez preverjanja podvojenosti), proti `app.py:262-266`, `app.py:303-307` (simptom) | da (morda namerno, ker je več terapij z enakim imenom lahko smiselnih, npr. dva različna recepta) |

**Česa iz kode ni mogoče presoditi:** nič posebnega — vsa zgornja opažanja so
neposredno razvidna iz kode; edino vprašanje je namernost odstopanj, kar je
avtorjeva presoja, ne vprašanje uporabniške izkušnje.

## Hevristika 6 — Prilagodljivost in učinkovitost uporabe

**Kaj je bilo preverjeno:** koliko korakov zahteva pogosto opravilo; ali
obstajajo bližnjice, privzete vrednosti, filtri, skupinska dejanja.

**Dokazi:**
- Beleženje jemanja terapije je en klik brez dodatnih polj
  (`app.py:538-559`, gumb `templates/terapije.html:33-40` in
  `templates/domov.html:58-65`).
- Množično brisanje s potrditvenimi polji in "izberi vse" je na voljo na
  Zgodovini in Zgodovini jemanja terapije (`static/vec-izbor.js`,
  `templates/zgodovina.html:32-35,40,52`,
  `templates/zgodovina_terapije.html:11-15,20,29`), dokumentirano kot
  namerna razširitev po mentorjevem predlogu (`docs/odlocitve.md:464-488`).
- Vrednosti filtra (obdobje, simptom) se ob ponovnem prikazu obrazca ohranijo
  iz parametrov poizvedbe (`templates/zgodovina.html:12,16,23`,
  `templates/povzetek.html:16,20`) — uporabnik ne izgubi nastavljenega filtra.
- Štirje koraki namesto treh na obrazcu za nov zapis simptoma so zavestno
  utemeljena izjema od N3, dokumentirana v `SPECIFIKACIJA.md:30-33` in
  `docs/odlocitve.md:490-513`.

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 6.1 | Zgodovina ima filter po simptomu poleg filtra po obdobju, Povzetek pa samo filter po obdobju — enaka zmožnost ni na voljo na obeh podobnih pregledovalnih zaslonih. | Zgodovina / Povzetek | `templates/zgodovina.html:9-29` proti `templates/povzetek.html:13-24` | da (Povzetek je morda namenoma celosten pregled za zdravnika, brez filtriranja) |
| 6.2 | Drsnik jakosti pri novem zapisu ima privzeto vrednost 5 (sredina lestvice), ne prazne/neizbrane vrednosti — prihrani korak, če je vrednost želena, a tvega, da uporabnik pomotoma shrani jakost 5, ne da bi drsnik sploh premaknil. | Nov zapis simptoma | `templates/nov_zapis_simptoma.html:23` (`value="5"`) | da |

**Česa iz kode ni mogoče presoditi:** ali uporabniki v praksi opazijo, da
morajo drsnik jakosti premakniti, tudi če je njihova dejanska jakost blizu
privzete vrednosti 5 — to zahteva preizkus.

## Hevristika 7 — Oblikovna zmernost

**Kaj je bilo preverjeno:** ali je na zaslonih kaj, kar ne služi nobeni
zahtevi iz `SPECIFIKACIJA.md`; ali je količina prikazanega primerna.

**Dokazi:**
- Vsa vnosna polja in stolpci tabel ustrezajo poljem podatkovnega modela iz
  `SPECIFIKACIJA.md`, poglavje 3: `simptom.naziv`
  (`templates/simptomi.html:19,50`), `terapija.naziv/odmerek/pogostost/aktivna`
  (`templates/terapije.html:14-18`), `zapis_simptoma.datum/jakost/opomba`
  (`templates/zgodovina.html:41-44`), `zapis_terapije.casovna_znacka`
  (`templates/zgodovina_terapije.html:21`). Nobenega stolpca ali polja brez
  ustrezne vrstice v podatkovnem modelu nisem našel.
- Ikone dejanj so namensko izdelane za obstoječa dejanja, ne dekorativne
  (`templates/_ikone.html:1-2`, komentar pojasnjuje namen).
- CSS za tisk skrije navigacijo in obrazce, ohrani le vsebino povzetka
  (`static/style.css:774-830`, razred `.ne-tiskaj` na
  `templates/povzetek.html:13,26`) — neposredno podpira F7 ("primerno za
  tiskanje").

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 7.1 | Polje "Potrdi geslo" na registraciji ni del podatkovnega modela niti izrecno navedeno v `SPECIFIKACIJA.md` pri F1 — gre za UX-varovalko pred tipkarsko napako, ki se ne shranjuje, zato po strogi črki N6 ("zbiraj čim manj podatkov") ni nova zbirka podatka, je pa dodatno polje na obrazcu brez lastne vrstice v specifikaciji. | Registracija | `templates/registracija.html:26-32`, ni ustrezne vrstice v `SPECIFIKACIJA.md` (primerjaj poglavje 1 in 3) | da |

**Česa iz kode ni mogoče presoditi:** splošna vizualna gostota strani
(razmiki, velikost pisave, količina besedila na zaslonu naenkrat) — to je
vprašanje vizualne presoje ob dejanskem ogledu zaslonov, ne statičnega branja
CSS.

## Hevristika 8 — Pomoč in navodila

**Kaj je bilo preverjeno:** ali uporabnik ob prvem obisku ve, kaj naj stori;
ali so sporočila o napakah razumljiva in povedo, kako napako odpraviti; ali
obstajajo pojasnila tam, kjer so potrebna.

**Dokazi:**
- Sporočilo o zahtevah za geslo vključuje konkreten primer ("npr. Geslo123!")
  na dveh mestih: statično na obrazcu (`templates/registracija.html:24`) in
  v sporočilu o napaki (`app.py:226-229`, uporablja isto konstanto
  `PRIMER_VELJAVNEGA_GESLA`, `app.py:50`).
- Sporočilo o zavrnjenem brisanju simptoma z obstoječimi zapisi pojasni
  natančen vzrok (število zapisov) in ponudi neposredno povezavo do rešitve
  (filtrirana Zgodovina): `app.py:341-347`, zgrajeno prek `Markup()` s
  komentarjem, ki pojasni, zakaj je to edino mesto brez samodejnega ubega HTML.
- Polji "Odmerek" in "Pogostost" imata namigovalni `placeholder` ("npr. 400
  mg", "npr. 2-krat dnevno") kot obliko vgrajene pomoči
  (`templates/terapije.html:81,86,91`).
- Prazno stanje pri manjkajočih podatkih je povsod prisotno (ne prazna
  tabela brez pojasnila): `templates/simptomi.html:42`,
  `templates/terapije.html:71`, `templates/zgodovina.html:84`,
  `templates/zgodovina_terapije.html:61`, `templates/domov.html:28,74`.

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 8.1 | Prazno stanje na nadzorni plošči ("Ni še podatkov za prikaz. Dodajte svoj prvi zapis simptoma.") ne omeni, da je pred prvim zapisom treba najprej dodati vrsto simptoma — to uporabnik izve šele posredno, če klikne "Nov zapis simptoma" in ga aplikacija preusmeri s sporočilom. | Nadzorna plošča | `templates/domov.html:28` proti `app.py:368-370` (dejanska zahteva, razkrita šele ob poskusu) | da |
| 8.2 | Prazno stanje "Nimate aktivnih terapij." nima nobene povezave ali napotka, kako dodati terapijo. | Nadzorna plošča | `templates/domov.html:74` | ne (odsotnost povezave je razvidna iz kode) |
| 8.3 | Splošna napaka 400 ("Zahteva ni veljavna. Poskusite znova.") ne pojasni verjetnega vzroka (npr. potekla seja, obrazec odprt v drugem zavihku, zastarel CSRF žeton) niti ne ponuja povezave nazaj na prejšnjo stran ali prijavo. | katerikoli obrazec ob neveljavnem žetonu | `app.py:909-911`, `templates/napaka.html:7-8` (edina povezava je "Nazaj na začetno stran") | ne |
| 8.4 | Sporočilo o zavrnjenem brisanju terapije z obstoječimi zapisi pojasni vzrok, a za razliko od analognega sporočila pri simptomu (glej Dokazi zgoraj) ne vsebuje neposredne povezave do Zgodovine jemanja, kjer bi uporabnik zapise lahko izbrisal. | Seznam terapij | `app.py:493-502` (navadno besedilo brez `Markup`/povezave) proti `app.py:341-347` (simptom, s povezavo) | ne |

**Česa iz kode ni mogoče presoditi:** ali je odsotnost kakršnegakoli
uvodnega vodiča/pomoči ob prvi prijavi (aplikacija nima ločenega zaslona za
prvi obisk) v praksi problematična za ciljno skupino — to je vprašanje za
uporabniško testiranje, ne za pregled kode; prav tako, ali placeholderji
(8.4, dokazi H8) dejansko delujejo kot zadostna pomoč, ker izginejo ob
tipkanju.

## Pokritost zaslonov

| Zaslon | Preverjene hevristike | Opombe |
|---|---|---|
| Prijava | H1, H2, H5, H6, H8 | Brez zaklepa po neuspelih poskusih — namerna, dokumentirana odločitev (`docs/odlocitve.md:101-133`), ni ponovno ocenjevano tu. |
| Registracija | H2, H5, H6, H7, H8 | Glej 7.1 (potrdi geslo). |
| Nadzorna plošča | H1, H3, H4, H6, H7, H8 | Zaslon z največ kandidati (1.1–1.3, 3.2, 4.1, 4.3, 6.2, 8.1, 8.2). |
| Nov zapis simptoma | H2, H3, H5, H6 | Glej 2.1/4.2 (oznaka jakosti), 3.1 (brez izhoda), 6.2 (privzeta jakost). |
| Seznam simptomov | H3, H5, H7, H8 | Brez novih kandidatov — dosleden vzorec dodajanja/urejanja/brisanja. |
| Urejanje simptoma | H3, H4, H5 | Brez novih kandidatov. |
| Seznam terapij | H1, H2, H3, H4, H5, H8 | Glej 2.3 (enota odmerka), 5.3 (podvojen naziv), 8.4 (sporočilo brez povezave). |
| Urejanje terapije | H3, H4, H5 | Glej 5.3 (podvojen naziv pri urejanju). |
| Zgodovina jemanja terapije | H2, H3, H5, H6 | Glej 5.2 (brez zaščite pred prihodnjim časom pri množičnem pregledu). |
| Urejanje zapisa jemanja | H3, H5 | Glej 5.2 (osrednji dokaz za to ugotovitev). |
| Zgodovina zapisov simptomov | H1, H3, H5, H6 | Glej 6.1 (filter po simptomu prisoten, primerjaj s Povzetkom). |
| Urejanje zapisa simptoma | H2, H4, H5 | Glej 2.1/4.2 (oznaka jakosti), 5.1 (osrednji dokaz). |
| Povzetek | H2, H6, H7 | Glej 6.1 (brez filtra po simptomu); preveril datumsko preverjanje `app.py:827-836`. |

## Vprašanja za avtorja

- Je drugačno mesto izpisa obvestil na nadzorni plošči (1.1/4.1) namerna
  zasnovna odločitev (npr. da so obvestila kontekstualno ob terapijah) ali
  nedokumentirano odstopanje? V `docs/odlocitve.md` ni zapisa o tem.
- Je odsotnost preverjanja prihodnjega datuma/časa pri urejanju obstoječih
  zapisov (5.1, 5.2) namerna (morda ker urejanje predpostavlja, da uporabnik
  že ve, kaj popravlja) ali spregled, ko je bila zaščita dodana samo na poti
  za nov vnos?
- Je odsotnost preverjanja podvojenega naziva pri terapijah (5.3) namerna,
  ker so lahko smiselne dve terapiji z enakim imenom (npr. dva recepta v
  različnih obdobjih), ali bi moralo veljati enako pravilo kot pri simptomih?
- Šteje polje "Potrdi geslo" (7.1) kot dodatno polje, ki bi po N6 potrebovalo
  utemeljitev v `SPECIFIKACIJA.md`, glede na to, da se ne shranjuje?
  Priporočljivo je vsaj eno-vrstično pojasnilo v `docs/odlocitve.md`, če se
  odloči, da polje ostane.
- Je razlika v ponujenih filtrih med Zgodovino (obdobje + simptom) in
  Povzetkom (samo obdobje, 6.1) namerna razlika v namenu zaslona (Povzetek =
  celosten pregled za zdravnika)?

## Predlogi izboljšav (ločeno, niso del vrednotenja)

1. Poenotiti mesto izpisa obvestil (flash) na nadzorni plošči z ostalimi
   zasloni (uporabiti privzeti blok `base.html` namesto ročnega izrisa
   znotraj razdelka).
2. Dodati preverjanje prihodnjega datuma/časa tudi pri urejanju obstoječih
   zapisov (zapis simptoma in zapis jemanja terapije), enako kot pri novem
   vnosu.
3. Dodati neposredno povezavo do Zgodovine jemanja terapije v sporočilu o
   zavrnjenem brisanju terapije, po zgledu enakega sporočila pri simptomu.
4. Dodati povezavo ali napotek "Dodaj terapijo" ob praznem stanju "Nimate
   aktivnih terapij." na nadzorni plošči.
5. Razmisliti o dodajanju povezave "Nazaj" na obrazec "Nov zapis simptoma",
   po zgledu vseh drugih obrazcev za urejanje.
6. Poenotiti besedilo oznake polja "Jakost" med obrazcema za nov vnos in
   urejanje zapisa simptoma.
7. Razmisliti o dodajanju filtra po simptomu tudi na zaslonu Povzetek, po
   zgledu Zgodovine — ali eksplicitno utemeljiti, zakaj ni potreben.
