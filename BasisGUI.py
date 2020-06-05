# -*- coding: utf-8 -*-
# Dateiname: MainGUI.py
# Autor: Andreas Fischer
# erstellt: April 2020

from DB_Tool import DB_Tool
from MyUtilities import *
from SQLGUI import SQLGUI
from SelectGUI import SelectGUI


class BasisGUI(MasterGUI):
    def __init__(self, **kwargs):
        h = kwargs.pop('host', None)
        u = kwargs.pop('user', None)
        pw = kwargs.pop('password', None)
        d = kwargs.pop('db', None)
        self.db = DB_Tool(host=h, user=u, password=pw, db=d)
        MasterGUI.__init__(self, **kwargs)
        padweite = 10
        eingabeWeite = 95
        buttonWeite = 50
        self.version = "0.1"
        if self.db.type == "SQLite":
            self.title("V" + self.version + " - " + self.db.type + " - " + self.db.db)
        else:
            self.title("V" + self.version + " - " + self.db.type)
        self.geometry("570x530+30+60")

        # -- Menue:
        self.menu = Menu(self)

        self.eingabeMenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=" Datenerfassung ", menu=self.eingabeMenu)

        self.ausgabeMenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="  Datenanzeige  ", menu=self.ausgabeMenu)

        self.sqlMenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="  SQL  ", menu=self.sqlMenu)
        self.sqlMenu.add_command(label='SELECT', command=self.startSELECT)
        self.sqlMenu.add_command(label='SQL', command=self.startSQL)

        self.helpmenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="  Hilfe  ", menu=self.helpmenu)
        self.helpmenu.add_command(label='Alle Tabellen inkl. Attribute',
                                  command=self.alleTabellenKommando)
        self.helpmenu.add_command(label='Datenbankabfrage',
                                  command=self.helpSelectKommando)
        self.helpmenu.add_command(label='Datensatz einfügen',
                                  command=self.helpInsertKommando)
        self.helpmenu.add_command(label='Datensatz aktualisieren',
                                  command=self.helpUpdateKommando)
        self.helpmenu.add_command(label='Datensatz löschen',
                                  command=self.helpDeleteKommando)
        self.helpmenu.add_command(label='Tabelle anlegen',
                                  command=self.helpCreateKommando)
        self.helpmenu.add_command(label='Tabelle löschen',
                                  command=self.helpDropKommando)
        self.helpmenu.add_command(label='View anlegen',
                                  command=self.helpViewKommando)
        self.menu.add_command(label='  Beenden  ', command=self.destroyCmd)

        bild = PhotoImage(file="GHO.gif")
        label = Label(master=self, compound=CENTER, image=bild)
        label.photo = bild
        label.pack()

    def startGUI(self):
        self.config(menu=self.menu)
        self.mainloop()

    def startSELECT(self):
        fenster = SelectGUI(self.db)
        self.ergGUIs.append(fenster)
        fenster.title("SELECT STATEMENT")
        fenster.mainloop()

    def startSQL(self):
        fenster = SQLGUI(self.db)
        self.ergGUIs.append(fenster)
        fenster.title("SQL STATEMENT")
        fenster.mainloop()

    def alleTabellenKommando(self):
        tabListe = self.db.alleTabellen()
        liste = [["Tabellen"]]
        liste = []
        for e in tabListe:
            liste.append(e)
            (b, attListe) = self.db.execute("SHOW COLUMNS FROM " + e[0])
            if b:
                for a in attListe:
                    liste.append(["   " + a[0]])
                liste.append([""])
        ergv = ScrolledTableGUI(liste, title='Alle Tabellen inkl. Attribute',
                                zeilennummern=False, schreibschutz=False)
        self.ergGUIs.append(ergv)
        ergv.mainloop()

    def helpSelectKommando(self):
        text = """
 ============================================
 Datenbankabfrage:
 ============================================

   SELECT <projektion> FROM <tabellenname(n) / view(s)> WHERE <selektion>;

     Innerhalb der Projektion:
     =========================
     Angabe der Attribute (Spaltenüberschriften) in der gewünschten Reihenfolge
     Tipp: * liefert alle Attribute
     Hinweis: bei mehreren Tabellen sollte der Tabellenname vorangestellt werden
              z.B.: kunden.kunr
     
     Funktionen:
     -----------
       Zählen:
         COUNT(Primärschlüsselattribut) 
         Hinweis: Vermeide COUNT(*)
       Maximum / Minimum:
         MAX(Attribut)
         MIN(Attribut)
       Summe / Durchschnitt:
         SUM(Attribut)
         AVG(Attribut)
         
     Mehrfach auftretende Datensätze nur einmal nennen:
       SELECT DISTINCT ...
     
     
     Innerhalb der Selektion:
     =========================

       Vergleichsoperatoren:
         >    ist größer als
         <    ist kleiner als
         >=   ist größer oder gleich als
         <=   ist kleiner oder gleich als
         =    ist gleich
         between Wert1 AND Wert2     zwischen zwei Werten, inklusive Wert1 und Wert2         
       
         Bei Textvergleichen besser LIKE anstelle von = benutzen!       
         LIKE '%Textteil%'       % ist ein beliebiger Textteil, 
                                 der auch leer sein kann
         LIKE 'M_ier'            _ ist genau ein beliebiges Zeichen
         
       IN: Liegt der Wert innerhalb einer Liste?
         kuname IN ('Cim', 'Fischer',  'Gulder',  'Schmidt') 

       Join: Verbinden zweier Tabellen (Entitäts- und Relationstabelle)
       ----------------------------------------------------------------
         Das Primärschlüsselattribut der Entitätstabelle wird mit dem
         dazu passenden Fremdschlüsselattribut der Relationstabelle
         gleichgesetzt.
         Beispiel: kunden = Entitätstabelle und ausleiehe = Relationstabelle
           kunden.kunr = ausleihe.kunr
       
       Sortieren:
         ORDER BY Attribut ASC            aufsteigend
         ORDER BY Attribut DESC           absteigend

       Gruppieren:
         GROUP BY Attribut
       
     Funktionen:
     -----------
       Länge:
         LENGTH(Attribut)
         
     Logische Verknüpfungen:
     -----------------------
       AND, OR, NOT

     Abfragen über mehrere Tabellen:
       Beispiel: Alle Klausuren eines Schülers
       SELECT schueler.vorname, klausur.fach
       FROM schueler, klausur 
       WHERE schueler.vorname like "Ferdinand" AND schueler.nr = klausur.schueler;
"""
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.title("GHO - Daten abfragen")
        ergv.mainloop()

    def helpInsertKommando(self):
        text = """
 ============================================
 Datensatz eintragen
 ============================================

   INSERT INTO <tabellenname> VALUES (<WertAttribut1>, <WertAttribut2>, ... <WertAttributn>);

   oder bei Nennung / Auslassung von Attributen:

   INSERT INTO <tabellenname> (<attribut3>, <attribut1>, ...) VALUES (<WertAttribut3>, <WertAttribut1>, ... );

   Beispiel:
   INSERT INTO person VALUES ("S0815", "Heinemann", "Gustav");
   oder bei anderer Reihenfolge
   INSERT INTO person ("vorname", "nachname", "PID") VALUES ("Gustav", "Heinemann", "P0815");

   TIPP: Manchmal möchte man einen neuen Datensatz hinzufügen oder, falls es diesen Datensatz bereits gibt,
   den bestehenden Datensatz aktualisieren. Dann ergänzt man den INSERT-Befehl und schreibt:
   
   INSERT OR REPLACE INTO <tabellenname> (<attribut3>, <attribut1>, ...) VALUES (<WertAttribut3>, <WertAttribut1>, ... );

"""
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.fenster.title("GHO - Datensatz eintragen ")
        ergv.fenster.mainloop()

    def helpUpdateKommando(self):
        text = """

 ============================================
 Datensatz aktualisieren
 ============================================

   UPDATE <tabellenname> SET <attribut1> = "neuerWert1", <attribut2> = "neuerWert2", ... WHERE <selektion>;

   Beispiel:

   UPDATE person SET nachname = "Meier" WHERE PID = 4711;

"""
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.fenster.title("GHO - Datensatz aktualisieren ")
        ergv.fenster.mainloop()

    def helpDeleteKommando(self):
        text = """

 ============================================
 Datensatz löschen
 ============================================

   DELETE FROM <tabellenname> WHERE <selektion>;

   Obacht: Abhängigkeiten beachten

   Beispiel:
   DELETE FROM schueler WHERE jahr < 2000;
 
"""
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.fenster.title("GHO - Datensatz löschen ")
        ergv.fenster.mainloop()

    def helpCreateKommando(self):
        text = """
 
 ===================================================
 Datenbanktabelle anlegen:
 ===================================================
 
   A. Entität mit 1 Primärschlüsselattribut
   =================================================
   CREATE TABLE <tabellenname>(
     <prim_key_attribut1>  <datentyp(anzahl)> PRIMARY KEY,
     <attribut2>  <datentyp(anzahl)>,
     <attribut3>  <datentyp(anzahl)>,
     ...
     <attributn>  <datentyp(anzahl)>
   );


   Alle Primärschlüsselattribute müssen ausgefüllt werden.
   Dürfen weitere Attribute wie im Beispiel Vor- und Nachname
   nicht leer bleiben, schreibt man jeweils rechts daneben: NOT NULL

   Beispiel:
   CREATE TABLE person(
     id            INT(10)     PRIMARY KEY,
     vorname       VARCHAR(50) NOT NULL,
     nachname      VARCHAR(50) NOT NULL,
     geburtsdatum  VARCHAR(10),
     mail          VARCHAR(60)
   );
 
   B. Entität mit mehreren Primärschlüsselattributen
   =================================================
   CREATE TABLE <tabellenname>(
     <prim_key_attribut1>  <datentyp(anzahl)>,
     <prim_key_attribut2>  <datentyp(anzahl)>,
     ...
     <attributn>  <datentyp(anzahl)>,
     PRIMARY KEY (prim_key_attribut1, prim_key_attribut2, ...)
   );
   
   Beispiel:
   CREATE TABLE person(
     vorname       VARCHAR(30),
     nachname      VARCHAR(30),
     geburtsdatum  VARCHAR(10),
     mail          VARCHAR(60),
     PRIMARY KEY (vorname, nachname)
   );
 
   C. Relation (n:m)
   =================================================
   CREATE TABLE <tabellenname> (
     <fk_attribut1> <datentyp(anzahl)>, 
     <fk_attribut2> <datentyp(anzahl)>,
     ...
     <attributn> <datentyp(anzahl)>,
     FOREIGN KEY (fk_attribut1) REFERENCES <tabelle1> (<prim_key_tabelle1>),
     FOREIGN KEY (fk_attribut2) REFERENCES <tabelle2> (<prim_key_tabelle2>)
   );
   Hinweis 1: Die Datentypen müssen exakt mit den Primärschlüsselattributen übereinstimmen.
   Hinweis 2: Hat eine Tabelle mehrere Primärschlüsselattribute, müssen diese auch bei den 
   Fremdschlüsseln zusammengefasst werden.
   
   Beispiel:
   CREATE TABLE in_Kurs_einschreiben(
      pv     VARCHAR(30),
      pn     VARCHAR(30),
      kn     VARCHAR(10),
      datum  VARCHAR(10),
      FOREIGN KEY (pv, pn) REFERENCES person(vorname, nachname),   
      FOREIGN KEY (kn) REFERENCES kurs(kursnr)
   );

   D. Entität inkl. 1:n Relation
   =================================================
   CREATE TABLE <Tabelle> (
     <attribut1> <datentyp(anzahl)> PRIMARY KEY,
     <attribut2> <datentyp(anzahl)>,
     <attribut3> <datentyp(anzahl)>,
     ...
     <fk_attributn> <datentyp(anzahl)>,
     FOREIGN KEY (fk_attributn) REFERENCES <tabelle1> (<prim_key_tabelle1>)
   );
   Hinweis: Die Datentypen müssen exakt mit den Primärschlüsselattributen übereinstimmen.

   Beispiel:
   CREATE TABLE auto(
     kennzeichen    VARCHAR(30) PRIMARY KEY,
     fabrikat       VARCHAR(50),
     modell         VARCHAR(30),
     farbe          VARCHAR(50),
     fahrer         INT(10),
     FOREIGN KEY (fahrer) REFERENCES person(id)
   );

  E. Automatische Hochzählen des Primärschlüssels
  ===============================================

  Möchte man sich nicht selbst um die Nummerierung der Datensätze kümmern,
  kann man das entsprechende Primärschlüsselattribut automatisch hochzählen
  lassen.

  Wichtig ist, dass man diese Nummer wie im Beispiel als Integer ohne Stellenangabe
  definiert und als letztes das Schlüsselwort AUTOINCREMENT (MySQL: AUTO_INCREMENT) kommt.
  
  CREATE TABLE person (
    nummer   INTEGER PRIMARY KEY AUTOINCREMENT,
    vorname  VARCHAR(50),
    nachname VARCHAR(50)
  );
  
"""
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.fenster.title("GHO - Tabelle anlegen")
        ergv.fenster.mainloop()

    def helpViewKommando(self):
        text = """
 
 ============================================
 Datenbank-View anlegen:
 ============================================

 CREATE VIEW <viewname> AS <selection>;

 Beispiel:
 
 CREATE VIEW informatikkurs AS SELECT * from kurs WHERE fach LIKE "Informatik";

"""
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.fenster.title("GHO - View anlegen")
        ergv.fenster.mainloop()

    def helpDropKommando(self):
        text = """

 ============================================
 Datenbanktabelle löschen:
 ============================================

   DROP TABLE <tabellenname>;

   Obacht: Abhängigkeiten beachten

   Beispiel:

   DROP TABLE auto;
   
   Durch den Zusatz IF EXISTS wird der Befehl nur ausgeführt,
   wenn die Tabelle existiert.
   
   DROP TABLE IF EXISTS auto;

 ============================================       

        """
        ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
        self.ergGUIs.append(ergv)
        ergv.zeigeAn(text)
        ergv.fenster.title("GHO - Tabelle löschen")
        ergv.fenster.mainloop()


if __name__ == "__main__":
    bgui = BasisGUI(db="unterricht.db")
    bgui.startGUI()
