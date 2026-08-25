// Potrditveno polje "izberi vse" v glavi tabele preklopi vsa potrditvena
// polja vrstic z enakim imenom (data-skupina).
document.querySelectorAll("[data-izberi-vse]").forEach(function (glavno) {
    var skupina = glavno.dataset.izberiVse;
    glavno.addEventListener("change", function () {
        document.querySelectorAll('input[data-skupina="' + skupina + '"]').forEach(function (polje) {
            polje.checked = glavno.checked;
        });
    });
});
