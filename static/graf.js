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

// Skupna paleta za oba grafa (simptomi, terapije) - namenoma brez
// rdeče/rožnate/vijolične (glej graf simptomov spodaj), oblika pike je
// dodatna ločnica med nizi za primer barvne slepote. Vgrajeni stili
// Chart.js, brez SVG-jev.
const BARVE_PO_NIZIH = ["#1e3a5f", "#22c55e", "#d97706", "#78350f", "#4b5563"];
const OBLIKE_PO_NIZIH = ["circle", "rect", "triangle", "rectRot", "crossRot"];

function narisiGrafSimptomov(podatki) {
    const platno = document.getElementById("graf-simptomov");
    if (!platno || podatki.nizi.length === 0) {
        return;
    }

    const oznakeOsiX = oblikujOznakeGrafa(podatki.datumi);

    new Chart(platno, {
        type: "line",
        data: {
            labels: oznakeOsiX,
            datasets: podatki.nizi.map((niz, i) => ({
                label: niz.naziv,
                data: niz.vrednosti,
                spanGaps: true,
                borderColor: BARVE_PO_NIZIH[i % BARVE_PO_NIZIH.length],
                backgroundColor: BARVE_PO_NIZIH[i % BARVE_PO_NIZIH.length],
                pointStyle: OBLIKE_PO_NIZIH[i % OBLIKE_PO_NIZIH.length],
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.2,
            })),
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { autoSkip: true, maxTicksLimit: 15 },
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

function narisiGrafTerapij(podatki) {
    const platno = document.getElementById("graf-terapij");
    if (!platno || podatki.nizi.length === 0) {
        return;
    }

    const oznakeOsiX = oblikujOznakeGrafa(podatki.datumi);

    new Chart(platno, {
        type: "line",
        data: {
            labels: oznakeOsiX,
            datasets: podatki.nizi.map((niz, i) => ({
                label: niz.naziv,
                // Brez spanGaps: manjkajoč dan tu pomeni resnično 0 odmerkov
                // (ne manjkajoč zapis, kot pri simptomih), zato so vrednosti
                // vedno cela števila, tudi 0.
                data: niz.vrednosti,
                borderColor: BARVE_PO_NIZIH[i % BARVE_PO_NIZIH.length],
                backgroundColor: BARVE_PO_NIZIH[i % BARVE_PO_NIZIH.length],
                pointStyle: OBLIKE_PO_NIZIH[i % OBLIKE_PO_NIZIH.length],
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.2,
            })),
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { autoSkip: true, maxTicksLimit: 15 },
                },
                y: {
                    min: 0,
                    ticks: { stepSize: 1, precision: 0 },
                    title: { display: true, text: "Število odmerkov" },
                },
            },
        },
    });
}
