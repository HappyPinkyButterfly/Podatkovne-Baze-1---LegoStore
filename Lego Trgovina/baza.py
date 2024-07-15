import csv
import sqlite3
import os

PARAM_FMT = ":{}"  # za SQLite


class Tabela:
    ime = None
    podatki = None

    def __init__(self, conn):
        self.conn = conn

    def ustvari(self):
        raise NotImplementedError

    def izbrisi(self):
        self.conn.execute(f"DROP TABLE IF EXISTS {self.ime};")

    def uvozi(self, encoding="UTF-8"):
        if self.podatki is None:
            return
        with open(self.podatki, encoding=encoding) as datoteka:
            podatki = csv.reader(datoteka)
            stolpci = next(podatki)
            for vrstica in podatki:
                vrstica = {k: None if v == "" else v for k, v in zip(stolpci, vrstica)}
                self.dodaj_vrstico(**vrstica)

    def izprazni(self):
        self.conn.execute(f"DELETE FROM {self.ime};")

    def dodajanje(self, stolpci=None):
        return f"""
            INSERT INTO {self.ime} ({", ".join(stolpci)})
            VALUES ({", ".join(PARAM_FMT.format(s) for s in stolpci)});
        """

    def dodaj_vrstico(self, **podatki):
        podatki = {kljuc: vrednost for kljuc, vrednost in podatki.items()
                   if vrednost is not None}
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.conn.execute(poizvedba, podatki)
        return cur.lastrowid


class Uporabnik(Tabela):
    ime = "uporabnik"
    podatki = "podatki/uporabnik.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE uporabnik (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                up_ime    TEXT NOT NULL UNIQUE,
                geslo     TEXT NOT NULL
                );
             """)


class Narocilo(Tabela):
    ime = "narocilo"
    podatki = "podatki/narocilo.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE narocilo (
                id_ponudbe        INTEGER,
                id_uporabnika     INTEGER
            );
        """)


class Set(Tabela):
    ime = "setto"
    podatki = "podatki/set.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE setto (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                starost       TEXT NOT NULL,
                id_teme       INTEGER NOT NULL,
                koscki        INTEGER NOT NULL,
                ime           TEXT NOT NULL
            );
        """)


class Ponudba(Tabela):
    ime = "ponudba"
    podatki = "podatki/ponudba.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE ponudba (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                id_seta      TEXT NOT NULL,
                cena          INTEGER NOT NULL,
                zaloga        TEXT NOT NULL
            );
        """)


class Teme(Tabela):
    ime = "teme"
    podatki = "podatki/teme.csv"

    def ustvari(self):
        self.conn.execute("""
            CREATE TABLE teme (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                tema       TEXT
            );
        """)


def ustvari_tabele(tabele):
    for t in tabele:
        t.ustvari()


def izbrisi_tabele(tabele):
    for t in tabele:
        t.izbrisi()


def uvozi_podatke(tabele):
    for t in tabele:
        t.uvozi()


def izprazni_tabele(tabele):
    for t in tabele:
        t.izprazni()


def ustvari_bazo(conn):
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)


def pripravi_tabele(conn):
    uporabnik = Uporabnik(conn)
    narocilo = Narocilo(conn)
    ponudba = Ponudba(conn)
    set = Set(conn)
    teme = Teme(conn)

    return [uporabnik, narocilo, ponudba, set, teme]


def ustvari_bazo_ce_ne_obstaja(conn):
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        if cur.fetchone()[0] == 0:
            ustvari_bazo(conn)


BAZA = 'baza.db'
conn = sqlite3.connect(BAZA)
ustvari_bazo_ce_ne_obstaja(conn)


