# Navodilo: sistematičen pregled vmesnika pred hevrističnim vrednotenjem

## Kaj je tvoja naloga

Pripravi **gradivo za hevristično vrednotenje** spletne aplikacije v tem
repozitoriju. Rezultat bo uporabljen v diplomskem delu (Fakulteta za upravo
UL, poglavje 5 — Razprava in evalvacija).

**Zelo pomembno — meja tvoje naloge:** ti zbiraš dokaze in pripravljaš
osnutke ugotovitev. Končno presojo, ali gre za pomanjkljivost, in oceno
resnosti bo opravil avtor sam, ko bo aplikacijo preizkusil. Zato:

- Ne razglašaj ničesar za dokončno ugotovitev. Piši »kandidat za ugotovitev«.
- Za vsako trditev navedi **datoteko in vrstico**, iz katere izhaja.
- Kadar iz kode ni mogoče presoditi (npr. ali je besedilo razumljivo
  bolniku, ali je postavitev pregledna), to **izrecno zapiši** v stolpec
  »zahteva človekovo presojo«. Ne ugibaj.
- Ničesar si ne izmišljaj. Če česa ne najdeš, napiši, da tega ni.

## Česa NE počni

- **Ne spreminjaj kode.** Nobenih popravkov, nobenega refaktoriranja,
  nobenih novih datotek razen izhodne datoteke, navedene spodaj.
- Ne predlagaj izboljšav znotraj tabele. Predloge zberi ločeno na koncu.
- Ne ocenjuj resnosti pomanjkljivosti. To je avtorjeva naloga.

## Kaj pregleduješ

Celoten repozitorij, predvsem:

- `app.py` — poti, obdelava obrazcev, preverjanje vnosa, sporočila
- `templates/` — vsi zasloni, obrazci, tabele, ikone, sporočila
- `static/style.css` — postavitev, odzivnost, tiskanje
- `static/*.js` — graf, oblika datuma, izbira več zapisov, prikaz gesla
- `SPECIFIKACIJA.md` — zahteve F1–F8 in N1–N6
- `docs/odlocitve.md` — utemeljitve sprejetih odločitev

Aplikacijo lahko tudi zaženeš (`python app.py`, nato `python demo_podatki.py`
za podatke), če ti to pomaga preveriti kakšno trditev. Podatkovne baze ne
spreminjaj na noben drug način.

## Hevristike

Uporabi natanko teh osem. Prevzete so iz vira, ki je citiran v diplomskem
delu, zato jih ne preimenuj in jih ne dodajaj.

1. **Prikaz stanja sistema** — ali uporabnik po vsakem dejanju izve, kaj se
   je zgodilo; ali je razvidno, kje v aplikaciji je; ali je stanje podatkov
   (npr. ali je terapija danes že vzeta) jasno prikazano.
2. **Skladnost z resničnim svetom** — ali so izrazi in pojmi razumljivi
   bolniku brez računalniškega predznanja; ali so lestvice in enote
   pojasnjene; ali so datumi in ure v domači obliki.
3. **Nadzor uporabnika nad postopkom** — ali lahko uporabnik vsak vnos
   popravi ali izbriše; ali lahko iz obrazca izstopi brez shranjevanja; ali
   obstaja možnost razveljavitve dejanja.
4. **Doslednost** — ali je isto dejanje na vseh zaslonih predstavljeno
   enako (ikone, gumbi, poimenovanja, razporeditev stolpcev, oblika
   sporočil).
5. **Preprečevanje napak** — ali aplikacija neveljaven vnos prepreči, še
   preden se zgodi; ali zahteva potrditev pred nepovratnimi dejanji; ali
   preverjanje poteka tudi na strežniku, ne le v brskalniku.
6. **Prilagodljivost in učinkovitost uporabe** — koliko korakov zahteva
   pogosto opravilo; ali obstajajo bližnjice, privzete vrednosti, filtri,
   skupinska dejanja.
7. **Oblikovna zmernost** — ali je na zaslonih kaj, kar ne služi nobeni
   zahtevi iz `SPECIFIKACIJA.md`; ali je količina prikazanega primerna.
8. **Pomoč in navodila** — ali uporabnik ob prvem obisku ve, kaj naj stori;
   ali so sporočila o napakah razumljiva in povedo, kako napako odpraviti;
   ali obstajajo pojasnila tam, kjer so potrebna.

## Zasloni, ki jih moraš zajeti

Prijava, registracija, nadzorna plošča, nov zapis simptoma, seznam
simptomov, urejanje simptoma, seznam terapij, urejanje terapije, zgodovina
jemanja terapije, urejanje zapisa jemanja, zgodovina zapisov simptomov,
urejanje zapisa simptoma, povzetek.

Za vsakega navedi, katere hevristike si na njem preveril.

## Izhodna datoteka

Zapiši v `docs/hevristicni_pregled_izsledki.md`. Jezik slovenski.

Zgradba:

```markdown
# Sistematičen pregled vmesnika — gradivo za hevristično vrednotenje

Pregledana različica: <zadnji commit, kratek hash in datum>
Pregled opravil: Claude Code (statični pregled kode in predlog)
Namen: gradivo za hevristično vrednotenje, ki ga opravi avtor

## Povzetek
<10–15 vrstic: kaj je pregledano, koliko kandidatov za ugotovitev je najdenih,
kje se jih največ pojavlja>

## Hevristika 1 — Prikaz stanja sistema

**Kaj je bilo preverjeno:** <konkretno>

**Dokazi:**
- <trditev> (`datoteka:vrstica`)
- <trditev> (`datoteka:vrstica`)

**Kandidati za ugotovitev:**
| # | Opis | Zaslon | Dokaz | Zahteva človekovo presojo |
|---|------|--------|-------|---------------------------|
| 1.1 | ... | ... | `app.py:123` | da / ne |

**Česa iz kode ni mogoče presoditi:** <naštej>

## Hevristika 2 — ...
(enako za vseh osem)

## Pokritost zaslonov
| Zaslon | Preverjene hevristike | Opombe |

## Vprašanja za avtorja
<kar je nejasno ali kar mora preveriti pri uporabi>

## Predlogi izboljšav (ločeno, niso del vrednotenja)
<oštevilčen seznam>
```

## Merilo kakovosti

Pregled je dober, če lahko avtor vsako trditev preveri tako, da odpre
navedeno datoteko in vrstico, in če je jasno razmejeno, kaj je razvidno iz
kode in kaj je treba preizkusiti pri uporabi. Neutemeljena posplošitev je
slabša kot priznanje, da nečesa iz kode ni mogoče presoditi.
