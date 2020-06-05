# -*- coding: utf-8 -*-
# Andreas Fischer

class Raum(object):
    def __init__(self, haus='', nummer=0, plaetze=None, lehrer=None, database=None):
        self.haus = haus
        self.nummer = nummer
        self.plaetze = plaetze
        self.lehrer = lehrer
        self.db = database
        if self.db == None: print("keine DB")

    def __str__(self):
        text = f"{self.haus}{self.nummer:02}"
        if self.plaetze != None:
            text += f" - Plaetze: {self.plaetze}"
        if self.lehrer != None:
            text += f" - Lehrkraft: {self.lehrer}"
        return text + '\n'

    def getInsertStatement(self):
        stm = ''
        stm += f'INSERT INTO raum (Haus, Nummer'
        if self.plaetze == None and self.lehrer == None:
            stm += f') VALUES ("{self.haus}", "{self.nummer}"'
        elif self.plaetze != None and self.lehrer == None:
            stm += ', Plaetze'
            stm += f') VALUES ("{self.haus}", "{self.nummer}", "{self.plaetze}"'
        elif self.plaetze == None and self.lehrer != None:
            stm += ', Lehrer'
            stm += f') VALUES ("{self.haus}", "{self.nummer}", "{self.lehrer}"'
        else:
            stm += f', Plaetze , Lehrer'
            stm += f') VALUES ("{self.haus}", "{self.nummer}", "{self.plaetze}", "{self.lehrer}"'
        stm += ');\n'
        return stm

    def insert(self):
        if self.db != None:
            self.db.execute(self.getInsertStatement())


if __name__ == "__main__":
    r = Raum('F', 60)
    print(r.getInsertStatement())
    r.plaetze = 17
    print(r.getInsertStatement())
    r.lehrer = 'FiA'
    print(r.getInsertStatement())
    r.plaetze = None
    print(r.getInsertStatement())
