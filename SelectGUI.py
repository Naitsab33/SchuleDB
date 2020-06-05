# -*- coding: utf-8 -*-
# Dateiname: SelectGUI.py
# Autor: Andreas Fischer
# erstellt: April 2020

from MyUtilities import *


class SelectGUI(MasterGUI):
    def __init__(self, db):
        self.db = db
        buttonWeite = 50
        eingabeWeite = 95
        padweite = 10
        MasterGUI.__init__(self)
        self.title("GHO")
        self.selectButton = Button(master=self, bg="blue",
                                   text="SELECT-Befehl ausführen",
                                   font=('Arial', 12, "bold"),
                                   width=buttonWeite, borderwidth=8,
                                   justify=CENTER,
                                   fg="white", relief=RAISED,
                                   command=self.selectKommando)
        self.selectResetButton = Button(master=self, bg="dark green",
                                        text="SELECT-Eingabe zurücksetzen",
                                        font=('Arial', 12, "bold"),
                                        width=buttonWeite // 2, borderwidth=8,
                                        justify=CENTER,
                                        fg="white", relief=RAISED,
                                        command=self.selectResetKommando)
        self.projLabel = Label(master=self, text="SELECT",
                               fg="blue", font=('Arial', 12, "bold"))
        self.tabLabel = Label(master=self, text="FROM",
                              font=('Arial', 12, "bold"), fg="blue")

        self.selLabel = Label(master=self, text="WHERE",
                              fg="blue", font=('Arial', 12, "bold"))

        self.projEntry = Entry(master=self, width=eingabeWeite,
                               font=('Arial', 12))

        self.tabEntry = Entry(master=self, width=eingabeWeite,
                              font=('Arial', 12))

        self.selText = Text(master=self, width=eingabeWeite,
                            font=('Arial', 12), height=12)

        zeile = 0
        self.projLabel.grid(column=0, row=zeile, sticky=E)
        self.projEntry.grid(column=1, row=zeile, sticky=W, columnspan=2,
                            padx=2 * padweite, pady=padweite)
        zeile += 1
        self.tabLabel.grid(column=0, row=zeile, sticky=E)
        self.tabEntry.grid(column=1, row=zeile, sticky=W, columnspan=2,
                           padx=2 * padweite, pady=padweite)
        zeile += 1
        self.selLabel.grid(column=0, row=zeile, sticky=E)
        self.selText.grid(column=1, row=zeile, sticky=W, columnspan=2,
                          padx=2 * padweite, pady=padweite)
        zeile += 1
        self.selectButton.grid(column=1, row=zeile, sticky=N,
                               padx=2 * padweite, pady=padweite)
        self.selectResetButton.grid(column=2, row=zeile, sticky=N,
                                    padx=padweite, pady=padweite)
        self.focus_force()

    def getTabEntry(self):
        return TextFormat.formatText(self.tabEntry.get())

    def getProjEntry(self):
        proj = TextFormat.formatText(self.projEntry.get())
        if not 'COUNT(*)' in proj and not 'count(*)' in proj:
            proj = proj.replace('COUNT(', 'COUNT (').replace('count(', 'COUNT (')
        proj = proj.replace('AVG(', 'AVG (').replace('avg(', 'AVG (')
        proj = proj.replace(' as ', ' AS ')
        proj = proj.replace('distinct ', 'DISTINCT ')
        proj = proj.replace('MAX(', 'MAX (').replace('max(', 'MAX (')
        proj = proj.replace('MIN(', 'MIN (').replace('min(', 'MIN (')
        proj = proj.replace('SUM(', 'SUM (').replace('sum(', 'SUM (')
        return proj

    def getSelText(self):
        text = TextFormat.formatText(self.selText.get(0.0, END))
        # Schlüsselwörter in GROSSBUCHSTABEN
        text = text.replace('order by', 'ORDER BY')
        text = text.replace('group by', 'GROUP BY')
        text = text.replace('length(', 'LENGTH(')
        text = text.replace(' and ', ' AND ')
        text = text.replace(' or ', ' OR ')
        text = text.replace(' not ', ' NOT ')
        text = text.replace(' desc', ' DESC')
        text = text.replace(' asc', ' ASC')
        return text

    def selectKommando(self):
        tab = self.getTabEntry()
        proj = self.getProjEntry()
        sel = self.getSelText()
        if len(proj) == 0:
            proj = "*"
        if len(sel) == 0:
            sel = "1"
        (tabelle, title) = self.db.selectStmt(proj, tab, sel)
        datensaetze = len(tabelle)
        maxi = 1000
        if datensaetze >= 100:
            fenster = ScrolledTextGUI()
            top = f" {title}\n Gesamtanzahl: {datensaetze - 1} Datensätze.\n"
            if datensaetze >= maxi:
                tabelle = tabelle[:maxi + 1]
                top += f" Es werden nur die ersten {maxi} Datensätze angezeigt.\n"
            fenster.zeigeAn(top + "\n" + TableFormat.table2text(tabelle, True))

        else:
            fenster = ScrolledTableGUI(tabelle, title)
        self.ergGUIs.append(fenster)
        # Dieses Fenster wird nach 120 Sekunden zerstört.
        #        fenster.after(120*1000, fenster.destroy)
        fenster.mainloop()

    #    def destroyKommando(self):
    #        for el in self.ergGUIs:
    #            # falls das Fenster bereits manuell geschlossen wurde:
    #            try:
    #                el.destroy()
    #            except:
    #                pass
    #        self.destroy()
    #

    def selectResetKommando(self):
        self.projEntry.delete("0", END)
        self.projEntry.insert(END, "*")
        self.tabEntry.delete("0", END)
        self.selText.delete("0.0", END)
