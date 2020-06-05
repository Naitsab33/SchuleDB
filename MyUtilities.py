from tkinter import *
from typing import Callable, Union, Sequence

SeqOrReturnsSeq = Union[Sequence, Callable[[], Sequence]]


class MasterGUI(Tk):
    def __init__(self, **kwargs):
        self.ergGUIs = []
        Tk.__init__(self, **kwargs)

    def destroyCmd(self):
        for el in self.ergGUIs:
            # falls das Fenster bereits manuell geschlossen wurde:
            try:
                el.destroyCmd()
            except Exception as e:
                pass
        # Ich habe die Methode destroy verändert -> daher der super call auf die Original-Methode
        super(MasterGUI, self).destroy()


class TableFormat:
    # Es reicht aus, dass diese methode static ist.
    @staticmethod
    def table2text(table, zn):
        zeilen = len(table)
        spalten = len(table[0])
        breiten = spalten * [3]
        for zeile in table:
            for i in range(spalten):
                if len(zeile[i]) > breiten[i]:
                    breiten[i] = len(zeile[i]) + 2
        gesamt = 0
        if zn:
            gesamt += 8
        for z in breiten:
            gesamt += z + 3
        text = ""
        for k in range(zeilen):
            text += " "
            if zn and k == 0:
                text += f" - ZN - "
            elif zn and k > 0:
                text += f" -{k:04}- "
            for i in range(spalten):
                ht = f"{breiten[i]}"
                text += f"| {table[k][i]:{ht}} "
            text += "\n " + gesamt * "-" + "\n"
        return text


class TextFormat:
    # Es reicht aus, dass diese methode static ist.
    @staticmethod
    def formatText(text):
        retString = ""
        for c in text:
            if ord(c) <= 128:
                retString += c
            elif ord(c) == 196:
                retString += "Ae"
            elif ord(c) == 214:
                retString += "Oe"
            elif ord(c) == 220:
                retString += "Ue"
            elif ord(c) == 228:
                retString += "ae"
            elif ord(c) == 246:
                retString += "oe"
            elif ord(c) == 252:
                retString += "ue"
            elif ord(c) == 223:
                retString += "ss"
            else:
                retString += "?"
        retString = retString.strip()
        return retString


class ValidatingEntry(Entry):
    # base class for validating entry widgets
    def __init__(self, **kw):
        self.__value = kw.pop('value', '')
        Entry.__init__(self, **kw)
        self.__variable = StringVar()
        self.__variable.set(self.__value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        # override: return value, new value, or None if invalid
        return value


class IntegerEntry(ValidatingEntry):
    def __init__(self, **kw):
        ValidatingEntry.__init__(self, **kw)

    def validate(self, value):
        try:
            if value:
                v = int(value)
            return value
        except ValueError:
            return None


class FloatEntry(ValidatingEntry):
    def __init__(self, **kw):
        ValidatingEntry.__init__(self, **kw)

    def validate(self, value):
        try:
            if value:
                v = float(value)
            return value
        except ValueError:
            return None


class MaxLengthEntry(ValidatingEntry):
    def __init__(self, **kw):
        self.maxlength = kw.pop('maxlength', 1)
        ValidatingEntry.__init__(self, **kw)

    def validate(self, value):
        return value[:self.maxlength]


class ScrolledFrame(object):
    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        self.bg = kwargs.pop('bg', kwargs.pop('background', '#EEEEEE'))

        self.outer = Frame(master, **kwargs)
        self.sbarY = Scrollbar(self.outer, orient=VERTICAL)
        self.sbarX = Scrollbar(self.outer, orient=HORIZONTAL)
        self.canvas = Canvas(self.outer, highlightthickness=0,
                             width=width, height=height, bg=self.bg,
                             yscrollcommand=self.sbarY.set,
                             xscrollcommand=self.sbarX.set)
        self.sbarY.config(command=self.canvas.yview)
        self.sbarX.config(command=self.canvas.xview)

        self.sbarY.pack(side=RIGHT, fill=Y)
        self.canvas.pack(fill=BOTH, expand=True)
        self.sbarX.pack(fill=X)

        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.sbarY.config(command=self.canvas.yview)
        self.sbarX.config(command=self.canvas.xview)

        self.inner = Frame(self.canvas, bg=self.bg)
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion=(0, 0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")


class ScrolledTable(ScrolledFrame):
    """ Tabelle in einem Scroll-Rahmen.
        Nicht geeignet für Tabellen mit deutlich mehr als 1000 Zeilen!

        Keyword-Argumente:
        borderwidth, bd: Breite des Rahmens        Beispiel: bd = 1
        font: Schriftfond und Größe                Beispiel: font = ('Arial', 10)
        colors: Tupel mit mind. 2 Farben
                1. Farbe für die Überschrift       Beispiel: colors = ('red', 'green', 'blue')
                alle weiteren Farben für die
                Zeilen
        zeilennummern: Wahrheitswert zum Anzeigen  Beispiel: zeilennummern = True
                       von Zeilennummern in der
                       ersten Spalte
        background, bg: Farbe des Frames           Beispiel: bg = 'light grey'
        width: Breite des Frames                   Beispiel: width = 400
        height: Höhe des Frames                    Beispiel: height = 600
        debug: Wahwert für Debug-Ausgaben          Beispiel: debug = False
    """

    def __init__(self, master, **kwargs):
        # speichere den Wert des Keys (hier: debug)
        # ist der Key nicht vorhanden, nimm den rechten Wert (hier: False)
        # falls vorhanden, entferne anschließend den Eintrag
        self.debug = kwargs.pop('debug', False)
        # weitere Attribute der Tabelle
        self.borderwidth = kwargs.pop('borderwidth', kwargs.pop('bd', 1))
        self.font = kwargs.pop('font', ('Arial', 10))
        self.colors = kwargs.pop('colors', ('darkseagreen', 'burlywood', 'moccasin'))
        self.colorUeberschrift = self.colors[0]
        if len(self.colors) > 1:
            self.colors = self.colors[1:]
        self.zeilennummern = kwargs.pop('zeilennummern', False)
        # Aufruf der Basisklasse mit den verbliebenen Attributen
        ScrolledFrame.__init__(self, master=master, **kwargs)
        self.anzahlZeilen = 0
        self.anzahlSpalten = 0
        self.cells = {}
        self.labels = []

    def anzeige(self, tabelle, schreibschutz=True):
        """ Anzeige einer Tabelle im Scroll-Rahmen.
        """
        self.loeschen()
        self.anzahlZeilen = len(tabelle)

        # Hänge bei jeder Zeile ein neues erstes Element an
        # mit der entsprechenden zeilennummer
        if self.zeilennummern:
            for i in range(len(tabelle)):
                zeile = tabelle[i]
                if i == 0:
                    zeile = ['  '] + zeile
                elif self.anzahlZeilen < 100:
                    zeile = [f'{i:02}'] + zeile
                else:
                    zeile = [f'{i:03}'] + zeile
                tabelle[i] = zeile
        self.anzahlSpalten = len(tabelle[0])

        gesamtbreite = 0
        breiten = []
        for j in range(self.anzahlSpalten):  # Columns
            breite = 2
            for i in range(self.anzahlZeilen):  # Rows
                if len(str(tabelle[i][j])) > breite:
                    breite = len(str(tabelle[i][j]))
            breiten.append(breite + 2)
            gesamtbreite += breite + 2

        for i in range(self.anzahlZeilen):  # Rows
            for j in range(self.anzahlSpalten):  # Columns
                b = Entry(master=self,
                          width=breiten[j],
                          font=self.font,
                          borderwidth=self.borderwidth,
                          disabledforeground="black",
                          disabledbackground=self.colors[i % (len(self.colors))])
                if i == 0:
                    b.config(disabledbackground=self.colorUeberschrift)
                b.grid(row=i, column=j)
                self.cells[(i, j)] = b
        for i in range(self.anzahlZeilen):
            for j in range(self.anzahlSpalten):
                inhalt = tabelle[i][j]
                self.cells[(i, j)].insert(END, '  ' + str(inhalt))
                if schreibschutz:
                    self.cells[(i, j)].config(state=DISABLED)

    def loeschen(self):
        for label in self.labels:
            label.destroy()
        for i in range(self.anzahlZeilen):
            for j in range(self.anzahlSpalten):
                self.cells[i, j].destroy()
        self.labels = []
        self.cells = {}
        self.anzahlZeilen = 0
        self.anzahlSpalten = 0


class ScrolledTableGUI(MasterGUI):
    def __init__(self, tabelle, title="GHO", zeilennummern=True,
                 schreibschutz=True):
        MasterGUI.__init__(self)
        self.title(title)
        if schreibschutz:
            self.scrolledTable = ScrolledTable(master=self, width=1000,
                                               height=500,
                                               bg='linen', borderwidth=0,
                                               zeilennummern=zeilennummern)
        else:
            self.scrolledTable = ScrolledTable(master=self, width=1000,
                                               height=500,
                                               bg='linen', borderwidth=1,
                                               zeilennummern=zeilennummern)

        self.scrolledTable.pack()
        self.scrolledTable.anzeige(tabelle, schreibschutz)
        self.focus_force()


class ScrolledTextGUI(MasterGUI):
    def __init__(self, breite=180, hoehe=45):
        MasterGUI.__init__(self)
        self.title("GHO")
        self.rahmen = Frame(master=self)
        self.scrollbarY = Scrollbar(master=self.rahmen)
        self.scrollbarX = Scrollbar(master=self.rahmen, orient=HORIZONTAL)
        self.anzeige = Text(master=self.rahmen,
                            font=('Courier New', 10),
                            bg="light green",
                            width=breite,
                            height=hoehe,
                            wrap=NONE,
                            yscrollcommand=self.scrollbarY.set,
                            xscrollcommand=self.scrollbarX.set)
        self.scrollbarY.config(command=self.anzeige.yview)
        self.scrollbarX.config(command=self.anzeige.xview)
        self.rahmen.pack()
        self.scrollbarY.pack(side=RIGHT, fill=Y)
        self.anzeige.pack(fill=BOTH, padx=10, pady=10)
        self.scrollbarX.pack(fill=X)
        # damit kommt das Ergebnisfenster nach vorne
        self.anzeige.focus_force()

    def zeigeAn(self, text):
        self.anzeige.config(state=NORMAL)
        self.loescheAnzeige()
        self.anzeige.insert(END, text)
        self.anzeige.config(state=DISABLED)

    def loescheAnzeige(self):
        self.anzeige.delete(0.0, END)
