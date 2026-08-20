-- Shema podatkovne baze za spremljanje simptomov in terapij.
-- Glej SPECIFIKACIJA.md, poglavje 3, za izvor vsake tabele in polja.

CREATE TABLE uporabnik (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uporabnisko_ime TEXT NOT NULL UNIQUE,
    geslo_zgostitev TEXT NOT NULL,
    ustvarjen TEXT NOT NULL
);

CREATE TABLE simptom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uporabnik_id INTEGER NOT NULL,
    naziv TEXT NOT NULL,
    FOREIGN KEY (uporabnik_id) REFERENCES uporabnik (id)
);

CREATE TABLE zapis_simptoma (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simptom_id INTEGER NOT NULL,
    datum TEXT NOT NULL,
    jakost INTEGER NOT NULL CHECK (jakost BETWEEN 0 AND 10),
    opomba TEXT,
    FOREIGN KEY (simptom_id) REFERENCES simptom (id)
);

CREATE TABLE terapija (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uporabnik_id INTEGER NOT NULL,
    naziv TEXT NOT NULL,
    odmerek TEXT,
    pogostost TEXT,
    aktivna INTEGER NOT NULL DEFAULT 1 CHECK (aktivna IN (0, 1)),
    FOREIGN KEY (uporabnik_id) REFERENCES uporabnik (id)
);

CREATE TABLE zapis_terapije (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    terapija_id INTEGER NOT NULL,
    casovna_znacka TEXT NOT NULL,
    FOREIGN KEY (terapija_id) REFERENCES terapija (id)
);
