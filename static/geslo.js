// Preklop prikaza/skritja gesla. Vsak gumb z razredom "gumb-oko" ima v
// atributu data-cilj id polja za geslo, ki ga preklaplja.
document.querySelectorAll(".gumb-oko").forEach(function (gumb) {
    gumb.addEventListener("click", function () {
        var polje = document.getElementById(gumb.dataset.cilj);
        if (!polje) {
            return;
        }
        var razkrito = polje.type === "text";
        polje.type = razkrito ? "password" : "text";
        gumb.classList.toggle("aktivno", !razkrito);
        gumb.setAttribute("aria-pressed", String(!razkrito));
        gumb.setAttribute("aria-label", razkrito ? "Prikaži geslo" : "Skrij geslo");
    });
});
