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

function narisiGrafSimptomov(podatki) {
    const platno = document.getElementById("graf-simptomov");
    if (!platno || podatki.nizi.length === 0) {
        return;
    }

    const barvePoNizih = ["#2b6cb0", "#7c3aed", "#c2410c", "#0f766e", "#be185d"];

    new Chart(platno, {
        type: "line",
        data: {
            labels: podatki.datumi,
            datasets: podatki.nizi.map((niz, i) => ({
                label: niz.naziv,
                data: niz.vrednosti,
                spanGaps: true,
                borderColor: barvePoNizih[i % barvePoNizih.length],
                backgroundColor: barvePoNizih[i % barvePoNizih.length],
                tension: 0.2,
            })),
        },
        options: {
            scales: {
                y: { min: 0, max: 10, ticks: { stepSize: 1 } },
            },
        },
        plugins: [vtaknjenoObmocja],
    });
}
