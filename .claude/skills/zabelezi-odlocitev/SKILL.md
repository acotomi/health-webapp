---
name: zabelezi-odlocitev
description: Zabeleži razvojno odločitev v docs/odlocitve.md. Uporabi, kadar je bila sprejeta odločitev o arhitekturi, podatkovnem modelu, knjižnici, varnosti, zasnovi vmesnika ali kadar je bila kakšna zahteva opuščena oziroma spremenjena. Uporabi tudi, kadar avtor reče „zabeleži to", „to gre v diplomsko" ali sprašuje, kaj vse je bilo doslej odločeno.
---

# Beleženje razvojnih odločitev

Avtor bo iz teh zapiskov pisal poglavja 4.3 (tehnološka zasnova), 4.4 (vmesnik),
4.5 (varstvo podatkov) in 5 (razprava, omejitve). Če odločitev ni zabeležena,
je čez mesec dni ne bo znal utemeljiti.

## Kdaj beležiti

- izbrana ali zavrnjena knjižnica oziroma pristop
- sprememba podatkovnega modela
- odločitev, povezana z varnostjo ali osebnimi podatki
- zahteva iz SPECIFIKACIJA.md, ki je bila poenostavljena ali opuščena
- omejitev, na katero si naletel in je nisi odpravil
- karkoli, kar bi mentor lahko vprašal z „zakaj tako?"

## Kako

Dopiši nov vnos na **konec** `docs/odlocitve.md`. Datoteko ustvari, če je še ni.
Obstoječih vnosov ne spreminjaj.

Predloga:

```markdown
## [DATUM] — [Kratek naslov]

**Vprašanje:** kaj je bilo treba odločiti

**Odločitev:** kaj je bilo izbrano

**Utemeljitev:** zakaj; kadar je mogoče, poveži z zahtevo (F1–F8, N1–N6) ali
z ugotovitvijo iz poglavja 3

**Zavrnjene možnosti:** kaj še je bilo v igri in zakaj ni bilo izbrano

**Za katero poglavje:** 4.3 / 4.4 / 4.5 / 5
```

## Pravila

- Piši v slovenščini, kratko, v celih povedih.
- Navedi resnične razloge, ne poznejših racionalizacij.
- Če je bila odločitev sprejeta zaradi pomanjkanja časa ali znanja, tako tudi zapiši —
  to sodi med omejitve v poglavju 5 in je pošteneje kot izmišljena utemeljitev.
- Ne zapisuj odločitev, ki niso bile dejansko sprejete.
