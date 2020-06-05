# -*- coding: utf-8 -*-
# Andreas Fischer
# Umwandlung einer CSV-Datei in Objekte

from MyUtilities import *
from Raum import Raum


class EingabeRaum(MasterGUI):
    def __init__(self, db):
        MasterGUI.__init__(self)
        self.db = db
        t = 24
        self.ft = ('Arial', t)
        self.title('Raumerfassung')
        # self.geometry('400x300')
        self.labelHaus = Label(master=self, text='Haus*:', font=self.ft)
        self.hausVar = StringVar(self)
        self.hausChoices = ('- -', 'A', 'B', 'C', 'D', 'E', 'F')
        self.hausVar.set(self.hausChoices[0])
        self.dropDownHaus = OptionMenu(self, self.hausVar, *self.hausChoices)
        self.dropDownHaus.config(font=self.ft)
        self.labelNummer = Label(master=self, text='Nummer*:', font=self.ft)
        self.entryNummer = IntegerEntry(master=self, width=3, font=self.ft)
        self.labelPlaetze = Label(master=self, text='Plätze:', font=self.ft)
        self.entryPlaetze = IntegerEntry(master=self, width=3, font=self.ft)

        self.refresh()

        self.einfuegen = Button(master=self, text='In DB eintragen',
                                font=self.ft, bg='light green',
                                command=self.insert)
        self.zuruecksetzen = Button(master=self, text='Zurücksetzen',
                                    font=self.ft, bg='orange',
                                    command=self.refresh)

        rowcounter = 0
        self.labelHaus.grid(column=0, row=rowcounter, sticky=W, padx=10)
        self.dropDownHaus.grid(column=1, row=rowcounter, padx=10)

        rowcounter += 1
        self.labelNummer.grid(column=0, row=rowcounter, sticky=W, padx=10)
        self.entryNummer.grid(column=1, row=rowcounter, padx=10)

        rowcounter += 1
        self.labelPlaetze.grid(column=0, row=rowcounter, sticky=W, padx=10)
        self.entryPlaetze.grid(column=1, row=rowcounter, padx=10)

        rowcounter += 1
        self.einfuegen.grid(column=0, row=rowcounter, columnspan=2,
                            padx=10, pady=20)

        rowcounter += 1
        self.zuruecksetzen.grid(column=0, row=rowcounter, columnspan=2,
                                padx=10, pady=10)

        # Damit das Fenster vorne im Fokus steht
        self.focus_force()

    def insert(self):
        self.labelHaus.config(fg="black")
        self.labelNummer.config(fg='black')
        haus = self.hausVar.get()
        nummer = self.entryNummer.get()
        plaetze = self.entryPlaetze.get()
        if len(haus) != 1:
            self.labelHaus.config(fg='red')
        elif len(nummer) == 0:
            self.labelNummer.config(fg='red')
        else:
            if len(plaetze) == 0:
                plaetze = '0'
                self.entryPlaetze.insert(END, '0')
            raum = Raum(database=self.db)
            raum.haus = haus.upper()
            raum.nummer = int(nummer)
            raum.plaetze = int(plaetze)
            raum.insert()
            self.refresh()

    def refresh(self):
        self.hausVar.set(self.hausChoices[0])  # Default-Haus
        self.entryNummer.delete(0, END)  # Löschen der Raumnummer
        self.entryPlaetze.delete(0, END)  # Löschen der Platzanzahl

    def getLehrerChoices(self, start='- - - - - - -'):
        erg = [start]
        result = self.db.execute('SELECT Kuerzel FROM lehrer ORDER BY Kuerzel;')
        if result[0]:
            liste = result[1]
            for e in liste:
                erg.append(e[0])
        return erg
