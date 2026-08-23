// Barvna območja jakosti (0-10) v ozadju grafa. Samo vizualna lestvica,
// brez interpretacije podatkov.
const obmocjaJakosti = [
    { od: 0, do: 3, barva: "rgba(21, 128, 61, 0.08)" },
    { od: 3, do: 6, barva: "rgba(202, 138, 4, 0.08)" },
    { od: 6, do: 10, barva: "rgba(185, 28, 28, 0.08)" },
];

const vtaknjenoObmocja = {
    id: "obmocjaJakosti",
    beforeDraw(chart) {
        const { ctx, chartArea, scales } = chart;
        if (!chartArea) {
            return;
        }

        for (const obmocje of obmocjaJakosti) {
            const yZgoraj = scales.y.getPixelForValue(obmocje.do);
            const ySpodaj = scales.y.getPixelForValue(obmocje.od);

            ctx.save();
            ctx.fillStyle = obmocje.barva;
            ctx.fillRect(chartArea.left, yZgoraj, chartArea.right - chartArea.left, ySpodaj - yZgoraj);
            ctx.restore();
        }
    },
};

function oblikujOznakeGrafa(seznamISO) {
    // Enaka logika kot za tabele (datumi.js): letnica se izpiše samo na prvi
    // oznaki in ob spremembi leta, sicer samo dan in mesec. Vrstni red/ločila
    // sledijo sistemski nastavitvi uporabnika (Intl, brez privzete lokacije),
    // enako kot pri <input type="date">.
    const zLetom = new Intl.DateTimeFormat(undefined, { day: "numeric", month: "numeric", year: "numeric" });
    const brezLeta = new Intl.DateTimeFormat(undefined, { day: "numeric", month: "numeric" });
    let zadnjeLeto = null;

    return seznamISO.map((iso) => {
        const d = new Date(`${iso}T00:00:00`);
        if (d.getFullYear() !== zadnjeLeto) {
            zadnjeLeto = d.getFullYear();
            return zLetom.format(d);
        }
        return brezLeta.format(d);
    });
}

function narisiGrafSimptomov(podatki) {
    const platno = document.getElementById("graf-simptomov");
    if (!platno || podatki.nizi.length === 0) {
        return;
    }

    const oznakeOsiX = oblikujOznakeGrafa(podatki.datumi);

    // Namenoma brez rdeče/rožnate/vijolične - ozadje uporablja rdečo za "huda",
    // modra in vijolična pa sta si (tudi pri barvni slepoti) preveč podobni.
    const barvePoNizih = ["#1e3a5f", "#22c55e", "#d97706", "#78350f", "#4b5563"];
    // Oblika pike je dodatna (ne edina) ločnica med nizi - pomaga pri barvni
    // slepoti, ko se dve barvi zlijeta. Vgrajeni stili Chart.js, brez SVG-jev.
    const oblikePoNizih = ["circle", "rect", "triangle", "rectRot", "crossRot"];

    new Chart(platno, {
        type: "line",
        data: {
            labels: oznakeOsiX,
            datasets: podatki.nizi.map((niz, i) => ({
                label: niz.naziv,
                data: niz.vrednosti,
                spanGaps: true,
                borderColor: barvePoNizih[i % barvePoNizih.length],
                backgroundColor: barvePoNizih[i % barvePoNizih.length],
                pointStyle: oblikePoNizih[i % oblikePoNizih.length],
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.2,
            })),
        },
        options: {
            scales: {
                x: {
                    ticks: { autoSkip: false },
                },
                y: {
                    min: 0,
                    max: 10,
                    ticks: { stepSize: 1 },
                    title: { display: true, text: "Jakost (0–10)" },
                },
            },
        },
        plugins: [vtaknjenoObmocja],
    });
}
