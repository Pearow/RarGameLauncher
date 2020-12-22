from tkinter import *
from Interface.main import width_changer


class SpecEntry(Canvas):

    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, bg="black", bd=-2, height=25, width=130, highlightthickness=0)

        self.Entry = Entry(self, cnf, **kw, borderwidth=0)
        entry = self.create_window((65, 10), window=self.Entry)
        self.create_line(0, 20, 127, 20, fill=kw["fg"])


class ListPopup(Toplevel):

    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw, bg="black", height=115, width=300)

        self.entry1 = SpecEntry(self, bg="black", fg="white")
        liste_ekle = Label(self, text="Liste Adı", bg="black", fg="white")
        Add_butt = Button(self, text="Ekle")

        self.bind("<Configure>", self.on_move)

        width_changer(self, self.entry1, "Entry1")
        width_changer(self, liste_ekle, "Label")
        width_changer(self, Add_butt, "Button")

        self.entry1.place(x=21, y=0)
        liste_ekle.place(x=0, y=5)
        Add_butt.place(x=0, y=0)

    def on_move(self, event):
        print(event.height, event.width)


class EntryWin(Toplevel):
    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw)




if __name__ == '__main__':
    pass