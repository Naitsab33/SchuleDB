# -*- coding: utf-8 -*-
# Dateiname: StartGUI.py
# Autor: Andreas Fischer
# erstellt: April 2020

from MyUtilities import *


class SQLGUI(MasterGUI):
    def __init__(self, db):
        self.db = db
        MasterGUI.__init__(self)
        self.title("SQl Abfrage")
        self.sqlEntry = Entry(master=self, width=80,
                              font=('Arial', 12))
        self.sqlEntry.bind('<Return>', self.sqlKommando)
        self.sqlEntry.pack(padx=5, pady=5)
        self.focus_force()

    def sqlKommando(self, event=None):
        sqltext = TextFormat.formatText(self.sqlEntry.get()).replace("\n", "")
        if ";" not in sqltext:
            ergv = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
            self.ergGUIs.append(ergv)
            ergv.zeigeAn("incomplete SQL statement: ';' is missing\n")
            ergv.mainloop()
        else:
            liste1 = sqltext.split(";")
            liste = []
            for el in liste1:
                cmd = el
                if cmd != "":
                    if ";" not in cmd:
                        cmd += ";"
                    liste.append(cmd)
            meldungen = ""
            for command in liste:
                if command != "":
                    erg = self.db.execute(command)
                    if erg[0]:
                        meldungen += f"{command} \nDas Kommando wurde erfolgreich ausgeführt.\n"
                    else:
                        meldungen += f"{command} \nDas Kommando wurde nicht erfolgreich ausgeführt.\n"
                    meldungen += str(erg[1]) + "\n\n"
            fenster = ScrolledTextGUI(breite=36 * 3, hoehe=9 * 3)
            fenster.zeigeAn(meldungen)
            self.ergGUIs.append(fenster)
            fenster.mainloop()

    def sqlClearKommando(self):
        self.sqlText.delete("0.0", END)
