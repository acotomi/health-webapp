// Prepiše datume iz privzete slovenske oblike (izrisane na strežniku, deluje
// tudi brez JavaScripta) v obliko, ki jo za <input type="date"> uporablja
// brskalnik/OS uporabnika - da so vsi izpisi na strani usklajeni z vnosnimi
// polji. Uporablja vgrajen Intl.DateTimeFormat, brez zunanjih knjižnic.
(function () {
    if (!window.Intl || !Intl.DateTimeFormat) {
        return;
    }

    var oblikaDatuma = new Intl.DateTimeFormat(undefined, {
        day: "numeric",
        month: "numeric",
        year: "numeric",
    });

    document.querySelectorAll("[data-datum]").forEach(function (el) {
        var d = new Date(el.dataset.datum + "T00:00:00");
        if (!isNaN(d)) {
            el.textContent = oblikaDatuma.format(d);
        }
    });

    var oblikaCasa = new Intl.DateTimeFormat(undefined, {
        day: "numeric",
        month: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });

    document.querySelectorAll("[data-casovna-znacka]").forEach(function (el) {
        var d = new Date(el.dataset.casovnaZnacka.replace(" ", "T"));
        if (!isNaN(d)) {
            el.textContent = oblikaCasa.format(d);
        }
    });
})();
