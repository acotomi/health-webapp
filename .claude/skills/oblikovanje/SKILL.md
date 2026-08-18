---
name: oblikovanje
description: Konvencije za obliko vmesnika (CSS, osnovna predloga). Preberi, preden ustvariš ali urejaš katerokoli HTML predlogo, da se stila ne izumlja znova pri vsakem zaslonu.
---

# Oblikovanje vmesnika

Vsa oblika je centralizirana v dveh datotekah — nove predloge praviloma ne
potrebujejo lastnega CSS:

- `static/style.css` — vsi stili. Stilira osnovne HTML elemente (`label`,
  `input`, `button`, `table`, ...) neposredno, ne prek razredov po meri
  (izjema: sporočila, glej spodaj).
- `templates/base.html` — osnovna predloga z `<head>`, glavo strani in
  izpisom `flash` sporočil. Vsaka nova predloga jo razširi:

```html
{% extends "base.html" %}
{% block naslov %}Ime zaslona{% endblock %}
{% block vsebina %}
    <!-- vsebina zaslona -->
{% endblock %}
```

## Sporočila uporabniku (flash)

Vedno podaj kategorijo, da se sporočilo pravilno obarva:

```python
flash("Besedilo napake.", "napaka")
flash("Besedilo uspeha.", "uspeh")
```

`base.html` sporočila že izpisuje in stilira (`sporocilo-napaka`,
`sporocilo-uspeh`) — v novih predlogah tega ni treba ponavljati.

## Barve in pisava

Definirano kot CSS spremenljivke v `style.css` — vrednosti ne podvajaj, sklicuj
se nanje:

- pisava: sistemska (`system-ui` ipd.), brez zunanjih virov/CDN — CLAUDE.md
  prepoveduje zunanje storitve
- poudarek (gumbi, povezave): `--barva-poudarek` (modra)
- napaka: `--barva-napaka-*` (rdeča) · uspeh: `--barva-uspeh-*` (zelena)

## Pravila

- Ne dodajaj `style="..."` neposredno v HTML. Če kaj manjka v `style.css`,
  dodaj tja, ne kot inline stil.
- Ne dodajaj CSS frameworkov (Bootstrap ipd.) ali CDN povezav.
- Tabele (Zgodovina, Povzetek) uporabljajo navaden `<table>` — že stiliran.
- Zaslon "Povzetek" (F7) bo potreboval `@media print` blok v `style.css` —
  dodaj ga takrat, ko se dela ta zaslon, ne prej.
- Če zaslon potrebuje nekaj, česar `style.css` še ne pokriva, dodaj pravilo
  vanj in na kratko omeni, kaj si dodal in zakaj.
