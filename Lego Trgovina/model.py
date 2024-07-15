import sqlite3
from baza import conn

class Uporabnik:
    def __init__(self, up_ime=None, geslo=None):
        self.uporabniskoIme = up_ime
        self.geslo = geslo

    def __str__(self):
        return self.uporabniskoIme

    def shrani_v_bazo(self):
        '''Shrani uporabnika v bazo'''
        with conn:
            conn.execute('''
            INSERT INTO uporabnik (up_ime, geslo) VALUES (?,?)
            ''', [self.uporabniskoIme, self.geslo])

    @staticmethod
    def dobi_uporabnika(uporabniskoIme):
        with conn:
            cursor = conn.execute("""
                SELECT up_ime, geslo 
                FROM uporabnik
                WHERE up_ime=?
            """, [uporabniskoIme])
            if cursor.fetchone():
                return cursor
            return None
        
    @staticmethod
    def dobi_id_up(uporabniskoIme):
        with conn:
            cursor = conn.execute("""
                SELECT id
                FROM uporabnik
                WHERE up_ime=?
            """, [uporabniskoIme])
            return cursor.fetchone()[0]

    @staticmethod
    def pravilen_vnos(uporabniskoIme, geslo):
        with conn:
            cursor = conn.execute("""
                SELECT up_ime, geslo 
                FROM uporabnik
                WHERE up_ime=? AND geslo=?;
            """, [uporabniskoIme, geslo])
            if cursor.fetchone():
                return cursor
            return None

class Teme:
    def __init__(self, id, tema):
        self.id = id
        self.tema = tema

    @staticmethod
    def dobi_temo(id_teme):
        with conn:
            cursor = conn.execute("""
                SELECT * FROM teme WHERE teme.id = ?
            """, [id_teme])
            podatki = list(cursor.fetchall())
            return [Teme(pod[0], pod[1]) for pod in podatki]
        return []

    @staticmethod
    def dobi_vse_teme():
        with conn:
            cursor = conn.execute("""
                SELECT * FROM teme
            """)
            podatki = list(cursor.fetchall())
            return [Teme(pod[0], pod[1]) for pod in podatki]
        return []

class Set:
    def __init__(self, id, starost, tema, koscki, ime, cena=None, zaloga=None):
        self.id = id
        self.starost = starost
        self.tema = tema
        self.koscki = koscki
        self.ime = ime
        self.cena = cena
        self.zaloga = zaloga

        
    @staticmethod
    def dobi_sete_z_imenom_teme(id_teme=None):
        with conn:
            query = """
                SELECT setto.id, setto.starost, teme.tema, setto.koscki, setto.ime, ponudba.cena, ponudba.zaloga
                FROM setto
                JOIN teme ON setto.id_teme = teme.id
                LEFT JOIN ponudba ON setto.id = ponudba.id_seta
            """
            params = []
            if id_teme:
                query += " WHERE setto.id_teme = ?"
                params.append(id_teme)
            cursor = conn.execute(query, params)
            podatki = list(cursor.fetchall())
            return [Set(pod[0], pod[1], pod[2], pod[3], pod[4], pod[5], pod[6]) for pod in podatki]
    

    @staticmethod
    def dobi_vse_sete_starost():
        with conn:
            cursor = conn.execute('''
                SELECT DISTINCT starost FROM setto
            ''')
            podatki = list(cursor.fetchall())
            return [pod[0] for pod in podatki]

    @staticmethod
    def dobi_vse_sete_tema(id_teme=None):
        if id_teme:
            with conn:
                cursor = conn.execute('''
                    SELECT setto.id, setto.starost, setto.id_teme, setto.koscki, setto.ime, ponudba.cena
                    FROM setto
                    LEFT JOIN ponudba ON setto.id = ponudba.id_seta
                    WHERE setto.id_teme = ?
                ''', [id_teme])
                podatki = list(cursor.fetchall())
                return [Set(pod[0], pod[1], pod[2], pod[3], pod[4], pod[5]) for pod in podatki]
        return []
    
    @staticmethod
    def dobi_vse_podatke_za_set(sett):
        with conn:
            cursor = conn.execute('''
                SELECT setto.id, setto.starost, teme.tema, setto.koscki, setto.ime, ponudba.cena
                FROM setto
                LEFT JOIN ponudba ON setto.id = ponudba.id_seta
                LEFT JOIN teme ON setto.id_teme = teme.id
                WHERE setto.id = ?
            ''', [sett])
            podatki = list(cursor.fetchall())
            return [Set(pod[0], pod[1], pod[2], pod[3], pod[4], pod[5]) for pod in podatki]
        return []



class Ponudba:
    def __init__(self, id, id_seta, cena, zaloga):
        self.id = id
        self.id_seta = id_seta
        self.cena = cena
        self.zaloga = zaloga
    
    @staticmethod
    def dobi_zalogo_za_set(id_seta):
        with conn:
            cursor = conn.execute("""
                SELECT zaloga FROM ponudba WHERE id_seta = ?
            """, [id_seta])
            zaloga = cursor.fetchone()
            if zaloga:
                return zaloga[0]
            return "Out of stock"

    @staticmethod
    def dobi_vse_ponudbe(id_seta=None):
        if id_seta:
            with conn:
                cursor = conn.execute("""
                    SELECT * FROM ponudba WHERE id_seta = ?""", [id_seta])
                podatki = list(cursor.fetchall())
                return [Ponudba(pod[0], pod[1], pod[2], pod[3]) for pod in podatki]
        return []

    @staticmethod
    def dobi_ponudbe_cena_do(max_cena):
        with conn:
            cursor = conn.execute("""
                SELECT * FROM ponudba WHERE cena <= ?""", [max_cena])
            podatki = list(cursor.fetchall())
            return [Ponudba(pod[0], pod[1], pod[2], pod[3]) for pod in podatki]
        return []


class Narocilo:
    def __init__(self, id_ponudbe, id_uporabnika):
        self.id_ponudbe = id_ponudbe
        self.id_uporabnika = id_uporabnika

    def dodaj_v_bazo(self, conn):
        '''Doda naročilo v bazo.'''
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO narocilo (id_ponudbe, id_uporabnika)
                VALUES (?, ?)
            """, (self.id_ponudbe, self.id_uporabnika))
            conn.commit()

    @staticmethod
    def dobi_narocila_uporabnika(uporabnisko_ime):
        with conn:
            cursor = conn.execute('''
                SELECT setto.ime, ponudba.cena
                FROM narocilo
                JOIN ponudba ON narocilo.id_ponudbe = ponudba.id
                JOIN setto ON ponudba.id_seta = setto.id
                JOIN uporabnik ON narocilo.id_uporabnika = uporabnik.id
                WHERE uporabnik.up_ime = ?
            ''', [uporabnisko_ime])
            podatki = list(cursor.fetchall())
            return [{'ime': pod[0], 'cena': pod[1]} for pod in podatki]


