# -*- coding: utf-8 -*-
# Dateiname: UnterrichtMainGUI.py
# Autor: Andreas Fischer
# erstellt: April 2020
from functools import partial

from BasisGUI import BasisGUI
from EingabeUniversal import EingabeUniversal
from MyUtilities import *


class UnterrichtGUI(BasisGUI):
    def __init__(self, **kwargs):
        BasisGUI.__init__(self, **kwargs)
        # Abrufen aller Tabellennamen
        result = self.db.execute("select name from sqlite_master where type='table' and name not like '%sql%'")
        tablenames = [i[0] for i in result[1]]
        # Iteratives Generieren der beiden Unterfenster für jede Tabelle
        for name in tablenames:
            foreign_keys = \
                self.db.execute(f"select \"from\", \"table\", \"to\" from PRAGMA_FOREIGN_KEY_LIST('{name}')")[1]
            keys = {}
            grouped = {}
            if foreign_keys is not None:
                # Vorgegebene Fremdschlüsse werden automatisch als Auswahlmöglichkeiten gegeben
                for fKey, table, pKey in foreign_keys:
                    if table not in grouped:
                        grouped[table] = []
                    grouped[table].append(fKey)
                    keys[fKey] = tuple(map(lambda x: x[0], self.db.execute(f"select {pKey} from {table}")[1]))

            self.eingabeMenu.add_command(label=name.capitalize(),
                                         command=partial(self.eingabeFenster, name, keys, grouped))
            self.ausgabeMenu.add_command(label=name.capitalize(), command=partial(self.ausgabeFenster, name))

    def eingabeFenster(self, table: AnyStr, restr_choices: Dict[AnyStr, Iterable[AnyStr]] = None,
                       combined: Iterable[AnyStr] = None) -> None:
        """
        Erstellt ein Fenster für die Dateneingabe für die Tabelle `table` der eigenen Datenbank `self.db`
        restr_choices gibt eine Möglichkeit Standardwerte für einzelne Spalten zu übergeben:
        {"columnname": ("- - - -", "A", "B", "C")}
        """

        fenster = EingabeUniversal(self.db, table, restr_choices, combined)
        self.ergGUIs.append(fenster)

    def ausgabeFenster(self, table: AnyStr, sel: AnyStr = "1=1"):
        """
        Erstellt ein Fenster in dem die gegebene Tabelle `table` mit der Selektion `sel` ausgegeben wird
        """
        tabelle, title = self.db.selectStmt("*", table, sel)
        fenster = ScrolledTableGUI(tabelle, title)
        self.ergGUIs.append(fenster)

    def destroy(self):
        self.destroyCmd()


if __name__ == "__main__":
    ugui = UnterrichtGUI(db="unterricht.db")
    ugui.startGUI()
