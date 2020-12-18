from tkinter import *


class Basic3EntryPopup(Toplevel):
    def __init__(self, master=None, title="Enter", ltext1="", ltext2="", ltext3="", btext="Tamam", command=None, cnf=None,
                 **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw)
        self.title(title)
        self.wm_geometry(f"+{self.master.winfo_rootx()}+{self.master.winfo_rooty()}")

        self.Entry1 = Entry(self)
        self.Entry2 = Entry(self)
        self.Entry3 = Entry(self)

        label1 = Label(self, text=ltext1)
        label2 = Label(self, text=ltext2)
        label3 = Label(self, text=ltext3)
        if command is None:
            command = self.command

        self.button = Button(self, text=btext, command=lambda: command(self))

        self.Entry1.grid(column=1, row=0)
        self.Entry2.grid(column=1, row=1)
        self.Entry3.grid(column=1, row=2)

        self.button.grid(column=1, row=3)

        label1.grid(column=0, row=0)
        label2.grid(column=0, row=1)
        label3.grid(column=0, row=2)

    def command(self, *args):
        print("You pressed the button and nothing happened", self.Entry1.get(), self.Entry2.get(), self.Entry3.get())


if __name__ == '__main__':
    a = Tk()

    b = Basic3EntryPopup(a, "Adı", "Soyadı", "Eşek adı", "Kaydet")

    a.mainloop()
