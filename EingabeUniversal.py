# -*- coding: utf-8 -*-
# Bastian Hentschel

from functools import partial

from DB_Tool import DB_Tool
from MyUtilities import *


class EingabeUniversal(MasterGUI):
    def __init__(self, db: DB_Tool, table_name: AnyStr,
                 restricted_choices: Dict[AnyStr, Union[Iterable[AnyStr], Callable[[], Iterable[AnyStr]]]] = None,
                 combined: Dict[AnyStr, Iterable[AnyStr]] = None):
        """
                Ein Fenster für die Dateneingabe für die Tabelle `table_name` der Datenbank `db`.
                `restr_choices` gibt eine Möglichkeit Standardwerte für einzelne Spalten zu übergeben:
                {"columnname": ("- - - -", "A", "B", "C"),
                 ...
                }
                """

        # Erstellung des Grundfensters
        super(EingabeUniversal, self).__init__()
        self.db = db
        self.table_name = table_name
        self.restricted_choices = restricted_choices or {}
        t = 24
        self.ft = ('Arial', t)
        self.title(f'{table_name.capitalize()}-Erfassung')
        self.labels = {}
        self.vars = {}
        self.varTraces = {}
        self.entries = {}
        self.dropdowns = {}
        self.combined = combined

        # Tabelleninfo (funzt nur für SQLite)
        fullTableSQL = f"SELECT name, type FROM PRAGMA_TABLE_INFO('{table_name}');"
        self.cols = dict(self.db.execute(fullTableSQL)[1])
        # Erstellen der Buttons
        self.einfuegen = Button(master=self, text='In DB eintragen', font=self.ft, bg='light green',
                                command=self.insert)
        self.zuruecksetzen = Button(master=self, text='Zurücksetzen', font=self.ft, bg='orange', command=self.refresh)
        rowcounter = 0
        # Einfügen der Eingabefelder
        for index, column in enumerate(self.cols.keys()):
            # Wenn es ein Autoincrement hat, wird die Spalte ignoriert
            if self.db.execute(f"SELECT pk FROM PRAGMA_TABLE_INFO('{table_name}');")[1][index][0] == "1":
                continue
            # Labelerstellung
            self.labels[column] = Label(self, text=column.capitalize(), font=self.ft)
            self.labels[column].grid(column=0, row=rowcounter, sticky=W, padx=10)

            if column in self.restricted_choices.keys():
                # Wenn es eine Auswahlbeschränkung (z. B. Foreign Keys) gibt
                # Tk Vars für Optionmenu erstellen und Standardwert setzen
                self.vars[column] = StringVar(self)
                self.vars[column].set(
                    int(self.getChoices(column)[0]) if self.getChoices(column)[0].isnumeric()
                    else self.getChoices(column)[0])
                # Dropdown/Optionmenu erstellen
                self.dropdowns[column] = OptionMenu(self, self.vars[column], *self.getChoices(column))
                self.dropdowns[column].config(font=self.ft)
                self.dropdowns[column].grid(column=1, row=rowcounter, sticky=W, padx=10)
                # Generierung der Trace-Callbacks, um verbundene Spalten zusammen zu aktualisieren
                for table, keys in self.combined.items():
                    if column in keys:
                        self.varTraces[column] = partial(self.combinedVarSetter, column=column, table=table)

            else:
                # Normale Entries ohne Auswahlbeschränkung
                self.entries[column] = Entry(master=self, width=10, font=self.ft)
                self.entries[column].grid(column=1, row=rowcounter, sticky=W, padx=10)
            rowcounter += 1
        # Aktivierung der Traces auf den entsprechenden Variablen
        for column, callbackFunc in self.varTraces.items():
            self.vars[column].trace_add("write", callbackFunc)
        self.refresh()
        # Knöpfe Bla Bla
        rowcounter += 1
        self.einfuegen.grid(column=0, row=rowcounter, columnspan=2,
                            padx=10, pady=20)

        rowcounter += 1
        self.zuruecksetzen.grid(column=0, row=rowcounter, columnspan=2,
                                padx=10, pady=10)

        self.focus_force()

    def combinedVarSetter(self, _, __, ___, column: AnyStr, table: Iterable[AnyStr]):
        """
        Setzt alle verbundenen Optionmenus (gleiche Tabelle `table`) auf den entsprechenden Wert des Optionmenu von `column`
        @param _: Benötigt für Trace-Callback, man braucht den Wert jedoch nur für Debugzwecke.
        @param __: Benötigt für Trace-Callback, man braucht den Wert jedoch nur für Debugzwecke.
        @param ___: Benötigt für Trace-Callback, man braucht den Wert jedoch nur für Debugzwecke.
        @param column: Die manuell aktualisierte Spalte.
        @param table: Die Originaltabelle des Fremdschlüssel.
        """
        for fKey in self.combined[table]:
            if fKey != column:
                self.vars[fKey].trace_remove("write", self.vars[fKey].trace_info()[0][1])
                self.vars[fKey].set(self.getChoices(fKey)[self.getChoices(column).index(str(self.vars[column].get()))])
                self.vars[fKey].trace_add("write", self.varTraces[fKey])

    def insert(self):
        """
        Prüft, ob die Eingaben mit den DB-Datentypen übereinstimmen und färbt ungültige Eingaben rot.
        Falls es keine Fehler gibt, wird der Datensatz eingefügt.
        """

        # Alle Labels werden schwarz gefärbt
        for label in self.labels.values():
            label.config(fg="black")
        # Datenzwischenspeicher
        values = {}

        # Auslesen der Werte je nach Eingabetyp (Optionmenu (bzw. die dazugehörige Var)/Entry)
        for column in self.labels.keys():
            if column in self.entries.keys():
                values[column] = self.entries[column].get()
            else:
                values[column] = self.vars[column].get()

        # Standardwert für Vorhandene Fehler
        error = False

        # Überprüfung auf falsche Werte
        for column in self.entries.keys():
            if "varchar" in self.cols[column]:
                # Falls Eingabe vom Typ str benötigt wird
                if len(values[column]) > int(self.cols[column][8:-1]) or not values[column]:
                    self.labels[column].config(fg="red")
                    error = True

            elif "int" in self.cols[column] and not "integer" in self.cols[column] and not values[column].isnumeric() \
                    and not len(str(values[column])) > int(self.cols[column][4:-1]):
                # Falls ein integer benötigt wird
                self.labels[column].config(fg="red")
                error = True

        if not error:  # Falls es keine Fehleingaben gab

            # Generierung und Ausführung des Insert-Statements
            stmt = f"INSERT INTO {self.table_name}({', '.join(str(k) for k, v in values.items() if v)}) VALUES " \
                   f"({', '.join((chr(39) if not v.isnumeric() else '') + str(v) + (chr(39) if not v.isnumeric() else '') for k, v in values.items() if v)});"
            sys.stderr.write(stmt + "\n")
            self.db.execute(stmt)

            # Zurücksetzen des Fensters
            self.refresh()

    def getChoices(self, column: AnyStr):
        """

        @param column: Die Spalte, die
        @return:
        """
        value = self.restricted_choices[column]
        if isinstance(value, Iterable):
            return value
        elif isinstance(value, Callable):
            return value()
        else:
            raise TypeError("column must be Iterable or Callable")

    def refresh(self):
        for col, var in self.vars.items():
            var.set(self.getChoices(col)[0])
        for entry in self.entries.values():
            entry.delete(0, END)
        for label in self.labels.values():
            label.config(fg="black")
