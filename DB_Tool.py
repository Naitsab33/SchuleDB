# -*- coding: utf-8 -*-
# Dateiname: DB_Tool.py
# Autor: Andreas Fischer
# erstellt: April 2020

# import mysql.connector
import sqlite3


class DB_Tool:
    """ Die Klasse DB_Tool stellt verschiedene Hilfsmethoden
        für die Verwendung der relationalen Datenbank MySQL
        und SQLite zur Verfügung.
    """

    def __init__(self, **kwargs):
        self.connection = None
        self.cursor = None
        self.type = "Unknown"
        self.host = kwargs.pop('host', None)
        self.user = kwargs.pop('user', None)
        self.password = kwargs.pop('password', None)
        self.db = kwargs.pop('db', None)
        if self.host is not None and self.user is not None and \
                self.password is not None and self.db is not None:
            self.type = "MySQL"
        elif self.db is not None:
            self.type = "SQLite"

    def execute(self, stmt, val=None):
        """ Das übergebene Statement wird ausgeführt und committed.
        """
        if self.type == "Unknown": return None
        success = True
        liste = None
        try:
            # Connection und Cursor
            # MySQL
            if self.type == "MySQL":
                self.connection = mysql.connector.connect(host=self.host,
                                                          user=self.user,
                                                          password=self.password,
                                                          db=self.db)
                self.cursor = self.connection.cursor()
            elif self.type == "SQLite":
                self.connection = sqlite3.connect(self.db)
                # Damit alle Zeichen einschließlich der Umlaute usw. angezeigt werden.
                self.connection.text_factory = str
                # Cursor
                self.cursor = self.connection.cursor()
                # Damit Fremdschlüssel richtig behandelt werden.
                self.cursor.execute('PRAGMA foreign_keys = 1;')
            # Connection und Cursor ==============

            if self.type == "SQLite":
                if stmt.upper().startswith("SHOW TABLES"):
                    stmt = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite%';"
                    self.cursor.execute(stmt)
                    liste = []
                    fetch = self.cursor.fetchall()
                    for e in fetch:
                        liste.append([e[0]])
                elif stmt.startswith("DESCRIBE"):
                    stmt = "SELECT sql FROM sqlite_master WHERE name = '" + stmt.replace(
                        "DESCRIBE ", "") + "';"
                    self.cursor.execute(stmt)
                    liste = []
                    fetch = self.cursor.fetchall()
                    for e in fetch:
                        liste.append([e[0]])
                elif stmt.startswith("SHOW COLUMNS FROM "):
                    stmt = "PRAGMA table_info('" + stmt.replace(
                        "SHOW COLUMNS FROM ", "").replace(";", "").replace(" ",
                                                                           "") + "');"
                    self.cursor.execute(stmt)
                    liste = []
                    fetch = self.cursor.fetchall()
                    for e in fetch:
                        liste.append([e[1]])
            elif self.type == "MySQL":
                if stmt.upper().startswith("SHOW TABLES") or \
                        stmt.upper().startswith("DESC") or \
                        stmt.upper().startswith("EXPLAIN") or \
                        stmt.upper().startswith("SHOW COLUMNS"):
                    self.cursor.execute(stmt)
                    liste = []
                    fetch = self.cursor.fetchall()
                    for e in fetch:
                        liste.append([e[0]])
            if stmt.upper().startswith("SELECT"):
                self.cursor.execute(stmt)
                fetch = self.cursor.fetchall()
                liste = []
                for e in fetch:
                    zeile = []
                    for k in e:
                        zeile.append(str(k))
                    liste.append(zeile)
            elif stmt.upper().startswith("INSERT") or stmt.upper().startswith(
                    "UPDATE"):
                self.cursor.execute(stmt)
                self.connection.commit()
            else:
                self.cursor.execute(stmt)
            self.connection.close()
        except Exception as e:
            print(e)
            success = False
        return success, liste

    def alleTabellen(self):
        erg = self.execute("SHOW TABLES")
        liste = []
        if erg[0]:
            for e in erg[1]:
                liste.append([e[0]])
        return liste

    def attributes(self, table):
        """ Liefert eine Liste der Attribute der angegebenen Tabelle.
            Die übergebene Projektion wird dabei berücksichtigt.
            Einschränkungen bei COUNT(*).
        """
        erg = self.execute("SHOW COLUMNS FROM " + table)
        # die Attribute sind in ` eingefasst
        attribute = []
        if erg[0]:
            for e in erg[1]:
                attribute.append(e[0])
        return attribute

    def selectStmt(self, proj=None, tab=None, sel=None):
        """
        Liefert eine 'Liste in Liste'-Tabelle zurück sowie das Statement.
        In der Tabelle stehendie Ergebnisse der SELECT-Abfrage.
        Die Tabelle bekommt zusätzlich eine Überschriftszeile.
        """
        tabelle = None
        stmt = ""
        if proj is not None and tab is not None and sel is not None:
            # nur Sortierung:
            if sel.upper().startswith('ORDER'): sel = '1 ' + sel
            # nur Gruppierung:
            if sel.upper().startswith('GROUP'): sel = '1 ' + sel

            stmt = "SELECT " + proj + " FROM " + tab + " WHERE " + sel + ";"
            (erfolg, selerg) = self.execute(stmt)

            if erfolg:
                ueberschrift = []
                attribute = []
                for i in range(len(selerg[0])):
                    ueberschrift.append(' ')
                if "*" == proj.replace(" ", ""):
                    # alle Attribute aller Tabellen
                    for e in tab.split(","):
                        attribute += self.attributes(e.replace(" ", ""))
                else:
                    attribute = proj.split(",")

                # Es dürfen nur so viele Attribute genommen werden, wie es Spalten gibt.
                for i in range(min(len(selerg[0]), len(attribute))):
                    # DISTINCT wird ignoriert
                    a = attribute[i].replace("DISTINCT", "").replace("distinct",
                                                                     "")
                    # AS wird berücksichtigt
                    if " AS " in a:
                        a = a.split(" AS ")[1]
                    elif " as " in a:
                        a = a.split(" as ")[1]
                        # Letztlich werden Leerzeichen eliminiert
                    ueberschrift[i] = a.replace(" ", "")
                # Die Ergebnistabelle beginnt mit den Überschriften
                tabelle = [ueberschrift]
                # Dann kommen die Ergebniszeilen.
                for e in selerg:
                    tabelle.append(e)
        return tabelle, stmt


if __name__ == "__main__":

    #    datei = input("SQLite-Dateiname: (MySQL = ENTER) ")
    datei = input("SQLite-Dateiname: ")
    if len(datei) > 0 and not datei.endswith(".db"):
        datei = datei + ".db"
    if len(datei) > 3:
        db = DB_Tool(db=datei)
    #    else:
    #        datei = ""
    #        db = DB_Tool(host="***REMOVED***", \
    #                     user="***REMOVED***", password="***REMOVED***", \
    #                     db="***REMOVED***")

    reset = input("Vollständiger Reset? (j/n) ") == "j"

    if reset:
        print("DROP TABLE IF EXISTS ...")
        print(db.execute("DROP TABLE IF EXISTS besucht;"))
        print(db.execute("DROP TABLE IF EXISTS kurs;"))
        print(db.execute("DROP TABLE IF EXISTS raum;"))
        print(db.execute("DROP TABLE IF EXISTS schueler;"))
        print(db.execute("DROP TABLE IF EXISTS lehrer;"))
        print(db.execute("DROP TABLE IF EXISTS test;"))

        print("Tabellen vorhanden?\n")
        print(db.execute("SHOW TABLES"))

        print("CREATE ...")
        if db.type == "SQLite":
            print(db.execute("""CREATE TABLE schueler(
              ID         integer PRIMARY KEY AUTOINCREMENT,
              Nachname   varchar(50) NOT NULL,
              Vorname    varchar(50) NOT NULL,
              Gebjahr    int(4),
              Gebmonat   int(2),
              Gebtag     int(2),
              Geschlecht varchar(1)
              );"""))
        elif db.type == "MySQL":
            print(db.execute("""CREATE TABLE schueler(
              ID         integer AUTO_INCREMENT PRIMARY KEY,
              Nachname   varchar(50) NOT NULL,
              Vorname    varchar(50) NOT NULL,
              Gebjahr    int(4),
              Gebmonat   int(2),
              Gebtag     int(2),
              Geschlecht varchar(1)
              );"""))

        print(db.execute("""CREATE TABLE lehrer(
              Kuerzel  varchar(5)  PRIMARY KEY,
              Nachname varchar(50) NOT NULL,
              Vorname  varchar(50) NOT NULL,
              Anrede   varchar(10)
              );"""))

        print(db.execute("""CREATE TABLE raum(
              Haus    varchar(1) NOT NULL,
              Nummer  int(2) NOT NULL,
              Plaetze int(2),
              Lehrer  varchar(5),
              PRIMARY KEY (Haus, Nummer), 
              FOREIGN KEY(Lehrer) REFERENCES lehrer(Kuerzel)
              );"""))

        print(db.execute("""CREATE TABLE kurs(
              Bezeichnung varchar(10)      PRIMARY KEY,
              Fach        varchar(50)      NOT NULL,
              Art         varchar(1)       NOT NULL,
              Nummer      int(3)           NOT NULL,
              Schuljahr   int(6)           NOT NULL,
              Lehrer      varchar(5),
              RHaus       varchar(1)       NOT NULL,
              RNummer     int(2)           NOT NULL,
              FOREIGN KEY (Lehrer)         REFERENCES lehrer(Kuerzel),
              FOREIGN KEY (RHaus, RNummer) REFERENCES raum(Haus, Nummer)
              );"""))

        print(db.execute("""CREATE TABLE besucht(
              Schueler integer      NOT NULL,
              Kurs     varchar(10)  NOT NULL,
              FOREIGN KEY(Schueler) REFERENCES schueler(ID),
              FOREIGN KEY(Kurs)     REFERENCES kurs(Bezeichnung)
              );"""))

        print("Tabellen vorhanden?\n")
        print(db.execute("SHOW TABLES"))

        print("INSERT ...")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Mainzel', 'Anton', '1964', '4', '2', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag ) VALUES ( 'Mainzel', 'Berti', '1964', '4', '2' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat ) VALUES ( 'Mainzel', 'Conny', '1964', '4' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr ) VALUES ( 'Mainzel', 'Det', '1964' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname ) VALUES ( 'Mainzel', 'Eddy' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname ) VALUES ( 'Mainzel', 'Fritzchen' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'König', 'Leopold', '1846', '2', '9', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Mueller', 'Hans', '1981', '9', '27', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Depp', 'Johnny', '1963', '6', '9', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Merkel', 'Angela', '1954', '7', '17', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Baggins', 'Frodo', '2968', '9', '22', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Gamdschie', 'Sam', '2967', '7', '30', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Oakenshield', 'Thorin', '2746', '9', '4', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Potter', 'Harry James', '1980', '7', '31', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Granger', 'Hermine', '1979', '9', '19', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Weasley', 'Ron', '1980', '3', '1', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Snape', 'Severus', '1960', '1', '9', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Lupin', 'Remus', '1960', '3', '10', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Weasley', 'Ginny', '1981', '8', '11', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Weasley', 'Molly', '1949', '10', '30', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Potter', 'Lily', '1960', '1', '30', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Riddle', 'Tom Vorlost', '1926', '12', '31', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Nicholas', 'Sir', '1492', '10', '31', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Mozart', 'Wolfgang Amadeus', '1776', '1', '27', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Curie', 'Marie', '1867', '11', '7', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Stuart', 'Maria', '1542', '12', '8', 'w' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Newton', 'Isaac', '1642', '12', '25', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'von Humboldt', 'Alexander', '1769', '9', '14', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Luther', 'Martin', '1483', '11', '10', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'van Beethoven', 'Ludwig', '1770', '12', '17', 'm' ); ")
        db.execute(
            "INSERT INTO schueler ( Nachname, Vorname, Gebjahr, Gebmonat, Gebtag, Geschlecht ) VALUES ( 'Duck', 'Donald', '1934', '6', '9', 'm' ); ")

        print("\nSchüler\n")
        print(db.execute("SELECT * FROM schueler ORDER BY ID;"))

        db.execute(
            "INSERT INTO lehrer VALUES ( 'FiA',  'Fischer',   'Andreas',  'Herr' ); ")
        db.execute(
            "INSERT INTO lehrer VALUES ( 'Pohl', 'Pohl',      'Matthias', 'Herr' ); ")
        db.execute(
            "INSERT INTO lehrer VALUES ( 'Smy',  'Smykowski', 'Adam',     'Dr'   ); ")
        db.execute(
            "INSERT INTO lehrer VALUES ( 'Dob',  'Dobberow',  'Anja',     'Frau' ); ")
        db.execute(
            "INSERT INTO lehrer VALUES ( 'Bad',  'Bader',     'Mark',     'Dr'   ); ")
        db.execute(
            "INSERT INTO lehrer VALUES ( 'Hen',  'Henke',     'Jörg',     'Herr' ); ")

        print("\nLehrer\n")
        print(db.execute("SELECT * FROM lehrer ORDER BY Kuerzel;"))

        db.execute(
            "INSERT INTO raum ( Haus, Nummer, Plaetze, Lehrer ) VALUES ( 'F', '60', '17', 'FiA' ); ")
        db.execute(
            "INSERT INTO raum ( Haus, Nummer, Plaetze, Lehrer ) VALUES ( 'A', '5', '24', 'Pohl' ); ")
        db.execute(
            "INSERT INTO raum ( Haus, Nummer, Plaetze ) VALUES ( 'A', '3', '17' ); ")
        db.execute(
            "INSERT INTO raum ( Haus, Nummer, Lehrer ) VALUES ( 'A', '53', 'Dob' ); ")

        print("\nRaum\n")
        print(db.execute("SELECT * FROM raum ORDER BY Haus, Nummer;"))

        db.execute(
            "INSERT INTO kurs ( Bezeichnung, Fach, Art, Nummer, Schuljahr, Lehrer, RHaus, RNummer ) VALUES ( 'ginf60_19', 'Informatik', 'G', '57', '201920', 'FiA', 'F', '60' ); ")
        db.execute(
            "INSERT INTO kurs ( Bezeichnung, Fach, Art, Nummer, Schuljahr, Lehrer, RHaus, RNummer ) VALUES ( 'gds5_17', 'DS', 'G', '73', '201718', 'Smy', 'A', '5' ); ")
        db.execute(
            "INSERT INTO kurs ( Bezeichnung, Fach, Art, Nummer, Schuljahr, Lehrer, RHaus, RNummer ) VALUES ( 'lmat61_20', 'Mathematik', 'L', '20', '202021', 'Dob', 'A', '53' ); ")
        db.execute(
            "INSERT INTO kurs ( Bezeichnung, Fach, Art, Nummer, Schuljahr, Lehrer, RHaus, RNummer ) VALUES ( 'gche5_19', 'Chemie', 'G', '52', '201920', 'Hen', 'A', '5' ); ")
        db.execute(
            "INSERT INTO kurs ( Bezeichnung, Fach, Art, Nummer, Schuljahr, Lehrer, RHaus, RNummer ) VALUES ( 'gdeu5_16', 'Deutsch', 'G', '5', '201617', 'Pohl', 'A', '53' ); ")

        print("\nKurs\n")
        print(db.execute("SELECT * FROM kurs ORDER BY Bezeichnung;"))

        db.execute(
            "INSERT INTO besucht ( Schueler, Kurs ) VALUES ( '1', 'gdeu5_16' ); ")
        db.execute(
            "INSERT INTO besucht ( Schueler, Kurs ) VALUES ( '2', 'ginf60_19' ); ")
        db.execute(
            "INSERT INTO besucht ( Schueler, Kurs ) VALUES ( '3', 'gds5_17' ); ")
        db.execute(
            "INSERT INTO besucht ( Schueler, Kurs ) VALUES ( '4', 'gche5_19' ); ")

        print("\nBesucht\n")
        print(db.execute("SELECT * FROM besucht ORDER BY Schueler;"))

    #    print("Tabellen\n")
    #    print(db.execute("SHOW TABLES"))
    #    print(db.execute("DESCRIBE schueler"))

    #    print("\nSchüler\n")
    #    print(db.execute("SELECT * FROM schueler ORDER BY ID;"))
    #    print("\nLehrer\n")
    #    print(db.execute("SELECT * FROM lehrer ORDER BY Kuerzel;"))
    #    print("\nRaum\n")
    #    print(db.execute("SELECT * FROM raum ORDER BY Haus, Nummer;"))
    #    print("\nKurs\n")
    #    print(db.execute("SELECT * FROM kurs ORDER BY Bezeichnung;"))
    #    print("\nBesucht\n")
    #    print(db.execute("SELECT * FROM besucht ORDER BY Schueler;"))

    print(db.execute("SHOW COLUMNS FROM raum;"))
