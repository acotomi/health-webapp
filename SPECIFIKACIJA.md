# Specifikacija prototipa

Izhaja iz poglavij 3.2 in 4.2 diplomskega dela. Vsaka zahteva ima izvor v
ugotovljeni pomanjkljivosti obstoječih rešitev.

## 1 Funkcionalne zahteve

| Oznaka | Zahteva | Izhaja iz |
|---|---|---|
| F1 | Uporabnik ustvari račun in se prijavi | ločen dostop do lastnih podatkov |
| F2 | Uporabnik zabeleži simptom (datum, vrsta, jakost 0–10, neobvezna opomba) | obremenjujoč vnos podatkov |
| F3 | Uporabnik vnese in ureja terapije (naziv, odmerek, pogostost) | ločenost simptomov od terapij |
| F4 | Uporabnik zabeleži, da je terapijo vzel | redka funkcija spremljanja terapije |
| F5 | Uporabnik pregleda zgodovino zapisov, omejeno na izbrano obdobje | raznolike potrebe uporabnikov |
| F6 | Aplikacija prikaže gibanje jakosti simptomov v grafični obliki z označenimi območji | redek prikaz podatkov pri spletnih aplikacijah |
| F7 | Uporabnik prikaže povzetek za izbrano obdobje, primeren za prikaz zdravniku, tiskanje ali shranjevanje v PDF | potreba po komunikaciji z zdravstvenim osebjem |
| F8 | Uporabnik ureja in briše lastne zapise | nadzor nad svojimi podatki |

## 2 Nefunkcionalne zahteve

| Oznaka | Zahteva |
|---|---|
| N1 | Dostopno prek brskalnika, brez nameščanja |
| N2 | Vmesnik v slovenščini, berljiva pisava, brez nepotrebnih elementov |
| N3 | Vnos dnevnega zapisa v največ treh korakih |
| N4 | Uporabnik dostopa izključno do lastnih podatkov |
| N5 | Gesla shranjena v zgoščeni obliki |
| N6 | Zbrani le podatki, nujni za delovanje |

## 3 Podatkovni model

Pet tabel. Vrste simptomov so ločena tabela, ker bi prosto besedilno polje
onemogočilo zanesljiv prikaz istega simptoma skozi čas (F6).

### uporabnik
| Polje | Tip | Opis |
|---|---|---|
| id | INTEGER | primarni ključ |
| uporabnisko_ime | TEXT | edinstveno |
| geslo_zgostitev | TEXT | zgoščena vrednost gesla |
| ustvarjen | TEXT | datum in čas nastanka |

### simptom
| Polje | Tip | Opis |
|---|---|---|
| id | INTEGER | primarni ključ |
| uporabnik_id | INTEGER | tuji ključ → uporabnik |
| naziv | TEXT | npr. „glavobol" |

### zapis_simptoma
| Polje | Tip | Opis |
|---|---|---|
| id | INTEGER | primarni ključ |
| simptom_id | INTEGER | tuji ključ → simptom |
| datum | TEXT | datum zapisa |
| jakost | INTEGER | 0–10 |
| opomba | TEXT | neobvezno |

### terapija
| Polje | Tip | Opis |
|---|---|---|
| id | INTEGER | primarni ključ |
| uporabnik_id | INTEGER | tuji ključ → uporabnik |
| naziv | TEXT | ime zdravila ali terapije |
| odmerek | TEXT | npr. „500 mg" |
| pogostost | TEXT | npr. „2-krat dnevno" |
| aktivna | INTEGER | 1 = v uporabi, 0 = ukinjena |

### zapis_terapije
| Polje | Tip | Opis |
|---|---|---|
| id | INTEGER | primarni ključ |
| terapija_id | INTEGER | tuji ključ → terapija |
| datum | TEXT | kdaj je bila vzeta |

**Razmerja:** uporabnik 1:N simptom · simptom 1:N zapis_simptoma ·
uporabnik 1:N terapija · terapija 1:N zapis_terapije

## 4 Zasloni

| Zaslon | Vsebina | Zahteve |
|---|---|---|
| Prijava / registracija | obrazec | F1 |
| Nadzorna plošča | graf zadnjih 30 dni, gumb za nov zapis, današnje terapije | F4, F6 |
| Nov zapis simptoma | izbira simptoma, drsnik jakosti, opomba | F2, N3 |
| Simptomi | seznam vrst simptomov, dodajanje | F2 |
| Terapije | seznam, dodajanje, urejanje, označi kot vzeto | F3, F4 |
| Zgodovina | tabela zapisov z izbiro obdobja, urejanje in brisanje | F5, F8 |
| Povzetek | graf in tabela za izbrano obdobje, oblikovano za tisk | F7 |

## 5 Seznam nalog

### Postavitev
- [ ] Virtualno okolje, `pip install flask`
- [ ] `.gitignore` (venv, `__pycache__`, `*.db`, `.env`)
- [ ] Osnovna Flask aplikacija, ki se zažene
- [ ] `requirements.txt`

### Podatkovna baza
- [ ] `schema.sql` s petimi tabelami
- [ ] Funkcija za povezavo in inicializacijo baze
- [ ] Testni podatki za razvoj

### Uporabniški računi (F1, N4, N5)
- [ ] Registracija z zgoščanjem gesla
- [ ] Prijava in odjava, seja
- [ ] Zaščita strani, ki zahtevajo prijavo
- [ ] Preverjanje lastništva pri vsaki poizvedbi

### Simptomi (F2)
- [ ] Dodajanje in prikaz vrst simptomov
- [ ] Obrazec za nov zapis — največ trije koraki
- [ ] Preverjanje vnosa (jakost 0–10, veljaven datum)

### Terapije (F3, F4)
- [ ] Dodajanje, urejanje, ukinjanje terapije
- [ ] Označevanje, da je terapija vzeta

### Pregled (F5, F6, F8)
- [ ] Zgodovina z izbiro obdobja
- [ ] Urejanje in brisanje zapisov
- [ ] Graf s Chart.js, označena območja jakosti, kratko pojasnilo

### Povzetek (F7)
- [ ] Zaslon s tabelo in grafom za izbrano obdobje
- [ ] CSS za tisk

### Zaključek
- [ ] Preizkus vseh scenarijev
- [ ] Posnetki zaslona za poglavje 4.4
- [ ] Izseki kode za prilogo
- [ ] `README.md` z navodili za zagon

## 6 Zunaj obsega

Dostop zdravnikov, povezava z zVEM ali CRPP, nosljive naprave, obveščanje po
e-pošti, obnovitev gesla, večjezičnost, mobilna aplikacija, algoritmi za razlago
podatkov.
