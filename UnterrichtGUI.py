# -*- coding: utf-8 -*-
# Dateiname: UnterrichtMainGUI.py
# Autor: Andreas Fischer
# erstellt: April 2020

from BasisGUI import BasisGUI
from EingabeRaum import EingabeRaum
from MyUtilities import *


class UnterrichtGUI(BasisGUI):
    def __init__(self, **kwargs):
        BasisGUI.__init__(self, **kwargs)

        self.eingabeMenu.add_command(label='Raum', command=self.eingabeRaum)
        self.ausgabeMenu.add_command(label='Raum', command=self.ausgabeRaum)

    def eingabeRaum(self):
        fenster = EingabeRaum(self.db)
        self.ergGUIs.append(fenster)
        fenster.title("Raum erfassen")
        fenster.mainloop()

    def ausgabeRaum(self):
        (tabelle, title) = self.db.selectStmt("*", "raum", "order by Haus, Nummer")
        fenster = ScrolledTableGUI(tabelle, title)
        self.ergGUIs.append(fenster)
        fenster.mainloop()


if __name__ == "__main__":
    ugui = UnterrichtGUI(db="unterricht.db")
    ugui.startGUI()
